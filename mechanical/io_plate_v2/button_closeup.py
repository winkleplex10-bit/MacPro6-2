#!/usr/bin/env python3
"""Close-up of the power-button area of plate v2 A0 (rev 2026-10-04): plan (back view, inner-face features + flex 821-2222-A trace + metal-frame
opening + main-board HDMI clamp post, outer-face scan 83f0b85e as underlay, re-centred on the flex button), two sections cut from the STL and a shaded
3D view of the inner face. Usage: button_closeup.py [stl] [features.json] [out.png]   (cadenv python)"""
import json, math, os, struct, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import Circle, Rectangle, Polygon, FancyBboxPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
HERE = os.path.dirname(os.path.abspath(__file__))
STL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "io_plate_v2_A0.stl")
FJS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "io_plate_v2_A0_features.json")
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "io_plate_v2_A0_button_closeup.png")
F = json.load(open(FJS)); FJ = json.load(open(os.path.join(HERE, "flex_821-2222_trace.json")))
B = F["button"]; BF = {f["id"]: f for f in B["features"]}; CK = B["check"]
P = F["params"]; CX, CY = P["outline"]["centre"]; CASE_R = P["case_r"]; SKIN = P["skin"]; fl = P["flex"]
BTN = FJ["button"]; bx, by = BTN["cx"], BTN["cy"]
def zs(x): u = x - CX; return -(CASE_R - math.sqrt(CASE_R ** 2 - u * u))
def zi(x): return zs(x) - SKIN
def load_stl(p):
    b = open(p, "rb").read(); n = struct.unpack("<I", b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("x", "<u2")]))
    return a["v"].reshape(n, 3, 3).astype(float)
T = load_stl(STL)
def section(p0, d):
    """vertical plane through p0 (x, y) along unit d; returns segments in (s, z)"""
    n = np.array([-d[1], d[0], 0.0]); sd = (T - np.array([p0[0], p0[1], 0.0])) @ n
    segs = []
    for tri, s in zip(T, sd):
        if (s > 0).all() or (s < 0).all(): continue
        pts = []
        for i in range(3):
            a, b_ = i, (i + 1) % 3
            if (s[a] > 0) != (s[b_] > 0) and s[a] != s[b_]:
                t = s[a] / (s[a] - s[b_]); q = tri[a] + t * (tri[b_] - tri[a]); pts.append(q)
        if len(pts) == 2:
            segs.append([((q[0] - p0[0]) * d[0] + (q[1] - p0[1]) * d[1], q[2]) for q in pts])
    return segs
