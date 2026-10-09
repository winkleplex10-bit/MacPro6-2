#!/usr/bin/env python3
"""Generate MP62 AM5 CPU-board (CB, DRAFT) footprints (KiCad 9 S-expression), mm.
Derived from kicad/macpro62-lga1700/tools/make_placeholders.py (power stage, inductor, DIMM socket, CPU-LINK fingers,
holes, lugs, M.2, area placeholders copied unchanged). NEW for AM5: U1 LGA1718 socket placeholder, U2 PROM21
FCBGA placeholder, SVI3 controller, USB 10G hub and AM5 rail areas.
AMD's AM5 land map, socket footprint and PROM21 ballout are NDA: those land/ball POSITIONS ARE SYNTHETIC
PLACEHOLDERS (correct pitch/outline class only). Do not fabricate."""
import csv, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "MP62_AM5_Placeholders.pretty")
PINOUT = os.path.join(HERE, "..", "docs", "cpulink_224_pinout_am5.csv")
os.makedirs(LIB, exist_ok=True)
def eff(size=1.0, th=0.15):
    return f'(effects (font (size {size} {size}) (thickness {th})))'
def rect(x1, y1, x2, y2, layer, w=0.1):
    return f'  (fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))\n'
def line(x1, y1, x2, y2, layer, w=0.1):
    return f'  (fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (layer "{layer}"))\n'
def circ(x, y, r, layer, w=0.1):
    return f'  (fp_circle (center {x:.3f} {y:.3f}) (end {x + r:.3f} {y:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))\n'
def text(s, x, y, layer, size=0.8):
    return f'  (fp_text user "{s}" (at {x:.3f} {y:.3f} 0) (layer "{layer}") {eff(size, size*0.15)})\n'
def smd(name, x, y, w, h, shape="rect", side="F", paste=True):
    lay = f'"{side}.Cu" "{side}.Paste" "{side}.Mask"' if paste else f'"{side}.Cu" "{side}.Mask"'
    return f'  (pad "{name}" smd {shape} (at {x:.3f} {y:.3f}) (size {w:.3f} {h:.3f}) (layers {lay}))\n'
def npth(x, y, d):
    return f'  (pad "" np_thru_hole circle (at {x:.3f} {y:.3f}) (size {d:.3f} {d:.3f}) (drill {d:.3f}) (layers "*.Cu" "*.Mask"))\n'
def pth(name, x, y, d, pad):
    return f'  (pad "{name}" thru_hole circle (at {x:.3f} {y:.3f}) (size {pad:.3f} {pad:.3f}) (drill {d:.3f}) (layers "*.Cu" "*.Mask"))\n'
def fp(name, descr, body, attr="smd", ref_y=-7, val_y=7):
    s = f'(footprint "{name}"\n  (version 20241229)\n  (generator "mp62_am5_make_placeholders")\n  (layer "F.Cu")\n'
    s += f'  (descr "{descr}")\n  (tags "MP62 AM5 PLACEHOLDER")\n'
    s += f'  (property "Reference" "REF**" (at 0 {ref_y} 0) (layer "F.SilkS") {eff()})\n'
    s += f'  (property "Value" "{name}" (at 0 {val_y} 0) (layer "F.Fab") {eff(0.8,0.12)})\n'
    s += f'  (attr {attr})\n' if attr else ''
    s += body + ')\n'
    open(os.path.join(LIB, name + ".kicad_mod"), "w").write(s)

# 3. Power stage Vishay SiC654CD (PowerPAK MLP55-31L, 5 x 5), 50 A. Simplified pads (VIN / PGND / SW + signal row).
b = smd("VIN", -1.45, -0.55, 1.6, 1.7) + smd("PGND", -1.45, 1.4, 1.6, 1.6) + smd("SW", 1.25, 0.5, 2.0, 3.0)
for i in range(7):
    b += smd(str(i + 1), -2.1 + i * 0.6, -2.2, 0.3, 0.5)
b += rect(-2.5, -2.5, 2.5, 2.5, "F.Fab") + rect(-2.75, -2.75, 2.75, 2.75, "F.CrtYd", 0.05) + circ(-2.2, -2.9, 0.15, "F.SilkS", 0.1)
fp("MP62_PowerStage_SiC654_MLP55-31L_5x5", "PLACEHOLDER Vishay SiC654CD-T1-GE3 50 A smart power stage, PowerPAK MLP55-31L 5x5 (LCSC C1852094). Pads simplified - use the Vishay land pattern.", b, ref_y=-3.6, val_y=3.6)

