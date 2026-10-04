#!/usr/bin/env python3
"""Screw-point evidence sheet (rev 2026-10-02 ~16:10 ET): stock corner features on the 300 dpi outer-face flatbed scan 83f0b85e,
frame-trace corner holes, the 4x M1.6 design screws, and radial sections of the csk (default) and pt (variant) bosses.
Usage: screw_candidates.py  ->  io_plate_v2_A0_screw_candidates.png"""
import json, math, os, struct, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
exec(open("scan_overlay.py").read().split("fig, ax")[0])          # im (de-skewed scan), cx, cy, W, H, sx, sy, c0, r0
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon
to_x = lambda px: cx + W / 2 - (px - c0) / sx; to_y = lambda py: cy + H / 2 - (py - r0) / sy
to_px = lambda X, Y: (c0 + (cx + W / 2 - X) * sx, r0 + (cy + H / 2 - Y) * sy)
F = json.load(open("io_plate_v2_A0_features.json")); SC = F["fixing"]["screws"]
FR = json.load(open("../../bracket/io_frame/io_frame.json"))["features"]; XM = 53.408
K = [("K1", 74.77, 150.08, "ring: core Ø1.0-1.3, ring Ø2.3-2.8 (sharp)"), ("K2", 29.84, 149.82, "ring (sharp)"), ("K3", 74.60, 15.05, "ring (sharp)"),
     ("K4", 29.54, 13.93, "ring, half off the scan edge"),
     ("K5", 79.52, 140.89, "dark round hole at the edge (+glue residue)"), ("K6", 30.61, 140.70, "C-shaped hook mark"), ("K7", 76.61, 23.24, "C-shaped arc"), ("K8", 28.96, 21.08, "C-shaped arc"),
     ("K9", 53.2, 76.1, "soft ring Ø~2.4\n(frame C1 / flex Ø3.3)"), ("K10", 53.0, 58.6, "dark disc Ø~4.5-5\n(frame C2 / flex Ø5.08)"),
     ("K11", 52.6, 19.3, "faint arc + blob\n(frame PIN_C3 / flex Ø5.67)")]
fig = plt.figure(figsize=(17, 15))
ax = fig.add_axes([0.045, 0.04, 0.28, 0.90])
ax.imshow(im, cmap="gray", vmin=0, vmax=255, extent=[to_x(-0.5), to_x(im.shape[1] - 0.5), to_y(im.shape[0] - 0.5), to_y(-0.5)])
ax.set_xlim(to_x(-0.5), to_x(im.shape[1] - 0.5)); ax.set_ylim(to_y(im.shape[0] - 0.5), to_y(-0.5))
for k, x, y, n in K:
    col = "yellow" if k in ("K1", "K2", "K3", "K4") else ("cyan" if k in ("K5", "K6", "K7", "K8") else "red")
    ax.add_patch(Circle((x, y), 2.2, fc="none", ec=col, lw=1.0)); ax.text(x + (3 if x > 53 else -3), y + 2.5, k, color=col, fontsize=8, ha="center")
for s in SC: ax.add_patch(Circle((s["x"], s["y"]), 3.25 / 2, fc="none", ec="red", lw=1.2))
for k, v in FR.items():
    if k.startswith(("CORNER", "HOLE_C", "PIN_C3")):
        ax.add_patch(Circle((2 * XM - v["cx"], v["cy"]), v["eq_d"] / 2, fc="none", ec="lime", lw=0.9, ls="--"))
        ax.add_patch(Circle((v["cx"], v["cy"]), v["eq_d"] / 2, fc="none", ec="lime", lw=0.7, ls=":"))
ax.set_title("scan 83f0b85e as scanned (front view: X decreases to the right)\nyellow K1-K4 = corner rings, cyan = clip marks, red K9-K11 = centre points (K9/K10 = PRIMARY plate->frame screws, soft)\n"
             "red circles = design M1.6 csk Ø3.25 (2 centre + 4 corner), lime dashed = frame-trace corner holes (mirrored, as used), dotted = unmirrored", fontsize=7.5)
