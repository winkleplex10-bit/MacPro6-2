#!/usr/bin/env python3
"""Deterministic power skeleton (locked) so Freerouting only sees the small connections and the high-current paths stay whole:
  PH_A/PH_B switch nodes (1.2 mm), 3V3_A/3V3_B trunks L -> 47 uF -> socket 3V3 pins (1.8 mm, 0.8 mm combs on the pin groups),
  +12V_SW eFuse OUT -> shunt (0.8), +12V_S shunt -> 22 uF -> L1 trunk (1.0, y 138.5, both board sides) -> each buck VIN / Cin,
  INA238 VBUS/IN- sense (0.25, one L1 hop under the +12V_IN pour), eFuse IN -> 2 vias into the L1 +12V_IN pour.
Every segment is checked against all other-net copper (pads, tracks, vias) with clearance >= CLR before it is written.
usage: route_pwr.py SRC DST"""
import sys, math, os
import pcbnew
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity
SRC, DST = sys.argv[1], sys.argv[2]
OX, OY = 60.0, 190.0
MM = pcbnew.FromMM; mm = pcbnew.ToMM
def K(x, y): return pcbnew.VECTOR2I(MM(OX + x), MM(OY - y))
def mf(v): return (mm(v.x) - OX, OY - mm(v.y))
b = pcbnew.LoadBoard(SRC)
F, B = pcbnew.F_Cu, pcbnew.B_Cu
CLR = {"default": 0.15}
# ---- existing copper (module frame) per layer ----
def padpoly(p, L):
    sp = p.GetEffectivePolygon(L, pcbnew.ERROR_OUTSIDE); gs = []
    for i in range(sp.OutlineCount()):
        o = sp.Outline(i); gs.append(Polygon([mf(o.CPoint(k)) for k in range(o.PointCount())]).buffer(0))
    return unary_union(gs)
CU = {F: [], B: [], "in": []}
for f in b.GetFootprints():
    for p in f.Pads():
        for L in (F, B):
            if p.IsOnLayer(L): CU[L].append((p.GetNetname(), padpoly(p, L), f.GetReference() + "." + p.GetNumber()))
        if p.GetDrillSize().x > 0:
            hp = Point(mf(p.GetPosition())).buffer(mm(p.GetDrillSize().x) / 2)
            for L in (F, B): CU[L].append((p.GetNetname() or "_npth", hp, f.GetReference() + ".hole"))
for t in b.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        g = Point(mf(t.GetPosition())).buffer(mm(t.GetWidth(F)) / 2)
        for L in (F, B): CU[L].append((t.GetNetname(), g, "via"))
    elif t.GetLayer() in (F, B):
        CU[t.GetLayer()].append((t.GetNetname(), LineString([mf(t.GetStart()), mf(t.GetEnd())]).buffer(mm(t.GetWidth()) / 2), "trk"))
for z in b.Zones():   # rule areas that forbid tracks
    if z.GetIsRuleArea() and z.GetDoNotAllowTracks():
        o = z.Outline(); poly = Polygon([mf(o.CVertex(i)) for i in range(o.TotalVertices())]).buffer(0)
        for L in (F, B):
            if z.IsOnLayer(L): CU[L].append(("_ruleNoTrk", poly, z.GetZoneName()))
bad = []; SEG = []; VIA = []
def chk(net, L, g, what, clr=0.15):
    for n, og, nm in CU[L]:
        if n == net: continue
        d = g.distance(og)
        if d < clr - 1e-4: bad.append("%s %s on %s: %.3f to %s [%s]" % (net, what, "F" if L == F else "B", d, nm, n))
def seg(net, L, pts, w):
    for a, c in zip(pts[:-1], pts[1:]):
        g = LineString([a, c]).buffer(w / 2)
        chk(net, L, g, "seg %s-%s w%.2f" % (a, c, w)); SEG.append((net, L, a, c, w))
    for a, c in zip(pts[:-1], pts[1:]): CU[L].append((net, LineString([a, c]).buffer(w / 2), "new"))
