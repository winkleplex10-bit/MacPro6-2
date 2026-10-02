#!/usr/bin/env python3
"""Trace the stock I/O plate (rear port cover) from Aidan's two flatbed scans (outer face, inner face).
Scale: same rulers as all scans (scanlib.calibrate). Frame: the I/O BOARD back-view frame of bracket/io_board/
(origin board bottom-left, X right, Y up toward the MEG edge; front view = mirror X_f = 101 - X), so the plate overlays
io_board_outline.dxf / io_board_ports.dxf directly. Registration: plate openings <-> traced board ports (reflection allowed).
Run: /workspace/cadenv/bin/python trace_io_plate.py"""
import json, os, sys, math
import cv2, numpy as np, ezdxf
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, "../scanlib"); import scanlib
from seg_plate import seg
OUT, INN = "io_plate_outer_scan.jpeg", "io_plate_inner_scan.jpeg"
cal = scanlib.calibrate(OUT); SX, SY = cal["SX"], cal["SY"]
mm = lambda p: np.array([p[0] / SX, -p[1] / SY])
B = {"AC": (50.43, 131.06), "HDMI": (42.8, 107.8), "ETH_1": (63.6, 92.9), "ETH_2": (42.7, 92.6), "TB_a1": (64.1, 74.7), "TB_a2": (64.1, 65.0), "TB_a3": (64.0, 55.4),
     "TB_b1": (42.6, 74.8), "TB_b2": (42.5, 65.1), "TB_b3": (42.5, 55.5), "USB_a1": (63.9, 42.9), "USB_a2": (63.8, 32.5), "USB_b1": (43.5, 42.9), "USB_b2": (43.5, 32.6)}
def classify(h):
    w, hh, a = h["w"], h["h"], h["area"]; big, small = max(w, hh), min(w, hh)
    if a > 500: return "AC_INLET"
    if 13.5 < big < 16.5 and 4.8 < small < 7 and a > 55 and h["cy"] < 500 and ("hdmi" not in h): return "HDMI?"
    if 11.5 < big < 15 and 9.5 < small < 12.5: return "ETHERNET"
    if 7.5 < big < 10 and 4.8 < small < 6.6: return "TB2"
    if 12.5 < big < 15 and 5.2 < small < 7: return "USB_A?"
    if 4.0 < big < 5.8 and 4.0 < small < 5.8 and h["circ"] > 0.85: return "AUDIO_JACK"
    return "small/icon"
def run(path, thr):
    r = seg(path, thr, os.path.basename(path)[:9] + str(thr))
    for h in r["holes"]: h["kind"] = classify(h)
    return r
o70, o90 = run(OUT, 70), run(OUT, 90)
i70 = run(INN, 70)
# ---- outer: label ports by layout (rows from the AC end) ----
def label(holes, hdmi_side):
    ac = [h for h in holes if h["kind"] == "AC_INLET"][0]
    L = {"AC": ac}
    eth = sorted([h for h in holes if h["kind"] == "ETHERNET"], key=lambda h: h["cx"])
    tb = [h for h in holes if h["kind"] == "TB2"]; usb = [h for h in holes if h["kind"] == "USB_A?" and h["cy"] > 650 or (h["kind"] == "HDMI?" and h["cy"] > 650)]
    hd = [h for h in holes if h["kind"] in ("HDMI?", "USB_A?") and abs(h["cy"] - ac["cy"]) < 140 and h["area"] > 55][0]
    L["HDMI"] = hd
    # column split by x relative to the AC centre line (perpendicular to plate axis approx.)
    xc = ac["cx"]
    side = lambda h: "H" if (h["cx"] > xc) == (hd["cx"] > xc) else "O"   # H = HDMI column, O = other column
    for grp, lst in (("ETH", eth), ("TB", tb), ("USB", usb)):
        for s in ("H", "O"):
            col = sorted([h for h in lst if side(h) == s], key=lambda h: abs(h["cy"] - ac["cy"]))
            for i, h in enumerate(col): L["%s_%s%d" % (grp, s, i + 1)] = h
    aud = sorted([h for h in holes if h["kind"] == "AUDIO_JACK"], key=lambda h: h["cx"])
    for h in aud: L["AUDIO_%s" % side(h)] = h
    return L
