#!/usr/bin/env python3
"""MacPro6,2 AM5 CPU board (CB) DRAFT rev A-am5 part-level FLOORPLAN fp0, KiCad 9 pcbnew API (system python3).
NEW sibling of kicad/macpro62-lga1700 (that project is only READ: outline method, mounting, core holes, frame approach and
connector positions are reused verbatim). Same frame: origin bottom-left, x right (0..156), y up from the board bottom
(tab tip y=1.722, shoulder y=12.982, top edge y=169.5). FRONT = socket/core side. KiCad sheet: X = 60 + x, Y = 240 - y.
AMD's AM5 land map, socket drawing and PROM21 ballout are NDA: U1/U2 pads are SYNTHETIC PLACEHOLDERS (flagged)."""
import json, math, os, sys
import pcbnew, ezdxf
from pcbnew import FromMM, VECTOR2I
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(PRJ, "macpro62_am5.kicad_pcb")
SYS = "/usr/share/kicad/footprints"
LOC = os.path.join(PRJ, "MP62_AM5_Placeholders.pretty")
DXF = "/workspace/bracket/cpu_board/cpu_board_outline_corrected.dxf"
OX, OY = 60.0, 240.0
def P(x, y): return VECTOR2I(FromMM(float(OX + x)), FromMM(float(OY - y)))

board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(10)
ds = board.GetDesignSettings()
ds.SetBoardThickness(FromMM(1.6))
# JLC 10-layer: 0.09/0.09 track/space, via 0.15 drill / 0.25 pad, via-in-pad POFV (same rules as the LGA1700 CB)
ds.m_TrackMinWidth = FromMM(0.09); ds.m_MinClearance = FromMM(0.09)
ds.m_ViasMinSize = FromMM(0.25); ds.m_MinThroughDrill = FromMM(0.15)
ds.m_CopperEdgeClearance = FromMM(0.5); ds.m_HoleClearance = FromMM(0.2); ds.m_HoleToHoleMin = FromMM(0.5)
ds.m_SilkClearance = FromMM(0.0)
try:
    ps = pcbnew.PAGE_INFO(); ps.SetType("A3"); board.SetPageSettings(ps)
except Exception:
    pass
tb = board.GetTitleBlock()
tb.SetTitle("MacPro6,2 AM5 CPU board (CB) - DRAFT rev A-am5-v3 floorplan fp0 (Ryzen 7000/9000 65 W, PROM21, 4 x DDR5 UDIMM)")
tb.SetRevision("A-am5-fp0"); tb.SetDate("2026-10-04"); tb.SetCompany("MacPro6,2 / Aidan Winkler")
tb.SetComment(0, "Edge.Cuts: stock riser outline (cpu_board_outline_corrected.dxf) + Mini Cool Edge 224 tab 79.89 at x=78 - identical to macpro62-lga1700")
tb.SetComment(1, "Stackup proposal: JLC 10L 1.6 mm: L1 S / L2 G / L3 S / L4 G / L5 P / L6 P / L7 G / L8 S / L9 G / L10 S, ENIG + hard-gold fingers, POFV")
tb.SetComment(2, "U1 Socket AM5 LGA1718 under the pedestal (78.41, 73.25) - SYNTHETIC lands (AMD NDA); U2 PROM21 FCBGA 19x19 - SYNTHETIC balls")
tb.SetComment(3, "DRAFT: placeholders flagged (placeholders_flagged.txt). Front parts <= 6.0 mm (plate). No nets, not routed.")
def seg(x1, y1, x2, y2, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def arc3(p1, pm, p2, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(P(*p1), P(*pm), P(*p2)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def rect(x1, y1, x2, y2, layer, w=0.15):
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        seg(*a, *b, layer, w)
def circle(x, y, r, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_CIRCLE)
    s.SetCenter(P(x, y)); s.SetEnd(P(x + r, y)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def txt(s, x, y, layer=pcbnew.Cmts_User, size=1.2, angle=0.0, left=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(size * 0.15))
    t.SetTextAngleDegrees(angle)
    if left: t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)

# ---------------- outline: stock DXF minus the stock tab, plus the new 224 tab ----------------
doc = ezdxf.readfile(DXF)
pl = [e for e in doc.modelspace() if e.dxf.layer == "OUTLINE_CORRECTED" and e.dxftype() == "LWPOLYLINE"][0]
V = [(float(round(x, 4)), float(round(y, 4)), float(b)) for x, y, s0, s1, b in pl.get_points("xyseb")]
i0 = [i for i, v in enumerate(V) if abs(v[0] - 136.309) < 0.01 and abs(v[1] - 12.982) < 0.01][0]
i1 = [i for i, v in enumerate(V) if abs(v[0] - 19.691) < 0.01 and abs(v[1] - 12.982) < 0.01][0]
stock = V[i0:i1 + 1]           # right shoulder -> around the top -> left shoulder (keeps every stock bulge)
poly_pts = []                   # for shapely
def bulge_mid(p1, p2, b):
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]; L = math.hypot(dx, dy)
    s = b * L / 2.0
    return (mx + s * dy / L, my - s * dx / L)
def arc_pts(p1, pm, p2, n=12):
    # circle through three points, sampled
    (ax, ay), (bx, by), (cx, cy) = p1, pm, p2
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax*ax + ay*ay) * (by - cy) + (bx*bx + by*by) * (cy - ay) + (cx*cx + cy*cy) * (ay - by)) / d
    uy = ((ax*ax + ay*ay) * (cx - bx) + (bx*bx + by*by) * (ax - cx) + (cx*cx + cy*cy) * (bx - ax)) / d
    r = math.hypot(ax - ux, ay - uy)
    a1, am, a2 = (math.atan2(p[1] - uy, p[0] - ux) for p in (p1, pm, p2))
    def norm(a): return a % (2 * math.pi)
    ccw = norm(am - a1) < norm(a2 - a1)
    sweep = norm(a2 - a1) if ccw else -norm(a1 - a2)
    return [(ux + r * math.cos(a1 + sweep * k / n), uy + r * math.sin(a1 + sweep * k / n)) for k in range(1, n + 1)]