FLEXP = MPath(FJ["outline"]); LEG = CK["frame_big_l"]
def in_frame_open(x, y): return (LEG["leg_x"][0] <= x <= LEG["leg_x"][1] and LEG["leg_y"][0] <= y <= LEG["leg_y"][1]) or (LEG["top_x"][0] <= x <= LEG["top_x"][1] and LEG["top_y"][0] <= y <= LEG["top_y"][1])
ears = [(h["cx"], h["cy"], h["d"]) for h in FJ["holes"] if h["id"].startswith("BTN_EAR")]
def in_flex(x, y): return FLEXP.contains_point((x, y)) and all(math.hypot(x - ex, y - ey) > ed / 2 for ex, ey, ed in ears)
def in_foam(x, y): return FLEXP.contains_point((x, y)) and math.hypot(x - bx, y - by) > BTN["ring_d"] / 2 + 0.5 and all(math.hypot(x - ex, y - ey) > BF["BTN_POST_1"]["w"] / 2 + 0.3 for ex, ey, ed in ears)
def draw_section(ax, p0, d, s_lo, s_hi, title):
    segs = section(p0, d); key = lambda q: (round(q[0], 4), round(q[1], 4))
    from collections import defaultdict
    adj = defaultdict(list)
    for i, (a, b_) in enumerate(segs): adj[key(a)].append(i); adj[key(b_)].append(i)
    used = [False] * len(segs); first = True
    for i0 in range(len(segs)):
        if used[i0]: continue
        used[i0] = True; loop = [segs[i0][0], segs[i0][1]]; cur = key(segs[i0][1])
        while True:
            nxt = [j for j in adj[cur] if not used[j]]
            if not nxt: break
            j = nxt[0]; used[j] = True; a, b_ = segs[j]; q = b_ if key(a) == cur else a; loop.append(q); cur = key(q)
        xs_ = [q[0] for q in loop]
        if max(xs_) < s_lo - 1 or min(xs_) > s_hi + 1: continue
        if key(loop[0]) != key(loop[-1]): continue          # only closed chains are filled; the raw outline is drawn below
        ax.add_patch(Polygon(loop, closed=True, fc="#808080", ec="none", zorder=4, label="plate (STL section)" if first else None)); first = False
    for (a, b_) in segs:
        if s_lo - 1 <= a[0] <= s_hi + 1: ax.plot([a[0], b_[0]], [a[1], b_[1]], "k-", lw=1.0, zorder=5)
    ss = np.linspace(s_lo, s_hi, 600)
    xy = [(p0[0] + s * d[0], p0[1] + s * d[1]) for s in ss]
    zf = np.array([zi(x) for x, y in xy])
    def band(mask, z0, z1, col, lab):
        m = np.array(mask); first = True
        for k in range(len(ss) - 1):
            if m[k] and m[k + 1]:
                ax.fill_between(ss[k:k + 2], z0[k:k + 2], z1[k:k + 2], color=col, lw=0, label=lab if first else None); first = False
    band([in_flex(x, y) for x, y in xy], zf - fl["psa_t"], zf - fl["psa_t"] - fl["flex_t"], "#e08000", "PSA + flex 821-2222 (0.17)")
    band([in_foam(x, y) for x, y in xy], zf - fl["psa_t"] - fl["flex_t"], zf - fl["psa_t"] - fl["flex_t"] - fl["foam_t"], "#ffe39a", "foam 1.0 (die-cut)")
    zfr = zf - fl["psa_t"] - fl["flex_t"] - fl["foam_t"]
    _ck = BF["BTN_COLLAR"]; _isl = [math.hypot(x - bx, y - by) <= BTN["ring_d"] / 2 for x, y in xy]
    band(_isl, zf - _ck["flex_depth"], zf - _ck["flex_depth"] - fl["flex_t"], "#c03000", "ASSUMED button island at the frame plane (depth %.2f; collar end %.2f clear)" % (_ck["flex_depth"], _ck["clr_to_flex"]))
    band([not in_frame_open(x, y) for x, y in xy], zfr, zfr - fl["frame_t"], "#9aa4b0", "metal I/O frame 1.0 (BIG_L opening = gap)")
    hp = CK["hdmi_clamp"]["post"]; dd = abs((hp[0] - p0[0]) * -d[1] + (hp[1] - p0[1]) * d[0])
    if dd < 1.9:
        sc = (hp[0] - p0[0]) * d[0] + (hp[1] - p0[1]) * d[1]; zb = F["params"]["d0"]["board_top_z"]; ht = CK["hdmi_clamp"]["head_top_above_board"]; w = 2 * math.sqrt(1.9 ** 2 - dd ** 2)
        hk = 1.2 if CK["hdmi_clamp"].get("head", "pan").startswith("csk") else 1.6; hb = ht - hk if hk == 1.2 else ht - 1.6
        ax.add_patch(Rectangle((sc - w / 2, zb + hb), w, hk, fc="#c0d0ff", ec="b", lw=0.6, label="HDMI clamp-post M2 head (main board, %s)" % CK["hdmi_clamp"].get("head", "pan")[:3]))
    ax.set_xlim(s_lo, s_hi); ax.set_aspect("equal"); ax.grid(alpha=0.25); ax.set_xlabel("mm along the cut"); ax.set_ylabel("z (0 = outer-face crown)")
    ax.set_title(title, fontsize=8); ax.legend(fontsize=5.5, loc="lower center", ncol=2)
