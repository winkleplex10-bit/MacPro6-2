#!/usr/bin/env python3
"""Build the MP62 I/O board (IOB rev A0) floorplan (KiCad 9 pcbnew API, system python3).
Frame: stock I/O-board BACK-VIEW frame of /workspace/bracket/io_board (origin bottom-left virtual corner, Y up toward the MEG-Array/logic-board end).
KiCad shows the board from the FRONT (port side): KiCad F = FRONT (ports, speaker, coin cell, button), B = BACK (PSU side).
KiCad position = (OX + (W - Xb), OY - Y). Aux/grid origin = back-view origin mirrored (front-view bottom-right corner)."""
import json, math, os, sys
import pcbnew
from pcbnew import FromMM, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(PRJ, "macpro62-io-board.kicad_pcb"); LIB = os.path.join(PRJ, "MP62_IO.pretty")
g = json.load(open(os.path.join(HERE, "io_geom.json"))); W = g["W"]
OX, OY = 40.0, 200.0
def P(xb, y): return VECTOR2I(FromMM(OX + (W - xb)), FromMM(OY - y))
board = pcbnew.NewBoard(OUT); board.SetCopperLayerCount(6)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6))
ds.m_TrackMinWidth = FromMM(0.1); ds.m_MinClearance = FromMM(0.1); ds.m_ViasMinSize = FromMM(0.45); ds.m_MinThroughDrill = FromMM(0.3)
ds.m_CopperEdgeClearance = FromMM(0.3); ds.m_HoleClearance = FromMM(0.2); ds.m_HoleToHoleMin = FromMM(0.25); ds.m_SilkClearance = FromMM(0.0)
ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
tb = board.GetTitleBlock(); tb.SetTitle("MP62 I/O board IOB rev A0 - FLOORPLAN (6 x USB-C DP-alt, 4 x USB-A, HDMI, 2 x RJ45, stock audio/speaker/PSU)")
tb.SetRevision("A0-floorplan"); tb.SetDate("2026-10-02"); tb.SetCompany("MacPro6,2 / Aidan Winkler (open spec)")
tb.SetComment(0, "Viewed from the FRONT (port side). Coordinates in docs = stock back-view frame (Xb, Y): KiCad x = OX + 101.0 - Xb")
tb.SetComment(1, "Stackup JLC06161H-2116 6L 1.6 mm (L1 sig, L2 GND, L3 sig, L4 PWR, L5 GND, L6 sig)")
tb.SetComment(2, "F: ports (vertical), speaker, coin cell, button, light-pipe LEDs, 5 V power stage. B: MCIO HS1 + display link, PSU connectors, PD/mux/redriver ICs, i226-V")
tb.SetComment(3, "PLACEMENT ONLY: not routed; vertical port connectors and most IC land patterns are PLACEHOLDERS")

def seg(x1, y1, x2, y2, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def arc3(a, m, b, layer, w=0.05):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*a), P(*m), P(*b)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def circle(x, y, r, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(P(x, y)); s.SetEnd(P(x + r, y)); s.SetLayer(layer); s.SetWidth(FromMM(w)); board.Add(s)
def rectd(x1, y1, x2, y2, layer, w=0.1):
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))): seg(*a, *b, layer, w)
def txt(s, x, y, layer=pcbnew.Cmts_User, size=1.0, angle=0.0, mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(size * 0.15)); t.SetTextAngleDegrees(angle); t.SetMirrored(mirror); board.Add(t)

def fillet_poly(verts, radii):
    """return list of ('L',a,b) / ('A',a,m,b) for a closed polygon with per-vertex fillet radii"""
    n = len(verts); pts = []
    for i in range(n):
        V = verts[i]; A = verts[i - 1]; B = verts[(i + 1) % n]; r = radii[i]
        u1 = [(A[0] - V[0]), (A[1] - V[1])]; l1 = math.hypot(*u1); u1 = [u1[0] / l1, u1[1] / l1]
        u2 = [(B[0] - V[0]), (B[1] - V[1])]; l2 = math.hypot(*u2); u2 = [u2[0] / l2, u2[1] / l2]
        th = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1]))) / 2
        t = r / math.tan(th); T1 = (V[0] + u1[0] * t, V[1] + u1[1] * t); T2 = (V[0] + u2[0] * t, V[1] + u2[1] * t)
        bis = [u1[0] + u2[0], u1[1] + u2[1]]; lb = math.hypot(*bis); bis = [bis[0] / lb, bis[1] / lb]
        C = (V[0] + bis[0] * r / math.sin(th), V[1] + bis[1] * r / math.sin(th)); M = (C[0] - bis[0] * r, C[1] - bis[1] * r)
        pts.append((T1, M, T2))
    out = []
    for i in range(n):
        out.append(("A",) + pts[i]); out.append(("L", pts[i][2], pts[(i + 1) % n][0]))
    return out
