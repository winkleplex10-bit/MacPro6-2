"""BP rev A1 high-speed router: J1 <-> J9 (FP x16) and J10 (FS x4) PCIe pairs, REFCLKs, MCIO sideband breakout.
Fixed breakout patterns at J1 / J9 / J10 (see PROGRESS_A1.md) + A* centerline router (0.2 mm grid, 45 deg, turn penalty)
for the bundles, P/N by miter offset, exact endpoints by 2-segment solve. All tracks/vias locked.
Run after build_bp.py; rewrites backplane.kicad_pcb (removes all tracks/vias first) and work/hs_geom.json."""
import pcbnew, math, json, heapq, os, sys
import numpy as np, shapely
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
from pcbnew import FromMM, ToMM, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.abspath(os.path.join(HERE, ".."))
PCB = os.path.join(PRJ, "backplane.kicad_pcb")
CX, CY = 150.0, 100.0
L1, L2, L3, L4 = pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu
LN = {L1: "L1", L3: "L3", L4: "L4"}
# pair geometry (zsolve, JLC04161H-7628)
GEO = {L1: (0.26, 0.385), L3: (0.21, 0.337), L4: (0.26, 0.385)}   # width, centre sep
NECK = 0.15; VIA_D, VIA_H = 0.45, 0.25; CLR = 0.1
PITCH = {L1: 1.15, L3: 1.1, L4: 1.15}
PITCH_THROAT = 0.95
GRID = 0.2; TURN_PEN = 1.2
def P(x, y): return VECTOR2I(FromMM(CX + x), FromMM(CY - y))
def D(v): return (ToMM(v.x) - CX, CY - ToMM(v.y))

b = pcbnew.LoadBoard(PCB)
for t in list(b.GetTracks()): b.Remove(t)
NETS = {n.GetNetname(): n for n in b.GetNetInfo().NetsByName().values()} if hasattr(b.GetNetInfo(), "NetsByName") else None
def net(name):
    n = b.FindNet(name)
    if n is None: sys.exit("no net " + name)
    return n
FP = {f.GetReference(): f for f in b.GetFootprints()}
def pad(ref, num):
    for p in FP[ref].Pads():
        if p.GetNumber() == num: return p
    sys.exit("no pad %s.%s" % (ref, num))
def padxy(ref, num): return D(pad(ref, num).GetPosition())
def padnet(ref, num): return pad(ref, num).GetNetname()

# ---------------- geometry bookkeeping ----------------
GEOM = {L1: [], L3: [], L4: [], "all": []}   # shapely copper (exact) for collision checks of later steps
ALLC = []   # (layer, geom, netname)
LANE_COPPER = set()
BOBJ = []
def add_track(layer, pts, netname, w, lane=False):
    n = net(netname); objs = []
    for a, c in zip(pts[:-1], pts[1:]):
        if math.hypot(c[0] - a[0], c[1] - a[1]) < 1e-4: continue
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetLayer(layer); t.SetWidth(FromMM(w)); t.SetNet(n); t.SetLocked(True); b.Add(t); objs.append(t)
    BOBJ.append(objs)
    g = LineString(pts).buffer(w / 2, cap_style="round", join_style="round")
    GEOM[layer].append(g); ALLC.append((layer, g, netname))
    if lane: LANE_COPPER.add(len(ALLC) - 1)
def add_via(xy, netname):
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(*xy)); v.SetWidth(L1, FromMM(VIA_D)); v.SetDrill(FromMM(VIA_H)); v.SetNet(net(netname)); v.SetLocked(True)
    v.SetLayerPair(L1, L4); b.Add(v); BOBJ.append([v])
    g = Point(xy).buffer(VIA_D / 2, 24); GEOM["all"].append(g); ALLC.append(("all", g, netname))

# ---------------- static obstacles from the board ----------------
def pad_poly(p):
    x, y = D(p.GetPosition()); sx, sy = ToMM(p.GetSize().x), ToMM(p.GetSize().y)
    ang = -p.GetOrientationDegrees()   # KiCad y-down -> disc y-up
    if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE: return Point(x, y).buffer(sx / 2, 24)
    if p.GetShape() == pcbnew.PAD_SHAPE_OVAL:
        r = min(sx, sy) / 2; L = max(sx, sy) / 2 - r
        seg = LineString([(-L, 0), (L, 0)]) if sx >= sy else LineString([(0, -L), (0, L)])
        g = seg.buffer(r, 24)
    else:
        g = box(-sx / 2, -sy / 2, sx / 2, sy / 2)
    return shapely.affinity.translate(shapely.affinity.rotate(g, ang, origin=(0, 0)), x, y)
STATIC = {L1: [], L3: [], L4: []}
HOLES = []
for f in b.GetFootprints():
    for p in f.Pads():
        g = pad_poly(p)
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            dr = ToMM(p.GetDrillSize().x)
            HOLES.append((D(p.GetPosition()), dr, p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH))
            hg = Point(D(p.GetPosition())).buffer(dr / 2 + 0.1, 24) if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else g
            for L in STATIC: STATIC[L].append(hg if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else g)
        else:
            if p.IsOnLayer(L1): STATIC[L1].append(g)
            if p.IsOnLayer(L4): STATIC[L4].append(g)
