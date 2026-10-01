#!/usr/bin/env python3
"""Generate MP62 placeholder footprints (S-expression, KiCad 9 format).
All dimensions in mm. Every footprint here is a PLACEHOLDER: outer dimensions are
from the cited drawings, pad details are approximate and MUST be re-checked
against the chosen part's customer drawing before layout."""
import os
LIB = os.path.join(os.path.dirname(__file__), "..", "MP62_Placeholders.pretty")

def eff(size=1.0, th=0.15):
    return f'(effects (font (size {size} {size}) (thickness {th})))'

def rect(x1, y1, x2, y2, layer, w=0.1):
    return f'  (fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))\n'

def line(x1, y1, x2, y2, layer, w=0.1):
    return f'  (fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (layer "{layer}"))\n'

def text(s, x, y, layer, size=0.8):
    return f'  (fp_text user "{s}" (at {x:.3f} {y:.3f} 0) (layer "{layer}") {eff(size, size*0.15)})\n'

def smd(name, x, y, w, h, shape="rect"):
    return f'  (pad "{name}" smd {shape} (at {x:.3f} {y:.3f}) (size {w:.3f} {h:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"))\n'

def npth(x, y, d):
    return f'  (pad "" np_thru_hole circle (at {x:.3f} {y:.3f}) (size {d:.3f} {d:.3f}) (drill {d:.3f}) (layers "*.Cu" "*.Mask"))\n'

def pth(name, x, y, d, pad):
    return f'  (pad "{name}" thru_hole circle (at {x:.3f} {y:.3f}) (size {pad:.3f} {pad:.3f}) (drill {d:.3f}) (layers "*.Cu" "*.Mask"))\n'

def fp(name, descr, body, attr="smd", ref_y=-7, val_y=7):
    s = f'(footprint "{name}"\n  (version 20241229)\n  (generator "mp62_make_placeholders")\n  (layer "F.Cu")\n'
    s += f'  (descr "{descr}")\n  (tags "MP62 PLACEHOLDER")\n'
    s += f'  (property "Reference" "REF**" (at 0 {ref_y} 0) (layer "F.SilkS") {eff()})\n'
    s += f'  (property "Value" "{name}" (at 0 {val_y} 0) (layer "F.Fab") {eff(0.8,0.12)})\n'
    s += f'  (attr {attr})\n' if attr else ''
    s += body + ')\n'
    with open(os.path.join(LIB, name + ".kicad_mod"), "w") as f:
        f.write(s)

# 1. CPU-board edge receptacle: PCIe CEM mechanical, x8 size (98 positions, 1.00 mm pitch), vertical SMT.
#    Outer dims: Samtec PCIE-G5 table: x8 body A = 55.40 mm, B = 57.70 mm with weld tabs;
#    TE 2337939 (x4, 64 pos) width 8.75 mm, height 11.25 mm. Pinout is MP62-custom (NOT PCIe CEM).
b = ""
L, Lw, W = 55.40, 57.70, 8.80
b += rect(-L/2, -W/2, L/2, W/2, "F.Fab")
b += rect(-Lw/2 - 0.5, -W/2 - 1.0, Lw/2 + 0.5, W/2 + 1.0, "F.CrtYd", 0.05)
b += rect(-27.3, -W/2 - 0.15, 27.3, W/2 + 0.15, "F.SilkS", 0.12)
b += text("PLACEHOLDER: CEM x8-size 98P vertical SMT, MP62 CPU-LINK pinout", 0, 0, "F.Fab", 0.7)
# 49 contacts per side; key after contact 11 (CEM convention), 2 mm extra gap
xs = []
x = -25.0
for i in range(49):
    xs.append(x)
    x += 1.0 + (2.0 if i == 10 else 0.0)
for i, xx in enumerate(xs):
    b += smd(f"A{i+1}", xx, -3.3, 0.6, 1.8)
    b += smd(f"B{i+1}", xx, 3.3, 0.6, 1.8)
b += smd("MP", -Lw/2 + 0.5, 0, 1.2, 3.0)
b += smd("MP", Lw/2 - 0.5, 0, 1.2, 3.0)
b += npth(-26.2, 0, 1.6)
b += npth(24.0, 0, 1.6)
fp("MP62_CPULINK_CEMx8_98P_Vertical_SMT_PLACEHOLDER",
   "PLACEHOLDER. PCIe CEM x8-size vertical SMT card-edge receptacle used mechanically for the MP62 CPU-LINK (custom pinout). Body 55.40 x 8.80 mm, 57.70 mm incl. weld tabs (Samtec PCIE-G5 table; TE 2337939 width). Pad geometry approximate.",
   b, ref_y=-6.5, val_y=6.5)