def E_line(p1, p2):
    seg(*p1, *p2, pcbnew.Edge_Cuts, 0.1); poly_pts.append(p2)
def E_arc(p1, pm, p2):
    arc3(p1, pm, p2, pcbnew.Edge_Cuts, 0.1); poly_pts.extend(arc_pts(p1, pm, p2))
poly_pts.append(stock[0][:2])
for k in range(len(stock) - 1):
    p1, p2, b = stock[k][:2], stock[k + 1][:2], stock[k][2]
    if abs(b) > 1e-6: E_arc(p1, bulge_mid(p1, p2, b), p2)
    else: E_line(p1, p2)
# new tab (Amphenol recommended AIC card, CME102241010301X rev A p.2), front view: A1 end at low x
T = 1.722; SH = 12.982; XC = 78.0; HW = 79.89 / 2; CH = 0.75; RIN = 0.30; SLOT_D = 7.5
XL, XR = XC - HW, XC + HW
SLOTS = [(XC - 20.30, 2.40, "KEY F"), (XC + 0.36, 1.85, "slot"), (XC + 20.57, 1.85, "slot")]
c45 = math.cos(math.radians(45))
cur = (19.691, SH)
E_line(cur, (XL - RIN, SH))
E_arc((XL - RIN, SH), (XL - RIN + RIN * c45, SH - RIN + RIN * c45), (XL, SH - RIN))
E_line((XL, SH - RIN), (XL, T + CH))
a = XL
bounds = []
for (sx, w, nm) in SLOTS:
    bounds.append((a, sx - w / 2)); a = sx + w / 2
bounds.append((a, XR))
for k, (a, b) in enumerate(bounds):
    E_line((a, T + CH), (a + CH, T)); E_line((a + CH, T), (b - CH, T)); E_line((b - CH, T), (b, T + CH))
    if k < len(SLOTS):
        sx, w, nm = SLOTS[k]; r = w / 2; yc = T + SLOT_D - r
        E_line((b, T + CH), (b, yc)); E_arc((b, yc), (sx, yc + r), (b + w, yc)); E_line((b + w, yc), (b + w, T + CH))
E_line((XR, T + CH), (XR, SH - RIN))
E_arc((XR, SH - RIN), (XR + RIN - RIN * c45, SH - RIN + RIN * c45), (XR + RIN, SH))
E_line((XR + RIN, SH), (136.309, SH))
BOARD = Polygon(poly_pts).buffer(0)
for (sx, w, nm) in SLOTS:
    txt("%s %.2f w, x=%.2f" % (nm, w, sx), sx, T + SLOT_D + 1.2, pcbnew.Cmts_User, 0.7)