br = g["board_radii"]
outline = fillet_poly(g["board_vertices"], [br["BL"], br["BR"], br["R_low"], br["R_up"], br["L_up"], br["L_low"]])
wr = g["window"]["radii"]
cut = fillet_poly(g["window"]["vertices_sharp"], [wr["BL"], wr["BR"], wr["R_low"], wr["R_up"], wr["L_up"], wr["L_low"]])
for e in outline + cut:
    if e[0] == "L": seg(*e[1], *e[2], pcbnew.Edge_Cuts, 0.05)
    else: arc3(e[1], e[2], e[3], pcbnew.Edge_Cuts, 0.05)

FP = []
def place(ref, name, xb, y, rot=0.0, side="F", value=None, dnp=False):
    f = pcbnew.FootprintLoad(LIB, name)
    if f is None: sys.exit("missing " + name)
    f.SetFPID(pcbnew.LIB_ID("MP62_IO", name)); f.SetReference(ref); f.SetValue(value or name)
    f.SetPosition(P(xb, y)); f.SetOrientationDegrees(rot)
    board.Add(f)
    if side == "B": f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    if dnp: f.SetDNP(True); f.SetExcludedFromBOM(True)
    f.Reference().SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab)
    FP.append((ref, name, xb, y, rot, side, value or name, dnp)); return f

# ---------------- port grid = centres of the stock 821-2222-A flex cut-outs (flatbed scan 2026-10-02; plate frame, +-0.15) ----------------
# Heights (board top -> mouth) needed for D0 = 18.0 / 16.5: USB-C 17.90 (H) / 17.82 (O), USB-A 17.49 / 17.38, HDMI 17.24, RJ45 face <= 13.6 (plan 4.7.4)
XH, XO = 43.09, 63.69
CY = [75.76, 65.84, 55.97]
for i, y in enumerate(CY):
    place("J%d" % (11 + i), "MP62_USB_C_24P_Vertical_PLACEHOLDER", XH, y, 0, "F", ["C1 GPU DP L0 (4-lane)", "C2 GPU DP L1 (4-lane)", "C3 GPU DP L3 (2-lane)"][i] + "; FG-ST-C-24P-VT-SMT-15.0 C51911913 H15.0 on +2.9 port riser (mouth 17.90)")
    place("J%d" % (14 + i), "MP62_USB_C_24P_Vertical_PLACEHOLDER", XO, y, 0, "F", ["C4 GPU DP L4 (2-lane)", "C5 iGPU DDI-B", "C6 iGPU DDI-C"][i] + "; FG-ST-C-24P-VT-SMT-15.0 C51911913 H15.0 on +2.8 port riser (mouth 17.82)")
for i, (x, y) in enumerate([(43.12, 42.64), (43.12, 32.54), (63.76, 42.64), (63.76, 32.54)]):
    place("J%d" % (21 + i), "MP62_USB_A3_9P_Vertical_PLACEHOLDER", x, y, 0, "F", "USB-A A%d 10G; KH-3.0AF180WJ-15JB C2979045 L15.0 on +%.1f port riser (mouth %.2f)" % (i + 1, 2.5 if x < 53 else 2.4, 17.49 if x < 53 else 17.38))
