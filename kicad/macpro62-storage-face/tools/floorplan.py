#!/usr/bin/env python3
"""Floorplan PNG (module frame, viewed from the OUTER side = mirrored X so it matches the module in your hand) - uses cadenv matplotlib."""
import json, os, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
HERE = os.path.dirname(os.path.abspath(__file__)); g = json.load(open(os.path.join(HERE, "face_geom.json")))
fig, axs = plt.subplots(1, 2, figsize=(15, 12))
for ax, view in zip(axs, ("CORE side (F) - as seen from the thermal core", "OUTER side (B) - as seen from outside (X mirrored)")):
    mx = (lambda x: x) if view.startswith("CORE") else (lambda x: 104 - x)
    poly = [(mx(x), y) for x, y in g["outline_poly"]]
    ax.add_patch(Polygon(poly, closed=True, fill=False, lw=1.5))
    for x, y in g["holes"]:
        ax.add_patch(Circle((mx(x), y), 2.5, fill=False, lw=1)); ax.add_patch(Circle((mx(x), y), 6.0, fill=False, ls=":", lw=0.7))
    for x, y in g["LUGS"]:
        ax.add_patch(Circle((mx(x), y), 4.4, fc="#f4c27a", ec="k", lw=0.6))
    for r in g["LUG_KOS"]:
        x0, x1 = sorted((mx(r[0]), mx(r[2]))); ax.add_patch(Rectangle((x0, r[1]), x1 - x0, r[3] - r[1], fc="none", ec="orange", hatch="//", lw=0.5))
    ax.set_xlim(-3, 107); ax.set_ylim(-16, 170); ax.set_aspect("equal"); ax.set_title(view, fontsize=11)
    ax.add_patch(Rectangle((0, 0), 104, 26, fc="#eeeeee", ec="none", zorder=0))
    if view.startswith("CORE"):
        ax.add_patch(Polygon(g["DIE_PAD"], closed=True, fc="#ffd9d9", ec="r", lw=0.8))
        ax.add_patch(Rectangle((52 - 10.5, 69.5 - 10.5), 21, 21, fc="#c0392b", ec="k", alpha=0.85)); ax.text(52, 69.5, "U1\nASM2824\n21x21 BGA\n+3 mm gap pad", ha="center", va="center", color="w", fontsize=8)
        for sp in g["STRIPS"]: ax.add_patch(Polygon(sp, closed=True, fc="none", ec="#999", lw=0.6, ls="--"))
        pl = g["PLATE"]; ax.add_patch(Rectangle((pl["x0"], pl["y0"]), pl["x1"] - pl["x0"], pl["y1"] - pl["y0"], fill=False, ec="#555", ls="-.", lw=0.6))
        for (x, y, t) in [(70.5, 60, "U5/L2 VDD_CORE"), (31, 86, "U8 SPI"), (70, 76, "Y1"), (35, 70, "U7 TMP1075"), (35, 52, "U9/U10/U12\nPERST#")]:
            ax.add_patch(Rectangle((x - 2, y - 2), 4, 4, fc="#2e86c1")); ax.text(x, y - 4.5, t, ha="center", fontsize=7)
        ax.text(52, 120, "core side: all parts <= 3.5 mm\n(<= 3.0 over strip pads, <= 1.0 outside plate)", ha="center", fontsize=8)
        ax.text(52, 145.5, "In1 12V / In4 GND: lug sites A+B in parallel", ha="center", fontsize=7)
    else:
        cols = [26.5, 52.0, 77.5]
        for i, cx in enumerate(cols):
            x = mx(cx)
            ax.add_patch(Rectangle((x - 11, 28.5), 22, 80, fc="#d6eaf8", ec="#1f618d", lw=1))
            ax.add_patch(Rectangle((x - 11.2, 108.5), 22.4, 6.5, fc="#1f618d"))
            ax.text(x, 70, "SSD%d\n2280\nM-key\nH4.2" % i, ha="center", va="center", fontsize=9)
            for Lc in (80, 60, 42, 30):
                if i == 1 and Lc in (30, 42): continue
                ax.add_patch(Circle((x, 108.5 - Lc), 2.5, fc="#888" if Lc == 80 else "none", ec="k", lw=0.5))
        x0 = mx(12.0); x1 = mx(92.0)
        ax.add_patch(Rectangle((min(x0, x1), 115), 80, 22, fc="#d6eaf8", ec="#1f618d", lw=1))
        ax.add_patch(Rectangle((x0 - 6.5 if x0 > x1 else x0 - 0, 115.0), 6.5, 22, fc="#1f618d")) if False else ax.add_patch(Rectangle((min(x0, x0 + (6.5 if x0 > x1 else -6.5)), 115), 6.5, 22, fc="#1f618d"))
        ax.text((x0 + x1) / 2, 126, "SSD3 2280 (horizontal)", ha="center", va="center", fontsize=9)
        _jx = g["J"]["J_PCIE"]["cx"]; ax.add_patch(Rectangle((mx(_jx) - 21.1, 14.5), 42.2, 10.07, fc="#7d3c98")); ax.text(mx(_jx), 8, "J1 MCIO 124 RA X %.1f (x8 wired, narrow plug)" % _jx, ha="center", fontsize=8)
        ax.add_patch(Rectangle((min(mx(13.5), mx(19.5)), 9.5), 6, 22, fc="#28b463")); ax.text(mx(16.5), 33, "J3 AUX\n(moved)", ha="center", fontsize=7)
        for (x, y, w, h, t) in [(30, 150, 6, 6, "Q1+U3\nrev.blk"), (44, 150, 4, 4, "U2\neFuse"), (58, 148, 3.5, 3.5, "U4\n3V3 buck"), (70, 152, 10, 10, "L1"), (82, 149, 8, 9, "Cout"), (22, 147, 5, 6, "U6\nEEPROM"), (46, 163, 22, 2, "LEDs D1-D7")]:
            xx = mx(x); ax.add_patch(Rectangle((xx - w / 2, y - h / 2), w, h, fc="#f5b041", ec="k", lw=0.5)); ax.text(xx, y - h / 2 - 3.2, t, ha="center", fontsize=6.5)
        ax.text(52, -6, "no X-bracket (D-S1); screw heads under SSD0/SSD2 edges: <= 1.6 mm", ha="center", fontsize=8)
    ax.text(52, -12, "module frame mm; grey band = connector band Y 0-26; hatched = bus-bar lug keep-outs", ha="center", fontsize=7)
plt.tight_layout(); out = os.path.join(HERE, "..", "floorplan_storage_SM1.png"); plt.savefig(out, dpi=110); print("saved", out)
