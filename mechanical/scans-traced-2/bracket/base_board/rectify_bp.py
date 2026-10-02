#!/usr/bin/env python3
"""Resample both base-board scans into the BP frame (top view, origin = hole-axis midpoint, +x toward the +x gold hole,
+y toward the core / GPU-connector side), K px/mm. Writes work/rect_bottom.png, work/rect_top.png (full) and grid crops."""
import json, math, sys, cv2, numpy as np
K = 8.0; EXT = 64.0
def maps(fn):     # returns image-pixel coordinates for each output pixel
    N = int(2 * EXT * K); xs = (np.arange(N) + 0.5) / K - EXT; ys = EXT - (np.arange(N) + 0.5) / K
    X, Y = np.meshgrid(xs, ys); return fn(X, Y)
B = json.load(open("work/bottom_feats.json")); F = B["feat"]; SXb, SYb = B["cal"]["SX"], B["cal"]["SY"]
mmb = lambda p: np.array([p[0] / SXb, p[1] / SYb])
G1 = mmb(F["G1"]["inner_px"]); G2 = mmb(F["G2"]["inner_px"]); O = (G1 + G2) / 2; u = (G2 - G1) / np.linalg.norm(G2 - G1); n = np.array([-u[1], u[0]])
def bot(X, Y):   # BP -> bottom image px: p_mm = O + x u + y n
    px = (O[0] + X * u[0] + Y * n[0]) * SXb; py = (O[1] + X * u[1] + Y * n[1]) * SYb; return px.astype(np.float32), py.astype(np.float32)
T = json.load(open("work/top_reg.json")); R = np.array(T["R"]); t = np.array(T["t"]); SXt, SYt = T["cal"]["SX"], T["cal"]["SY"]
def top(X, Y):   # q = R bp + t ; q = (X/SX, -Y/SY)
    qx = R[0, 0] * X + R[0, 1] * Y + t[0]; qy = R[1, 0] * X + R[1, 1] * Y + t[1]; return (qx * SXt).astype(np.float32), (-qy * SYt).astype(np.float32)
out = {}
for name, fn, src in (("bottom", bot, "base_board_bottom_scan.jpeg"), ("top", top, "base_board_top_scan.jpeg")):
    im = cv2.imread(src); mx, my = maps(fn); r = cv2.remap(im, mx, my, cv2.INTER_CUBIC); cv2.imwrite(f"work/rect_{name}.png", r); out[name] = r
def grid_crop(img, x0, x1, y0, y1, path, step=5, f=1.0):
    c0 = int((x0 + EXT) * K); c1 = int((x1 + EXT) * K); r0 = int((EXT - y1) * K); r1 = int((EXT - y0) * K)
    cr = img[r0:r1, c0:c1].copy()
    lab = cv2.cvtColor(cr, cv2.COLOR_BGR2LAB); lab[:, :, 0] = cv2.createCLAHE(2.5, (6, 6)).apply(lab[:, :, 0]); cr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    if f != 1: cr = cv2.resize(cr, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
    kk = K * f
    for v in np.arange(math.ceil(x0 / step) * step, x1, step):
        X = int((v - x0) * kk); col = (0, 255, 255) if v % 10 == 0 else (0, 110, 170); cv2.line(cr, (X, 0), (X, cr.shape[0]), col, 1)
        if v % 10 == 0: cv2.putText(cr, "%g" % v, (X + 2, 12), 0, 0.4, (0, 255, 255), 1)
    for v in np.arange(math.ceil(y0 / step) * step, y1, step):
        Y = int((y1 - v) * kk); col = (0, 255, 255) if v % 10 == 0 else (0, 110, 170); cv2.line(cr, (0, Y), (cr.shape[1], Y), col, 1)
        if v % 10 == 0: cv2.putText(cr, "%g" % v, (2, Y - 2), 0, 0.4, (0, 255, 255), 1)
    cv2.imwrite(path, cr)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        a = sys.argv; grid_crop(out[a[1]], float(a[2]), float(a[3]), float(a[4]), float(a[5]), a[6], step=float(a[7]) if len(a) > 7 else 5, f=float(a[8]) if len(a) > 8 else 1.0)