# 2. M.2 2242 M-key socket for the OpenCore SATA SSD, with card + standoff keep-out.
b = ""
b += rect(-2.5, -11.0, 2.5, 11.0, "F.Fab")          # socket body ~5 x 22
b += rect(2.5, -11.0, 2.5 + 42.0, 11.0, "F.Fab")     # 22 x 42 card
b += rect(-3.0, -11.5, 2.5 + 42.0 + 3.0, 11.5, "F.CrtYd", 0.05)
b += rect(-2.65, -11.15, 2.65, 11.15, "F.SilkS", 0.12)
b += text("PLACEHOLDER: M.2 M-key socket (SATA, B+M cards OK)", 22, -3, "F.Fab", 0.7)
b += text("M.2 2242 card area (no parts under card > 1.5 mm, TBD)", 22, 0, "F.Fab", 0.7)
b += text("OpenCore boot SSD (SATA0)", 22, 3, "F.Fab", 0.7)
b += smd("MP", 0, -10.2, 2.0, 1.2)
b += smd("MP", 0, 10.2, 2.0, 1.2)
for i in range(0, 37):
    yy = -9.0 + i * 0.5
    b += smd(str(i + 1), -1.2 if i % 2 == 0 else 1.2, yy, 1.4, 0.3)
b += pth("S", 2.5 + 42.0, 0, 2.2, 5.0)              # standoff / screw point (M2 SMT nut or press standoff TBD)
fp("MP62_M2_2242_MKey_SATA_PLACEHOLDER",
   "PLACEHOLDER. M.2 M-key socket + 2242 card area + standoff. Card 22 x 42 mm (M.2 spec). Socket pads approximate; choose a JLC-stocked socket (e.g. 4.2 mm or 8.5 mm height) and replace.",
   b, ref_y=-13, val_y=13)

# 3. Generic area placeholders (no pads)
def area(name, w, h, lines, descr):
    b = rect(-w/2, -h/2, w/2, h/2, "F.Fab")
    b += rect(-w/2 - 0.25, -h/2 - 0.25, w/2 + 0.25, h/2 + 0.25, "F.CrtYd", 0.05)
    b += rect(-w/2, -h/2, w/2, h/2, "F.SilkS", 0.12)
    for i, s in enumerate(lines):
        b += text(s, 0, -h/2 + 2.0 + i * 1.6, "F.Fab", 0.8)
    fp(name, descr, b, attr="smd allow_missing_courtyard", ref_y=-h/2 - 1.5, val_y=h/2 + 1.5)

area("MP62_AREA_StandbyPower_22x12_PLACEHOLDER", 22, 12,
     ["PLACEHOLDER area: STANDBY POWER", "11V_SB -> 3V3_SB buck (MCU, EEPROM)", "11V_SB -> 5V_SBY buck (COM-HPC)", "PSU_EN gate logic (interlock AND req AND !latch)", "THERM latch, HW watchdog"],
     "PLACEHOLDER area reservation for standby power and the hardware safety gate.")
area("MP62_AREA_MainPower_20x12_PLACEHOLDER", 20, 12,
     ["PLACEHOLDER area: MAIN-RAIL POWER", "12V -> 3V3_BP buck", "FACE_P / FACE_S 3V3_AUX load switches", "12V fan eFuse, INA power monitor", "12V/11V input TVS + fuse"],
     "PLACEHOLDER area reservation for main-rail (S0) power on the backplane.")

# 4. MCIO 124-pos (16i) vertical SMT receptacle, from TE 2360189 rev A1 customer drawing
#    (2X NPTH 1.30 at 40.50; 124X 0.35 x 1.20 pads at 0.60 pitch; body 42.00 x 8.62/8.77;
#    keep-out 44.75 long). Not placed on the backplane (direct topology); kept for the
#    CPU-board and face-module projects and for the hub fit check.
b = ""
b += rect(-21.0, -4.385, 21.0, 4.385, "F.Fab")
b += rect(-22.375, -6.86, 22.375, 6.86, "F.CrtYd", 0.05)
b += rect(-22.25, -4.5, 22.25, 4.5, "F.SilkS", 0.12)
b += text("PLACEHOLDER: MCIO 124P vertical (TE 2360189 / 1-2381578-9 class)", 0, 0, "F.Fab", 0.6)
# 62 contacts per row: port 1 = 37 contacts (21.60 = 36 x 0.60), 4.50 gap, port 2 = 25 contacts (14.40).
# Contact span 21.60 + 4.50 + 14.40 = 40.50 = NPTH spacing, so the end contacts sit beside the NPTHs.
xs = [-20.25 + i * 0.6 for i in range(37)] + [5.85 + i * 0.6 for i in range(25)]
for i, xx in enumerate(xs):
    b += smd(f"A{i+1}", xx, 1.50, 0.35, 1.20)    # row offsets from drawing dims 62X 1.50 / 62X 3.10 (interpreted)
    b += smd(f"B{i+1}", xx, -1.60, 0.35, 1.20)