txt("NEW CPU-LINK TAB: Mini Cool Edge 224 card 79.89 +/-0.10 x 1.57, x %.3f-%.3f, tip y 1.722, shoulder y 12.982 (11.26 >= 6.00 MIN)" % (XL, XR), XC, -1.0, pcbnew.Cmts_User, 1.0)
txt("8x 0.75x45 deg tip chamfers, 30 deg bevel, slots 7.5 deep (>= 7.00), R0.30 inside corners; hard gold, no vias y<6", XC, -2.8, pcbnew.Cmts_User, 0.9)
txt("stock tab was x 45.364-111.021 (65.66), key 2.12 @ x 69.03 (front view; 86.97 was the back-view scan) -> removed; shoulder flat 19.69-136.31 and lower chamfers UNCHANGED", XC, -4.6, pcbnew.Cmts_User, 0.9)
# stock tab ghost
for k in range(7):
    p1, p2 = V[k][:2], V[(k + 1)][:2]
    seg(*p1, *p2, pcbnew.Eco2_User, 0.08)

# ---------------- footprint placement helper ----------------
placed = []
def place(ref, lib, name, x, y, rot=0.0, value=None, side="F", center=True):
    libpath = LOC if lib == "MP62_AM5_Placeholders" else os.path.join(SYS, lib + ".pretty")
    f = pcbnew.FootprintLoad(libpath, name)
    if f is None: sys.exit("missing footprint %s:%s" % (lib, name))
    f.SetFPID(pcbnew.LIB_ID(lib, name)); f.SetReference(ref); f.SetValue(value or name)
    f.SetPosition(P(x, y)); f.SetOrientationDegrees(rot); board.Add(f)
    if side == "B": f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    if center:
        try:
            cb = f.GetCourtyard(pcbnew.B_CrtYd if side == "B" else pcbnew.F_CrtYd).BBox()
            cc = cb.GetCenter() if cb.GetWidth() > 0 else f.GetBoundingBox(False).GetCenter()
        except Exception:
            cc = f.GetBoundingBox(False).GetCenter()
        tgt = P(x, y); f.Move(VECTOR2I(tgt.x - cc.x, tgt.y - cc.y))
    placed.append((ref, f, value or name, side))
    return f


# ---------------- symmetry check of the stock outline (back-view scan) ----------------
_mir = affinity.scale(BOARD, xfact=-1, yfact=1, origin=(78.0, 0))
_sym = BOARD.symmetric_difference(_mir)
_sym_hi = _sym.intersection(box(-5, 13.5, 165, 175)).area      # above the shoulder (tab region excluded)
print("outline mirror check: symmetric-difference area above the shoulder = %.3f mm2 (0 = mirror-invariant)" % _sym_hi)

L = "MP62_AM5_Placeholders"
D = pcbnew.Dwgs_User; C = pcbnew.Cmts_User; E1 = pcbnew.Eco1_User; E2 = pcbnew.Eco2_User
ALLCU = [pcbnew.F_Cu, pcbnew.B_Cu] + [getattr(pcbnew, "In%d_Cu" % i) for i in range(1, 9)]
def rule_area(name, pts, layers, fp=False, vias=False, tracks=False, pads=False, pour=False):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True)
    z.SetDoNotAllowFootprints(fp); z.SetDoNotAllowVias(vias); z.SetDoNotAllowTracks(tracks)
    z.SetDoNotAllowPads(pads); z.SetDoNotAllowCopperPour(pour); z.SetZoneName(name)
    ls = pcbnew.LSET(); [ls.AddLayer(l) for l in layers]; z.SetLayerSet(ls)
    o = z.Outline(); o.NewOutline()
    for (x, y) in pts:
        p = P(x, y); o.Append(p.x, p.y)
    board.Add(z)


FLAG = {}   # ref -> (status, note)
def flag(ref, status, note): FLAG[ref] = (status, note)

# ---------------- CPU socket, frame, holes (positions identical to the LGA1700 CB) ----------------
PED = (78.41, 73.25); PW, PH = 40.6, 41.1
CX, CY = PED
place("U1", L, "MP62_AM5_LGA1718_Socket_PLACEHOLDER_Hex0.81x0.94", CX, CY, value="U1 Socket AM5 LGA1718 PLACEHOLDER (PE17181 / AZIFS055)")
flag("U1", "PLACEHOLDER-NDA", "1718 synthetic lands on the sourced 0.81 x 0.94 hex pitch; AMD land map + socket drawing needed; orientation [Inference]")
CORE_HOLES = [(43.25, 46.0), (112.75, 46.0), (43.25, 101.0), (112.75, 101.0)]
for i, (x, y) in enumerate(CORE_HOLES):
    f_ = place("H%d" % (i + 1), L, "MP62_CB_CoreMountHole_D5.0_Pad9", x, y, center=False, value="CORE D5 69.5x55 FIXED")
    GNDN = pcbnew.NETINFO_ITEM(board, "GND_CORE_H%d" % (i + 1)); board.Add(GNDN)
    for pd in f_.Pads(): pd.SetNet(GNDN)
    n = 32
    rule_area("CORE_BOSS_%d_%d" % (x, y), [(x + 6 * math.cos(2 * math.pi * i / n), y + 6 * math.sin(2 * math.pi * i / n)) for i in range(n)],
              ALLCU, tracks=True, vias=True)
    flag("H%d" % (i + 1), "FIXED (measured)", "stock core hole, same as LGA1700")