# 4. Inductor Eaton FLAT-PAC FP4-150-R: 10.2 max x 6.8 max x 5.00 max, 0.15 uH 42 A; pads approx (2x 2.5 x 4.5, 10.5 span).
b = smd("1", -4.0, 0, 2.5, 4.5) + smd("2", 4.0, 0, 2.5, 4.5)
b += rect(-5.1, -3.4, 5.1, 3.4, "F.Fab") + rect(-5.6, -3.65, 5.6, 3.65, "F.CrtYd", 0.05) + line(-1.5, -3.45, 1.5, -3.45, "F.SilkS", 0.12) + line(-1.5, 3.45, 1.5, 3.45, "F.SilkS", 0.12)
b += text("FP4 h5.0", 0, 0, "F.Fab", 0.7)
fp("MP62_IND_Eaton_FP4_10.2x6.8x5.0", "Eaton FLAT-PAC FP4-150-R 0.15 uH 42 A, 10.2 x 6.8 x 5.00 max (Eaton datasheet Apr 2022). Pads approximate.", b, ref_y=-4.4, val_y=4.4)
# 5b. DDR5 UDIMM 288P VERTICAL SMT socket, UMAX 90414 series (drawing C-90414 rev 3, LCSC datasheet of C2922443).
#     0.85 pitch, 2 rows; key 1.425 right of the socket centre; pins 1..75 / 145..219 left of the key (1.85 + 74 x 0.85 = 64.75),
#     76..144 / 220..288 right (4.10 + 68 x 0.85 = 61.90). Boardlock pegs D2.45 at key -70.40 / +67.55.
#     Body width 6.30 (6.5 max), height 21.30 max, module seating plane <= 2.0 -> module top <= 2.0 + 31.25 = 33.25.
#     Latch envelope (sheet 4): SHORT latch closed 142.0 / open 151.5 / keep-out 152.0; LONG (LCSC C2922443 = -21) 147.5 / 158.5 / 162.0.
#     Row-to-row 3.0 (TE 1-2355626-1 data); pad 0.52 x 2.05 (UMAX detail A). Local: long axis = x, centre = body centre.
b = ""
KEY = 1.425
for k in range(75):
    x = KEY - 1.85 - (74 - k) * 0.85
    b += smd(str(k + 1), x, 1.5, 0.52, 2.05) + smd(str(k + 145), x, -1.5, 0.52, 2.05)
for k in range(69):
    x = KEY + 4.10 + k * 0.85
    b += smd(str(k + 76), x, 1.5, 0.52, 2.05) + smd(str(k + 220), x, -1.5, 0.52, 2.05)
b += npth(KEY - 70.40, 0, 2.45) + npth(KEY + 67.55, 0, 2.45)
b += rect(-70.85, -3.15, 70.85, 3.15, "F.Fab", 0.12)                 # body 141.7 x 6.30
b += rect(-71.0, -3.25, 71.0, 3.25, "F.SilkS", 0.12)                 # short latch closed 142.0 x 6.5 max
b += rect(-71.25, -3.5, 71.25, 3.5, "F.CrtYd", 0.05)
b += rect(-76.0, -3.25, 76.0, 3.25, "Dwgs.User", 0.08)               # latch-open keep-out (DIM A short = 152)
b += rect(-66.675, -2.025, 66.675, 2.025, "F.Fab", 0.08)             # module 133.35 x 4.05 max thick (MO-329 / C-90414 sheet 2)
b += line(KEY, -3.25, KEY, 3.25, "F.Fab", 0.1)
b += text("DDR5 UDIMM 288P VERT SMT, UMAX 90414 short latch (closed 142 / open 152)", 0, -5.0, "F.Fab", 0.9)
b += text("module 133.35 x 31.25 (x 4.05 max) stands 33.25 max off the board; key", KEY + 9, 0, "F.Fab", 0.6)
fp("MP62_DIMM_DDR5_288P_Vert_UMAX_90414_ShortLatch", "DDR5 UDIMM 288-pin 0.85 mm vertical SMT socket, UMAX 90414 series (drawing C-90414 rev 3): body 141.7 x 6.30, height 21.3, seating plane <= 2.0. Short latch: closed 142.0, open 151.5, keep-out 152.0 (Dwgs). LCSC stocks the long-latch C2922443 (90414-15011-21, closed 147.5) - order the short-latch code. Pads per drawing detail A (0.52 x 2.05), rows +-1.5.", b, ref_y=-6.5, val_y=6.5)