R0 = None
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_CIRCLE:
        R0 = ToMM(d.GetRadius()); OC = D(d.GetCenter())
EDGE = Point(OC).buffer(R0 + 5, 128).difference(Point(OC).buffer(R0 - 0.4, 128))
KEEP = []
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetDoNotAllowTracks():
        o = z.Outline(); pts = [D(o.CVertex(i)) for i in range(o.OutlineCount() and o.Outline(0).PointCount())]
        KEEP.append(Polygon(pts))
for L in STATIC: STATIC[L] += [EDGE] + KEEP

# ---------------- connector frames ----------------
class Frame:
    def __init__(s, ref):
        s.ref = ref
        B1, B2, A1 = padxy(ref, "B1"), padxy(ref, "B2"), padxy(ref, "A1")
        t = (B2[0] - B1[0], B2[1] - B1[1]); l = math.hypot(*t); s.t = (t[0] / l, t[1] / l)
        n = (B1[0] - A1[0], B1[1] - A1[1]); l = math.hypot(*n); s.n = (n[0] / l, n[1] / l); s.o = B1
    def g(s, u, v): return (s.o[0] + u * s.t[0] + v * s.n[0], s.o[1] + u * s.t[1] + v * s.n[1])
    def u(s, k, row="B"):
        x, y = padxy(s.ref, "%s%d" % (row, k)); return (x - s.o[0]) * s.t[0] + (y - s.o[1]) * s.t[1]
    def gl(s, pts): return [s.g(u, v) for (u, v) in pts]
F9, F10 = Frame("J9"), Frame("J10")

