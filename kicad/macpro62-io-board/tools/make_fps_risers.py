"""New footprints for D-IO14 risers, D-IO15 RJ45 and the CONN_C fan+AirPort connector (2026-10-02 ~10:40 ET).
All PLACEHOLDER land patterns: dimensions from catalogue tables; replace with the vendor drawing before fab."""
import os, sys
OUT = [sys.argv[1]] if len(sys.argv) > 1 else ["/workspace/kicad/macpro62-io-board/MP62_IO.pretty", "/workspace/kicad/macpro62-io-risers/MP62_RISER.pretty"]
def hdr(name, descr, attr="smd"):
    return ['(footprint "%s"' % name, '  (version 20241229)', '  (generator "mp62_io")', '  (layer "F.Cu")', '  (descr "%s")' % descr,
            '  (property "Reference" "REF**" (at 0 -1 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
            '  (property "Value" "%s" (at 0 1 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))' % name, '  (attr %s)' % attr]
def rect(x0, y0, x1, y1, layer, w=0.05):
    return '  (fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width %.2f) (type solid)) (fill no) (layer "%s"))' % (x0, y0, x1, y1, w, layer)
def smd(num, x, y, w, h, shape="roundrect"):
    rr = ' (roundrect_rratio 0.25)' if shape == "roundrect" else ""
    return '  (pad "%s" smd %s (at %.3f %.3f) (size %.3f %.3f) (layers "F.Cu" "F.Paste" "F.Mask")%s)' % (num, shape, x, y, w, h, rr)
def npth(x, y, d):
    return '  (pad "" np_thru_hole circle (at %.3f %.3f) (size %.3f %.3f) (drill %.3f) (layers "*.Cu" "*.Mask"))' % (x, y, d, d, d)
def pth(num, x, y, d, ring):
    return '  (pad "%s" thru_hole circle (at %.3f %.3f) (size %.3f %.3f) (drill %.3f) (layers "*.Cu" "*.Mask"))' % (num, x, y, ring, ring, d)
FP = {}
def dual_row(name, n, pitch, row, pw, pl, body, descr, extra=()):
    L = hdr(name, descr); half = n // 2; span = (half - 1) * pitch
    for i in range(half):
        x = -span / 2 + i * pitch
        L.append(smd(str(2 * i + 1), x, row / 2, pw, pl)); L.append(smd(str(2 * i + 2), x, -row / 2, pw, pl))
    L += list(extra)
    bx, by = body; L.append(rect(-bx / 2, -by / 2, bx / 2, by / 2, "F.Fab", 0.1))
    cx, cy = max(bx, span + pw) / 2 + 0.3, max(by, row + pl) / 2 + 0.3; L.append(rect(-cx, -cy, cx, cy, "F.CrtYd"))
    FP[name] = L + [")"]
# Hirose DF40C receptacle (0.4 mm, mated 1.5 with DF40C-xxDP): pads 0.23 x 0.8, row centres 3.2 [PLACEHOLDER: check the DF40 drawing]; body A = 0.4*(n/2-1)+2.6 (approx)
for n in (80, 50, 40):
    dual_row("MP62_Hirose_DF40C-%dDS-0.4V_PLACEHOLDER" % n, n, 0.4, 3.2, 0.23, 0.8, (0.4 * (n / 2 - 1) + 2.6, 3.4),
             "Hirose DF40C-%dDS-0.4V(51) receptacle, 0.4 mm, %d pos, mated 1.5 mm with DF40C-%dDP plug on the riser flex jumper. Rated per Hirose to 16+ Gbps class (USB 3.2 Gen2 / DP HBR3) with GND-signal-signal-GND pinning. PLACEHOLDER lands." % (n, n, n),
             extra=[smd("MP1", -(0.4 * (n / 2 - 1) / 2 + 1.0), 0, 0.5, 1.0), smd("MP2", 0.4 * (n / 2 - 1) / 2 + 1.0, 0, 0.5, 1.0)])
# Hirose DF12 40 pos receptacle (stock fan + AirPort press connector match: 2 x 20 @ 0.5, A 12.1 / B 9.5 per Hirose table)
dual_row("MP62_Hirose_DF12-40DS-0.5V_PLACEHOLDER", 40, 0.5, 4.4, 0.3, 1.6, (12.1, 4.6),
         "CONN_C fan + AirPort press connector, 2 x 20 @ 0.5 mm (photo count 2026-10-02), body ~12.6 measured. Footprint-compatible candidate Hirose DF12-40DS-0.5V(86) (LCSC C431048, A 12.1 / B 9.5). Mating with the stock Apple plug NOT verified (M-IOC1). PLACEHOLDER lands.",
         extra=[npth(-5.75, -0.9, 0.7), npth(5.75, -0.9, 0.7)])