place("J25", "MP62_RJ45_HanRun_HR913790A_Vertical_2G5", 63.67, 91.60, 0, "F", "ETH1 i226-V #1 2.5GbE. HR913790A (16.9) TOO TALL for D0 18: face must be <= 13.6 -> non-magnetic vertical RJ45 <= 13.0 + V24P05S magnetics (footprint TBD)")
place("J26", "MP62_RJ45_HanRun_HR913790A_Vertical_2G5", 43.15, 91.41, 0, "F", "ETH2 i226-V #2 2.5GbE. HR913790A (16.9) TOO TALL for D0 18: face must be <= 13.7 (behind the frame) -> non-magnetic vertical RJ45 <= 13.0 + V24P05S magnetics (footprint TBD)")
place("J27", "MP62_HDMI_A_Vertical_PLACEHOLDER", 42.96, 107.07, 0, "F", "HDMI (GPU link 2 via TDP158); vertical H15 (JLC C9900153431, verify shell <= 15.4 x 5.6) on +2.2 port riser (mouth 17.24)")
place("SW1", "SW_SPST_PTS810", 63.79, 108.11, 0, "F", "DNP with the stock 821-2222-A flex (its dome switch is the power button, via J31); fit only without the flex", dnp=True)
place("J30", "JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical", 56.5, 104.5, 0, "F", "Optional stock/remote power button 2P (parallel to SW1)")
place("J31", "Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal", 82.8, 10.0, 0, "F", "I/O-wall (821-2222) flex ZIF 14P 0.5: power button + port illumination (HX FPC 0.5-14P HYH2.0, C7502869; land pattern = FH12 placeholder, verify)")
place("D20", "LED_0603_1608Metric", 63.79, 103.38, 0, "F", "DNP with the stock flex (its 2 button LEDs light the cap via J31); power/sleep LED only without the flex", dnp=True)
place("J28", "MP62_StockAudio_EdgeCard_50P_P0.5_PLACEHOLDER", 50.9, 10.4, 0, "F", "Stock audio module connector (PLACEHOLDER)")
place("BT1", "BatteryHolder_Keystone_3034_1x20mm", g["coin"]["c"][0], g["coin"]["c"][1], 0, "F", "CR2032/BR2032 holder (stock spot) -> VBAT_RTC over HS1")
for i, (x, y) in enumerate(g["speaker"]["screws"]):
    place("H%d" % (11 + i), "MP62_SMT_Nut_M1.6_H1.5_SMTSO1615", x, y, 0, "F", "M1.6 x 1.5 SMT nut SMTSO1615MTJ (C2928168) - speaker")
place("J29", "JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical", g["speaker"]["jst"][0], g["speaker"]["jst"][1] + 1.0, 180, "F", "Speaker 2P (stock lead; pitch verify 1.0)")
place("H13", "MP62_Frame_Standoff_M2_SMT_PLACEHOLDER", 53.38, 58.38, 0, "F", "I/O-frame centre screw standoff (stock TB-bar point), height M-IOF2")
for i, (n, x, y) in enumerate([("HDMI label", 46.2, 115.6), ("ETH icon", 53.42, 92.9), ("USB-C icon upper", 53.25, 70.4),
                               ("USB-C icon lower", 53.25, 62.6), ("USB icon", 53.7, 49.4), ("audio icons", 53.8, 21.0)]):
    place("D%d" % (21 + i), "LED_0603_1608Metric", x, y, 90, "F", "Light-pipe LED: " + n + " - DNP with the stock flex (its own LEDs light the icon pads via J31)", dnp=True)
place("U30", "SOT-23", 72.0, 112.0, 0, "F", "Hall A (DRV5032 class) - position TBD M-IOH1")
place("U31", "SOT-23", 72.0, 104.0, 0, "F", "Hall B (DRV5032 class) - position TBD M-IOH1")
# mounting holes (stock, 6)
for k, h in g["holes"].items():
    place("H%s" % k, "MP62_IO_MountHole_D3.8_Pad7.5", h["x"], h["y"], 0, "F", "Stock mount hole %s" % k)

# ---------------- F side power stage (stock tall-parts region X 75-98, Y 100-150) ----------------
place("U40", "Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm", 91.0, 104.0, 0, "F", "TPS259824ON eFuse 12 V in (15 A, ILIM ~10 A)")
place("U41", "MP62_TI_RNN0018A_VQFN-HR-18_3.5x3.5mm_PLACEHOLDER", 91.0, 137.0, 0, "F", "TPS56C215 5V_C buck (USB-C VBUS, 12 A)")
place("L41", "L_Bourns_SRP1038C_10.0x10.0mm", 81.5, 140.5, 0, "F", "1.5uH 10x10 (5V_C)")
place("U42", "MP62_TI_RNN0018A_VQFN-HR-18_3.5x3.5mm_PLACEHOLDER", 91.0, 119.0, 0, "F", "TPS56C215 5V_A buck (USB-A VBUS + 5V_SYS, 12 A)")
place("L42", "L_Bourns_SRP1038C_10.0x10.0mm", 81.5, 120.0, 0, "F", "1.5uH 10x10 (5V_A)")
for k, (x, y) in enumerate([(78.0, 131.5), (81.0, 131.5), (84.0, 131.5), (87.0, 131.5), (78.0, 110.5), (81.0, 110.5), (84.0, 110.5), (87.0, 110.5)]):
    place("C%d" % (40 + k), "C_1206_3216Metric", x, y, 90, "F", "47uF 10V output bulk")
