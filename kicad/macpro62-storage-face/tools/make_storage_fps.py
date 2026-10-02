#!/usr/bin/env python3
"""Write MP62_Storage.pretty: storage-module footprints (custom placeholders + copies of KiCad 9 stock parts).
PLACEHOLDER footprints are marked in their descr and on F.Fab; replace them with vendor land patterns before routing."""
import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.abspath(os.path.join(HERE, "..", "MP62_Storage.pretty"))
SYS = "/usr/share/kicad/footprints"
os.makedirs(LIB, exist_ok=True)

def head(name, descr, tags, attr="smd"):
    return [f'(footprint "{name}"', '  (version 20241229)', '  (generator "mp62_storage")', '  (layer "F.Cu")',
            f'  (descr "{descr}")', f'  (tags "{tags}")',
            '  (property "Reference" "REF**" (at 0 -1 0) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.15))))',
            f'  (property "Value" "{name}" (at 0 1 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
            f'  (attr {attr})']
def rect(x1, y1, x2, y2, layer, w=0.1, dash=False):
    t = "dash" if dash else "solid"
    return f'  (fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type {t})) (fill no) (layer "{layer}"))'
def circ(x, y, r, layer, w=0.05):
    return f'  (fp_circle (center {x:.3f} {y:.3f}) (end {x + r:.3f} {y:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))'
def text(s, x, y, layer="F.Fab", size=0.6):
    return f'  (fp_text user "{s}" (at {x:.3f} {y:.3f} 0) (layer "{layer}") (effects (font (size {size} {size}) (thickness {size * 0.15:.3f}))))'
def write(name, lines):
    open(os.path.join(LIB, name + ".kicad_mod"), "w").write("\n".join(lines + [")"]) + "\n"); print("wrote", name)

M2_REMOVED = set(range(59, 67))  # M key: positions 59-66 removed -> 67 contacts
def m2_socket():
    name = "MP62_M2_MKey_SMT_H4.2_PLACEHOLDER"
    L = head(name, "PLACEHOLDER M.2 Socket 3 M-key 67P SMT receptacle, H4.2 class (LOTES APCI0107-P001A, LCSC C841661; alt H3.2 APCI0079-P002A C841651). "
             "Origin = card-edge datum (card centreline). Card extends toward local +y. Pad rows/hold-downs/pegs are GENERIC (0.5 mm pitch per row, rows 0.25 offset) "
             "and MUST be replaced by the LOTES land pattern before routing.", "M.2 NGFF M-key NVMe socket placeholder")
    for n in range(1, 76):
        if n in M2_REMOVED: continue
        x = (38 - n) * 0.25          # pin 1 at +x (verify), pin 75 at -x
        y = -5.3 if n % 2 else -3.9  # odd row (card top side) further back
        L.append(f'  (pad "{n}" smd rect (at {x:.3f} {y:.3f}) (size 0.300 1.100) (layers "F.Cu" "F.Paste" "F.Mask"))')
    for sx in (-1, 1):
        L.append(f'  (pad "MP" smd rect (at {sx * 11.5:.3f} -2.0) (size 1.600 2.600) (layers "F.Cu" "F.Paste" "F.Mask"))')
        L.append(f'  (pad "" np_thru_hole circle (at {sx * 9.9:.3f} -1.2) (size 1.000 1.000) (drill 1.000) (layers "*.Cu" "*.Mask"))')
    L += [rect(-11.2, -6.2, 11.2, 0.6, "F.Fab", 0.1), rect(-12.6, -6.6, 12.6, 1.0, "F.CrtYd", 0.05),
          rect(-11.0, 0.0, 11.0, 80.0, "F.Fab", 0.08, dash=True),
          f'  (fp_line (start -11.2 -6.4) (end 11.2 -6.4) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
          text("PLACEHOLDER M.2 M-key socket H4.2 - replace land pattern", 0, -7.4, "F.Fab", 0.7),
          text("2280 card outline (dashed); host parts under card <= 1.6 mm", 0, 40, "F.Fab", 0.8),
          text("key (pins 59-66)", (38 - 62.5) * 0.25, -2.6, "F.Fab", 0.5)]
    write(name, L)

def m2_standoff():
    name = "MP62_M2_Standoff_SMT_M2_Pad5.0"
    L = head(name, "SMT M2 threaded standoff for M.2 card retention (YIYUAN SMTSO-M2 class, e.g. SMTSOM225BTR C5301773 is 2.5 mm tall; "
             "height must equal the socket card-bottom height, ~3.5 mm for H4.2 - VERIFY). Round SMD pad D5.0 (blind standoff, no hole).",
             "M.2 standoff SMT M2")
    L += ['  (pad "1" smd circle (at 0 0) (size 5.000 5.000) (layers "F.Cu" "F.Paste" "F.Mask"))',
          circ(0, 0, 2.75, "F.CrtYd"), circ(0, 0, 2.5, "F.Fab", 0.1)]
    write(name, L)