fig = plt.figure(figsize=(16, 13))
# ---- plan ----
ax = fig.add_axes([0.03, 0.40, 0.46, 0.52])
SCAN = "/tmp/scan_plate.png"
if os.path.exists(SCAN):
    from PIL import Image
    im0 = Image.open(SCAN).convert("L")
    def _w(a):
        dk = np.asarray(im0.rotate(a, resample=Image.BICUBIC, fillcolor=255)) < 90; c = np.nonzero(dk.mean(0) > 0.35)[0]; return c.max() - c.min()
    ANG = min([k * 0.25 for k in range(-20, 21)], key=_w)
    im = np.asarray(im0.rotate(ANG, resample=Image.BICUBIC, fillcolor=255)).astype(float); dark = im < 90
    rows = np.nonzero(dark.mean(1) > 0.35)[0]; cols = np.nonzero(dark.mean(0) > 0.35)[0]
    r0, r1, c0 = rows.min(), rows.max(), cols.min(); W, H = P["outline"]["w"], P["outline"]["h"]; sx, sy = 12.0, 11.925
    r0 = (r0 + r1) / 2 - H / 2 * sy; c0 = c0 + 0.5
    SH = (bx - 42.49, by - 107.06)            # scan button-hole centroid (42.49, 107.06) -> flex button centre
    def to_px(X, Y): return (c0 + (CX + W / 2 - (X - SH[0])) * sx, r0 + (CY + H / 2 - (Y - SH[1])) * sy)
    Xa, Xb, Ya, Yb = 26, 60, 94, 124; pa = to_px(Xb, Yb); pb = to_px(Xa, Ya)
    sub = im[int(pa[1]):int(pb[1]), int(pa[0]):int(pb[0])]
    ax.imshow(np.clip(sub / 120.0, 0, 1) ** 0.6, cmap="gray", extent=(Xb, Xa, Ya, Yb), alpha=0.55, zorder=0)
ol = P["outline"]
for f in F["features"]:
    if f["kind"] in ("ROUND",) and f["w"]: ax.add_patch(Circle((f["x"], f["y"]), f["w"] / 2, fc="none", ec="k", lw=1.0, zorder=3))
    elif f["kind"] in ("RJ45", "HDMI", "AC", "USBC", "LIGHT_WINDOW") and f["w"]:
        ax.add_patch(FancyBboxPatch((f["x"] - f["w"] / 2, f["y"] - f["h"] / 2), f["w"], f["h"], boxstyle="square,pad=0", fc="none", ec="k", lw=1.0, zorder=3)); ax.text(f["x"], f["y"], f["id"], fontsize=7, ha="center", zorder=4, clip_on=True)
ax.add_patch(Polygon(FJ["outline"], fc="#ffb84d", ec="#c07000", lw=0.8, alpha=0.35, zorder=1, label="flex 821-2222 (trace)"))
ax.add_patch(Circle((bx, by), BTN["ring_d"] / 2, fc="none", ec="m", lw=0.8, ls="--", zorder=3, label="button carrier ring Ø%.2f (board side)" % BTN["ring_d"]))
ax.add_patch(Circle((bx, by), BTN["dome_d"] / 2, fc="#ffd700", ec="k", lw=0.4, zorder=3, label="dome Ø%.1f" % BTN["dome_d"]))
for ex, ey, ed in ears: ax.add_patch(Circle((ex, ey), ed / 2, fc="w", ec="#c07000", lw=0.8, zorder=3))
for l in FJ["leds"]:
    if math.hypot(l["cx"] - bx, l["cy"] - by) < 12: ax.add_patch(Rectangle((l["cx"] - l["w"] / 2, l["cy"] - l["h"] / 2), l["w"], l["h"], fc="#fff200", ec="k", lw=0.4, zorder=4))
pk = BF["BTN_COLLAR"]; from matplotlib.patches import Wedge
ax.add_patch(Wedge((pk["x"], pk["y"]), pk["od"] / 2, 0, 360, width=(pk["od"] - pk["id_"]) / 2, fc="#3070ff", ec="b", lw=1.0, alpha=0.45, zorder=2, label="RAISED collar OD %.1f / ID %.1f x %.2f high" % (pk["od"], pk["id_"], pk["height"])))
ky = BF.get("BTN_KEY"); a = math.radians(ky["ang"]) if ky else 0.0; u = (math.cos(a), math.sin(a)); v = (-u[1], u[0])
r_0, r_1 = ky["r"] if ky else (0, 0)
if ky: ax.add_patch(Polygon([(bx + r * u[0] + s * ky["kw"] / 2 * v[0], by + r * u[1] + s * ky["kw"] / 2 * v[1]) for r, s in ((r_0, -1), (r_1, -1), (r_1, 1), (r_0, 1))], fc=("#3070ff" if ky["mode"] == "tab" else "w"), ec="b", alpha=0.6, zorder=2, label="key %s %.1f wide (collar height)" % (ky["mode"], ky["kw"])))
for k in ("BTN_POST_1", "BTN_POST_2"):
    p = BF[k]; ax.add_patch(Circle((p["x"], p["y"]), p["w"] / 2, fc="#0030c0", ec="k", lw=0.5, zorder=5)); ax.add_patch(Circle((p["x"], p["y"]), p["core"][0] / 2, fc="w", ec="none", zorder=6))
    if p.get("mode") == "boss": ax.add_patch(Circle((p["x"], p["y"]), p["screw"]["head_d"] / 2, fc="none", ec="r", lw=0.9, ls="--", zorder=6, label="M1.4 screw head Ø%.1f (carrier side)" % p["screw"]["head_d"] if k == "BTN_POST_1" else None))
    ax.annotate(("%s BOSS Ø%.1f x %.2f\npilot Ø%.2f, %s x %.1f" % (k, p["w"], p["length"], p["core"][0], p["screw"]["size"], p["screw"]["length"])) if p.get("mode") == "boss" else ("%s Ø%.1f x %.1f\ncore Ø%.1f" % (k, p["w"], p["length"], p["core"][0])), (p["x"], p["y"]), (p["x"] + (3 if p["x"] < bx else -1), p["y"] + (-5 if p["x"] < bx else 4)), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5), zorder=7)
