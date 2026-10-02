#!/usr/bin/env python3
"""MacPro6,2 LGA1700 CPU board (CB) rev-A part-level FLOORPLAN fl1, KiCad 9 pcbnew API (system python3).
Same frame as the COM-HPC carrier: origin bottom-left, x right (0..156), y up from the board bottom (tab tip y=1.722,
shoulder y=12.982, top edge y=169.5). FRONT = socket/core side. KiCad sheet: X = 60 + x, Y = 240 - y.
The stock outline DXF is a back-view scan; it is mirror-symmetric about x = 78 except for the stock tab
(checked by build: symmetric-difference area printed below), so it is used unmirrored and the stock tab is replaced."""
import json, math, os, sys
import pcbnew, ezdxf
from pcbnew import FromMM, VECTOR2I
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(PRJ, "macpro62_lga1700.kicad_pcb")
SYS = "/usr/share/kicad/footprints"
LOC = os.path.join(PRJ, "MP62_LGA_Placeholders.pretty")
DXF = "/workspace/bracket/cpu_board/cpu_board_outline_corrected.dxf"
OX, OY = 60.0, 240.0
def P(x, y): return VECTOR2I(FromMM(float(OX + x)), FromMM(float(OY - y)))

board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(10)
ds = board.GetDesignSettings()
ds.SetBoardThickness(FromMM(1.6))
# JLC 10-layer: 0.09/0.09 track/space (3.5/3.5 mil), via 0.15 drill / 0.25 pad, via-in-pad POFV (default >= 6L)
ds.m_TrackMinWidth = FromMM(0.09); ds.m_MinClearance = FromMM(0.09)
ds.m_ViasMinSize = FromMM(0.25); ds.m_MinThroughDrill = FromMM(0.15)
ds.m_CopperEdgeClearance = FromMM(0.5); ds.m_HoleClearance = FromMM(0.2); ds.m_HoleToHoleMin = FromMM(0.5)
ds.m_SilkClearance = FromMM(0.0)
try:
    ps = pcbnew.PAGE_INFO(); ps.SetType("A3"); board.SetPageSettings(ps)
except Exception:
    pass
tb = board.GetTitleBlock()
tb.SetTitle("MacPro6,2 LGA1700 CPU board (CB) - rev A part-level floorplan fl2 (4 x DDR5 UDIMM)")
tb.SetRevision("A-fl2.3"); tb.SetDate("2026-10-02"); tb.SetCompany("MacPro6,2 / Aidan Winkler")
tb.SetComment(0, "Edge.Cuts: stock riser outline (cpu_board_outline_corrected.dxf) + Mini Cool Edge 224 tab 79.89 wide at x=78 (as the CC carrier)")
tb.SetComment(1, "Stackup: JLC 10L 1.6 mm: L1 S / L2 G / L3 S / L4 G / L5 P / L6 P / L7 G / L8 S / L9 G / L10 S, ENIG + hard-gold fingers, POFV")
tb.SetComment(2, "U1 LGA1700 (Foxconn PE17007) under the measured pedestal (78.41, 73.25); U2 PCH Z790 FCBGA 28x25; lands/balls from Intel public ballouts")
tb.SetComment(3, "Placeholders: real outer dims where sourced, pads approximate. Front parts <= 6.0 mm (plate). Not routed.")

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
    libpath = LOC if lib == "MP62_LGA_Placeholders" else os.path.join(SYS, lib + ".pretty")
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

L = "MP62_LGA_Placeholders"
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

# ---------------- CPU socket, frame, holes ----------------
PED = (78.41, 73.25); PW, PH = 40.6, 41.1
CX, CY = PED
place("U1", L, "MP62_LGA1700_Socket_IntelBallout_0.8", CX, CY, value="U1 LGA1700 socket PE17007-11NK0-1H")
CORE_HOLES = [(43.25, 46.0), (112.75, 46.0), (43.25, 101.0), (112.75, 101.0)]
for i, (x, y) in enumerate(CORE_HOLES):
    f_ = place("H%d" % (i + 1), L, "MP62_CB_CoreMountHole_D5.0_Pad9", x, y, center=False, value="CORE D5 69.5x55 FIXED")
    GNDN = pcbnew.NETINFO_ITEM(board, "GND_CORE_H%d" % (i + 1)); board.Add(GNDN)
    for pd in f_.Pads(): pd.SetNet(GNDN)
    n = 32
    rule_area("CORE_BOSS_%d_%d" % (x, y), [(x + 6 * math.cos(2 * math.pi * i / n), y + 6 * math.sin(2 * math.pi * i / n)) for i in range(n)],
              ALLCU, tracks=True, vias=True)
