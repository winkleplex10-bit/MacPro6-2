#!/usr/bin/env python3
"""JLC FPC fab + assembly outputs for the port modules (2026-10-04). Usage: python3 tools/make_fab.py [board ...]
Per board -> <dir>/fab/: Gerbers (Cu, coverlay = mask, paste, silk, Edge.Cuts, User.1 = FR4 stiffener drawing) + Excellon (PTH / NPTH separate,
oval holes as routed slots) zipped as <name>_gerber.zip; <name>_bom_jlc.csv (Comment, Designator, Footprint, LCSC Part #);
<name>_cpl_jlc.csv (Designator, Mid X, Mid Y, Layer, Rotation). Coupons / panels get Gerbers + drill only."""
import os, sys, csv, glob, shutil, subprocess, zipfile, re
import pcbnew
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE)
LCSC = {"C5342202": "HOAUC HYCW417-USBC24-180B", "C7501870": "Hong Cheng HC-USB3.0-L137-WJ", "C711353": "HOAUC HYC79-HDMIA19-105",
        "C424645": "Hirose DF40C-50DP-0.4V(51)", "C2828222": "BL24C02F-NTRC", "C76939": "100nF 25V X5R 0201 (muRata GRM033R61E104KE14D)"}
def lcsc_of(f):
    v = f.GetValue(); m = re.search(r"\b(C\d{4,9})\b", v)
    if m: return m.group(1)
    if f.GetFPIDAsString().endswith("C_0201_0603Metric") and v.startswith("100nF"): return "C76939"
    return ""
LAYERS = "F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts,User.1"
def run(*a): r = subprocess.run(list(a), capture_output=True, text=True); assert r.returncode == 0, (a, r.stdout, r.stderr); return r.stdout
def fab(pcb, assembly=True):
    d = os.path.dirname(pcb); nm = os.path.splitext(os.path.basename(pcb))[0]; out = os.path.join(d, "fab"); g = os.path.join(out, "gerber")
    shutil.rmtree(out, ignore_errors=True); os.makedirs(g)
    run("kicad-cli", "pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask", "--no-x2", "-o", g + "/", pcb)
    run("kicad-cli", "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--excellon-oval-format", "route", "--excellon-units", "mm",
        "--generate-map", "--map-format", "gerberx2", "-o", g + "/", pcb)
    files = sorted(os.listdir(g)); zp = os.path.join(out, nm + "_gerber.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files: z.write(os.path.join(g, f), f)
    rep = dict(board=nm, gerber_zip=zp, files=files)
    if assembly:
        b = pcbnew.LoadBoard(pcb); rows = {}
        place = []
        for f in b.GetFootprints():
            if f.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_BOM: continue
            lc = lcsc_of(f); fp = f.GetFPIDAsString().split(":")[-1]
            comment = LCSC.get(lc, f.GetValue())
            k = (comment, fp, lc); rows.setdefault(k, []).append(f.GetReference())
            if not (f.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_POS_FILES): place.append(f)
        bom = os.path.join(out, nm + "_bom_jlc.csv")
        with open(bom, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
            for (c, fp, lc), refs in sorted(rows.items(), key=lambda kv: kv[1][0]): w.writerow([c, ",".join(sorted(refs)), fp, lc])
        # CPL from kicad-cli (board-origin-free coordinates, mm), JLC column names
        raw = os.path.join(out, nm + "_pos_kicad.csv")
        run("kicad-cli", "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "-o", raw, pcb)
        cpl = os.path.join(out, nm + "_cpl_jlc.csv")
        with open(raw) as fi, open(cpl, "w", newline="") as fo:
            r = csv.DictReader(fi); w = csv.writer(fo); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
            for row in r: w.writerow([row["Ref"], row["PosX"] + "mm", row["PosY"] + "mm", "Top" if row["Side"].lower().startswith("top") else "Bottom", row["Rot"]])
        os.remove(raw)
        rep.update(bom=bom, cpl=cpl, bom_rows=[[c, refs, fp, lc] for (c, fp, lc), refs in rows.items()])
    return rep
if __name__ == "__main__":
    import json
    tg = sys.argv[1:] or [os.path.join(PRJ, m, m + ".kicad_pcb") for m in ("mod_usbc", "mod_usba", "mod_hdmi")] + \
         [os.path.join(PRJ, "tdr", c, c + ".kicad_pcb") for c in ("tdr_coupon_c50", "tdr_coupon_a25")] + [os.path.join(PRJ, "panel", c, c + ".kicad_pcb") for c in ("panel_c50", "panel_a25")]
    R = [fab(p, assembly=("tdr_coupon" not in os.path.basename(p))) for p in tg]
    for r in R: print(json.dumps({k: v for k, v in r.items() if k != "files"}), len(r["files"]), "files")