ax.set_xlabel("back-view X, mm"); ax.set_ylabel("Y, mm")
# zoom tiles K1-K4 (+ K5, K6) with size references
for i, (k, x, y, n) in enumerate([K[0], K[1], K[2], K[8], K[9], K[10]]):
    a = fig.add_axes([0.34 + (i % 3) * 0.105, 0.70 - (i // 3) * 0.24, 0.10, 0.22])
    px, py = to_px(x, y); r = 42
    sub = im[max(int(py) - r, 0):int(py) + r, max(int(px) - r, 0):min(int(px) + r, im.shape[1])]
    a.imshow(sub, cmap="gray", vmin=0, vmax=(160 if i < 3 else (90 if i < 5 else 40)), extent=[0, sub.shape[1] / sx, sub.shape[0] / sy, 0])
    ccx, ccy = (px - max(int(px) - r, 0)) / sx, (py - max(int(py) - r, 0)) / sy
    if i < 3:
        for dd, c in ((1.2, "orange"), (2.8, "yellow"), (3.3, "lime")): a.add_patch(Circle((ccx, ccy), dd / 2, fc="none", ec=c, lw=0.6, ls="--"))
    a.plot([0.4, 1.4], [6.5, 6.5], "w-", lw=2); a.text(0.9, 6.3, "1 mm", color="w", fontsize=6, ha="center")
    a.set_title("%s (%.2f, %.2f)\n%s" % (k, x, y, n), fontsize=6.5); a.set_xticks([]); a.set_yticks([])
fig.text(0.34, 0.46, "zoom refs (K1-K3): orange Ø1.2 (core), yellow Ø2.8, lime Ø3.3 (frame corner hole). K9-K11 are soft (out of the scan focus plane), contrast stretched", fontsize=7)
# radial sections through SCR_T+ for both variants
def load_stl(p):
    b = open(p, "rb").read(); n = struct.unpack("<I", b[80:84])[0]
    return np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("x", "<u2")]))["v"].reshape(n, 3, 3).astype(float)
def slice_y(T, y0):
    segs = []
    for t in T:
        d = t[:, 1] - y0; pts = []
        for i in range(3):
            a, b = t[i], t[(i + 1) % 3]; da, db = d[i], d[(i + 1) % 3]
            if (da < 0) != (db < 0): s = da / (da - db); pts.append(a + s * (b - a))
        if len(pts) == 2: segs.append(((pts[0][0], pts[0][2]), (pts[1][0], pts[1][2])))
    return segs
