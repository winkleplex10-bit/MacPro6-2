"""Sections through the plate v2 A0 stack (rev 2026-10-02 ~10:08 ET): curved plate (constant 1.2 wall, no lands/bosses), stock 821-2222-A
flex flat on the inner face, foam, metal frame (schematic), board top at the measured D0, straight vertical connectors at the required
height (port riser where the catalogue part is too short), USB-C overmold spot-faces."""
import math, json, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
FJ = json.load(open(os.path.join(HERE, "io_plate_v2_A0_features.json")))
P = FJ["params"]; FL = P["flex"]; ST = {s["port"]: s for s in FJ["stack"]}; SF = FJ["spotfaces"]
R = P["case_r"]; C = P["outline"]["centre"][0]; SK = P["skin"]; ZB = P["d0"]["board_top_z"]
zs = lambda x: -(R - math.sqrt(R * R - (x - C) ** 2))
fr = json.load(open(os.path.join(HERE, "..", "..", "bracket", "io_frame", "io_frame.json")))["features"]
SH = {"USBC": (8.94, "USB-C"), "USBA": (13.2, "USB-A"), "RJ45": (16.2, "RJ45"), "HDMI": (15.2, "HDMI")}
rows = [("Y = %.2f: USB-C C2 / C5 row" % ST["C2"]["y"], ("C2", "C5"), ("TALL_R", "TALL_L")),
        ("Y = %.2f: USB-A A1 / A3 row" % ST["A1"]["y"], ("A1", "A3"), ("SQ_R", "SQ_L")),
        ("Y = %.2f: RJ45 ETH2 / ETH1 row" % ST["ETH2"]["y"], ("ETH2", "ETH1"), ("SMALL_R2", "BIG_L"))]
fig, axs = plt.subplots(3, 1, figsize=(12, 15))
for ax, (title, ports, slots) in zip(axs, rows):
    xs = [27.24 + i * 0.1 for i in range(520)]
    ax.fill_between(xs, [zs(x) for x in xs], [zs(x) - SK for x in xs], color="#555555", alpha=0.55, label="plate, constant %.1f wall, outer R %.1f (from D0)" % (SK, R))
    zfl = lambda x: zs(x) - SK + FL["pocket"] - FL["psa_t"]
    ax.plot(xs, [zfl(x) - FL["flex_t"] for x in xs], color="#d08000", lw=1.6, label="821-2222-A flex, flat on the smooth inner face (0.2 glue pocket)")
    ax.fill_between(xs, [zfl(x) - FL["flex_t"] for x in xs], [zfl(x) - FL["flex_t"] - FL["foam_t"] for x in xs], color="#ffe7a8", alpha=0.7, label="foam %.1f (TO MEASURE)" % FL["foam_t"])
    zf = lambda x: zfl(x) - FL["flex_t"] - FL["foam_t"]
    gaps = []
    for sl in slots:
        v = fr[sl]
        if sl == "BIG_L": gaps.append((v["x_range_leg"][0], v["x_range_leg"][1]))
        else: gaps.append((v["cx"] - v["w"] / 2, v["cx"] + v["w"] / 2))
    gaps.sort()
    solid = [x for x in xs if not any(a <= x <= b for a, b in gaps)]
    for seg in [[x for x in solid if x < gaps[0][0]], [x for x in solid if gaps[0][1] < x < gaps[1][0]], [x for x in solid if x > gaps[1][1]]]:
        if seg: ax.fill_between(seg, [zf(x) for x in seg], [zf(x) - FL["frame_t"] for x in seg], color="g", alpha=0.35, label="metal I/O frame %.1f (schematic, TO MEASURE)" % FL["frame_t"] if seg[0] < 30 else None)
    ax.axhline(ZB, color="#2a7a2a", lw=2); ax.text(27.5, ZB + 0.2, "board top z = %.1f (D0 %.1f crown / %.1f at |u| %.1f)" % (ZB, P["d0"]["crown"], P["d0"]["edge"], P["d0"]["edge_u"]), fontsize=7, color="#2a7a2a")
    for p in ports:
        s = ST[p]; w, nm = SH[s["kind"]]; x = s["x"]
        if s["kind"] == "RJ45":
            top = s["face_z_max"]; h = s["max_height"]
            ax.add_patch(Rectangle((x - w / 2, ZB), w, h, fc="#cccccc", ec="k", label="vertical connector at the required / max height" if p == ports[0] and ax is axs[2] else None))
            ax.text(x, ZB + h / 2, "%s %s\nface <= %.1f above board\n(non-magnetic jack)" % (p, nm, h), ha="center", fontsize=7)
        else:
            ph = s["part_h"]; rs = s["riser_needed"]
            if rs > 0.05:
                ax.add_patch(Rectangle((x - w / 2 - 1.5, ZB), w + 3, rs, fc="#9fd0ff", ec="b", label="port riser (BTB stack + riser PCB)" if p == ports[0] else None))
            ax.add_patch(Rectangle((x - w / 2, ZB + max(rs, 0)), w, ph, fc="#cccccc", ec="k", label="straight vertical connector (catalogue height)" if p == ports[0] else None))
            ax.plot([x - w / 2 - 1, x + w / 2 + 1], [s["mouth_z"]] * 2, "r-", lw=1.2)
            ax.text(x, ZB + rs + ph / 2, "%s %s\nneeds %.2f\n= %.1f part + %.2f riser\nplug recess %.2f" % (p, nm, s["required_height"], ph, rs, s["plug_recess"]), ha="center", fontsize=7)
        ang = math.degrees(math.asin((x - C) / R))
        ax.annotate("surface normal %.1f deg" % ang, (x, zs(x)), (x - 6, 1.6), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5))
    for rid, sf in SF.items():
        if title.startswith("Y = %.2f: USB-C" % ST["C2"]["y"]):
            ax.plot([sf["cx"] - sf["w"] / 2, sf["cx"] + sf["w"] / 2], [sf["floor_z"]] * 2, "m--", lw=1.0, label="overmold spot-face floor" if rid.endswith("_H") else None)
    ax.set_xlim(26, 81); ax.set_ylim(ZB - 1.0, 3.0); ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.set_title(title, fontsize=9)
    ax.set_xlabel("Xb (mm, back view)"); ax.set_ylabel("z (mm, 0 = crown of the outer face)")
    ax.legend(fontsize=6, loc="lower right", ncol=2)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "io_plate_v2_A0_section.png"), dpi=130)
