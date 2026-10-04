#!/usr/bin/env python3
"""Pin-1 check through the 180 deg fold (D-IO16).  Maps the module header J2 pads (flat module frame u, v) through the fold into the
main-board plane and compares them with the JMn receptacle pads on the main board (pin 1, 2, 25, 26, 49, 50).
Frames: module (u = outboard along the tail, v; KiCad y = -v) viewed from F (= outer face side, port side).  Main board: back-view (Xb, Y).
H-side modules (fold toward -X) are drawn as-is: u -> -X, v -> +Y.  O-side modules are the same design rotated 180 deg: u -> +X, v -> -Y.
Fold: arc u f0..f1 (flat length pi R); a point at u > f1 lands at X = X_p -/+ (f0 + f1 - u) after the fold, Y unchanged, F.Cu now facing DOWN
(J2 mates into JMn). Plate tilt / curvature shift X by < 0.15 (cos 5.5 deg) and are ignored here; centre offsets are reported.
Run with the KiCad python (pcbnew); writes pin1_check.json; the PNG is drawn by the same script under /workspace/cadenv/bin/python --plot."""
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE); MB = os.path.join(PRJ, "..", "macpro62-io-board")
OUT = os.path.join(PRJ, "pin1_check.json"); PNG = os.path.join(PRJ, "pin1_check_3d.png")
SLOTS = ["C1", "C4", "A1", "A3", "HDMI"]
PINS = ["1", "2", "25", "26", "49", "50"]
def extract():
    import pcbnew
    MJ = json.load(open(os.path.join(PRJ, "modules.json"))); G = json.load(open(os.path.join(MB, "tools", "io_geom.json"))); W = G["W"]
    mb = pcbnew.LoadBoard(os.path.join(MB, "macpro62-io-board.kicad_pcb"))
    mods = {m["slot"]: (k, m) for k, m in enumerate(MJ["modules"])}
    fn = {"USBC": "mod_usbc", "USBA": "mod_usba", "HDMI": "mod_hdmi"}
    res = []
    for sl in SLOTS:
        k, m = mods[sl]; kind = m["kind"]
        b = pcbnew.LoadBoard(os.path.join(PRJ, fn[kind], fn[kind] + ".kicad_pcb"))
        J2 = b.FindFootprintByReference("J2"); J1 = b.FindFootprintByReference("J1")
        f0, f1 = m["unfolded"]["fold_u"]; s = -1 if m["side"] == "H" else 1; Xp, Yp = m["paddle_x"] if False else (None, None)
        # port centre in the board plane = J1 (u = 0) axis foot; use the flex cut-out centre (module record x, y)
        Xp = m.get("x", None) or (m["stiffener_plan_x"][0] + m["stiffener_plan_x"][1]) / 2; Yp = m["y"]
        Xp = (m["stiffener_plan_x"][0] + m["stiffener_plan_x"][1]) / 2 if Xp is None else Xp
        rec = dict(slot=sl, kind=kind, side=m["side"], jm="JM%d" % (k + 1), jm_rot=m["jm_rot"], fold_u=[f0, f1], pins={})
        jm = mb.FindFootprintByReference("JM%d" % (k + 1))
        for pn in PINS:
            ph = [p for p in J2.Pads() if p.GetNumber() == pn][0]; u = pcbnew.ToMM(ph.GetPosition().x) - 100.0; v = 100.0 - pcbnew.ToMM(ph.GetPosition().y)
            X = Xp + s * (f0 + f1 - u); Y = Yp + (v if s < 0 else -v)
            pr = [p for p in jm.Pads() if p.GetNumber() == pn][0]; xr = W - (pcbnew.ToMM(pr.GetPosition().x) - 40.0); yr = 200.0 - pcbnew.ToMM(pr.GetPosition().y)
            rec["pins"][pn] = dict(module_uv=[round(u, 3), round(v, 3)], header_folded=[round(X, 3), round(Y, 3)], receptacle=[round(xr, 3), round(yr, 3)])
        hp = rec["pins"]; d = lambda a, b_: [round(hp[b_]["header_folded"][i] - hp[a]["header_folded"][i], 3) for i in (0, 1)]
        e = lambda a, b_: [round(hp[b_]["receptacle"][i] - hp[a]["receptacle"][i], 3) for i in (0, 1)]
        off = [round(hp["1"]["header_folded"][i] - hp["1"]["receptacle"][i], 3) for i in (0, 1)]
        cen_h = [sum(hp[p]["header_folded"][i] for p in PINS) / len(PINS) for i in (0, 1)]; cen_r = [sum(hp[p]["receptacle"][i] for p in PINS) / len(PINS) for i in (0, 1)]
        rec.update(vec_1_25_header=d("1", "25"), vec_1_25_recept=e("1", "25"), vec_1_2_header=d("1", "2"), vec_1_2_recept=e("1", "2"),
                   centre_offset=[round(cen_h[i] - cen_r[i], 3) for i in (0, 1)],
                   pin1_offset_minus_centre=[round(off[i] - (cen_h[i] - cen_r[i]), 3) for i in (0, 1)])
        same = lambda a_, b_: all(abs(a_[i] - b_[i]) < 0.05 for i in (0, 1))
        sgn = lambda q: (q > 0.01) - (q < -0.01)
        # contact rows mate on their CENTRES; header (2.6) and receptacle (3.2) placeholder pad rows differ in pitch -> compare the row ORDER only
        rec["row_pitch_header_recept"] = [abs(rec["vec_1_2_header"][1]), abs(rec["vec_1_2_recept"][1])]
        rec["pin1_ok"] = same(rec["vec_1_25_header"], rec["vec_1_25_recept"]) and all(sgn(rec["vec_1_2_header"][i]) == sgn(rec["vec_1_2_recept"][i]) for i in (0, 1)) \
            and abs(rec["pin1_offset_minus_centre"][0]) < 0.05 and abs(rec["centre_offset"][1]) < 0.05
        rec["note"] = "centre X offset = simplified fold model (%s); authoritative JM position = modules_geom.py (jm_ok)" % m.get("fold_mode")
        res.append(rec); print(sl, rec["side"], rec["jm"], "rot", rec["jm_rot"], "pin1_ok", rec["pin1_ok"], "centre offset", rec["centre_offset"], "1->25", rec["vec_1_25_header"], rec["vec_1_25_recept"], "1->2", rec["vec_1_2_header"], rec["vec_1_2_recept"])
    json.dump(res, open(OUT, "w"), indent=1)
