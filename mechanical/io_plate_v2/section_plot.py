"""Section at Y = 65.45 (USB-C row) and Y = 37.7 (USB-A pair): curved plate with constant 1.2 wall, flat lands (pockets outside,
bosses inside with ramped inboard edges), straight connectors, and the 821-2222 flex + foam on the inner skin (rev 2026-10-02 09:10 ET)."""
import math, json, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
HERE = os.path.dirname(os.path.abspath(__file__))
FJ = json.load(open(os.path.join(HERE, "io_plate_v2_A0_features.json")))
B = FJ["bosses"]; P = FJ["params"]; FL = P["flex"]
R = P["case_r"]; C = P["outline"]["centre"][0]; SK = P["skin"]
zs = lambda x: -(R - math.sqrt(R * R - (x - C) ** 2))
fr = json.load(open(os.path.join(HERE, "..", "..", "bracket", "io_frame", "io_frame.json")))["features"]
fig, axs = plt.subplots(2, 1, figsize=(12, 8.2))
rows = [("Section Y = 65.45 (USB-C C2 / C5 row)", [("LAND_C_H", 42.6, 10.6, 0.6), ("LAND_C_O", 63.9, 10.6, 0.6)], 8.94, 6.5, 0.0, ("TALL_R", "TALL_L")),
        ("Section Y = 37.7 (USB-A pair)", [("LAND_A_H", 43.3, 15.6, 0.6), ("LAND_A_O", 64.05, 15.6, 0.6)], 13.1, 7.0, 1.2, ("SQ_R", "SQ_L"))]
for ax, (title, lands, pw, ph, setback, slots) in zip(axs, rows):
    xs = [27.24 + i * 0.1 for i in range(520)]
    ax.plot(xs, [zs(x) for x in xs], "k-", lw=1, label="outer face (R %g, MEASURE M-IOT2)" % R)
    ax.plot(xs, [zs(x) - SK for x in xs], "k--", lw=0.8, label="inner face, concentric (constant %.1f wall)" % SK)
    ax.plot(xs, [zs(x) - SK - FL["flex_t"] for x in xs], color="#d08000", lw=1.6, label="821-2222 flex on the inner skin (%.2f, in a %.2f glue pocket)" % (FL["flex_t"], FL["pocket"]))
    ax.fill_between(xs, [zs(x) - SK - FL["flex_t"] for x in xs], [zs(x) - SK - FL["flex_t"] - FL["foam_t"] for x in xs], color="#ffe7a8", alpha=0.6, label="foam %.1f (TO MEASURE)" % FL["foam_t"])
    zf = lambda x: zs(x) - SK - FL["flex_t"] - FL["foam_t"]
    gaps = [(fr[sl]["cx"] - fr[sl]["w"] / 2, fr[sl]["cx"] + fr[sl]["w"] / 2) for sl in slots]
    solid = [x for x in xs if not any(a <= x <= b for a, b in gaps)]
    for seg in [[x for x in solid if x < gaps[0][0]], [x for x in solid if gaps[0][1] < x < gaps[1][0]], [x for x in solid if x > gaps[1][1]]]:
        if seg: ax.fill_between(seg, [zf(x) for x in seg], [zf(x) - 0.8 for x in seg], color="g", alpha=0.35, label="metal I/O frame (schematic, thickness/depth TO MEASURE)" if seg[0] < 30 else None)
    for sl, (a, b) in zip(slots, gaps): ax.text((a + b) / 2, zf((a + b) / 2) - 1.6, "frame slot %s" % sl, fontsize=6, ha="center", color="g")
    for lid, cx, w, b in lands:
        bi = B[lid]; zl = bi["land_z"]; zb = bi["boss_bottom_z"]; s = 1 if cx < C else -1
        x_out = cx - s * (w / 2 + b); x_in = cx + s * (w / 2 + b); z_in = zs(x_in) - SK
        run = bi["ramp_run"] or 0.0
        poly = [(x_out, zs(x_out)), (x_out, zb), (x_in - s * run, zb), (x_in, z_in), (x_in, zl), (cx + s * w / 2, zl), (cx - s * w / 2, zl), (x_out, zl)]
        ax.add_patch(Polygon(poly, closed=True, fc="#bbbbff", ec="b", lw=0.6, label="land boss (flat, parallel to the board), ramped %s deg inboard" % bi["ramp_deg"] if lid == lands[0][0] else None))
        ax.plot([cx - w / 2, cx + w / 2], [zl, zl], "b-", lw=2)
        ax.annotate("boss %.2f proud of the skin:\nflex rim must fold into the slot" % bi["proud_of_inner_skin"], (x_in, (z_in + zb) / 2), ((31.0 if s > 0 else 61.0), -11.2), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5))
        top = zl - setback
        ax.add_patch(plt.Rectangle((cx - pw / 2, top - ph), pw, ph, fc="#cccccc", ec="k", label="straight receptacle (mouth/face)" if lid == lands[0][0] else None))
        ang = math.degrees(math.asin((cx - C) / R))
        ax.annotate("stock shell normal %.1f deg" % ang, (cx, zs(cx)), (cx - 8, 2.2), fontsize=7, arrowprops=dict(arrowstyle="-", lw=0.5))
    ax.set_xlim(26, 81); ax.set_ylim(-12, 4); ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.set_title(title, fontsize=9)
    ax.set_xlabel("Xb (mm, back view)"); ax.set_ylabel("z (mm, 0 = crown of the outer face)")
axs[0].legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "io_plate_v2_A0_section.png"), dpi=140)
