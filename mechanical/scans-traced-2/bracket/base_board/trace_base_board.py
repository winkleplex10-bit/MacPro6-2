#!/usr/bin/env python3
"""Trace Aidan's two flatbed scans of the stock Mac Pro 6,1 round base (interconnect) board.
  base_board_bottom_scan.jpeg : solder/bottom side (sharp)      base_board_top_scan.jpeg : top/core side (defocused)
Method (same as core_gpu_face): scale from the cm rulers (tick-period fit, scanlib.calibrate), sub-pixel circle fits,
registration of the two sides on 8 common holes (mirror handled), resampling into the BP frame.
BP frame (top view, as /workspace/kicad/macpro62-backplane): +x toward the +x gold hole (the end of the CPU socket
nearer its key), +y toward the core / GPU-connector side, -y = PSU side. ORIGIN = midpoint of the two gold Ø4 holes
(the hole axis). The disc centre is reported separately (it is ~0.6 mm off the hole axis).
Run: /workspace/cadenv/bin/python trace_base_board.py   (needs work/ seeds only for nothing; all is recomputed)"""
import json, math, os, sys
import cv2, numpy as np, ezdxf
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "scanlib")); import scanlib
os.chdir(HERE); os.makedirs("work", exist_ok=True)
BOT, TOP = "base_board_bottom_scan.jpeg", "base_board_top_scan.jpeg"
cb = scanlib.calibrate(BOT); ct = scanlib.calibrate(TOP)
def disc_fit(path, c, thr_list=(60, 90, 115)):
    g = cv2.imread(path, 0); SX, SY = c["SX"], c["SY"]; fits = []
    for T in thr_list:
        m = (g < T).astype(np.uint8) * 255; m[:, 655:] = 0; m[960:, :] = 0; m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); cc = max(cnts, key=cv2.contourArea)[:, 0, :].astype(float)
        x = cc[:, 0] / SX; y = cc[:, 1] / SY; cx, cy, r = scanlib.fitc(x, y)
        for _ in range(6):
            res = np.hypot(x - cx, y - cy) - r; k = np.abs(res) < max(0.6, 3 * np.median(np.abs(res))); cx, cy, r = scanlib.fitc(x[k], y[k])
        res = np.hypot(x - cx, y - cy) - r
        fits.append(dict(T=T, cx_px=cx * SX, cy_px=cy * SY, D=2 * r, sd=float(res[np.abs(res) < 0.6].std()), maxdev=float(np.abs(res).max()), contour=cc))
    return fits
fb = disc_fit(BOT, cb); ft = disc_fit(TOP, ct)
gb = cv2.GaussianBlur(cv2.imread(BOT, 0).astype(float), (3, 3), 0.8)
def ring_fit(x0, y0, rmin, rmax, SX, SY, img=gb):
    cx, cy = x0, y0
    for _ in range(4):
        pts = []
        for a in np.linspace(0, 2 * math.pi, 72, endpoint=False):
            rs = np.linspace(rmin, rmax, 60); xs = cx + rs * math.cos(a); ys = cy + rs * math.sin(a)
            v = cv2.remap(img.astype(np.float32), xs.astype(np.float32).reshape(1, -1), ys.astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR)[0]
            k = int(np.argmin(np.diff(v))); pts.append((xs[k] + 0.5 * (xs[1] - xs[0]), ys[k] + 0.5 * (ys[1] - ys[0])))
        P = np.array(pts); X = P[:, 0] / SX; Y = P[:, 1] / SY; mx, my, r = scanlib.fitc(X, Y)
        res = np.hypot(X - mx, Y - my) - r; k = np.abs(res) < max(0.25, 2.5 * np.median(np.abs(res))); mx, my, r = scanlib.fitc(X[k], Y[k]); cx, cy = mx * SX, my * SY
    return cx, cy, 2 * r, float(np.std((np.hypot(X - mx, Y - my) - r)[k]))