def via(net, p, d=0.6, h=0.3):
    g = Point(p).buffer(d / 2)
    for L in (F, B): chk(net, L, g, "via %s" % (p,))
    VIA.append((net, p, d, h))
    for L in (F, B): CU[L].append((net, g, "newvia"))
# ---------------- PH ----------------
seg("PH_A", B, [(18.5, 70.09), (18.5, 68.3), (26.1, 68.3), (26.1, 72.0)], 1.2)
seg("PH_A", B, [(22.5, 66.4), (22.5, 68.3)], 1.2)
seg("PH_A", B, [(17.97, 70.09), (18.5, 70.09)], 0.6)
seg("PH_B", B, [(93.03, 73.91), (90.1, 73.91)], 0.9)
seg("PH_B", B, [(90.1, 72.0), (90.1, 68.3), (92.5, 68.3), (92.5, 66.4)], 1.2)
# ---------------- 3V3 ----------------
# 3V3_A / 3V3_B = islands on In2 (L3) under the cards (Y 55-81; HS copper ends at Y 51.3, L2 stays solid GND). B side: buck L -> 47 uF bar
# with 3 vias; socket 3V3 pin groups -> short combs -> via each; the even-row signal pins (DAS, PERST, CLKREQ, WAKE) stay free to escape.
ISL = {"3V3_A": [(1.0, 55.0), (57.6, 55.0), (57.6, 81.0), (1.0, 81.0)], "3V3_B": [(58.4, 55.0), (103.0, 55.0), (103.0, 81.0), (58.4, 81.0)]}
def v33(net, lx, c2x, xs, groups):
    seg(net, B, [(lx, 72.0), (lx, 76.53), (c2x, 76.53)], 1.8)
    for p in ((lx, 75.07), ((lx + c2x) / 2, 76.53)): via(net, p)
    for (xa, xb) in groups:          # pins xa..xb (0.5 pitch) -> comb(s) w0.6 UP under the socket body (F side outside the die pad) -> bar -> via
        xc = (xa + xb) / 2; combs = [xc] if xb - xa <= 0.55 else [xa + 0.25, xb - 0.25]
        for cx in combs: seg(net, B, [(cx, 58.77), (cx, 57.5)], 0.6)
        if len(combs) > 1: seg(net, B, [(combs[0], 57.5), (combs[-1], 57.5)], 0.6)
        seg(net, B, [(xc, 57.5), (xc, 56.7)], 0.6); via(net, (xc, 56.7))
