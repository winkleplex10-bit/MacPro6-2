#!/usr/bin/env python3
"""Wall-thickness check of the IO plate STL (numpy ray cast, no trimesh).
For a grid of points on the OUTER face, cast a ray along the inward surface normal and measure the distance to the
next surface = local wall thickness (normal to the skin). Points inside the port-attachment regions (plug seats,
spot-faces) are reported separately (allowed exception); points within 0.8 of an opening edge or the outline edge are skipped
(ray grazes the cut wall). Usage: check_thickness.py plate.stl features.json [out.png]"""
import json, sys, struct, numpy as np

def load_stl(p):
    b = open(p, "rb").read(); n = struct.unpack("<I", b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("x", "<u2")]))
    return a["v"].reshape(n, 3, 3).astype(float)

def ray_hits(o, d, T, eps=1e-9):
    v0, e1, e2 = T[:, 0], T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
    p = np.cross(d, e2); det = (e1 * p).sum(1); ok = np.abs(det) > eps
    inv = np.where(ok, 1 / np.where(ok, det, 1), 0); s = o - v0
    u = (s * p).sum(1) * inv; q = np.cross(s, e1); v = (q * d).sum(1) * inv; t = (e2 * q).sum(1) * inv
    m = ok & (u >= -1e-7) & (v >= -1e-7) & (u + v <= 1 + 1e-7)
    return t[m], np.nonzero(m)[0]

def main(stl, fj, png=None):
    T = load_stl(stl); F = json.load(open(fj)); feats = [(f["id"], f["kind"], f["x"], f["y"], f["w"], f["h"]) if isinstance(f, dict) else f for f in F["features"]]; ol = F["params"]["outline"]
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    cx, cy = ol["centre"]; W, H = ol["w"], ol["h"]
    port = [f for f in feats if f[1] in ("SEAT", "SPOTFACE", "CRADLE", "BOSS")]
    opens = [f for f in feats if f[1] not in ("SEAT", "SPOTFACE", "GLUE", "CRADLE", "BOSS") and f[4] > 0]
    xmin, xmax = T[:, :, 0].min(1), T[:, :, 0].max(1); ymin, ymax = T[:, :, 1].min(1), T[:, :, 1].max(1)
    res = []
    for x in np.arange(cx - W / 2 + 0.25, cx + W / 2, 0.5):
        for y in np.arange(cy - H / 2 + 0.25, cy + H / 2, 0.5):
            # skip near outline (corner radius approximated) and near openings
            if abs(x - cx) > W / 2 - 0.8 or abs(y - cy) > H / 2 - 0.8: continue
            r = ol["r"]; dx = abs(x - cx) - (W / 2 - r); dy = abs(y - cy) - (H / 2 - r)
            if dx > 0 and dy > 0 and np.hypot(dx, dy) > r - 0.8: continue
            if any(abs(x - f[2]) < f[4] / 2 + 0.8 and abs(y - f[3]) < f[5] / 2 + 0.8 for f in opens): continue
            sel = (xmin <= x + 2) & (xmax >= x - 2) & (ymin <= y + 2) & (ymax >= y - 2); Ts = T[sel]; Ns = N[sel]
            t, idx = ray_hits(np.array([x, y, 10.0]), np.array([0, 0, -1.0]), Ts)
            if len(t) < 2: continue
            k = idx[np.argmin(t)]; top = np.array([x, y, 10 - t.min()]); n = Ns[k]
            if n[2] < 0: n = -n
            d = -n; t2, _ = ray_hits(top + d * 1e-4, d, Ts); t2 = t2[t2 > 1e-3]
            if not len(t2): continue
            th = t2.min(); tz = np.sort(t)[1] - t.min()
            inport = any(abs(x - f[2]) < f[4] / 2 + 0.5 and abs(y - f[3]) < f[5] / 2 + 0.5 for f in port)   # +0.5 = seat run-out band
            res.append((x, y, th, tz, inport))
    R = np.array(res, dtype=float); g = R[R[:, 4] == 0]; p = R[R[:, 4] == 1]
    out = dict(stl=stl, points=len(R), general=dict(n=len(g), min=round(g[:, 2].min(), 3), max=round(g[:, 2].max(), 3), p01=round(np.percentile(g[:, 2], 1), 3), p99=round(np.percentile(g[:, 2], 99), 3),
               off_1p4_gt_0p02=int((np.abs(g[:, 2] - 1.4) > 0.02).sum())),
               port_attach=dict(n=len(p), min=round(p[:, 2].min(), 3) if len(p) else None, max=round(p[:, 2].max(), 3) if len(p) else None))
    bad = g[np.abs(g[:, 2] - 1.4) > 0.02]
    out["general"]["off_examples"] = [[round(a, 2), round(b, 2), round(c, 3)] for a, b, c, *_ in bad[:12]]
    print(json.dumps(out, indent=1))
    if png:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(4.6, 11)); sc = ax.scatter(R[:, 0], R[:, 1], c=R[:, 2], s=3, cmap="viridis", vmin=1.3, vmax=max(1.5, R[:, 2].max()))
        plt.colorbar(sc, ax=ax, label="wall thickness normal to skin, mm"); ax.set_aspect("equal")
        ax.set_title("%s (STL facets add +-0.03; exact B-rep probe = 1.400 normal)\nwall: general %.3f-%.3f mm (n=%d); port seats + screw bosses %s-%s" % (stl.split("/")[-1], g[:, 2].min(), g[:, 2].max(), len(g), out["port_attach"]["min"], out["port_attach"]["max"]), fontsize=7)
        fig.tight_layout(); fig.savefig(png, dpi=130)
    return out

if __name__ == "__main__":
    main(*sys.argv[1:])
