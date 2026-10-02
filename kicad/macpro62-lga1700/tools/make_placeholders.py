#!/usr/bin/env python3
"""Generate MP62 LGA1700 CPU-board (CB) footprints (KiCad 9 S-expression), mm.
Land/ball POSITIONS of U1 (LGA1700) and U2 (700-series PCH) come from Intel's PUBLIC ballout spreadsheets
(attachments of datasheets 743844 vol.1 and 743835 vol.1, extracted with pdfdetach). PAD SIZES are estimates
(Intel's recommended land sizes are in the CNDA PDG). Everything else is a PLACEHOLDER with real outer dims
where a drawing was available; pads approximate."""
import csv, os, openpyxl
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "MP62_LGA_Placeholders.pretty")
REF = "/workspace/mp62-spec-refs/lga1700"
PINOUT = os.path.join(HERE, "..", "docs", "cpulink_224_pinout_draft.csv")
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
    s = f'(footprint "{name}"\n  (version 20241229)\n  (generator "mp62_lga_make_placeholders")\n  (layer "F.Cu")\n'
    s += f'  (descr "{descr}")\n  (tags "MP62 LGA1700 PLACEHOLDER")\n'
    s += f'  (property "Reference" "REF**" (at 0 {ref_y} 0) (layer "F.SilkS") {eff()})\n'
    s += f'  (property "Value" "{name}" (at 0 {val_y} 0) (layer "F.Fab") {eff(0.8,0.12)})\n'
    s += f'  (attr {attr})\n' if attr else ''
    s += body + ')\n'
    open(os.path.join(LIB, name + ".kicad_mod"), "w").write(s)

def ballout(xlsx, hdr_row, cols):
    ws = openpyxl.load_workbook(os.path.join(REF, xlsx), read_only=True)["Pinlist"]
    out, seen = [], set()
    for r in list(ws.iter_rows(values_only=True))[hdr_row + 1:]:
        b, n, x, y = (r[c] for c in cols)
        if b is None or x is None or y is None: continue
        k = (round(float(x), 3), round(float(y), 3))
        if k in seen: continue
        seen.add(k); out.append((str(b).strip(), str(n).strip(), float(x), float(y)))
    return out

# ---------------------------------------------------------------------------------------------
# 1. LGA1700 socket land pattern. Intel 743844-001_S_LGA_Ballout.xlsx (public attachment of the 13th/14th Gen
#    desktop datasheet vol.1, 743844-015): 1706 lands, X +-21.247, Y +-17.688, 0.8 mm grid (staggered rows).
#    Local footprint coords: x = Intel X, y = -Intel Y (Intel Y up -> KiCad up). ASSUMES Intel X/Y are a top view
#    of the board footprint - VERIFY against the package/socket drawing (pin-1 corner) before layout.
#    Pad 0.45 round = [Estimate] for 0.8 mm-pitch solder-ball socket tails (Foxconn/Lotes footprint governs).
lga = ballout("743844-001_S_LGA_Ballout.xlsx", 0, (0, 1, 3, 4))
b = ""
for ball, name, x, y in lga:
    b += smd(ball, x, -y, 0.45, 0.45, "circle")
