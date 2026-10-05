"""Aidan's 200 dpi flatbed scan (2026-10-04 ~15:00 ET): 3 printed plates (top) + the stock plate (bottom), inner face on the glass.
Registers every plate on its port openings (Y = shadow-free scan axis: scale + offset; X: mean opening shift) and overlays the CURRENT model
(io_plate_v2_A0_features.json) on each plate. Writes registration.json, scan_compare.json and ../io_plate_v2_A0_scan_compare.png.
Run measure_scan.py first (outline_fit.json + /tmp/iso.npy)."""
import numpy as np, json, os, sys, cv2, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
from warp import warp, K, X0, X1, Y0, Y1
from blobs2 import blob_otsu
iso = np.load("/tmp/iso.npy")
F = json.load(open(os.path.join(HERE, "..", "io_plate_v2_A0_features.json"))); M = {f["id"]: f for f in F["features"]}
OL = F["params"]["outline"]
OPEN_IDS = ["C1", "C2", "C3", "C4", "C5", "C6", "A1", "A2", "A3", "A4", "ETH1", "ETH2", "HDMI", "AC", "AUD_H", "AUD_O"]
BAD = {"P2": ["C1", "C2", "C3", "A3"], "P3": ["C1", "A2"], "STOCK": ["AUD_H", "AUD_O"]}     # stringing in the print holes / stock blobs merged with the light pipes
# opening geometry for the fit uses the 13:10 model positions (unchanged by the 15:30 revision); sizes for the blob windows
REF = {i: (M[i]["x"], M[i]["y"], 4.8 if i.startswith("AUD") else M[i]["w"], 4.8 if i.startswith("AUD") else M[i]["h"]) for i in OPEN_IDS}
# corner-screw ring centres, read on 40 px/mm crops of the outline-centred warp (radial-symmetry fit agrees within 0.15 where the ring is clean), +-0.2
RINGS = {"P1_top": {"T-": (29.7, 150.6), "T+": (75.1, 150.6), "B-": (29.9, 15.8), "B+": (75.0, 15.7)},
         "P2": {"T-": (29.8, 150.6), "T+": (74.7, 150.6), "B-": (29.9, 15.5), "B+": (74.6, 15.5)},
         "P3": {"T-": (29.9, 149.9), "T+": (74.8, 149.6), "B-": (29.9, 14.5), "B+": (74.6, 14.7)},
         "STOCK": {"T-": (31.1, 148.6), "T+": (76.6, 148.85), "B-": (31.3, 14.3), "B+": (76.6, 14.2)}}
REG, CMP = {}, {}
W = {}
for nm in ("P1_top", "P2", "P3", "STOCK"):
    w = warp(iso, nm); W[nm] = w
    bl = {i: blob_otsu(w, *REF[i]) for i in OPEN_IDS}
    ids = [i for i in OPEN_IDS if bl[i] and i not in BAD.get(nm, [])]
    ym = np.array([REF[i][1] for i in ids]); ys = np.array([bl[i]["cy"] for i in ids])
    b, a = np.polyfit(ym, ys, 1); res = ys - (a + b * ym)
    dx = float(np.mean([bl[i]["cx"] - REF[i][0] for i in ids if not i.startswith("C")]))
    REG[nm] = dict(y_scale=float(b), y_off=float(a), x_shift=dx, rms=float(res.std()), n=len(ids), residuals={i: round(float(r), 2) for i, r in zip(ids, res)})
    to_m = lambda y: (y - a) / b
    CMP[nm] = dict(screws_model_y={k: round(to_m(v[1]), 2) for k, v in RINGS[nm].items()},
                   screw_pitch_x=dict(top=round(RINGS[nm]["T+"][0] - RINGS[nm]["T-"][0], 2), bottom=round(RINGS[nm]["B+"][0] - RINGS[nm]["B-"][0], 2)),
                   openings={i: dict(dy=round(float(to_m(bl[i]["cy"]) - REF[i][1]), 2), h_scan=round(bl[i]["y1"] - bl[i]["y0"], 2), w_scan_shadowed=round(bl[i]["x1"] - bl[i]["x0"], 2)) for i in OPEN_IDS if bl[i]})
    print(nm, "Y scale %.4f off %.3f rms %.2f (n %d)  x-shift %+.2f  screws(model Y) %s" % (b, a, res.std(), len(ids), dx, CMP[nm]["screws_model_y"]))
