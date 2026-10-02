"""Footprints for the D-IO16 port modules (2026-10-02 ~12:35 ET). PLACEHOLDER land patterns from catalogue data: replace with vendor drawings before fab.
Main board (MP62_IO.pretty): clamp-post SMT nut, cradle locating peg, TSSOP-24 (TCA9548A / TCA9555).
Modules (MP62_MOD.pretty): all-SMD vertical USB-C, DF40C-50DP header, WLCSP-4 ID EEPROM, sleeve GND rings, copies of the USB-A / HDMI placeholders and 0201/0402."""
import os, shutil
IO = "/workspace/kicad/macpro62-io-board/MP62_IO.pretty"; MOD = "/workspace/kicad/macpro62-io-modules/MP62_MOD.pretty"; SYS = "/usr/share/kicad/footprints"
def hdr(name, descr, attr="smd"):
    return ['(footprint "%s"' % name, '  (version 20241229)', '  (generator "mp62_io")', '  (layer "F.Cu")', '  (descr "%s")' % descr,
            '  (property "Reference" "REF**" (at 0 -1 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
            '  (property "Value" "%s" (at 0 1 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))' % name, '  (attr %s)' % attr]
def rect(x0, y0, x1, y1, layer, w=0.05):
    return '  (fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width %.2f) (type solid)) (fill no) (layer "%s"))' % (x0, y0, x1, y1, w, layer)
def smd(num, x, y, w, h, shape="roundrect", layers='"F.Cu" "F.Paste" "F.Mask"'):
    rr = ' (roundrect_rratio 0.25)' if shape == "roundrect" else ""
    return '  (pad "%s" smd %s (at %.3f %.3f) (size %.3f %.3f) (layers %s)%s)' % (num, shape, x, y, w, h, layers, rr)
def npth(x, y, d): return '  (pad "" np_thru_hole circle (at %.3f %.3f) (size %.3f %.3f) (drill %.3f) (layers "*.Cu" "*.Mask"))' % (x, y, d, d, d)
def pth(num, x, y, d, ring): return '  (pad "%s" thru_hole circle (at %.3f %.3f) (size %.3f %.3f) (drill %.3f) (layers "*.Cu" "*.Mask"))' % (num, x, y, ring, ring, d)
def circ(r, layer="F.CrtYd"): return '  (fp_circle (center 0 0) (end %.2f 0) (stroke (width 0.05) (type solid)) (fill no) (layer "%s"))' % (r, layer)
def write(d, name, L): os.makedirs(d, exist_ok=True); open(os.path.join(d, name + ".kicad_mod"), "w").write("\n".join(L + [")"]) + "\n")
# ---- main board ----
L = hdr("MP62_Cradle_Nut_M2_SMT_PLACEHOLDER", "M2 BLIND SMT standoff (closed end, OD 4.0, e.g. Wurth WA-SMSI 9774xxx243 class; PART TBC on LCSC) under a port-module clamp post: clamp screw -> plate -> printed post -> standoff. F-only pad, no hole (B-side parts underneath stay).")
L += [smd("1", 0, 0, 4.4, 4.4, "circle"), circ(2.6)]; write(IO, "MP62_Cradle_Nut_M2_SMT_PLACEHOLDER", L)
L = hdr("MP62_Cradle_Peg_D1.6_NPTH", "Locating hole for a printed port-module cradle peg (D1.5 peg, D1.6 hole).", "exclude_from_pos_files exclude_from_bom")
L += [npth(0, 0, 1.6), circ(1.3)]; write(IO, "MP62_Cradle_Peg_D1.6_NPTH", L)
shutil.copy(os.path.join(SYS, "Package_SO.pretty", "TSSOP-24_4.4x7.8mm_P0.65mm.kicad_mod"), os.path.join(IO, "TSSOP-24_4.4x7.8mm_P0.65mm.kicad_mod"))
# ---- modules ----
# all-SMD vertical USB-C (HOAUC HYCW417-USBC24-180B, C5342202): 2 x 12 signal pads + 4 SMD shell tabs [PLACEHOLDER geometry]
L = hdr("MP62_MOD_USB_C_24P_Vertical_SMD_PLACEHOLDER", "Vertical USB-C 24P receptacle, ALL SMD (signal + 4 shell tabs) for FPC mounting: HOAUC HYCW417-USBC24-180B (LCSC C5342202), L 10.0. Generic land pattern (2 x 12 at 0.5 + 4 SMD tabs) - REPLACE with the HOAUC drawing.")
for i in range(12):
    x = -2.75 + 0.5 * i; L.append(smd("A%d" % (i + 1), x, -2.6, 0.3, 1.0)); L.append(smd("B%d" % (12 - i), x, 2.6, 0.3, 1.0))
