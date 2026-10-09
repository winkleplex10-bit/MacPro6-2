"""place the v3 BP parts (R64/Q12/R65) at the nearest free spot to an anchor (courtyard + L1 copper clear)."""
import pcbnew, sys, math
from shapely.geometry import box, LineString, Point
from shapely.ops import unary_union
mm = pcbnew.ToMM; MM = pcbnew.FromMM
src, dst = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(src)
fp = {f.GetReference(): f for f in b.GetFootprints()}
import os, json
ANCH = {"R64": (96.14, 107.5), "Q12": (99.0, 105.0), "R65": (104.0, 111.8)}
ANCH.update({k: tuple(v) for k, v in json.loads(os.environ.get("ANCH", "{}")).items()})
if os.environ.get("ONLY"): ANCH = {k: v for k, v in ANCH.items() if k in os.environ["ONLY"].split(",")}
def court(f):
    bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox() if f.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else f.GetBoundingBox(False, False)
    return box(mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
edge = b.GetBoardEdgesBoundingBox()
cop = []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T: cop.append(Point(mm(t.GetPosition().x), mm(t.GetPosition().y)).buffer(0.225))
    elif t.GetLayer() == pcbnew.F_Cu: cop.append(LineString([(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]).buffer(mm(t.GetWidth()) / 2))
cop = unary_union(cop)
for ref, (ax, ay) in ANCH.items():
    f = fp[ref]; others = unary_union([court(g) for r, g in fp.items() if r != ref and abs(mm(g.GetPosition().x) - ax) < 15 and abs(mm(g.GetPosition().y) - ay) < 15])
    best = None
    for rot in (90.0, 0.0):
        f.SetOrientationDegrees(rot)
        for r in [i * 0.25 for i in range(1, 100)]:
            for k in range(int(8 * r / 0.25) + 1):
                a = 2 * math.pi * k / (int(8 * r / 0.25) + 1); x, y = round((ax + r * math.cos(a)) / 0.05) * 0.05, round((ay + r * math.sin(a)) / 0.05) * 0.05
                f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
                c = court(f); pads = unary_union([box(mm(p.GetBoundingBox().GetLeft()), mm(p.GetBoundingBox().GetTop()), mm(p.GetBoundingBox().GetRight()), mm(p.GetBoundingBox().GetBottom())).buffer(0.2) for p in f.Pads()])
                if c.intersects(others) or pads.intersects(cop): continue
                if not (mm(edge.GetLeft()) + 3 < x < mm(edge.GetRight()) - 3 and mm(edge.GetTop()) + 3 < y < mm(edge.GetBottom()) - 3): continue
                if best is None or r < best[0]: best = (r, x, y, rot)
                break
            if best and best[0] <= r: break
    r, x, y, rot = best; f.SetOrientationDegrees(rot); f.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); print(ref, "->", x, y, rot, "dist", r)
b.Save(dst)