# ---------------- fixed patterns ----------------
MLANES = [(2, 0), (5, 1), (14, 2), (17, 3), (20, 4), (23, 5), (32, 6), (35, 7), (39, 8), (42, 9), (45, 10), (48, 11), (51, 12), (54, 13), (57, 14), (60, 15)]
MGND = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 38, 41, 44, 47, 50, 53, 56, 59, 62]
def mcio_pattern(F, nlanes, gnd_skip=lambda u: False, l4_rx=()):
    """returns entries: {lane: {'tx': (pt, heading), 'rx': (pt, heading)}} in global coords; draws the breakouts."""
    ent = {}
    hd = (-F.n[0], -F.n[1])
    W1, S1 = GEO[L1]; W3, S3 = GEO[L3]
    for p, l in MLANES[:nlanes]:
        uP = F.u(p); uc = uP + 0.3
        tP, tN = padnet(F.ref, "B%d" % p), padnet(F.ref, "B%d" % (p + 1))
        rP, rN = padnet(F.ref, "A%d" % p), padnet(F.ref, "A%d" % (p + 1))
        # TX vias + L1 stubs to B pads
        add_via(F.g(uc, 1.6), tP); add_via(F.g(uc, 2.5), tN)
        add_track(L1, F.gl([(uc, 1.6), (uc - 0.3, 1.3), (uc - 0.3, 0.0)]), tP, NECK)
        add_track(L1, F.gl([(uc, 2.5), (uc + 0.45, 2.05), (uc + 0.45, 1.0), (uc + 0.3, 0.85), (uc + 0.3, 0.0)]), tN, NECK)
        # TX L3 entry
        add_track(L3, F.gl([(uc - S3 / 2, 3.4), (uc - S3 / 2, 2.75), (uc, 2.5)]), tN, W3)
        add_track(L3, F.gl([(uc + S3 / 2, 3.4), (uc + 0.45, 3.4 - (0.45 - S3 / 2))]), tP, W3)
        add_track(L3, F.gl([(uc + 0.45, 3.4 - (0.45 - S3 / 2)), (uc + 0.45, 1.85), (uc, 1.6)]), tP, NECK)
        ur = uc + 0.9
        if l in l4_rx:   # RX lane arriving on L4 from the OUTER side (around the pin-1 end): between-row vias + outer tail
            add_via(F.g(uc - 0.3, -1.475), rP); add_via(F.g(uc + 0.3, -1.475), rN)
            add_track(L1, F.gl([(uc - 0.3, -1.475), (uc - 0.3, -2.95)]), rP, NECK)
            add_track(L1, F.gl([(uc + 0.3, -1.475), (uc + 0.3, -2.95)]), rN, NECK)
            W4, S4 = GEO[L4]; h4 = S4 / 2; vo = -4.9; ut = uc
            cl = LineString(F.gl([(-1.2, vo), (ut - 0.45, vo), (ut, vo + 0.45), (ut, -2.3)]))
            Pg = list(cl.offset_curve(-h4, join_style="mitre").coords); Ng = list(cl.offset_curve(h4, join_style="mitre").coords)
            if math.dist(Pg[0], F.g(-1.2, vo)) > math.dist(Pg[-1], F.g(-1.2, vo)): Pg = Pg[::-1]
            if math.dist(Ng[0], F.g(-1.2, vo)) > math.dist(Ng[-1], F.g(-1.2, vo)): Ng = Ng[::-1]
            add_track(L4, Pg + [F.g(uc - 0.3, -1.475)], rP, W4)    # P = left of travel (+v side on the outer run)
            add_track(L4, Ng + [F.g(uc + 0.3, -1.475)], rN, W4)
            ent[l] = {"tx": (F.g(uc, 3.4), hd, tP, tN), "rx": (F.g(-1.2, vo), F.t, rP, rN), "rx_layer": L4}
            continue
        # RX dive vias, L1 entry
        add_via(F.g(ur, 1.6), rP); add_via(F.g(ur, 2.5), rN)
        add_track(L1, F.gl([(ur - S1 / 2, 3.4), (ur - S1 / 2, 2.69), (ur, 2.5)]), rN, W1)
        add_track(L1, F.gl([(ur + S1 / 2, 3.4), (ur + 0.45, 3.4 - (0.45 - S1 / 2))]), rP, W1)
        add_track(L1, F.gl([(ur + 0.45, 3.4 - (0.45 - S1 / 2)), (ur + 0.45, 1.85), (ur, 1.6)]), rP, NECK)
        # L4 breakout to between-row vias, L1 to A pads
        add_track(L4, F.gl([(ur, 1.6), (ur, 0.9), (uc - 0.3, -0.3), (uc - 0.3, -1.475)]), rP, 0.1)
        add_track(L4, F.gl([(ur, 2.5), (uc + 1.35, 2.05), (uc + 1.35, 0.6), (uc + 0.3, -0.45), (uc + 0.3, -1.475)]), rN, 0.1)
        add_via(F.g(uc - 0.3, -1.475), rP); add_via(F.g(uc + 0.3, -1.475), rN)
        add_track(L1, F.gl([(uc - 0.3, -1.475), (uc - 0.3, -2.95)]), rP, NECK)
        add_track(L1, F.gl([(uc + 0.3, -1.475), (uc + 0.3, -2.95)]), rN, NECK)
        ent[l] = {"tx": (F.g(uc, 3.4), hd, tP, tN), "rx": (F.g(ur, 3.4), hd, rP, rN)}
    for g in MGND:
        ug = F.u(g)
        add_track(L1, F.gl([(ug, 0.0), (ug, -2.95)]), "GND", 0.2)
        if not gnd_skip(ug):
            add_track(L1, F.gl([(ug, -2.95), (ug, -4.1)]), "GND", 0.2); add_via(F.g(ug, -4.1), "GND")
    # REFCLK A11/A12 vias (outer side)
    for k in (11, 12):
        uk = F.u(k, "A"); add_track(L1, F.gl([(uk, -2.95), (uk, -4.1)]), padnet(F.ref, "A%d" % k), NECK); add_via(F.g(uk, -4.1), padnet(F.ref, "A%d" % k))
    # sideband PERST B11, PRSNT B12 -> inner vias
    u10, u11, u12, u13 = F.u(10), F.u(11), F.u(12), F.u(13)
    nPE, nPR = padnet(F.ref, "B11"), padnet(F.ref, "B12")
    add_track(L1, F.gl([(u11, 0.0), (u11, 0.9), (u10, 1.45)]), nPE, NECK); add_via(F.g(u10, 1.45), nPE)
    add_track(L1, F.gl([(u12, 0.0), (u12, 0.9), (u13, 1.45)]), nPR, NECK); add_via(F.g(u13, 1.45), nPR)
    return ent, (nPE, nPR, u10, u13)

ENT9, sb9 = mcio_pattern(F9, 16, l4_rx=(0,))
ENT10, sb10 = mcio_pattern(F10, 4, gnd_skip=lambda u: u > 25.0)
# sideband L4 runs under the A-row channel
nPE, nPR, u10, u13 = sb9
add_track(L4, F9.gl([(u10, 1.45), (u10, -3.0), (36.65, -3.0), (36.65, -5.7)]), nPE, 0.1); add_via(F9.g(36.65, -5.7), nPE)
add_track(L4, F9.gl([(u13, 1.45), (u13, -2.6), (37.15, -2.6), (37.15, -5.9), (37.45, -6.2)]), nPR, 0.1); add_via(F9.g(37.45, -6.2), nPR)
nPE, nPR, u10, u13 = sb10
add_track(L4, F10.gl([(u10, 1.45), (u10, -2.6), (0.3, -2.6), (-0.6, -1.7), (-0.6, -1.55)]), nPE, 0.1); add_via(F10.g(-0.6, -1.55), nPE)
add_track(L4, F10.gl([(u13, 1.45), (u13, -3.0), (0.0, -3.0), (-0.6, -2.4)]), nPR, 0.1); add_via(F10.g(-0.6, -2.4), nPR)