v33("3V3_A", 20.9, 25.5, 46.0, [(37.0, 37.5), (39.5, 41.0), (54.0, 55.0)])
v33("3V3_B", 84.9, 89.5, 70.0, [(61.0, 61.5), (63.5, 65.0), (78.0, 79.0)])
# PERST level-shifter pull-ups (R14 / R17, outside the islands) -> B trace -> via into the island
seg("3V3_A", B, [(26.51, 40.0), (27.3, 40.0), (27.3, 55.7)], 0.3); via("3V3_A", (27.3, 55.7), 0.45, 0.25)
seg("3V3_B", B, [(81.51, 40.0), (82.4, 40.0), (82.4, 55.7)], 0.3); via("3V3_B", (82.4, 55.7), 0.45, 0.25)
# ---------------- 12 V ----------------
seg("+12V_SW", B, [(45.74, 150.0), (45.74, 148.2)], 0.25)
seg("+12V_SW", B, [(45.74, 148.2), (45.74, 146.6), (53.04, 146.6), (53.04, 148.3)], 0.8)
seg("+12V_SW", B, [(53.8, 144.0), (53.8, 146.6)], 0.25)
seg("+12V_SW", B, [(51.98, 145.5), (51.98, 146.6)], 0.4)
seg("+12V_S", B, [(58.96, 148.3), (58.96, 147.4), (66.5, 147.4), (66.5, 138.5)], 1.0)
seg("+12V_S", B, [(63.0, 147.4), (63.0, 148.53)], 1.0)
via("+12V_S", (66.5, 138.5)); seg("+12V_S", B, [(66.5, 138.5), (65.2, 138.5)], 1.0); via("+12V_S", (65.2, 138.5))
seg("+12V_S", F, [(65.2, 138.5), (3.0, 138.5), (3.0, 70.5), (11.3, 70.5)], 1.0)
seg("+12V_S", F, [(66.5, 138.5), (101.0, 138.5), (101.0, 72.64), (99.75, 72.64)], 1.0)
via("+12V_S", (11.3, 70.5)); seg("+12V_S", B, [(9.9, 70.53), (11.3, 70.5)], 1.0); seg("+12V_S", B, [(11.3, 70.5), (11.3, 71.36), (13.03, 71.36)], 0.6)
via("+12V_S", (99.75, 72.64)); seg("+12V_S", B, [(97.97, 72.64), (99.75, 72.64)], 0.6); seg("+12V_S", B, [(99.75, 72.64), (99.75, 70.53), (101.1, 70.53)], 0.8)
# INA238 VBUS / IN- sense: pins 8+9 -> left -> via -> L1 (under the +12V_IN pour) -> via -> up into the +12V_S trunk
seg("+12V_S", B, [(53.8, 143.0), (53.8, 143.5)], 0.25)
seg("+12V_S", B, [(53.8, 143.25), (52.4, 143.25), (52.4, 144.6)], 0.25)
via("+12V_S", (52.4, 144.6), 0.45, 0.25); seg("+12V_S", F, [(52.4, 144.6), (59.6, 144.6), (59.6, 145.4)], 0.25); via("+12V_S", (59.6, 145.4), 0.45, 0.25)
seg("+12V_S", B, [(59.6, 145.4), (59.6, 147.4)], 0.25)
# INA238 GND pin 7 (boxed in between 6 and 8): stub left + via
seg("GND", B, [(53.8, 142.5), (51.7, 142.5)], 0.25); via("GND", (51.7, 142.5), 0.45, 0.25)
# eFuse IN -> 2 vias into the L1 +12V_IN pour
seg("+12V_IN", B, [(46.23, 150.0), (46.23, 152.75)], 0.3); via("+12V_IN", (46.23, 152.75))
seg("+12V_IN", B, [(46.23, 152.75), (46.23, 153.75)], 0.5); via("+12V_IN", (46.23, 153.75))
if bad:
    print("COLLISIONS:"); [print("  ", x) for x in bad]
    if "--force" not in sys.argv: sys.exit(1)
for n, L, a, c, w in SEG:
    t = pcbnew.PCB_TRACK(b); t.SetStart(K(*a)); t.SetEnd(K(*c)); t.SetLayer(L); t.SetWidth(MM(w)); t.SetNet(b.FindNet(n)); t.SetLocked(True); b.Add(t)
for n, p, d, h in VIA:
    v = pcbnew.PCB_VIA(b); v.SetPosition(K(*p)); v.SetWidth(F, MM(d)); v.SetDrill(MM(h)); v.SetNet(b.FindNet(n)); v.SetLocked(True); b.Add(v)
KEEPZ = []
for net, pts in ISL.items():
    z = pcbnew.ZONE(b); z.SetLayer(pcbnew.In2_Cu); z.SetNet(b.FindNet(net)); z.SetAssignedPriority(6); z.SetZoneName("L3_" + net)
    z.SetLocalClearance(MM(0.25)); z.SetMinThickness(MM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
    for q in pts: ps.Append(K(*q))
    z.SetOutline(ps); b.Add(z); KEEPZ.extend([z, ps])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(DST, b); print("power skeleton: segments", len(SEG), "vias", len(VIA), "->", DST)
