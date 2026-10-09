"""Print overlapping courtyard pairs (module frame) for a board."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); OX, OY = 60, 190
from shapely.geometry import Polygon
def poly(f):
    for L in (pcbnew.B_CrtYd, pcbnew.F_CrtYd):
        c = f.GetCourtyard(L)
        if c.OutlineCount():
            o = c.Outline(0); return L, Polygon([(pcbnew.ToMM(o.CPoint(i).x) - OX, OY - pcbnew.ToMM(o.CPoint(i).y)) for i in range(o.PointCount())])
    return None, None
fs = [(f.GetReference(),) + poly(f) for f in b.GetFootprints()]
fs = [x for x in fs if x[2] is not None]
for i in range(len(fs)):
    for j in range(i + 1, len(fs)):
        if fs[i][1] == fs[j][1] and fs[i][2].intersects(fs[j][2]) and fs[i][2].intersection(fs[j][2]).area > 1e-4:
            print(fs[i][0], fs[j][0], [round(v, 2) for v in fs[i][2].bounds], [round(v, 2) for v in fs[j][2].bounds])
