"""Hand-route helper: add tracks/vias from a JSON spec after a clearance check (shapely, per layer, other-net copper).
usage: bp_hand.py SRC DST spec.json [--dry]
spec: [{"net":..., "layer":"L4_GND_BRK", "w":0.15, "pts":[[x,y],...]}, {"net":..., "via":[x,y]} ...]"""
import sys, json, math, pcbnew
from shapely.geometry import LineString, Point, Polygon
src, dst, spec = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3])); dry = "--dry" in sys.argv
b = pcbnew.LoadBoard(src); MM = pcbnew.FromMM
lid = {b.GetLayerName(i): i for i in range(64) if b.IsLayerEnabled(i)}
CU = [lid[n] for n in ("L1_SIG_RX", "L3_SIG_TX_PWR", "L4_GND_BRK", "L2_GND")]
def P(v): return (v.x / 1e6, v.y / 1e6)
def other(L, net, region):
    out = []
    for t in b.GetTracks():
        if t.GetNetname() == net: continue
        if t.Type() == pcbnew.PCB_VIA_T:
            gg = Point(P(t.GetPosition())).buffer(t.GetWidth(L) / 2e6, 16)
        elif t.GetLayer() == L: gg = LineString([P(t.GetStart()), P(t.GetEnd())]).buffer(t.GetWidth() / 2e6, 8)
        else: continue
        if gg.distance(region) < 1: out.append((gg, t.GetNetname()))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() == net or not p.IsOnLayer(L): continue
            if Point(P(p.GetPosition())).distance(region) > 4: continue
            sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
            for o in range(sp.OutlineCount()):
                ol = sp.COutline(o); out.append((Polygon([P(ol.CPoint(k)) for k in range(ol.PointCount())]), "%s-%s:%s" % (f.GetReference(), p.GetNumber(), p.GetNetname())))
    return out
bad = 0
for it in spec:
    net = it["net"]; nobj = b.FindNet(net)
    if "via" in it:
        c = tuple(it["via"]); gg = Point(c).buffer(0.225, 16); worst = (9, "")
        for L in (lid["L1_SIG_RX"], lid["L3_SIG_TX_PWR"], lid["L4_GND_BRK"]):
            for og, on in other(L, net, gg):
                d = og.distance(gg)
                if d < worst[0]: worst = (d, on + "@" + b.GetLayerName(L))
        for t in b.GetTracks():   # hole-to-hole
            if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() != net:
                hd = math.dist(P(t.GetPosition()), c) - 0.25
                if hd < 0.25 and hd < worst[0]: worst = (hd, "hole " + t.GetNetname())
        okk = worst[0] >= 0.1; bad += not okk
        print("via", net, c, "min clr %.3f %s" % worst, "OK" if okk else "BAD")
        if not dry and okk:
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(c[0]), MM(c[1]))); v.SetWidth(MM(0.45)); v.SetDrill(MM(0.25)); v.SetNet(nobj); b.Add(v)
        continue
    L = lid[it["layer"]]; w = it["w"]; pts = [tuple(p) for p in it["pts"]]
    gg = LineString(pts).buffer(w / 2, 8); worst = (9, "")
    clr = it.get("clr", 0.1)
    for og, on in other(L, net, gg):
        d = og.distance(gg)
        if d < clr: c_ = og.centroid; print("   conflict %-18s d=%.3f near (%.2f,%.2f)" % (on, d, c_.x, c_.y))
        if d < worst[0]: worst = (d, on); okk = worst[0] >= clr; bad += not okk
    print("trk", net, it["layer"], pts[0], "->", pts[-1], "min clr %.3f %s" % worst, "OK" if okk else "BAD")
    if not dry and okk:
        for a, c in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
            t.SetWidth(MM(w)); t.SetLayer(L); t.SetNet(nobj); b.Add(t)
print("bad", bad)
if not dry and not bad: pcbnew.SaveBoard(dst, b); print("saved", dst)
