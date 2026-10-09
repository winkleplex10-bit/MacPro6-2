"""Stitch GND pour islands on L1/L4 that have no GND through-via/THT pad: add a 0.45/0.25 GND via inside the island
   (clear of other-net copper on L1/L3/L4 incl. holes).  python3 tools/bp_island.py SRC DST"""
import pcbnew, sys
from shapely.geometry import Polygon, Point, LineString
from shapely.strtree import STRtree
src, dst = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(src); MM = pcbnew.FromMM
L1, L3, L4 = pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu
def P(v): return (v.x / 1e6, v.y / 1e6)
gnd = b.FindNet("GND"); gc = gnd.GetNetCode()
anch = [P(t.GetPosition()) for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == gc]
anch += [P(p.GetPosition()) for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode() == gc and p.GetDrillSize().x > 0]
obs = {L: [] for L in (L1, L3, L4)}; holes = []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        holes.append(Point(P(t.GetPosition())).buffer(t.GetDrillValue() / 2e6))
        if t.GetNetCode() != gc:
            for L in obs: obs[L].append(Point(P(t.GetPosition())).buffer(t.GetWidth(L) / 2e6))
    elif t.GetNetCode() != gc and t.GetLayer() in obs:
        obs[t.GetLayer()].append(LineString([P(t.GetStart()), P(t.GetEnd())]).buffer(t.GetWidth() / 2e6))
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetDrillSize().x > 0: holes.append(Point(P(p.GetPosition())).buffer(p.GetDrillSize().x / 2e6))
        if p.GetNetCode() == gc: continue
        for L in obs:
            if p.IsOnLayer(L) or p.GetDrillSize().x > 0:
                sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
                for o in range(sp.OutlineCount()):
                    ol = sp.COutline(o); obs[L].append(Polygon([P(ol.CPoint(k)) for k in range(ol.PointCount())]))
trees = {L: STRtree(obs[L]) for L in obs}; ht = STRtree(holes)
def okv(c):
    v = Point(c)
    for L in obs:
        for i in trees[L].query(v.buffer(0.225 + 0.16)):
            if obs[L][i].distance(v) < 0.225 + 0.15: return False
    for i in ht.query(v.buffer(0.6)):
        if holes[i].distance(v) < 0.125 + 0.26: return False
    return True
added = 0
for z in b.Zones():
    if z.GetNetCode() != gc or z.GetIsRuleArea(): continue
    for L in (L1, L4):
        if not z.IsOnLayer(L) or not z.HasFilledPolysForLayer(L): continue
        fp = z.GetFilledPolysList(L)
        for o in range(fp.OutlineCount()):
            ol = fp.COutline(o); poly = Polygon([P(ol.CPoint(k)) for k in range(ol.PointCount())])
            if not poly.is_valid: poly = poly.buffer(0)
            if any(poly.contains(Point(a)) for a in anch): continue
            inner = poly.buffer(-0.24); spot = None
            if not inner.is_empty:
                x0, y0, x1, y1 = inner.bounds; cands = []
                k = 0
                import numpy as np
                for x in np.arange(x0, x1 + 0.01, 0.1):
                    for y in np.arange(y0, y1 + 0.01, 0.1):
                        if inner.contains(Point(x, y)): cands.append((x, y))
                cands.sort(key=lambda c: Point(c).distance(inner.centroid))
                for c in cands:
                    if okv(c): spot = (round(float(c[0]), 3), round(float(c[1]), 3)); break
            print(b.GetLayerName(L), "island area %.2f" % poly.area, "at", tuple(round(v, 2) for v in poly.representative_point().coords[0]), "->", spot)
            if spot:
                v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(spot[0]), MM(spot[1]))); v.SetWidth(MM(0.45)); v.SetDrill(MM(0.25)); v.SetNet(gnd); b.Add(v)
                anch.append(spot); added += 1
                for L_ in obs: obs[L_].append(Point(spot).buffer(0.225))
                holes.append(Point(spot).buffer(0.125))
                trees = {L_: STRtree(obs[L_]) for L_ in obs}; ht = STRtree(holes)
print("added", added)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(dst, b)