b += rect(-22.5, -18.75, 22.5, 18.75, "F.Fab", 0.12)            # package 45 x 37.5 (Intel ARK / datasheet)
b += rect(-21.6, -18.05, 21.6, 18.05, "F.Fab", 0.05)
b += rect(-24.5, -21.5, 24.5, 21.5, "F.SilkS", 0.15)            # socket housing envelope [Estimate]
b += rect(-24.75, -21.75, 24.75, 21.75, "F.CrtYd", 0.05)
b += circ(-22.0, 18.3, 0.5, "F.Fab", 0.1)
b += text("U1 LGA1700 socket (Foxconn PE17007-11NK0-1H, LCSC C38520273)", 0, -15.0, "F.Fab", 1.0)
b += text("lands from Intel 743844-001 ballout: %d lands, 0.8 grid, field 42.5 x 35.4" % len(lga), 0, -13.4, "F.Fab", 0.8)
b += text("package 45 x 37.5 (fab); housing envelope 49 x 43 = ESTIMATE, get the Foxconn drawing", 0, -12.0, "F.Fab", 0.8)
fp("MP62_LGA1700_Socket_IntelBallout_0.8", "LGA1700 socket land pattern, land positions from Intel 743844-001_S_LGA_Ballout.xlsx (%d lands). Pad size 0.45 and housing 49x43 are estimates; orientation (top vs bottom view) to be verified." % len(lga), b, ref_y=-23, val_y=23)
with open(os.path.join(HERE, "..", "docs", "u1_lga1700_lands.csv"), "w") as f:
    f.write("land,name,x_intel_mm,y_intel_mm\n")
    for r in lga: f.write("%s,%s,%.3f,%.3f\n" % r)

# 2. 700-series PCH, FCBGA 28 x 25. Intel 743835_001_Ballout.xlsx: 1045 balls, X +-13.34 (28 side), Y +-11.84,
#    0.5005 mm min pitch (staggered, typ. neighbour 0.565). Pad 0.25 round = [Estimate] (NSMD), PDG governs.
pch = ballout("743835_001_Ballout.xlsx", 1, (0, 1, 2, 3))
b = ""
for ball, name, x, y in pch:
    b += smd(ball, x, -y, 0.25, 0.25, "circle")
b += rect(-14.0, -12.5, 14.0, 12.5, "F.Fab", 0.12)
b += rect(-14.0, -12.5, 14.0, 12.5, "F.SilkS", 0.12)
b += rect(-14.5, -13.0, 14.5, 13.0, "F.CrtYd", 0.05)
b += circ(-13.4, 12.0, 0.35, "F.Fab", 0.1)
b += text("U2 PCH Z790 (FH82Z790 SRM8P) / B760 / H770: same 700-series ballout", 0, -9.0, "F.Fab", 0.9)
b += text("%d balls from Intel 743835_001 ballout, min pitch 0.50, FCBGA 28 x 25" % len(pch), 0, -7.6, "F.Fab", 0.8)
fp("MP62_PCH700_FCBGA1045_28x25_IntelBallout", "Intel 700-series PCH (B760/H770/Z790) FCBGA 28x25, ball positions from Intel 743835_001_Ballout.xlsx (%d balls). Pad 0.25 is an estimate (PDG/CNDA governs)." % len(pch), b, ref_y=-14, val_y=14)

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

# 5. SO-DIMM DDR5 RA socket UMAX 90415-4015SR (LCSC C19267513, 262P, 0.5 pitch, H 4.0) + module zone.
#    JEDEC DDR5 SO-DIMM module 69.6 x 30. Socket envelope incl. latches 78 x 32 = [Estimate] (get the UMAX drawing).
#    Local: contact row along x at y = 0, module extends toward -y (away from the contacts).
b = ""
for i in range(131):                                   # 2 staggered rows x 131 at 0.5 pitch (odd / even pins) - approximate
    b += smd(str(2 * i + 1), -32.5 + i * 0.5, 1.6, 0.25, 1.6)
    b += smd(str(2 * i + 2), -32.25 + i * 0.5, 3.6, 0.25, 1.6)
