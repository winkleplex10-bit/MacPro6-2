#!/usr/bin/env python3
"""Trace Aidan's two flatbed scans of the stock Mac Pro 6,1 PSU board (solder side sharp, component side defocused).
Scale: cm rulers (scanlib.calibrate). Frame: the Fusion/CAD PSU frame (/workspace/macpro62-cad/psu_board_outline.dxf,
origin = CAD model origin ~ board centre, +y toward the top tab). The solder-side scan matches the CAD drawing WITHOUT a mirror
(registration on the 6 screw heads, rms ~0.55 mm); the CAD outline is left-right symmetric, so whether the CAD view is the solder
or component side is not decidable from geometry. Everything here is reported AS SEEN FROM THE SOLDER SIDE.
Run: /workspace/cadenv/bin/python trace_psu_board.py"""
import json, math, os, sys, itertools
import cv2, numpy as np, ezdxf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "scanlib")); import scanlib
os.chdir(HERE); os.makedirs("work", exist_ok=True)
SOL, COMP = "psu_board_solder_scan.jpeg", "psu_board_component_scan.jpeg"
c = scanlib.calibrate(SOL); SX, SY = c["SX"], c["SY"]; g8 = cv2.imread(SOL, 0)
CAD = {"L-top": (-48.0, 58.95), "L-mid": (-48.0, -5.05), "L-bot": (-48.0, -69.05), "R-top": (47.956, 58.548), "R-mid": (47.956, -5.452), "R-bot": (47.956, -69.452)}
SEEDS = {"L-top": (219, 252), "R-top": (586, 257), "L-mid": (203, 500), "R-mid": (583, 512), "L-bot": (203, 760), "R-bot": (583, 763)}
HO = {}
for k, (x, y) in SEEDS.items():
    w = 40; t = g8[y - w:y + w, x - w:x + w]; z = cv2.GaussianBlur(cv2.resize(t, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC), (7, 7), 2)
    h = cv2.HoughCircles(z, cv2.HOUGH_GRADIENT, dp=1, minDist=300, param1=60, param2=15, minRadius=40, maxRadius=70)[0][0]
    HO[k] = (float(x - w + h[0] / 4), float(y - w + h[1] / 4), float(h[2] / 2 / SX))
A = np.array([CAD[k] for k in CAD]); S = np.array([[HO[k][0] / SX, -HO[k][1] / SY] for k in CAD])
R, t, rms, res = scanlib.procrustes(A, S)                     # scan(y-up mm) = R cad + t
def s2c(px, py): return R.T @ (np.array([px / SX, -py / SY]) - t)
K, X0, X1, Y0, Y1 = 8.0, -62.0, 62.0, -100.0, 92.0
W_, H_ = int((X1 - X0) * K), int((Y1 - Y0) * K); xs = X0 + (np.arange(W_) + 0.5) / K; ys = Y1 - (np.arange(H_) + 0.5) / K; XX, YY = np.meshgrid(xs, ys)
qx = R[0, 0] * XX + R[0, 1] * YY + t[0]; qy = R[1, 0] * XX + R[1, 1] * YY + t[1]
rect = cv2.remap(cv2.imread(SOL), (qx * SX).astype(np.float32), (-qy * SY).astype(np.float32), cv2.INTER_CUBIC); cv2.imwrite("work/rect_solder.png", rect)
toPX = lambda x, y: ((x - X0) * K - 0.5, (Y1 - y) * K - 0.5)
gr = cv2.GaussianBlur(cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY).astype(float), (0, 0), 1.0)
# ---- edges by max-gradient along scan lines (board dark, background light) ----
def edge_x(y, xa, xb, side):     # side 'L': background left of the edge
    r = int((Y1 - y) * K); c0, c1 = int((xa - X0) * K), int((xb - X0) * K); p = gr[r - 2:r + 3, c0:c1].mean(0); d = np.diff(p)
    k = int(np.argmin(d) if side == "L" else np.argmax(d)); return X0 + (c0 + k + 1) / K
