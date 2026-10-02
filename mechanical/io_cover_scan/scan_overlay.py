"""Stock plastic I/O cover phone scan (Gaussian-splat PLY, 156 788 splats, inner/back face) vs plate v2 A0.
rev 2026-10-02 ~11:30 ET. Pipeline: load splats -> keep opaque, small, dark splats of the cover -> PCA frame -> detect the
window holes -> similarity fit (mirror, scale, rotation, shift) to the plate openings (flex-scan grid) -> plate back-view frame ->
outline edges, inner-face curvature, raised features -> overlay PNG + JSON."""
import json, os, numpy as np
from scipy import ndimage as ndi
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
HERE = os.path.dirname(os.path.abspath(__file__)); PL = os.path.join(HERE, "..", "io_plate_v2")
ply = os.path.join(HERE, "raw", "Untitled scan.ply")
f = open(ply, "rb"); hdr = b""
while not hdr.endswith(b"end_header\n"): hdr += f.readline()
props = [l.split()[-1] for l in hdr.decode().splitlines() if l.startswith("property")]
n = int([l for l in hdr.decode().splitlines() if l.startswith("element vertex")][0].split()[-1])
d = np.frombuffer(f.read(n * 4 * len(props)), dtype="<f4").reshape(n, len(props)); Pp = {k: d[:, i] for i, k in enumerate(props)}
xyz = d[:, :3]; op = 1 / (1 + np.exp(-Pp["opacity"])); sc = np.exp(np.c_[Pp["scale_0"], Pp["scale_1"], Pp["scale_2"]]).max(1)
col = np.clip(0.5 + 0.28209479 * np.c_[Pp["f_dc_0"], Pp["f_dc_1"], Pp["f_dc_2"]], 0, 1); lum = col.mean(1); blue = col[:, 2] > col[:, 0] + 0.12
base = (np.linalg.norm(xyz, axis=1) < 0.5) & (op > 0.5) & (sc < 0.01) & ~blue
b = base & (xyz[:, 0] > -0.06) & (xyz[:, 0] < 0.02) & (xyz[:, 1] > -0.075) & (xyz[:, 1] < 0.104) & (xyz[:, 2] > -0.02) & (xyz[:, 2] < 0.045) & (lum < 0.45)
X = xyz[b]
for it in range(3):
    c = np.median(X, 0); w, V = np.linalg.eigh(np.cov((X - c).T)); V = V[:, ::-1]; Y = (X - c) @ V; X = X[np.abs(Y[:, 2]) < 4 * np.sqrt(w[0])]
Yall = (xyz - c) @ V * 1000.0
# holes in the PCA frame (scan units)
Ys = (X - c) @ V * 1000.0; px = 0.5; xe = np.arange(-45, 45 + px, px); ye = np.arange(-95, 95 + px, px)
H, _, _ = np.histogram2d(Ys[:, 1], Ys[:, 0], bins=[xe, ye]); occ = ndi.binary_closing(H > 0, iterations=2); holes = ndi.binary_fill_holes(occ) & ~occ
lab, nl = ndi.label(holes); HO = []
for i in range(1, nl + 1):
    m = lab == i
    if m.sum() * px * px < 8: continue
    ii, jj = np.nonzero(m); HO.append((xe[0] + (ii.mean() + .5) * px, ye[0] + (jj.mean() + .5) * px, m.sum() * px * px))