SEAT = [(CX - 28, CY - 21), (CX + 28, CY - 21), (CX - 28, CY + 21), (CX + 28, CY + 21)]
for i, (x, y) in enumerate(SEAT):
    place("H%d" % (i + 5), L, "MP62_CB_FrameSeatScrew_D3.4_NPTH", x, y, center=False, value="FRAME SEAT M3 -> PEM in backplate")
    flag("H%d" % (i + 5), "REUSED (LGA1700 pattern)", "MP62 own frame seat screw; hole edge ~3.3 mm from the estimated AM5 housing - re-check with the socket drawing")
# MP62 contact frame (Eco1): same 71 x 54 body + 4 ears on the core holes; AM5 window ~36 x 36 bears on the IHS flange
FX, FY = 35.5, 27.0
rect(CX - FX, CY - FY, CX + FX, CY + FY, E1, 0.25)
for (x, y) in CORE_HOLES:
    circle(x, y, 5.5, E1, 0.25)
rect(CX - 18.0, CY - 18.0, CX + 18.0, CY + 18.0, E1, 0.12)
txt("MP62 CONTACT FRAME 71 x 54 x <= 6.0 (7075, SAME as LGA1700) + 4 ears on the core holes; AM5 window ~36 x 36 [Estimate] on the IHS flange", CX, CY + FY + 1.4, E1, 0.7)
txt("replaces the stock AM5 ILM (Lotes AZIF0002 / AHSK0001 not fitted); load spec + IHS flange geometry = AMD (NDA) -> open item", CX, CY + FY + 2.6, E1, 0.6)
rect(CX - 23.0, CY - 23.0, CX + 23.0, CY + 23.0, D, 0.12)
txt("AM5 socket housing ~46 x 46 [Estimate]", CX, CY - 22.0, D, 0.6)
# pedestal + plate
rect(PED[0] - PW / 2, PED[1] - PH / 2, PED[0] + PW / 2, PED[1] + PH / 2, D, 0.3)
txt("CORE PEDESTAL 40.6 x 41.1 (measured) vs AM5 IHS 40 x 40 class: Z = M-AM5-1", CX, CY - PH / 2 + 1.2, D, 0.7)
PLATE = (16.2, 22.5, 140.4, 164.4)
rect(*PLATE, C, 0.3)
txt("BLACK PLATE 124 x 142 = FRONT HEIGHT ZONE: every front part <= 6.0 mm (5.5 rec.); board floats on springs; AM5 seated IHS Z = M-AM5-1", 78.0, 165.4, C, 0.75)
# ASSUMED AM5 interface regions (AMD land map is NDA): Dwgs only, for routing intent
LGRP = []
for (nm, x1, y1, x2, y2) in (("DDR5 CH-A (assumed)", -17.8, 9.0, -1.0, 18.8), ("DDR5 CH-B (assumed)", 1.0, 9.0, 17.8, 18.8),
                             ("PCIe GFX x16 (assumed)", -2.0, -18.8, 17.8, -9.0), ("PCIe GPP x4 + x4 + PROM21 x4 (assumed)", -17.8, -18.8, -3.0, -9.0),
                             ("USB4/USB/DP (assumed)", -17.8, -7.5, -7.0, 7.5), ("SVI3 / FCH / SPI / misc (assumed)", 7.0, -7.5, 17.8, 7.5)):
    rect(CX + x1, CY + y1, CX + x2, CY + y2, D, 0.12)
    txt(nm, CX + (x1 + x2) / 2, CY + (y1 + y2) / 2, D, 0.6)
    LGRP.append("  ASSUMED land group %-38s board x %.1f..%.1f  y %.1f..%.1f  [Inference, AMD land map NDA]" % (nm, CX + x1, CX + x2, CY + y1, CY + y2))
txt("ASSUMED land-group regions (AMD NDA) - routing intent only", CX, CY - 20.6, D, 0.6)