for k, (x, y) in enumerate([(91.0, 131.0), (91.0, 112.5), (94.0, 112.5), (94.0, 131.0)]):
    place("C%d" % (50 + k), "C_1206_3216Metric", x, y, 90, "F", "22uF 25V buck input")
place("U43", "SOT-563", 87.5, 99.0, 0, "F", "TLV62585 3V3 (3 A) from 5V_SYS")
place("L43", "L_1008_2520Metric", 91.5, 99.0, 0, "F", "0.47uH 2520")

# ---------------- B side: cables (MEG-Array end), PSU, management ----------------
place("J1", "MP62_MCIO_124P_RA_SFF-TA-1016", 36.5, 158.0, 0, "B", "IOB-HS1 MCIO 124 RA <- CB J3 (10 x USB3, i226 PCIe x1, 2 x DDI, USB2, VBAT)")
place("J2", "MP62_MCIO_74P_RA_SFF-TA-1016", 75.0, 150.6, 0, "B", "DISPLAY-LINK MCIO 74 RA <- Face P (GPU links 0-4)")
place("J3", "MP62_StockPSU_DC_12P_P1.5_Shrouded_PLACEHOLDER", g["stock_conn"]["PSU_DC_12P"][0], g["stock_conn"]["PSU_DC_12P"][1], 0, "B", "Stock PSU DC-out 12P (UNCONFIRMED pinout)")
place("J4", "MP62_StockPSU_SIG_6P_P1.25_Vertical_PLACEHOLDER", 8.75, g["stock_conn"]["PSU_SIG_6P"][1], 0, "B", "Stock PSU signal 6P (UNCONFIRMED pinout)")
place("J5", "Molex_Micro-Fit_3.0_43045-0812_2x04_P3.00mm_Vertical", 52.0, 18.0, 0, "B", "PSU pass-through -> BP J2 (12V, 11V_SB, PS_ON#, PWR_OK)")
place("J6", "JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", 80.0, 12.0, 0, "B", "IOB-LINK GH15 <- BP J6")
# USB-C path: PD controllers, alt-mode redriver muxes
place("U1", "MP62_TI_TPS65994AD_QFN-48_6x6_P0.4_PLACEHOLDER", 18.5, 70.0, 0, "B", "TPS65994AD PD #1 (C1, C2)")
place("U2", "MP62_TI_TPS65994AD_QFN-48_6x6_P0.4_PLACEHOLDER", 53.5, 66.5, 0, "B", "TPS65994AD PD #2 (C3, C4)")
place("U3", "MP62_TI_TPS65994AD_QFN-48_6x6_P0.4_PLACEHOLDER", 85.0, 66.0, 0, "B", "TPS65994AD PD #3 (C5, C6)")
for i, y in enumerate(CY):
    place("U%d" % (11 + i), "MP62_TI_TUSB1046A_WQFN-40_4x6_P0.5_PLACEHOLDER", 29.0, y, 90, "B", "TUSB1046A C%d alt-mode mux/redriver" % (1 + i))
    place("U%d" % (14 + i), "MP62_TI_TUSB1046A_WQFN-40_4x6_P0.5_PLACEHOLDER", 77.5, y, 90, "B", "TUSB1046A C%d alt-mode mux/redriver" % (4 + i))
place("U4", "SOIC-8_3.9x4.9mm_P1.27mm", 18.5, 79.0, 90, "B", "PD #1 config SPI flash (W25Q80 class, 8 Mbit)")
place("U6", "SOIC-8_3.9x4.9mm_P1.27mm", 53.5, 75.5, 90, "B", "PD #2 config SPI flash")
place("U7", "SOIC-8_3.9x4.9mm_P1.27mm", 85.0, 75.5, 90, "B", "PD #3 config SPI flash")
# USB-A path
for i, (x, y) in enumerate([(29.0, 42.75), (29.0, 32.6), (77.5, 42.75), (77.5, 32.6)]):
    place("U%d" % (21 + i), "MP62_TI_TUSB1002A_WQFN-24_4x4_P0.5_PLACEHOLDER", x, y, 0, "B", "TUSB1002A A%d 10G redriver" % (i + 1))