Lo = label(o70["holes"], None)
MAP = {"AC": "AC", "HDMI": "HDMI", "ETH_H1": "ETH_2", "ETH_O1": "ETH_1", "TB_H1": "TB_b1", "TB_H2": "TB_b2", "TB_H3": "TB_b3", "TB_O1": "TB_a1", "TB_O2": "TB_a2",
       "TB_O3": "TB_a3", "USB_H1": "USB_b1", "USB_H2": "USB_b2", "USB_O1": "USB_a1", "USB_O2": "USB_a2"}
keys = [k for k in MAP if k in Lo]
A = np.array([B[MAP[k]] for k in keys]); S = np.array([mm((Lo[k]["cx"], Lo[k]["cy"])) for k in keys])
R, t, rms, res = scanlib.procrustes(A, S, allow_reflection=True)        # S = R A + t
to_board = lambda p: R.T @ (mm(p) - t)
print("outer->board rms %.3f det %+.0f" % (rms, np.linalg.det(R)))
# ---- power button ring (outer) ----
g = cv2.imread(OUT, 0); hd = Lo["HDMI"]; ac = Lo["AC"]
guess = (2 * ac["cx"] - hd["cx"] + (hd["cx"] - ac["cx"]) * 0 , hd["cy"])  # other column, HDMI row
cand = [h for h in o70["holes"] if h["kind"] == "small/icon" and abs(h["cy"] - hd["cy"]) < 12 and abs(h["cx"] - hd["cx"]) > 40]
bx, by = (cand[0]["cx"], cand[0]["cy"]) if cand else guess
z = cv2.GaussianBlur(g[int(by) - 40:int(by) + 40, int(bx) - 40:int(bx) + 40], (5, 5), 1.5)
hc = cv2.HoughCircles(cv2.resize(z, None, fx=4, fy=4), cv2.HOUGH_GRADIENT, dp=1, minDist=400, param1=40, param2=12, minRadius=60, maxRadius=110)
btn = None
if hc is not None:
    c0 = hc[0][0]; btn = dict(cx=int(bx) - 40 + c0[0] / 4, cy=int(by) - 40 + c0[1] / 4, d=2 * c0[2] / 4 / SX)
print("power button", btn)
# ---- outline (outer) in board frame ----
def outline_board(r):
    pts = np.array([to_board(p) for p in r["outline"]]); return pts
ol = outline_board(o70); ol90 = outline_board(o90)
rect = cv2.minAreaRect((ol * 100).astype(np.float32)); rect90 = cv2.minAreaRect((ol90 * 100).astype(np.float32))
pl = dict(centre=[round(rect[0][0] / 100, 2), round(rect[0][1] / 100, 2)], size_thr70=sorted([round(v / 100, 2) for v in rect[1]]),
          size_thr90=sorted([round(v / 100, 2) for v in rect90[1]]), angle_deg=round(rect[2], 2),
          x_range=[round(ol[:, 0].min(), 2), round(ol[:, 0].max(), 2)], y_range=[round(ol[:, 1].min(), 2), round(ol[:, 1].max(), 2)])
# corner radius estimate: area deficit of the outline vs its rectangle: A_rect - A = (4 - pi) r^2
A_out = cv2.contourArea((ol * 100).astype(np.float32)) / 1e4; wr, hr = rect[1][0] / 100, rect[1][1] / 100
pl["corner_r_est"] = round(math.sqrt(max(0, wr * hr - A_out) / (4 - math.pi)), 1)
print("plate", pl)
# ---- openings table (outer), board frame ----
rows = []
for k, h in Lo.items():
    c = to_board((h["cx"], h["cy"]))
    d = None
    if k in MAP: d = (np.array(B[MAP[k]]) - c).round(2).tolist()
    h90 = min(o90["holes"], key=lambda q: (q["cx"] - h["cx"]) ** 2 + (q["cy"] - h["cy"]) ** 2)
    rows.append(dict(id=k, kind=h["kind"].rstrip("?"), board_port=MAP.get(k), centre=c.round(2).tolist(), w=round((h["w"] + h90["w"]) / 2, 2), h=round((h["h"] + h90["h"]) / 2, 2),
                     w_thr70_90=[round(h["w"], 2), round(h90["w"], 2)], h_thr70_90=[round(h["h"], 2), round(h90["h"], 2)], board_minus_plate=d))
