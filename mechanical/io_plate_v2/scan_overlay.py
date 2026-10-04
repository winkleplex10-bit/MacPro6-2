#!/usr/bin/env python3
"""Overlay of the plate v2 A0 openings (FRONT view = outer face, mirrored from the back-view design frame about the plate centre) on the
rectified outer-face flatbed scan (2026-10-02, ~12 px/mm). Registration = bbox of the dark plate in the scan -> design outline (scale per axis)."""
import json, sys, numpy as np
from PIL import Image
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
scan = sys.argv[1] if len(sys.argv) > 1 else "/tmp/scan_plate.png"
_im0 = Image.open(scan).convert("L")
def _w(a):
    d = np.asarray(_im0.rotate(a, resample=Image.BICUBIC, fillcolor=255)) < 90; c = np.nonzero(d.mean(0) > 0.35)[0]; return c.max() - c.min()
ANG = min([k * 0.25 for k in range(-20, 21)], key=_w)   # de-skew: angle that gives the narrowest plate (scan rotated ~3 deg)
im = np.asarray(_im0.rotate(ANG, resample=Image.BICUBIC, fillcolor=255)).astype(float); print("de-skew %.2f deg" % ANG)
dark = im < 90
rows = np.nonzero(dark.mean(1) > 0.35)[0]; cols = np.nonzero(dark.mean(0) > 0.35)[0]
r0, r1, c0, c1 = rows.min(), rows.max(), cols.min(), cols.max()
F = json.load(open("io_plate_v2_A0_features.json")); ol = F["params"]["outline"]; cx, cy = ol["centre"]; W, H = ol["w"], ol["h"]
sx, sy = 12.0, 11.925   # ruler calibration (scan 300 dpi, ruler-checked)
r0 = (r0 + r1) / 2 - H / 2 * sy; c0 = c0 + 0.5   # length centred; left (-u) edge = sharp flat edge, right edge lifted (shadow)
print("scan bbox px", r0, r1, c0, c1, "-> scale px/mm x %.3f y %.3f (apparent %.2f x %.2f mm at 12.0/11.925)" % (sx, sy, (c1 - c0) / 12.0, (r1 - r0) / 11.925))
# front view: u = mirrored X (outer face seen from outside, AC on top as scanned); image row grows downward = -Y
def to_px(X, Y): return (c0 + (cx + W / 2 - X) * sx, r0 + (cy + H / 2 - Y) * sy)
fig, ax = plt.subplots(figsize=(6, 15)); ax.imshow(im, cmap="gray")
x0, y0 = to_px(cx + W / 2, cy + H / 2)
ax.add_patch(FancyBboxPatch((x0 + ol["r"] * sx, y0 + ol["r"] * sy), W * sx - 2 * ol["r"] * sx, H * sy - 2 * ol["r"] * sy, boxstyle="round,pad=%g" % (ol["r"] * sx), fc="none", ec="lime", lw=1.2))
for f in F["features"]:
    if f["kind"] in ("SEAT", "GLUE") or not f["w"]: continue
    px, py = to_px(f["x"], f["y"])
    if f["kind"] == "BOSS": ax.add_patch(Circle((px, py), 3.25 / 2 * sx, fc="none", ec="cyan", lw=1.2)); continue   # M1.6 csk corner screws (rev ~16:10 ET)
    if f["kind"] == "ROUND": ax.add_patch(Circle((px, py), f["w"] / 2 * sx, fc="none", ec="r", lw=1))
    else: ax.add_patch(plt.Rectangle((px - f["w"] / 2 * sx, py - f["h"] / 2 * sy), f["w"] * sx, f["h"] * sy, fc="none", ec="r" if f["kind"] != "LIGHT_WINDOW" else "y", lw=0.9))
    ax.text(px, py, f["id"], color="c", fontsize=5, ha="center", va="center")
ax.set_title("Outer-face scan vs plate v2 A0 openings (red), outline (green)\nFRONT view: HDMI slot left / button right with AC on top = stock", fontsize=8)
ax.set_axis_off(); fig.tight_layout(); fig.savefig("io_plate_v2_A0_scan_overlay.png", dpi=110)
