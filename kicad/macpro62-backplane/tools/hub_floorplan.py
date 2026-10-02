# HUB floorplan fp5 (2026-10-02: face normals 45/135 deg per Aidan, M2c; was fp4 30/150) (exec'd from build_pcb.py; uses place/seg/txt/circle/P from there). Disc coordinates (+y = core/GPU side).
# Inputs: M1 (GPU board bottom edges ~15 mm above BP), M2 (GPU board planes ~55 mm from disc centre) measured by Aidan 2026-10-01.
# CPU board plane ESTIMATED at y = -12.6 (stock logic-board riser slot, service-guide photo) - TBD measurement M2b.
import math as _m
MCRA = "MP62_MCIO_124P_RA_SFF-TA-1016"   # ICD 2026-10-02: SFF-TA-1016 Annex A RA footprint, same as the face template (face spec C-2 / CR-2)
# fp5 (ICD rev 2, 2026-10-02): face normals at 45 / 135 deg (Aidan: ~45 deg from the I/O-card bottom gaps; stock GPU
# connector fields at +/-46.6 deg agree). The two face boards now meet at 90 deg, so J9 and J10 form a 90 deg V.
# Joint scan (scratch/icd2/joint.py): rim 58, G-hole 6, S-hole 3, J1 clearance, J9/J10 gap >= 1.5. Face J_PCIE stays at
# module X 43.5 (s = +8.5, CR-2); CR-2 is CLOSED by the jog cable (Aidan: flat twinax MCIO, ICD I-4). With the faces at
# 90 deg the two RA receptacles cannot both sit near s = +8.5 (they collide at the apex), and J4 (Face S AUX) only fits beyond
# J10's lower-left end if J10 s <= -2 (G1 6 mm keep-out). Chosen: J10 s = -2.0 (r_c 31.5), J9 s = -5.2 (r_c 31.2), J9/J10 gap
# 1.3 mm at the apex. Cable jogs: Face P 13.7 mm, Face S 10.5 mm (flat twinax, <= 15 mm allowed, ICD I-4).
FACE_P_ANG, FACE_S_ANG = 45.0, 135.0
MCIO_S_P, MCIO_RC_P = -5.2, 31.2
MCIO_S_S, MCIO_RC_S = -2.0, 31.5
GH = "Connector_JST"
Y_CPU = -12.6
place("J1", "MP62_Placeholders", "MP62_CPULINK_MiniCoolEdge_224P_Vertical_SMT_PLACEHOLDER", 0.0, Y_CPU, 180,
      "CPU-LINK: Amphenol Mini Cool Edge 224P vertical (ME1022410103011) at stock riser-slot position (ESTIMATE y=-12.6)")
# right-angle MCIO, mating face toward the rim (radial, under the face board bottom edge); courtyard outer edge at r = 50
def face_pos(ang_deg, r_c, s):
    a = _m.radians(ang_deg); n = (_m.cos(a), _m.sin(a)); t = (-n[1], n[0])
    return (r_c * n[0] + s * t[0], r_c * n[1] + s * t[1])
xP, yP = face_pos(FACE_P_ANG, MCIO_RC_P, MCIO_S_P)
xS, yS = face_pos(FACE_S_ANG, MCIO_RC_S, MCIO_S_S)
place("J9", "MP62_Placeholders", MCRA, xP, yP, FACE_P_ANG - 90.0,
      "MCIO 124 RA OUT -> Face P (x16, REFCLK, PERST#, sideband); cable exits radially under the Face P board edge")
place("J10", "MP62_Placeholders", MCRA, xS, yS, FACE_S_ANG - 90.0,
      "MCIO 124 RA OUT -> Face S (x4 wired, REFCLK, PERST#, sideband); cable exits radially under the Face S board edge")
# ICD 2026-10-02 (face spec C-4): AUX = GH 15P (pin 15 MOD_LED#, pins 13/14 USB2 primary). Moved clear of the S4/S5 keep-outs (CR-BP-1).
# fp5: J3 (Face P) in the apex wedge beyond the J9/J10 short sides: Face P's J_AUX (module X 16.5, s = +35.5) is at its
# apex end; J3 sits at Face-P s = +36.3. J4 (Face S) beyond J10's lower-left short side, long axis along the Face S normal,
# at Face-S s = +25.1 (Face S's J_AUX end, s = +35.5, points to the lower left by rotational symmetry); 6.2 mm from G1.
J4_NS = (28.6, 25.1)   # (n, s) in the Face S frame
_a4 = _m.radians(FACE_S_ANG); J4_P = (J4_NS[0] * _m.cos(_a4) - J4_NS[1] * _m.sin(_a4), J4_NS[0] * _m.sin(_a4) + J4_NS[1] * _m.cos(_a4))
place("J3", GH, "JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", 0.0, 51.4, 0.0,
      "FACE-P AUX: JST GH 15P (MP62-FACE v0.1 J_AUX: PWR_EN, PWR_GOOD, SMBus, THERM, PRSNT, 3V3_AUX, USB2, MOD_LED#)")