# ---------------- J1 patterns ----------------
J1 = {}
for p in FP["J1"].Pads():
    if p.GetNumber()[:1] in "AB" and p.GetNumber()[1:].isdigit(): J1[p.GetNumber()] = (D(p.GetPosition()), p.GetNetname())
YA, YB = J1["A2"][0][1], J1["B2"][0][1]
VIA_A, VIA_B, YS = -15.4, -9.9, -9.4
PCIE_A = [k for k in range(1, 113) if J1["A%d" % k][1].startswith(("FP_TX", "FS_TX", "FP_REFCLK", "FS_REFCLK")) or
          (J1["A%d" % k][1] == "GND" and 2 <= k <= 72)]
PCIE_B = [k for k in range(1, 113) if J1["B%d" % k][1] == "GND" and 1 <= k <= 72]
for k in PCIE_A:
    (x, y), n = J1["A%d" % k]; add_via((x, VIA_A), n); add_track(L1, [(x, y), (x, VIA_A)], n, 0.2 if n == "GND" else NECK)
for k in PCIE_B:
    (x, y), n = J1["B%d" % k]; add_via((x, VIA_B), n); add_track(L1, [(x, y), (x, VIA_B)], n, 0.2)
for k in range(51, 113):   # B-row low-speed / power / GND escapes: via north of the pad (L1 north side is the bundle area)
    (x, y), n = J1["B%d" % k]
    if not n or n.startswith(("FP_", "FS_")) or k in PCIE_B or n.startswith("unconnected"): continue
    ax = [J1["A%d" % kk][0][0] for kk in PCIE_A if J1["A%d" % kk][1] != "GND"]
    if any(abs(x - a) < 0.75 for a in ax):   # would sit on an A-row L3 stub: via between the rows, shifted left
        vx = x - 0.87; add_track(L1, [(x, y), (x, y - 0.6), (vx, -12.6)], n, NECK); add_via((vx, -12.6), n); continue
    add_via((x, VIA_B), n); add_track(L1, [(x, y), (x, VIA_B)], n, 0.2 if n in ("GND", "3V3_SB", "5V_SBY") else NECK)
def j1_pairs(row, pre):
    out = {}
    for k in range(1, 112):
        n = J1["%s%d" % (row, k)][1]
        if n.startswith(pre) and n.endswith("_P"):
            nn = J1["%s%d" % (row, k + 1)][1]; assert nn == n[:-2] + "_N", (k, n, nn)
            out[n[:-2]] = (k, J1["%s%d" % (row, k)][0][0], J1["%s%d" % (row, k + 1)][0][0], n, nn)
    return out
def j1_tx_start(name, kx):   # L3 from A-row vias north to (xc, YS)
    k, xP, xN, nP, nN = kx; xc = (xP + xN) / 2; h = GEO[L3][1] / 2; W = GEO[L3][0]
    add_track(L3, [(xP, VIA_A), (xc + h, VIA_A + (xP - xc - h)), (xc + h, YS)], nP, W)
    add_track(L3, [(xN, VIA_A), (xc - h, VIA_A + (xc - h - xN)), (xc - h, YS)], nN, W)
    return (xc, YS)
def j1_rx_start(name, kx):   # L1 from B pads north
    k, xP, xN, nP, nN = kx; xc = (xP + xN) / 2; h = GEO[L1][1] / 2; W = GEO[L1][0]
    add_track(L1, [(xP, YB), (xP, YB + 0.75), (xc + h, YB + 0.75 + (xP - xc - h)), (xc + h, YS)], nP, W)
    add_track(L1, [(xN, YB), (xN, YB + 0.75), (xc - h, YB + 0.75 + (xc - h - xN)), (xc - h, YS)], nN, W)
    return (xc, YS)
TXA = j1_pairs("A", ("FP_TX", "FS_TX", "FP_REFCLK", "FS_REFCLK")); RXB = j1_pairs("B", ("FP_RX", "FS_RX"))
START = {}
for nm, kx in TXA.items(): START[nm] = (j1_tx_start(nm, kx), (0.0, 1.0), kx[3], kx[4])
for nm, kx in RXB.items(): START[nm] = (j1_rx_start(nm, kx), (0.0, 1.0), kx[3], kx[4])
print("J1 starts:", {k: tuple(round(c, 2) for c in v[0]) for k, v in sorted(START.items())})

# ---------------- A* bundle router ----------------
XMIN, XMAX, YMIN, YMAX = -58.0, 58.0, -17.0, 58.0
NX, NY = int(round((XMAX - XMIN) / GRID)) + 1, int(round((YMAX - YMIN) / GRID)) + 1
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
def dir_index(h):
    a = math.atan2(h[1], h[0]); return int(round(a / (math.pi / 4))) % 8