# ---------------- front: SVI3 VRM (left), CPU aux rails (right), PROM21 (top right), misc (top) ----------------
PH_NAMES = ["VDDCR %d" % (k + 1) for k in range(5)] + ["SOC 1", "SOC 2", "MISC"]
for k in range(8):
    y = 42.0 + 9.0 * k
    place("Q%d" % (k + 1), L, "MP62_PowerStage_SiC654_MLP55-31L_5x5", 11.15, y, value="PS %s SiC654" % PH_NAMES[k])
    place("L%d" % (k + 1), L, "MP62_IND_Eaton_FP4_10.2x6.8x5.0", 24.5, y, value="L %s FP4-150-R" % PH_NAMES[k])
    flag("Q%d" % (k + 1), "SOURCED-DIMS", "SiC654 5x5 MLP55-31L; pads approximate; current per AM5 IccMax (NDA) TBD")
    flag("L%d" % (k + 1), "SOURCED-DIMS", "Eaton FP4 10.2 x 6.8 x 5.0; value 150 nH [Estimate]")
place("CIN1", L, "MP62_AREA_12V_InCaps_5x75", 5.5, 73.5, value="12V in caps (8 phases)")
place("COUT1", L, "MP62_AREA_VDDCR_OutCaps_5x75", 33.5, 73.5, value="VDDCR/SOC/MISC out caps")
place("U3", L, "MP62_AREA_SVI3_Ctrl_RAA229139_6x6", 14.0, 117.0, value="U3 SVI3 3-rail ctrl RAA229139 (alt MP2857)")
flag("CIN1", "AREA", "12 V input MLCC field"); flag("COUT1", "AREA", "output caps; values from AMD VR design guide (NDA)")
flag("U3", "AREA", "SVI3 triple-rail controller candidate; part not frozen, config tools under NDA")
txt("12V SINGLE ENTRY (stock): LUG1/2 top-left", 3.0, 136.0, C, 0.6, left=True)
txt("-> U11 eFuse -> 12V plane L5+L6 >= 20 mm", 3.0, 134.4, C, 0.6, left=True)
txt("down the left edge to CIN1/VRM (~8 A at 88 W PPT);", 3.0, 132.8, C, 0.6, left=True)
txt(">= 8 mm across the top band to the right rails", 3.0, 131.2, C, 0.6, left=True)
txt("SVI3: VDDCR 5 ph + VDDCR_SOC 2 ph + VDD_MISC 1 ph = 8 x SiC654 + FP4; v3: 7600/9600 65 W (PPT 88 W, TDC 75 A, EDC 150 A); 105 W parts not supported", 20.0, 34.0, C, 0.7)
RIGHT = [("U4", "MP62_AREA_CPU_S5_Rails_28x22", 134.0, 45.0, "CPU S5/aux rails (1.8/3.3/MISC_S5)"),
         ("U5", "MP62_AREA_CPU_Seq_Misc_28x14", 134.0, 66.0, "CPU seq/straps/SVI3 pull-ups"),
         ("U6", "MP62_AREA_PROM21_Rails_28x18", 134.0, 86.0, "PROM21 rails"),
         ("U7", "MP62_AREA_5V_DIMM_VINBULK_14x8", 127.0, 104.0, "5V VIN_BULK 4x UDIMM"),
         ("U8", "MP62_AREA_VDDIO_MEM_Buck_14x8", 62.0, 110.0, "VDDIO_MEM_S3 1.1V")]
for ref, nm, x, y, v in RIGHT:
    place(ref, L, nm, x, y, value=v); flag(ref, "AREA", v + "; rail list [Unverified] until the AMD datasheet (NDA)")
