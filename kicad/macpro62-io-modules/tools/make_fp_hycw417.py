#!/usr/bin/env python3
"""HOAUC HYCW417-USBC24-180B (LCSC C5342202) footprint from the LCSC / EasyEDA package data (D-IO16, 2026-10-04).
Source: tools/easyeda/C5342202_easyeda_components.json = https://easyeda.com/api/products/C5342202/components?version=6.4.19.5
(package "USB-C-SMD_HYCW417-USBC24-180B", JLCEDA/EasyEDA Official Library - https://lceda.cn/ , https://easyeda.com).
Cross-checked against the HOAUC drawing HYC-2212201742 "RECOMMENDED P.C.B. LAYOUT (T:1.00mm)" (tools/easyeda/HYCW417-USBC24-180B_datasheet.pdf):
24 x 0.27 at 0.50 (span 5.50), row pitch 3.30 (pad 1.30), shell slots 4 x 1.30 x 0.80 at 8.20 x 2.94, 2 x NPTH 0.60 at 11.00 (diagonal).
EasyEDA units: 1 = 10 mil = 0.254 mm; EasyEDA y grows downward = KiCad y."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE)
SRC = os.path.join(HERE, "easyeda", "C5342202_easyeda_components.json")
NAME = "HOAUC_HYCW417-USBC24-180B"
U = 0.254
def main():
    d = json.load(open(SRC))["result"]; pk = d["packageDetail"]; ds = pk["dataStr"]
    ox, oy = float(ds["head"]["x"]), float(ds["head"]["y"])
    mm = lambda x, y: (round((float(x) - ox) * U, 2) + 0.0, round((float(y) - oy) * U, 2) + 0.0)   # snapped to 0.01 (drawing nominals; EasyEDA rounding ~2 um)
    smd, tht, npth = [], [], []
    for s in ds["shape"]:
        f = s.split("~")
        if f[0] == "PAD":
            shp, x, y, w, h, layer, num = f[1], f[2], f[3], float(f[4]) * U, float(f[5]) * U, f[6], f[8]
            hole_r = float(f[9] or 0) * U; rot = float(f[11] or 0); hole_len = float(f[13] or 0) * U if len(f) > 13 and f[13] else 0.0
            c = mm(x, y)
            if shp == "RECT" and layer == "1": smd.append((num, c, round(w, 3), round(h, 3)))
            elif shp == "OVAL" and layer == "11":
                # EasyEDA OVAL w x h rotated 90 -> KiCad size (h, w); slot: width 2 r, length holeLength along the long axis
                sx, sy = (h, w) if abs(rot % 180 - 90) < 1 else (w, h)
                tht.append((num, c, round(sx, 2), round(sy, 2), round(hole_len, 2), round(2 * hole_r, 2)))
        elif f[0] == "HOLE":
            npth.append((mm(f[1], f[2]), round(2 * float(f[3]) * U, 2)))
    assert len(smd) == 24 and len(tht) == 4 and len(npth) == 2, (len(smd), len(tht), len(npth))
    L = ['(footprint "%s"' % NAME, '  (version 20241229)', '  (generator "mp62_io")', '  (layer "F.Cu")',
         '  (descr "HOAUC HYCW417-USBC24-180B vertical USB Type-C 24P receptacle, IPX8, H 10.0, shell legs 1.8 (LCSC C5342202). 24 SMD signal pads 0.27 x 1.30 at 0.50, '
         'row pitch 3.30; 4 plated THT shell slots 1.30 x 0.80 (EasyEDA pads 1.70 x 1.20 grown to 1.80 x 1.30 for a 0.25 JLC FPC annular ring, pin-in-paste) = pad S (GND); 2 NPTH 0.60 locating pegs. '
         'Land pattern from the JLCEDA/EasyEDA Official Library (https://lceda.cn/ , https://easyeda.com), package USB-C-SMD_HYCW417-USBC24-180B; '
         'checked against HOAUC drawing HYC-2212201742.")',
         '  (tags "USB C Type-C receptacle vertical 24P HOAUC HYCW417 C5342202")',
         '  (property "Reference" "REF**" (at 0 -3.2 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         '  (property "Value" "%s" (at 0 3.2 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))' % NAME,
         '  (property "LCSC" "C5342202" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 0.6 0.6) (thickness 0.1))))',
         '  (attr through_hole)']
    for num, (x, y), w, h in sorted(smd, key=lambda p: (p[0][0], int(p[0][1:]))):
        L.append('  (pad "%s" smd rect (at %.4f %.4f) (size %.4f %.4f) (layers "F.Cu" "F.Paste" "F.Mask"))' % (num, x, y, w, h))
    for num, (x, y), sx, sy, hl, hw in tht:
        # 2026-10-04: EasyEDA pads 1.70 x 1.20 on the 1.30 x 0.80 slot = 0.20 ring; JLC FPC PTH annular ring regular >= 0.25 (abs 0.18) -> grow to 1.80 x 1.30
        sx, sy = (max(sx, max(hl, hw) + 0.5), max(sy, min(hl, hw) + 0.5)) if sx >= sy else (max(sx, min(hl, hw) + 0.5), max(sy, max(hl, hw) + 0.5))
        L.append('  (pad "S" thru_hole oval (at %.4f %.4f) (size %.4f %.4f) (drill oval %.4f %.4f) (layers "*.Cu" "*.Mask" "F.Paste") (remove_unused_layers no))'
                 % (x, y, sx, sy, max(hl, hw), min(hl, hw)))
    for (x, y), dd in npth:
        L.append('  (pad "" np_thru_hole circle (at %.4f %.4f) (size %.4f %.4f) (drill %.4f) (layers "*.Cu" "*.Mask"))' % (x, y, dd, dd, dd))
    def rect(x0, y0, x1, y1, layer, w):
        return '  (fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width %.3f) (type solid)) (fill no) (layer "%s"))' % (x0, y0, x1, y1, w, layer)
    L.append(rect(-6.0, -2.5, 6.0, 2.5, "F.Fab", 0.1))                    # body at the seat 12.0 x 5.0 (EasyEDA silk)
    L.append(rect(-6.0, -3.39, 6.0, 3.39, "F.Fab", 0.05))                 # 3D outline incl. the gasket ears
    L.append(rect(-6.25, -3.65, 6.25, 3.65, "F.CrtYd", 0.05))
    L.append('  (fp_circle (center -3.3 -2.9) (end -3.15 -2.9) (stroke (width 0.1) (type solid)) (fill yes) (layer "F.Fab"))')   # A1 marker
    L.append('  (fp_text user "A1" (at -2.75 -2.95 0) (layer "F.Fab") (effects (font (size 0.4 0.4) (thickness 0.06))))')
    L.append('  (fp_text user "${REFERENCE}" (at 0 0 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.09))))')
    L.append(')')
    fn = os.path.join(PRJ, "MP62_MOD.pretty", NAME + ".kicad_mod"); open(fn, "w").write("\n".join(L) + "\n")
    print("wrote", fn); print("smd", len(smd), "tht", tht, "npth", npth)
if __name__ == "__main__": main()