SEAT = [(CX - 28, CY - 21), (CX + 28, CY - 21), (CX - 28, CY + 21), (CX + 28, CY + 21)]
for i, (x, y) in enumerate(SEAT):
    place("H%d" % (i + 5), L, "MP62_CB_FrameSeatScrew_D3.4_NPTH", x, y, center=False, value="FRAME SEAT M3 -> PEM in backplate")
# MP62 contact frame (Eco1): 71 x 54 body centred on the socket (long axis = package X = board x) + 4 ears on the core holes
FX, FY = 35.5, 27.0
rect(CX - FX, CY - FY, CX + FX, CY + FY, E1, 0.25)
for (x, y) in CORE_HOLES:
    circle(x, y, 5.5, E1, 0.25)
rect(CX - 23.0, CY - 19.25, CX + 23.0, CY + 19.25, E1, 0.12)
txt("MP62 CONTACT FRAME 71 x 54 x <= 6.0 (7075) + 4 ears on the core holes; inner window ~46 x 38.5 bears on the substrate", CX, CY + FY + 1.4, E1, 0.75)
# pedestal + plate
rect(PED[0] - PW / 2, PED[1] - PH / 2, PED[0] + PW / 2, PED[1] + PH / 2, D, 0.3)
txt("CORE PEDESTAL 40.6 x 41.1 (measured)", CX, CY - PH / 2 + 1.2, D, 0.8)
PLATE = (16.2, 22.5, 140.4, 164.4)
rect(*PLATE, C, 0.3)
txt("BLACK PLATE 124 x 142 = FRONT HEIGHT ZONE: every front part <= 6.0 mm (5.5 rec.); board floats on springs, gap = IHS Z 6.53-7.53", 78.0, 165.4, C, 0.75)
# LGA interface regions from the public ballout (land groups), Dwgs
import csv as _csv
grp = {}
for r in _csv.DictReader(open(os.path.join(PRJ, "docs", "u1_lga1700_lands.csv"))):
    n = r["name"]; k = None
    for pre, lab in (("DDR0", "DDR0"), ("DDR1", "DDR1"), ("PCIE", "PCIe x16+x4"), ("DMI", "DMI x8"), ("DDI", "DDI A-E"),
                     ("VCCGT", "VCCGT"), ("VCCIN_AUX", "VCCIN_AUX"), ("VDD2", "VDD2")):
        if n.startswith(pre) and (pre not in ("VCCGT", "VCCIN_AUX") or n == pre): k = lab; break
    if n == "VCCCORE": k = "VCCCORE"
    if k: grp.setdefault(k, []).append((CX + float(r["x_intel_mm"]), CY + float(r["y_intel_mm"])))