HALF = {L: GEO[L][1] / 2 + GEO[L][0] / 2 for L in GEO}
MARGIN = 0.04
THROAT = Polygon(F9.gl([(-2.0, 2.0), (12.0, 2.0), (12.0, 8.0), (-2.0, 8.0)]))
CNT = {L: np.zeros((NY, NX), np.int16) for L in (L1, L3, L4)}
def rast(geom):
    x0, y0, x1, y1 = geom.bounds
    i0, i1 = max(0, int(math.floor((x0 - XMIN) / GRID))), min(NX - 1, int(math.ceil((x1 - XMIN) / GRID)))
    j0, j1 = max(0, int(math.floor((y0 - YMIN) / GRID))), min(NY - 1, int(math.ceil((y1 - YMIN) / GRID)))
    if i1 < i0 or j1 < j0: return None
    xs = XMIN + GRID * np.arange(i0, i1 + 1); ys = YMIN + GRID * np.arange(j0, j1 + 1)
    X, Y = np.meshgrid(xs, ys)
    m = shapely.contains_xy(geom, X, Y)
    return (j0, i0, m)
def cnt_add(L, geom, sign=1):
    r = rast(geom)
    if r is None: return
    j0, i0, m = r; CNT[L][j0:j0 + m.shape[0], i0:i0 + m.shape[1]] += sign * m.astype(np.int16)
ITEMS = []   # (layers, geom_buffered_by_layer dict, net)
def register(layer, g, netname, margin=None):
    lays = (L1, L3, L4) if layer == "all" else (layer,)
    mg = MARGIN if margin is None else margin
    gb = {L: g.buffer(HALF[L] + CLR + mg, 8) for L in lays}
    ITEMS.append((lays, gb, netname))
    for L in lays: cnt_add(L, gb[L])
for L in (L1, L3, L4):
    for g in STATIC[L]: cnt_add(L, g.buffer(HALF[L] + CLR + MARGIN, 8))
for (layer, g, n) in ALLC: register(layer, g, n)
NREG = len(ALLC)
def sync_items():
    global NREG
    for k in range(NREG, len(ALLC)):
        layer, g, n = ALLC[k]; register(layer, g, n, 0.03 if k in LANE_COPPER else None)
    NREG = len(ALLC)

def astar(L, s, hs, g, hg, extra_block=None, wh=1.15):
    blocked = CNT[L] > 0
    if extra_block is not None: blocked = blocked | extra_block
    si, sj = int(round((s[0] - XMIN) / GRID)), int(round((s[1] - YMIN) / GRID))
    gi, gj = int(round((g[0] - XMIN) / GRID)), int(round((g[1] - YMIN) / GRID))
    ds, dg = dir_index(hs), dir_index(hg)
    blocked[sj, si] = False; blocked[gj, gi] = False
    SQ2 = math.sqrt(2)
    def hfun(i, j):
        dx, dy = abs(i - gi), abs(j - gj); return wh * GRID * (max(dx, dy) + (SQ2 - 1) * min(dx, dy))
    start = (si, sj, ds); best = {start: 0.0}; prev = {}
    pq = [(hfun(si, sj), 0.0, start)]
    n = 0
    while pq:
        f, c, st = heapq.heappop(pq)
        if best.get(st, 1e18) < c - 1e-9: continue
        i, j, d = st
        if (i, j, d) == (gi, gj, dg):
            path = [st]
            while path[-1] in prev: path.append(prev[path[-1]])
            path.reverse(); return [(XMIN + GRID * a, YMIN + GRID * bb) for (a, bb, _) in path], n
        n += 1
        if n > 3000000: return None, n
        for dd, pen in ((0, 0.0), (1, TURN_PEN), (-1, TURN_PEN)):
            nd = (d + dd) % 8; di, dj = DIRS[nd]; ni, nj = i + di, j + dj
            if not (0 <= ni < NX and 0 <= nj < NY) or blocked[nj, ni]: continue
            nc = c + GRID * (SQ2 if nd % 2 else 1.0) + pen
            ns = (ni, nj, nd)
            if nc < best.get(ns, 1e18) - 1e-9:
                best[ns] = nc; prev[ns] = st; heapq.heappush(pq, (nc + hfun(ni, nj), nc, ns))
    return None, n

def simplify(pts):
    out = [pts[0]]
    for k in range(1, len(pts) - 1):
        a, b0, c = out[-1], pts[k], pts[k + 1]
        if abs((b0[0] - a[0]) * (c[1] - b0[1]) - (b0[1] - a[1]) * (c[0] - b0[0])) < 1e-6: continue
        out.append(b0)
    out.append(pts[-1]); return out
def unit(a, b0):
    dx, dy = b0[0] - a[0], b0[1] - a[1]; l = math.hypot(dx, dy); return (dx / l, dy / l)
def solve2(d0, d1, e):   # e = a*d0 + b*d1
    det = d0[0] * d1[1] - d0[1] * d1[0]
    return ((e[0] * d1[1] - e[1] * d1[0]) / det, (d0[0] * e[1] - d0[1] * e[0]) / det)