b += smd("MP1", -35.8, 1.0, 2.0, 3.0) + smd("MP2", 35.8, 1.0, 2.0, 3.0)
b += rect(-34.8, -30.0 + 4.0, 34.8, 4.0, "F.Fab", 0.12)           # module 69.6 x 30, contact edge inserted ~ at y=4
b += rect(-38.75, -26.75, 38.75, 4.75, "F.SilkS", 0.12)           # envelope 77.5 x 31.5 incl. latches [Estimate]
b += rect(-39.0, -27.0, 39.0, 5.0, "F.CrtYd", 0.05)
b += text("DDR5 SO-DIMM RA socket UMAX 90415-4015SR (H 4.0), module 69.6 x 30", 0, -14.0, "F.Fab", 1.0)
b += text("envelope 78 x 32 incl. latches = ESTIMATE; pads approximate", 0, -12.2, "F.Fab", 0.8)
fp("MP62_SODIMM_DDR5_262P_RA_UMAX_90415-4015SR", "PLACEHOLDER DDR5 SO-DIMM 262P right-angle SMT socket, UMAX 90415-4015SR (LCSC C19267513, H 4.0). Module 69.6 x 30 (JEDEC). Pads/latch envelope approximate.", b, ref_y=-28.5, val_y=6.5)

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
b += text("PLACEHOLDER M.2 M-key 2280 boot SSD (PCH PCIe Gen4 x4)", 42, -2, "F.Fab", 0.8)
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
A = [
 ("MP62_AREA_VRctrl_RT3628AE_8x8", 8, 8, ["RT3628AEGQW", "IMVP9.1 dual rail", "LCSC C3249940", "core 6ph + GT 1ph"], "Richtek RT3628AE digital multiphase controller (LCSC C3249940) + SVID/telemetry passives."),
 ("MP62_AREA_VCCCORE_OutCaps_5x66", 5, 66, ["VCCCORE out", "polymer/MLCC"], "VCCCORE output capacitors (polymer <= 2.8 mm + MLCC), front side, height <= 5.5."),
 ("MP62_AREA_12V_InCaps_5x66", 5, 66, ["12V in", "MLCC"], "12 V input MLCCs for the VCCCORE/VCCGT phases (1206/1210 25 V)."),
 ("MP62_AREA_VCCIN_AUX_2ph_28x22", 28, 22, ["VCCIN_AUX 2-phase, 33 A IccMax (35 W)", "PCH-VID set (discrete levels)", "2x SiC654 + 2x FP4 + caps", "controller TBD (2-ph, VID pins)"], "VCCIN_AUX 2-phase VR (IccMax 33 A for the 35 W 6P+8E die, datasheet 743844 Table 81)."),
 ("MP62_AREA_VCC1P05_1P8_PROC_28x14", 28, 14, ["VCC1P05_PROC (fixed) buck", "VCC1P8_PROC LDO/buck", "CPU sideband rails"], "CPU fixed rails VCC1P05_PROC and VCC1P8_PROC."),
 ("MP62_AREA_PCH_Rails_28x18", 28, 18, ["PCH VCCPRIM_CORE 0.82 V ~12 A buck", "+ 1.8 V (~2.3 A), 1.05, 3.3 primary", "DSW 3.3, RTC (VBAT_RTC from J3 / 3V3_DSW OR)", "743835 Electr_Therm Icc sheet"], "PCH rails per 743835 'Power Rail Icc' (0.82 V core 11.2 A S0 + HSIO adders; 1.8 V; 3.3 V; DSW; RTC)."),
 ("MP62_AREA_VDD2_Buck_14x8", 14, 8, ["VDD2 1.1 V DDR5 MC", "4 A (non-ECC) / 4.5 A ECC", "743844 Table 83"], "VDD2 CPU memory-controller rail buck (DDR5 1.1 V, IccMax 4 A non-ECC)."),
 ("MP62_AREA_5V_SODIMM_VINBULK_14x8", 14, 8, ["5V VIN_BULK for 2x DDR5", "SO-DIMM PMIC (on module)", "12V -> 5V buck ~4 A"], "12 V -> 5 V buck for the DDR5 SO-DIMM on-module PMICs (VIN_BULK)."),
 ("MP62_AREA_5V_DIMM_VINBULK_14x8", 14, 8, ["5V VIN_BULK for 4x DDR5 UDIMM", "PMIC on module (5 V in)", "12V -> 5V buck ~6 A"], "12 V -> 5 V buck for the 4 DDR5 UDIMM on-module PMICs (VIN_BULK), ~6 A [Estimate]."),
 ("MP62_AREA_eFuse_TPS25985_14x12", 14, 12, ["12V eFuse TPS259851 (whole CB)", "single entry, ILIM ~25 A", "+ TVS, IMON -> EC ADC"], "TI TPS259851 eFuse + TVS + ILIM/DVDT at the single 12 V entry (stock lug pair, top-left)."),
 ("MP62_AREA_Bulk12V_Back_16x30", 16, 30, ["12V bulk (BACK)", "4x 470uF 16V polymer", "(too tall for the front)"], "12 V bulk polymer capacitors - on the back because 16 V polymer cans exceed the 6.0 mm front limit."),
 ("MP62_AREA_EC_RP2350_14x12", 14, 12, ["EC: RP2350 QFN-60 7x7", "(LCSC C42411118) + QSPI + 12M", "power sequencing / fan demand / SMBus", "RSMRST#, PWRBTN#, SLP_Sx#, PWROKs"], "Embedded controller RP2350 (no eSPI; GPIO sequencing), its QSPI flash and 12 MHz crystal."),
 ("MP62_AREA_BIOS_SPI_W25Q256_10x8", 10, 8, ["BIOS SPI 32 MB", "W25Q256JV class", "+ SOIC clip / TC2050"], "PCH SPI0 flash 256 Mbit (descriptor + ME + coreboot/EDK2/OpenCore) and an external programming header."),
 ("MP62_AREA_TPM_Header_10x6", 10, 6, ["SPI TPM header", "(SPI0 CS2#)"], "SPI TPM 2.0 header (optional)."),
 ("MP62_AREA_CLK_XTAL_10x6", 10, 6, ["PCH 38.4 MHz XTAL", "+ 32.768 kHz RTC"], "PCH crystals: 38.4 MHz main and 32.768 kHz RTC."),
 ("MP62_AREA_HDA_ALC897_DNP_10x10", 10, 10, ["DNP: ALC897 HDA codec", "LQFP-48 7x7 LCSC C5884442", "(rev-A default = USB audio)"], "Optional HDA codec Realtek ALC897-VA2-CG (LCSC C5884442); rev-A default is USB audio on the IOB."),
 ("MP62_AREA_J3_MCIO_RA_IOB_44x12", 44, 12, ["J3 IOB-HS: MCIO 124 RA (BACK)", "USB3 x10, USB2 x1, 2x i226 PCIe x1, DDI-B x4 + DDI-C x2", "VBAT_RTC in, USB_OC#; > 6.0 tall -> back"], "IOB high-speed connector (MCIO 124 right-angle, Amphenol G97R24332HR / Molex 2173463021 class, same part as IOB HS1) on the back; host-end pinout docs/mp62-cb-j3_mcio124_host-end.csv (IOB HS1 v0.2 with rows A/B swapped)."),
 ("MP62_AREA_BT1_CR2032_22x16", 22, 16, ["BT1 CR2032 holder: DNP", "VBAT_RTC comes from the IOB (J3)", "fit only for bench use w/o IOB"], "RTC coin cell holder CR2032 (back), DNP by default: the RTC cell is on the IOB (BT1) and arrives on J3 B26."),
 ("MP62_AREA_DebugHdr_12x5", 12, 5, ["Debug: PCH UART0 +", "EC SWD + POST LEDs"], "Debug header: PCH LPSS UART (coreboot console), EC SWD, status LEDs."),
 ("MP62_AREA_PEG_ACcaps_70x8", 70, 8, ["PCIe AC caps (CPU PEG x16 Gen5 -> Face P, CPU x4 Gen4 -> Face S)", "0201 caps on the TX pairs near J1 (side B front / A back)"], "AC coupling caps for the TX lanes before the CPU-LINK fingers."),
]
for a in A:
    area(*a)
print("placeholders ok: LGA lands %d, PCH balls %d" % (len(lga), len(pch)))