# 6. CPU-LINK fingers (identical to the carrier; Amphenol CME102241010301X rev A p.2). See carrier make_placeholders.py.
def offA(n):
    bay = (n - 1) // 28; k = (n - 1) % 28
    return [38.96, 17.85, -2.36, -22.575][bay] - 0.6 * k
rows = {r["pin"]: r["signal"] for r in csv.DictReader(open(PINOUT))}
b = ""
for n in range(1, 113):
    for side, layer in (("A", "B"), ("B", "F")):
        pin = f"{side}{n}"; sig = rows[pin]
        x = -offA(n) + (0.27 if side == "B" else 0.0)
        y0 = 0.88 if sig == "GND" else (1.68 if sig.startswith("CC_PRSNT") else 1.28)
        b += smd(pin, x, -(y0 + 3.0) / 2, 0.38, 3.0 - y0, "rect", layer, paste=False)
b += rect(-39.945, -11.26, 39.945, 0.0, "F.Fab", 0.08)
b += text("CPU-LINK 224 card edge: front = side B (host RX), back = side A (host TX); A1/B1 at -x", 0, -8.5, "F.Fab", 0.8)
fp("MP62_CPULINK_MiniCoolEdge224_CardEdge_Fingers", "CPU-LINK edge fingers for Amphenol Mini Cool Edge 224 (ME1022410103011), per Amphenol recommended AIC card (CME102241010301X rev A). Same as the CC carrier.", b, attr="smd", ref_y=-12.5, val_y=-13.8)

# 7. Holes
b = pth("1", 0, 0, 5.0, 9.0) + circ(0, 0, 4.2, "F.Fab") + circ(0, 0, 5.0, "F.CrtYd", 0.05)
b += text("CORE MOUNT D5 (stock 69.5 x 55) - FIXED", 0, 6.2, "F.Fab", 0.7)
fp("MP62_CB_CoreMountHole_D5.0_Pad9", "Stock MacPro6,2 CPU-board heatsink/thermal-core hole D5.0, plated GND ring 9.0. Fixed position (69.5 x 55).", b, attr="", ref_y=-6, val_y=7.4)
b = npth(0, 0, 3.4) + circ(0, 0, 2.9, "F.CrtYd", 0.05) + circ(0, 0, 2.8, "F.Fab") + circ(0, 0, 2.8, "B.Fab")
fp("MP62_CB_FrameSeatScrew_D3.4_NPTH", "MP62 contact-frame seating screw (M3 / #6-32) clearance D3.4 NPTH into a PEM nut in the MP62 backplate. Own pattern (free).", b, attr="", ref_y=-3.6, val_y=3.6)
b = smd("1", 0, 0, 8.0, 6.0) + smd("1", 0, 0, 8.0, 6.0, side="B")
for xx in (-2.25, 2.25):                 # stock lug = U-shaped copper strip, 2 x 2 soldered pins per lug (back photo 2026-10-01) [Estimate]
    for yy in (-1.35, 1.35):
        b += pth("1", xx, yy, 1.3, 2.0)
b += rect(-4.3, -3.3, 4.3, 3.3, "F.CrtYd", 0.05) + text("12V/GND LUG (stock bus-bar, single left entry) - polarity TBD", 0, -4.0, "F.Fab", 0.6)
fp("MP62_CB_BusBarLug_8x6_PLACEHOLDER", "PLACEHOLDER 12 V / GND bus-bar lug landing at the stock positions (one pair, top-left, CPU-side view; photo 2026-10-01). 2x2 pins [Estimate]. Polarity TBD (M-CC7).", b, attr="", ref_y=4.3, val_y=5.6)

