#!/usr/bin/env python3
"""Build the MP62 Face S storage module (4 x M.2 + ASM2824) floorplan board, derived from the MP62-FACE v0.1 template (KiCad 9 pcbnew API, system python3).
Geometry comes from tools/face_geom.json (copy of /workspace/macpro62-face/tools/face_geom.json).
MP62-FACE frame: origin bottom-left, +X right, +Y up, viewed from the CORE side = KiCad top (F).
KiCad position = (OX + X, OY - Y). The grid/aux origin is set to the MP62 origin."""
import json, math, os, sys
import pcbnew
from pcbnew import FromMM, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(PRJ, "macpro62-storage-face.kicad_pcb")
SLIB = os.path.join(PRJ, "MP62_Storage.pretty")
LIB = os.path.join(PRJ, "MP62_Face.pretty")
g = json.load(open(os.path.join(HERE, "face_geom.json")))
OX, OY = 60.0, 190.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))

board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(6)
ds = board.GetDesignSettings()
ds.SetBoardThickness(FromMM(1.6))
ds.m_TrackMinWidth = FromMM(0.127); ds.m_MinClearance = FromMM(0.127)
ds.m_ViasMinSize = FromMM(0.45); ds.m_MinThroughDrill = FromMM(0.3)
ds.m_CopperEdgeClearance = FromMM(0.5); ds.m_HoleClearance = FromMM(0.25); ds.m_HoleToHoleMin = FromMM(0.5)
ds.m_SilkClearance = FromMM(0.0)
ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
tb = board.GetTitleBlock()
tb.SetTitle("MP62 Face S storage module SM-1 rev A0 (4 x M.2 NVMe, ASM2824) - FLOORPLAN")
tb.SetRevision("A0-floorplan"); tb.SetDate("2026-10-01"); tb.SetCompany("MacPro6,2 / Aidan Winkler (open spec)")
tb.SetComment(0, "Frame: origin = aux/grid origin = outline bottom-left, viewed from the CORE side (F = core side, B = outer side)")
tb.SetComment(1, "Stackup JLC06161H-2116 6L 1.6 mm (L1 sig, L2 GND, L3 sig, L4 3V3/PWR, L5 GND, L6 sig)")
tb.SetComment(2, "B (outer): J_PCIE MCIO124 RA, J_AUX GH15 (moved, dev. D-S2), 4 x M.2 M-key H4.2. F (core): ASM2824 on die pad. NO X-bracket (dev. D-S1)")
tb.SetComment(3, "PLACEMENT ONLY: not routed; M.2 socket, ASM2824 BGA and TPS56C215 land patterns are PLACEHOLDERS")