rb = BF["BTN_RIB"]; ax.add_patch(Rectangle((rb["x"] - rb["w"] / 2, rb["y"] - rb["h"] / 2), rb["w"], rb["h"], fc="#0030c0", ec="k", lw=0.5, zorder=5, label="ear bosses / rib (dark blue)"))
ax.annotate("BTN_RIB %.1f x %.1f x %.1f" % (rb["w"], rb["h"], rb["length"]), (rb["x"], rb["y"]), (rb["x"] + 1.0, rb["y"] - 4.5), fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.5), zorder=7)
ax.add_patch(Rectangle((LEG["leg_x"][0], LEG["leg_y"][0]), LEG["leg_x"][1] - LEG["leg_x"][0], LEG["leg_y"][1] - LEG["leg_y"][0], fc="none", ec="g", ls=":", lw=1.2, zorder=3, label="frame BIG_L opening (mirrored scan)"))
ax.add_patch(Rectangle((LEG["top_x"][0], LEG["top_y"][0]), LEG["top_x"][1] - LEG["top_x"][0], LEG["top_y"][1] - LEG["top_y"][0], fc="none", ec="g", ls=":", lw=1.2, zorder=3))
hp = CK["hdmi_clamp"]["post"]; ax.add_patch(Circle(hp, 1.9, fc="none", ec="c", lw=1.0, ls="-.", zorder=4, label="H25 M2 %s head Ø3.8 (%.1f, %.1f) (dotted: old)" % (CK["hdmi_clamp"].get("head", "pan")[:3], hp[0], hp[1])))
if "was" in CK["hdmi_clamp"]: ax.add_patch(Circle(CK["hdmi_clamp"]["was"], 1.9, fc="none", ec="c", lw=0.6, ls=":", zorder=4))
for (s0, s1, lab) in (((ears[1][0], ears[1][1]), (ears[0][0], ears[0][1]), "A"), ((30.0, by), (56.0, by), "B")):
    dx_, dy_ = s1[0] - s0[0], s1[1] - s0[1]; L = math.hypot(dx_, dy_); e = 3.0
    ax.plot([s0[0] - e * dx_ / L, s1[0] + e * dx_ / L], [s0[1] - e * dy_ / L, s1[1] + e * dy_ / L], "r-.", lw=0.8, zorder=6); ax.text(s1[0] + e * dx_ / L, s1[1] + e * dy_ / L + 0.3, lab, color="r", fontsize=9, zorder=7)