FE = {ft["id"]: ft for ft in json.load(open(os.path.join(PL, "io_plate_v2_A0_features.json")))["features"]}
FJ = json.load(open(os.path.join(PL, "io_plate_v2_A0_features.json")))
ST = {s["port"]: s for s in FJ["stack"]}
TGT = {k: (ST[k]["x"], ST[k]["y"]) for k in ST}; TGT["BTN"] = (FE["PWR_BTN"]["x"], FE["PWR_BTN"]["y"]); TGT["AC"] = (FE["AC"]["x"], FE["AC"]["y"])
# first guess (manual id 2026-10-02): scan hole centres -> plate opening ids
GUESS = {"HDMI": (10.17, 37.32), "ETH2": (11.73, 20.44), "ETH1": (-10.39, 19.43), "BTN": (-11.2, 36.33), "C1": (12.85, 3.3), "C4": (-10.18, 2.51), "C2": (13.41, -7.06),
         "C5": (-9.42, -7.58), "C3": (13.79, -17.43), "C6": (-8.99, -18.06), "A1": (14.29, -32.06), "A3": (-8.41, -33.39), "A4": (-7.51, -44.06), "AC": (-1.07, 61.16)}
pairs = []
for k, g in GUESS.items():
    hh = min(HO, key=lambda h: (h[0] - g[0]) ** 2 + (h[1] - g[1]) ** 2); pairs.append((k, (hh[0], hh[1])))
S = np.array([p[1] for p in pairs]) * np.array([-1, 1]); T = np.array([TGT[p[0]] for p in pairs]); fit = [p[0] != "AC" for p in pairs]
def sim(A, B):
    ma, mb = A.mean(0), B.mean(0); A0, B0 = A - ma, B - mb; U, s, Vt = np.linalg.svd(A0.T @ B0); R = (U @ Vt).T
    k = np.trace((A0 @ R.T).T @ B0) / np.trace(A0.T @ A0); return k, R, mb - k * ma @ R.T
fit = np.array(fit); k, R, t = sim(S[fit], T[fit]); res = k * S @ R.T + t - T; rms = float(np.sqrt((res[fit] ** 2).sum(1).mean()))
P = k * (Yall[:, [1, 0]] * np.array([-1, 1])) @ R.T + t; N = Yall[:, 2] * k
m = base & (np.abs(N) < 8) & (P[:, 0] > 20) & (P[:, 0] < 86) & (P[:, 1] > -8) & (P[:, 1] < 158) & (lum < 0.4); P, N, colm = P[m], N[m], col[m]
# outline edges (50 % density)
edges = []
for y0 in range(5, 151, 15):
    s = (P[:, 1] > y0 - 4) & (P[:, 1] < y0 + 4); hh, bb = np.histogram(P[s, 0], bins=np.arange(20, 88, 0.5)); cc = bb[:-1] + 0.25; ref = np.median(hh[(cc > 32) & (cc < 74)])
    edges.append((y0, cc[np.argmax(hh > 0.5 * ref)], cc[len(hh) - 1 - np.argmax(hh[::-1] > 0.5 * ref)]))
ends = []
for x0 in (40, 53):
    s = np.abs(P[:, 0] - x0) < 5; hh, bb = np.histogram(P[s, 1], bins=np.arange(-15, 170, 0.5)); cc = bb[:-1] + 0.25
    ends.append((x0, cc[np.argmax(hh > 0.5 * np.median(hh[(cc > 5) & (cc < 20)]))], cc[len(hh) - 1 - np.argmax(hh[::-1] > 0.5 * np.median(hh[(cc > 145) & (cc < 152)]))]))
# curvature (robust: plane + u^2/2R over |u| < 22, i.e. inside the 3 mm rim)
def cfit(sel):
    u = P[sel, 0] - 53.19; z = N[sel]; A = np.c_[np.ones(len(u)), u, P[sel, 1], u * u / 2]; w = np.ones(len(z))
    for it in range(8):
        W = np.sqrt(w); co, *_ = np.linalg.lstsq(A * W[:, None], z * W, rcond=None); r = z - A @ co; s = 1.4826 * np.median(np.abs(r)); w = 1 / (1 + (r / (1.5 * s)) ** 2)
    return co, s