place("U2", L, "MP62_PROM21_FCBGA_19x19_PLACEHOLDER", 110.0, 133.0, value="U2 PROM21 218-0891025 PLACEHOLDER")
flag("U2", "PLACEHOLDER-NDA", "19 x 19 body sourced; 484 synthetic balls at 0.8 (ballout NDA); thermal pad to the core plate (~7 W)")
place("Y1", L, "MP62_AREA_CLK_XTAL_10x6", 89.0, 140.0, value="Y1/Y2 48M + 32k (FCH)")
place("U9", L, "MP62_AREA_EC_RP2350_14x12", 66.0, 140.0, value="U9 EC RP2350")
place("U10", L, "MP62_AREA_BIOS_SPI_W25Q256_10x8", 82.0, 127.0, value="U10 FCH SPI 32MB (Dasharo)")
place("J4", L, "MP62_AREA_TPM_Header_10x6", 67.0, 126.0, value="J4 SPI TPM (opt.)")
place("J5", L, "MP62_AREA_DebugHdr_12x5", 66.0, 154.0, value="J5 debug UART/SWD/POST")
place("U11", L, "MP62_AREA_eFuse_TPS25985_14x12", 36.0, 146.0, value="U11 eFuse 12V IN (whole CB)")
place("U15", L, "MP62_AREA_PwrMon_INA228_10x6", 51.0, 146.0, value="U15 INA228 + RS1 0.5 mOhm (12V in, I2C0 0x45)")
place("U16", L, "MP62_AREA_USB10G_Hub_VL822_14x12", 90.0, 154.0, value="U16 VL822-Q7 USB 10G hub (J3 A1-A4)")
place("U17", L, "MP62_AREA_PROM21_SPI_8x6", 126.0, 150.0, value="U17 PROM21 SPI flash")
for ref, why in (("Y1", "48 MHz [Unverified]"), ("U9", "same as LGA1700, AM5 GPIO map"), ("U10", "FCH SPI ROM"), ("J4", "optional"),
                 ("J5", "debug"), ("U11", "same as LGA1700"), ("U15", "same as LGA1700"), ("U16", "NEW: VL822-Q7 9x9 QFN-76 (LCSC C42419379)"),
                 ("U17", "NEW: PROM21 own FW flash [Unverified]")):
    flag(ref, "AREA", why)
LUGS = [("LUG1", 27.95, "GND?"), ("LUG2", 40.75, "12V?")]
for ref, x, pol in LUGS:
    f_ = place(ref, L, "MP62_CB_BusBarLug_8x6_PLACEHOLDER", x, 159.8, center=False, value="%s %s" % (ref, pol))
    ni = pcbnew.NETINFO_ITEM(board, "LUG_" + ref); board.Add(ni)
    for pd in f_.Pads(): pd.SetNet(ni)
    txt("%s %s" % (ref, pol), x, 155.4, C, 0.7)
    flag(ref, "PLACEHOLDER", "stock lug position +-0.8 (photo); polarity M-CC7; same as LGA1700")
GPU_KO = (105.0, 160.5, 135.0, 169.5)
rule_area("GPU_BUSBAR_PASSTHROUGH", [(GPU_KO[0], GPU_KO[1]), (GPU_KO[2], GPU_KO[1]), (GPU_KO[2], GPU_KO[3]), (GPU_KO[0], GPU_KO[3])],
          ALLCU, fp=True, vias=True, tracks=True, pads=True, pour=True)
rect(*GPU_KO, C, 0.15)
txt("GPU BUS-BAR PASS-THROUGH (no CB lugs)", 120.0, 158.6, C, 0.6)
txt("keep-out notch +3 mm, all layers, both sides", 120.0, 157.4, C, 0.5)
place("J1", L, "MP62_CPULINK_MiniCoolEdge224_CardEdge_Fingers", XC, T, center=False, value="J1 CPU-LINK 224 fingers (AM5 map: docs/cpulink_224_pinout_am5.csv)")
flag("J1", "SOURCED (Amphenol AIC card drawing)", "physical identical to LGA1700; AM5 net map in docs/cpulink_224_pinout_am5.csv")
place("CAC1", L, "MP62_AREA_PEG_ACcaps_70x8", 80.0, 19.0, value="PCIe AC caps (GFX x16 + GPP x4)")
flag("CAC1", "AREA", "AC caps")
rule_area("TAB_FINGERS_NO_VIAS", [(XL - 0.5, 0.0), (XR + 0.5, 0.0), (XR + 0.5, 6.0), (XL - 0.5, 6.0)], ALLCU, vias=True, pour=True)

# ---------------- back side (identical positions to the LGA1700 CB) ----------------
DIMM_YC = 95.6
DIMMS = [("J6", 15.8, "CH-A DIMM1 near"), ("J7", 6.5, "CH-A DIMM2 far"), ("J9", 140.55, "CH-B DIMM1 near"), ("J10", 149.85, "CH-B DIMM2 far")]
for ref, x, nm in DIMMS:
    f_ = place(ref, L, "MP62_DIMM_DDR5_288P_Vert_UMAX_90414_ShortLatch", x, DIMM_YC, rot=90, side="B", value="%s %s DDR5 UDIMM" % (ref, nm))
    f_.Reference().SetLayer(pcbnew.B_Fab)
    flag(ref, "SOURCED-DIMS (UMAX C-90414)", "pads approximate; 2DPC on AM5 = DDR5-3600 (8600G spec) [Sourced]")
