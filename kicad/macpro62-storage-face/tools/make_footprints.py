#!/usr/bin/env python3
"""Write the MP62_Face.pretty footprints for the MP62-FACE v0.1 template.
MCIO footprints follow SFF-TA-1016 Rev 1.3 Annex A recommended RA footprints (Table A-1 74P, Table A-2 124P).
Footprint origin = datum X (connector centre) on datum Y (locating-hole centreline). Mating face toward local -y.
ASSUMPTION (TO VERIFY vs the Amphenol G97R2x332HR drawing): pad rows / solder-pin slots lie on the side of
datum Y away from the mating face (+y). Run with any python3."""
import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.abspath(os.path.join(HERE, "..", "MP62_Face.pretty"))
SYS = "/usr/share/kicad/footprints"
os.makedirs(LIB, exist_ok=True)

def head(name, descr, tags, attr="smd"):
    return [f'(footprint "{name}"', '  (version 20241229)', '  (generator "mp62_face_template")', '  (layer "F.Cu")',
            f'  (descr "{descr}")', f'  (tags "{tags}")',
            '  (property "Reference" "REF**" (at 0 -1 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))',
            f'  (property "Value" "{name}" (at 0 1 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
            f'  (attr {attr})']
def rect(x1, y1, x2, y2, layer, w=0.1):
    return f'  (fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))'
def circ(x, y, r, layer, w=0.05):
    return f'  (fp_circle (center {x:.3f} {y:.3f}) (end {x + r:.3f} {y:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))'
def text(s, x, y, layer="F.Fab", size=0.6):
    return f'  (fp_text user "{s}" (at {x:.3f} {y:.3f} 0) (layer "{layer}") (effects (font (size {size} {size}) (thickness {size * 0.15:.3f}))))'
def write(name, lines):
    open(os.path.join(LIB, name + ".kicad_mod"), "w").write("\n".join(lines + [")"]) + "\n")
    print("wrote", name)

def mcio(npos):
    # npos = 74 (8i: 37 per row) or 124 (16i: 62 per row)
    if npos == 124:
        xs = [-18.90 + 0.6 * i for i in range(37)] + [4.50 + 0.6 * i for i in range(25)]
        peg, slot, body_w, plug_w = 40.645, 41.70, 42.20, 46.0
        name = "MP62_MCIO_124P_RA_SFF-TA-1016"
        descr = ("MCIO 124P (16i, x16 + 2 sideband sets) right-angle receptacle, SFF-TA-1016 Rev 1.3 Table A-2 recommended footprint. "
                 "Amphenol G97R24332HR (LCSC C4867471) / JPC / Molex 2173463021 class. Pad rows assumed behind datum Y (verify vs vendor drawing). "
                 "Courtyard includes the straight-plug zone (13.1 mm) in front of the mating face.")
    else:
        xs = [-10.80 + 0.6 * i for i in range(37)]
        peg, slot, body_w, plug_w = 24.445, 25.50, 25.80, 29.0
        name = "MP62_MCIO_74P_RA_SFF-TA-1016"
        descr = ("MCIO 74P (8i, 8 pairs/row + sideband) right-angle receptacle, SFF-TA-1016 Rev 1.3 Table A-1 recommended footprint. "
                 "Amphenol G97R22332HR (LCSC C5433520) / JPC P947B0743313 class. Pad rows assumed behind datum Y (verify vs vendor drawing). "
                 "Courtyard includes the plug zone.")
    L = head(name, descr, "MCIO SFF-TA-1016 MP62")
    yf, yr = -6.025, 4.045                     # mating face, body rear (Table 5-4: 6.025 face-to-peg, 10.07 long)
    L += [rect(-body_w / 2, yf, body_w / 2, yr, "F.Fab"),
          rect(-plug_w / 2, yf - 13.1, plug_w / 2, yf, "F.Fab", 0.08),
          rect(-plug_w / 2 - 0.25, yf - 13.1 - 0.25, plug_w / 2 + 0.25, yr + 0.85, "F.CrtYd", 0.05),
          f'  (fp_line (start {-body_w / 2:.3f} {yf:.3f}) (end {body_w / 2:.3f} {yf:.3f}) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
          f'  (fp_circle (center {xs[0]:.3f} {yr + 1.2:.3f}) (end {xs[0] + 0.25:.3f} {yr + 1.2:.3f}) (stroke (width 0.12) (type solid)) (fill yes) (layer "F.SilkS"))',
          text("MATING FACE / plug zone (cable exits this way)", 0, yf - 6.5),
          text("pin A1/B1", xs[0], yr + 2.0, "F.Fab", 0.8)]
    for i, x in enumerate(xs):
        n = i + 1
        L.append(f'  (pad "A{n}" smd rect (at {x:.3f} 0.575) (size 0.350 1.400) (layers "F.Cu" "F.Paste" "F.Mask"))')
        L.append(f'  (pad "B{n}" smd rect (at {x:.3f} 3.525) (size 0.350 1.400) (layers "F.Cu" "F.Paste" "F.Mask"))')
    for sx in (-1, 1):
        L.append(f'  (pad "" np_thru_hole circle (at {sx * peg / 2:.4f} 0) (size 1.100 1.100) (drill 1.100) (layers "*.Cu" "*.Mask"))')
        for yy in (1.775, 4.325):
            L.append(f'  (pad "MP" thru_hole oval (at {sx * slot / 2:.3f} {yy:.3f}) (size 1.000 1.900) (drill oval 0.600 1.500) (layers "*.Cu" "*.Mask"))')
    write(name, L)