sel = np.abs(P[:, 0] - 53.19) < 22; co, mad = cfit(sel); R_all = 1 / co[3]
bands = {"%d-%d" % ab: 1 / cfit(sel & (P[:, 1] > ab[0]) & (P[:, 1] < ab[1]))[0][3] for ab in ((-5, 40), (40, 85), (85, 120), (120, 158))}
widths = {hw: 1 / cfit(np.abs(P[:, 0] - 53.19) < hw)[0][3] for hw in (16, 19, 22, 24)}
rng = np.random.default_rng(0); idx = np.nonzero(sel)[0]; boot = []
for i in range(100):
    bb = np.zeros(len(P), bool); bb[rng.choice(idx, len(idx))] = True; boot.append(1 / cfit(bb)[0][3])
Rplate = FJ["params"]["r_inner"]
out = dict(rev="2026-10-02 ~11:30 ET", format="Gaussian-splat PLY (3DGS: xyz, normals, SH deg 3, opacity, scale, rot), 156788 splats, no mesh faces",
           cover_splats=int(m.sum()), splat_size_median_mm=float(np.median(sc[base]) * 1000), height_noise_mad_mm=float(mad),
           scale_to_plate=float(k), rotation_deg=float(np.degrees(np.arctan2(R[1, 0], R[0, 0]))), mirrored=True, opening_fit_rms_mm=rms,
           opening_residuals={p[0]: [round(float(a), 2) for a in r] for p, r in zip(pairs, res)},
           outline_edges=[[int(a), float(b_), float(c_)] for a, b_, c_ in edges], outline_ends=[[int(a), float(b_), float(c_)] for a, b_, c_ in ends],
           R_inner_fit=float(R_all), R_inner_bootstrap_5_95=[float(np.percentile(boot, 5)), float(np.percentile(boot, 95))], R_inner_by_band={k_: float(v) for k_, v in bands.items()},
           R_inner_by_halfwidth={str(k_): float(v) for k_, v in widths.items()}, R_inner_plate=Rplate)
json.dump(out, open(os.path.join(HERE, "io_cover_scan_check.json"), "w"), indent=1)
# ---------------- overlay ----------------
u = P[:, 0] - 53.19; base_plane = co[0] + co[1] * u + co[2] * P[:, 1]; resid = N - base_plane - u * u / (2 * Rplate)
pxm = 0.75; xe = np.arange(22, 86, pxm); ye = np.arange(-10, 164, pxm)
Hd, _, _ = np.histogram2d(P[:, 0], P[:, 1], bins=[xe, ye]); Sd, _, _ = np.histogram2d(P[:, 0], P[:, 1], bins=[xe, ye], weights=resid); M = np.where(Hd >= 2, Sd / np.maximum(Hd, 1), np.nan)
fl = np.array(json.load(open(os.path.join(PL, "flex_821-2222_trace.json")))["outline"])
fig = plt.figure(figsize=(21, 17)); gs = fig.add_gridspec(2, 3, height_ratios=[3.2, 1])
axs = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2])]
o = FJ["params"]["outline"]
def plate_overlay(ax, lw=1.0):
    ax.add_patch(FancyBboxPatch((o["centre"][0] - o["w"] / 2 + o["r"], o["centre"][1] - o["h"] / 2 + o["r"]), o["w"] - 2 * o["r"], o["h"] - 2 * o["r"], boxstyle="round,pad=%g" % o["r"], fc="none", ec="lime", lw=1.6))
    for ft in FJ["features"]:
        if ft.get("w", 0) <= 0: continue
        if ft["kind"] == "PIN": ax.add_patch(Circle((ft["x"], ft["y"]), ft["w"] / 2, fc="none", ec="m", lw=1.5))
        elif ft["kind"] == "ROUND": ax.add_patch(Circle((ft["x"], ft["y"]), ft["w"] / 2, fc="none", ec="b", lw=lw))
        elif ft["kind"] != "GLUE": ax.add_patch(Rectangle((ft["x"] - ft["w"] / 2, ft["y"] - ft["h"] / 2), ft["w"], ft["h"], fc="none", ec="orange" if ft["kind"] == "LIGHT_WINDOW" else "b", lw=lw))
    for x_, y_, o_ in FJ["clips"]: ax.plot(x_, y_, "g^", ms=9, mfc="none", mew=2)
    ax.plot(fl[:, 0], fl[:, 1], "-", color="darkorange", lw=0.8)
    ax.set_xlim(22, 86); ax.set_ylim(-10, 164); ax.set_aspect("equal"); ax.grid(alpha=.25); ax.set_xlabel("Xb (mm, back view)"); ax.set_ylabel("Y (mm)")