for sx in (-1, 1):
    for sy in (-1, 1): L.append(smd("S", sx * 4.3, sy * 1.4, 1.2, 2.0))
L += [rect(-4.47, -1.63, 4.47, 1.63, "F.Fab", 0.1), rect(-5.0, -3.4, 5.0, 3.4, "F.CrtYd")]; write(MOD, "MP62_MOD_USB_C_24P_Vertical_SMD_PLACEHOLDER", L)
# DF40C-50DP header (module paddle), 0.4 mm, 2 x 25 [PLACEHOLDER]: pads 0.23 x 0.7, rows 2.6 apart, fitting pads
L = hdr("MP62_Hirose_DF40C-50DP-0.4V_PLACEHOLDER", "Hirose DF40C-50DP-0.4V(51) header (LCSC C424645) on the port-module paddle (FPC + FR4 1.0 stiffener on the back), mates DF40C-50DS-0.4V(51) (C424646) on the main board, mated 1.5. PLACEHOLDER lands.")
for i in range(25):
    x = -4.8 + 0.4 * i; L.append(smd(str(2 * i + 1), x, 1.3, 0.23, 0.7)); L.append(smd(str(2 * i + 2), x, -1.3, 0.23, 0.7))
L += [smd("MP1", -5.9, 0, 0.5, 1.0), smd("MP2", 5.9, 0, 0.5, 1.0), rect(-6.1, -1.8, 6.1, 1.8, "F.Fab", 0.1), rect(-6.3, -2.1, 6.3, 2.1, "F.CrtYd")]
write(MOD, "MP62_Hirose_DF40C-50DP-0.4V_PLACEHOLDER", L)
# WLCSP-4 ID EEPROM 24C02 class (0.8 x 0.8, 0.4 pitch)
L = hdr("MP62_WLCSP-4_0.8x0.8_P0.4_EEPROM", "24C02-class I2C ID EEPROM, WLCSP-4 0.8 x 0.8, 0.4 pitch (e.g. Microchip AT24C02D-UUM0B; LCSC TBC). Fixed 0x50 (no address pins): one module per mux channel.")
for k, (x, y) in enumerate(((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2))): L.append(smd(str(k + 1), x, y, 0.22, 0.22, "circle"))
L += [rect(-0.4, -0.4, 0.4, 0.4, "F.Fab", 0.05), rect(-0.6, -0.6, 0.6, 0.6, "F.CrtYd")]; write(MOD, "MP62_WLCSP-4_0.8x0.8_P0.4_EEPROM", L)
# sleeve GND ring: exposed copper frame (coverlay opening, no paste) round the port courtyard; the SUS sleeve foot bears on it
for kind, (hx, hy) in {"USBC": (5.25, 3.65), "USBA": (7.65, 3.65), "HDMI": (8.85, 3.95)}.items():   # outer edge = stiffener/FPC edge - 0.35
    nm = "MP62_MOD_Sleeve_GND_Ring_%s" % kind
    L = hdr(nm, "Exposed GND frame (coverlay opening, ENIG, no paste) under the bonded SUS304 shield-sleeve foot, %s module; sleeve -> module GND -> frame finger." % kind)
    ly = "\"F.Cu\" \"F.Mask\""; w = 0.4
    L += [smd("G", 0, -hy - w / 2, 2 * hx + 2 * w, w, "rect", ly), smd("G", 0, hy + w / 2, 2 * hx + 2 * w, w, "rect", ly),
          smd("G", -hx - w / 2, 0, w, 2 * hy, "rect", ly), smd("G", hx + w / 2, 0, w, 2 * hy, "rect", ly),
          rect(-hx - w, -hy - w, hx + w, hy + w, "F.Fab", 0.05)]   # no courtyard: the ring surrounds the port courtyard by design
    write(MOD, nm, L)
for n in ("MP62_USB_A3_9P_Vertical_PLACEHOLDER", "MP62_HDMI_A_Vertical_PLACEHOLDER", "C_0402_1005Metric"):
    shutil.copy(os.path.join(IO, n + ".kicad_mod"), os.path.join(MOD, n + ".kicad_mod"))
shutil.copy(os.path.join(SYS, "Capacitor_SMD.pretty", "C_0201_0603Metric.kicad_mod"), os.path.join(MOD, "C_0201_0603Metric.kicad_mod"))
print("ok")
