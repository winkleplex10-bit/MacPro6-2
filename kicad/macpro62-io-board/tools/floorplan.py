#!/usr/bin/env python3
"""Floorplan PNG (both sides, stock back-view frame: Xb right, Y up toward the MEG/base end)."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, FancyBboxPatch
HERE = os.path.dirname(os.path.abspath(__file__))
g = json.load(open(os.path.join(HERE, "io_geom.json"))); P = json.load(open(os.path.join(HERE, "placement.json")))
def col(r, v):
    v = v.lower()
    if r[0] == "H": return "#999999"
    if r.startswith("JM"): return "#4c9be8" if "MOD-C" in v.upper() else "#7fb3ff" if "MOD-A" in v.upper() else "#c77dff"   # D-IO16 port-module receptacles
    if r in ("U95", "U96", "U97"): return "#b0e0a0"
    if r.startswith("J1") and len(r) == 3: return "#4c9be8"   # USB-C
    if r in ("J21", "J22", "J23", "J24"): return "#7fb3ff"
    if r in ("J1", "J2"): return "#ff9f40"
    if r in ("J25", "J26", "U50", "U51", "Y4", "L44", "U52", "U53", "Y6", "L45"): return "#6cc070"
    if r in ("J27", "U60", "U61"): return "#c77dff"
    if r in ("J3", "J4", "J5", "U40", "U41", "U42", "U43") or r[0] in "LC" and "uh" in v or r.startswith("C4") or r.startswith("C5"): return "#ff6b6b"
    if r in ("J28", "J29", "U70", "U71", "Y5"): return "#ffd166"
    if r.startswith("U1") or r in ("U1", "U2", "U3", "U4", "U6", "U7"): return "#2a6fdb"
    if r.startswith("U2"): return "#5fa8ff"
    if r in ("U32", "U33", "U34", "Y1", "Y2", "Y3"): return "#9ad1d4"
    return "#e0e0e0"
fig, axs = plt.subplots(1, 2, figsize=(17, 14))
for ax, side, title in ((axs[0], "F", "F side = port side (seen THROUGH the board from the back, back-view frame)"),
                        (axs[1], "B", "B side = PSU side (seen from the back, back-view frame)")):
    ax.add_patch(Polygon(g["board_vertices"], closed=True, fc="#20402a", ec="k", alpha=0.15))
    w = g["window"]; ax.add_patch(Rectangle((w["xL"], w["yB"]), w["width"], w["height"], fc="white", ec="k", hatch="//"))
    ax.text(w["cx"], w["cy"], "AC inlet\ncut-out", ha="center", va="center", fontsize=8)
    for k, h in g["holes"].items():
        ax.add_patch(Circle((h["x"], h["y"]), h["pad_d"] / 2, fc="none", ec="k", ls="--"))
    if side == "B":
        for x0, y0, x1, y1 in g["rails_B"]: ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#ffcccc", ec="r", alpha=0.4))
        ax.text(5.5, 50, "foam\nrail", ha="center", fontsize=7, color="r"); ax.text(95.5, 50, "foam\nrail", ha="center", fontsize=7, color="r")
    else:
        s = g["speaker"]; ax.add_patch(FancyBboxPatch((s["oval_x"][0], s["oval_y"][0]), s["oval_x"][1] - s["oval_x"][0], s["oval_y"][1] - s["oval_y"][0],
                                                       boxstyle="round,pad=0,rounding_size=11", fc="none", ec="orange", ls=":", lw=1.5))
        ax.text(20, 66, "stock speaker\n(keep-out)", ha="center", fontsize=7, color="darkorange")
        c = g["coin"]; ax.add_patch(Circle(c["c"], c["d"] / 2, fc="none", ec="gray", ls=":"))
    for r, d in P.items():
        if d["side"] != side and not r.startswith("H"): continue
        x0, x1 = d["xb"]; y0, y1 = d["y"]
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=col(r, d["value"]), ec="k", lw=0.6, alpha=0.85, ls="--" if d["dnp"] else "-"))
        if (x1 - x0) * (y1 - y0) > 4 or r[0] in "UJ":
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, r + (" DNP" if d["dnp"] else ""), ha="center", va="center", fontsize=6.5 if (x1 - x0) > 6 else 5)
    ax.set_xlim(-3, 104); ax.set_ylim(-3, 177); ax.set_aspect("equal"); ax.set_title(title, fontsize=9)
    ax.set_xlabel("Xb (mm, stock back-view frame)"); ax.set_ylabel("Y (mm) - MEG / base end up, audio end down"); ax.grid(alpha=0.2)
fig.suptitle("MP62 I/O board IOB rev A0 floorplan (101.0 x 173.6, 6 stock holes) - blue USB-C/PD/mux, light blue USB-A, green Ethernet, purple HDMI,\n"
             "yellow audio, red power, orange cable connectors, teal USB2 hubs, grey management", fontsize=10)
plt.tight_layout(rect=(0, 0, 1, 0.94)); out = os.path.join(HERE, "..", "floorplan_iob_A0.png"); plt.savefig(out, dpi=130); print(out)