# 8. M.2 2280 M-key (back) - same as the carrier placeholder.
b = rect(-2.5, -11.0, 2.5, 11.0, "F.Fab") + rect(2.5, -11.0, 2.5 + 80.0, 11.0, "F.Fab")
b += rect(-3.0, -11.5, 2.5 + 80.0 + 3.0, 11.5, "F.CrtYd", 0.05) + rect(-2.65, -11.15, 2.65, 11.15, "F.SilkS", 0.12)
b += text("PLACEHOLDER M.2 M-key 2280 boot SSD (CPU GPP PCIe Gen4 x4)", 42, -2, "F.Fab", 0.8)
b += smd("MP", 0, -10.2, 2.0, 1.2) + smd("MP", 0, 10.2, 2.0, 1.2)
for i in range(67):
    b += smd(str(i + 1), -1.2 if i % 2 == 0 else 1.2, -8.25 + i * 0.25, 1.4, 0.2)
b += pth("S", 2.5 + 80.0 - 1.5, 0, 2.2, 5.0)
fp("MP62_CB_M2_2280_MKey_PLACEHOLDER", "PLACEHOLDER M.2 M-key socket + 2280 card zone + standoff. Pads approximate.", b, ref_y=-13, val_y=13)

# 9. Generic area placeholders (no pads), real outer size where a part is chosen
def area(name, w, h, lines, descr):
    b = rect(-w/2, -h/2, w/2, h/2, "F.Fab") + rect(-w/2 - 0.25, -h/2 - 0.25, w/2 + 0.25, h/2 + 0.25, "F.CrtYd", 0.05)
    b += rect(-w/2, -h/2, w/2, h/2, "F.SilkS", 0.12)
    for i, s in enumerate(lines):
        b += text(s, 0, -h/2 + 1.4 + i * 1.15, "F.Fab", 0.6)
    fp(name, descr, b, attr="smd allow_missing_courtyard", ref_y=-h/2 - 1.3, val_y=h/2 + 1.3)

# ---------------------------------------------------------------------------------------------
# A1. U1 Socket AM5 (LGA1718) PLACEHOLDER land pattern.
#     [Sourced: Lotes socket brochure E1 230131, "Socket AM5 (LGA1718)": pitch 0.81 (X) x 0.94 (Y), 1718 contacts,
#     SMT solder ball, 1.4 A/contact; ILM (TFLM) AZIF0002 with 6-32 screws 10.3 kgf.cm, back plate AHSK0001.]
#     0.94 x sin(60 deg) = 0.814, i.e. a hexagonal field: 0.94 along local y in each column, columns 0.81 apart,
#     odd columns offset 0.47. Package 40 x 40 [Sourced: AMD/press]. The land MAP (which lands exist, names, keep-out
#     voids) is AMD NDA -> positions below are SYNTHETIC (field +-17.8 x +-18.8, central void, corners trimmed to 1718).
#     Pad 0.50 round and housing 46.5 x 46.5 are [Estimate]. DO NOT FABRICATE from this footprint.
pts = []
for i in range(-22, 23):
    x = i * 0.81
    off = 0.47 if i % 2 else 0.0
    for j in range(-20, 21):
        y = off + j * 0.94
        if abs(y) > 18.85: continue
        if abs(x) < 4.5 and abs(y) < 4.3: continue          # central cavity (land-side caps) [Estimate]
        pts.append((x, y))
pts.sort(key=lambda p: (max(abs(p[0]) / 17.82, abs(p[1]) / 18.35) + 0.15 * (abs(p[0]) + abs(p[1])) / 36.0, p))
pts = sorted(pts[:1718], key=lambda p: (round(p[0], 3), round(p[1], 3)))
assert len(pts) == 1718, len(pts)
cols = sorted(set(round(p[0], 3) for p in pts))
b = ""
for (x, y) in pts:
    ci = cols.index(round(x, 3)); nm = "C%02dR%02d" % (ci, int(round((y + 18.85) / 0.47)))
    b += smd(nm, x, -y, 0.50, 0.50, "circle")
with open(os.path.join(HERE, "..", "docs", "u1_am5_lands_PLACEHOLDER.csv"), "w") as f:
    f.write("# SYNTHETIC AM5 land field (NOT the AMD land map - NDA). pitch 0.81 x 0.94 hex [Lotes]; footprint-local mm, +y up\n")
    f.write("land,x_mm,y_mm,assignment\n")
    for (x, y) in pts:
        ci = cols.index(round(x, 3))
        f.write("C%02dR%02d,%.3f,%.3f,UNASSIGNED (NDA)\n" % (ci, int(round((y + 18.85) / 0.47)), x, y))