for i, (x, y) in enumerate([(24.0, 43.5), (19.0, 32.6), (86.0, 42.75), (86.0, 32.6)]):
    place("U%d" % (25 + i), "SOT-23-5", x, y, 90, "B", "USB-A A%d VBUS switch 1.5 A (SY6280/TPS2553 class)" % (i + 1))
# USB2 hubs
place("U34", "MP62_WCH_CH334R_QFN-24_4x4_P0.5_PLACEHOLDER", 53.5, 52.0, 0, "B", "CH334R hub H1a (C1-C3 + H1b) <- HS1 USB2")
place("U32", "MP62_WCH_CH334R_QFN-24_4x4_P0.5_PLACEHOLDER", 53.5, 84.5, 0, "B", "CH334R hub H1b (C4-C6 + codec)")
place("U33", "MP62_WCH_CH334R_QFN-24_4x4_P0.5_PLACEHOLDER", 19.0, 53.0, 0, "B", "CH334R hub H2 (A1-A4) <- IOB-LINK USB2")
for k, (x, y) in enumerate([(53.6, 46.6), (53.0, 95.5), (19.0, 47.4)]):   # Y2 moved above the RJ45 shield pins (HR913790A, 2026-10-02)
    place("Y%d" % (1 + k), "Crystal_SMD_3225-4Pin_3.2x2.5mm", x, y, 0, "B", "12 MHz hub crystal")
# Ethernet
place("U50", "MP62_Intel_i226V_QFN-56_7x7_P0.4_PLACEHOLDER", 78.0, 101.0, 0, "B", "i226-V 2.5GbE (PCIe x1 from HS1)")
place("Y4", "Crystal_SMD_3225-4Pin_3.2x2.5mm", 86.0, 104.5, 0, "B", "25 MHz (i226-V)")
place("U51", "SOIC-8_3.9x4.9mm_P1.27mm", 86.0, 97.0, 90, "B", "i226-V NVM SPI flash (size per Intel)")
# HDMI
place("U60", "MP62_TI_TDP158_WQFN-40_5x5_P0.4_PLACEHOLDER", 28.5, 108.0, 0, "B", "TDP158 HDMI 2.0 retimer (GPU link 2)")
place("U61", "SOT-23-5", 20.5, 108.0, 90, "B", "1V1 LDO (TDP158 core)")
# Audio
place("U70", "LQFP-48_7x7mm_P0.5mm", 38.0, 22.0, 0, "B", "C-Media CM108B USB audio codec (UAC1)")
place("Y5", "Crystal_SMD_3225-4Pin_3.2x2.5mm", 30.5, 22.0, 90, "B", "12 MHz (CM108B)")
place("U71", "MSOP-8_3x3mm_P0.65mm", 15.5, 103.0, 0, "B", "PAM8302A mono class-D 2.5 W (speaker)")
# management
place("U80", "TSSOP-28_4.4x9.7mm_P0.65mm", 68.5, 110.5, 90, "B", "TLC59116 16-ch I2C LED driver (diag x8, power, light pipes)")
place("U81", "LGA-12_2x2mm_P0.5mm", 79.0, 115.5, 0, "B", "LIS2DH12 accelerometer (rotate-to-light, optional)")
place("U82", "SOIC-8_3.9x4.9mm_P1.27mm", 85.5, 115.5, 90, "B", "BL24C64A IOB ID EEPROM @0x51")
place("U83", "MSOP-8_3x3mm_P0.65mm", 75.0, 121.0, 0, "B", "TCA9517 I2C buffer (I2C_SYS <-> PD bus)")
place("U84", "SOT-23-5", 81.0, 122.0, 0, "B", "74LVC1G07 PD_INT -> IOB_INT_N")
place("L44", "L_1008_2520Metric", 78.0, 108.5, 0, "B", "i226 SVR inductor")
# i226-V #2 (ETH2, D-IO2 resolved 2026-10-02): B side left of the J26 THT field
place("U52", "MP62_Intel_i226V_QFN-56_7x7_P0.4_PLACEHOLDER", 28.0, 92.0, 0, "B", "i226-V #2 2.5GbE (PCIe x1 from HS1 k14, PCH RP4)")
place("U53", "SOIC-8_3.9x4.9mm_P1.27mm", 19.5, 86.5, 0, "B", "i226-V #2 NVM SPI flash")
place("Y6", "Crystal_SMD_3225-4Pin_3.2x2.5mm", 28.0, 85.0, 0, "B", "25 MHz (i226-V #2)")
place("L45", "L_1008_2520Metric", 28.0, 98.5, 0, "B", "i226 #2 SVR inductor")
for k in range(8):
    place("D%d" % (1 + k), "LED_0603_1608Metric", 13.5 + 2.4 * k, 121.0, 90, "B", "Diag LED %d (stock #1-#8 set)" % (1 + k))
