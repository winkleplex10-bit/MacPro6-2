#!/usr/bin/env python3
"""HOAUC HYC79-HDMIA19-105 (LCSC C711353) vertical HDMI-A 19P footprint (D-IO16, 2026-10-04 ~10:30 ET).
Source: tools/easyeda/C711353_HYC79-HDMIA19-105.json = https://easyeda.com/api/products/C711353/components?version=6.4.19.5
(package "HDMI-SMD_HYC79-HDMIA19-105", JLCEDA/EasyEDA Official Library - https://lceda.cn/ , https://easyeda.com).
Checked against the HOAUC drawing HYC-HDMI17102115 "RECOMMENDED P.C.B. LAYOUT (T=1.6mm)" (tools/easyeda/HOAUC_HYC79-HDMIA19-105_C711353.pdf):
  19 SMD 0.30 x 2.00 at 0.50 in ONE row (pin 1 at -4.21, pin 19 at +4.79 from the centre-hole axis: span 9.00, offset 0.29)   EasyEDA: 0.28 wide -> drawing 0.30 used
  + 2 DUMMY PIN pads left of pin 1 (drawing; EasyEDA omits them) -> pads "MP" at -4.71 / -5.21, same size, no net
  3 THT shell / support legs: drill 1.30, pad D1.90 (drawing; EasyEDA D2.00) -> annular ring 0.30 (JLC FPC >= 0.25 OK; the old placeholder had 0.20)
  outer legs at +-7.25 (14.50), 1.60 from the pad-row edge; centre leg on the axis, 3.30 behind the outer legs.          EasyEDA positions agree to 0.01.
Origin: the receptacle SHELL centre (= module port axis), estimated from the drawing views (flange 17.30 x 6.45, shell 14.00 x 4.55) and the
EasyEDA silk outline (flange y -4.1 .. +2.6 about the EasyEDA origin): shell centre = EasyEDA y -0.55 (+-0.2, VERIFY on a part / STEP).
EasyEDA units: 1 = 10 mil = 0.254 mm; EasyEDA y grows downward = KiCad y."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE)
SRC = os.path.join(HERE, "easyeda", "C711353_HYC79-HDMIA19-105.json")
NAME = "HOAUC_HYC79-HDMIA19-105"
U = 0.254
YC = -0.55                      # shell centre in EasyEDA footprint coords (KiCad origin)
W_PAD, L_PAD = 0.30, 2.00       # drawing
D_DRILL, D_PAD = 1.30, 1.90     # drawing
def main():
    ds = json.load(open(SRC))["result"]["packageDetail"]["dataStr"]; ox, oy = float(ds["head"]["x"]), float(ds["head"]["y"])
    mm = lambda x, y: (round((float(x) - ox) * U, 2) + 0.0, round((float(y) - oy) * U - YC, 2) + 0.0)
    smd, tht = [], []
    for s in ds["shape"]:
        f = s.split("~")
        if f[0] != "PAD": continue
        c = mm(f[2], f[3]); num = f[8]
        if f[6] == "1": smd.append((num, c))
        elif f[6] == "11": tht.append(c)
    assert len(smd) == 19 and len(tht) == 3, (len(smd), len(tht))
    smd.sort(key=lambda t: int(t[0]))
    for n, (x, y) in smd: assert abs(x - (-4.21 + 0.5 * (int(n) - 1))) < 0.011, (n, x)      # drawing check
    yr = smd[0][1][1]
    L = ['(footprint "%s"' % NAME, '  (version 20241229)', '  (generator "mp62_io")', '  (layer "F.Cu")',
         '  (descr "HOAUC HYC79-HDMIA19-105 (LCSC C711353) HDMI-A 19P vertical 180 deg, H 10.5, SMD signals (1 row 0.5 pitch) + 3 THT legs D1.30. JLCEDA/EasyEDA Official Library land data checked against HOAUC drawing HYC-HDMI17102115; pads 0.30 x 2.00 and 2 dummy pads per the drawing; leg pads D1.90 (ring 0.30). Origin = shell centre (VERIFY +-0.2).")',
         '  (property "Reference" "REF**" (at 0 -5 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         '  (property "Value" "%s" (at 0 5.3 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))' % NAME, '  (attr smd)']
    for n, (x, y) in smd:
        L.append('  (pad "%s" smd rect (at %.3f %.3f) (size %.3f %.3f) (layers "F.Cu" "F.Paste" "F.Mask"))' % (n, x, y, W_PAD, L_PAD))
    for x in (smd[0][1][0] - 0.5, smd[0][1][0] - 1.0):
        L.append('  (pad "MP" smd rect (at %.3f %.3f) (size %.3f %.3f) (layers "F.Cu" "F.Paste" "F.Mask"))' % (x, yr, W_PAD, L_PAD))
    for (x, y) in tht:
        L.append('  (pad "S" thru_hole circle (at %.3f %.3f) (size %.3f %.3f) (drill %.3f) (layers "*.Cu" "*.Mask"))' % (x, y, D_PAD, D_PAD, D_DRILL))
    fy0, fy1 = -3.95 - YC, 2.50 - YC          # flange 6.45 deep (drawing), EasyEDA silk -4.1 .. +2.6
    L += ['  (fp_rect (start -8.650 %.3f) (end 8.650 %.3f) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))' % (fy0, fy1),
          '  (fp_rect (start -7.000 -2.275) (end 7.000 2.275) (stroke (width 0.06) (type dash)) (fill no) (layer "F.Fab"))',
          '  (fp_rect (start -8.900 %.3f) (end 8.900 %.3f) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))' % (fy0 - 0.25, yr + L_PAD / 2 + 0.25),
          '  (fp_circle (center %.3f %.3f) (end %.3f %.3f) (stroke (width 0.1) (type solid)) (fill solid) (layer "F.Fab"))' % (smd[0][1][0], yr - 1.4, smd[0][1][0] + 0.12, yr - 1.4),
          '  (fp_text user "pin 1" (at %.3f %.3f 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))' % (smd[0][1][0], yr - 1.9), ")"]
    fn = os.path.join(PRJ, "MP62_MOD.pretty", NAME + ".kicad_mod"); open(fn, "w").write("\n".join(L) + "\n")
    print("wrote", fn, "pad row y %.2f" % yr, "legs", tht)
if __name__ == "__main__": main()
