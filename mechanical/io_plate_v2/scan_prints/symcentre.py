import numpy as np, cv2, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from warp import K, X0, Y1
def sym_centre(w, x, y, rmax=1.8, search=0.8, step=0.05):
    """radial-symmetry centre: minimise the across-angle variance of the polar-resampled patch (r 0.3..rmax mm)"""
    img = cv2.GaussianBlur(w.astype(np.float32), (3, 3), 0.8)
    th = np.linspace(0, 2 * np.pi, 72, endpoint=False); rs = np.arange(0.3, rmax, 0.1)
    best = (1e18, None)
    for dx in np.arange(-search, search + 1e-9, step):
        for dy in np.arange(-search, search + 1e-9, step):
            cx, cy = x + dx, y + dy
            px = ((cx + np.outer(rs, np.cos(th))) - X0) * K; py = (Y1 - (cy + np.outer(rs, np.sin(th)))) * K
            v = cv2.remap(img, px.astype(np.float32), py.astype(np.float32), cv2.INTER_LINEAR)
            s = (v.var(axis=1) * rs).sum() / rs.sum()
            if s < best[0]: best = (s, (cx, cy))
    return best[1][0], best[1][1], best[0]