place("SW2", "SW_SPST_TL3342", 16.5, 114.5, 0, "B", "DIAG button")
place("D30", "D_SOD-323", 14.0, 131.0, 90, "B", "BAT54WS VBAT no-charge diode")
place("R30", "R_0402_1005Metric", 14.0, 134.5, 90, "B", "1k VBAT series")

# ---------------- rule areas / documentation ----------------
KEEP = []
def poly(pts):
    s = pcbnew.SHAPE_POLY_SET(); s.NewOutline()
    for x, y in pts:
        v = P(x, y); s.Append(v.x, v.y)
    return s
def circ_poly(x, y, r, n=40): return poly([(x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n)) for i in range(n)])
def rule_area(name, layers, ps, fp_=True, pads=True, vias=False, tracks=False, pour=False):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetZoneName(name)
    z.SetDoNotAllowFootprints(fp_); z.SetDoNotAllowPads(pads); z.SetDoNotAllowVias(vias); z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowCopperPour(pour)
    ls = pcbnew.LSET()
    for l in layers: ls.AddLayer(l)
    z.SetLayerSet(ls); KEEP.append(ps); z.SetOutline(ps); board.Add(z); KEEP.append(z)
for i, r in enumerate(g["rails_B"]):
    rule_area("KO_FOAM_RAIL_B_%d" % i, [pcbnew.B_Cu], poly([(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]))
# speaker keep-out (F): stadium minus the two nut pads
sx0, sx1 = g["speaker"]["oval_x"]; sy0, sy1 = g["speaker"]["oval_y"]; rr = (sx1 - sx0) / 2; cx = (sx0 + sx1) / 2
pts = [(cx + rr * math.cos(math.radians(a)), sy1 - rr + rr * math.sin(math.radians(a))) for a in range(0, 181, 10)] + \
      [(cx + rr * math.cos(math.radians(a)), sy0 + rr + rr * math.sin(math.radians(a))) for a in range(180, 361, 10)]
spk = poly(pts)
for (x, y) in g["speaker"]["screws"]: spk.BooleanSubtract(circ_poly(x, y, 2.6))
rule_area("KO_SPEAKER_F_no_parts", [pcbnew.F_Cu], spk)
# AC inlet margin (B side 3 mm around the cutout, F side 1 mm) -- inlet body passes through from the PSU
wv = g["window"]
for lay, m in ((pcbnew.B_Cu, 3.0), (pcbnew.F_Cu, 1.0)):
    rule_area("KO_AC_INLET_%s" % ("B" if lay == pcbnew.B_Cu else "F"), [lay],
              poly([(wv["xL"] - m, wv["yB"] - m), (wv["xR"] + m, wv["yB"] - m), (wv["xR"] + m, wv["yT"] + m), (wv["xL"] - m, wv["yT"] + m)]), fp_=True, pads=False)

# documentation drawings
U1L, U2L, U3L, U4L = pcbnew.User_1, pcbnew.User_2, pcbnew.User_3, pcbnew.User_4
for o in g["openings_outer"]:
    (x, y), w, h = o["centre"], o["w"], o["h"]
    if o["id"] == "POWER_BUTTON": circle(x, y, w / 2, U1L, 0.08)
    elif o["id"].startswith("AUDIO"): circle(x, y, w / 2, U1L, 0.08)
    else: rectd(x - w / 2, y - h / 2, x + w / 2, y + h / 2, U1L, 0.08)
pl = g["plate"]; x0, x1 = pl["x_straight"]; rectd(x0, -4.47, x1, 158.62, U1L, 0.12)
txt("User.1: stock I/O plate outline + outer openings (scan, +-0.3..1)", 53, 160.5, U1L, 0.8)
fo = g["frame_outline"]; rectd(fo["x_range"][0], fo["y_range"][0], fo["x_range"][1], fo["y_range"][1], U2L, 0.1)
for k, f in g["frame_features"].items():
    if "cx" in f and "w" in f: rectd(f["cx"] - f["w"] / 2, f["cy"] - f["h"] / 2, f["cx"] + f["w"] / 2, f["cy"] + f["h"] / 2, U2L, 0.06)
txt("User.2: I/O carrier frame openings (metal, stays). Every port body must pass these", 53, 162.5, U2L, 0.8)
for r in g["rails_B"]: rectd(*r, U3L, 0.1)
txt("User.3: B-side PSU-frame foam rails (no B parts)", 50, 23, U3L, 0.8)
for (x, y) in g["speaker"]["screws"]: circle(x, y, 1.25, U4L, 0.08)
rectd(sx0, sy0, sx1, sy1, U4L, 0.1); txt("User.4: stock speaker (oval) + M1.6 screws, pitch 54.9", 20, 67, U4L, 0.8, 90)
circle(g["coin"]["c"][0], g["coin"]["c"][1], g["coin"]["d"] / 2, U4L, 0.1)
for (x, y) in g["stock_conn"]["CONN_C_standoffs"]: circle(x, y, 2.0, pcbnew.Dwgs_User, 0.08)
txt("Dwgs.User: stock CONN_C standoffs (back side) - function unknown, not reproduced", 50, -3, pcbnew.Dwgs_User, 0.7)
notes = ["MP62 I/O board IOB rev A0 FLOORPLAN (not routed). Viewed from the FRONT (port side). F = front, B = back (PSU side).",
         "Port grid (stock flex cut-outs, scan 2026-10-02): USB-C Xb 43.09 / 63.69, Y 75.76 / 65.84 / 55.97; USB-A 43.12 / 63.76, Y 42.64 / 32.54; RJ45 (43.15,91.41)/(63.67,91.60); HDMI (42.96,107.07); button (63.79,108.11).",
         "D0 = 18.0 crown / 16.5 edge: USB-C/USB-A/HDMI need 17.2-17.9 board-to-mouth -> port risers (+2.2..2.9) under 15.0 parts; RJ45 face <= 13.6 (plan 4.7.4).",
         "All ports are VERTICAL (mating axis normal to the board); the plate is curved with no lands (stock flex must lie flat), mouths flush at the outboard edge (plan 4.4/4.7).",
         "B top: J1 IOB-HS1 MCIO124 (CB J3), J2 display link MCIO74 (Face P). B bottom: stock PSU DC 12P + signal 6P (pinouts UNCONFIRMED), J5 Micro-Fit -> BP J2, J6 IOB-LINK.",
         "PLACEHOLDER land patterns: all vertical port connectors, stock audio/PSU connectors, TPS65994AD, TUSB1046A, TUSB1002A, TDP158, i226-V, CH334R."]
for i, s in enumerate(notes): txt(s, 50, -8 - 2.0 * i, pcbnew.Cmts_User, 0.9)
txt("MP62 IOB A0", 86, 90, pcbnew.F_SilkS, 1.5, 90)
pcbnew.SaveBoard(OUT, board)
bb = {}
for f in board.GetFootprints():
    r = f.GetCourtyard(pcbnew.F_CrtYd if not f.IsFlipped() else pcbnew.B_CrtYd).BBox() if f.GetCourtyard(pcbnew.F_CrtYd if not f.IsFlipped() else pcbnew.B_CrtYd).OutlineCount() else f.GetBoundingBox(False)
    x0 = W - (pcbnew.ToMM(r.GetRight()) - OX); x1 = W - (pcbnew.ToMM(r.GetLeft()) - OX); y0 = OY - pcbnew.ToMM(r.GetBottom()); y1 = OY - pcbnew.ToMM(r.GetTop())
    bb[f.GetReference()] = dict(side="B" if f.IsFlipped() else "F", xb=[round(x0, 2), round(x1, 2)], y=[round(y0, 2), round(y1, 2)], value=f.GetValue(), fp=f.GetFPIDAsString(), dnp=f.IsDNP())
json.dump(bb, open(os.path.join(HERE, "placement.json"), "w"), indent=0)
print("saved", OUT, len(FP), "footprints")
