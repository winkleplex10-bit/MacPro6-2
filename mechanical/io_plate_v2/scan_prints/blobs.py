import numpy as np, cv2, json, os, sys
from scipy import ndimage as nd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from warp import warp, K, X0, Y1, to_px
def blob(w, x, y, ww, hh, thr, marg=3.0, bright=True):
    """bright connected blob nearest the predicted centre inside the feature box + margin; returns centroid / extents in model mm."""
    a = to_px(x - ww / 2 - marg, y + hh / 2 + marg); b = to_px(x + ww / 2 + marg, y - hh / 2 - marg)
    j0, i0, j1, i1 = int(a[0]), int(a[1]), int(b[0]), int(b[1])
    sub = w[i0:i1, j0:j1].astype(float)
    m = sub > thr if bright else sub < thr
    m = nd.binary_opening(m, iterations=1)
    lab, n = nd.label(m)
    if n == 0: return None
    cj, ci = (x - X0) * K - j0, (Y1 - y) * K - i0
    best = None
    for k in range(1, n + 1):
        ii, jj = np.nonzero(lab == k)
        if len(ii) < 15: continue
        d = np.hypot(ii.mean() - ci, jj.mean() - cj)
        if best is None or d < best[0]: best = (d, ii, jj, k)
    if best is None: return None
    _, ii, jj, k = best
    filled = nd.binary_fill_holes(lab == k); ii, jj = np.nonzero(filled)
    X = X0 + (jj + j0) / K; Y = Y1 - (ii + i0) / K
    # extents from robust percentiles (0.5 / 99.5) + half a pixel
    xl, xr = np.percentile(X, 0.3), np.percentile(X, 99.7); yb, yt = np.percentile(Y, 0.3), np.percentile(Y, 99.7)
    return dict(cx=float(X.mean()), cy=float(Y.mean()), w=float(xr - xl + 1 / K), h=float(yt - yb + 1 / K), area=float(len(ii) / K ** 2),
                touches=bool(ii.min() == 0 or jj.min() == 0 or ii.max() == sub.shape[0] - 1 or jj.max() == sub.shape[1] - 1))