def mount():
    name = "MP62_FACE_MountHole_D5.0_Pad9.0"
    L = head(name, "MP62-FACE mounting hole: D5.0 PTH, D9.0 pad both sides (bond to GND/chassis per spec). Courtyard F D11 (core boss D9 + margin = spec KO-F1) and B D12 (screw head/spring zone D12 = KO-B2).",
             "MP62 mounting hole", "through_hole")
    L += ['  (pad "1" thru_hole circle (at 0 0) (size 9.000 9.000) (drill 5.000) (layers "*.Cu" "*.Mask"))',
          circ(0, 0, 5.5, "F.CrtYd"), circ(0, 0, 6.0, "B.CrtYd"), circ(0, 0, 5.0, "F.Fab", 0.1), circ(0, 0, 6.0, "B.Fab", 0.1)]
    write(name, L)

def lug():
    name = "MP62_FACE_BusBarLug_D3.2_Pad8.8"
    L = head(name, "MP62-FACE 12 V / GND bus-bar lug site for the stock PSU bus bar (T8 923-0716 class screw, thread TO MEASURE M5). D3.2 PTH, D8.8 pad both sides, 8 x D0.5 stitching holes. Use 2 oz outer copper; >= 15 A per lug.",
             "MP62 power lug busbar", "through_hole")
    L += ['  (pad "1" thru_hole circle (at 0 0) (size 8.800 8.800) (drill 3.200) (layers "*.Cu" "*.Mask"))']
    import math
    for i in range(8):
        a = 2 * math.pi * i / 8
        L.append(f'  (pad "1" thru_hole circle (at {3.2 * math.cos(a):.3f} {3.2 * math.sin(a):.3f}) (size 0.900 0.900) (drill 0.500) (layers "*.Cu"))')
    L += [circ(0, 0, 4.9, "F.CrtYd"), circ(0, 0, 4.9, "B.CrtYd"), circ(0, 0, 4.4, "F.Fab", 0.1)]
    write(name, L)

def copy_sys(lib, name, newname=None):
    src = os.path.join(SYS, lib + ".pretty", name + ".kicad_mod")
    s = open(src).read()
    if newname:
        s = s.replace(f'(footprint "{name}"', f'(footprint "{newname}"', 1)
    open(os.path.join(LIB, (newname or name) + ".kicad_mod"), "w").write(s)
    print("copied", name)

mcio(124); mcio(74); mount(); lug()
copy_sys("Connector_JST", "JST_GH_SM15B-GHS-TB_1x15-1MP_P1.25mm_Horizontal")
copy_sys("Connector_Molex", "Molex_Mini-Fit_Jr_5569-08A2_2x04_P4.20mm_Horizontal")