if btn: rows.append(dict(id="POWER_BUTTON", kind="POWER_BUTTON", centre=to_board((btn["cx"], btn["cy"])).round(2).tolist(), w=round(btn["d"], 2), h=round(btn["d"], 2)))
icons = [h for h in o70["holes"] if h["kind"] == "small/icon"]
for h in icons: h["board"] = to_board((h["cx"], h["cy"])).round(2).tolist()
for r_ in rows: print(r_["id"], r_["kind"], r_["centre"], r_["w"], "x", r_["h"], "d", r_.get("board_minus_plate"))
# ---- inner: register to outer via NN on port openings (reflection) ----
big_o = [(k, h) for k, h in Lo.items()]
Si = [h for h in i70["holes"] if h["kind"] not in ("small/icon",)]
best = None
for sx in (1, -1):
    for sy in (1, -1):
        # initial: align centroids of big openings with a flip, then iterate NN + procrustes
        Po = np.array([mm((h["cx"], h["cy"])) for _, h in big_o]); Pi = np.array([mm((h["cx"], h["cy"])) for h in Si])
        Pi0 = (Pi - Pi.mean(0)) * [sx, sy]
        ang = 0
        for it in range(6):
            Rm = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
            Q = Pi0 @ Rm.T + Po.mean(0)
            pairs = [(i, int(np.argmin(((Po - q) ** 2).sum(1)))) for i, q in enumerate(Q)]
            pairs = [(i, j) for i, j in pairs if ((Po[j] - Q[i]) ** 2).sum() < 36]
            if len(pairs) < 5: break
            R2, t2, rms2, _ = scanlib.procrustes(Pi[[i for i, _ in pairs]], Po[[j for _, j in pairs]], allow_reflection=True)
            Q = Pi @ R2.T + t2; pairs = [(i, int(np.argmin(((Po - q) ** 2).sum(1)))) for i, q in enumerate(Q)]
            pairs = [(i, j) for i, j in pairs if ((Po[j] - Q[i]) ** 2).sum() < 9]
            ang = math.atan2(R2[1, 0], R2[0, 0]) if np.linalg.det(R2) > 0 else ang
        if len(pairs) >= 8:
            R2, t2, rms2, _ = scanlib.procrustes(Pi[[i for i, _ in pairs]], Po[[j for _, j in pairs]], allow_reflection=True)
            if best is None or rms2 < best[2]: best = (R2, t2, rms2, pairs, sx, sy)
R2, t2, rms2, pairs, _, _ = best
print("inner->outer rms %.3f det %+.0f n %d" % (rms2, np.linalg.det(R2), len(pairs)))
in_to_board = lambda p: R.T @ ((R2 @ mm(p) + t2) - t)
inner_rows = []
for h in i70["holes"]:
    c = in_to_board((h["cx"], h["cy"]))
    inner_rows.append(dict(kind=h["kind"].rstrip("?"), centre=c.round(2).tolist(), w=round(h["w"], 2), h=round(h["h"], 2), circ=round(h["circ"], 2)))
for r_ in inner_rows: print("inner", r_)
oli = np.array([in_to_board(p) for p in i70["outline"]])
json.dump(dict(calibration=cal, frame="I/O board back-view frame (bracket/io_board), mm", outer_to_board=dict(R=R.tolist(), t=t.tolist(), rms=rms),
               inner_to_outer=dict(R=R2.tolist(), t=t2.tolist(), rms=rms2, n=len(pairs)), plate=pl, openings_outer=rows,
               icons_outer=[dict(centre=h["board"], w=round(h["w"], 2), h=round(h["h"], 2)) for h in icons], features_inner=inner_rows,
               power_button_px=btn), open("io_plate.json", "w"), indent=1, default=float)
np.save("work/outline_outer_board.npy", ol); np.save("work/outline_inner_board.npy", oli)