# Non-magnetic vertical RJ45 (Lingqiang ZJLQ-RJ45-SMD-PCB125-8P8C, LCSC C55547809) - generic vertical 8P8C SMD placeholder
L = hdr("MP62_RJ45_Vertical_SMD_NoMag_PLACEHOLDER", "Vertical SMD RJ45 8P8C, no magnetics, no LED (Lingqiang ZJLQ-RJ45-SMD-PCB125-8P8C, LCSC C55547809; height must be <= 13.0, VERIFY datasheet). Generic 8 x 1.02 pads + 2 locating posts. PLACEHOLDER.")
for i in range(8): L.append(smd(str(i + 1), -3.57 + 1.02 * i, -6.5, 0.6, 2.0))
L += [smd("SH1", -7.6, 4.6, 1.6, 3.0), smd("SH2", 7.6, 4.6, 1.6, 3.0), npth(-5.7, 0.0, 3.25), npth(5.7, 0.0, 3.25), rect(-8.0, -7.8, 8.0, 7.8, "F.Fab", 0.1), rect(-8.6, -8.1, 8.6, 8.1, "F.CrtYd")]
FP["MP62_RJ45_Vertical_SMD_NoMag_PLACEHOLDER"] = L + [")"]
# JASN V24P05S 2.5G magnetics, SMD-24P 15.1 x 7.1 (LCSC C2827281): 2 x 12 gull-wing, pitch 1.27 [PLACEHOLDER, check drawing]
L = hdr("MP62_JASN_V24P05S_SMD-24P_15.1x7.1_PLACEHOLDER", "JASN V24P05S 2.5GBASE-T magnetics (1CT:1CT, 180 uH, 1.5 kVrms), SMD-24P 15.1 x 7.1, LCSC C2827281. Pitch 1.27 assumed. PLACEHOLDER.")
for i in range(12):
    x = -6.985 + 1.27 * i; L.append(smd(str(i + 1), x, 4.6, 0.7, 2.0)); L.append(smd(str(24 - i), x, -4.6, 0.7, 2.0))
L += [rect(-7.55, -3.55, 7.55, 3.55, "F.Fab", 0.1), rect(-8.0, -5.9, 8.0, 5.9, "F.CrtYd")]
FP["MP62_JASN_V24P05S_SMD-24P_15.1x7.1_PLACEHOLDER"] = L + [")"]
# SMD pogo pin (VBUS/GND to the riser), D 2.0 barrel, 3 A class, working height = local riser gap (4.6-7.3)
L = hdr("MP62_Pogo_SMD_D2.0_PLACEHOLDER", "SMD pogo pin, 2.0 barrel, >= 3 A, free length ~= local gap + 1.0, stroke >= 1.5 (riser VBUS/GND). PART TBC on LCSC. PLACEHOLDER.")
L += ['  (pad "1" smd circle (at 0 0) (size 2.6 2.6) (layers "F.Cu" "F.Paste" "F.Mask"))', '  (fp_circle (center 0 0) (end 1.6 0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))']
FP["MP62_Pogo_SMD_D2.0_PLACEHOLDER"] = L + [")"]
# riser landing pad (riser underside) for a pogo
L = hdr("MP62_Pogo_Target_D3.0", "Gold pogo target pad D2.6 (ENIG) on the riser underside.")
L += ['  (pad "1" smd circle (at 0 0) (size 2.6 2.6) (layers "F.Cu" "F.Mask"))', '  (fp_circle (center 0 0) (end 1.6 0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))']
FP["MP62_Pogo_Target_D3.0"] = L + [")"]
# cradle screw hole (M2 clearance, NPTH) and riser screw hole
for name, d in (("MP62_Cradle_Screw_M2_NPTH", 2.4), ("MP62_Riser_Screw_M2", 2.3)):
    L = hdr(name, "M2 clearance hole for the printed riser cradle (D-IO14).", "exclude_from_pos_files exclude_from_bom")
    L += [npth(0, 0, d), '  (fp_circle (center 0 0) (end %.2f 0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))' % (d / 2 + 1.0)]
    FP[name] = L + [")"]
# ASM1182e: real QFN-48 7x7 land pattern now written by make_fps.py (2026-10-04); the old QFN-64 placeholder is disabled here. EMC2101 uses the stock MSOP-8
def qfn(name, n, body, pitch, ep, descr):
    L = hdr(name, descr); per = n // 4; span = (per - 1) * pitch; k = 1
    for side in range(4):
        for i in range(per):
            t = -span / 2 + i * pitch; o = body / 2 - 0.1
            x, y, w, h = [(-o, t, 0.6, 0.25), (t, o, 0.25, 0.6), (o, -t, 0.6, 0.25), (-t, -o, 0.25, 0.6)][side]
            L.append(smd(str(k), x, y, w, h)); k += 1
    L += [smd("EP", 0, 0, ep, ep, "rect"), rect(-body / 2, -body / 2, body / 2, body / 2, "F.Fab", 0.1), rect(-body / 2 - 0.6, -body / 2 - 0.6, body / 2 + 0.6, body / 2 + 0.6, "F.CrtYd")]
    FP[name] = L + [")"]
if False: qfn("MP62_ASMedia_ASM1182e_QFN-64_9x9_P0.5_PLACEHOLDER", 64, 9.0, 0.5, 6.0, "ASMedia ASM1182e PCIe Gen2 x1 -> 2 x x1 packet switch (package per datasheet: VERIFY). PLACEHOLDER.")
for d in OUT:
    os.makedirs(d, exist_ok=True)
    for k, v in FP.items(): open(os.path.join(d, k + ".kicad_mod"), "w").write("\n".join(v) + "\n")
print(len(FP), "footprints ->", OUT)
