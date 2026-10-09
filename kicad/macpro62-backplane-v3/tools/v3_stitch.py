"""BP v3 6L: GND return vias next to every slot-B pair via (FS lanes 4-7 + REFCLK1), placed after all pairs are routed.
For each P/N via couple, one GND via per signal via, outward along the P-N axis (then rotated tries), clearance-checked on all layers.
usage: python3 tools/v3_stitch.py SRC DST"""
import sys, re, math, pcbnew
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree
mm = pcbnew.ToMM; MM = pcbnew.FromMM
b = pcbnew.LoadBoard(sys.argv[1]); gnd = b.FindNet("GND")
RE = re.compile(r"FS_(TX|RX)[4-7]_[PN]$|FS_REFCLK1_[PN]$")
VD, VDR, CL, CLHS, HOLE = 0.45, 0.25, 0.13, 0.2, 0.25
geo = []; holes = []
for t in b.GetTracks():
    n = t.GetNetname()
    if t.Type() == pcbnew.PCB_VIA_T:
        c = (mm(t.GetPosition().x), mm(t.GetPosition().y)); geo.append((Point(c).buffer(mm(t.GetWidth(pcbnew.F_Cu)) / 2), n, None)); holes.append(Point(c))
    else:
        geo.append((LineString([(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]).buffer(mm(t.GetWidth()) / 2), n, t.GetLayer()))
for f in b.GetFootprints():
    for p in f.Pads():
        c = (mm(p.GetPosition().x), mm(p.GetPosition().y))
        bb = p.GetBoundingBox(); from shapely.geometry import box
        geo.append((box(mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())), p.GetNetname(), "pad"))
        if p.GetDrillSize().x > 0: holes.append(Point(c).buffer(mm(p.GetDrillSize().x) / 2))
kos = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
edge = b.GetBoardEdgesBoundingBox(); cx, cy, R = mm(edge.GetCenter().x), mm(edge.GetCenter().y), mm(edge.GetWidth()) / 2
tree = STRtree([g for g, _, _ in geo])
HSRE = re.compile(r"(FP|FS)_(TX|RX|REFCLK)|USB2_|SATA0_")
def ok(q):
    pt = Point(q); disc = pt.buffer(VD / 2)
    if math.hypot(q[0] - cx, q[1] - cy) > R - 1.0: return False
    for z in kos:
        if z.Outline().Contains(pcbnew.VECTOR2I(MM(q[0]), MM(q[1]))): return False
    for i in tree.query(disc.buffer(0.4)):
        g, n, L = geo[i]
        if n == "GND" and L == "pad": 
            if g.distance(pt) < VD / 2 + 0.1: return False
            continue
        if n == "GND" and L is not None: continue          # GND tracks: fine to touch? keep clear anyway
        cl = CL + (CLHS if HSRE.match(n) else 0)
        if g.distance(disc) < cl: return False
    for h in holes:
        if h.distance(pt) < VDR / 2 + HOLE + 0.05 and h.distance(pt) > 1e-6: return False
    return True
vias = {}
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T and RE.match(t.GetNetname()):
        vias.setdefault(t.GetNetname()[:-2], []).append((mm(t.GetPosition().x), mm(t.GetPosition().y), t.GetNetname()[-1]))
added = 0; miss = 0
for pair, vs in sorted(vias.items()):
    P = [v for v in vs if v[2] == "P"]; N = [v for v in vs if v[2] == "N"]
    for vp in P:
        vn = min(N, key=lambda v: math.hypot(v[0] - vp[0], v[1] - vp[1]))
        if math.hypot(vn[0] - vp[0], vn[1] - vp[1]) > 1.2: continue
        ax = ((vp[0] - vn[0]), (vp[1] - vn[1])); l = math.hypot(*ax); ax = (ax[0] / l, ax[1] / l)
        for c, sg in ((vp, 1), (vn, -1)):
            done = False
            for rr in (0.75, 0.85, 1.0, 1.15, 1.3, 1.5):
                for ang in (0, 30, -30, 60, -60, 90, -90, 120, -120, 150, -150):
                    a = math.radians(ang); ox, oy = ax[0] * sg, ax[1] * sg
                    u = (ox * math.cos(a) - oy * math.sin(a), ox * math.sin(a) + oy * math.cos(a))
                    q = (round(c[0] + u[0] * rr, 3), round(c[1] + u[1] * rr, 3))
                    if ok(q):
                        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(q[0]), MM(q[1]))); v.SetWidth(MM(VD)); v.SetDrill(MM(VDR)); v.SetNet(gnd); v.SetLocked(True); b.Add(v)
                        geo.append((Point(q).buffer(VD / 2), "GND", None)); holes.append(Point(q)); tree = STRtree([g for g, _, _ in geo]); added += 1; done = True; break
                if done: break
            if not done: miss += 1; print("no stitch site for", pair, c[:2])
print("slot-B return vias added", added, "missing", miss)
pcbnew.SaveBoard(sys.argv[2], b)