SEEDS = {"G1": (237, 447, 5, 22), "G2": (450, 769, 5, 22), "S1": (183.7, 463.5, 2, 9), "S2": (440, 419.5, 2, 9), "S3": (555.5, 592, 2, 9),
         "S4": (136.5, 658.5, 2, 9), "S5": (216, 778.5, 2, 9), "S6": (411.5, 811, 2, 9),
         "PEG_A1": (318.5, 455.5, 1.5, 7), "PEG_A2": (296, 470.5, 1.5, 7), "PEG_K1": (415.5, 601, 1.5, 7), "PEG_K2": (392, 617.5, 1.5, 7),
         "PEG_B1": (472, 689, 1.5, 7), "PEG_B2": (450.5, 704.5, 1.5, 7)}
SXb, SYb = cb["SX"], cb["SY"]; FE = {}
for k, (x, y, a, b) in SEEDS.items():
    cx, cy, d, sd = ring_fit(x, y, a, b, SXb, SYb); FE[k] = dict(px=(cx, cy), d=d, sd=sd)
for k in ("G1", "G2"):
    cx, cy, d, sd = ring_fit(*FE[k]["px"], 2, 9, SXb, SYb); FE[k]["inner_px"] = (cx, cy); FE[k]["inner_d"] = d
mmb = lambda p: np.array([p[0] / SXb, p[1] / SYb])
G1 = mmb(FE["G1"]["inner_px"]); G2 = mmb(FE["G2"]["inner_px"]); O = (G1 + G2) / 2; u = (G2 - G1) / np.linalg.norm(G2 - G1); nrm = np.array([-u[1], u[0]])
def b2bp(px, py): p = mmb((px, py)) - O; return np.array([p @ u, p @ nrm])
fbm = [f for f in fb if f["T"] == 90][0]; disc_b = b2bp(fbm["cx_px"], fbm["cy_px"])
BPF = {k: b2bp(*(v.get("inner_px", v["px"]))) for k, v in FE.items()}
# ---------- top registration on the 8 holes ----------
SXt, SYt = ct["SX"], ct["SY"]; gt = cv2.GaussianBlur(cv2.imread(TOP, 0).astype(float), (0, 0), 1.5)
TSEEDS = {"S6": (313, 432), "G2": (368, 440), "S3": (563, 510), "S2": (587, 718), "G1": (413, 827), "S1": (360, 848), "S4": (198, 728), "S5": (182, 585)}
TB = {}
for k, (x, y) in TSEEDS.items():
    w = gt[y - 12:y + 13, x - 12:x + 13]; W = np.clip(w - np.percentile(w, 40), 0, None); W[W < 0.5 * W.max()] = 0
    Yg, Xg = np.mgrid[y - 12:y + 13, x - 12:x + 13]; TB[k] = ((W * Xg).sum() / W.sum(), (W * Yg).sum() / W.sum())
