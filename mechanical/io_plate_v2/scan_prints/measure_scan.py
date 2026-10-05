"""Measure the 3 printed plates vs the stock plate on Aidan's 200 dpi flatbed scan (2026-10-04 ~15:00 ET).
Step 1: outlines (rounded-rect fit) + through-openings of every plate, in mm, in each plate's own frame."""
import numpy as np, json, cv2, sys, os
from PIL import Image
from scipy import ndimage as nd
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "prints_vs_stock_scan.jpg")
SX, SY = 7.891, 7.875          # px/mm from the two rulers (horizontal 200.4 dpi, vertical 200.0 dpi)
im = np.asarray(Image.open(IMG).convert("L")).astype(np.uint8)
# resample to an isotropic 10 px/mm grid so all geometry is in mm
K = 10.0
iso = cv2.resize(im, (int(im.shape[1] / SX * K), int(im.shape[0] / SY * K)), interpolation=cv2.INTER_CUBIC)
dark = (iso < 120).astype(np.uint8)
dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
lab, n = nd.label(dark); sz = nd.sum(dark, lab, range(1, n + 1)); objs = nd.find_objects(lab)
big = [i for i in np.argsort(sz)[::-1][:4]]
big.sort(key=lambda i: objs[i].start if False else objs[i][0].start)
names = ["P1_top", "P2", "P3", "STOCK"]
out = {}
for nm, i in zip(names, big):
    m = (lab == i + 1).astype(np.uint8)
    filled = nd.binary_fill_holes(m).astype(np.uint8)
    filled = cv2.morphologyEx(filled, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    filled = nd.binary_fill_holes(filled).astype(np.uint8)
    cs, _ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); c = max(cs, key=cv2.contourArea)
    (cx, cy), (w, h), ang = cv2.minAreaRect(c)
    if w < h: w, h, ang = h, w, ang + 90
    A = cv2.contourArea(c) / K ** 2; L, W = w / K, h / K
    # refine L/W from the straight edges: rotate contour into the rect frame
    t = np.radians(ang); R = np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])
    p = (c[:, 0, :] - [cx, cy]) @ R.T / K            # mm, u along the length, v across
    u, v = p[:, 0], p[:, 1]
    mid = np.abs(u) < L / 2 - 20
    vt, vb = np.median(v[mid & (v < 0)]), np.median(v[mid & (v > 0)])
    side = np.abs(v - (vt + vb) / 2) < W / 2 - 15
    ul, ur = np.median(u[side & (u < 0)]), np.median(u[side & (u > 0)])
    Wm, Lm = vb - vt, ur - ul
    Rc = np.sqrt(max(Lm * Wm - A, 0) / (4 - np.pi))
    # per-corner radius: fit circles to the contour points in each corner zone
    cr = []
    for su in (-1, 1):
        for sv in (-1, 1):
            uc, vc = (ur if su > 0 else ul), (vb if sv > 0 else vt)
            sel = (su * (u - uc) > -16) & (sv * (v - vc) > -16)
            pu, pv = u[sel], v[sel]
            # keep points off the straight edges
            keep = (np.abs(pu - uc) > 0.4) & (np.abs(pv - vc) > 0.4)
            pu, pv = pu[keep], pv[keep]
            Am = np.c_[2 * pu, 2 * pv, np.ones_like(pu)]; b = pu ** 2 + pv ** 2
            s, *_ = np.linalg.lstsq(Am, b, rcond=None); r = np.sqrt(s[2] + s[0] ** 2 + s[1] ** 2)
            cr.append(dict(corner=("R" if su > 0 else "L") + ("B" if sv > 0 else "T"), r=round(float(r), 2), centre_from_edges=(round(float(abs(s[0] - uc)), 2), round(float(abs(s[1] - vc)), 2))))
    out[nm] = dict(centre_px_iso=(round(cx, 1), round(cy, 1)), angle_deg=round(ang, 3), L=round(Lm, 2), W=round(Wm, 2), area=round(A, 1), R_area=round(float(Rc), 2), corners=cr,
                   rect=dict(ul=float(ul), ur=float(ur), vt=float(vt), vb=float(vb)))
    print(nm, json.dumps({k: v for k, v in out[nm].items() if k != "rect"}))
json.dump(out, open(os.path.join(HERE, "outline_fit.json"), "w"), indent=1)
np.save("/tmp/iso.npy", iso)
