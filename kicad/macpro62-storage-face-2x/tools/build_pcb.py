#!/usr/bin/env python3
"""MP62 Face S 2-drive switchless storage module (S2X) rev A0: board from tools/model.py.
Reuses the MP62-FACE outline / holes / lugs / J_PCIE (X 47.0) / J_AUX spec position (face_geom.json from SM-1).
Module frame: origin bottom-left, +X right, +Y up, viewed from the CORE side (F = core, B = outer). KiCad = (OX + X, OY - Y).
4 layers JLC04161H-7628: L1 sig/pour (ref L2), L2 GND, L3 GND, L4 = all parts + sig (ref L3). Output: work/s2x_placed.kicad_pcb"""
import json, math, os, sys
import pcbnew
from pcbnew import FromMM, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import model as M
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PRJ, "work", "s2x_placed.kicad_pcb")
LIB = os.path.join(PRJ, "MP62_S2X.pretty")
g = json.load(open("/workspace/kicad/macpro62-storage-face/tools/face_geom.json"))
OX, OY = 60.0, 190.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(FromMM(1.6))
ds.m_TrackMinWidth = FromMM(0.09); ds.m_MinClearance = FromMM(0.1)
ds.m_ViasMinSize = FromMM(0.45); ds.m_MinThroughDrill = FromMM(0.25)
ds.m_CopperEdgeClearance = FromMM(0.4); ds.m_HoleClearance = FromMM(0.2); ds.m_HoleToHoleMin = FromMM(0.25)
ds.m_SilkClearance = FromMM(0.0)
ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
tb = board.GetTitleBlock()
tb.SetTitle("MP62 Face S storage module S2X rev A0 (2 x M.2 2280 NVMe x4, switchless)")
tb.SetRevision("A0"); tb.SetDate("2026-10-08"); tb.SetCompany("MacPro6,2 / Aidan Winkler (open spec)")
tb.SetComment(0, "Frame: origin = aux/grid origin = outline bottom-left, viewed from the CORE side (F = core side, B = outer side)")
tb.SetComment(1, "Stackup JLC04161H-7628 4L 1.6 mm: L1 sig/pour, L2 GND, L3 GND, L4 parts + sig. 85R pairs 0.26/0.13")
tb.SetComment(2, "J_PCIE x8 = 2 x4 (CPU bifurcation): lanes 0-3 + REFCLK0/PERST0 -> slot A, lanes 4-7 + set B -> slot B")
tb.SetComment(3, "All parts on B (single-sided assembly). F = copper only + exposed GND thermal area on the die pad")
KEEP = []
def shape_seg(x1, y1, x2, y2, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def shape_arc(cx, cy, r, a0, a1, layer, w=0.1):
    if a1 < a0: a1 += 360
    am = (a0 + a1) / 2
    pt = lambda a: P(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(pt(a0), pt(am), pt(a1)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def shape_rect(r, layer, w=0.1):
    x1, y1, x2, y2 = r
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))): shape_seg(*a, *b, layer, w)
def shape_poly(pts, layer, w=0.1):
    for i in range(len(pts)): shape_seg(*pts[i], *pts[(i + 1) % len(pts)], layer, w)
def filled_poly(pts, layer):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_POLY); s.SetFilled(True); s.SetLayer(layer); s.SetWidth(0)
    s.SetPolyPoints([P(x, y) for x, y in pts]); board.Add(s); return s
def txt(s, x, y, layer=pcbnew.Cmts_User, size=1.0, angle=0.0, mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(size * 0.15))
    t.SetTextAngleDegrees(angle); t.SetMirrored(mirror); board.Add(t)
for s in g["outline"]:
    if s[0] == "L": shape_seg(s[1], s[2], s[3], s[4], pcbnew.Edge_Cuts, 0.05)
    else: shape_arc(s[1], s[2], s[3], s[4], s[5], pcbnew.Edge_Cuts, 0.05)
nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]
IO = pcbnew.PCB_IO_KICAD_SEXPR()
FPS = {}
for p in M.PARTS:
    f = IO.FootprintLoad(LIB, p["fp"])
    if f is None: sys.exit("missing " + p["fp"])
    f.SetFPID(pcbnew.LIB_ID(M.LIBN, p["fp"])); f.SetReference(p["ref"]); f.SetValue(p["value"])
    f.SetPosition(P(p["x"], p["y"])); f.SetOrientationDegrees(p["rot"])
    board.Add(f)
    if p["side"] == "B": f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    if p["ref"] == "J3":   # spec position = body centre
        cy = f.GetCourtyard(pcbnew.B_CrtYd).BBox(); c = cy.GetCenter(); t = P(p["x"], p["y"]); f.Move(VECTOR2I(t.x - c.x, t.y - c.y))
    for pd in f.Pads():
        n = p["nets"].get(pd.GetNumber())
        if n: pd.SetNet(net(n))
    if p["lcsc"]:
        f.SetField("LCSC", p["lcsc"]); fl = f.GetFieldByName("LCSC"); fl.SetVisible(False); fl.SetLayer(pcbnew.B_Fab)
    if p["dnp"]: f.SetDNP(True); f.SetExcludedFromBOM(True)
    if p["ref"].startswith(("H", "J2")) or p["ref"] in ("MH1", "MH2") and False: pass
    if p["ref"].startswith("H") or p["ref"] in ("J20", "J21", "J22", "J23"):
        f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
    f.Reference().SetLayer(pcbnew.B_Fab if p["side"] == "B" else pcbnew.F_Fab)
    FPS[p["ref"]] = f
# orientation checks
def bf(v): return (round(pcbnew.ToMM(v.x) - OX, 3), round(OY - pcbnew.ToMM(v.y), 3))
def padpos(ref, num): return bf(FPS[ref].FindPadByNumber(num).GetPosition())
chk = [("J1 A2 at (28.7, 21.1)", padpos("J1", "A2") == (28.7, 21.1)), ("J1 B36 at (49.1, 24.05)", padpos("J1", "B36") == (49.1, 24.05))]
for sl, ref in (("A", "J5"), ("B", "J6")):
    xs = M.XS[sl]
    chk.append(("%s pin1 at X-9.25, odd row toward J1" % ref, padpos(ref, "1") == (round(xs - 9.25, 3), round(M.YS - 3.77, 3))))
    chk.append(("%s pin 74 at X+9.0, even row card side" % ref, padpos(ref, "74") == (round(xs + 9.0, 3), round(M.YS + 3.77, 3))))
mp = [bf(p.GetPosition()) for p in FPS["J3"].Pads() if p.GetNumber() == "MP"]
chk.append(("J_AUX opening toward -X", all(m[0] < padpos("J3", "1")[0] for m in mp)))
for c, ok in chk: print(("OK  " if ok else "FAIL"), c)
if not all(ok for _, ok in chk): sys.exit("orientation check failed")

# ---------- rule areas ----------
def ps_poly(pts):
    s = pcbnew.SHAPE_POLY_SET(); s.NewOutline()
    for x, y in pts:
        v = P(x, y); s.Append(v.x, v.y)
    KEEP.append(s); return s
def ps_circle(x, y, r, n=48): return ps_poly([(x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n)) for i in range(n)])
def ps_rect(r): return ps_poly([(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])])
def rule_area(name, layers, polyset, fp_=True, pads=True, vias=False, tracks=False, pour=False):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetZoneName(name)
    z.SetDoNotAllowFootprints(fp_); z.SetDoNotAllowPads(pads); z.SetDoNotAllowVias(vias)
    z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowCopperPour(pour)
    ls = pcbnew.LSET()
    for L in layers: ls.AddLayer(L)
    z.SetLayerSet(ls); z.SetOutline(polyset); board.Add(z); KEEP.append(z); return z
for sfx, L in (("F", pcbnew.F_Cu), ("B", pcbnew.B_Cu)):
    for tag, r in zip(("A", "B"), g["LUG_KOS"]):
        lko = ps_rect(r); lko.BooleanIntersection(ps_poly(g["outline_poly"]))
        for (x, y) in g["LUGS"]: lko.BooleanSubtract(ps_circle(x, y, 5.2))
        lko.Simplify(); rule_area("KO-F2%s_BUSBAR_no_parts_%s" % (tag, sfx), [L], lko)
for (x, y) in g["holes"]:
    rule_area("KO_outer_hole_D12_(%g,%g)" % (x, y), [pcbnew.B_Cu], ps_circle(x, y, g["OUTER_HOLE_KO_D"] / 2), pads=False)
TH = {}
for sl in "AB":
    xs = M.XS[sl]; r = [xs - 9.5, 70.0, xs + 9.5, 127.0]; TH[sl] = r
    rule_area("THERMAL_PAD_%s_B_no_tracks_no_parts" % sl, [pcbnew.B_Cu], ps_rect(r), fp_=True, pads=True, vias=False, tracks=True)
