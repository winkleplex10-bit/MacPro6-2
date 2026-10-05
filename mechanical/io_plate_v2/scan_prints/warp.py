"""Warp each plate of the scan into MODEL coordinates (X across, Y along; mm, 10 px/mm), back view (= inner face seen from the board), using the outline fit."""
import numpy as np, json, cv2, os
HERE = os.path.dirname(os.path.abspath(__file__))
K = 10.0
OF = json.load(open(os.path.join(HERE, "outline_fit.json")))
PL_C = (53.19, 77.07)
X0, X1, Y0, Y1 = 20.0, 86.4, -12.0, 166.0
# orientation of each plate on the scan: image u (along, right) / v (across, down) in terms of model (X, Y).
# prints: AC (model Y high) on the LEFT, power button (X 43 < centre) in the TOP row  -> u = -(Y - Yc), v = +(X - Xc)
# stock : rotated 180 deg on the glass                                                    -> u = +(Y - Yc), v = -(X - Xc)
ORI = {"P1_top": (-1, +1), "P2": (-1, +1), "P3": (-1, +1), "STOCK": (+1, -1)}
def warp(iso, name, dxy=(0.0, 0.0), dang=0.0):
    o = OF[name]; cx, cy = o["centre_px_iso"]; t = np.radians(o["angle_deg"] + dang)
    # outline centre in the plate frame (rect centre may differ from the minAreaRect centre)
    uc = (o["rect"]["ul"] + o["rect"]["ur"]) / 2; vc = (o["rect"]["vt"] + o["rect"]["vb"]) / 2
    su, sv = ORI[name]
    W, H = int((X1 - X0) * K), int((Y1 - Y0) * K)
    j, i = np.meshgrid(np.arange(W), np.arange(H))
    X = X0 + j / K; Y = Y1 - i / K                      # row 0 = top = Y1 (Y up), X right
    u = su * (Y - PL_C[1] - dxy[1]) + uc; v = sv * (X - PL_C[0] - dxy[0]) + vc
    px = cx + K * (u * np.cos(t) - v * np.sin(t)); py = cy + K * (u * np.sin(t) + v * np.cos(t))
    return cv2.remap(iso, px.astype(np.float32), py.astype(np.float32), cv2.INTER_LINEAR, borderValue=255)
def to_px(x, y): return ((x - X0) * K, (Y1 - y) * K)