A = np.array([BPF[k] for k in TB]); Bq = np.array([[TB[k][0] / SXt, -TB[k][1] / SYt] for k in TB])
ca, cq = A.mean(0), Bq.mean(0); U_, S_, Vt = np.linalg.svd((A - ca).T @ (Bq - cq)); R = Vt.T @ U_.T; assert np.linalg.det(R) > 0
t = cq - R @ ca; reg_res = Bq - (A @ R.T + t); reg_rms = float(np.sqrt((reg_res ** 2).sum(1).mean()))
def t2bp(px, py): return R.T @ (np.array([px / SXt, -py / SYt]) - t)
ftm = [f for f in ft if f["T"] == 90][0]; disc_t = t2bp(ftm["cx_px"], ftm["cy_px"])
# ---------- rectified images (BP frame, top view) ----------
K, EXT = 8.0, 64.0; N = int(2 * EXT * K); xs = (np.arange(N) + 0.5) / K - EXT; ys = EXT - (np.arange(N) + 0.5) / K; XX, YY = np.meshgrid(xs, ys)
mxb = ((O[0] + XX * u[0] + YY * nrm[0]) * SXb).astype(np.float32); myb = ((O[1] + XX * u[1] + YY * nrm[1]) * SYb).astype(np.float32)
rect_b = cv2.remap(cv2.imread(BOT), mxb, myb, cv2.INTER_CUBIC)
qx = R[0, 0] * XX + R[0, 1] * YY + t[0]; qy = R[1, 0] * XX + R[1, 1] * YY + t[1]
rect_t = cv2.remap(cv2.imread(TOP), (qx * SXt).astype(np.float32), (-qy * SYt).astype(np.float32), cv2.INTER_CUBIC)
cv2.imwrite("work/rect_bottom.png", rect_b); cv2.imwrite("work/rect_top.png", rect_t)
toBP = lambda c, r: ((c + 0.5) / K - EXT, EXT - (r + 0.5) / K); toPX = lambda x, y: ((x + EXT) * K - 0.5, (EXT - y) * K - 0.5)
# ---------- socket: top frame + slot + key ----------
gs = cv2.GaussianBlur(cv2.imread(TOP, 0), (3, 3), 0); soc = {}
for T in (65, 75, 85):
    m = (gs > T).astype(np.uint8); m[:, :380] = 0; m[:, 500:] = 0; m[:440, :] = 0; m[820:, :] = 0
    n_, lab, st, _ = cv2.connectedComponentsWithStats(m); i = 1 + np.argmax(st[1:, 4]); comp = (lab == i).astype(np.uint8)
    cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); P = np.array([t2bp(x, y) for x, y in cnts[0][:, 0, :]])
    r = cv2.minAreaRect(P.astype(np.float32)); fl = comp.copy(); cv2.drawContours(fl, cnts, -1, 1, -1); inner = fl - comp
    n2, l2, s2, _ = cv2.connectedComponentsWithStats(inner); j = 1 + np.argmax(s2[1:, 4])
    c2, _ = cv2.findContours((l2 == j).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); P2 = np.array([t2bp(x, y) for x, y in c2[0][:, 0, :]])
    soc[T] = dict(outer=r, slot=cv2.minAreaRect(P2.astype(np.float32)), outer_bbox=(P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max()))
def wh(r): w, h = r[1]; a = r[2]; return (max(w, h), min(w, h))
so = soc[75]; SOCK_OUT = dict(c=so["outer"][0], L=wh(so["outer"])[0], W=wh(so["outer"])[1]); SOCK_SLOT = dict(c=so["slot"][0], L=wh(so["slot"])[0], W=wh(so["slot"])[1])
it = cv2.cvtColor(rect_t, cv2.COLOR_BGR2GRAY).astype(float); row = int((EXT - SOCK_SLOT["c"][1]) * K); pr = it[row - 2:row + 3, :].mean(0)
msk = (xs > -30) & (xs < 30); KEY_X = float(xs[msk][np.argmax(pr[msk])])
pm = lambda a, b: (BPF[a] + BPF[b]) / 2
PEG_A, PEG_B, PEG_K = pm("PEG_A1", "PEG_A2"), pm("PEG_B1", "PEG_B2"), pm("PEG_K1", "PEG_K2")
sock_axis = (PEG_B - PEG_A) / np.linalg.norm(PEG_B - PEG_A); SOCK_ANG = math.degrees(math.atan2(sock_axis[1], sock_axis[0]))
SOCK_C_PEGS = (PEG_A + PEG_B) / 2
# ---------- connector pad fields (bottom, seen through) ----------
ib = cv2.cvtColor(rect_b, cv2.COLOR_BGR2GRAY).astype(float); g1 = cv2.GaussianBlur(ib, (0, 0), 1.2); d = g1 - cv2.GaussianBlur(ib, (0, 0), 5)
rs, cs = np.where((d == cv2.dilate(d, np.ones((5, 5)))) & (d > 12)); PK = np.array([toBP(c, r) for r, c in zip(rs, cs)])
REG = {"GPU_L (stock GPU link, -x side)": [(-58, 20), (-45, 8), (-15, 42), (-28, 55)], "GPU_R (stock GPU link, +x side)": [(58, 20), (45, 8), (15, 42), (28, 55)],
       "PSU_SIDE (stock link, -y side)": [(-24, -38), (24, -38), (24, -58), (-24, -58)]}
