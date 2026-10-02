"""Sections through the plate v2 A0 stack (rev 2026-10-02 ~12:35 ET, D-IO16 port modules): curved plate (constant 1.2 wall, R from D0 18.0 crown / 16.5 at the
outermost port edge), stock 821-2222-A flex flat on the inner face, foam, metal frame (schematic), board top at D0, USB-C / USB-A / HDMI on
swappable FPC port modules (axis normal to the plate, receptacle on FPC + FR4 stiffener, C-folded tail to a DF40 receptacle JMn, bonded SUS
sleeve + collar under a screwed clamp plate, printed cradle ledges), RJ45 straight on the main board."""
import math, json, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
MJ = json.load(open("/workspace/kicad/macpro62-io-modules/modules.json")); MM = {m["slot"]: m for m in MJ["modules"]}; MST = MJ["stack"]
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
            m_ = MM[p]; T_ = MJ["types"][s["kind"]]; a = math.radians(s["tilt_deg"]); n = (math.sin(a), math.cos(a)); ex = (math.cos(a), -math.sin(a))
            Bx, Bz = s["riser_top_centre"]; t = MST["stack_t"]; sx = T_["sx"]; xo = (-1 if x < C else 1) * (1 if ex[0] > 0 else -1); so = -1 if x < C else 1
            T = lambda q, h: (Bx + ex[0] * q + n[0] * h, Bz + ex[1] * q + n[1] * h)
            ax.add_patch(Polygon([T(-sx, -MST["fpc_t"] - MST["psa_t"]), T(sx, -MST["fpc_t"] - MST["psa_t"]), T(sx, -t), T(-sx, -t)], fc="#c8b560", ec="k", lw=0.5, label="FR4 1.0 stiffener (module)" if p == ports[0] else None))
            ax.plot([T(-sx, -0.055)[0], T(sx, -0.055)[0]], [T(-sx, -0.055)[1], T(sx, -0.055)[1]], color="#e07000", lw=1.4, label="module FPC 0.11 (2-layer)" if p == ports[0] else None)
            ax.add_patch(Polygon([T(-w / 2, 0), T(w / 2, 0), T(w / 2, s["conn_h"]), T(-w / 2, s["conn_h"])], fc="#cccccc", ec="k", label="receptacle on the FPC (catalogue height)" if p == ports[0] else None))
            hz = (m_["collar_top_height"] + ZB - Bz) / n[1]; cw = w / 2 + MST["sleeve_t"]
            for sg in (-1, 1):
                ax.add_patch(Polygon([T(sg * (w / 2), 0), T(sg * cw, 0), T(sg * cw, hz), T(sg * (w / 2), hz)], fc="#4060a0", ec="#203060", lw=0.3, label="SUS304 0.2 shield sleeve, bonded to the shell" if p == ports[0] and sg < 0 else None))
                ax.add_patch(Polygon([T(sg * cw, hz - 0.2), T(sg * (cw + MST["collar_w"]), hz - 0.2), T(sg * (cw + MST["collar_w"]), hz), T(sg * cw, hz)], fc="#4060a0", ec="#203060", lw=0.3))
            zc = m_["collar_top_height"] + ZB; xc0, xc1 = T(-(cw + MST["collar_w"] + 2.5), hz)[0], T(cw + MST["collar_w"] + 2.5, hz)[0]
            xq = [min(xc0, xc1) + k * abs(xc1 - xc0) / 40 for k in range(41)]; zt_ = [zf(q) - FL["frame_t"] - 0.3 for q in xq]
            ax.fill_between(xq, zt_, [v - MST["plate_t"] for v in zt_], color="#b08fd8", alpha=0.8, lw=0.5, label="clamp plate (MJF PA12, top = frame back - 0.3), screws to M2 SMT standoffs" if p == ports[0] else None)
            # cradle (schematic): ledge band out of plane, walls to the board
            sb = [T(-sx, -t), T(sx, -t)]
            ax.add_patch(Polygon([sb[0], sb[1], (sb[1][0], ZB), (sb[0][0], ZB)], fc="none", ec="#7a5ab0", lw=0.6, ls="--", hatch="..",
                                 label="printed cradle: ledges at |y'| 3.6-%.1f (out of plane) + walls" % T_["sy"] if p == ports[0] else None))
            # tail: flap, C-fold, return run, header + stiffener, JM receptacle
            E = T(xo * sx, -0.055); Fp = (E[0] + so * m_["flap"], E[1]); R_ = m_["fold_r"]; zt = ZB + MST["mated"] + 0.055
            ax.plot([E[0], Fp[0]], [E[1], Fp[1]], color="#e07000", lw=1.2)
            th = [math.pi / 2 - k * math.pi / 30 for k in range(31)]; cz = (Fp[1] + zt) / 2
            ax.plot([Fp[0] + so * R_ * math.cos(q) for q in th], [cz + R_ * math.sin(q) for q in th], color="#e07000", lw=1.2)
            x0r, x1r = m_["jm_x_range"]; ax.plot([Fp[0], (x0r + x1r) / 2 + (-so) * 7.8], [zt, zt], color="#e07000", lw=1.2, label="FPC tail, C-fold R %.1f" % R_ if p == ports[0] else None)
            ax.add_patch(Rectangle((x0r + 0.15, ZB), x1r - x0r - 0.3, MST["mated"], fc="#303030", ec="k", lw=0.4, label="DF40C-50DS JMn + DF40C-50DP (mated 1.5)" if p == ports[0] else None))
            ax.add_patch(Rectangle((x0r - 0.85, zt + 0.055 + MST["psa_t"]), x1r - x0r + 1.7, 1.0, fc="#c8b560", ec="k", lw=0.4))
            mo = s["mouth_centre"]; ax.plot([T(0, -3)[0], mo[0] + n[0] * 3], [T(0, -3)[1], mo[1] + n[1] * 3], "r-.", lw=0.8)
            ax.plot(*mo, "ro", ms=3)
            ax.text(Bx, ZB + 3.2, "%s %s module\nmouth %.2f above board, axis %+.2f deg (%+.1f off normal)\nseat %.2f, stiffener bottom %.1f-%.1f\nmouth recess %.2f-%.2f, plug stand-off %.2f" % (p, nm,
                    s["mouth_centre_height"], s["tilt_deg"], s.get("off_normal_deg", 0.0), m_["seat_height"], min(m_["stiffener_bottom_heights"]), max(m_["stiffener_bottom_heights"]),
                    min(s.get("mouth_recess_edges", [s["mouth_recess"]])), max(s.get("mouth_recess_edges", [s["mouth_recess"]])), s["plug_recess"]), ha="center", fontsize=5.6)
            if s.get("seat_floor"):
                (sx0, sz0), (sx1, sz1) = s["seat_floor"]; ax.plot([sx0, sx1], [sz0, sz1], "m-", lw=1.6, label="flat plug seat floor (perpendicular to the axis)" if p == ports[0] else None)
        ang = math.degrees(math.asin((x - C) / R))
        ax.annotate("surface normal %.1f deg" % ang, (x, zs(x)), (x - 6, 1.6), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5))
    for rid, sf in SF.items():
        if title.startswith("Y = %.2f: USB-C" % ST["C2"]["y"]):
            ax.plot([sf["cx"] - sf["w"] / 2, sf["cx"] + sf["w"] / 2], [sf["floor_z"]] * 2, "m--", lw=1.0, label="overmold spot-face floor" if rid.endswith("_H") else None)
    ax.set_xlim(26, 81); ax.set_ylim(ZB - 1.0, 3.0); ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.set_title(title, fontsize=9)
    ax.set_xlabel("Xb (mm, back view)"); ax.set_ylabel("z (mm, 0 = crown of the outer face)")
    ax.legend(fontsize=6, loc="lower right", ncol=2)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "io_plate_v2_A0_section.png"), dpi=130)
