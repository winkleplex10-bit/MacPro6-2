# HUB floorplan (exec'd from build_pcb.py; uses place/seg/txt/circle/P from there). Disc coordinates.
MC = "MP62_MCIO_124P_Vertical_SMT_TE2360189_PLACEHOLDER"
GH = "Connector_JST"
place("J1", "MP62_Placeholders", "MP62_CPULINK_MiniCoolEdge_224P_Vertical_SMT_PLACEHOLDER", 0.0, -30.0, 0,
      "CPU-LINK: Amphenol Mini Cool Edge 224P vertical (ME1022410103011) - CPU board card edge, MP62 hub pinout")
place("J9", "MP62_Placeholders", MC, 25.2, 28.4, -60.0, "MCIO 124 OUT -> Face P (x16, REFCLK, PERST#, sideband)")
place("J10", "MP62_Placeholders", MC, -25.2, 28.4, 60.0, "MCIO 124 OUT -> Face S (x4 wired, REFCLK, PERST#, sideband)")
place("J3", GH, "JST_GH_BM14B-GHS-TBT_1x14-1MP_P1.25mm_Vertical", 35.6, 35.0, -60.0,
      "FACE-P AUX: JST GH 14P (PWR_EN, PWR_GOOD, SMBus, THERM, PRSNT, 3V3_AUX, USB2 fallback)")
place("J4", GH, "JST_GH_BM14B-GHS-TBT_1x14-1MP_P1.25mm_Vertical", -35.6, 35.0, 60.0,
      "FACE-S AUX: JST GH 14P (same pinout as J3)")
fJ7 = place("J7", "MP62_Placeholders", "MP62_M2_2242_MKey_SATA_PLACEHOLDER", 0.0, 6.0, 90.0,
      "OpenCore boot: M.2 M-key socket, SATA0, 2242 card (card toward +y; PCIe may route under the card on L1/L6)")
fU1 = place("U1", "Package_DFN_QFN", "QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm", 0.0, 37.0, 0, "RP2350A (LCSC C42411118)")
place("U2", "Package_SON", "WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4.3mm", 0.0, 45.5, 0, "W25Q128 QSPI flash (part TBD)")
place("Y1", "Crystal", "Crystal_SMD_3225-4Pin_3.2x2.5mm", -9.5, 36.5, 0, "12 MHz crystal")
place("U3", "Package_SO", "VSSOP-8_3x3mm_P0.65mm", 0.0, 52.0, 0, "TMP1075 core-base temp sensor #1")
place("U4", "Package_SO", "VSSOP-8_3x3mm_P0.65mm", -30.0, -14.0, 0, "TMP1075 core-base temp sensor #2")
place("PS1", "MP62_Placeholders", "MP62_AREA_StandbyPower_22x12_PLACEHOLDER", -20.0, -42.0, 0, "Standby power + HW safety gate")
place("PS2", "MP62_Placeholders", "MP62_AREA_MainPower_20x12_PLACEHOLDER", 20.0, -42.0, 0, "Main-rail power (3V3_BP incl. redrivers ~6.5 W)")
place("J2", "Connector_Molex", "Molex_Micro-Fit_3.0_43045-0812_2x04_P3.00mm_Vertical", 0.0, -43.5, 0,
      "PSU-IN: Micro-Fit 3.0 2x4 (12V x2, GND x3, 11V_SB, PS_ON#, PWR_OK)")
place("J6", GH, "JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", 0.0, -52.5, 180.0,
      "IOB-LINK: GH 15P (PWRBTN, HALL x2, LED I2C, USB2, 3V3_SB, GND)")
for i, (x, y) in enumerate(((19.0, -15.0), (32.0, -15.0), (19.0, -4.0), (32.0, -4.0))):
    place("U%d" % (10 + i), "MP62_Placeholders", "MP62_AREA_Redriver_DS320PR810_12x8_PLACEHOLDER", x, y, 0,
          "OPTION Gen5: DS320PR810 #%d, Face P lanes %d-%d (TX+RX)" % (i + 1, 4 * i, 4 * i + 3))
fU14 = place("U14", "MP62_Placeholders", "MP62_AREA_Redriver_DS320PR810_12x8_PLACEHOLDER", -19.0, -15.0, 0,
      "OPTION Gen5: DS320PR810 #5, Face S lanes 0-3 (TX+RX)")
place("J5", GH, "JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical", 46.0, -11.0, 90.0,
      "FAN: GH 4P (12V, GND, PWM, FG) - harness to top interposer, stock pinout TBD")