def plot():
    import math, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    R = json.load(open(OUT)); MJ = json.load(open(os.path.join(PRJ, "modules.json"))); mods = {m["slot"]: m for m in MJ["modules"]}
    fig = plt.figure(figsize=(16, 9))
    for i, r in enumerate(R):
        m = mods[r["slot"]]; ax = fig.add_subplot(2, 3, i + 1, projection="3d"); s = -1 if r["side"] == "H" else 1
        f0, f1 = r["fold_u"]; Rf = (f1 - f0) / math.pi; zt = 1.5 + 0.2; ztop = zt + 2 * Rf
        Xp = (m["stiffener_plan_x"][0] + m["stiffener_plan_x"][1]) / 2; Y = m["y"]
        uu = np.linspace(-3, f0, 20); X1 = Xp + s * uu; ax.plot(X1, [Y] * len(uu), [ztop] * len(uu), color="#e07000", lw=2)
        th = np.linspace(0, math.pi, 30); ax.plot(Xp + s * (f0 + Rf * np.sin(th)), [Y] * 30, zt + Rf + Rf * np.cos(th), color="#e07000", lw=2)
        ur = np.linspace(f1, f1 + 14, 20); ax.plot(Xp + s * (f0 + f1 - ur), [Y] * 20, [zt] * 20, color="#e07000", lw=2, label="module FPC (tail, fold, return)")
        for pn, c in (("1", "r"), ("2", "m"), ("25", "b"), ("49", "g")):
            hx, hy = r["pins"][pn]["header_folded"]; rx, ry = r["pins"][pn]["receptacle"]
            ax.scatter([hx], [hy], [zt], c=c, marker="v", s=30); ax.scatter([rx], [ry], [0], c=c, marker="o", s=30)
            ax.plot([hx, rx], [hy, ry], [zt, 0], c=c, lw=0.8, label="pin %s header -> JM" % pn)
        ax.set_title("%s (%s side, %s rot %d): pin-1 %s\ncentre offset %+.2f/%+.2f" % (r["slot"], r["side"], r["jm"], r["jm_rot"], "OK" if r["pin1_ok"] else "MISMATCH", *r["centre_offset"]), fontsize=8,
                     color="g" if r["pin1_ok"] else "r")
        ax.set_xlabel("Xb"); ax.set_ylabel("Y"); ax.set_zlabel("z above board"); ax.view_init(25, -60 if s > 0 else -120)
        if i == 0: ax.legend(fontsize=6, loc="upper left")
    fig.suptitle("D-IO16 pin-1 through the 180 deg fold: header J2 pads (triangles, folded) vs main-board JMn pads (dots)", fontsize=10)
    fig.tight_layout(); fig.savefig(PNG, dpi=110); print(PNG)
if __name__ == "__main__":
    if "--plot" in sys.argv: plot()
    else:
        extract(); subprocess.run(["/workspace/cadenv/bin/python", os.path.abspath(__file__), "--plot"])