place("J4", GH, "JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", J4_P[0], J4_P[1], FACE_S_ANG,
      "FACE-S AUX: JST GH 15P (same pinout as J3)")
# redrivers (optional Gen5) in the V between J1 and the two MCIO inner edges (fp5: x + y < 27.4, y - x < 27.4)
RDRV = ((-6.45, -3.5), (6.45, -3.5), (6.45, 6.0), (19.35, -3.5))
for i, (x, y) in enumerate(RDRV):
    place("U%d" % (10 + i), "MP62_Placeholders", "MP62_AREA_Redriver_DS320PR810_12x8_PLACEHOLDER", x, y, 0,
          "OPTION Gen5: DS320PR810 #%d, Face P lanes %d-%d (TX+RX)" % (i + 1, 4 * i, 4 * i + 3))
place("U14", "MP62_Placeholders", "MP62_AREA_Redriver_DS320PR810_12x8_PLACEHOLDER", -19.35, -3.5, 0,
      "OPTION Gen5: DS320PR810 #5, Face S lanes 0-3 (TX+RX)")
# MCU cluster at the top of the V (under the core bottom); flash + crystal in the second redriver row
fU1 = place("U1", "Package_DFN_QFN", "QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm", 0.0, 15.3, 0, "RP2350A (LCSC C42411118)")
place("U2", "Package_SON", "WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4.3mm", -9.0, 6.0, 0, "W25Q128 QSPI flash (part TBD)")
place("Y1", "Crystal", "Crystal_SMD_3225-4Pin_3.2x2.5mm", -2.6, 6.0, 0, "12 MHz crystal")
place("U3", "Package_SO", "VSSOP-8_3x3mm_P0.65mm", 0.0, 41.6, 0, "TMP1075 core-base temp sensor #1 (under core bottom, I2C_SYS 0x48)")
place("SW1", "Button_Switch_SMD", "SW_Push_1P1T_XKB_TS-1187A", 30.5, -34.0, 0, "BOOTSEL (fp5: PSU side)")
place("J8", "Connector_JST", "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical", -40.0, -34.0, 0, "SWD (3V3, SWCLK, SWDIO, GND) (fp5: PSU side)")
# PSU side (behind the CPU board, under the PSU)
fJ7 = place("J7", "MP62_Placeholders", "MP62_M2_2242_MKey_SATA_PLACEHOLDER", 0.0, -30.0, 0,
      "OpenCore boot: M.2 M-key socket, SATA0, 2242 card (PSU side; height under PSU TBD M7)")
place("PS1", "MP62_Placeholders", "MP62_AREA_StandbyPower_22x12_PLACEHOLDER", -37.3, -24.5, 0, "Standby power + HW safety gate")
place("PS2", "MP62_Placeholders", "MP62_AREA_MainPower_20x12_PLACEHOLDER", 38.0, -24.5, 0, "Main-rail power (3V3_BP incl. redrivers ~6.5 W)")
place("J2", "Connector_Molex", "Molex_Micro-Fit_3.0_43045-0812_2x04_P3.00mm_Vertical", -13.0, -48.0, 0,
      "PSU-IN: Micro-Fit 3.0 2x4 (12V x2, GND x3, 11V_SB, PS_ON#, PWR_OK)")
IOBL_P = (11.4, -48.8)   # was (13.0, -48.8): S3 keep-out (CR-BP-1)
place("J6", GH, "JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", IOBL_P[0], IOBL_P[1], 180.0,
      "IOB-LINK: GH 15P <-> IOB J6 (3V3_SB x2, PWRBTN_IN_N, HALL_A/B_N, I2C_SYS, IOB_INT_N, IOB_PRSNT_N, USB2_LINK, GND)")
