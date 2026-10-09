"""Grid A* clean-up router for the low-speed nets Freerouting left open (and GND islands after bp_finish).
  python3 tools/bp_fix.py route SRC DST [NET ...]  : connect every split net (own-net components) on L1/L3/L4, 0.05 mm grid,
                                                     through vias (0.45/0.25); L3 only outside the L3_3V3_SB plane outline
  python3 tools/bp_fix.py gnd SRC DST              : GND pads/zone islands that are cut off -> short track + via to the L2 plane
Clearances: netclass (0.1, PWR 0.15) + pixel margin; HS copper is a soft cost (<0.35 mm same layer, <0.6 mm L3<->L4 cross);
rule areas (no tracks / no vias) and a 0.4 mm board-edge band are hard obstacles; then re-check with kicad-cli DRC."""
import pcbnew, sys, re, math, heapq, collections, json, subprocess, os
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point, Polygon, box
MM = pcbnew.FromMM; mm = pcbnew.ToMM
G = 0.05
HS = re.compile(r"(FP|FS)_(TX|RX)\d+_[PN]$|(FP|FS)_REFCLK1?_[PN]$" + os.environ.get("HSX", "|SATA0_.*|USB2_SPARE_.*"))
L1, L3, L4 = pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu
LX = pcbnew.In3_Cu                       # BP v3 6L: In3 = new signal layer (ref In4 GND); In1/In4 = GND planes
BP6 = os.environ.get("BP6") == "1"
RL = [L1, L3, LX, L4] if BP6 else [L1, L3, L4]     # physical order (via planes connect neighbours)
XPAIRS = ((L3, LX), (LX, L3)) if BP6 else ((L3, L4), (L4, L3))   # broadside / reference neighbours for the HS cross penalty
VIA_D, VIA_H = 0.45, 0.25
PIXM = float(os.environ.get("PIXMF", "0.72")) * G   # rasterisation margin
HINC = float(os.environ.get("HINC", "15")); HW = float(os.environ.get("HW", "1.6")); RIP = os.environ.get("RIP", "1") == "1"; RIPC = float(os.environ.get("RIPC", "25"))
def P(v): return (mm(v.x), mm(v.y))