LGRP = []
for k, pts in grp.items():
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    rect(min(xs) - 0.4, min(ys) - 0.4, max(xs) + 0.4, max(ys) + 0.4, D, 0.12)
    txt("%s (%d)" % (k, len(pts)), (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, D, 0.7)
    LGRP.append("  land group %-12s n=%4d  board x %.1f..%.1f  y %.1f..%.1f" % (k, len(pts), min(xs), max(xs), min(ys), max(ys)))

# ---------------- front: VRM (left), CPU aux rails (right), PCH (top right), misc (top) ----------------
for k in range(7):
    y = 42.0 + 9.0 * k
    nm = "GT" if k == 6 else "C%d" % (k + 1)
    place("Q%d" % (k + 1), L, "MP62_PowerStage_SiC654_MLP55-31L_5x5", 11.15, y, value="PS %s SiC654" % nm)
    place("L%d" % (k + 1), L, "MP62_IND_Eaton_FP4_10.2x6.8x5.0", 24.5, y, value="L %s FP4-150-R" % nm)
place("CIN1", L, "MP62_AREA_12V_InCaps_5x66", 5.5, 69.0, value="12V in caps")
place("COUT1", L, "MP62_AREA_VCCCORE_OutCaps_5x66", 33.5, 69.0, value="VCCCORE/GT out caps")
place("U3", L, "MP62_AREA_VRctrl_RT3628AE_8x8", 14.0, 108.0, value="U3 RT3628AE (C3249940)")
txt("12V SINGLE ENTRY (stock): LUG1/2 top-left", 3.0, 136.0, C, 0.6, left=True)
txt("-> U11 eFuse -> 12V plane L5+L6 >= 20 mm", 3.0, 134.4, C, 0.6, left=True)
txt("down the left edge to CIN1/VRM (~13 A pk);", 3.0, 132.8, C, 0.6, left=True)
txt(">= 8 mm across the top band to the right rails", 3.0, 131.2, C, 0.6, left=True)
txt("VCCCORE 6 phases + VCCGT 1 phase (7 x SiC654 50 A + FP4 0.15 uH h5.0), 120 A IccMax (35 W) / 160 A (65 W 6P+8E)", 20.0, 34.0, C, 0.7)
place("U4", L, "MP62_AREA_VCCIN_AUX_2ph_28x22", 134.0, 45.0, value="VCCIN_AUX 2ph")
place("U5", L, "MP62_AREA_VCC1P05_1P8_PROC_28x14", 134.0, 66.0, value="VCC1P05/1P8_PROC")
place("U6", L, "MP62_AREA_PCH_Rails_28x18", 134.0, 86.0, value="PCH rails")
place("U7", L, "MP62_AREA_5V_DIMM_VINBULK_14x8", 127.0, 104.0, value="5V VIN_BULK 4x UDIMM")
place("U8", L, "MP62_AREA_VDD2_Buck_14x8", 62.0, 110.0, value="VDD2 1.1V")
place("U2", L, "MP62_PCH700_FCBGA1045_28x25_IntelBallout", 110.0, 133.0, value="U2 PCH Z790 FH82Z790")
place("Y1", L, "MP62_AREA_CLK_XTAL_10x6", 89.0, 140.0, value="Y1/Y2 38.4M + 32k")
place("U9", L, "MP62_AREA_EC_RP2350_14x12", 66.0, 140.0, value="U9 EC RP2350")
place("U10", L, "MP62_AREA_BIOS_SPI_W25Q256_10x8", 82.0, 127.0, value="U10 BIOS SPI 32MB")
place("J4", L, "MP62_AREA_TPM_Header_10x6", 67.0, 126.0, value="J4 SPI TPM")
place("J5", L, "MP62_AREA_DebugHdr_12x5", 66.0, 154.0, value="J5 debug UART/SWD")
place("U11", L, "MP62_AREA_eFuse_TPS25985_14x12", 36.0, 146.0, value="U11 eFuse 12V IN (whole CB)")
# ICD rev 2 (live power target): CB 12 V telemetry for the BP MCU (I2C0 0x45) + fast alert on CPU-LINK A105 PWR_ALERT#
place("U15", L, "MP62_AREA_PwrMon_INA228_10x6", 51.0, 146.0, value="U15 INA228 + RS1 0.5 mOhm (12V in, I2C0 0x45)")
# Stock 12 V entry = ONE lug pair at the top-left (CPU-side view), Aidan + photo 2026-10-01: legs x 24.0-31.9 / 36.9-44.7
# (photo homography on the 4 core holes, corrected by the notch walls 24/48; +-0.8). No lugs on the right.
LUGS = [("LUG1", 27.95, "GND?"), ("LUG2", 40.75, "12V?")]
for ref, x, pol in LUGS:
    f_ = place(ref, L, "MP62_CB_BusBarLug_8x6_PLACEHOLDER", x, 159.8, center=False, value="%s %s" % (ref, pol))
    ni = pcbnew.NETINFO_ITEM(board, "LUG_" + ref); board.Add(ni)
    for pd in f_.Pads(): pd.SetNet(ni)
    txt("%s %s" % (ref, pol), x, 155.4, C, 0.7)
# Right notch (x 108-132, y 163.5-169.5) = pass-through for the GPU power bus bars/lugs (Aidan 2026-10-01 ~21:19 ET);
# the CB has NO lugs there. Keep-out = notch + 3 mm margin [Proposal]: no parts, pads, tracks, vias or pour, both sides.
GPU_KO = (105.0, 160.5, 135.0, 169.5)
rule_area("GPU_BUSBAR_PASSTHROUGH", [(GPU_KO[0], GPU_KO[1]), (GPU_KO[2], GPU_KO[1]), (GPU_KO[2], GPU_KO[3]), (GPU_KO[0], GPU_KO[3])],
          ALLCU, fp=True, vias=True, tracks=True, pads=True, pour=True)
rect(*GPU_KO, C, 0.15)
txt("GPU BUS-BAR PASS-THROUGH (no CB lugs)", 120.0, 158.6, C, 0.6)
txt("keep-out notch +3 mm, all layers, both sides", 120.0, 157.4, C, 0.5)
place("J1", L, "MP62_CPULINK_MiniCoolEdge224_CardEdge_Fingers", XC, T, center=False, value="J1 CPU-LINK 224 fingers")
place("CAC1", L, "MP62_AREA_PEG_ACcaps_70x8", 80.0, 19.0, value="PCIe AC caps")
rule_area("TAB_FINGERS_NO_VIAS", [(XL - 0.5, 0.0), (XR + 0.5, 0.0), (XR + 0.5, 6.0), (XL - 0.5, 6.0)], ALLCU, vias=True, pour=True)

# ---------------- back side ----------------
# 4 x DDR5 UDIMM vertical in the stock DIMM strips (stock card centrelines x 6.5 / 15.8 and 140.55 / 149.85, 9.3 pitch;
# stock strip y 22.5-168.2). 2DPC daisy chain: CPU -> inner (near, DIMM1) -> outer (far, DIMM2; populate first).
DIMM_YC = 95.6
DIMMS = [("J6", 15.8, "CH-A DIMM1 near"), ("J7", 6.5, "CH-A DIMM2 far"), ("J9", 140.55, "CH-B DIMM1 near"), ("J10", 149.85, "CH-B DIMM2 far")]
for ref, x, nm in DIMMS:
    f_ = place(ref, L, "MP62_DIMM_DDR5_288P_Vert_UMAX_90414_ShortLatch", x, DIMM_YC, rot=90, side="B", value="%s %s DDR5 UDIMM" % (ref, nm))
    f_.Reference().SetLayer(pcbnew.B_Fab)          # 9.3 pitch leaves no room for silk refs between the sockets
for (x1, x2) in ((2.5, 18.5), (137.0, 153.0)):
    rect(x1, 22.5, x2, 168.2, E2, 0.1)                                       # stock DIMM-pair body (scan)
txt("STOCK DDR3 PAIR 22.5-168.2", 10.5, 20.5, E2, 0.55); txt("STOCK DDR3 PAIR 22.5-168.2", 145.0, 20.5, E2, 0.55)
txt("BACK: 4 x DDR5 UDIMM vertical, module top <= 33.25 off the back (stock DDR3 30.0 + seat) -> confirm M-CC15; CH-A J6 near / J7 far", 1.0, 172.0, E2, 0.6, left=True)
txt("CH-B J9 near / J10 far", 128.0, 172.0, E2, 0.6, left=True)
for y in range(40, 104, 9):
    rect(9.05, y - 2.6, 13.25, y + 2.6, E2, 0.08)                            # via corridor under each power stage
txt("VRM via corridor x 9.05-13.25 (between the J7/J6 pad rows)", 11.15, 112.5, E2, 0.5, angle=90)
place("J8", L, "MP62_CB_M2_2280_MKey_PLACEHOLDER", 123.0, 24.8, side="B", center=False, value="J8 M.2 2280 boot (PCH x4)")
place("J3", L, "MP62_AREA_J3_MCIO_RA_IOB_44x12", 78.0, 160.0, side="B", value="J3 IOB-HS MCIO 124 RA (host end, docs/mp62-cb-j3_mcio124_host-end.csv)")
place("BT1", L, "MP62_AREA_BT1_CR2032_22x16", 70.0, 128.0, side="B", value="BT1 CR2032 DNP (VBAT_RTC from the IOB via J3 B26)")
place("CB1", L, "MP62_AREA_Bulk12V_Back_16x30", 28.0, 55.0, side="B", value="12V bulk L")
place("CB2", L, "MP62_AREA_Bulk12V_Back_16x30", 128.5, 55.0, side="B", value="12V bulk R")
# U13 i226-V removed 2026-10-02 (ICD): both i226-V are on the IOB (PCH RP3 / RP4 PCIe x1 over J3)
place("U14", L, "MP62_AREA_HDA_ALC897_DNP_10x10", 46.0, 120.0, side="B", value="U14 ALC897 DNP")
BPZ = (37.25, 40.0, 118.75, 107.0)
rule_area("MP62_BACKPLATE_B", [(BPZ[0], BPZ[1]), (BPZ[2], BPZ[1]), (BPZ[2], BPZ[3]), (BPZ[0], BPZ[3])], [pcbnew.B_Cu], fp=True)
rect(*BPZ, E2, 0.25)
txt("BACK: MP62 steel backplate 81.5 x 67 (insulated; PEM nuts for the frame seat screws; window for socket-cavity MLCCs)", 78.0, BPZ[1] + 1.5, E2, 0.7)
rect(96.0, 120.5, 124.0, 145.5, E2, 0.12); txt("BACK: PCH decoupling field (keep free)", 110.0, 118.8, E2, 0.6)

# ---------------- routing intent arrows/notes (Cmts) ----------------
txt("DDR0/DDR1 exit the +Y package edge -> left (CH-A J6 near, J7 far) / right (CH-B J9 near, J10 far), daisy chain on L3/L8", CX, 96.0, C, 0.65)
txt("PEG x16 Gen5 + CPU x4 Gen4 -> down to J1 (Face P / Face S)", CX, 30.0, C, 0.7)
txt("DMI x8 -> PCH (right, up)", 107.0, 112.0, C, 0.65)
txt("DDI lands (bottom-left of the package): DDI-B 4-lane + DDI-C 2-lane DP -> J3 -> IOB C5 / C6 (plan sec. 7, ICD)", CX, 50.5, C, 0.6)
txt("PCH x4 Gen4 -> J8 M.2 (back)", 78.0, 38.0, C, 0.65)

NOTES = [
 "MP62 LGA1700 CPU BOARD (CB) rev A floorplan fl2 - frame: x right, y up from the board bottom, FRONT = socket/core side",
 "1  U1 LGA1700 (Foxconn PE17007-11NK0-1H) centred under the measured pedestal (78.41, 73.25); package X (45) along board x.",
 "   Lands from Intel 743844-001 ballout (public). Orientation assumes the ballout is a top view - VERIFY (pin-1 corner).",
 "2  MP62 contact frame 71 x 54 x <= 6.0 + 4 ears on the FIXED 69.5 x 55 core holes; 4 own seat screws (H5-H8) into the backplate.",
 "3  VRM front-left: 6 + 1 phases SiC654 (x 11.15, vias in the back corridor between J7/J6) + Eaton FP4 (5.0 mm); RT3628AE.",
 "4  U2 PCH (Z790, 28 x 25, 0.5 pitch) front top-right, under the plate (thermal pad to the core plate, 6 W).",
 "5  BACK: 4 x DDR5 UDIMM vertical (UMAX 90414 short latch) at the stock centrelines, 2DPC; M.2 bottom; J3 top; backplate centre.",
 "5b 12V: ONE stock lug pair at the top-left (LUG1 x 27.95, LUG2 x 40.75; photo 2026-10-01) -> one eFuse U11; no right-side lugs.",
 "6  Front height limit 6.0 (5.5 rec.) everywhere under the plate (x 16.2-140.4, y 22.5-164.4): no polymer cans, no MCIO on the front.",
 "7  Stackup JLC 10L 1.6: L1 S / L2 G / L3 S / L4 G / L5 P / L6 P / L7 G / L8 S / L9 G / L10 S; POFV via-in-pad; 85/90/100 ohm.",
 "8  PLACEHOLDERS: real outer dims where sourced (FP4, SiC654, PCH, LGA, M.2, DIMM socket C-90414); pads approximate; no nets.",
 "9  DIMM top <= 33.25 mm off the back (seat 2.0 + 31.25) vs stock DDR3 30.0 + seat: confirm M-CC15; VLP 18.75 UDIMM = fallback.",
]
for i, n in enumerate(NOTES):
    txt(n, 162.0, 168.0 - i * 3.2, pcbnew.User_1, 1.3 if i == 0 else 1.1, left=True)

# ---------------- report ----------------
rep = ["outline symmetric-difference above shoulder: %.3f mm2" % _sym_hi] + LGRP
PLB = box(*PLATE)
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
    rep.append("%-5s %s x %6.1f..%6.1f y %6.1f..%6.1f %-9s %-11s %s" % (ref, side, x1, x2, y1, y2, "in-board" if inside else "OUTSIDE?", under, val))
open(os.path.join(PRJ, "fitcheck_floorplan.txt"), "w").write("\n".join(rep) + "\n")
print("\n".join(rep))
pcbnew.SaveBoard(OUT, board)
print("saved", OUT)