b += rect(-20.0, -20.0, 20.0, 20.0, "F.Fab", 0.12)                 # package 40 x 40
b += rect(-23.0, -23.0, 23.0, 23.0, "F.SilkS", 0.15)               # socket housing envelope [Estimate]
b += rect(-23.25, -23.25, 23.25, 23.25, "F.CrtYd", 0.05)
b += line(-23.0, 19.5, -19.5, 23.0, "F.SilkS", 0.15)               # pin-1 corner mark (orientation TBD)
b += circ(-19.0, 19.0, 0.6, "F.Fab", 0.1)
b += text("U1 Socket AM5 LGA1718 PLACEHOLDER (Foxconn PE17181-11AJ0-1H / PE17186 / Lotes AZIFS055)", 0, -16.0, "F.Fab", 0.9)
b += text("1718 SYNTHETIC lands, hex 0.81 x 0.94 (Lotes); AMD land map NDA - DO NOT FAB", 0, -14.6, "F.Fab", 0.8)
b += text("package 40 x 40; housing 46 x 46 = ESTIMATE; get the socket vendor drawing", 0, -13.2, "F.Fab", 0.8)
for (sx, sy) in ((-27, -45), (27, -45), (-27, 45), (27, 45)):      # stock AM4/AM5 cooler pattern 54 x 90 (reference only)
    b += circ(sx, sy, 2.0, "Dwgs.User", 0.1)
b += rect(-27, -45, 27, 45, "Dwgs.User", 0.05)
b += text("stock AM5 cooler 54 x 90 (NOT drilled; MP62 frame on the 69.5 x 55 core holes)", 0, -46.5, "Dwgs.User", 0.8)
fp("MP62_AM5_LGA1718_Socket_PLACEHOLDER_Hex0.81x0.94",
   "PLACEHOLDER Socket AM5 (LGA1718) footprint: 1718 SYNTHETIC land positions on the sourced hex pitch 0.81 x 0.94 (Lotes); package 40x40; pad 0.50 and housing 46x46 estimated. The AMD land map and socket footprint are NDA - replace before layout.", b, ref_y=-24.5, val_y=24.5)

# A2. U2 PROM21 chipset (B650/B850/X870 class), FCBGA 19 x 19 [Sourced: cost study sec. 10, wepc/geerlingguy #818].
#     Ball count and pitch are NOT public: 22 x 22 at 0.80 (484) is a SYNTHETIC placeholder. 218-0891025 preferred.
b = ""
for i in range(22):
    for j in range(22):
        b += smd("%s%d" % ("ABCDEFGHJKLMNPRTUVWYAAAB"[i], j + 1), -8.4 + i * 0.8, -8.4 + j * 0.8, 0.40, 0.40, "circle")
b += rect(-9.5, -9.5, 9.5, 9.5, "F.Fab", 0.12) + rect(-9.5, -9.5, 9.5, 9.5, "F.SilkS", 0.12) + rect(-10.0, -10.0, 10.0, 10.0, "F.CrtYd", 0.05)
b += circ(-8.9, -8.9, 0.3, "F.Fab", 0.1)
b += text("U2 AMD PROM21 218-0891025 (X870-marked, pref.) / 218-0891018 (B650)", 0, -6.5, "F.Fab", 0.7)
b += text("FCBGA 19 x 19; 484 SYNTHETIC balls 0.8 - ballout NDA", 0, -5.4, "F.Fab", 0.7)
fp("MP62_PROM21_FCBGA_19x19_PLACEHOLDER",
   "PLACEHOLDER AMD Promontory 21 (PROM21) chipset FCBGA 19x19 (~7 W). Ball count/pitch unknown (NDA): 22x22 at 0.80 is synthetic. Replace before layout.", b, ref_y=-11, val_y=11)

# A3. Area placeholders (no pads)
def area(name, w, h, lines, descr):
    b = rect(-w/2, -h/2, w/2, h/2, "F.Fab") + rect(-w/2 - 0.25, -h/2 - 0.25, w/2 + 0.25, h/2 + 0.25, "F.CrtYd", 0.05)
    b += rect(-w/2, -h/2, w/2, h/2, "F.SilkS", 0.12)
    for i, s in enumerate(lines):
        b += text(s, 0, -h/2 + 1.4 + i * 1.15, "F.Fab", 0.6)
    fp(name, descr, b, attr="smd allow_missing_courtyard", ref_y=-h/2 - 1.3, val_y=h/2 + 1.3)