class Grid:
    def __init__(s, b):
        s.b = b
        bb = b.GetBoardEdgesBoundingBox()
        s.x0, s.y0 = mm(bb.GetLeft()) - 1, mm(bb.GetTop()) - 1
        s.W = int((mm(bb.GetWidth()) + 2) / G) + 1; s.H = int((mm(bb.GetHeight()) + 2) / G) + 1
        s.cx, s.cy = mm(bb.GetCenter().x), mm(bb.GetCenter().y); s.R = mm(bb.GetWidth()) / 2
        s.netid = {}; s.names = [""]
        s.lab = {L: np.zeros((s.H, s.W), np.int32) for L in RL}      # copper owner net id (0 free)
        s.pwr = {L: np.zeros((s.H, s.W), bool) for L in RL}          # copper of PWR-class nets (0.15 clearance)
        s.hs = {L: np.zeros((s.H, s.W), bool) for L in RL}
        s.notrk = {L: np.zeros((s.H, s.W), bool) for L in RL}
        s.novia = np.zeros((s.H, s.W), bool)
        s.drill = np.zeros((s.H, s.W), bool)
        s.rip = {L: np.zeros((s.H, s.W), bool) for L in RL}
        s.hist = {L: np.zeros((s.H, s.W), np.float32) for L in RL}   # PathFinder history: grows where copper was ripped
        s.iter = 0   # pixels owned by rip-able copper (unlocked routed tracks/vias)
        yy, xx = np.mgrid[0:s.H, 0:s.W]
        out = np.hypot(s.x0 + xx * G - s.cx, s.y0 + yy * G - s.cy) > s.R - 0.4
        for L in RL: s.notrk[L] |= out
        s.novia |= np.hypot(s.x0 + xx * G - s.cx, s.y0 + yy * G - s.cy) > s.R - 0.6
        s.cls = {}
        for n, ni in b.GetNetInfo().NetsByName().items():
            s.cls[str(n)] = ni.GetNetClassName()
        s.zone3 = None
        for z in list(b.Zones()) + [fz for f in b.GetFootprints() for fz in f.Zones()]:   # incl. footprint keepouts
            if z.GetIsRuleArea():
                o = z.Outline(); img = ndimage.binary_dilation(s.polyimg(o), iterations=int(math.ceil(float(os.environ.get("KOD", "0.22")) / G)))   # centreline mask: grow by half track width + margin
                for L in RL:
                    if z.IsOnLayer(L) and z.GetDoNotAllowTracks(): s.notrk[L] |= img
                if z.GetDoNotAllowVias(): s.novia |= img
            elif z.GetZoneName() == "L3_3V3_SB":
                s.zone3 = s.polyimg(z.Outline())
        for t in b.GetTracks(): s.add_item(t)
        for f in b.GetFootprints():
            for p in f.Pads(): s.add_pad(p)
        s.zfill = {}   # own-net zone fills (by net) for connectivity
        for z in b.Zones():
            if z.GetIsRuleArea(): continue
            for L in RL:
                if z.IsOnLayer(L) and z.HasFilledPolysForLayer(L):
                    fp = z.GetFilledPolysList(L)
                    img = s.polyimg(fp)
                    nid = s.nid(z.GetNetname())
                    s.zfill.setdefault(nid, {}).setdefault(L, np.zeros((s.H, s.W), bool))
                    s.zfill[nid][L] |= img
    def nid(s, n):
        if n not in s.netid: s.netid[n] = len(s.names); s.names.append(n)
        return s.netid[n]
    def px(s, x, y): return ((x - s.x0) / G, (y - s.y0) / G)
    def polyimg(s, sps):
        im = Image.new("1", (s.W, s.H), 0); d = ImageDraw.Draw(im)
        for i in range(sps.OutlineCount()):
            ol = sps.COutline(i); pts = [s.px(*P(ol.CPoint(k))) for k in range(ol.PointCount())]
            if len(pts) > 2: d.polygon(pts, fill=1)
            for h in range(sps.HoleCount(i)):
                hl = sps.CHole(i, h); hp = [s.px(*P(hl.CPoint(k))) for k in range(hl.PointCount())]
                if len(hp) > 2: d.polygon(hp, fill=0)
        return np.array(im, bool)
    def geomimg(s, g):
        im = Image.new("1", (s.W, s.H), 0); d = ImageDraw.Draw(im)
        for q in (g.geoms if hasattr(g, "geoms") else [g]):
            d.polygon([s.px(*c) for c in q.exterior.coords], fill=1)
            for h in q.interiors: d.polygon([s.px(*c) for c in h.coords], fill=0)
        return np.array(im, bool)
    def stamp(s, L, g, n, rip=False):
        nid = s.nid(n)
        x0, y0, x1, y1 = g.bounds
        i0, j0 = max(int((x0 - s.x0) / G) - 1, 0), max(int((y0 - s.y0) / G) - 1, 0)
        i1, j1 = min(int((x1 - s.x0) / G) + 2, s.W), min(int((y1 - s.y0) / G) + 2, s.H)
        im = Image.new("1", (i1 - i0, j1 - j0), 0); d = ImageDraw.Draw(im)
        for q in (g.geoms if hasattr(g, "geoms") else [g]):
            d.polygon([((c[0] - s.x0) / G - i0, (c[1] - s.y0) / G - j0) for c in q.exterior.coords], fill=1)
        m = np.array(im, bool)
        s.lab[L][j0:j1, i0:i1][m] = nid
        if rip: s.rip[L][j0:j1, i0:i1] |= m
        if s.cls.get(n) == "PWR": s.pwr[L][j0:j1, i0:i1] |= m
        if HS.match(n): s.hs[L][j0:j1, i0:i1] |= m
        return (j0, j1, i0, i1, m)
    def geom(s, t):
        if isinstance(t, pcbnew.PCB_VIA): return Point(P(t.GetPosition())).buffer(mm(t.GetWidth(L1)) / 2, 16)
        return LineString([P(t.GetStart()), P(t.GetEnd())]).buffer(mm(t.GetWidth()) / 2, 8)
    def ripable(s, t): return (not t.IsLocked()) and t.GetNetname() != "GND" and not HS.match(t.GetNetname())
    def add_item(s, t):
        n = t.GetNetname(); rp = s.ripable(t)
        if isinstance(t, pcbnew.PCB_VIA):
            c = P(t.GetPosition()); g = s.geom(t)
            for L in RL: s.stamp(L, g, n, rp)
            j0, j1, i0, i1, m = s.stamp(L1, Point(c).buffer(mm(t.GetDrill()) / 2, 16), n, rp); s.drill[j0:j1, i0:i1] |= m
        else:
            L = t.GetLayer()
            if L in RL: s.stamp(L, s.geom(t), n, rp)
    def remove_item(s, t):
        n = t.GetNetname(); nid = s.nid(n); g = s.geom(t)
        lays = RL if isinstance(t, pcbnew.PCB_VIA) else [t.GetLayer()]
        x0, y0, x1, y1 = g.bounds
        i0, j0 = max(int((x0 - s.x0) / G) - 1, 0), max(int((y0 - s.y0) / G) - 1, 0)
        i1, j1 = min(int((x1 - s.x0) / G) + 2, s.W), min(int((y1 - s.y0) / G) + 2, s.H)
        for L in lays:
            if L not in RL: continue
            sub = s.lab[L][j0:j1, i0:i1]; m = s.rip[L][j0:j1, i0:i1] & (sub == nid)
            sub[m] = 0; s.rip[L][j0:j1, i0:i1][m] = False; s.pwr[L][j0:j1, i0:i1][m] = False
        if isinstance(t, pcbnew.PCB_VIA): s.drill[j0:j1, i0:i1][(s.lab[L1][j0:j1, i0:i1] == 0)] = False
        s.b.Remove(t); KEEPALIVE.append(t)   # removed items must outlive the board (SWIG ownership)
        bx = box(x0 - 1, y0 - 1, x1 + 1, y1 + 1)   # re-stamp same-net neighbours that shared pixels
        for u in s.b.GetTracks():
            if u.GetNetname() == n and s.geom(u).intersects(bx): s.add_item(u)
        for f in s.b.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() == n and Point(P(p.GetPosition())).distance(bx) < 3: s.add_pad(p)
    def add_pad(s, p):
        n = p.GetNetname() or ("_nc_%d" % id(p))
        for L in RL:
            if p.IsOnLayer(L):
                sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
                img = s.polyimg(sp); s.lab[L][img] = s.nid(n)
                if s.cls.get(n) == "PWR": s.pwr[L] |= img
                if HS.match(n): s.hs[L] |= img
        if p.GetDrillSize().x > 0:
            c = P(p.GetPosition()); g = Point(c).buffer(mm(p.GetDrillSize().x) / 2, 16)
            j0, j1, i0, i1, m = s.stamp(L1, g, n); s.drill[j0:j1, i0:i1] |= m
            for L in RL:   # NPTH / hole: copper-free on every layer
                if not p.IsOnLayer(L) or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH: s.stamp(L, g.buffer(float(os.environ.get("NPTHC", "0.22"))), n)