for (x1, x2) in ((2.5, 18.5), (137.0, 153.0)):
    rect(x1, 22.5, x2, 168.2, E2, 0.1)
txt("STOCK DDR3 PAIR 22.5-168.2", 10.5, 20.5, E2, 0.55); txt("STOCK DDR3 PAIR 22.5-168.2", 145.0, 20.5, E2, 0.55)
txt("BACK: 4 x DDR5 UDIMM vertical, 2DPC (AM5: 2DPC 1R/2R = DDR5-3600); module top <= 33.25 off the back -> M-CC15; CH-A J6 near / J7 far", 1.0, 172.0, E2, 0.6, left=True)
txt("CH-B J9 near / J10 far", 128.0, 172.0, E2, 0.6, left=True)
for k in range(8):
    y = 40 + 9 * k
    rect(9.05, y - 2.6, 13.25, y + 2.6, E2, 0.08)
txt("VRM via corridor x 9.05-13.25 (8 stages, between the J7/J6 pad rows)", 11.15, 120.0, E2, 0.5, angle=90)
place("J8", L, "MP62_CB_M2_2280_MKey_PLACEHOLDER", 123.0, 24.8, side="B", center=False, value="J8 M.2 2280 boot (PROM21 Gen4 x4, v3)")
flag("J8", "PLACEHOLDER", "M.2 2280 M-key outline; v3 source = PROM21 free Gen4 x4 (CPU GPP#2 -> Face S slot B)")
place("J3", L, "MP62_AREA_J3_MCIO_RA_IOB_44x12", 78.0, 160.0, side="B", value="J3 IOB-HS MCIO 124 RA (AM5 host map docs/mp62-cb-j3_mcio124_host-end_am5.csv)")
flag("J3", "AREA (part = LGA1700 CB J3)", "same physical/position; AM5 host-end sources re-mapped")
place("BT1", L, "MP62_AREA_BT1_CR2032_22x16", 70.0, 128.0, side="B", value="BT1 CR2032 DNP (VBAT_RTC from the IOB via J3 B26)")
place("CB1", L, "MP62_AREA_Bulk12V_Back_16x30", 28.0, 55.0, side="B", value="12V bulk L")
place("CB2", L, "MP62_AREA_Bulk12V_Back_16x30", 128.5, 55.0, side="B", value="12V bulk R")
place("U14", L, "MP62_AREA_HDA_ALC897_DNP_10x10", 46.0, 120.0, side="B", value="U14 ALC897 DNP (FCH AZ)")
for ref in ("BT1", "CB1", "CB2", "U14"): flag(ref, "AREA", "same as LGA1700")
BPZ = (37.25, 40.0, 118.75, 107.0)
rule_area("MP62_BACKPLATE_B", [(BPZ[0], BPZ[1]), (BPZ[2], BPZ[1]), (BPZ[2], BPZ[3]), (BPZ[0], BPZ[3])], [pcbnew.B_Cu], fp=True)
rect(*BPZ, E2, 0.25)
txt("BACK: MP62 steel backplate 81.5 x 67 (insulated; PEM nuts for the frame seat screws; window for socket-cavity MLCCs) - same as LGA1700", 78.0, BPZ[1] + 1.5, E2, 0.7)
rect(100.0, 123.0, 120.0, 143.0, E2, 0.12); txt("BACK: PROM21 decoupling field (keep free)", 110.0, 121.3, E2, 0.6)
# stock AM5 cooler reference (Dwgs only; MP62 never uses it)
txt("stock AM5 cooler / ILM pattern is drawn in the U1 footprint (Dwgs, NOT drilled)", CX, CY - 49.5, D, 0.6)

# ---------------- routing intent (Cmts) ----------------
txt("DDR5 CH-A / CH-B exit the +Y package edge -> left (J6 near, J7 far) / right (J9 near, J10 far), daisy chain on L3/L8 [orientation assumed]", CX, 98.5, C, 0.6)
txt("GFX x16 + GPP#1 x4 + GPP#2 x4 (slot B) -> down to J1 (Face P / Face S, CPU-LINK v3)", CX, 30.0, C, 0.65)
txt("CPU x4 Gen4 -> PROM21 (right, up)", 107.0, 112.0, C, 0.65)
txt("USB4/10G + DP (assumed left) -> up to J3 (back) / U16 hub", CX, 50.5, C, 0.6)
txt("PROM21 Gen4 x4 -> J8 M.2 (back, v3)", 78.0, 38.0, C, 0.65)