axs[0].scatter(P[:, 0], P[:, 1], s=0.4, c=colm); plate_overlay(axs[0]); axs[0].set_title("scan splats (true colour), registered: x%.3f, %.1f deg, mirrored\nopening-centre rms %.2f mm on 13 openings" % (k, out["rotation_deg"], rms), fontsize=9)
axs[1].imshow(np.log1p(Hd).T, origin="lower", extent=[xe[0], xe[-1], ye[0], ye[-1]], cmap="gray_r"); plate_overlay(axs[1])
for (kk, (sx, sy)), r_ in zip(pairs, res):
    p_ = k * np.array([-sx, sy]) @ R.T + t; axs[1].plot(*p_, "r+", ms=10, mew=1.5)
axs[1].set_title("splat density + plate v2 (lime outline, blue openings, orange windows + flex outline,\nmagenta pins, green clips); red + = scan opening centroids", fontsize=9)
im = axs[2].imshow(M.T, origin="lower", extent=[xe[0], xe[-1], ye[0], ye[-1]], cmap="coolwarm", vmin=-3, vmax=3); plate_overlay(axs[2], 0.8); plt.colorbar(im, ax=axs[2], shrink=0.4, label="mm")
axs[2].set_title("height vs an R%.0f inner face (+ = toward the inside)\nnoise MAD %.1f mm: clips / ribs / pins NOT resolvable" % (Rplate, mad), fontsize=9)
ax = fig.add_subplot(gs[1, :]); sb = np.abs(u) < 26; xb = np.arange(-26, 26.1, 1.0)
med = [np.median((N - co[1] * u - co[2] * P[:, 1])[sb & (u >= a) & (u < a + 1)]) for a in xb]
ax.plot(xb + 0.5, med, "k.-", label="scan: median inner-face height per 1 mm (plane removed)")
zc = co[0]
for Rr, st in ((Rplate, "g-"), (R_all, "r--"), (82.0, "b:")):
    ax.plot(xb, zc + xb ** 2 / (2 * Rr), st, label="R %.0f%s" % (Rr, {Rplate: " (plate, from D0)", R_all: " (scan fit |u|<22)", 82.0: " (old case-cylinder guess)"}[Rr]))
ax.axvspan(-26, -22, color="0.9"); ax.axvspan(22, 26, color="0.9"); ax.text(-25.8, zc + 4.2, "rim", fontsize=8); ax.set_xlabel("u = Xb - 53.19 (mm)"); ax.set_ylabel("height (mm)")
ax.set_title("cross-section (all Y): scan R %.0f (bootstrap %.0f-%.0f; bands %s) vs plate R %.0f" % (R_all, out["R_inner_bootstrap_5_95"][0], out["R_inner_bootstrap_5_95"][1], ", ".join("%.0f" % v for v in bands.values()), Rplate), fontsize=9)
ax.legend(fontsize=8); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "io_cover_scan_overlay.png"), dpi=80)
print(json.dumps({k_: out[k_] for k_ in ("scale_to_plate", "rotation_deg", "opening_fit_rms_mm", "R_inner_fit", "R_inner_bootstrap_5_95", "R_inner_by_band", "R_inner_by_halfwidth", "height_noise_mad_mm", "splat_size_median_mm", "outline_ends")}, indent=0))
print(out["outline_edges"])
