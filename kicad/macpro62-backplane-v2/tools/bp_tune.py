"""Intra-pair skew compensation: adds 45-degree trapezoid bumps on the shorter leg of each pair
(outward, away from the partner), clearance-checked with shapely. in -> out pcb."""
import pcbnew, sys, math, re, collections, os
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
sys.path.insert(0, "tools")
SRC, DST = sys.argv[1], sys.argv[2]
TARGET = 0.02
CLR = 0.1 + 0.03
b = pcbnew.LoadBoard(SRC)
mm = pcbnew.ToMM; MM = pcbnew.FromMM
def P(v): return (mm(v.x), mm(v.y))

def lengths():
    L = collections.defaultdict(float); V = collections.Counter()
    for t in b.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA): V[t.GetNetname()] += 1
        else: L[t.GetNetname()] += mm(t.GetLength())
    return L, V

def obstacles(layer, exclude):
    g = []
    for t in b.GetTracks():
        if t.GetNetname() in exclude: continue
        if isinstance(t, pcbnew.PCB_VIA):
            g.append(Point(P(t.GetPosition())).buffer(mm(t.GetWidth(pcbnew.F_Cu)) / 2))
        elif t.GetLayer() == layer:
            g.append(LineString([P(t.GetStart()), P(t.GetEnd())]).buffer(mm(t.GetWidth()) / 2))
    for fp in b.GetFootprints():
        for pd in fp.Pads():
            if pd.GetNetname() in exclude or not pd.IsOnLayer(layer): continue
            bb = pd.GetBoundingBox()
            g.append(box(mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())))
    return unary_union(g)

def bump_path(a, b_, ux, uy, nx, ny, amp, nb, flat=0.3, gap=0.3):
    """points from a to b_ with nb trapezoid bumps centred on the segment."""
    unit = 2 * amp + flat
    tot = nb * unit + (nb - 1) * gap
    L = math.dist(a, b_)
    s0 = (L - tot) / 2
    pts = [a]
    s = s0
    for i in range(nb):
        q = lambda d, h: (a[0] + ux * d + nx * h, a[1] + uy * d + ny * h)
        pts += [q(s, 0), q(s + amp, amp), q(s + amp + flat, amp), q(s + unit, 0)]
        s += unit + gap
    pts.append(b_)
    return pts

def tune(pair):
    L, V = lengths()
    nP, nN = pair + "_P", pair + "_N"
    sk = L[nP] - L[nN] + float(os.environ.get("TUNE_VIA", "0")) * (V[nP] - V[nN])   # TUNE_VIA=1.6: count vias as board thickness (bp_skew)
    if abs(sk) <= TARGET: return 0.0, "ok"
    short, other = (nP, nN) if sk < 0 else (nN, nP)
    need = abs(sk)
    segs = [t for t in b.GetTracks() if not isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == short]
    segs.sort(key=lambda t: -t.GetLength())
    partner = [t for t in b.GetTracks() if not isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == other]
    for t in segs:
        a, c = P(t.GetStart()), P(t.GetEnd())
        Ls = math.dist(a, c)
        if Ls < float(os.environ.get("TUNE_MINSEG", "2.0")): break
        ux, uy = (c[0] - a[0]) / Ls, (c[1] - a[1]) / Ls
        nx, ny = -uy, ux
        mid = ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2)
        # outward = away from the partner
        pl = [LineString([P(q.GetStart()), P(q.GetEnd())]) for q in partner if q.GetLayer() == t.GetLayer()]
        if not pl: continue
        pm = min(pl, key=lambda g: g.distance(Point(mid)))
        cp = pm.interpolate(pm.project(Point(mid)))
        if (cp.x - mid[0]) * nx + (cp.y - mid[1]) * ny > 0: nx, ny = -nx, -ny
        w = mm(t.GetWidth())
        obs = obstacles(t.GetLayer(), {short})
        PART = os.environ.get("TUNE_PART") == "1"
        for amp in ((0.7, 0.6, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1) if PART else (0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45)):
            per = 2 * amp * (math.sqrt(2) - 1)
            nb = max(1, math.ceil((need - 0.005) / per))
            if PART:   # partial compensation: as many bumps as fit on this segment
                nbmax = int((Ls - 0.6 + 0.3) // (2 * amp + 0.6))
                if nbmax < 1: continue
                nb = min(nb, nbmax)
            # trim last bump amplitude for exactness: use uniform amp solving nb*0.828*amp = need
            amp2 = min(amp, need / (nb * 2 * (math.sqrt(2) - 1))) if PART else need / (nb * 2 * (math.sqrt(2) - 1))
            unit = 2 * amp2 + 0.3
            if nb * unit + (nb - 1) * 0.3 > Ls - 0.6: continue
            pts = bump_path(a, c, ux, uy, nx, ny, amp2, nb)
            geom = LineString(pts).buffer(w / 2 + CLR).difference(LineString([a, c]).buffer(w / 2 + CLR + 0.01))
            if geom.intersects(obs): continue
            # replace
            lay, net = t.GetLayer(), t.GetNet()
            b.Remove(t)
            for p0, p1 in zip(pts, pts[1:]):
                if math.dist(p0, p1) < 1e-4: continue
                n = pcbnew.PCB_TRACK(b); n.SetStart(pcbnew.VECTOR2I(MM(p0[0]), MM(p0[1])))
                n.SetEnd(pcbnew.VECTOR2I(MM(p1[0]), MM(p1[1]))); n.SetWidth(MM(w)); n.SetLayer(lay); n.SetNet(net)
                b.Add(n)
            return nb * 2 * amp2 * (math.sqrt(2) - 1), "%s %d bump(s) a=%.3f on %s" % (short, nb, amp2, b.GetLayerName(lay))
    return 0.0, "FAILED"

pairs = sorted({n[:-2] for n in lengths()[0] if n.endswith("_P") and re.match(os.environ.get("TUNE_RE", r"(FP|FS)_(TX|RX)\d+_P|(FP|FS)_REFCLK_P"), n)})
for p in pairs:
    for _ in range(int(os.environ.get("TUNE_IT", "3"))):
        d, msg = tune(p)
        print("%-10s %s" % (p, msg))
        if msg in ("FAILED", "ok") or os.environ.get("TUNE_PART") != "1": break
pcbnew.SaveBoard(DST, b)
