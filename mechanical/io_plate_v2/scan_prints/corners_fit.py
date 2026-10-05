import numpy as np, json, cv2
from scipy import ndimage as nd
iso = np.load("/tmp/iso.npy"); K = 10.0
OF = json.load(open("outline_fit.json"))
dark = (iso < 120).astype(np.uint8); dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
lab, n = nd.label(dark); out = {}
def fit_circle(pu, pv):
    A = np.c_[2 * pu, 2 * pv, np.ones_like(pu)]; b = pu ** 2 + pv ** 2
    s, *_ = np.linalg.lstsq(A, b, rcond=None); return s[0], s[1], np.sqrt(s[2] + s[0] ** 2 + s[1] ** 2)
for nm, o in OF.items():
    cx, cy = o["centre_px_iso"]; i = lab[int(cy), int(cx)]
    if i == 0:   # centre may fall in an opening: take the biggest label in a neighbourhood
        win = lab[int(cy) - 60:int(cy) + 60, int(cx) - 60:int(cx) + 60]; i = np.bincount(win[win > 0]).argmax()
    m = nd.binary_fill_holes(lab == i).astype(np.uint8); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); c = max(cs, key=cv2.contourArea)
    t = np.radians(o["angle_deg"]); R = np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])
    p = (c[:, 0, :] - [cx, cy]) @ R.T / K; u, v = p[:, 0], p[:, 1]
    rc = o["rect"]; res = {}
    for su in (-1, 1):
        uc = rc["ur"] if su > 0 else rc["ul"]; vc = rc["vt"]                      # TOP (sharp, shadow-free) corners only
        r = 12.0
        for it in range(6):
            ox, oy = uc - su * r, vc + r                                           # corner-circle centre guess
            ang = np.degrees(np.arctan2(-(v - oy), su * (u - ox)))                  # 0 = along the end, 90 = along the top edge
            sel = (ang > 12) & (ang < 78) & (np.hypot(u - ox, v - oy) < r + 3) & (np.hypot(u - ox, v - oy) > r - 3)
            if sel.sum() < 20: break
            a_, b_, r = fit_circle(u[sel], v[sel])
        rr = np.hypot(u[sel] - a_, v[sel] - b_) - r
        res["L" if su < 0 else "R"] = dict(r=round(float(r), 2), rms=round(float(rr.std()), 3), n=int(sel.sum()), inset_end=round(float(su * (uc - a_)), 2), inset_top=round(float(b_ - vc), 2))
    out[nm] = res; print(nm, res)
json.dump(out, open("corner_radius_fit.json", "w"), indent=1)