def width_of(cls): return {"PWR": 0.3, "PWR_FINE": 0.2, "USB2_SATA_90R": 0.24}.get(cls, 0.15)
def clr_of(cls): return 0.15 if cls == "PWR" else 0.1

def route_net(g, n, maxcomp=50, log=print):
    nid = g.nid(n); cls = g.cls.get(n, "Default"); w = width_of(cls); c0 = clr_of(cls)
    added = []
    for it in range(maxcomp):
        own = {L: (g.lab[L] == nid) | g.zfill.get(nid, {}).get(L, np.zeros((g.H, g.W), bool)) for L in RL}
        labs = {}; uf = {}
        def find(a):
            while uf[a] != a: uf[a] = uf[uf[a]]; a = uf[a]
            return a
        for L in RL:
            lb, k = ndimage.label(own[L], structure=np.ones((3, 3)))
            labs[L] = lb
            for q in range(1, k + 1): uf[(L, q)] = (L, q)
        # vias / THT pads link the layers: pixels that are own on all layers and drilled
        dm = g.drill & np.logical_and.reduce([own[L] for L in RL])
        ys, xs = np.nonzero(dm)
        for y, x in zip(ys, xs):
            a = find((L1, labs[L1][y, x]))
            for L in RL[1:]:
                if labs[L][y, x]: uf[find((L, labs[L][y, x]))] = a
        roots = collections.defaultdict(int)
        for k in uf: roots[find(k)] += 1
        # components that contain a pad/track: count pixels
        comp = {}
        for L in RL:
            for q in np.unique(labs[L])[1:]: comp.setdefault(find((L, q)), []).append((L, q))
        if len(comp) <= 1: return added, True
        # source = component with most pixels
        sizes = {r: sum(int((labs[L] == q).sum()) for L, q in v) for r, v in comp.items()}
        src = max(sizes, key=sizes.get)
        S = {L: np.isin(labs[L], [q for (LL, q) in comp[src] if LL == L]) for L in RL}
        T = {L: own[L] & ~S[L] for L in RL}
        path = astar(g, nid, cls, w, c0, S, T)
        if path is None:
            mine = [t for t in g.b.GetTracks() if t.GetNetname() == n and g.ripable(t)]
            if RIP and not FRESH.get(n) and mine:
                FRESH[n] = True; log("  %s: no path (%d comps) -> rip own %d items, retry from pads" % (n, len(comp), len(mine)))
                for t in mine: g.remove_item(t)
                added = []; continue
            log("  %s: no path (%d comps)" % (n, len(comp))); return added, False
        segs = emit(g, n, path, w)
        added += segs
        RIPPED.update(rip_conflicts(g, n, segs, c0))
    return added, False