place("SW2", "Button_Switch_SMD", "SW_Push_1P1T_XKB_TS-1187A", 42.5, -22.0, 0, "Bench power button")
place("J8", "Connector_JST", "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical", -38.0, -6.0, 0, "SWD (3V3, SWCLK, SWDIO, GND)")
place("SW1", "Button_Switch_SMD", "SW_Push_1P1T_XKB_TS-1187A", -38.5, -17.0, 0, "BOOTSEL")
for i, (y, lbl) in enumerate(((-22.0, "11V_SB"), (-19.0, "12V main"), (-16.0, "S0"), (-13.0, "FAULT"))):
    place("D%d" % (i + 1), "LED_SMD", "LED_0603_1608Metric", -46.0, y, 90, "LED " + lbl)

fU1.Reference().SetPosition(P(-5.5, 41.5))
fJ7.Reference().SetPosition(P(0.0, -12.0))
# ---- drawings: CPU board line, PCIe corridors ----
seg(-52.0, -30.0, 52.0, -30.0, pcbnew.Dwgs_User, 0.3)
txt("CPU board (1.57 mm card edge, shoulder 105 mm) enters J1 here; parts within ~6 mm of this line: height <= shoulder gap (M3)", 0, -24.6, pcbnew.Dwgs_User, 0.8)
def poly(pts, layer=pcbnew.Dwgs_User, w=0.25):
    for (a, b) in zip(pts[:-1], pts[1:]):
        seg(a[0], a[1], b[0], b[1], layer, w)
poly([(2, -26), (12, -21), (38, -21), (38, 2), (36, 9), (14, 47)], pcbnew.Dwgs_User, 0.2)
poly([(2, -26), (8, -19), (13, 2), (8, 44)], pcbnew.Dwgs_User, 0.2)
txt("Face P x16 corridor (TX L1 / RX L6)", 26, 4.5, pcbnew.Dwgs_User, 0.9, 0)
poly([(-21, -26), (-26, -20), (-26, 8), (-36, 9)], pcbnew.Dwgs_User, 0.2)
poly([(-2, -26), (-12, -20), (-12, 14), (-16, 43)], pcbnew.Dwgs_User, 0.2)
txt("Face S x4 corridor", -19, 0.0, pcbnew.Dwgs_User, 0.9, 90)
txt("Optional cutout zone (not cut): core-channel air/cable relief - only if M1 shows airflow from below", 0, 52.0 - 4.0, pcbnew.Dwgs_User, 0.6)

# ---- lane length estimate (octilinear distance x 1.15 breakout/meander) ----
import math as _m
def octi(a, b):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(dx, dy) + (_m.sqrt(2) - 1) * min(dx, dy)
def mcio_pin(cx, cy, rot, s):
    a = _m.radians(rot); return (cx + s * _m.cos(a), cy + s * _m.sin(a))
lane_rep = []
# Face P: 16 lanes on J1 bays 3-4 (x ~ +2 .. +38.5), order-preserving onto J9 pin span (s = +20 .. -20 along its axis)
for k in range(16):
    xj = 2.5 + k * (36.0 / 15)
    via = (19.0 + 13.0 * ((k // 4) % 2), -15.0 + 11.0 * (k // 8))     # redriver row the lane passes
    pe = mcio_pin(25.2, 28.4, -60.0, 19.0 - k * (38.0 / 15))
    L = (octi((xj, -28.6), via) + octi(via, pe)) * 1.15
    lane_rep.append(("P", k, L))
for k in range(4):
    xj = -4.0 - k * 4.0
    via = (-19.0, -15.0)
    pe = mcio_pin(-25.2, 28.4, 60.0, -8.0 + k * 5.0)
    L = (octi((xj, -28.6), via) + octi(via, pe)) * 1.15
    lane_rep.append(("S", k, L))
LP = [l for f, k, l in lane_rep if f == "P"]; LS = [l for f, k, l in lane_rep if f == "S"]
open(os.path.join(PRJ, "lane_length_estimate.txt"), "w").write(
    "BP lane length estimate (J1 pad -> redriver area -> MCIO pad), octilinear x 1.15, mm\n" +
    "\n".join("Face %s lane %2d: %5.1f mm" % r for r in lane_rep) +
    "\nFace P: min %.1f / max %.1f / mean %.1f mm;  Face S: min %.1f / max %.1f mm\n" % (min(LP), max(LP), sum(LP)/len(LP), min(LS), max(LS)))
