import numpy as np, cv2, os, sys
from scipy import ndimage as nd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from warp import K, X0, Y1, to_px
def blob_otsu(w, x, y, ww, hh, marg=2.0, min_contrast=25):
    a = to_px(x - ww / 2 - marg, y + hh / 2 + marg); b = to_px(x + ww / 2 + marg, y - hh / 2 - marg)
    j0, i0, j1, i1 = max(int(a[0]), 0), max(int(a[1]), 0), int(b[0]), int(b[1])
    sub = cv2.GaussianBlur(w[i0:i1, j0:j1], (3, 3), 0)
    t, m = cv2.threshold(sub, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU); m = m > 0
    lo, hi = sub[~m].mean() if (~m).any() else 0, sub[m].mean() if m.any() else 0
    if hi - lo < min_contrast: return None
    m = nd.binary_opening(m, iterations=2); lab, n = nd.label(m)
    cj, ci = (x - X0) * K - j0, (Y1 - y) * K - i0; best = None
    for k in range(1, n + 1):
        ii, jj = np.nonzero(lab == k)
        if len(ii) < 20: continue
        inside = lab[int(np.clip(ci, 0, lab.shape[0] - 1)), int(np.clip(cj, 0, lab.shape[1] - 1))] == k
        d = 0 if inside else np.hypot(ii.mean() - ci, jj.mean() - cj)
        if best is None or d < best[0]: best = (d, k)
    if best is None: return None
    f = nd.binary_fill_holes(lab == best[1]); ii, jj = np.nonzero(f)
    X = X0 + (jj + j0) / K; Y = Y1 - (ii + i0) / K
    rows = np.unique(ii); cols = np.unique(jj)
    return dict(cx=float(X.mean()), cy=float(Y.mean()), x0=float(X.min() - 0.05), x1=float(X.max() + 0.05), y0=float(Y.min() - 0.05), y1=float(Y.max() + 0.05),
                area=float(len(ii) / K ** 2), thr=float(t), contrast=float(hi - lo),
                touches=bool(ii.min() == 0 or jj.min() == 0 or ii.max() == sub.shape[0] - 1 or jj.max() == sub.shape[1] - 1))