# measured outline / corner data (width.py manual texture-end reads for the prints, dark edge line for the stock; corners_fit.py)
OF = json.load(open(os.path.join(HERE, "corner_radius_fit.json")))
CMP["outline"] = dict(width=dict(prints=52.4, prints_spread=0.15, stock=53.15, stock_spread=0.1, model_prints=51.9, delta_stock_minus_prints=0.75, delta_unc=0.3,
                                  note="sub-scan (vertical) axis: no perspective; sharp edge to the shadow-free edge (prints: end of the printed-line texture, stock: dark edge line)"),
                      corner_r=dict(prints=[OF[k][s]["r"] for k in ("P1_top", "P2", "P3") for s in ("L", "R")], stock=[OF["STOCK"][s]["r"] for s in ("L", "R")], model_prints=11.5,
                                    note="top-edge (shadow-free) corners only; prints read 0.3 below their model R on average"),
                      ends_model_y=dict(note="opening-registered; prints AC end 158.59-158.73 / audio end -4.57..-4.73, stock 158.46 / -4.78 (model 158.62 / -4.48): length matches within 0.2"))
STK = CMP["STOCK"]["screws_model_y"]
CMP["decision"] = dict(corner_screw_shift_total=-1.0, extra_shift=0.0,
                       note="stock rings at Y %.2f / %.2f (AC end) and %.2f / %.2f (audio end) in model coordinates; prints P1/P2 = the +1.0 build (150.95/15.70), P3 = the original (149.95/14.70); "
                            "print bottom-ring reads sit 0.2-0.4 below their model -> stock bottom 13.5-13.8: the current -1.0 (148.95 / 13.70) matches the stock within 0.2 (top) / 0.3 (bottom)" % (STK["T-"], STK["T+"], STK["B-"], STK["B+"]),
                       shield_w_add=0.8, corner_r=12.8, aud_d=5.3)
json.dump(REG, open(os.path.join(HERE, "registration.json"), "w"), indent=1)
json.dump(CMP, open(os.path.join(HERE, "scan_compare.json"), "w"), indent=1)

# ---------------- overlay ----------------
OLD = dict(w=51.9, r=11.5)
def draw_model(ax, nm, zoom=False):
    g = REG[nm]; T = lambda x, y: (x + g["x_shift"], g["y_off"] + g["y_scale"] * y)
    cx, cy = OL["centre"]
    for (ww, hh, rr, col, ls, lab) in ((OL["w"], OL["h"], OL["r"], "r", "-", "new outline %.1f x %.1f R%.1f" % (OL["w"], OL["h"], OL["r"])), (OLD["w"], OL["h"], OLD["r"], "c", "--", "old outline 51.9 R11.5")):
        x0, y0 = T(cx - ww / 2, cy - hh / 2); x1, y1 = T(cx + ww / 2, cy + hh / 2)
        ax.add_patch(FancyBboxPatch((x0 + rr, y0 + rr), (x1 - x0) - 2 * rr, (y1 - y0) - 2 * rr, boxstyle="round,pad=%g" % rr, fc="none", ec=col, lw=1.0 if zoom else 0.6, ls=ls, label=lab))
    for f in F["features"]:
        if f["kind"] in ("USBC", "USBA", "RJ45", "HDMI", "AC", "LIGHT_WINDOW") and f["w"]:
            x0, y0 = T(f["x"] - f["w"] / 2, f["y"] - f["h"] / 2); ax.add_patch(Rectangle((x0, y0), f["w"], f["h"] * g["y_scale"], fc="none", ec="lime", lw=0.6))
        elif f["kind"] == "ROUND":
            ax.add_patch(Circle(T(f["x"], f["y"]), f["w"] / 2, fc="none", ec="orange" if f["id"].startswith("AUD") else ("m" if f["id"] == "PWR_BTN" else "lime"), lw=0.9 if zoom else 0.6))
        elif f["kind"] == "BOSS":
            ax.add_patch(Circle(T(f["x"], f["y"]), 3.25 / 2, fc="none", ec="r", lw=1.0)); ax.plot(*T(f["x"], f["y"]), "r+", ms=6 if zoom else 3)
        elif f["id"].startswith("BTN_POST"):
            ax.add_patch(Circle(T(f["x"], f["y"]), f["w"] / 2, fc="none", ec="m", lw=0.9)); ax.add_patch(Circle(T(f["x"], f["y"]), 1.1 / 2, fc="none", ec="m", lw=0.6))
            ax.add_patch(Circle(T(f["x"], f["y"]), 2.6 / 2, fc="none", ec="r", lw=0.6, ls="--"))
        elif f["id"] == "BTN_COLLAR":
            ax.add_patch(Circle(T(f["x"], f["y"]), f["w"] / 2, fc="none", ec="m", lw=0.9))
        elif f["id"] == "BTN_KEY":
            ax.add_patch(Circle(T(f["x"], f["y"]), f["w"] / 2, fc="none", ec="m", lw=0.5, ls=":"))
    for yy, col, lab in (((150.95, 15.70), "lime", "+1.0 build"), ((149.95, 14.70), "deepskyblue", "original")):
        for xx in (30.64, 75.74):
            for y_ in yy: ax.plot(*T(xx, y_), "x", color=col, ms=6 if zoom else 3, mew=1.0)
