#!/usr/bin/env python3
"""2-D quasi-static (Laplace, finite-difference) impedance solver for coupled microstrip / stripline cross-sections.
Odd mode: Zdiff = 2*Z_odd, Z = 1/(c*sqrt(C*C0)) per conductor. Used for the MP62 BP / SM-1 JLC04161H-7628 4-layer stackup check.
Layers are given bottom-up as (thickness_mm, eps_r, kind) with kind 'gnd' | 'diel' | 'sig' (signal copper layer, traces placed in it)."""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl, sys, json
C0 = 299792458.0; E0 = 8.854e-12
def solve(stack, w, s, sig_layer, h_step=0.004, xpad=2.0, mask=(0.015, 3.8), single=False):
    # build y grid: list of layers bottom-up; air on top (1.0 mm)
    layers = list(stack) + [(1.2, 1.0, "air")]
    ys = [0.0]; kinds = []
    for t, er, k in layers: ys.append(ys[-1] + t)
    H = ys[-1]
    ny = int(round(H / h_step)) + 1
    width = (2 * w + s if not single else w) + 2 * xpad
    nx = int(round(width / h_step)) + 1
    y = np.linspace(0, H, ny); x = np.linspace(-width / 2, width / 2, nx)
    eps = np.ones((ny, nx)); fixed = np.zeros((ny, nx), bool); val = np.zeros((ny, nx))
    for i, (t, er, k) in enumerate(layers):
        m = (y >= ys[i] - 1e-9) & (y <= ys[i + 1] + 1e-9)
        if k in ("diel",): eps[m, :] = er
        if k == "gnd": fixed[m, :] = True; val[m, :] = 0.0
        if k == "sig":
            eps[m, :] = er   # dielectric fill around traces (er given = embedding resin / surrounding)
    # traces in the signal layer
    i = [n for n, l in enumerate(layers) if l[2] == "sig"][sig_layer]
    ya, yb = ys[i], ys[i + 1]
    my = (y >= ya - 1e-9) & (y <= yb + 1e-9)
    if single:
        mx = [(np.abs(x) <= w / 2 + 1e-9, 1.0)]
    else:
        mx = [((x >= s / 2 - 1e-9) & (x <= s / 2 + w + 1e-9), 1.0), ((x <= -s / 2 + 1e-9) & (x >= -s / 2 - w - 1e-9), -1.0)]
    # outer-layer solder mask (top/bottom signal layer exposed to air): coat mask thickness above the copper
    top_air = layers[i + 1][2] == "air"
    if top_air and mask:
        mt, mer = mask
        mm = (y > yb) & (y <= yb + mt)
        eps[mm, :] = np.where(eps[mm, :] < mer, mer, eps[mm, :])
        if top_air: eps[my, :] = np.where(eps[my, :] == 1.0, mer, eps[my, :])
    for m, v in mx:
        fixed[np.ix_(my, m)] = True; val[np.ix_(my, m)] = v
    # outer box = 0
    fixed[0, :] = fixed[-1, :] = True; fixed[:, 0] = fixed[:, -1] = True
    def cap(epsg):
        N = ny * nx; idx = np.arange(N).reshape(ny, nx)
        rows = []; cols = []; data = []; b = np.zeros(N)
        # face eps (harmonic-ish average)
        def fe(a, c): return 0.5 * (a + c)
        for (dy, dx) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            pass
        e = epsg
        eN = fe(e[1:-1, 1:-1], e[2:, 1:-1]); eS = fe(e[1:-1, 1:-1], e[:-2, 1:-1]); eE = fe(e[1:-1, 1:-1], e[1:-1, 2:]); eW = fe(e[1:-1, 1:-1], e[1:-1, :-2])
        I = idx[1:-1, 1:-1].ravel()
        diag = (eN + eS + eE + eW).ravel()
        A = sp.lil_matrix((N, N))
        A = sp.coo_matrix((diag, (I, I)), shape=(N, N))
        nb = [(idx[2:, 1:-1].ravel(), eN.ravel()), (idx[:-2, 1:-1].ravel(), eS.ravel()), (idx[1:-1, 2:].ravel(), eE.ravel()), (idx[1:-1, :-2].ravel(), eW.ravel())]
        rr = [I]; cc = [I]; dd = [diag]
        for J, ev in nb: rr.append(I); cc.append(J); dd.append(-ev)
        A = sp.coo_matrix((np.concatenate(dd), (np.concatenate(rr), np.concatenate(cc))), shape=(N, N)).tocsr()
        fx = fixed.ravel(); free = ~fx
        phi = val.ravel().copy()
        Aff = A[free][:, free]; rhs = -A[free][:, fx] @ phi[fx]
        phi[free] = spl.spsolve(Aff.tocsc(), rhs)
        phi = phi.reshape(ny, nx)
        # charge on conductor +1: energy method W = 0.5*eps*|grad|^2 ; C_total = 2W/V^2 (V = 1 per conductor, odd: total V^2 sum = 2)
        gy, gx = np.gradient(phi, y, x)
        W = 0.5 * E0 * np.sum(epsg * (gx ** 2 + gy ** 2)) * (h_step * h_step) * 1e-6 / 1e-6   # per metre (mm^2 -> m^2 / grad in 1/mm -> 1/m)
        # grad in V/mm -> V/m factor 1e3 squared = 1e6, area mm^2 -> m^2 1e-6 -> cancels
        Vsq = 1.0 if single else 2.0
        return 2 * W / Vsq
    C = cap(eps); Ca = cap(np.ones_like(eps))
    Z = 1.0 / (C0 * np.sqrt(C * Ca))
    eeff = C / Ca
    return (Z if single else 2 * Z), eeff
if __name__ == "__main__":
    pass
