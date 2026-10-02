#!/usr/bin/env python3
"""Write MP62_IO.pretty: I/O-board footprints. PLACEHOLDER = generic pattern with the right body/mouth size; replace with the vendor land
pattern before routing (marked in descr and on F.Fab). Stock KiCad 9 parts are copied in unchanged."""
import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.abspath(os.path.join(HERE, "..", "MP62_IO.pretty")); SYS = "/usr/share/kicad/footprints"
STOR = "/workspace/kicad/macpro62-storage-face"
os.makedirs(LIB, exist_ok=True)
def head(name, descr, tags, attr="smd"):
    return [f'(footprint "{name}"', '  (version 20241229)', '  (generator "mp62_io")', '  (layer "F.Cu")', f'  (descr "{descr}")', f'  (tags "{tags}")',
            '  (property "Reference" "REF**" (at 0 -1 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
            f'  (property "Value" "{name}" (at 0 1 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))', f'  (attr {attr})']
def rect(x1, y1, x2, y2, layer, w=0.1, dash=False):
    return f'  (fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type {"dash" if dash else "solid"})) (fill no) (layer "{layer}"))'
def circ(x, y, r, layer, w=0.05):
    return f'  (fp_circle (center {x:.3f} {y:.3f}) (end {x + r:.3f} {y:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))'
def text(s, x, y, layer="F.Fab", size=0.5):
    return f'  (fp_text user "{s}" (at {x:.3f} {y:.3f} 0) (layer "{layer}") (effects (font (size {size} {size}) (thickness {size * 0.15:.3f}))))'
def smd(n, x, y, w, h, shape="rect"):
    return f'  (pad "{n}" smd {shape} (at {x:.3f} {y:.3f}) (size {w:.3f} {h:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"))'
def tht(n, x, y, d, drill, shape="circle"):
    return f'  (pad "{n}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size {d:.3f} {d:.3f}) (drill {drill:.3f}) (layers "*.Cu" "*.Mask"))'
def oval(n, x, y, w, h, dw, dh):
    return f'  (pad "{n}" thru_hole oval (at {x:.3f} {y:.3f}) (size {w:.3f} {h:.3f}) (drill oval {dw:.3f} {dh:.3f}) (layers "*.Cu" "*.Mask"))'
def npth(x, y, d):
    return f'  (pad "" np_thru_hole circle (at {x:.3f} {y:.3f}) (size {d:.3f} {d:.3f}) (drill {d:.3f}) (layers "*.Cu" "*.Mask"))'
def write(name, L):
    open(os.path.join(LIB, name + ".kicad_mod"), "w").write("\n".join(L + [")"]) + "\n"); print("wrote", name)
def silk_box(w, h):
    return rect(-w / 2, -h / 2, w / 2, h / 2, "F.SilkS", 0.12)