fig = plt.figure(figsize=(18, 18.5))
names = ["STOCK", "P1_top", "P2", "P3"]
for k, nm in enumerate(names):
    ax = fig.add_axes([0.02 + k * 0.245, 0.42, 0.225, 0.49])
    ax.imshow(W[nm], cmap="gray", extent=(X0, X0 + W[nm].shape[1] / K, Y1 - W[nm].shape[0] / K, Y1), vmin=0, vmax=255)
    draw_model(ax, nm); ax.set_xlim(22, 84); ax.set_ylim(-8, 162); ax.set_aspect("equal")
    sc = CMP[nm]["screws_model_y"]
    ax.set_title("%s%s\nopening fit: Y scale %.4f, rms %.2f (n %d)\ncorner rings (model Y): AC end %.2f / %.2f, audio end %.2f / %.2f" % (nm, " (stock)" if nm == "STOCK" else " (print)", REG[nm]["y_scale"], REG[nm]["rms"], REG[nm]["n"], sc["T-"], sc["T+"], sc["B-"], sc["B+"]), fontsize=8)
    if k == 0: ax.legend(fontsize=6.5, loc="lower center", framealpha=0.85)
zooms = [("AC-end corner T- (stock)", 24, 40, 140, 160), ("audio-end corner B- (stock)", 24, 40, 6, 24), ("button area (stock, inner face)", 32, 56, 96, 121), ("audio jacks (stock): orange = new Ø5.3", 36, 70, 8, 26)]
for k, (tt, xa, xb, ya, yb) in enumerate(zooms):
    ax = fig.add_axes([0.03 + k * 0.245, 0.03, 0.215, 0.33])
    ax.imshow(W["STOCK"], cmap="gray", extent=(X0, X0 + W["STOCK"].shape[1] / K, Y1 - W["STOCK"].shape[0] / K, Y1), vmin=0, vmax=255)
    draw_model(ax, "STOCK", zoom=True); ax.set_xlim(xa, xb); ax.set_ylim(ya, yb); ax.set_aspect("equal"); ax.grid(alpha=0.3, color="y", lw=0.4)
    ax.set_title(tt + "\nred + = model screw (Y 148.95 / 13.70), x = older builds (lime +1.0, blue original)", fontsize=7.5)
fig.suptitle("MP62 IO plate v2 A0 (rev 2026-10-04 ~15:30 ET) overlaid on Aidan's 200 dpi scan (inner face on the glass), back view (X right, Y up), mm.  Each plate registered on its port openings (Y scale+offset, X mean shift).\n"
             "Width: stock %.2f vs prints %.2f (model 51.9) -> +0.8 (52.7); corner R: stock %.1f/%.1f vs prints %.1f avg (model 11.5) -> R12.8; corner screws: stock matches the current -1.0 (no extra move); audio Ø4.8 -> Ø5.3; ear posts -> Ø3.0 bosses"
             % (53.15, 52.4, CMP["outline"]["corner_r"]["stock"][0], CMP["outline"]["corner_r"]["stock"][1], np.mean(CMP["outline"]["corner_r"]["prints"])), fontsize=9.5, y=0.995)
out = os.path.join(HERE, "..", "io_plate_v2_A0_scan_compare.png"); fig.savefig(out, dpi=110); print("wrote", os.path.abspath(out))