def seglen(q, k): return math.dist(q[k], q[k + 1])
def exactify(pts, S, G):
    q = [list(p) for p in simplify(pts)]
    n = len(q) - 1
    if n < 2: raise RuntimeError("straight path")
    # start: e = a*d0 + b*dm, shift q1..qm by b*dm, q0 by e
    e = (S[0] - q[0][0], S[1] - q[0][1]); d0 = unit(q[0], q[1]); best = None
    for m in range(1, n):
        dm = unit(q[m], q[m + 1])
        if abs(d0[0] * dm[1] - d0[1] * dm[0]) < 0.5: continue
        a, bb = solve2(d0, dm, e)
        if seglen(q, 0) - a < 0.3 or seglen(q, m) - bb < 0.15: continue
        if best is None or abs(bb) < abs(best[2]): best = (m, a, bb, dm)
        if m > 6: break
    if best is None: raise RuntimeError("start fix failed")
    m, a, bb, dm = best
    for k in range(1, m + 1): q[k] = [q[k][0] + bb * dm[0], q[k][1] + bb * dm[1]]
    q[0] = list(S)
    e = (G[0] - q[n][0], G[1] - q[n][1]); dl = unit(q[n - 1], q[n]); best = None
    for m in range(n - 2, -1, -1):
        dm = unit(q[m], q[m + 1])
        if abs(dl[0] * dm[1] - dl[1] * dm[0]) < 0.5: continue
        a, bb = solve2(dl, dm, e)
        if seglen(q, n - 1) + a < 0.15 or seglen(q, m) + bb < (0.3 if m == 0 else 0.15): continue
        if best is None or abs(bb) < abs(best[2]): best = (m, a, bb, dm)
        if m < n - 8: break
    if best is None: raise RuntimeError("end fix failed")
    m, a, bb, dm = best
    for k in range(m + 1, n): q[k] = [q[k][0] + bb * dm[0], q[k][1] + bb * dm[1]]
    q[n] = list(G)
    return [tuple(p) for p in q]

ROUTES = {}
def dbg_png(L, x0, x1, y0, y1, fn, marks=(), extra=None):
    from PIL import Image, ImageDraw
    i0, i1 = int((x0 - XMIN) / GRID), int((x1 - XMIN) / GRID); j0, j1 = int((y0 - YMIN) / GRID), int((y1 - YMIN) / GRID)
    blk = (CNT[L][j0:j1, i0:i1] > 0).astype(np.uint8) * 2
    if extra is not None: blk |= extra[j0:j1, i0:i1].astype(np.uint8)
    sub = blk[::-1]; S = 5
    im = Image.new("RGB", (sub.shape[1] * S, sub.shape[0] * S), "white"); d = ImageDraw.Draw(im)
    ys, xs = np.nonzero(sub)
    for j, i in zip(ys, xs): d.rectangle([i * S, j * S, i * S + S - 1, j * S + S - 1], fill=(90, 90, 90) if sub[j, i] & 2 else (190, 190, 255))
    tp = lambda p: ((p[0] - x0) / GRID * S, (y1 - p[1]) / GRID * S)
    for k, r in ROUTES.items():
        col = {"L1": "red", "L3": "orange", "L4": "green"}[r["layer"]]
        d.line([tp(p) for p in r["cl"]], fill=col, width=2)
    for e in marks: c = tp(e); d.ellipse([c[0] - 4, c[1] - 4, c[0] + 4, c[1] + 4], fill="blue")
    im.save(fn)