def shape_seg(x1, y1, x2, y2, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def shape_arc(cx, cy, r, a0, a1, layer, w=0.1):
    if a1 < a0: a1 += 360
    am = (a0 + a1) / 2
    pt = lambda a: P(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(pt(a0), pt(am), pt(a1)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def shape_circle(x, y, r, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_CIRCLE)
    s.SetCenter(P(x, y)); s.SetEnd(P(x + r, y)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def shape_rect(r, layer, w=0.1):
    x1, y1, x2, y2 = r
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        shape_seg(*a, *b, layer, w)
def shape_poly(pts, layer, w=0.1):
    for i in range(len(pts)):
        shape_seg(*pts[i], *pts[(i + 1) % len(pts)], layer, w)
def txt(s, x, y, layer=pcbnew.Cmts_User, size=1.0, angle=0.0, mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(size * 0.15))
    t.SetTextAngleDegrees(angle); t.SetMirrored(mirror); board.Add(t)

# ---------- Edge.Cuts ----------
for s in g["outline"]:
    if s[0] == "L": shape_seg(s[1], s[2], s[3], s[4], pcbnew.Edge_Cuts, 0.05)
    else: shape_arc(s[1], s[2], s[3], s[4], s[5], pcbnew.Edge_Cuts, 0.05)

# ---------- footprints ----------
nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); nets[name] = n
    return nets[name]
def place(ref, name, x, y, rot=0.0, side="F", value=None, centre_bbox=False, netmap=None, dnp=False, lib="MP62_Face"):
    f = pcbnew.FootprintLoad(LIB if lib == "MP62_Face" else SLIB, name)
    if f is None: sys.exit("missing " + name)
    f.SetFPID(pcbnew.LIB_ID(lib, name)); f.SetReference(ref); f.SetValue(value or name)
    f.SetPosition(P(x, y)); f.SetOrientationDegrees(rot)
    board.Add(f)
    if side == "B": f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    if centre_bbox:
        cy = f.GetCourtyard(pcbnew.B_CrtYd if side == "B" else pcbnew.F_CrtYd).BBox()
        c = cy.GetCenter(); t = P(x, y); f.Move(VECTOR2I(t.x - c.x, t.y - c.y))
    if netmap:
        for p in f.Pads():
            if p.GetNumber() in netmap: p.SetNet(net(netmap[p.GetNumber()]))
    if dnp:
        f.SetDNP(True); f.SetExcludedFromBOM(True)
    f.Reference().SetVisible(True)
    f.Reference().SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab)
    return f
def S(ref, name, x, y, rot=0.0, side="F", value=None, dnp=False):
    return place(ref, name, x, y, rot, side, value, dnp=dnp, lib="MP62_Storage")
for i, (x, y) in enumerate(g["holes"]):
    place("H%d" % (i + 1), "MP62_FACE_MountHole_D5.0_Pad9.0", x, y, value="MOUNT D5.0 (screw + washer, NO bracket)")
for (x, y), ref, n, site in zip(g["LUGS"], g["LUG_REFS"], g["LUG_NETS"], g["LUG_SITE"]):
    place(ref, "MP62_FACE_BusBarLug_D3.2_Pad8.8", x, y, value="BUSBAR LUG site %s %s (polarity TO MEASURE)" % (site, n), netmap={"1": n})
def track(pts, layer, w, netname):
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        t = pcbnew.PCB_TRACK(board); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetLayer(layer)
        t.SetWidth(FromMM(w)); t.SetNet(net(netname)); board.Add(t)
(a12, agnd), (b12, bgnd) = g["LUGS_A"], g["LUGS_B"]
track([a12, (a12[0], 140.0), (b12[0], 140.0), b12], pcbnew.In1_Cu, 3.0, "+12V_IN")
track([agnd, (agnd[0], 163.4), (bgnd[0], 163.4), bgnd], pcbnew.In4_Cu, 2.0, "GND")
jp = g["J"]["J_PCIE"]
fp = place("J1", "MP62_MCIO_124P_RA_SFF-TA-1016", jp["cx"], g["Y_MATE"] + 6.025, rot=180, side="B", value="J_PCIE MCIO124 RA G97R24332HR (lanes 0-7 used)")
AUX_CY = 20.5   # deviation D-S2: J_AUX moved from Y 26.5 to Y 20.5 (spec position is 'should')
a = g["AUX"]
fa = place("J3", "JST_GH_SM15B-GHS-TB_1x15-1MP_P1.25mm_Horizontal", a["cx"], AUX_CY, rot=90, side="B", value="J_AUX GH15 RA SM15B-GHS-TB (moved -6 mm Y)", centre_bbox=True)

# ---- M.2 slots (B side). Columns: card edge datum Y_D, card toward -Y. Slot 3: datum X 12, card toward +X ----
COLS = [26.5, 52.0, 77.5]; Y_D = 108.5; S4_Y = 126.0; S4_X = 12.0
LENS = [80, 60, 42, 30]
socks = []
for i, cx in enumerate(COLS):
    socks.append(S("J%d" % (5 + i), "MP62_M2_MKey_SMT_H4.2_PLACEHOLDER", cx, Y_D, 0, "B", "M.2 M-key H4.2 SSD%d (LOTES APCI0107-P001A)" % i))
    for k, Lc in enumerate(LENS):
        if i == 1 and Lc in (30, 42): continue   # would sit behind U1 (switch BGA escape area)
        S("MH%d%d" % (i, Lc), "MP62_M2_Standoff_SMT_M2_Pad5.0", cx, Y_D - Lc, 0, "B", "M.2 standoff 22%02d" % Lc, dnp=(Lc != 80))
s4 = S("J8", "MP62_M2_MKey_SMT_H4.2_PLACEHOLDER", S4_X, S4_Y, -90, "B", "M.2 M-key H4.2 SSD3 (LOTES APCI0107-P001A)")
socks.append(s4)
for Lc in LENS:
    S("MH3%d" % Lc, "MP62_M2_Standoff_SMT_M2_Pad5.0", S4_X + Lc, S4_Y, 0, "B", "M.2 standoff 22%02d" % Lc, dnp=(Lc != 80))

# ---- core side (F): switch on the die pad + its local support ----
DX, DY = g["DIE"]
S("U1", "MP62_BGA-492_21x21mm_Layout25x25_P0.8mm_PLACEHOLDER", DX, DY, 0, "F", "ASM2824 PCIe Gen3 switch (JLC C9900092023)")
S("U5", "SOT-563", 70.5, 62.0, 0, "F", "TLV62585 VDD_CORE buck (rail TBD per datasheet)")
S("L2", "L_1008_2520Metric", 70.5, 58.0, 0, "F", "0.47uH 2520 (core buck)")
S("U8", "SOIC-8_3.9x4.9mm_P1.27mm", 31.0, 86.0, 90, "F", "SPI flash 25Q (switch config, TBD)")
S("Y1", "Crystal_SMD_3225-4Pin_3.2x2.5mm", 70.0, 76.0, 0, "F", "25 MHz (populate only if ASM2824 needs it)")
S("U7", "Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm", 35.0, 70.0, 0, "F", "TMP1075DSGR @0x48")
S("U9", "SOT-363_SC-70-6", 35.0, 56.0, 0, "F", "74LVC2G07 PERST# fan-out SSD0/1")
S("U10", "SOT-363_SC-70-6", 35.0, 52.0, 0, "F", "74LVC2G07 PERST# fan-out SSD2/3")
S("U12", "SOT-363_SC-70-6", 35.0, 48.0, 0, "F", "74LVC2G07 switch PERST# gate (PG_ALL)")
S("U11", "Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm", 52.0, 100.0, 0, "B", "TMP1075DSGR @0x49 THERM_TRIP# (under SSD1, <=1.6 mm)")
for k, x in enumerate([58.0, 64.0]):
    S("D%d" % (6 + k), "SOT-23", x, 163.0, 0, "B", "BAT54A (DAS# -> MOD_LED# wired-OR)")
for k, (x, y) in enumerate([(38.0, 60.0), (38.0, 79.0), (66.0, 79.0), (66.0, 66.0)]):
    S("C%d" % (60 + k), "C_0805_2012Metric", x, y, 90, "F", "22uF switch bulk")

# ---- top band (B), X 16-88, Y 139-166: protection + power ----
S("Q1", "TDSON-8-1", 30.0, 150.0, 0, "B", "N-MOSFET 30 V <=5 mOhm (reverse block)")
S("U3", "SOT-23-6", 30.0, 157.0, 0, "B", "LM74700-Q1 ideal-diode ctrl")
S("U2", "Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm", 44.0, 150.0, 0, "B", "TPS259824ONRGER eFuse I_LIM 5 A")
for k, x in enumerate([38.0, 50.0]):
    S("C%d" % (10 + k), "C_1206_3216Metric", x, 157.0, 90, "B", "10uF 25V")
# ICD rev 2 live power target: 12 V monitor (face spec 6.8: INA228 @0x40 on FACE_SMB) + 2 mOhm Kelvin shunt ahead of U2
S("R520", "R_2512_6332Metric", 44.0, 143.0, 0, "B", "2 mOhm 2512 shunt (+12V_PROT -> U2)")
S("U13", "VSSOP-10_3x3mm_P0.5mm", 51.5, 143.0, 0, "B", "INA228 @0x40 FACE_SMB, ALERT -> FACE_SMB_ALERT#")
S("C520", "C_0402_1005Metric", 51.5, 140.5, 0, "B", "100nF U13 VS")
S("U4", "MP62_TI_RNN0018A_VQFN-HR-18_3.5x3.5mm_PLACEHOLDER", 58.0, 148.0, 0, "B", "TPS56C215RNNR 3V3_SSD 12 A buck")
S("L1", "L_Bourns_SRP1038C_10.0x10.0mm", 70.0, 152.0, 0, "B", "1.0uH 10x10 >=15 A Isat")
for k, x in enumerate([57.0, 60.0]):
    S("C%d" % (20 + k), "C_1206_3216Metric", x, 156.0, 90, "B", "22uF 25V buck input")
for k, (x, y) in enumerate([(79.0, 146.0), (82.0, 146.0), (85.0, 146.0), (79.0, 152.0), (82.0, 152.0), (85.0, 152.0)]):
    S("C%d" % (30 + k), "C_1206_3216Metric", x, y, 90, "B", "47uF 6.3V 3V3_SSD")
S("U6", "SOIC-8_3.9x4.9mm_P1.27mm", 22.0, 147.0, 90, "B", "BL24C64A-SFRC ID EEPROM @0x50")
for k in range(5):
    S("D%d" % (1 + k), "LED_0603_1608Metric", 36.0 + 4.0 * k, 163.0, 0, "B", ("SSD%d activity (DAS#)" % k) if k < 4 else "3V3_SSD power LED")
# 3V3_SSD local bulk at each socket (under the socket body area is free: put beside the socket, B side)
k = 40
for cx in COLS:
    for dx in (-5.0, 5.0):
        S("C%d" % k, "C_0805_2012Metric", cx + dx, Y_D - 4.0, 0, "B", "22uF 0805 3V3 slot bulk (under card, <=1.6 mm)"); k += 1
for dy in (-5.0, 5.0):
    S("C%d" % k, "C_0805_2012Metric", S4_X + 4.0, S4_Y + dy, 90, "B", "22uF 0805 3V3 slot bulk (under card, <=1.6 mm)"); k += 1

# orientation checks (board frame)
def bf(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
def padpos(f, num): return bf([p for p in f.Pads() if p.GetNumber() == num][0].GetPosition())
chk = []
fy = bf(fp.GetPosition())[1]
chk.append(("J_PCIE pad rows above datum", padpos(fp, "A1")[1] > fy and padpos(fp, "B1")[1] > padpos(fp, "A1")[1]))
mp = [bf(p.GetPosition()) for p in fa.Pads() if p.GetNumber() == "MP"]
chk.append(("J_AUX opening toward -X", all(m[0] < padpos(fa, "1")[0] for m in mp)))
for i, f in enumerate(socks[:3]):
    chk.append(("SSD%d socket pads behind datum (+Y), card toward -Y" % i, padpos(f, "1")[1] > Y_D))
chk.append(("SSD3 socket pads left of datum (-X), card toward +X", padpos(s4, "1")[0] < S4_X))
for c, ok in chk: print(("OK  " if ok else "FAIL"), c)

# ---------- rule areas ----------
def rule_area(name, layer, polyset, fp_=True, pads=True, vias=False, tracks=False, pour=False):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetZoneName(name)
    z.SetDoNotAllowFootprints(fp_); z.SetDoNotAllowPads(pads); z.SetDoNotAllowVias(vias)
    z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowCopperPour(pour)
    ls = pcbnew.LSET(); ls.AddLayer(layer); z.SetLayerSet(ls); z.SetOutline(polyset); board.Add(z); return z
def ps_poly(pts):
    s = pcbnew.SHAPE_POLY_SET(); s.NewOutline()
    for x, y in pts:
        v = P(x, y); s.Append(v.x, v.y)
    return s
def ps_circle(x, y, r, n=48): return ps_poly([(x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n)) for i in range(n)])
def ps_rect(r): return ps_poly([(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])])
keep = []
for side_layer, sfx in ((pcbnew.F_Cu, "F"), (pcbnew.B_Cu, "B")):   # spec: lug zones free of parts on BOTH sides
    for tag, r in zip(("A", "B"), g["LUG_KOS"]):
        lko = ps_rect(r); lko.BooleanIntersection(ps_poly(g["outline_poly"]))
        for (x, y) in g["LUGS"]: lko.BooleanSubtract(ps_circle(x, y, 5.2))
        lko.Simplify(); keep.append(lko)
        rule_area("KO-F2%s_BUSBAR_no_parts_%s" % (tag, sfx), side_layer, lko)
for tag, r in (("A", g["TAB_KO"]), ("B", g["TAB_KO_B"])):
    tab_ps = ps_rect(r); keep.append(tab_ps)
    rule_area("KO-F5%s_CORE_TAB_no_parts" % tag, pcbnew.F_Cu, tab_ps)
jko = ps_rect(jp["ko"]); keep.append(jko); rule_area("J_PCIE_plug_zone_B", pcbnew.B_Cu, jko, fp_=False, pads=False)

# ---------- documentation layers ----------
U1L, U2L, U3L, U4L = pcbnew.User_1, pcbnew.User_2, pcbnew.User_3, pcbnew.User_4
shape_poly(g["DIE_PAD"], U1L, 0.15); shape_rect(g["TZ1"], U1L, 0.08)
txt("DIE PAD: U1 ASM2824 + 3.0 mm soft gap pad (no Cu block, no preload needed)", 52, 84.5, U1L, 0.8)
for sp in g["STRIPS"]: shape_poly(sp, U1L, 0.12)
pl = g["PLATE"]; shape_rect((pl["x0"], pl["y0"], pl["x1"], pl["y1"]), U1L, 0.08)
for (x, y) in g["CORE_BOSSES"]: shape_circle(x, y, g["CORE_BOSS_D"] / 2, U1L, 0.08)
txt("F (core) parts <= 3.5 mm; <= 3.0 over strip pads; <= 1.0 outside the plate", 52, 20, U1L, 0.8)
for a_, b_, h_ in g["HZ"]:
    for x0 in (52 + a_, 52 - a_):
        shape_seg(x0, 0, x0, 166, U2L, 0.05)
cards = [(cx - 11, Y_D - 80, cx + 11, Y_D) for cx in COLS] + [(S4_X, S4_Y - 11, S4_X + 80, S4_Y + 11)]
for i, r in enumerate(cards):
    shape_rect(r, U4L, 0.15)
    txt("SSD%d 2280 card (B side, card bottom ~3.5 mm, top ~5.8 mm)" % i, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2, U4L, 0.9, angle=(90 if i < 3 else 0))
    txt("SSD%d" % i, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2 + (-11 if i < 3 else 6), pcbnew.B_SilkS, 2.0, mirror=True)
txt("User.4: M.2 cards. Under a card: host parts <= 1.6 mm (0402/0603 passives only)", 52, 24.5, U4L, 0.9)
shape_rect(g["CONN_BAND"], U3L, 0.1)
shape_poly(g["bracket_ref"], pcbnew.Dwgs_User, 0.08)
txt("Dwgs.User: stock X-bracket outline - NOT FITTED on Face S SM-1 (deviation D-S1)", 52, 104, pcbnew.Dwgs_User, 0.9)
notes = ["MP62 Face S storage module SM-1 rev A0 FLOORPLAN (not routed). Viewed from the CORE side. F = core side, B = outer side.",
         "B: 3 x 2280 columns (X 15.5-37.5 / 41-63 / 66.5-88.5, sockets Y 108.5-115, cards to Y 28.5) + 1 x 2280 across the top (Y 115-137).",
         "F: ASM2824 (U1) centred on the die pad (52, 69.5) with gap pad to the core; core buck, crystal, flash, PERST# buffers, TMP1075.",
         "Top band B (Y 139-166, X 16-88): LM74700+FET reverse block, TPS259824 eFuse, TPS56C215 3V3_SSD buck, EEPROM, LEDs.",
         "Deviations: D-S1 no X-bracket (screws + washers; heads under SSD0/SSD2 edges <= 1.6 mm); D-S2 J_AUX moved to Y 20.5.",
         "PLACEHOLDER land patterns: M.2 socket, ASM2824 BGA, TPS56C215 RNN. Replace before routing."]
for i, s in enumerate(notes): txt(s, 52, -6 - 2.2 * i, pcbnew.Cmts_User, 1.0)
txt("MP62 FACE S SM-1 A0", 52, 150, pcbnew.F_SilkS, 1.5)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "ALL CHECKS OK" if all(ok for _, ok in chk) else "CHECK FAIL")
