"""2D finite-difference quasi-static solver (sparse direct) for single / edge-coupled microstrip on a JLC FPC cross-section.
D-IO16 port modules. Stack (bottom up): L2 GND plane (optionally with an opening under the pair = hatch window) / PI core h (er 3.3, JLC) /
L1 copper t / coverlay = adhesive 15 um + PI 12.5 um (er 2.9, JLC) / air. Energy method: C = 2W/V^2, Z = 1/(c sqrt(C Cair)).
Returns (Z_single or Z_odd, eps_eff); Zdiff = 2 Zodd. Accuracy ~2-3 % (grid dx = h/10). [Estimate - verify with the TDR coupon]"""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
C0 = 299792458.0; E0 = 8.854e-12
def solve(w, s, h, t=0.012, cov=0.0275, er_core=3.3, er_cov=2.9, mode="odd", gnd_gap=None, gnd_sides=None, gnd_open=None, dx=None):
    dx = dx or min(h / 10, t / 2, w / 10)
    n_tr = 1 if s is None else 2; span = w if n_tr == 1 else 2 * w + s
    W = span + 2 * max(12 * h, 0.4); H = h + t + cov + max(14 * h, 0.4)
    nx, ny = int(round(W / dx)) + 1, int(round(H / dx)) + 1
    x = np.linspace(-W / 2, W / 2, nx); y = np.arange(ny) * dx
    X, Y = np.meshgrid(x, y, indexing="ij")
    cx = [0.0] if n_tr == 1 else [-(s + w) / 2, (s + w) / 2]
    vs = [1.0] if n_tr == 1 else ([1.0, -1.0] if mode == "odd" else [1.0, 1.0])
    def energy(er_on):
        er = np.ones((nx, ny))   # cell-centred permittivity (cell between node j and j+1 in y)
        yc = (y[:-1] + y[1:]) / 2
        epsy = np.ones(ny - 1)
        if er_on:
            epsy[yc < h] = er_core; epsy[(yc >= h) & (yc < h + t + cov)] = er_cov
        fixedv = np.full((nx, ny), np.nan)
        g = np.zeros((nx, ny), bool); g[:, 0] = True
        if gnd_gap: g[:, 0] &= ~(np.abs(x) < gnd_gap / 2)
        for (o0, o1) in (gnd_open or []): g[:, 0] &= ~((x > o0) & (x < o1))
        if gnd_sides is not None:   # coplanar GND on L1 at |x| >= gnd_sides
            g |= (np.abs(X) >= gnd_sides) & (Y >= h - 1e-12) & (Y <= h + t + 1e-12)
        fixedv[g] = 0.0; fixedv[:, -1] = 0.0; fixedv[0, :] = 0.0; fixedv[-1, :] = 0.0
        for c, v in zip(cx, vs):
            m = (np.abs(X - c) <= w / 2 + 1e-12) & (Y >= h - 1e-12) & (Y <= h + t + 1e-12); fixedv[m] = v
        # link permittivities: x-links at node row j use average of the cells above/below; y-links use the cell value
        epsx = np.ones(ny)
        epsx[1:-1] = (epsy[:-1] + epsy[1:]) / 2; epsx[0] = epsy[0]; epsx[-1] = epsy[-1]
        idx = np.arange(nx * ny).reshape(nx, ny); free = np.isnan(fixedv); fv = np.nan_to_num(fixedv)
        rows, cols, vals = [], [], []; b = np.zeros(nx * ny)
        diag = np.zeros((nx, ny))
        def link(i0, j0, i1, j1, e):  # arrays of node pairs + link weights
            nonlocal rows, cols, vals
            a = idx[i0, j0].ravel(); c = idx[i1, j1].ravel(); e = np.broadcast_to(e, i0.shape).ravel()
            for p, q in ((a, c), (c, a)):
                rows.append(p); cols.append(q); vals.append(-e)
            np.add.at(diag, (i0.ravel(), j0.ravel()), e); np.add.at(diag, (i1.ravel(), j1.ravel()), e)
        I, J = np.meshgrid(np.arange(nx - 1), np.arange(ny), indexing="ij"); link(I, J, I + 1, J, epsx[J])
        I, J = np.meshgrid(np.arange(nx), np.arange(ny - 1), indexing="ij"); link(I, J, I, J + 1, epsy[J])
        rows.append(idx.ravel()); cols.append(idx.ravel()); vals.append(diag.ravel())
        A = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(nx * ny, nx * ny))
        fr = free.ravel(); A_ff = A[fr][:, fr]; A_fc = A[fr][:, ~fr]
        phi = fv.ravel().copy(); phi[fr] = spl.spsolve(A_ff.tocsc(), -A_fc @ fv.ravel()[~fr]); phi = phi.reshape(nx, ny)
        Ex = np.diff(phi, axis=0) / dx; Ey = np.diff(phi, axis=1) / dx
        return 0.5 * E0 * (np.sum(epsx[None, :] * Ex ** 2) + np.sum(epsy[None, :] * Ey ** 2)) * dx * dx
    nv = n_tr
    C1 = 2 * energy(True) / nv; Ca = 2 * energy(False) / nv
    return 1.0 / (C0 * np.sqrt(C1 * Ca)), C1 / Ca
def zdiff(w, s, h, **k): z, e = solve(w, s, h, mode="odd", **k); return 2 * z, e
def zdiff_hatch(w, s, h, lw=0.1, p=0.3, **k):
    """45-deg cross-hatched L2 under the pair: average C and L per length over the copper fraction f = 1-(g/p)^2 (two-way hatch)
    and the open fraction (worst case: an opening of width g under each trace). Crude periodic-loading estimate."""
    g = p - lw; f = 1 - (g / p) ** 2
    cx = (s + w) / 2
    def CL(op):
        z, e = solve(w, s, h, mode="odd", gnd_open=op, **k)   # Zodd, eps_eff
        vp = C0 / np.sqrt(e); return 1 / (z * vp), z / vp       # C, L per m (odd mode)
    Cs, Ls = CL(None); Co, Lo = CL([(-cx - g / 2, -cx + g / 2), (cx - g / 2, cx + g / 2)])
    C = f * Cs + (1 - f) * Co; L = f * Ls + (1 - f) * Lo
    return 2 * np.sqrt(L / C), f
if __name__ == "__main__":
    import time; t0 = time.time()
    print("50um core, w0.11 single:", solve(0.11, None, 0.05)); print(time.time() - t0)