def lead(p, h, l): return (p[0] + h[0] * l, p[1] + h[1] * l)
def route_pair(name, L, S, hs, G, hg, nP, nN, reserve=(), lead_s=1.0, lead_g=0.3, wh=1.15, record=True, blocks=()):
    sync_items()
    own = [it for it in ITEMS if it[2] in (nP, nN)]
    for lays, gb, n in own:
        for LL in lays: cnt_add(LL, gb[LL], -1)
    s1, g1 = lead(S, hs, lead_s), lead(G, hg, -lead_g)
    pts = None
    for dp in (0.0, 0.06, 0.12):
        extra = np.zeros((NY, NX), bool)
        geoms = list(reserve) + list(blocks) + [c.buffer(PITCH[L] - dp, 8).difference(THROAT).union(c.buffer(PITCH_THROAT, 8).intersection(THROAT)) for c in CL[L]]
        if L == L4: geoms += [ALLC[k][1].buffer(0.45) for k in LANE_COPPER if ALLC[k][0] == L3]
        if L == L3: geoms += [ALLC[k][1].buffer(0.45) for k in LANE_COPPER if ALLC[k][0] == L4]
        for geom in geoms:
            r = rast(geom)
            if r: j0, i0, m = r; extra[j0:j0 + m.shape[0], i0:i0 + m.shape[1]] |= m
        pts, n = astar(L, s1, hs, g1, hg, extra, wh)
        if pts is not None:
            try:
                q = simplify([S] + exactify(pts, s1, g1) + [G])
            except RuntimeError as e:
                print("   exactify:", e); pts = None; continue
            if dp: print("   (pitch relaxed by %.2f)" % dp)
            break
    for lays, gb, nn in own:
        for LL in lays: cnt_add(LL, gb[LL], +1)
    if pts is None:
        print("  FAIL", name, "expanded", n)
        dbg_png(L, min(S[0], G[0]) - 6, max(S[0], G[0]) + 6, min(S[1], G[1]) - 6, max(S[1], G[1]) + 6, "/tmp/fail_%s.png" % name, [S, G, s1, g1], extra)
        return None
    cl = LineString(q)
    w, sep = GEO[L]
    Pl = list(cl.offset_curve(-sep / 2, join_style="mitre", mitre_limit=5.0).coords)
    Nl = list(cl.offset_curve(sep / 2, join_style="mitre", mitre_limit=5.0).coords)
    def fixdir(pl, end_expect):
        return pl if math.dist(pl[0], end_expect) < math.dist(pl[-1], end_expect) else pl[::-1]
    rs = (hs[1], -hs[0]); Pl = fixdir(Pl, (S[0] + rs[0] * sep / 2, S[1] + rs[1] * sep / 2)); Nl = fixdir(Nl, (S[0] - rs[0] * sep / 2, S[1] - rs[1] * sep / 2))
    add_track(L, Pl, nP, w, True); add_track(L, Nl, nN, w, True)
    CL[L].append(cl)
    ROUTES[name] = {"layer": LN[L], "cl": q, "P": Pl, "N": Nl, "nP": nP, "nN": nN}
    lp, ln_ = LineString(Pl).length, LineString(Nl).length
    print("  routed %-10s %s len %.2f skew %.3f expanded %d" % (name, LN[L], cl.length, lp - ln_, n))
    return q
def transition_swap(T, h, nP, nN, La, Lb):
    """layer change La->Lb at T with P/N swap (P right on La -> P left on Lb). N via behind-left, P via ahead-left... see notes."""
    r = (h[1], -h[0]); g = lambda a, c: (T[0] + r[0] * a + h[0] * c, T[1] + r[1] * a + h[1] * c)
    sa, sb = GEO[La][1] / 2, GEO[Lb][1] / 2
    VN, VP = g(-0.35, 0.0), g(-0.35, 1.2)
    # La: N straight to its via, P forward then across (over N's Lb run) to its via
    add_track(La, [g(-sa, 0.0), VN], nN, NECK)
    add_track(La, [g(sa, 0.0), g(sa, 0.3), VP], nP, NECK)
    # Lb: N from VN to the right lane, P from VP to the left lane; pair continues from 1.9 ahead
    add_track(Lb, [VN, g(sb, 0.9), g(sb, 1.9)], nN, NECK)
    add_track(Lb, [VP, g(-sb, 1.55), g(-sb, 1.9)], nP, NECK)
    add_via(VN, nN); add_via(VP, nP)
    add_via(g(1.35, 0.6), "GND"); add_via(g(-1.45, 0.6), "GND")
    return g(0.0, 1.9)
def transition(T, h, nP, nN, La, Lb):
    """pair layer change at T (heading h): signal vias at +-0.45 across, GND vias at +-1.3; short stubs on both layers."""
    r = (h[1], -h[0])
    for Lx in (La, Lb):
        sep = GEO[Lx][1]
        add_track(Lx, [(T[0] + r[0] * sep / 2, T[1] + r[1] * sep / 2), (T[0] + r[0] * 0.45, T[1] + r[1] * 0.45)], nP, NECK)
        add_track(Lx, [(T[0] - r[0] * sep / 2, T[1] - r[1] * sep / 2), (T[0] - r[0] * 0.45, T[1] - r[1] * 0.45)], nN, NECK)
    add_via((T[0] + r[0] * 0.45, T[1] + r[1] * 0.45), nP); add_via((T[0] - r[0] * 0.45, T[1] - r[1] * 0.45), nN)
    add_via((T[0] + r[0] * 1.3, T[1] + r[1] * 1.3), "GND"); add_via((T[0] - r[0] * 1.3, T[1] - r[1] * 1.3), "GND")
CL = {L1: [], L3: [], L4: []}
def term_reserve(S, hs, L, l=1.0):
    return LineString([S, lead(S, hs, l)]).buffer(PITCH[L], 8)