A = [
 ("MP62_AREA_SVI3_Ctrl_RAA229139_6x6", 8, 8, ["SVI3 3-rail controller", "RAA229139 (6+1+1 / 5+2+1)", "alt MP2857 / uP9533P", "VDDCR 5 + SOC 2 + MISC 1"], "AMD SVI3 digital multiphase controller, triple output: Renesas RAA229139 (X+Y+Z <= 8, rail1 <= 3, rail2 <= 2, Type II on rail 2; short-form DS). Alternates: MPS MP2857 (3-rail, rail C), uPI uP9533P (8+2+1). RAA229621 / XDPE192C3B are dual-rail -> separate VDD_MISC loop. Config tools NDA."),
 ("MP62_AREA_VDDCR_OutCaps_5x75", 5, 75, ["VDDCR / SOC / MISC out", "polymer <= 2.8 + MLCC"], "SVI3 rail output capacitors (polymer <= 2.8 mm + MLCC), front, height <= 5.5."),
 ("MP62_AREA_12V_InCaps_5x75", 5, 75, ["12V in", "MLCC"], "12 V input MLCCs for the 8 SVI3 phases (1206/1210 25 V)."),
 ("MP62_AREA_CPU_S5_Rails_28x22", 28, 22, ["CPU always-on / S5 rails (from 5V_SBY):", "VDD_18_S5, VDD_33_S5, VDD_MISC_S5 (USB PHY)", "VDD_18 / VDD_33 (S0 load switches)", "values + currents: AMD AM5 datasheet (NDA)"], "AM5 CPU auxiliary rails (names from public AM5 rail lists [Unverified]); bucks/LDOs from 5V_SBY and 3V3_SB."),
 ("MP62_AREA_CPU_Seq_Misc_28x14", 28, 14, ["SVI3 bus pull-ups, PWROK/RSMRST logic", "48 MHz CPU clock buffer area", "FCH strap resistors (boot ROM, SPI)"], "CPU support: SVI3 bus pull-ups, power-good combiner, strapping, clock."),
 ("MP62_AREA_PROM21_Rails_28x18", 28, 18, ["PROM21 rails (~7 W total):", "core ~0.9-1.0 V buck (~6 A est.)", "1.8 V + 3.3 V + PHY rails", "values: AMD (NDA) [Estimate]"], "PROM21 supply rails [Estimate]; core buck from 12 V or 5 V."),
 ("MP62_AREA_VDDIO_MEM_Buck_14x8", 14, 8, ["VDDIO_MEM_S3 1.1 V", "DDR5 PHY (2 ch, 2DPC)", "~4-6 A [Estimate]"], "CPU memory PHY rail VDDIO_MEM_S3 (DDR5 1.1 V) buck [Estimate current]."),
 ("MP62_AREA_5V_DIMM_VINBULK_14x8", 14, 8, ["5V VIN_BULK for 4x DDR5 UDIMM", "PMIC on module (5 V in)", "12V -> 5V buck ~6 A"], "12 V -> 5 V buck for the 4 DDR5 UDIMM on-module PMICs (VIN_BULK), ~6 A [Estimate]."),
 ("MP62_AREA_PwrMon_INA228_10x6", 10, 6, ["U15 INA228 12V power mon", "0x45 on I2C0, RS1 0.5 mR 2512", "ALERT -> PWR_ALERT# (A105)"], "TI INA228 power monitor on the CB 12 V input (after U11), 0.5 mOhm Kelvin shunt RS1; I2C0 0x45; ALERT wired-OR with U11 FLT# onto CPU-LINK PWR_ALERT# (same as LGA1700)."),
 ("MP62_AREA_eFuse_TPS25985_14x12", 14, 12, ["12V eFuse TPS259851 (whole CB)", "single entry, ILIM ~25 A", "+ TVS, IMON -> EC ADC"], "TI TPS259851 eFuse + TVS at the single 12 V entry (stock lug pair, top-left); same as LGA1700."),
 ("MP62_AREA_Bulk12V_Back_16x30", 16, 30, ["12V bulk (BACK)", "4x 470uF 16V polymer", "(too tall for the front)"], "12 V bulk polymer capacitors on the back (16 V cans exceed the 6.0 mm front limit)."),
 ("MP62_AREA_EC_RP2350_14x12", 14, 12, ["EC: RP2350 QFN-60 7x7", "(LCSC C42411118) + QSPI + 12M", "AM5: RSMRST_L, PWR_BTN_L, SLP_S3/S5_L", "PWR_GOOD, SVI3 VR enable, fan demand"], "Embedded controller RP2350 (GPIO sequencing for AM5: RSMRST_L, PWR_GOOD, SLP_S3_L/SLP_S5_L, PWR_BTN_L), its QSPI flash and 12 MHz crystal."),
 ("MP62_AREA_BIOS_SPI_W25Q256_10x8", 10, 8, ["FCH SPI ROM 32 MB", "W25Q256JV class (coreboot/openSIL", "+ PSP blobs) + SOIC clip / TC2050"], "CPU (FCH) SPI ROM 256 Mbit: Dasharo coreboot + openSIL phoenix_poc + PSP firmware; external programming header."),
 ("MP62_AREA_PROM21_SPI_8x6", 8, 6, ["PROM21 SPI flash", "(own FW image, from", "a retail BIOS)"], "PROM21 own SPI firmware flash (image extracted from a retail BIOS per the AIC developer [Unverified])."),
 ("MP62_AREA_TPM_Header_10x6", 10, 6, ["SPI TPM header", "(FCH SPI CS TBD)"], "SPI TPM 2.0 header (optional; AM5 also has fTPM)."),
 ("MP62_AREA_CLK_XTAL_10x6", 10, 6, ["CPU 48 MHz XTAL", "+ 32.768 kHz RTC"], "AM5 FCH crystals: 48 MHz main [Unverified frequency] and 32.768 kHz RTC."),
 ("MP62_AREA_USB10G_Hub_VL822_14x12", 14, 12, ["U16 USB 3.2 Gen2 hub VL822-Q7", "QFN-76 9x9 (LCSC C42419379)", "UP: PROM21 10G #4 -> DS1-4 = J3 A1-A4", "+ SPI flash, 25 MHz XTAL"], "VIA Labs VL822-Q7 USB 3.2 Gen2 (10 Gb/s) 1-to-4 hub, QFN-76 9x9 (LCSC C42419379); makes the 9th/10th 10G port for the IOB (A1-A4 share one 10 Gb/s uplink). Alt: Genesys GL3590 (QFN-76/88)."),
 ("MP62_AREA_HDA_ALC897_DNP_10x10", 10, 10, ["DNP: ALC897 HDA codec", "LQFP-48 7x7 LCSC C5884442", "(rev-A default = USB audio)"], "Optional HDA codec (FCH AZ); rev-A default is USB audio on the IOB."),
 ("MP62_AREA_J3_MCIO_RA_IOB_44x12", 44, 12, ["J3 IOB-HS: MCIO 124 RA (BACK)", "AM5 map: docs/mp62-cb-j3_mcio124_host-end_am5.csv", "physical + IOB end unchanged"], "IOB high-speed connector (MCIO 124 right-angle, same part/position as the LGA1700 CB) on the back; AM5 host-end sources in docs/mp62-cb-j3_mcio124_host-end_am5.csv."),
 ("MP62_AREA_BT1_CR2032_22x16", 22, 16, ["BT1 CR2032 holder: DNP", "VBAT_RTC comes from the IOB (J3)", "fit only for bench use w/o IOB"], "RTC coin cell holder CR2032 (back), DNP by default (VBAT_RTC from the IOB on J3)."),
 ("MP62_AREA_DebugHdr_12x5", 12, 5, ["Debug: FCH UART +", "EC SWD + POST code (port 80)"], "Debug header: FCH UART (coreboot console), EC SWD, status LEDs."),
 ("MP62_AREA_PEG_ACcaps_70x8", 70, 8, ["PCIe AC caps: CPU GFX x8 (x16 for 7000/9000) -> Face P,", "CPU GPP x4 -> Face S; 0201 220 nF near J1"], "AC coupling caps for the CPU TX lanes before the CPU-LINK fingers (all 16 GFX lanes fitted for the 7000/9000 option)."),
]
for a in A:
    area(*a)
print("AM5 placeholders ok: U1 %d synthetic lands, U2 484 synthetic balls, %d areas" % (len(pts), len(A)))