def section(a, tag, mode, sid):
    s0 = [s for s in SC if s["id"] == sid][0]; gap = s0["post_len_below_inner_face"] - 0.8; od = s0["post_od"]; centre = sid.startswith("SCR_C")
    p = "/tmp/fine%s.stl" % tag if os.path.exists("/tmp/fine%s.stl" % tag) else "io_plate_v2_A0%s.stl" % tag
    T = load_stl(p); T = T[(T[:, :, 1].min(1) <= s0["y"]) & (T[:, :, 1].max(1) >= s0["y"]) & (T[:, :, 0].max(1) >= s0["x"] - 7) & (T[:, :, 0].min(1) <= s0["x"] + 7)]
    for (p1, p2) in slice_y(T, s0["y"]): a.plot([p1[0], p2[0]], [p1[1], p2[1]], "k-", lw=1.0)
    ang = math.radians(s0["axis_deg"]); R0 = F["params"]["case_r"]; X0 = 53.19
    n = np.array([-math.sin(ang), -math.cos(ang)]); e = np.array([math.cos(ang), -math.sin(ang)])
    O = np.array([X0 + R0 * math.sin(ang), -R0 + R0 * math.cos(ang)])
    def poly(pts, **kw): a.add_patch(Polygon([O + u * e + v * n for u, v in pts], closed=True, **kw))
    SK, FT = 1.4, 1.0; fhr = {"SCR_C1": (3.3, 3.17, 5.0), "SCR_C2": (5.08, 4.84, 7.0)}.get(sid, (None, 3.3, None))
    if centre:   # PSA + flex 0.17, foam 1.0 (hole = flex hole + 0.5 radius)
        for v0, v1, fc, hr in ((SK, SK + 0.17, "#ffb347", fhr[0] / 2), (SK + 0.17, SK + gap, "#f0f0c0", fhr[0] / 2 + 0.5)):
            poly([(-7, v0), (-hr, v0), (-hr, v1), (-7, v1)], fc=fc, ec="#a07000", lw=0.4); poly([(hr, v0), (7, v0), (7, v1), (hr, v1)], fc=fc, ec="#a07000", lw=0.4)
    fr_ = fhr[1] / 2; v0 = SK + gap
    poly([(-7, v0), (-fr_, v0), (-fr_, v0 + FT), (-7, v0 + FT)], fc="#9ad29a", ec="g", lw=0.5); poly([(fr_, v0), (7, v0), (7, v0 + FT), (fr_, v0 + FT)], fc="#9ad29a", ec="g", lw=0.5)
    wd = 6.0 if sid == "SCR_C2" else 4.0; vb = v0 + FT
    poly([(-wd / 2, vb), (wd / 2, vb), (wd / 2, vb + 0.3), (-wd / 2, vb + 0.3)], fc="#e0c080", ec="#806000", lw=0.5)
    if mode.startswith("csk"):
        poly([(-1.5, 0.12), (1.5, 0.12), (0.8, 1.08), (-0.8, 1.08)], fc="#c0c0ff", ec="b", lw=0.5)
        poly([(-0.8, 1.08), (0.8, 1.08), (0.8, vb + 2.1), (-0.8, vb + 2.1)], fc="#c0c0ff", ec="b", lw=0.5)
        poly([(-1.6, vb + 0.3), (1.6, vb + 0.3), (1.6, vb + 1.6), (-1.6, vb + 1.6)], fc="#e0c080", ec="#806000", lw=0.5)
        L = math.ceil(vb + 2.1 - 0.12); txt = "M1.6x%d ISO 7046 csk T5 from outside, Ø1.8 clr; washer Ø%.0f + M1.6 nut on the frame back" % (L, wd)
    else:
        poly([(-1.6, vb + 0.3), (1.6, vb + 0.3), (1.6, vb + 1.6), (-1.6, vb + 1.6)], fc="#c0c0ff", ec="b", lw=0.5)
        L = 3 if not centre else 4
        poly([(-0.8, vb + 0.3 - L), (0.8, vb + 0.3 - L), (0.8, vb + 0.3), (-0.8, vb + 0.3)], fc="#c0c0ff", ec="b", lw=0.5, alpha=0.6)
        txt = "M1.6x%d thread-forming (plastics) pan T5 from the frame side, blind pilot Ø1.30; washer Ø%.0f" % (L, wd)
    zb = -19.4
    if centre:   # module clamp plate C (collar top 13.66 + 1.6 PA12) with the required clearance hole, and H13 for C2
        ct = zb + s0["clamp_plate_top_h"]; hh = {"SCR_C1": 2.5, "SCR_C2": 3.5}[sid]
        a.add_patch(Rectangle((s0["x"] - 8, ct - 1.6), 8 - hh, 1.6, fc="#d8c8f0", ec="m", lw=0.5)); a.add_patch(Rectangle((s0["x"] + hh, ct - 1.6), 8 - hh, 1.6, fc="#d8c8f0", ec="m", lw=0.5))
        a.text(s0["x"] + hh + 0.2, ct - 1.2, "module clamp plate C\n(needs Ø%.1f hole)" % (2 * hh), fontsize=5.5, color="m")
        if sid == "SCR_C2": a.add_patch(Rectangle((s0["x"] - 2.65, zb), 5.3, s0["frame_back_h"], fc="none", ec="r", lw=0.8, ls="--")); a.text(s0["x"] - 2.5, ct - 2.6, "H13 standoff\n(main board)\nCONFLICT", fontsize=5.5, color="r")
    a.set_aspect("equal"); a.set_xlim(s0["x"] - 6, s0["x"] + 6); a.set_ylim(-8.5 if centre else -8.0, 1.0); a.grid(alpha=0.3)
    a.set_title("%s (%.2f, %.2f) %s, radial section y = %.2f, axis %.1f deg - %s\npost Ø%.1f x %.2f below the inner face (%.2f to the frame + 0.8 into the frame hole), wall %.2f\n%s\n"
                "black = plate STL, orange = PSA+flex, cream = foam, green = frame 1.0 (schematic)" % (sid, s0["x"], s0["y"], s0["role"], s0["y"], s0["axis_deg"], mode, od, s0["post_len_below_inner_face"], gap, s0["local_wall"], txt), fontsize=6.3)
    a.set_xlabel("X, mm"); a.set_ylabel("Z, mm (0 = outer crown, board top -19.4)")
for j, (tag, mode, sid) in enumerate((("", "csk (default)", "SCR_C2"), ("_screwpt", "pt (_screwpt)", "SCR_C2"), ("", "csk (default)", "SCR_T+"))):
    section(fig.add_axes([0.665, 0.655 - j * 0.32, 0.33, 0.235]), tag, mode, sid)
fig.suptitle(y=0.995, t="IO plate v2 A0 - stock screw points: 2 centre (PRIMARY, Aidan 16:14 ET) + 4 corner (secondary) - scan evidence vs design (rev 2026-10-02 ~16:25 ET)", fontsize=12)
fig.savefig("io_plate_v2_A0_screw_candidates.png", dpi=110); print("ok")
