import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
im = np.asarray(Image.open("prints_vs_stock_scan.jpg").convert("L")).astype(float)
SY = 7.875
plates = {"P1_top": (40, 530), "P2": (495, 960), "P3": (975, 1460), "STOCK": (1455, 1915)}
out = {}
for nm, (r0, r1) in plates.items():
    Ws = []; T = []; B = []; C = []
    for c in range(330, 1000, 8):
        strip = im[r0:r1, c - 15:c + 16]
        p = strip.mean(1)
        bg = np.median(p[:8]); k = np.argmax(p < (bg + 40) / 2); t = r0 + k - 1 + (p[k - 1] - (bg + 40) / 2) / (p[k - 1] - p[k])
        if nm == "STOCK":
            q = p[k + 395:k + 435]; b = r0 + k + 395 + np.argmin(q) + 0.5
        else:
            d2 = np.abs(np.diff(p, 2)); e = nd.uniform_filter1d(d2, 5)
            ref = np.median(e[k + 330:k + 380])          # texture energy inside the plate near the bottom edge
            j = k + 380
            while j < len(e) - 1 and e[j] > 0.35 * ref: j += 1
            b = r0 + j + 1
        Ws.append((b - t) / SY); T.append(t); B.append(b); C.append(c)
    Ws = np.array(Ws)
    out[nm] = dict(W_median=float(np.median(Ws)), W_iqr=float(np.subtract(*np.percentile(Ws, [75, 25]))), n=len(Ws))
    print(nm, "W median %.2f  IQR %.2f  min %.2f max %.2f" % (np.median(Ws), out[nm]["W_iqr"], Ws.min(), Ws.max()))
json.dump(out, open("width_fit.json", "w"), indent=1)
