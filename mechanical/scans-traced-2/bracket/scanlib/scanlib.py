"""Shared helpers for Aidan's ~100 dpi flatbed scans (same ruler sheet: cm rulers right and bottom).
calibrate(img) -> px/mm in X (bottom ruler) and Y (two right rulers) from tick-period fits (FFT + least-squares)."""
import math, numpy as np, cv2
from scipy.optimize import minimize_scalar
def period(p, lo=3.7, hi=4.2):
    p = p - p.mean(); n = np.arange(len(p)); w = np.hanning(len(p))
    f = lambda T: -abs((w * p * np.exp(-2j * np.pi * n / T)).sum())
    Ts = np.linspace(lo, hi, 3000); v = [f(T) for T in Ts]; T0 = Ts[int(np.argmin(v))]
    return minimize_scalar(f, bounds=(T0 - 0.003, T0 + 0.003), method="bounded").x
def find_band(g, axis, lo, hi, span):
    """find the tick band: rows (axis='h') or cols (axis='v') in lo..hi with the strongest ~4 px periodicity"""
    best = None
    for k in range(lo, hi - 3):
        p = g[k:k + 3, span[0]:span[1]].mean(0) if axis == "h" else g[span[0]:span[1], k:k + 3].mean(1)
        p = p - p.mean(); F = np.abs(np.fft.rfft(p * np.hanning(len(p))))
        fr = np.fft.rfftfreq(len(p)); m = (fr > 1 / 4.2) & (fr < 1 / 3.7)
        s = F[m].max() / (F[1:].mean() + 1e-9)
        if best is None or s > best[0]: best = (s, k)
    return best[1], best[0]
def calibrate(path):
    g = cv2.imread(path, 0).astype(float)
    hb, hs = find_band(g, "h", 950, 1010, (70, 640))
    SX = period(g[hb:hb + 3, 70:640].mean(0))
    h2 = [period(g[hb:hb + 3, 70:355].mean(0)), period(g[hb:hb + 3, 355:640].mean(0))]
    vb1, s1 = find_band(g, "v", 655, 700, (150, 950))
    vb2, s2 = find_band(g, "v", 760, 800, (150, 950))
    SY1 = period(g[150:950, vb1:vb1 + 3].mean(1)); SY2 = period(g[150:950, vb2:vb2 + 3].mean(1))
    SY = (SY1 + SY2) / 2
    return dict(SX=float(SX), SY=float(SY), SY_rulers=[float(SY1), float(SY2)], SX_halves=[float(x) for x in h2],
                bands=dict(h=int(hb), v1=int(vb1), v2=int(vb2)), aniso_pct=float(100 * (SX / SY - 1)),
                unc_pct=float(100 * max(abs(h2[0] - h2[1]) / SX, abs(SY1 - SY2) / SY) / 2 + 0.2))
def fitc(x, y):
    A = np.c_[2 * x, 2 * y, np.ones_like(x)]; c = np.linalg.lstsq(A, x * x + y * y, rcond=None)[0]
    return float(c[0]), float(c[1]), float(math.sqrt(c[2] + c[0] ** 2 + c[1] ** 2))
def ring_fit(img, x0, y0, rmin, rmax, SX, SY, falling=True, n_iter=4):
    """sub-pixel circle fit on the strongest radial edge (falling = bright inside -> dark outside). img float gray."""
    import cv2
    cx, cy = float(x0), float(y0); f32 = img.astype(np.float32)
    for _ in range(n_iter):
        pts = []
        for a in np.linspace(0, 2 * math.pi, 90, endpoint=False):
            rs = np.linspace(rmin, rmax, 80); xs = cx + rs * math.cos(a); ys = cy + rs * math.sin(a)
            v = cv2.remap(f32, xs.astype(np.float32).reshape(1, -1), ys.astype(np.float32).reshape(1, -1), cv2.INTER_LINEAR)[0]
            d = np.diff(v); k = int(np.argmin(d) if falling else np.argmax(d)); pts.append((xs[k] + 0.5 * (xs[1] - xs[0]), ys[k] + 0.5 * (ys[1] - ys[0])))
        P = np.array(pts); X = P[:, 0] / SX; Y = P[:, 1] / SY; mx, my, r = fitc(X, Y)
        res = np.hypot(X - mx, Y - my) - r; k = np.abs(res) < max(0.25, 2.5 * np.median(np.abs(res))); mx, my, r = fitc(X[k], Y[k]); cx, cy = mx * SX, my * SY
    res = np.hypot(X - mx, Y - my) - r
    return cx, cy, 2 * r, float(np.std(res[k]))
def procrustes(A, B, allow_reflection=False):
    """find R,t with B ~ R A + t (A,B: Nx2). returns R, t, rms, residuals"""
    ca, cb = A.mean(0), B.mean(0); U, S, Vt = np.linalg.svd((A - ca).T @ (B - cb)); R = Vt.T @ U.T
    if np.linalg.det(R) < 0 and not allow_reflection:
        Vt[-1] *= -1; R = Vt.T @ U.T
    t = cb - R @ ca; res = B - (A @ R.T + t); return R, t, float(np.sqrt((res ** 2).sum(1).mean())), res
