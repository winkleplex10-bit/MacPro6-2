#!/usr/bin/env python3
"""JLC fab + assembly outputs for a KiCad 9 board (used for BP A1 and SM-1).
  python3 jlc_out.py board.kicad_pcb outdir
-> outdir/gerbers/*.g* + drill (Excellon, PTH/NPTH split), outdir/<name>_gerbers.zip,
   outdir/<name>_BOM_JLC.csv (Comment, Designator, Footprint, LCSC Part #; DNP / exclude-from-BOM skipped, merged by LCSC+value),
   outdir/<name>_CPL_JLC.csv (Designator, Mid X, Mid Y, Layer, Rotation; DNP skipped)."""
import sys, os, subprocess, csv, zipfile, collections, glob
import pcbnew
pcb, out = sys.argv[1], sys.argv[2]
name = os.path.splitext(os.path.basename(pcb))[0]
g = os.path.join(out, "gerbers"); os.makedirs(g, exist_ok=True)
for f in glob.glob(os.path.join(g, "*")): os.remove(f)
b = pcbnew.LoadBoard(pcb)
n = b.GetCopperLayerCount()
cu = ["F.Cu"] + ["In%d.Cu" % i for i in range(1, n - 1)] + ["B.Cu"]
layers = ",".join(cu + ["F.Mask", "B.Mask", "F.Paste", "B.Paste", "F.Silkscreen", "B.Silkscreen", "Edge.Cuts"])
subprocess.run(["kicad-cli", "pcb", "export", "gerbers", "--layers", layers, "--subtract-soldermask", "--no-x2", "--use-drill-file-origin", "-o", g + "/", pcb], check=True, capture_output=True)
subprocess.run(["kicad-cli", "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--excellon-units", "mm", "--drill-origin", "plot",
                "--generate-map", "--map-format", "gerberx2", "-o", g + "/", pcb], check=True, capture_output=True)
zp = os.path.join(out, name + "_gerbers.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(g)): z.write(os.path.join(g, f), f)
bom = collections.OrderedDict(); cpl = []
for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    ref = f.GetReference()
    lcsc = f.GetFieldText("LCSC") if f.HasField("LCSC") else ""
    if f.IsDNP() or f.IsExcludedFromBOM(): continue
    if f.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_POS_FILES: continue
    key = (f.GetValue(), str(f.GetFPID().GetLibItemName()), lcsc)
    bom.setdefault(key, []).append(ref)
    p = f.GetPosition()
    cpl.append((ref, "%.4fmm" % pcbnew.ToMM(p.x), "%.4fmm" % (-pcbnew.ToMM(p.y)), "Top" if f.GetLayer() == pcbnew.F_Cu else "Bottom", "%.1f" % (f.GetOrientation().AsDegrees() % 360)))
with open(os.path.join(out, name + "_BOM_JLC.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (v, fp, lc), refs in bom.items(): w.writerow([v, ",".join(refs), fp, lc])
with open(os.path.join(out, name + "_CPL_JLC.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]); w.writerows(cpl)
print("layers", n, "gerber files", len(os.listdir(g)), "BOM lines", len(bom), "placed", len(cpl), "bottom", sum(1 for c in cpl if c[3] == "Bottom"))