def bga():
    name = "MP62_BGA-492_21x21mm_Layout25x25_P0.8mm_PLACEHOLDER"
    rows = "ABCDEFGHJKLMNPRTUVWYAAABACADAE"
    rn = ["A","B","C","D","E","F","G","H","J","K","L","M","N","P","R","T","U","V","W","Y","AA","AB","AC","AD","AE"]
    L = head(name, "PLACEHOLDER for ASMedia ASM2824 LFBGA-492 21 x 21 mm (JLC C9900092023 'nbs_bga_492p'). Ball map and pitch NOT public here: "
             "assumed 25 x 25 @ 0.8 mm minus 133 (inner 11 x 11 + 3 per corner). REPLACE with the ASMedia/JLC land pattern before routing.",
             "BGA ASM2824 placeholder")
    n = 0
    for i, r in enumerate(rn):
        for j in range(25):
            c = j + 1
            inner = 7 <= i <= 17 and 7 <= j <= 17
            corner = (i, j) in [(0, 0), (0, 1), (1, 0), (0, 24), (0, 23), (1, 24), (24, 0), (23, 0), (24, 1), (24, 24), (23, 24), (24, 23)]
            if inner or corner: continue
            n += 1
            L.append(f'  (pad "{r}{c}" smd circle (at {(j - 12) * 0.8:.3f} {(i - 12) * 0.8:.3f}) (size 0.400 0.400) (layers "F.Cu" "F.Paste" "F.Mask"))')
    assert n == 492, n
    L += [rect(-10.5, -10.5, 10.5, 10.5, "F.Fab", 0.1), rect(-11.0, -11.0, 11.0, 11.0, "F.CrtYd", 0.05),
          f'  (fp_line (start -10.6 -9.0) (end -10.6 -10.6) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
          f'  (fp_line (start -10.6 -10.6) (end -9.0 -10.6) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
          circ(-9.8, -9.8, 0.3, "F.Fab", 0.1), text("ASM2824 PLACEHOLDER", 0, 0, "F.Fab", 1.0)]
    write(name, L)

def qfn_ph(name, w, h, pins_per_side, pitch, ep, descr):
    L = head(name, descr, "QFN placeholder")
    k = 0
    for side in range(4):
        for i in range(pins_per_side[side]):
            k += 1
            off = (i - (pins_per_side[side] - 1) / 2) * pitch
            if side == 0: x, y, sx, sy = -w / 2, off, 0.8, 0.25
            elif side == 1: x, y, sx, sy = off, h / 2, 0.25, 0.8
            elif side == 2: x, y, sx, sy = w / 2, -off, 0.8, 0.25
            else: x, y, sx, sy = -off, -h / 2, 0.25, 0.8
            L.append(f'  (pad "{k}" smd rect (at {x:.3f} {y:.3f}) (size {sx} {sy}) (layers "F.Cu" "F.Paste" "F.Mask"))')
    if ep:
        L.append(f'  (pad "{k + 1}" smd rect (at 0 0) (size {ep[0]} {ep[1]}) (layers "F.Cu" "F.Paste" "F.Mask"))')
    L += [rect(-w / 2, -h / 2, w / 2, h / 2, "F.Fab", 0.1), rect(-w / 2 - 0.7, -h / 2 - 0.7, w / 2 + 0.7, h / 2 + 0.7, "F.CrtYd", 0.05),
          circ(-w / 2 - 0.6, -h / 2 - 0.6, 0.15, "F.SilkS", 0.12), text("PLACEHOLDER", 0, 0, "F.Fab", 0.4)]
    write(name, L)

def copy_sys(lib, name):
    shutil.copy(os.path.join(SYS, lib + ".pretty", name + ".kicad_mod"), os.path.join(LIB, name + ".kicad_mod")); print("copied", name)

m2_socket(); m2_standoff(); bga()
qfn_ph("MP62_TI_RNN0018A_VQFN-HR-18_3.5x3.5mm_PLACEHOLDER", 3.5, 3.5, (5, 4, 5, 4), 0.5, None,
       "PLACEHOLDER outline for TI TPS56C215RNNR (VQFN-HR 18, 3.5 x 3.5, LCSC C473372). HotRod pads are NOT generic: replace with the TI RNN0018A land pattern.")
for lib, n in [("Package_DFN_QFN", "Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm"),
               ("Package_SO", "VSSOP-10_3x3mm_P0.5mm"), ("Resistor_SMD", "R_2512_6332Metric"), ("Package_TO_SOT_SMD", "SOT-23-6"), ("Package_TO_SOT_SMD", "SOT-23"), ("Package_TO_SOT_SMD", "SOT-563"), ("Package_TO_SOT_SMD", "SOT-363_SC-70-6"),
               ("Package_TO_SOT_SMD", "TDSON-8-1"), ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"),
               ("Package_SON", "Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm"),
               ("Crystal", "Crystal_SMD_3225-4Pin_3.2x2.5mm"), ("Inductor_SMD", "L_Bourns_SRP1038C_10.0x10.0mm"),
               ("Inductor_SMD", "L_1008_2520Metric"), ("Capacitor_SMD", "C_0402_1005Metric"), ("Capacitor_SMD", "C_0805_2012Metric"),
               ("Capacitor_SMD", "C_1206_3216Metric"), ("Resistor_SMD", "R_0402_1005Metric"), ("LED_SMD", "LED_0603_1608Metric")]:
    copy_sys(lib, n)