def astar(g, nid, cls, w, c0, S, T):
    # crop window around S and T
    ys, xs = [], []
    for L in RL:
        for M in (S[L], T[L]):
            yy, xx = np.nonzero(M)
            if len(yy): ys += [yy.min(), yy.max()]; xs += [xx.min(), xx.max()]
    pad = int(12 / G)
    y0, y1 = max(min(ys) - pad, 0), min(max(ys) + pad + 1, g.H); x0, x1 = max(min(xs) - pad, 0), min(max(xs) + pad + 1, g.W)
    H, W = y1 - y0, x1 - x0
    rt = w / 2 + c0 + PIXM; rtp = w / 2 + 0.15 + PIXM
    rv = VIA_D / 2 + c0 + PIXM; rvp = VIA_D / 2 + 0.15 + PIXM
    free = {}; cost = {}; viac_extra = {}
    viaok = ~g.novia[y0:y1, x0:x1]
    dd = ndimage.distance_transform_edt(~g.drill[y0:y1, x0:x1]) * G
    viaok &= dd > VIA_H / 2 + 0.25 + 0.125 + PIXM   # hole-to-hole
    for L in RL:
        lab = g.lab[L][y0:y1, x0:x1]
        oth = (lab != 0) & (lab != nid); pw = g.pwr[L][y0:y1, x0:x1] & oth
        rp = g.rip[L][y0:y1, x0:x1] & oth
        d1 = ndimage.distance_transform_edt(~(oth & ~pw)) * G
        d2 = ndimage.distance_transform_edt(~pw) * G if pw.any() else np.full((H, W), 99.0)
        hard = oth & ~rp; hp = hard & g.pwr[L][y0:y1, x0:x1]
        e1 = ndimage.distance_transform_edt(~(hard & ~hp)) * G
        e2 = ndimage.distance_transform_edt(~hp) * G if hp.any() else np.full((H, W), 99.0)
        dhs = ndimage.distance_transform_edt(~(g.hs[L][y0:y1, x0:x1] & oth)) * G
        f = (d1 > rt) & (d2 > rtp) & ~g.notrk[L][y0:y1, x0:x1]
        soft = (e1 > rt) & (e2 > rtp) & ~g.notrk[L][y0:y1, x0:x1] & ~f if RIP else np.zeros((H, W), bool)
        own = (lab == nid)
        f |= own & ~g.notrk[L][y0:y1, x0:x1] & (d1 > w / 2 + c0)   # allow running over own copper
        free[L] = f
        viaok &= (d1 > rv) & (d2 > rvp) if not RIP else (e1 > rv) & (e2 > rvp)
        if RIP: viahit = (d1 <= rv) | (d2 <= rvp); viac_extra[L] = viahit
        cst = np.ones((H, W), np.float32)
        cst[soft] += RIPC * (1 + g.iter / 40.0) + g.hist[L][y0:y1, x0:x1][soft]; f = f | soft; free[L] = f
        cst[dhs < 0.35 + w / 2] += 4.0
        cost[L] = cst
    if g.zone3 is not None and os.environ.get("L3PEN", "3") != "x":
        cost[L3][g.zone3[y0:y1, x0:x1]] += float(os.environ.get("L3PEN", "3"))
    # cross-layer HS penalty (L3 HS -> L4 and L4 HS -> L3)
    for La, Lb in XPAIRS:
        hsd = ndimage.distance_transform_edt(~g.hs[La][y0:y1, x0:x1]) * G
        cost[Lb][hsd < 0.6 + w / 2] += 6.0
    # L1 runs below L1 HS are same-layer only; L4 under L1 RX is fine (L2 reference between)
    lid = {L: i for i, L in enumerate(RL)}
    F = np.stack([free[L] for L in RL]); C = np.stack([cost[L] for L in RL]).astype(np.float64)
    Sm = np.stack([S[L][y0:y1, x0:x1] for L in RL]) & F
    Tm = np.stack([T[L][y0:y1, x0:x1] for L in RL]) & F
    if not Sm.any() or not Tm.any():
        # allow start/goal pixels even if not free (pad interior near other copper) -> use own pixels with d1 > w/2 + c0 - margin
        Sm = np.stack([S[L][y0:y1, x0:x1] for L in RL]); Tm = np.stack([T[L][y0:y1, x0:x1] for L in RL])
    from skimage.graph import MCP_Geometric
    VX = (np.stack([viac_extra[L] for L in RL]).any(0) * RIPC * 8) if RIP else np.zeros((H, W))
    INF = np.inf
    NL = len(RL); cst5 = np.full((2 * NL - 1, H, W), INF)
    for k in range(NL):
        cst5[2 * k] = np.where(F[k] | Tm[k] | Sm[k], C[k], INF)
    vc = np.where(viaok, 1.6 / G + VX, INF)
    for k in range(NL - 1): cst5[2 * k + 1] = vc
    offs = [(0, dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx] + [(1, 0, 0), (-1, 0, 0)]
    m = MCP_Geometric(cst5, offsets=np.array(offs), fully_connected=False)
    S5 = [(2 * l, y, x) for l, y, x in zip(*np.nonzero(Sm))]
    T5 = [(2 * l, y, x) for l, y, x in zip(*np.nonzero(Tm))]
    if not S5 or not T5: return None
    if os.environ.get("DBG"):
        for k in range(len(RL)):
            lb, _ = ndimage.label(F[k] | Sm[k] | Tm[k], structure=np.ones((3, 3)))
            tl = set(np.unique(lb[Tm[k]])) - {0}; sl = set(np.unique(lb[Sm[k]])) - {0}
            treg = np.isin(lb, list(tl))
            print("  DBG L%d: S px %d T px %d, T region %d px, viaok in T region %d, S/T share %s" % (k, int(Sm[k].sum()), int(Tm[k].sum()), int(treg.sum()), int((treg & viaok).sum()), bool(sl & tl)))
            sreg = np.isin(lb, list(sl))
            if sreg.sum() and sreg.sum() < 3000:
                ys, xs = np.nonzero(sreg); print("   S region bbox", [round(float(g.x0 + (x0 + xs.min()) * G - 150), 2), round(float(100 - (g.y0 + (y0 + ys.max()) * G)), 2), round(float(g.x0 + (x0 + xs.max()) * G - 150), 2), round(float(100 - (g.y0 + (y0 + ys.min()) * G)), 2)], "viaok", int((sreg & viaok).sum()))
            if treg.sum() and treg.sum() < 3000:
                ys, xs = np.nonzero(treg); print("   T region bbox disc", [round(float(g.x0 + (x0 + xs.min()) * G - 150), 2), round(float(100 - (g.y0 + (y0 + ys.max()) * G)), 2), round(float(g.x0 + (x0 + xs.max()) * G - 150), 2), round(float(100 - (g.y0 + (y0 + ys.min()) * G)), 2)])
    cum, tb = m.find_costs(S5, T5, find_all_ends=False)
    Tc = [(cum[q], q) for q in T5]
    best = min(Tc)
    if not np.isfinite(best[0]): return None
    tr = m.traceback(best[1])
    path = []
    for (z, y, x) in tr:
        if z % 2: continue
        path.append((RL[z // 2], y + y0, x + x0))
    return path

def emit(g, n, path, w):
    b = g.b; net = b.FindNet(n); out = []
    def xy(y, x): return (float(g.x0 + x * G), float(g.y0 + y * G))
    # split by layer, add vias at layer changes
    runs = [[path[0]]]; lastv = None
    for p in path[1:]:
        if p[0] != runs[-1][-1][0]:
            if lastv == (p[1], p[2]): runs.append([p]); continue
            lastv = (p[1], p[2])
            v = pcbnew.PCB_VIA(b); c = xy(p[1], p[2]); v.SetPosition(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
            v.SetWidth(L1, MM(VIA_D)); v.SetDrill(MM(VIA_H)); v.SetNet(net); b.Add(v); g.add_item(v); out.append(v)
            runs.append([p])
        else: runs[-1].append(p)
    for run in runs:
        if len(run) < 2: continue
        pts = [run[0]]
        for k in range(1, len(run) - 1):
            a, c_, d = run[k - 1], run[k], run[k + 1]
            if (c_[1] - a[1], c_[2] - a[2]) != (d[1] - c_[1], d[2] - c_[2]): pts.append(c_)
        pts.append(run[-1])
        for a, c_ in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b); pa, pc = xy(a[1], a[2]), xy(c_[1], c_[2])
            t.SetStart(pcbnew.VECTOR2I(MM(pa[0]), MM(pa[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(pc[0]), MM(pc[1])))
            t.SetWidth(MM(w)); t.SetLayer(a[0]); t.SetNet(net); b.Add(t); g.add_item(t); out.append(t)
    return out

RIPPED = collections.Counter(); FRESH = {}; KEEPALIVE = []
def rip_conflicts(g, n, segs, c0):
    out = collections.Counter()
    newg = [(t.GetLayer() if not isinstance(t, pcbnew.PCB_VIA) else None, g.geom(t)) for t in segs]
    bx = [ng.bounds for _, ng in newg]
    X0 = min(q[0] for q in bx) - 1; Y0 = min(q[1] for q in bx) - 1; X1 = max(q[2] for q in bx) + 1; Y1 = max(q[3] for q in bx) + 1
    kill = []
    for t in list(g.b.GetTracks()):
        if t.GetNetname() == n or not g.ripable(t): continue
        tg = g.geom(t); b0 = tg.bounds
        if b0[2] < X0 or b0[0] > X1 or b0[3] < Y0 or b0[1] > Y1: continue
        tv = isinstance(t, pcbnew.PCB_VIA)
        cl = max(c0, clr_of(g.cls.get(t.GetNetname())))
        for L, ng in newg:
            if not (tv or L is None or L == t.GetLayer()): continue
            if ng.distance(tg) < cl - 0.005: kill.append(t); break
    for t in kill:
        out[t.GetNetname()] += 1
        tg = g.geom(t).buffer(0.15); x0, y0, x1, y1 = tg.bounds
        i0, j0 = max(int((x0 - g.x0) / G), 0), max(int((y0 - g.y0) / G), 0); i1, j1 = min(int((x1 - g.x0) / G) + 1, g.W), min(int((y1 - g.y0) / G) + 1, g.H)
        for L in (RL if isinstance(t, pcbnew.PCB_VIA) else [t.GetLayer()]):
            if L in RL: g.hist[L][j0:j1, i0:i1] += HINC
        g.remove_item(t)
    for t in segs: g.add_item(t)   # restore own pixels possibly cleared
    return out

def split_nets(b):
    """nets with >1 connected island according to KiCad connectivity"""
    b.BuildConnectivity(); cn = b.GetConnectivity()
    res = []
    for n, ni in b.GetNetInfo().NetsByName().items():
        n = str(n)
        if not n or n == "GND" or n.startswith("unconnected-") or HS.match(n): continue
        if cn.GetUnconnectedCount if False else False: pass
    return res

def drc_unconnected(pcb):
    out = "/tmp/bpfix_drc.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", out, pcb], capture_output=True)
    d = json.load(open(out))
    nets = collections.Counter()
    for u in d["unconnected_items"]:
        m = re.search(r"\[([^\]]+)\]", u["items"][0]["description"]); nets[m.group(1) if m else "?"] += 1
    return nets, d

def plane_stitch(g, item, n, log=print):
    """isolated pad/track of a plane net (GND -> L2 plane, 3V3_SB -> L3_3V3_SB plane): short L1 track to a free via spot that lands in the plane"""
    from skimage.graph import MCP_Geometric
    nid = g.nid(n)
    if isinstance(item, pcbnew.PAD):
        c = P(item.GetPosition()); smask = g.polyimg(item.GetEffectivePolygon(L1, pcbnew.ERROR_INSIDE)); lay = L1
        if not item.IsOnLayer(L1): return False
    else:
        if isinstance(item, pcbnew.PCB_VIA) or item.GetLayer() != L1: return False
        c = P(item.GetStart()); geo = g.geom(item); smask = g.geomimg(geo)
    j, i = int((c[1] - g.y0) / G), int((c[0] - g.x0) / G); r = int(5 / G)
    y0, y1, x0, x1 = max(j - r, 0), min(j + r, g.H), max(i - r, 0), min(i + r, g.W)
    viaok = ~g.novia[y0:y1, x0:x1] & (ndimage.distance_transform_edt(~g.drill[y0:y1, x0:x1]) * G > VIA_H / 2 + 0.25 + 0.125 + PIXM)
    for L in RL:
        o = (g.lab[L][y0:y1, x0:x1] != 0) & (g.lab[L][y0:y1, x0:x1] != nid)
        viaok &= ndimage.distance_transform_edt(~o) * G > VIA_D / 2 + (0.15 if L == L3 else 0.12) + PIXM
    if n == "3V3_SB":
        zf = g.zfill.get(nid, {}).get(L3)
        if zf is None: return False
        viaok &= ndimage.binary_erosion(zf[y0:y1, x0:x1], iterations=int(0.5 / G))
    lab = g.lab[L1][y0:y1, x0:x1]; oth = (lab != 0) & (lab != nid)
    d1 = ndimage.distance_transform_edt(~oth) * G
    w = 0.25; free = (d1 > w / 2 + 0.1 + PIXM) & ~g.notrk[L1][y0:y1, x0:x1]
    sp = smask[y0:y1, x0:x1]
    free |= sp & (d1 > w / 2 + 0.1)
    if not (free & sp).any(): free |= sp
    cst = np.where(free, 1.0, np.inf)
    m = MCP_Geometric(cst)
    S = list(zip(*np.nonzero(sp & free))); T = list(zip(*np.nonzero(viaok & free)))
    if not S or not T: log("  stitch %s @%s: no via spot" % (n, c)); return False
    cum, _ = m.find_costs(S, T, find_all_ends=False)
    best = min((cum[q], q) for q in T)
    if not np.isfinite(best[0]): log("  stitch %s @%s: unreachable" % (n, c)); return False
    tr = m.traceback(best[1])
    path = [(L1, yy + y0, xx + x0) for yy, xx in tr]
    segs = emit(g, n, path, w) if len(path) > 1 else []
    b = g.b; v = pcbnew.PCB_VIA(b); e = path[-1]
    v.SetPosition(pcbnew.VECTOR2I(MM(float(g.x0 + e[2] * G)), MM(float(g.y0 + e[1] * G)))); v.SetWidth(L1, MM(VIA_D)); v.SetDrill(MM(VIA_H))
    v.SetNet(b.FindNet(n)); b.Add(v); g.add_item(v)
    log("  stitch %s @(%.1f,%.1f): via + %d segs" % (n, c[0] - 150, 100 - c[1], len(segs))); return True

def gnd_stitch(g, pad, log=print):
    """isolated GND pad (SMD on F): shortest 0.3 mm track to a free via spot (via drops to the L2 GND plane)"""
    from skimage.graph import MCP_Geometric
    nid = g.nid("GND"); c = P(pad.GetPosition())
    j, i = int((c[1] - g.y0) / G), int((c[0] - g.x0) / G); r = int(4 / G)
    y0, y1, x0, x1 = max(j - r, 0), min(j + r, g.H), max(i - r, 0), min(i + r, g.W)
    lab = g.lab[L1][y0:y1, x0:x1]; oth = (lab != 0) & (lab != nid)
    viaok = ~g.novia[y0:y1, x0:x1] & (ndimage.distance_transform_edt(~g.drill[y0:y1, x0:x1]) * G > VIA_H / 2 + 0.25 + 0.125 + PIXM)
    for L in RL:
        o = (g.lab[L][y0:y1, x0:x1] != 0) & (g.lab[L][y0:y1, x0:x1] != nid)
        viaok &= ndimage.distance_transform_edt(~o) * G > VIA_D / 2 + 0.15 + PIXM
    d1 = ndimage.distance_transform_edt(~oth) * G
    w = 0.3; free = (d1 > w / 2 + 0.15 + PIXM) & ~g.notrk[L1][y0:y1, x0:x1]
    sp = g.polyimg(pad.GetEffectivePolygon(L1, pcbnew.ERROR_INSIDE))[y0:y1, x0:x1]
    free |= sp & (d1 > w / 2 + 0.1)
    if not (free & sp).any(): free |= sp; w = 0.2
    cst = np.where(free, 1.0, np.inf)
    m = MCP_Geometric(cst)
    S = list(zip(*np.nonzero(sp & free))); T = list(zip(*np.nonzero(viaok & free)))
    if not S or not T: log("  gnd %s-%s: no via spot" % (pad.GetParentFootprint().GetReference(), pad.GetNumber())); return False
    cum, _ = m.find_costs(S, T, find_all_ends=False)
    best = min((cum[q], q) for q in T)
    if not np.isfinite(best[0]): log("  gnd %s-%s: unreachable" % (pad.GetParentFootprint().GetReference(), pad.GetNumber())); return False
    tr = m.traceback(best[1])
    path = [(L1, yy + y0, xx + x0) for yy, xx in tr]
    segs = emit(g, "GND", path, w) if len(path) > 1 else []
    b = g.b; v = pcbnew.PCB_VIA(b); e = path[-1]
    v.SetPosition(pcbnew.VECTOR2I(MM(float(g.x0 + e[2] * G)), MM(float(g.y0 + e[1] * G)))); v.SetWidth(L1, MM(VIA_D)); v.SetDrill(MM(VIA_H))
    v.SetNet(b.FindNet("GND")); b.Add(v); g.add_item(v)
    log("  gnd %s-%s: via + %d segs" % (pad.GetParentFootprint().GetReference(), pad.GetNumber(), len(segs))); return True

if __name__ == "__main__":
    mode, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    only = sys.argv[4:]
    b = pcbnew.LoadBoard(src)
    if mode == "stitch":
        nets, d = drc_unconnected(src)
        want = set(); 
        for u in d["unconnected_items"]:
            for it in u["items"]:
                mm_ = re.search(r"\[(GND|3V3_SB)\]", it["description"])
                if mm_ and not it["description"].startswith("Zone"): want.add((it["uuid"], mm_.group(1)))
        print("plane-net items to stitch", len(want))
        g = Grid(b)
        byid = {}
        for t in b.GetTracks(): byid[t.m_Uuid.AsString()] = t
        for f in b.GetFootprints():
            for p in f.Pads(): byid[p.m_Uuid.AsString()] = p
        for uid, n in sorted(want):
            if uid in byid: plane_stitch(g, byid[uid], n)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(dst, b)
    if mode == "gnd":
        nets, d = drc_unconnected(src)
        refs = set()
        for u in d["unconnected_items"]:
            for it in u["items"]:
                mm_ = re.match(r"Pad (\S+) \[GND\] of (\S+)", it["description"])
                if mm_: refs.add((mm_.group(2), mm_.group(1)))
        print("GND pads in unconnected list", sorted(refs))
        g = Grid(b)
        for f in b.GetFootprints():
            for p in f.Pads():
                if (f.GetReference(), p.GetNumber()) in refs and p.IsOnLayer(L1): gnd_stitch(g, p)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(dst, b)
    if mode == "drcfix":   # remove unlocked, non-HS, non-GND copper with DRC errors, then route those nets + unconnected
        nets, d = drc_unconnected(src)
        bad = set(); bn = set()
        for v in d["violations"]:
            if v["severity"] != "error" or v["type"] not in ("clearance", "hole_clearance", "items_not_allowed", "copper_edge_clearance", "tracks_crossing", "shorting_items"): continue
            for i in v["items"]: bad.add(i["uuid"])
        n_ = 0
        for t in list(b.GetTracks()):
            if t.m_Uuid.AsString() in bad and not t.IsLocked() and t.GetNetname() != "GND" and not HS.match(t.GetNetname()) and not t.GetNetname().startswith("SATA0_"):
                bn.add(t.GetNetname()); b.Remove(t); n_ += 1
        print("removed DRC items", n_, "nets", sorted(bn))
        pcbnew.SaveBoard(dst, b); sys.exit(0)
    if mode == "route":
        # nets to fix: from DRC on src (needs project next to it)
        if only and os.environ.get("NODRC") == "1": nets = {}   # explicit net list: skip the (slow) source DRC
        else: nets, d = drc_unconnected(src)
        todo = [n for n in nets if n != "GND" and not HS.match(n)] if not only else only
        print("unconnected nets", len(todo), dict(nets))
        g = Grid(b)
        # shortest first: by pad bbox span
        def span(n):
            ps = [P(p.GetPosition()) for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == n]
            return (max(x for x, y in ps) - min(x for x, y in ps)) + (max(y for x, y in ps) - min(y for x, y in ps)) if ps else 0
        todo.sort(key=span)
        ok = []; bad = []; tries = collections.Counter()
        queue = list(todo); it = 0
        while queue and it < int(os.environ.get("MAXIT", "200")):
            n = queue.pop(0); it += 1; tries[n] += 1; g.iter = it
            RIPPED.clear()
            a, done = route_net(g, n)
            print("%3d %-22s %s +%d items, ripped %s" % (it, n, "OK" if done else "FAIL", len(a), dict(RIPPED)), flush=True)
            if not done: bad.append(n)
            for m in RIPPED:
                if m not in queue: queue.append(m)
            if it % 10 == 0: pcbnew.SaveBoard(dst, b)
        pcbnew.SaveBoard(dst, b)
        print("left in queue", queue, "failed", bad)