DIE = g["DIE_PAD"]
rule_area("THERMAL_DIE_PAD_F_no_tracks", [pcbnew.F_Cu], ps_poly(DIE), fp_=True, pads=True, vias=False, tracks=True)
# exposed copper (mask openings) for the thermal interface: SSD gap pads (B) and the core die pad (F)
for sl in "AB":
    x0, y0, x1, y1 = TH[sl]; filled_poly([(x0 + 0.5, y0 + 0.5), (x1 - 0.5, y0 + 0.5), (x1 - 0.5, y1 - 0.5), (x0 + 0.5, y1 - 0.5)], pcbnew.B_Mask)
filled_poly([(x, y) for x, y in DIE], pcbnew.F_Mask)
# ---------- documentation ----------
U1L, U2L, U3L, U4L = pcbnew.User_1, pcbnew.User_2, pcbnew.User_3, pcbnew.User_4
shape_poly(DIE, U1L, 0.15)
txt("DIE PAD: exposed GND copper (F.Mask open) + via array -> core (thermal path from the SSD gap pads)", 52, 84.5, U1L, 0.8)
for a_, b_, h_ in g["HZ"]:
    for x0 in (52 + a_, 52 - a_): shape_seg(x0, 0, x0, 166, U2L, 0.05)
for sl in "AB":
    xs = M.XS[sl]; r = (xs - 11, M.YS - 0.25, xs + 11, M.YS - 0.25 + 80)
    shape_rect(r, U4L, 0.15)
    txt("SSD %s 2280 (B side, card bottom 2.92 mm)" % sl, xs, 100, U4L, 0.9, angle=90)
    txt("SSD %s" % sl, xs, 131.5 - 8, pcbnew.B_SilkS, 2.0, mirror=True)
    shape_rect(TH[sl], U1L, 0.1)
    txt("GAP PAD %s: exposed GND" % sl, xs, 72, U1L, 0.7)
txt("User.4: M.2 cards. Under a card: host parts <= 1.6 mm (0402-1206 passives, VSSOP)", 52, 136.5, U4L, 0.8)
shape_rect(g["CONN_BAND"], U3L, 0.1)
notes = ["MP62 Face S storage module S2X rev A0: 2 x M.2 2280 NVMe x4 (no PCIe switch). Viewed from the CORE side. F = core side, B = outer side.",
         "J_PCIE MCIO124 x8 = x4 slot A (lanes 0-3, REFCLK0, PERST0#) + x4 slot B (lanes 4-7, REFCLK1, PERST1#): host PEG 2x8 / x4x4 bifurcation.",
         "Top band B: TPS259470A eFuse (EN = FACE_PWR_EN, ILIM 3.3 A), 2 mOhm shunt + INA238 @0x40. Strips: 2 x TPS54331 3V3 3 A bucks.",
         "Deviations: D-2X-1 hot-spot centroid ~(58, 75); D-S1 no X-bracket (as SM-1). Single-sided assembly (JLC Economic eligible)."]
for i, s in enumerate(notes): txt(s, 52, -6 - 2.2 * i, pcbnew.Cmts_User, 1.0)
txt("MP62 FACE S S2X A0", 52, 158.5, pcbnew.B_SilkS, 1.5, mirror=True)
pcbnew.SaveBoard(OUT, board)
# ---------- stackup (JLC04161H-7628) ----------
D = lambda n, t, th, mat, er, lt=0.02: f'\t\t\t(layer "dielectric {n}" (type "{t}") (thickness {th}) (material "{mat}") (epsilon_r {er}) (loss_tangent {lt}))\n'
Cu = lambda name, th: f'\t\t\t(layer "{name}" (type "copper") (thickness {th}))\n'
HEAD = '\t\t(stackup\n\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))\n\t\t\t(layer "F.Paste" (type "Top Solder Paste"))\n\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))\n'
TAIL = '\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))\n\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))\n\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))\n\t\t\t(copper_finish "HAL lead-free")\n\t\t\t(dielectric_constraints no)\n\t\t)\n'
body = (Cu("F.Cu", 0.035) + D(1, "prepreg", 0.2104, "7628 (JLC04161H-7628)", 4.4) + Cu("In1.Cu", 0.0152) + D(2, "core", 1.065, "FR4 core", 4.6) +
        Cu("In2.Cu", 0.0152) + D(3, "prepreg", 0.2104, "7628 (JLC04161H-7628)", 4.4) + Cu("B.Cu", 0.035))
s = open(OUT).read()
if "(stackup" not in s: s = s.replace("\t(setup\n", "\t(setup\n" + HEAD + body + TAIL, 1); open(OUT, "w").write(s)
print("saved", OUT, len(M.PARTS), "parts")
