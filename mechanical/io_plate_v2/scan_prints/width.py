import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
im = np.asarray(Image.open("prints_vs_stock_scan.jpg").convert("L")).astype(float)
SX, SY = 7.891, 7.875
plates = {"P1_top": (40, 530), "P2": (495, 960), "P3": (975, 1460), "STOCK": (1455, 1915)}
res = {}
for nm, (r0, r1) in plates.items():
    tops, bots, cols = [], [], []
    for c in range(330, 1000, 6):
        p = im[r0:r1, c - 2:c + 3].mean(1)
        bg = np.median(p[:8])
        # top edge: first crossing below (bg + plate)/2 coming from the top
        k = np.argmax(p < (bg + 40) / 2)
        if k == 0: continue
        t = r0 + k - 1 + (p[k - 1] - (bg + 40) / 2) / (p[k - 1] - p[k])
        if nm == "STOCK":
            # bottom: thin dark edge line inside the lower grey band
            q = p[int(t - r0) + 380:int(t - r0) + 440]; kk = np.argmin(q); b = r0 + int(t - r0) + 380 + kk
        else:
            # bottom: end of the printed-line texture (local std along the column)
            z0 = int(t - r0) + 385; z1 = int(t - r0) + 440
            seg = p[z0:z1]; s = nd.generic_filter(seg, np.std, size=5)
            bright = np.nonzero(seg > 120)[0]; lim = bright[0] if len(bright) else len(seg)   # start of the bright background (after the shadow)
            tex = np.nonzero(s[:lim] > 10)[0]
            if len(tex) == 0: continue
            b = r0 + z0 + tex[-1] - 1                 # last textured row = material edge (the smooth band after it is the shadow)
        tops.append(t); bots.append(b); cols.append(c)
    tops, bots, cols = map(np.array, (tops, bots, cols))
    at = np.polyfit(cols, tops, 1); ab = np.polyfit(cols, bots, 1)
    ang = np.arctan((at[0] + ab[0]) / 2 * SX / SY)
    W = (np.polyval(ab, cols) - np.polyval(at, cols)) / SY * np.cos(ang)
    rt = tops - np.polyval(at, cols); rb = bots - np.polyval(ab, cols)
    res[nm] = dict(W_mean=float(W.mean()), W_std_px_fit=(float(rt.std()), float(rb.std())), slope_t=float(at[0]), slope_b=float(ab[0]), n=len(cols))
    print(nm, "W %.2f mm  (top-fit rms %.1f px, bottom-fit rms %.1f px, slopes %.4f / %.4f, n %d)" % (W.mean(), rt.std(), rb.std(), at[0], ab[0], len(cols)))
json.dump(res, open("width_fit.json", "w"), indent=1)