FIELDS = {}
def lattice_angle(Q):
    tr = cKDTree(Q); V = np.array([Q[j] - Q[i] for i, j in tr.query_pairs(1.6)]); ang = np.degrees(np.arctan2(V[:, 1], V[:, 0])) % 90
    h, e = np.histogram(ang, bins=90, range=(0, 90)); a0 = e[np.argmax(h)] + 0.5; sel = np.abs(((ang - a0 + 45) % 90) - 45) < 6
    return float((math.degrees(np.angle(np.mean(np.exp(1j * np.radians(ang[sel] * 4))))) / 4) % 90)
for k, poly in REG.items():
    pp = np.array(poly, np.float32); Q = PK[[cv2.pointPolygonTest(pp, (float(x), float(y)), False) >= 0 for x, y in PK]]
    tr = cKDTree(Q); Q = Q[np.array([len(tr.query_ball_point(q, 1.5)) for q in Q]) >= 3]
    a = lattice_angle(Q); best = None
    for cand in (a, a + 90):                                   # long axis = direction of the larger extent
        d1 = np.array([math.cos(math.radians(cand)), math.sin(math.radians(cand))]); d2 = np.array([-d1[1], d1[0]])
        s1 = Q @ d1; s2 = Q @ d2; ext = (s1.max() - s1.min(), s2.max() - s2.min())
        if best is None or ext[0] > best[1][0]: best = (cand, ext, d1, d2, s1, s2)
    ang, (L, W), d1, d2, s1, s2 = best; ang = (ang + 90) % 180 - 90
    c = d1 * (s1.max() + s1.min()) / 2 + d2 * (s2.max() + s2.min()) / 2
    box = [c + d1 * sx * L / 2 + d2 * sy * W / 2 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    dd, _ = cKDTree(Q).query(Q, k=2)
    FIELDS[k] = dict(centre=[float(c[0]), float(c[1])], L=float(L), W=float(W), long_axis_deg=float(ang), n_pads=int(len(Q)), nn_pitch=float(np.median(dd[:, 1])),
                     box=[list(map(float, p)) for p in box], r_centre=float(math.hypot(*c)), ang_centre=float(math.degrees(math.atan2(c[1], c[0]))),
                     axis_line_dist_from_origin=float(abs(c[0] * d1[1] - c[1] * d1[0])), note="extent of pad CENTRES (add ~1 mm for the pad field edge)")
# pitch check on the PSU-side field (FFT of the rectified intensity)
def fft_period(x0, x1, y0, y1, axis):
    c0 = int((x0 + EXT) * K); c1 = int((x1 + EXT) * K); r0 = int((EXT - y1) * K); r1 = int((EXT - y0) * K); sub = ib[r0:r1, c0:c1]
    p = sub.mean(0) if axis == 0 else sub.mean(1); p = p - p.mean(); n = np.arange(len(p)); w = np.hanning(len(p)); Ts = np.linspace(8.0, 12.0, 4000)
    return float(Ts[int(np.argmax([abs((w * p * np.exp(-2j * np.pi * n / T)).sum()) for T in Ts]))] / K)
PITCH = dict(x=fft_period(-22, 18, -56, -41, 0), y=fft_period(-20, 16, -57, -40, 1))
# ---------- outputs ----------
def r3(v): return [round(float(a), 2) for a in v]
holes = {k: dict(bp=r3(BPF[k]), r=round(float(np.linalg.norm(BPF[k])), 2), ang=round(math.degrees(math.atan2(BPF[k][1], BPF[k][0])), 1),
                 pad_or_ring_d=round(FE[k]["d"], 2), hole_d=round(FE[k].get("inner_d", float("nan")), 2) if "inner_d" in FE[k] else None) for k in ("G1", "G2", "S1", "S2", "S3", "S4", "S5", "S6")}
OTHER = {"dark_round_part_-y_rim": (-0.1, -59.7), "dark_round_part_+y": (0.2, 50.5), "dark_square_bottom_-x": (-45.2, -14.2), "small_dim_pad_+y": (-7.0, 56.7),
         "bottom_IC_~8x8": (31.0, -35.0), "tall_part_+x_-y (white block)": (45.7, -35.0), "top_IC_under_tweezers_~10x12 (+-2)": (1.0, 20.0)}
res = dict(
    calibration=dict(bottom={k: cb[k] for k in ("SX", "SY", "aniso_pct", "unc_pct")}, top={k: ct[k] for k in ("SX", "SY", "aniso_pct", "unc_pct")}),
    frame="BP frame, top view. Origin = midpoint of the two gold Ø4 holes; +x toward G2 (key end of the CPU socket); +y toward the GPU connectors (core); -y = PSU side",
    disc=dict(D_bottom_by_threshold={f["T"]: round(f["D"], 2) for f in fb}, D=round(fbm["D"], 2), sd=round(fbm["sd"], 3), max_dev=round(fbm["maxdev"], 2),
              centre_bottom=r3(disc_b), centre_top=r3(disc_t), D_top_by_threshold={f["T"]: round(f["D"], 2) for f in ft}),
    holes=holes, hole_pitch=round(float(np.linalg.norm(G2 - G1)), 2),
    registration=dict(rms_mm=round(reg_rms, 2), residuals={k: r3(v) for k, v in zip(TB, reg_res)}),
    cpu_socket=dict(top_frame=dict(centre=r3(SOCK_OUT["c"]), L=round(SOCK_OUT["L"], 2), W=round(SOCK_OUT["W"], 2), by_threshold={T: [r3(v["outer"][0]), round(wh(v["outer"])[0], 2), round(wh(v["outer"])[1], 2)] for T, v in soc.items()}),
                    top_slot=dict(centre=r3(SOCK_SLOT["c"]), L=round(SOCK_SLOT["L"], 2), W=round(SOCK_SLOT["W"], 2)), key_crossbar_x=round(KEY_X, 2),
                    bottom_pegs={k: dict(bp=r3(BPF[k]), d=round(FE[k]["d"], 2)) for k in FE if k.startswith("PEG")},
                    centre_from_end_pegs=r3(SOCK_C_PEGS), end_peg_span=round(float(np.linalg.norm(PEG_B - PEG_A)), 2), key_pegs_x=round(float(PEG_K[0]), 2),
                    axis_deg_vs_hole_axis=round(SOCK_ANG, 2)),
    connector_fields={k: {kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "box"} for k, v in FIELDS.items()},
    other_features=OTHER, scale_check_pad_pitch_mm=PITCH)
json.dump(res, open("base_board.json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
# DXF in BP frame
doc = ezdxf.new("R2010"); doc.units = ezdxf.units.MM; msp = doc.modelspace()
for ln, col in (("DISC_OUTLINE", 7), ("HOLES_GOLD_D4", 2), ("HOLES_SMALL", 3), ("CPU_SOCKET_FRAME", 1), ("CPU_SOCKET_SLOT", 1), ("CPU_SOCKET_PEGS", 6), ("CPU_SOCKET_KEY", 6),
                ("CONN_FIELDS", 4), ("OTHER", 8), ("BP_KICAD_REF", 9), ("NOTES", 7)): doc.layers.add(ln, color=col)
msp.add_circle(tuple(disc_b), fbm["D"] / 2, dxfattribs={"layer": "DISC_OUTLINE"})
for k, h in holes.items():
    L = "HOLES_GOLD_D4" if k[0] == "G" else "HOLES_SMALL"; msp.add_circle(tuple(h["bp"]), h["pad_or_ring_d"] / 2, dxfattribs={"layer": L})
    if h["hole_d"]: msp.add_circle(tuple(h["bp"]), h["hole_d"] / 2, dxfattribs={"layer": L})
    msp.add_text(k, height=1.5, dxfattribs={"layer": "NOTES"}).set_placement((h["bp"][0] + 2.5, h["bp"][1] + 2.5))
for key, L in ((so["outer"], "CPU_SOCKET_FRAME"), (so["slot"], "CPU_SOCKET_SLOT")): msp.add_lwpolyline([tuple(p) for p in cv2.boxPoints(key)], close=True, dxfattribs={"layer": L})
for k in FE:
    if k.startswith("PEG"): msp.add_circle(tuple(BPF[k]), FE[k]["d"] / 2, dxfattribs={"layer": "CPU_SOCKET_PEGS"})
msp.add_line((KEY_X, SOCK_SLOT["c"][1] - 3), (KEY_X, SOCK_SLOT["c"][1] + 3), dxfattribs={"layer": "CPU_SOCKET_KEY"})
for k, v in FIELDS.items(): msp.add_lwpolyline([tuple(p) for p in v["box"]], close=True, dxfattribs={"layer": "CONN_FIELDS"}); msp.add_text(k.split(" ")[0], height=1.5, dxfattribs={"layer": "NOTES"}).set_placement(tuple(v["centre"]))
for k, p in OTHER.items(): msp.add_circle(p, 1.5, dxfattribs={"layer": "OTHER"})
bpk = json.load(open("work/bp_kicad_fps.json"))
for ref in ("J1", "J9", "J10", "H1", "H2", "J2", "J3", "J4", "J6", "J7"):
    c = bpk[ref]["courtyard"]
    if c: msp.add_lwpolyline([tuple(p) for p in c], close=True, dxfattribs={"layer": "BP_KICAD_REF"})
msp.add_text("Stock base board traced from scans; BP frame (hole-axis origin). BP_KICAD_REF = current backplane courtyards (disc-centre origin, drawn as-is).", height=2, dxfattribs={"layer": "NOTES"}).set_placement((-64, -70))
doc.saveas("base_board_bp_frame.dxf")
# overlays
def ov(img, path, kicad=False):
    v = img.copy()
    def P(x, y): c, r = toPX(x, y); return (int(round(c)), int(round(r)))
    cv2.circle(v, P(*disc_b), int(fbm["D"] / 2 * K), (0, 255, 255), 1)
    for k, h in holes.items():
        cv2.circle(v, P(*h["bp"]), int(h["pad_or_ring_d"] / 2 * K), (0, 255, 0), 1); cv2.putText(v, k, P(h["bp"][0] + 3, h["bp"][1] + 3), 0, 0.45, (0, 255, 0), 1)
    for key in (so["outer"], so["slot"]): cv2.polylines(v, [np.array([P(*p) for p in cv2.boxPoints(key)], np.int32)], True, (0, 0, 255), 1)
    for k in FE:
        if k.startswith("PEG"): cv2.circle(v, P(*BPF[k]), int(FE[k]["d"] / 2 * K), (255, 0, 255), 1)
    cv2.line(v, P(KEY_X, SOCK_SLOT["c"][1] - 4), P(KEY_X, SOCK_SLOT["c"][1] + 4), (255, 0, 255), 2)
    for k, f in FIELDS.items(): cv2.polylines(v, [np.array([P(*p) for p in f["box"]], np.int32)], True, (255, 160, 0), 1)
    if kicad:
        for ref in ("J1", "J9", "J10", "H1", "H2", "J2", "J3", "J4", "J6", "J7"):
            c = bpk[ref]["courtyard"]
            if c: cv2.polylines(v, [np.array([P(*p) for p in c], np.int32)], True, (60, 60, 255), 1); cv2.putText(v, ref, P(*bpk[ref]["pos"]), 0, 0.45, (60, 60, 255), 1)
    for vv in range(-60, 61, 10):
        cv2.putText(v, str(vv), P(vv, -63), 0, 0.35, (200, 200, 200), 1); cv2.putText(v, str(vv), P(-63.5, vv), 0, 0.35, (200, 200, 200), 1)
    cv2.line(v, P(-62, 0), P(62, 0), (90, 90, 90), 1); cv2.line(v, P(0, -62), P(0, 62), (90, 90, 90), 1)
    cv2.imwrite(path, v)
ov(rect_b, "base_board_overlay_bottom_bpframe.png"); ov(rect_t, "base_board_overlay_top_bpframe.png"); ov(rect_b, "base_board_vs_bp_kicad.png", kicad=True)
print(json.dumps({k: res[k] for k in ("disc", "hole_pitch", "registration")}, indent=1, default=str))
print(json.dumps(res["cpu_socket"], indent=1, default=str)); print(json.dumps(res["connector_fields"], indent=1, default=str)); print(json.dumps(holes, indent=1))