# J5 (fan GH4) REMOVED 2026-10-02: the fan is driven from the IOB CONN_C (EMC2101 @0x4C on I2C_SYS), spec change 27 / ICD.
place("SW2", "Button_Switch_SMD", "SW_Push_1P1T_XKB_TS-1187A", 30.0, -40.0, 0, "Bench power button")
U4_P = (-30.0, -38.0)   # CR-BP-1: moved off S2 (was (-27, -46.5), S2 inside its courtyard)
place("U4", "Package_SO", "VSSOP-8_3x3mm_P0.65mm", U4_P[0], U4_P[1], 0, "TMP1075 PSU-side temp sensor #2 (I2C_SYS 0x49)")
for i, (y, lbl) in enumerate(((-33.0, "11V_SB"), (-36.0, "12V main"), (-39.0, "S0"), (-42.0, "FAULT"))):
    place("D%d" % (i + 1), "LED_SMD", "LED_0603_1608Metric", 37.5, y, 0, "LED " + lbl)

fU1.Reference().SetPosition(P(-6.8, 15.3))
fJ7.Reference().SetPosition(P(0.0, -30.0))
for _r, _f, _v in placed:
    if _r in ("U10", "U11", "U12", "U13", "U14"):
        _p = _f.GetPosition(); _f.Reference().SetPosition(_p)
    if _r == "J1":
        _f.Reference().SetPosition(P(47.5, Y_CPU))
    if _r in ("J8", "U3"):
        _p = _f.GetPosition(); _f.Reference().SetPosition(VECTOR2I(_p.x - FromMM(6.0), _p.y))
    if _r == "J4":
        _f.Reference().SetPosition(P(J4_P[0] + 6.5, J4_P[1] + 6.5))
    if _r in ("SW1", "SW2"):   # fp5: SW1 moved next to SW2 -> refs inside the bodies
        _f.Reference().SetPosition(_f.GetPosition()); _f.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))

def poly(pts, layer=pcbnew.Dwgs_User, w=0.25):
    for (a, b) in zip(pts[:-1], pts[1:]):
        seg(a[0], a[1], b[0], b[1], layer, w)
# ---- drawings ----
txt("CPU carrier 224 card (79.89 x 1.57) enters J1 here (J1 at 180 deg: A row = host TX on the PSU side, A1 at +x); parts within ~6 mm: height <= shoulder gap (M3)", 0, Y_CPU - 5.2, pcbnew.Dwgs_User, 0.7)
txt("PSU SIDE (behind CPU board, under PSU): heights TBD (M7)", 0, -58.5 + 3.0, pcbnew.Dwgs_User, 0.8)
# GPU/face board footprints in plan (board plane at 55; full width 104, bottom flat 70 between 17x13 chamfers), estimated core bottom
for ang in (FACE_P_ANG, FACE_S_ANG):
    a = _m.radians(ang); n = (_m.cos(a), _m.sin(a)); t = (-n[1], n[0])
    c = (55.0 * n[0], 55.0 * n[1])
    for hw, w in ((52.0, 0.15), (35.0, 0.5)):
        seg(c[0] - hw * t[0], c[1] - hw * t[1], c[0] + hw * t[0], c[1] + hw * t[1], pcbnew.Dwgs_User, w)
    # radial cable exit arrow from the MCIO mating face to beyond the board plane
    r0, r1 = 50.5, 62.0
    s0 = MCIO_S_P if ang == FACE_P_ANG else MCIO_S_S
    # face J_PCIE landing (module X 43.5 -> s = +8.5 on both faces, face spec C-2): tick on the board-plane chord
    sj = 8.5
    seg(55.0 * n[0] + sj * t[0] - 2.0 * n[0], 55.0 * n[1] + sj * t[1] - 2.0 * n[1], 55.0 * n[0] + sj * t[0] + 2.0 * n[0], 55.0 * n[1] + sj * t[1] + 2.0 * n[1], pcbnew.Dwgs_User, 0.4)
    txt("J_PCIE (module X 43.5, s=+8.5); BP receptacle s=%+.1f -> cable jog %.1f mm" % (s0, abs(sj - s0)), 52.5 * n[0] + sj * t[0], 52.5 * n[1] + sj * t[1], pcbnew.Dwgs_User, 0.5, _m.degrees(_m.atan2(t[1], t[0])) - (180 if ang == FACE_P_ANG else 0))
    for ds in (-16.0, 16.0):
        p0 = (r0 * n[0] + (s0 + ds) * t[0], r0 * n[1] + (s0 + ds) * t[1]); p1 = (r1 * n[0] + (s0 + ds) * t[0], r1 * n[1] + (s0 + ds) * t[1])
        seg(p0[0], p0[1], p1[0], p1[1], pcbnew.Dwgs_User, 0.2)
    lx, ly = 58.5 * n[0] + s0 * t[0], 58.5 * n[1] + s0 * t[1]
    rot = _m.degrees(_m.atan2(t[1], t[0]))
    if rot > 90: rot -= 180
    if rot < -90: rot += 180
    txt("MCIO exit: plug 8.2 high under the 15 mm board edge; flat twinax bends up outside (R >= 3 per layer), jog %.1f mm" % abs(8.5 - s0), lx, ly, pcbnew.Dwgs_User, 0.6, rot)