ax.set_xlim(26, 60); ax.set_ylim(94, 124); ax.set_aspect("equal"); ax.grid(alpha=0.25)
ax.legend(fontsize=6, loc="lower right", framealpha=0.85)
ax.set_title("Power-button area, plan (back view = from the board, X right), mm.\nUnderlay: outer-face scan 83f0b85e re-centred on the flex button (+%.2f, +%.2f)\n"
             "collar to AC %.2f / ETH2 %.2f / flex slot %.2f / rib %.2f;\ncollar end %.2f short of the frame plane; boss-to-collar web %.2f / %.2f (<0 = fused); button LEDs in the bore %.2f\n"
             "ear screw heads: frame-opening margin %.2f / %.2f, to the HDMI clamp-post head %.2f plan / %.2f vertical (ear 1)\n"
             "HDMI clamp post H25 (%.2f, %.2f), csk M2 flush (top %.2f): to ear-1 boss %.2f plan, carrier ring %.2f, ear-1 lug %.2f;\nclamp-plate edge to the ear-1 head %.2f plan; head %.2f under the frame bar (a pan head would hit it by %.2f)"
             % (bx - 42.49, by - 107.06, CK["collar"]["to_AC_opening"], CK["collar"]["to_ETH2_opening"] or 0, CK["collar"]["flex"]["to_slot_edge_x50_83"], CK["collar"]["flex"]["to_rib"], CK["collar"]["end_to_frame_plane"],
                CK["posts"][0]["web_to_collar"], CK["posts"][1]["web_to_collar"], CK["button_led_collar_bore_margin"],
                CK["posts"][0].get("screw", {}).get("head_frame_open_margin", 0), CK["posts"][1].get("screw", {}).get("head_frame_open_margin", 0),
                CK["posts"][0].get("screw", {}).get("head_to_hdmi_head_plan", 0), CK["posts"][0].get("screw", {}).get("head_to_hdmi_head_vert", 0), CK["hdmi_clamp"]["post"][0], CK["hdmi_clamp"]["post"][1], CK["hdmi_clamp"]["head_top_above_board"],
                CK["hdmi_clamp"]["ear1_boss"]["plan"], CK["hdmi_clamp"]["carrier_ring"]["plan"], CK["hdmi_clamp"]["carrier_ear1_lug"]["plan"], CK["hdmi_clamp"]["clamp_plate_edge_to_ear1_head"]["plan"],
                CK["hdmi_clamp"]["frame"]["head_to_frame_back_vert"], -CK["hdmi_clamp"]["frame"]["pan_head_would_be"]), fontsize=7.5)
# ---- sections ----
e2, e1 = (ears[1][0], ears[1][1]), (ears[0][0], ears[0][1]); dA = np.array([e1[0] - e2[0], e1[1] - e2[1]]); LA = np.linalg.norm(dA); dA = dA / LA
c_ = ((e1[0] + e2[0]) / 2, (e1[1] + e2[1]) / 2)
axA = fig.add_axes([0.52, 0.69, 0.47, 0.27]); draw_section(axA, c_, dA, -LA / 2 - 4, LA / 2 + 4, "Section A-A through both ear bosses (BTN_EAR_2 left -> BTN_EAR_1 right); 0 = midpoint (%.2f, %.2f)" % c_)
axA.set_ylim(-4.6, 0.3)
axB = fig.add_axes([0.52, 0.39, 0.47, 0.27]); draw_section(axB, (bx, by), (1.0, 0.0), -13, 13, "Section B-B along X at Y %.2f (button centre); 0 = X %.2f; rib at +%.2f" % (by, bx, rb["x"] - bx))
axB.set_ylim(-4.6, 0.3)
# ---- 3D inner face ----
ax3 = fig.add_axes([0.03, 0.02, 0.94, 0.36], projection="3d")
cen = T.mean(1); m = (np.abs(cen[:, 0] - bx) < 13) & (np.abs(cen[:, 1] - by) < 11)
Ts = T[m]; N = np.cross(Ts[:, 1] - Ts[:, 0], Ts[:, 2] - Ts[:, 0]); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
keep = N[:, 2] < 0.2   # inner-facing + walls (seen from the board side)
L_ = np.array([0.4, -0.5, -0.75]); L_ /= np.linalg.norm(L_); sh = np.clip(N[keep] @ L_, 0, 1)
cols = plt.cm.Greys(0.25 + 0.6 * (1 - sh))
pc = Poly3DCollection(Ts[keep], facecolors=cols, edgecolors="none"); ax3.add_collection3d(pc)
ax3.set_xlim(bx - 13, bx + 13); ax3.set_ylim(by - 11, by + 11); ax3.set_zlim(-6, 2); ax3.set_box_aspect((26, 22, 8))
ax3.view_init(elev=-58, azim=-75); ax3.set_axis_off()
ax3.set_title("Inner face around the button, seen from the board side (STL %s)" % os.path.basename(STL), fontsize=8)
fig.suptitle(y=0.998, x=0.005, ha="left", t="MP62 IO plate v2 A0 power button (rev 2026-10-04 15:30 / 15:50 ET: HDMI clamp post moved): raised collar 15.0/12.4 x 0.8 + key tab, 2 ear BOSSES Ø3.0 (M1.4 x 2.5 through the ear holes), rib.  From the 821-2222-A flex trace; heights ASSUMED (M-IOPB1..7)", fontsize=8.5)
fig.savefig(OUT, dpi=120); print("wrote", OUT)
