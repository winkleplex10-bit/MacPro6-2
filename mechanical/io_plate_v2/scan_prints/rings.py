import numpy as np, cv2, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from warp import K, X0, Y1, to_px
def ring(w, x, y, search=3.0, rmin=0.6, rmax=1.9):
    """best circle (centre, r) on the gradient magnitude around (x, y) [model mm]; returns cx, cy, r, score"""
    a = to_px(x - search - rmax - 1, y + search + rmax + 1); j0, i0 = int(a[0]), int(a[1]); n = int(2 * (search + rmax + 1) * K)
    sub = cv2.GaussianBlur(w[i0:i0 + n, j0:j0 + n].astype(np.float32), (5, 5), 1.2)
    gx = cv2.Sobel(sub, cv2.CV_32F, 1, 0); gy = cv2.Sobel(sub, cv2.CV_32F, 0, 1); G = np.hypot(gx, gy)
    th = np.linspace(0, 2 * np.pi, 64, endpoint=False)
    best = (-1, None)
    c0 = (x - X0) * K - j0, (Y1 - y) * K - i0
    for r in np.arange(rmin, rmax + 1e-6, 0.1):
        rr = r * K
        for dj in np.arange(-search * K, search * K + 1, 1.0):
            for di in np.arange(-search * K, search * K + 1, 1.0):
                cj, ci = c0[0] + dj, c0[1] + di
                xs = (cj + rr * np.cos(th)).astype(int); ys = (ci + rr * np.sin(th)).astype(int)
                s = G[ys, xs]
                sc = s.mean() - 0.5 * s.std()          # favour complete, uniform rings
                if sc > best[0]: best = (sc, (cj, ci, r))
    cj, ci, r = best[1]
    return dict(cx=X0 + (cj + j0) / K, cy=Y1 - (ci + i0) / K, r=float(r), score=float(best[0]))