NOTES = [
 "MP62 AM5 CPU BOARD (CB) DRAFT rev A-am5 fp0 - frame: x right, y up from the board bottom, FRONT = socket/core side",
 "1  U1 Socket AM5 LGA1718 PLACEHOLDER at the measured pedestal (78.41, 73.25): 1718 SYNTHETIC lands, 0.81 x 0.94 hex (Lotes). AMD land map NDA.",
 "   Orientation (DDR to +y, PCIe to -y) is an assumption -> open item; replace U1 with the vendor footprint before any routing.",
 "2  MP62 contact frame 71 x 54 x <= 6.0 + 4 ears on the FIXED 69.5 x 55 core holes, 4 seat screws H5-H8 - all as LGA1700; stock ILM not fitted.",
 "3  SVI3 VRM front-left: 5 VDDCR + 2 SOC + 1 MISC = 8 x SiC654 + FP4 (x 11.15 / 24.5, y 42-105); U3 RAA229139-class 3-rail controller.",
 "4  U2 PROM21 (19 x 19, ~7 W) front top-right under the plate; U16 VL822 10G hub top-centre; U17 PROM21 SPI.",
 "5  BACK: 4 x DDR5 UDIMM vertical 2DPC (as LGA1700); M.2 boot on PROM21 x4 (v3); J3 MCIO 124 top; backplate centre.",
 "5b 12V: ONE stock lug pair top-left -> U11 eFuse; GPU bus-bar pass-through keep-out top-right (as LGA1700).",
 "6  Front height limit 6.0 (5.5 rec.) under the plate (x 16.2-140.4, y 22.5-164.4).",
 "7  Stackup proposal JLC 10L 1.6: L1 S / L2 G / L3 S / L4 G / L5 P / L6 P / L7 G / L8 S / L9 G / L10 S; POFV; 85/90/40 ohm.",
 "8  PLACEHOLDERS flagged in placeholders_flagged.txt; NDA-synthetic: U1, U2. No nets, not routed.",
 "9  CPU-LINK J1 + IOB-HS J3 physicals unchanged; AM5 pin maps in docs/*_am5.csv (delta vs ICD rev 3).",
]
for i, n in enumerate(NOTES):
    txt(n, 162.0, 168.0 - i * 3.2, pcbnew.User_1, 1.3 if i == 0 else 1.1, left=True)

# ---------------- report ----------------
rep = ["outline symmetric-difference above shoulder: %.3f mm2" % _sym_hi] + LGRP
PLB = box(*PLATE)
fl = ["# MP62 AM5 CB fp0 - placeholder flags (every placed footprint). PLACEHOLDER-NDA = synthetic pads, DO NOT FAB.",
      "%-5s %-4s %-38s %s" % ("ref", "side", "status", "note")]
for ref, f, val, side in placed:
    try:
        bb = f.GetCourtyard(pcbnew.B_CrtYd if side == "B" else pcbnew.F_CrtYd).BBox()
        if bb.GetWidth() <= 0: raise ValueError
    except Exception:
        bb = f.GetBoundingBox(False, False)
    x1 = pcbnew.ToMM(bb.GetLeft()) - OX; x2 = pcbnew.ToMM(bb.GetRight()) - OX
    y2 = OY - pcbnew.ToMM(bb.GetTop()); y1 = OY - pcbnew.ToMM(bb.GetBottom())
    bx = box(x1, y1, x2, y2)
    inside = BOARD.buffer(0.01).contains(bx) if not ref.startswith("J1") else True
    under = "UNDER PLATE" if (side == "F" and bx.intersects(PLB)) else ""
    st, note = FLAG.get(ref, ("UNFLAGGED", ""))
    rep.append("%-5s %s x %6.1f..%6.1f y %6.1f..%6.1f %-9s %-11s %-22s %s" % (ref, side, x1, x2, y1, y2, "in-board" if inside else "OUTSIDE?", under, st, val))
    fl.append("%-5s %-4s %-38s %s" % (ref, side, st, note))
    try:
        f.SetField("MP62_STATUS", st)
        fld = f.GetFieldByName("MP62_STATUS"); fld.SetVisible(False); fld.SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab)
    except Exception:
        pass
open(os.path.join(PRJ, "fitcheck_floorplan.txt"), "w").write("\n".join(rep) + "\n")
open(os.path.join(PRJ, "placeholders_flagged.txt"), "w").write("\n".join(fl) + "\n")
print("\n".join(rep))
pcbnew.SaveBoard(OUT, board)
print("saved", OUT)