def route_group(tag, L, lanes, ends, key):
    # reserve all terminals first
    res = {}
    for l in lanes:
        S, hs, nP, nN = START["%s%d" % (tag, l)]
        G, hg, gP, gN = ends[l][key]
        assert (nP, nN) == (gP, gN), (tag, l, nP, gP)
        s1 = lead(S, hs, 1.0); nw = (-math.sqrt(0.5), math.sqrt(0.5))
        res[l] = [LineString([S, s1, lead(s1, nw, 1.0)]).buffer(PITCH[L] - 0.08, 8), term_reserve(G, (-hg[0], -hg[1]), L, 0.3)]
    ok = True
    for l in lanes:
        if ends[l].get(key + "_layer") == L4: continue
        S, hs, nP, nN = START["%s%d" % (tag, l)]; G, hg, _, _ = ends[l][key]
        others = [g for k in lanes if k != l and k not in DONE for g in res[k]]
        q = route_pair("%s%d" % (tag, l), L, S, hs, G, hg, nP, nN, others)
        if q is None: ok = False
        else: DONE.add(l)
    DONE.clear(); return ok
DONE = set()
def refclk_tail(F, L, nP, nN, vo=-5.0):
    """L3 tail on the connector's outer side: arrive heading +u at (3.5, vo); P inner -> A11 via, N outer -> A12 via."""
    w, sep = GEO[L]; u11, u12 = F.u(11, "A"), F.u(12, "A"); h = sep / 2
    if vo > -5.5:
        add_track(L, F.gl([(3.5, vo + h), (u11, vo + h), (u11, -4.1)]), nP, w)
        add_track(L, F.gl([(3.5, vo - h), (u12, vo - h), (u12, -4.1)]), nN, w)
    else:
        dp = (vo + h) + 4.5315; dn = (vo - h) + 4.5685
        add_track(L, F.gl([(3.5, vo + h), (u11 + dp, vo + h), (u11, -4.5315), (u11, -4.1)]), nP, w)
        add_track(L, F.gl([(3.5, vo - h), (u12 + dn, vo - h), (u12, -4.5685), (u12, -4.1)]), nN, w)
    return F.g(3.5, vo), F.t
STAGE = sys.argv[1] if len(sys.argv) > 1 else "all"
print("== FP TX (L3)"); route_group("FP_TX", L3, list(range(15, -1, -1)), ENT9, "tx")
print("== FP RX (L1)"); route_group("FP_RX", L1, list(range(15, -1, -1)), ENT9, "rx")
print("== FP RX0: L1 -> (swap) L4 under J10, around J9 pin-1 end")
def rx_l4(name, ent, Tcands):
    S, hs, nP, nN = START[name]; G, hg, _, _ = ent
    for T in Tcands:
        hT = (0.0, 1.0)
        zone = Point(T).buffer(1.9)
        if any(g.intersects(zone) for (lay, g, nn) in ALLC if lay in (L3, L4, "all") and nn != "GND"):
            print("   T", T, "occupied on L3/L4"); continue
        nall = len(ALLC)
        q1 = route_pair(name + "a", L1, S, hs, T, hT, nP, nN, [], lead_g=0.5)
        if q1 is None: continue
        transition(T, hT, nP, nN, L1, L4)
        q2 = route_pair(name + "b", L4, T, hT, G, hg, nP, nN, [], lead_s=0.8, lead_g=0.3)
        if q2 is not None: print("  ", name, "transition at", T); return True
        print("   T", T, "failed on L4"); undo(nall); ROUTES.pop(name + "a", None); CL[L1].pop()
    return False
def undo(n):
    global NREG
    while len(ALLC) > n:
        k = len(ALLC) - 1; layer, g, nn = ALLC.pop(); LANE_COPPER.discard(k)
        if k < NREG:
            it = ITEMS.pop()
            for LL in it[0]: cnt_add(LL, it[1][LL], -1)
            NREG -= 1
        if layer in GEOM and GEOM[layer]: GEOM[layer].pop()
        for o in BOBJ.pop(): b.Remove(o)
cands = [(x, y) for y in (14.0, 16.0, 12.0, 18.0, 10.0, 20.0) for x in (-8.5, -9.5, -10.5, -7.5)]
if len(sys.argv) > 2: cands = [tuple(map(float, sys.argv[2].split(",")))]
rx_l4("FP_RX0", ENT9[0]["rx"], cands)
print("== FP REFCLK (L3)")
S, hs, nP, nN = START["FP_REFCLK"]; G, hg = refclk_tail(F9, L3, nP, nN, -6.4); route_pair("FP_REFCLK", L3, S, hs, G, hg, nP, nN, [], lead_g=0.5)
print("== FS TX (L3)"); route_group("FS_TX", L3, [3, 2, 1, 0], ENT10, "tx")
print("== FS REFCLK (L3)")
S, hs, nP, nN = START["FS_REFCLK"]; G, hg = refclk_tail(F10, L3, nP, nN); route_pair("FS_REFCLK", L3, S, hs, G, hg, nP, nN, [], lead_g=0.5)
print("== FS RX (L1)"); route_group("FS_RX", L1, [3, 2, 1, 0], ENT10, "rx")
json.dump({"routes": ROUTES}, open(os.path.join(PRJ, "work", "hs_routes.json"), "w"), indent=0)
pcbnew.SaveBoard(os.path.join(PRJ, "work", "bp_patterns.kicad_pcb"), b)
print("patterns saved; tracks", len(b.GetTracks()))
