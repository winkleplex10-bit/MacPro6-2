#!/usr/bin/env python3
"""Stage 2 of the PSU-board trace (supersedes the frame of stage 1).
Finding: the outline (tab widths/protrusions, hole-to-edge distances) shows the scanned board is the CAD outline turned end
for end: the end with the lug pads is the CAD TOP-tab end (+y). Stage 1 had registered the 6 holes the wrong way round (the
hole pattern alone is ambiguous by 180 deg + 10.1 mm shift).
Frame used here: CAD frame (/workspace/macpro62-cad/psu_board_outline.dxf) VIEWED FROM THE COMPONENT SIDE [Assumption: the
CAD is drawn from the component side]; the solder scan is mirrored into it (y-flip registration). If the CAD is a solder-side
drawing instead, x changes sign (outline is symmetric to 0.4 mm, so geometry cannot decide).
Run: /workspace/cadenv/bin/python trace_psu_board2.py"""
import json, os, sys
import cv2, numpy as np, ezdxf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "scanlib")); import scanlib
os.chdir(HERE)
SOL, COMP = "psu_board_solder_scan.jpeg", "psu_board_component_scan.jpeg"
c = scanlib.calibrate(SOL); SX, SY = c["SX"], c["SY"]; g8 = cv2.imread(SOL, 0)
CAD = {"L-top": (-48.0, 58.95), "L-mid": (-48.0, -5.05), "L-bot": (-48.0, -69.05), "R-top": (47.956, 58.548), "R-mid": (47.956, -5.452), "R-bot": (47.956, -69.452)}
SEEDS = {"s-TL": (219, 252), "s-TR": (586, 257), "s-ML": (203, 500), "s-MR": (583, 512), "s-BL": (203, 760), "s-BR": (583, 763)}
HO = {}
for k, (x, y) in SEEDS.items():
    w = 40; t = g8[y - w:y + w, x - w:x + w]; z = cv2.GaussianBlur(cv2.resize(t, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC), (7, 7), 2)
    h = cv2.HoughCircles(z, cv2.HOUGH_GRADIENT, dp=1, minDist=300, param1=60, param2=15, minRadius=40, maxRadius=70)[0][0]
    HO[k] = (float(x - w + h[0] / 4), float(y - w + h[1] / 4), float(h[2] / 2 / SX))
S = lambda keys: np.array([[HO[k][0] / SX, -HO[k][1] / SY] for k in keys])
OPTS = {  # scan label -> CAD label
 "stage1 (as registered before)": dict(zip(SEEDS, ["L-top", "R-top", "L-mid", "R-mid", "L-bot", "R-bot"])),
 "y-mirror (solder view of a component-view CAD)": dict(zip(SEEDS, ["L-bot", "R-bot", "L-mid", "R-mid", "L-top", "R-top"])),
 "180 deg rotation (CAD is a solder-view drawing)": dict(zip(SEEDS, ["R-bot", "L-bot", "R-mid", "L-mid", "R-top", "L-top"])),
}
res = {}
for name, mp in OPTS.items():
    A = np.array([CAD[mp[k]] for k in SEEDS]); B = S(SEEDS)
    R, t, rms, r = scanlib.procrustes(A, B, allow_reflection=True)
    res[name] = dict(R=R.tolist(), t=list(map(float, t)), rms=float(rms), det=float(np.linalg.det(R)))
    print("%-50s rms %.3f det %+.0f" % (name, rms, np.linalg.det(R)))
CH = "y-mirror (solder view of a component-view CAD)"
R = np.array(res[CH]["R"]); t = np.array(res[CH]["t"])
K, X0, X1, Y0, Y1 = 8.0, -62.0, 62.0, -92.0, 100.0
W_, H_ = int((X1 - X0) * K), int((Y1 - Y0) * K)
xs = X0 + (np.arange(W_) + 0.5) / K; ys = Y1 - (np.arange(H_) + 0.5) / K; XX, YY = np.meshgrid(xs, ys)
P = R @ np.vstack([XX.ravel(), YY.ravel()]) + t[:, None]
qx = P[0].reshape(XX.shape); qy = P[1].reshape(XX.shape)
rect = cv2.remap(cv2.imread(SOL), (qx * SX).astype(np.float32), (-qy * SY).astype(np.float32), cv2.INTER_CUBIC)
cv2.imwrite("work/rect2_solder_compview.png", rect)
json.dump(dict(cal=c, holes_px=HO, options=res, chosen=CH, rect=dict(K=K, X0=X0, X1=X1, Y0=Y0, Y1=Y1,
          file="work/rect2_solder_compview.png", note="CAD frame, component-side view (solder scan mirrored)")),
          open("work/reg2.json", "w"), indent=1)
print("hole fit Ø (mm):", {k: round(v[2] * 2, 2) for k, v in HO.items()})