# core interior: bounded by the three board planes (GPU 55 / 55 measured at 45 / 135 deg, CPU 12.6 measured). Plane triangle
# (fp5): apex (0, 77.8) 90 deg, base corners (+/-90.4, -12.6); incentre y_c from 55 - 0.707*y_c = y_c + 12.6 -> y_c = 24.8,
# inradius 37.4 (corners truncated by the R~80 case). GPU board ends (s = +/-52) at (+/-2.1, 75.7) and (+/-75.7, 2.1).
txt("open core interior / air path above the region bounded by the 3 board planes (45/135 deg: incentre (0, 24.8), inradius ~37; disc centre 12.6 mm inside the CPU board)", 0, 57.0, pcbnew.Dwgs_User, 0.45)
# PCIe corridors
poly([(2, -11), (2, -8), (4, 1), (8, 12), (12, 18)], pcbnew.Dwgs_User, 0.2)
poly([(38, -11), (30, -8), (27, -1), (24, 4)], pcbnew.Dwgs_User, 0.2)
txt("Face P x16 corridor (TX L1 / RX L6)", 21, 8.0, pcbnew.Dwgs_User, 0.7, -45)
poly([(-4, -11), (-10, -8), (-15, -2), (-20, 3)], pcbnew.Dwgs_User, 0.2)
poly([(-20, -11), (-26, -8), (-28, -3)], pcbnew.Dwgs_User, 0.2)
txt("Face S x4 corridor", -19, 6.0, pcbnew.Dwgs_User, 0.7, 45)

# ---- lane length estimate from real pad positions (octilinear distance x 1.15 breakout/meander) ----
def octi(a, b):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(dx, dy) + (_m.sqrt(2) - 1) * min(dx, dy)
def pads_of(ref, prefix):
    f = [ff for r, ff, v in placed if r == ref][0]
    out = []
    for pd in f.Pads():
        if pd.GetNumber().startswith(prefix):
            p = pd.GetPosition(); out.append((pcbnew.ToMM(p.x) - CX, CY - pcbnew.ToMM(p.y)))
    return out
def span(pts, ang):
    a = _m.radians(ang); t = (_m.cos(a), _m.sin(a))
    return sorted(pts, key=lambda p: p[0] * t[0] + p[1] * t[1])
j9 = span(pads_of("J9", "A"), FACE_P_ANG + 90.0)    # along Face P tangent
j10 = span(pads_of("J10", "A"), FACE_S_ANG - 90.0)
lane_rep = []
for k in range(16):
    xj = 2.5 + k * (36.0 / 15)
    via = RDRV[k // 4]
    pe = j9[int(round(4 + k * (len(j9) - 9) / 15.0))]
    L = (octi((xj, Y_CPU + 1.4), via) + octi(via, pe)) * 1.15
    lane_rep.append(("P", k, L))
for k in range(4):
    xj = -4.0 - k * 4.0
    via = (-19.35, -3.5)
    pe = j10[int(round(len(j10) * 0.35 + k * 5))]
    L = (octi((xj, Y_CPU + 1.4), via) + octi(via, pe)) * 1.15
    lane_rep.append(("S", k, L))
LP = [l for f, k, l in lane_rep if f == "P"]; LS = [l for f, k, l in lane_rep if f == "S"]
open(os.path.join(PRJ, "lane_length_estimate.txt"), "w").write(
    "BP lane length estimate fp5, faces 45/135 deg (J1 at y=-12.6 -> redriver area -> RA MCIO pad), octilinear x 1.15, mm\n" +
    "\n".join("Face %s lane %2d: %5.1f mm" % r for r in lane_rep) +
    "\nFace P: min %.1f / max %.1f / mean %.1f mm;  Face S: min %.1f / max %.1f mm\n" % (min(LP), max(LP), sum(LP)/len(LP), min(LS), max(LS)))