def usb_c_vert():
    n = "MP62_USB_C_24P_Vertical_PLACEHOLDER"
    L = head(n, "PLACEHOLDER vertical (top-entry) USB Type-C 24P USB 3.2 receptacle, mouth 8.94 x 3.26 on F.Fab. Generic 2 x 12 SMD rows at 0.5 + 4 THT shell tabs. "
             "Replace with the chosen part (JLC vertical 24P USB-C, e.g. SHOU HAN / Korean Hroparts vertical; Molex 217175 class [Unverified]).", "USB-C vertical 24P placeholder", "through_hole")
    names = ["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12"]
    for i in range(12):
        x = -2.75 + 0.5 * i
        L.append(smd("A%d" % (i + 1), x, -2.6, 0.3, 1.0)); L.append(smd("B%d" % (12 - i), x + 0.25 - 0.25, 2.6, 0.3, 1.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            L.append(oval("S", sx * 4.3, sy * 1.2, 1.0, 1.8, 0.6, 1.4))
    L += [rect(-4.47, -1.63, 4.47, 1.63, "F.Fab", 0.1), rect(-5.0, -3.4, 5.0, 3.4, "F.CrtYd", 0.05),
          text("USB-C mouth 8.94x3.26 (vertical) PLACEHOLDER", 0, 4.0, "F.Fab", 0.4)]
    write(n, L)

def usb_a_vert():
    n = "MP62_USB_A3_9P_Vertical_PLACEHOLDER"
    L = head(n, "PLACEHOLDER vertical USB 3.0 Type-A receptacle (9 signal THT + 4 shell THT), mouth 12.5 x 5.12 on F.Fab, shell 13.2 x 5.8. "
             "Replace with the chosen JLC vertical USB3.0 A part (e.g. SHOU HAN / XKB vertical AF 3.0 [Unverified]).", "USB-A 3.0 vertical placeholder", "through_hole")
    for i in range(4): L.append(tht(str(i + 1), -3.0 + 2.0 * i, -1.25, 1.1, 0.7))
    for i in range(5): L.append(tht(str(5 + i), -4.0 + 2.0 * i, 1.25, 1.1, 0.7))
    for sx in (-1, 1):
        for sy in (-1, 1): L.append(oval("S", sx * 6.75, sy * 1.9, 1.3, 2.4, 0.8, 1.9))
    L += [rect(-6.25, -2.56, 6.25, 2.56, "F.Fab", 0.1), rect(-7.6, -3.4, 7.6, 3.4, "F.CrtYd", 0.05),
          text("USB-A 3.0 vertical PLACEHOLDER", 0, 3.9, "F.Fab", 0.4)]
    write(n, L)

def rj45_hr913790a():
    """HanRun HR913790A: 1x1 vertical (top-entry) RJ45 with integrated 2.5G/5GBASE-T magnetics + 3 LEDs. From the HanRun drawing REV A1
    (component-side view): body 16.20 x 17.00, height 16.90; 10 signal pins d0.89 at 1.27 pitch in two rows 2.54 apart; LEDs d1.02;
    shield d1.63 at 15.80; 2 x d3.20 posts at 11.43. Origin = body centre; LED/latch side toward -y. Row y-positions read from the drawing (VERIFY)."""
    n = "MP62_RJ45_HanRun_HR913790A_Vertical_2G5"
    L = head(n, "HanRun HR913790A vertical RJ45 magjack, 2.5G/5GBASE-T (IEEE 802.3bz), 3 LEDs, shielded. Body 16.2 x 17.0 x 16.9 h. Land pattern from the HanRun drawing REV A1; verify row offsets before ordering.",
             "RJ45 vertical magjack 2.5G HR913790A", "through_hole")
    yh = -8.5 + 6.83
    for k in range(1, 11):
        x = (5.5 - k) * 1.27; y = yh + 8.89 - (2.54 if k % 2 == 0 else 0.0)
        L.append(tht(str(k), x, y, 1.4, 0.95))
    for k, x in ((14, -6.325), (13, -3.785), (12, 3.785), (11, 6.325)): L.append(tht(str(k), x, yh - 4.11, 1.6, 1.1))
    for sx in (-1, 1): L.append(tht("S", sx * 7.90, yh + 3.89, 2.5, 1.7))
    L += [npth(-5.715, yh, 3.2), npth(5.715, yh, 3.2)]
    L += [rect(-8.1, -8.5, 8.1, 8.5, "F.Fab", 0.1), rect(-5.85, -4.2, 5.85, 4.2, "F.Fab", 0.08, True),
          rect(-9.3, -8.8, 9.3, 8.8, "F.CrtYd", 0.05), rect(-8.3, -8.7, 8.3, 8.7, "F.SilkS", 0.12) if False else '  (fp_line (start -8.3 -8.7) (end 8.3 -8.7) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))', '  (fp_line (start -8.3 8.7) (end 8.3 8.7) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
          text("HR913790A 16.2x17.0 h16.9 (LED/latch side -y)", 0, -9.4, "F.Fab", 0.4)]
    write(n, L)

def rj45_vert():
    n = "MP62_RJ45_Mag_2G5_Vertical_PLACEHOLDER"
    L = head(n, "PLACEHOLDER vertical (top-entry) RJ45 with integrated magnetics, 2.5GBASE-T/10GBASE-T rated, 2 LEDs. Shell <= 15.2 wide x 13.6, plug mouth 11.7 x 8.4 on F.Fab. "
             "8 + 4 CT/LED + 2 shield THT generic. Part TBD (must be rated 2.5G; 10G for the AQC107 site).", "RJ45 vertical magjack placeholder", "through_hole")
    for i in range(8): L.append(tht(str(i + 1), -4.445 + 1.27 * i, -3.0 + (1.27 if i % 2 else 0), 0.95, 0.6))
    for i, x in enumerate((-6.0, -4.0, 4.0, 6.0)): L.append(tht(str(9 + i), x, 4.5, 1.1, 0.7))
    for sx in (-1, 1): L.append(tht("S", sx * 7.0, -1.0, 2.0, 1.4))
    L += [npth(-5.7, 1.5, 3.2), npth(5.7, 1.5, 3.2)]
    L += [rect(-5.85, -4.2, 5.85, 4.2, "F.Fab", 0.1), rect(-7.6, -6.8, 7.6, 6.8, "F.Fab", 0.08, True), 
          rect(-8.3, -7.2, 8.3, 7.2, "F.CrtYd", 0.05), text("RJ45 magjack vertical PLACEHOLDER (shell 15.2)", 0, 7.8, "F.Fab", 0.4)]
    write(n, L)

def hdmi_vert():
    n = "MP62_HDMI_A_Vertical_PLACEHOLDER"
    L = head(n, "PLACEHOLDER vertical HDMI Type-A receptacle, mouth 14.0 x 4.55, shell 15.0 x 5.6 on F.Fab; 19 SMD at 0.5 (2 rows) + 4 shell THT generic. Part TBD.", "HDMI vertical placeholder", "through_hole")
    for i in range(19): L.append(smd(str(i + 1), -4.5 + 0.5 * i, -2.9 if i % 2 == 0 else 2.9, 0.3, 1.1))
    for sx in (-1, 1):
        for sy in (-1, 1): L.append(oval("S", sx * 7.85, sy * 1.6, 1.1, 1.9, 0.7, 1.5))
    L += [rect(-7.5, -2.8, 7.5, 2.8, "F.Fab", 0.1), rect(-7.0, -2.27, 7.0, 2.27, "F.Fab", 0.06, True), 
          rect(-8.6, -3.7, 8.6, 3.7, "F.CrtYd", 0.05), text("HDMI-A vertical PLACEHOLDER", 0, 4.3, "F.Fab", 0.4)]
    write(n, L)

def aud_edge():
    n = "MP62_StockAudio_EdgeCard_50P_P0.5_PLACEHOLDER"
    L = head(n, "PLACEHOLDER for the stock Mac Pro 6,1 audio-module connector (front side, X 34-68 x Y ~10 on the stock board, ~34 x 5 mm body, long slot with a row of spring contacts). "
             "Pin count and pitch NOT confirmed (photo: ~45-50 contacts, ~0.5 mm). Single row of 50 SMD at 0.5 mm + 2 hold-downs. Replace once Aidan counts the contacts and measures the pitch.", "stock audio flex edge-card placeholder")
    for i in range(50): L.append(smd(str(i + 1), -12.25 + 0.5 * i, -1.9, 0.28, 1.2))
    for sx in (-1, 1): L.append(smd("MP", sx * 15.6, 0.6, 2.0, 2.8))
    L += [rect(-17.0, -2.6, 17.0, 2.6, "F.Fab", 0.1), rect(-12.6, -0.4, 12.6, 0.4, "F.Fab", 0.06, True), 
          rect(-17.4, -3.2, 17.4, 3.2, "F.CrtYd", 0.05), text("STOCK AUDIO MODULE CONNECTOR - PLACEHOLDER (count pins!)", 0, 3.7, "F.Fab", 0.5)]
    write(n, L)

def psu_dc12():
    n = "MP62_StockPSU_DC_12P_P1.5_Shrouded_PLACEHOLDER"
    L = head(n, "PLACEHOLDER for the stock PSU DC-out header (B side, stock position): shrouded 22.6 x 11.0, one row of blade contacts on one wall, "
             "pitch ~1.5-1.6 mm, 11 or 12 positions (photo shows 11 clearly; Aidan reports 12). Generic 12 x THT at 1.5. CONFIRM count, pitch, row offset and the mating plug.", "PSU DC header placeholder", "through_hole")
    for i in range(12): L.append(tht(str(i + 1), -8.25 + 1.5 * i, 1.2, 1.0, 0.65))
    L += [rect(-11.3, -5.5, 11.3, 5.5, "F.Fab", 0.1), rect(-11.4, -5.8, 11.4, 5.8, "F.CrtYd", 0.05),
          text("PSU DC-OUT 12P PLACEHOLDER", 0, 6.5, "F.Fab", 0.5)]
    write(n, L)

def nut_m16():
    n = "MP62_SMT_Nut_M1.6_H1.5_SMTSO1615"
    L = head(n, "SMT threaded standoff M1.6 x 1.5 mm (Sinhoo SMTSO1615MTJ, LCSC C2928168, hex 3.18 + 0.48 pilot; alt YIYUAN SMTSOM1.615STR C49236407 round). "
             "Pilot into a 2.2 mm plated hole, annular pad 4.2 (VERIFY against the Sinhoo drawing). Speaker screws: M1.6, ~3 mm overall, ~2 mm thread.", "SMT nut M1.6 speaker", "smd")
    L += [f'  (pad "1" thru_hole circle (at 0 0) (size 4.200 4.200) (drill 2.200) (layers "*.Cu" "F.Paste" "*.Mask"))',
          circ(0, 0, 1.59, "F.Fab", 0.1), circ(0, 0, 2.4, "F.CrtYd", 0.05), circ(0, 0, 2.25, "F.SilkS", 0.12), text("M1.6 SMT nut", 0, 3.0, "F.Fab", 0.4)]
    write(n, L)

def standoff_frame():
    n = "MP62_Frame_Standoff_M2_SMT_PLACEHOLDER"
    L = head(n, "SMT M2 threaded standoff for the I/O-frame centre screw (stock TB-bar screw point). Height = M-IOF2 (TBD), thread TBD (stock screw). "
             "YIYUAN SMTSO-M2 class. Pad D5.0 over a 2.6 plated hole.", "frame standoff", "smd")
    L += [f'  (pad "1" thru_hole circle (at 0 0) (size 5.000 5.000) (drill 2.600) (layers "*.Cu" "F.Paste" "*.Mask"))',
          circ(0, 0, 2.6, "F.CrtYd", 0.05), circ(0, 0, 2.5, "F.Fab", 0.1)]
    write(n, L)

def mount_hole():
    n = "MP62_IO_MountHole_D3.8_Pad7.5"
    L = head(n, "Stock I/O-board mounting hole: plated, drill 3.8 (stock 3.8-4.3 est.), pad 7.5 (stock pads 7.2-7.8). GND/chassis. Keep Ø8 clear both sides.", "mount hole", "through_hole")
    L += [tht("1", 0, 0, 7.5, 3.8), circ(0, 0, 4.0, "F.CrtYd", 0.05), circ(0, 0, 4.0, "B.CrtYd", 0.05)]
    write(n, L)

def picoblade6():
    n = "MP62_StockPSU_SIG_6P_P1.25_Vertical_PLACEHOLDER"
    L = head(n, "PLACEHOLDER for the stock PSU signal connector (B side, stock position): 6 positions at ~1.2-1.25 mm, vertical SMT with 2 hold-downs, body ~8.8 x 4.5 "
             "(Molex PicoBlade 53398-0671 / JST GH BM06B-GHS-TBT class). CONFIRM pitch and series.", "PSU signal placeholder")
    for i in range(6): L.append(smd(str(i + 1), -3.125 + 1.25 * i, -1.6, 0.6, 1.6))
    for sx in (-1, 1): L.append(smd("MP", sx * 4.6, 1.6, 1.2, 2.2))
    L += [rect(-4.4, -2.2, 4.4, 2.6, "F.Fab", 0.1), rect(-4.6, -2.8, 4.6, 3.2, "F.SilkS", 0.12) if False else rect(-5.3, -2.8, 5.3, 3.2, "F.CrtYd", 0.05)]
    write(n, L)

def qfn_ph(name, w, h, pins_per_side, pitch, ep, descr):
    L = head(name, descr, "QFN placeholder"); k = 0
    for side in range(4):
        for i in range(pins_per_side[side]):
            k += 1; off = (i - (pins_per_side[side] - 1) / 2) * pitch
            if side == 0: x, y, sx, sy = -w / 2, off, 0.7, 0.22
            elif side == 1: x, y, sx, sy = off, h / 2, 0.22, 0.7
            elif side == 2: x, y, sx, sy = w / 2, -off, 0.7, 0.22
            else: x, y, sx, sy = -off, -h / 2, 0.22, 0.7
            L.append(smd(str(k), x, y, sx, sy))
    if ep: L.append(smd(str(k + 1), 0, 0, ep[0], ep[1]))
    L += [rect(-w / 2, -h / 2, w / 2, h / 2, "F.Fab", 0.1), rect(-w / 2 - 0.7, -h / 2 - 0.7, w / 2 + 0.7, h / 2 + 0.7, "F.CrtYd", 0.05),
          circ(-w / 2 - 0.6, -h / 2 - 0.6, 0.15, "F.SilkS", 0.12), text("PLACEHOLDER", 0, 0, "F.Fab", 0.4)]
    write(name, L)

def copy(lib, name, src=SYS):
    shutil.copy(os.path.join(src, lib + ".pretty", name + ".kicad_mod"), os.path.join(LIB, name + ".kicad_mod")); print("copied", name)

usb_c_vert(); usb_a_vert(); rj45_vert(); rj45_hr913790a(); hdmi_vert(); aud_edge(); psu_dc12(); nut_m16(); standoff_frame(); mount_hole(); picoblade6()
qfn_ph("MP62_TI_TPS65994AD_QFN-48_6x6_P0.4_PLACEHOLDER", 6, 6, (12, 12, 12, 12), 0.4, (4.2, 4.2),
       "PLACEHOLDER TI TPS65994ADRSLR dual-port USB-C PD controller (6 x 6 VQFN, LCSC stock seen). Replace with the TI land pattern (power-path pads are not generic).")
qfn_ph("MP62_TI_TUSB1046A_WQFN-40_4x6_P0.5_PLACEHOLDER", 4, 6, (12, 8, 12, 8), 0.4, (2.4, 4.4),
       "PLACEHOLDER TI TUSB1046A-DCI USB-C 10 Gbps + DP 8.1 Gbps alt-mode linear redriver crosspoint (WQFN-40 4 x 6, RNQ). Replace with TI RNQ0040A.")
qfn_ph("MP62_TI_TUSB1002A_WQFN-24_4x4_P0.5_PLACEHOLDER", 4, 4, (6, 6, 6, 6), 0.5, (2.6, 2.6),
       "PLACEHOLDER TI TUSB1002A USB 3.2 10 Gbps 2-channel redriver (WQFN-24 4 x 4, RGE). Replace with TI RGE0024.")
qfn_ph("MP62_TI_TDP158_WQFN-40_5x5_P0.4_PLACEHOLDER", 5, 5, (10, 10, 10, 10), 0.4, (3.5, 3.5),
       "PLACEHOLDER TI TDP158RSBT 6 Gbps AC-coupled TMDS -> HDMI 2.0 retimer (WQFN-40 5 x 5, RSB). Replace with TI RSB0040.")
qfn_ph("MP62_Intel_i226V_QFN-56_7x7_P0.4_PLACEHOLDER", 7, 7, (14, 14, 14, 14), 0.4, (5.1, 5.1),
       "PLACEHOLDER Intel Ethernet Controller i226-V (QFN 7 x 7). Land pattern and pin map from the Intel datasheet (CNDA).")
qfn_ph("MP62_WCH_CH334R_QFN-24_4x4_P0.5_PLACEHOLDER", 4, 4, (6, 6, 6, 6), 0.5, (2.6, 2.6),
       "PLACEHOLDER WCH CH334R 4-port USB 2.0 MTT hub (QFN-24 4 x 4). Verify pinout and package vs the WCH datasheet.")
for src, n in [(STOR, "MP62_TI_RNN0018A_VQFN-HR-18_3.5x3.5mm_PLACEHOLDER"), (STOR, "MP62_MCIO_124P_RA_SFF-TA-1016"), (STOR, "MP62_MCIO_74P_RA_SFF-TA-1016")]:
    lib = "MP62_Storage" if "RNN" in n else "MP62_Face"
    copy(lib, n, src)
for lib, n in [("Package_DFN_QFN", "Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm"), ("Package_TO_SOT_SMD", "SOT-23-5"), ("Package_TO_SOT_SMD", "SOT-23-6"),
               ("Package_TO_SOT_SMD", "SOT-23"), ("Package_TO_SOT_SMD", "SOT-563"), ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"), ("Package_SO", "MSOP-8_3x3mm_P0.65mm"),
               ("Package_SO", "TSSOP-28_4.4x9.7mm_P0.65mm"), ("Package_QFP", "LQFP-48_7x7mm_P0.5mm"), ("Package_LGA", "LGA-12_2x2mm_P0.5mm"),
               ("Crystal", "Crystal_SMD_3225-4Pin_3.2x2.5mm"), ("Inductor_SMD", "L_Bourns_SRP1038C_10.0x10.0mm"), ("Inductor_SMD", "L_1008_2520Metric"),
               ("Capacitor_SMD", "C_0402_1005Metric"), ("Capacitor_SMD", "C_0805_2012Metric"), ("Capacitor_SMD", "C_1206_3216Metric"), ("Resistor_SMD", "R_0402_1005Metric"), ("Resistor_SMD", "R_0805_2012Metric"), ("Connector_FFC-FPC", "Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal"),
               ("LED_SMD", "LED_0603_1608Metric"), ("Diode_SMD", "D_SOD-323"), ("Battery", "BatteryHolder_Keystone_3034_1x20mm"),
               ("Connector_JST", "JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical"), ("Connector_JST", "JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical"),
               ("Connector_Molex", "Molex_Micro-Fit_3.0_43045-0812_2x04_P3.00mm_Vertical"), ("Button_Switch_SMD", "SW_SPST_TL3342"),
               ("Button_Switch_SMD", "SW_SPST_PTS810")]:
    copy(lib, n)