b += npth(-20.25, 0, 1.30)
b += npth(20.25, 0, 1.30)
for (xx, yy) in [(-20.575, 3.19), (20.575, 3.19), (-21.45, -2.40), (21.45, -2.40), (3.275, 3.19)]:
    b += f'  (pad "SH" thru_hole oval (at {xx:.3f} {yy:.3f}) (size 1.10 1.60) (drill oval 0.50 1.00) (layers "*.Cu" "*.Mask"))\n'
fp("MP62_MCIO_124P_Vertical_SMT_TE2360189_PLACEHOLDER",
   "PLACEHOLDER from TE 2360189 rev A1 recommended PCB layout (124X 0.35x1.20 pads, 0.60 pitch, 2X NPTH 1.30 at 40.50, body 42.00 x 8.62, keep-out 44.75). Row pitch and shell-peg positions approximate: verify before use.",
   b, ref_y=-8, val_y=8)
print("ok")

# 5. CPU-LINK for the HUB topology: Amphenol Mini Cool Edge 0.60 mm, 224 positions, vertical SMT
#    (ME1022410103011 = with optional board lock). Dimensions from Amphenol customer drawing
#    C-ME10224101X0X1X rev A (2021-05-12): overall 85.56 mm, body 83.76 +/-0.08, recommended PCB
#    layout: 224X pads 0.35 x 1.20 at 0.60 pitch, 4 bays x 28 per row, overall pad span ~82.93,
#    keep-out >= 85.86 x 6.30, 2X NPTH 1.10 locating pegs, 4X PTH 1.10 board locks; 1.57 mm card.
#    Pad row spacing and bay offsets below are APPROXIMATE (placeholder).
b = ""
b += rect(-41.88, -3.0, 41.88, 3.0, "F.Fab")
b += rect(-42.78, -2.2, 42.78, 2.2, "F.Fab")
b += rect(-43.2, -3.75, 43.2, 3.75, "F.CrtYd", 0.05)
b += rect(-43.12, -3.15, 43.12, 3.15, "F.SilkS", 0.12)
b += text("PLACEHOLDER: Mini Cool Edge 224P vertical SMT (ME1022410103011), MP62 CPU-LINK hub pinout", 0, 0, "F.Fab", 0.6)
bay_c = [-30.45, -10.15, 10.15, 30.45]   # bay centres, pitch 20.30 (card drawing)
n = 0
for bi, bc in enumerate(bay_c[::-1]):     # A1 at the +x end (drawing: A1 mark at right)
    for k in range(28):
        xx = bc + 8.1 - k * 0.6
        n += 1
        b += smd(f"A{n}", xx, -1.425, 0.35, 1.20)
        b += smd(f"B{n}", xx, 1.425, 0.35, 1.20)
b += npth(-41.47, 0.0, 1.10)
b += npth(41.47, 0.0, 1.10)
for (xx, yy) in [(-42.2, -1.9), (-42.2, 1.9), (42.2, -1.9), (42.2, 1.9)]:
    b += pth("BL", xx, yy, 1.10, 1.6)
fp("MP62_CPULINK_MiniCoolEdge_224P_Vertical_SMT_PLACEHOLDER",
   "PLACEHOLDER. Amphenol Mini Cool Edge 0.60 mm 224-pos vertical SMT (ME1022410103011, board lock). Outer dims per Amphenol drawing CME102241010301X rev A: 85.56 overall, 83.76 body, keep-out 85.86 x 6.30. Pad rows/bay offsets approximate. Side A (row toward +y on disc) = CPU-TX lanes on L1, side B = CPU-RX lanes via to L6.",
   b, ref_y=-5.5, val_y=5.5)

# 6. Optional PCIe 5.0 linear redriver area: TI DS320PR810 (8 ch, WQFN-64 10 x 5.5 mm) + decoupling/straps.
area("MP62_AREA_Redriver_DS320PR810_12x8_PLACEHOLDER", 12, 8,
     ["OPTION (Gen5 build): DS320PR810", "8-ch linear redriver, WQFN-64 10x5.5", "flow-through, 3V3 1.3 W"],
     "PLACEHOLDER area for an optional TI DS320PR810 PCIe 5.0 linear redriver (8 one-direction channels = one x4 link, 4 TX + 4 RX; x16 needs 4 devices) plus decoupling. Not populated in the Gen4 baseline build.")
print("ok2")
