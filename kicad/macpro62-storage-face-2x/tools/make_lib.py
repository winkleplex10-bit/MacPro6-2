#!/usr/bin/env python3
"""Project footprint library MP62_S2X.pretty: KiCad 9 stock footprints, SM-1 MP62_Face footprints (MCIO SFF-TA-1016 Annex A,
mount hole, bus-bar lug, JST GH SM15B) and LCSC/EasyEDA land patterns (sm2x_lib) converted to KiCad 9 format with fixes:
equal-size 'thru_hole' locating pegs -> NPTH, courtyards added, 3D model paths dropped."""
import os, shutil, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.abspath(os.path.join(HERE, ".."))
LIB = os.path.join(PRJ, "MP62_S2X.pretty"); os.makedirs(LIB, exist_ok=True)
SYS = "/usr/share/kicad/footprints"; SM1 = "/workspace/kicad/macpro62-storage-face/MP62_Face.pretty"; EZ = "/workspace/scratch/sm2x_lib/lcsc.pretty"
STOCK = {"Resistor_SMD": ["R_0402_1005Metric", "R_0603_1608Metric", "R_2512_6332Metric"],
         "Capacitor_SMD": ["C_0402_1005Metric", "C_0805_2012Metric", "C_1206_3216Metric"],
         "LED_SMD": ["LED_0603_1608Metric"], "Package_TO_SOT_SMD": ["SOT-23"], "Diode_SMD": ["D_SMA", "D_SOD-323"],
         "Package_SO": ["SOIC-8_3.9x4.9mm_P1.27mm", "VSSOP-8_3x3mm_P0.65mm", "VSSOP-10_3x3mm_P0.5mm"]}
for lib, names in STOCK.items():
    for n in names: shutil.copy(os.path.join(SYS, lib + ".pretty", n + ".kicad_mod"), LIB)
for n in ["MP62_MCIO_124P_RA_SFF-TA-1016", "MP62_FACE_MountHole_D5.0_Pad9.0", "MP62_FACE_BusBarLug_D3.2_Pad8.8", "JST_GH_SM15B-GHS-TB_1x15-1MP_P1.25mm_Horizontal"]:
    shutil.copy(os.path.join(SM1, n + ".kicad_mod"), LIB)

MM = pcbnew.FromMM
def conv(src, dst, descr, crt=None, fab=None):
    IO = pcbnew.PCB_IO_KICAD_SEXPR()
    f = IO.FootprintLoad(EZ, src)
    for p in f.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and p.GetNumber() == "" :
            p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Mask); ls.AddLayer(pcbnew.B_Mask)
            ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); p.SetLayerSet(pcbnew.LSET.AllCuMask().AddLayer(pcbnew.F_Mask).AddLayer(pcbnew.B_Mask))
            p.SetSize(p.GetDrillSize())
    f.Models().clear()
    for it in list(f.GraphicalItems()):
        if it.GetLayer() == pcbnew.F_CrtYd: f.Remove(it)
    if crt is None:
        bb = None
        for p in f.Pads():
            b = p.GetBoundingBox(); bb = b if bb is None else bb.Merge(b) or bb
        x0, y0, x1, y1 = pcbnew.ToMM(bb.GetLeft()) - 0.25, pcbnew.ToMM(bb.GetTop()) - 0.25, pcbnew.ToMM(bb.GetRight()) + 0.25, pcbnew.ToMM(bb.GetBottom()) + 0.25
    else: x0, y0, x1, y1 = crt
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        s = pcbnew.PCB_SHAPE(f); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        s.SetLayer(pcbnew.F_CrtYd); s.SetWidth(MM(0.05)); f.Add(s)
    for r in (fab or []):
        x0, y0, x1, y1 = r
        for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            s = pcbnew.PCB_SHAPE(f); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            s.SetLayer(pcbnew.F_Fab); s.SetWidth(MM(0.1)); f.Add(s)
    f.SetLibDescription(descr); f.SetFPID(pcbnew.LIB_ID("", dst)); f.SetValue(dst)
    IO.FootprintSave(LIB, f)
JOBS = []
JOBS.append(lambda: conv("CONN-SMD_APCI0107-P001A", "M2_M-Key_LOTES_APCI0107-P001A",
     "M.2 Socket 3 key M, SMT, LOTES APCI0107-P001A (LCSC C841661), land pattern from the LCSC/EasyEDA library, checked against the LOTES drawing "
     "(odd row y -3.77 = rear, even row +3.77 = card side, pin n at x = -9.25 + 0.25(n-1)). Card reference plane at y -0.25; 2280 screw at y +78.75.",
     crt=(-11.3, -5.0, 11.3, 4.8), fab=[(-11.0, -0.25, 11.0, 79.75)]))
JOBS.append(lambda: conv("SMD_BD5.6-L5.6-W5.6-D3.6-H3.0", "M2_Standoff_SMTSO2030CTJ_M2_H3.0", "SMT M2 standoff H3.0 (Wurth-style SMTSO2030CTJ, LCSC C2915627), EasyEDA land pattern", crt=(-3.05, -3.05, 3.05, 3.05)))
JOBS.append(lambda: conv("IND-SMD_L6.0-W6.0_SWPA6045S", "L_Sunlord_SWPA6045S", "Sunlord SWPA6045S 6x6x4.5 power inductor (SWPA6045S6R8MT, LCSC C57254), EasyEDA land pattern", crt=(-4.1, -3.3, 4.1, 3.3)))
JOBS.append(lambda: conv("VQFN-10_L2.0-W2.0-P0.45-TL", "TI_RPW_VQFN-10_2x2mm_P0.45mm", "TI RPW 10-pin QFN 2x2 (TPS259470ARPWR, LCSC C3662799), EasyEDA land pattern; pinout checked vs TPS25947 datasheet Fig 5-1", crt=(-1.5, -1.5, 1.5, 1.5)))
import sys, subprocess
if len(sys.argv) > 1: JOBS[int(sys.argv[1])]()
else:
    for i in range(len(JOBS)): subprocess.run([sys.executable, __file__, str(i)], stderr=subprocess.DEVNULL)
    print(sorted(os.listdir(LIB)))