def edge_y(x, ya, yb, side):     # side 'B': background below the edge (larger y index)
    cc = int((x - X0) * K); r0, r1 = int((Y1 - yb) * K), int((Y1 - ya) * K); p = gr[r0:r1, cc - 2:cc + 3].mean(1); d = np.diff(p)
    k = int(np.argmax(d) if side == "B" else np.argmin(d)); return Y1 - (r0 + k + 1) / K
E = {}
E["left"] = [edge_x(y, -58, -45, "L") for y in np.arange(-60, 66, 2.0)]
E["right"] = [edge_x(y, 45, 58, "R") for y in np.arange(-60, 66, 2.0)]
E["top_main_L"] = [edge_y(x, 70, 82, "T") for x in np.arange(-46, -31, 1.0)]
E["top_main_R"] = [edge_y(x, 70, 82, "T") for x in np.arange(32, 46, 1.0)]
E["top_tab"] = [edge_y(x, 72, 86, "T") for x in np.arange(-24, 24, 1.0)]
E["bot_main_L"] = [edge_y(x, -80, -66, "B") for x in np.arange(-46, -42, 0.5)]
E["bot_main_R"] = [edge_y(x, -80, -66, "B") for x in np.arange(43, 47, 0.5)]
E["bot_tab"] = [edge_y(x, -86, -72, "B") for x in np.arange(-34, 34, 1.0)]
E["bot_tab_L_side"] = [edge_x(y, -44, -34, "L") for y in np.arange(-77.5, -75.0, 0.5)]
E["bot_tab_R_side"] = [edge_x(y, 34, 44, "R") for y in np.arange(-77.5, -75.0, 0.5)]
E["top_tab_L_side"] = [edge_x(y, -34, -22, "L") for y in np.arange(77.0, 78.6, 0.4)]
E["top_tab_R_side"] = [edge_x(y, 22, 34, "R") for y in np.arange(77.0, 78.6, 0.4)]
med = {k: float(np.median(v)) for k, v in E.items()}; spread = {k: float(np.percentile(v, 90) - np.percentile(v, 10)) for k, v in E.items()}
CADE = {"left": -51.5, "right": 51.456, "top_main_L": 75.966, "top_main_R": 75.966, "top_tab": 79.966, "bot_main_L": -72.55, "bot_main_R": -72.952, "bot_tab": -79.05,
        "bot_tab_L_side": -39.5, "bot_tab_R_side": 39.456, "top_tab_L_side": -28.0, "top_tab_R_side": 27.956}
edges = {k: dict(scan=round(med[k], 2), cad=CADE[k], delta=round(med[k] - CADE[k], 2), p10_p90=round(spread[k], 2)) for k in med}
W = med["right"] - med["left"]; H = med["top_tab"] - med["bot_tab"]
# ---- mounting holes: refine on the rectified image (screw heads) ----
gry = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY).astype(float); holes = {}
for k, (x, y) in CAD.items():
    cx, cy = toPX(x, y); o = scanlib.ring_fit(cv2.GaussianBlur(gry, (0, 0), 1.2), cx, cy, 8, 40, 1.0, 1.0)
    hx, hy = X0 + (o[0] + 0.5) / K, Y1 - (o[1] + 0.5) / K
    holes[k] = dict(scan_head_centre=[round(hx, 2), round(hy, 2)], head_d=round(o[2] / K, 2), cad=list(CAD[k]), delta=[round(hx - x, 2), round(hy - y, 2)], hough_res=None)
for (k, r_) in zip(CAD, res): holes[k]["hough_res"] = [round(float(r_[0]), 2), round(float(r_[1]), 2)]
json.dump(dict(cal=c, R=R.tolist(), t=t.tolist(), rms=rms), open("work/reg.json", "w"), indent=1)
res_out = dict(calibration={k: c[k] for k in ("SX", "SY", "aniso_pct", "unc_pct")}, registration_rms_mm=round(rms, 2),
               frame="CAD frame (psu_board_outline.dxf), viewed from the solder side as scanned; +y = top tab end; bottom tab = lug-pad end",
               edges=edges, width=round(W, 2), height_incl_tabs=round(H, 2), cad_width=102.956, cad_height=159.016, holes=holes)
json.dump(res_out, open("psu_board.json", "w"), indent=1)
print(json.dumps(res_out, indent=1))
