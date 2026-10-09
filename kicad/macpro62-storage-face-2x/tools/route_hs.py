#!/usr/bin/env python3
"""Deterministic coupled routing of the 8 + 8 PCIe pairs and 2 REFCLK pairs (S2X), plus J1 / socket breakout (GND + sideband escapes).
Scheme (see PROGRESS.md / docs): J1-side vertical (B for module TX / REFCLK, L1 for host TX after the row-A gap vias), one L1 horizontal
per pair at a stacked level, B vertical into the M.2 odd row. Every pair = exactly 2 vias per net (AM3 = 0: straight on B).
Corners are 'offset' corners (+-0.35 x / +-0.45 y); the J1-side right turn and the socket-side left turn cancel the intra-pair skew.
REFCLK uses a crossed via pair at the J1-side corner (keeps + -> REFCLKp). Residual skew is trimmed with bumps on the J-side B vertical.
usage: route_hs.py SRC DST"""
import sys, math, os
import pcbnew
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M
SRC, DST = sys.argv[1], sys.argv[2]
OX, OY = 60.0, 190.0
MM = pcbnew.FromMM
def K(x, y): return pcbnew.VECTOR2I(MM(OX + x), MM(OY - y))
def mf(v): return (pcbnew.ToMM(v.x) - OX, OY - pcbnew.ToMM(v.y))
b = pcbnew.LoadBoard(SRC)
W, HP, SP, VD, VH = 0.26, 0.195, 0.35, 0.45, 0.25          # width, half pitch (0.39), spread half pitch, via
L1, L4 = pcbnew.F_Cu, pcbnew.B_Cu
ORDER = ["BH3", "BH2", "BH1", "BH0", "BM0", "AH3", "BM1", "AH2", "AM2", "ACLK", "BM2", "BM3", "BCLK", "AH1", "AH0", "AM0", "AM1"]
H0, PITCH = 26.65, 1.25
GAP_AFTER = {"BM0": 0.6, "BCLK": 0.6}      # extra room where a J-side corner sits under a nearby socket-side corner of the next level
LEV = {}; _h = H0
for n in ORDER: LEV[n] = _h; _h += PITCH + GAP_AFTER.get(n, 0.0)
Y_CONV = 48.6           # socket-side: converge to pad pitch above this
pads = {}
for f in b.GetFootprints():
    for p in f.Pads():
        pads.setdefault(p.GetNetname(), []).append((f.GetReference(), p.GetNumber(), mf(p.GetPosition())))
def padof(net, ref):
    l = [q for q in pads[net] if q[0] == ref]; assert len(l) == 1, (net, ref, l); return l[0][2]
SEG, VIA = [], []        # (net, layer, p1, p2, w) ; (net, p)
def seg(net, layer, pts, w=W):
    for a, c in zip(pts[:-1], pts[1:]):
        if math.hypot(a[0] - c[0], a[1] - c[1]) > 1e-6: SEG.append((net, layer, a, c, w))
def via(net, p): VIA.append((net, p))
def bumps(pts, side, need):
    """insert trapezoid bumps (45 deg, height bh <= 0.35) on the longest vertical segment of polyline pts, toward x side (+1/-1)."""
    if need <= 1e-3: return pts
    k = max(range(len(pts) - 1), key=lambda i: abs(pts[i + 1][1] - pts[i][1]) if abs(pts[i + 1][0] - pts[i][0]) < 1e-6 else -1)
    (x0, ya), (_, yb) = pts[k], pts[k + 1]; L = yb - ya
    n = max(1, math.ceil(need / (0.828 * 0.35))); bh = need / (0.828 * n)
    pitch = 4 * bh + 0.3
    assert n * pitch < L - 0.6, ("no room for bumps", need, L)
    y = ya + (L - n * pitch) / 2; new = [pts[k]]
    for _ in range(n):
        new += [(x0, y), (x0 + side * bh, y + bh), (x0 + side * bh, y + 2 * bh + 0.3 - bh + bh), (x0, y + 3 * bh + 0.3)]
        y += pitch
    new.append(pts[k + 1])
    return pts[:k] + new[:-1] + pts[k + 1:]
def plen(pts): return sum(math.hypot(a[0] - c[0], a[1] - c[1]) for a, c in zip(pts[:-1], pts[1:]))
report = []
def route_pair(key):
    sl, kind = key[0], key[1:]
    if kind == "CLK": nP, nN = "REFCLK_%s_P" % sl, "REFCLK_%s_N" % sl
    else: nP, nN = "PCIE_%s_%sTX%s_P" % (sl, kind[0], kind[1]), "PCIE_%s_%sTX%s_N" % (sl, kind[0], kind[1])
    ref = "J5" if sl == "A" else "J6"
    jP, jN, sP, sN = padof(nP, "J1"), padof(nN, "J1"), padof(nP, ref), padof(nN, ref)
    jl, jr = (nP, nN) if jP[0] < jN[0] else (nN, nP)            # left / right net at J1
    sl_, sr_ = (nP, nN) if sP[0] < sN[0] else (nN, nP)
    xj = (jP[0] + jN[0]) / 2; xs = (sP[0] + sN[0]) / 2; yj = jP[1]; ys = sP[1]
    host = kind.startswith("H"); clk = kind == "CLK"
    J = {jl: [], jr: []}; S = {sl_: [], sr_: []}; EX = {nP: 0.0, nN: 0.0}
    if key == "AM3":                                             # straight on B, no vias
        assert jl == sl_
        for n, sg in ((jl, -1), (jr, 1)):
            x0 = xj + sg * 0.3; xs0 = xs + sg * 0.25
            pts = [(x0, yj), (x0, 24.9), (xj + sg * HP, 24.9 + 0.105), (xj + sg * HP, Y_CONV), (xs0, Y_CONV + 0.1), (xs0, ys)]
            seg(n, L4, pts); J[n] = pts
        report.append((key, nP, nN, plen(J[nP]), plen(J[nN]), 0)); return
    h = LEV[key]
    # ---- J1 side ----
    if host:
        # row-A pads -> gap vias (left low 22.1, right high 23.0) -> L1 vertical
        for n, sg, yv in ((jl, -1, 22.1), (jr, 1, 23.0)):
            x0 = xj + sg * 0.3
            seg(n, L4, [(x0, yj), (x0, yv)], 0.2); via(n, (x0, yv)); EX[n] = yv - yj
            J[n] = [(x0, yv), (x0, 23.4), (xj + sg * HP, 23.505)]
        lay_j = L1
    else:
        for n, sg in ((jl, -1), (jr, 1)):
            x0 = xj + sg * 0.3
            J[n] = [(x0, yj), (x0, 24.9), (xj + sg * HP, 25.005)]
        lay_j = L4
    # vertical to h-1.0, spread to +-SP, corner
    for n, sg in ((jl, -1), (jr, 1)):
        J[n] += [(xj + sg * HP, h - 1.0), (xj + sg * SP, h - 1.0 + (SP - HP))]
    if clk:   # crossed: left (+) via low, right (-) via high -> + becomes the bottom net on L1
        top, bot = jr, jl
        J[jl].append((xj - SP, h - 0.45)); J[jr].append((xj + SP, h + 0.45))
        xt, xb = xj + SP, xj - SP
    else:
        top, bot = jl, jr
        J[jl].append((xj - SP, h + 0.45)); J[jr].append((xj + SP, h - 0.45))
        xt, xb = xj - SP, xj + SP
    # L1 horizontals: jog to +-HP immediately after the corner
    Lh = {top: [(xt, h + 0.45), (xt + 0.255, h + HP)], bot: [(xb, h - 0.45), (xb + 0.255, h - HP)]}
    # ---- socket side (left turn): top net -> left vertical ----
    assert (top == sl_) == True, ("polarity", key, top, sl_)
    Lh[top] += [(xs - SP - 0.255, h + HP), (xs - SP, h + 0.45)]
    Lh[bot] += [(xs + SP - 0.255, h - HP), (xs + SP, h - 0.45)]
    for n, sg, y0 in ((sl_, -1, h + 0.45), (sr_, 1, h - 0.45)):
        S[n] = [(xs + sg * SP, y0), (xs + sg * SP, Y_CONV), (xs + sg * 0.25, Y_CONV + 0.1), (xs + sg * 0.25, ys)]
    # skew: lengths per net (vias equal: 2 per net)
    ln = {n: EX[n] + plen(J[n]) + plen(Lh[n]) + plen(S[n]) for n in (nP, nN)}
    d = ln[nP] - ln[nN]
    if abs(d) > 0.01:
        short = nN if d > 0 else nP
        if lay_j == L4 or not host:
            side = -1 if short == jl else 1
            J[short] = bumps(J[short], side, abs(d))
        else:
            sd = -1 if short == sl_ else 1
            S[short] = bumps(S[short], sd, abs(d))
    ln2 = {n: EX[n] + plen(J[n]) + plen(Lh[n]) + plen(S[n]) for n in (nP, nN)}
    for n in (nP, nN):
        seg(n, lay_j, J[n]); seg(n, L1, Lh[n]); seg(n, L4, S[n])
        if lay_j == L4: via(n, J[n][-1])
        via(n, S[n][0])
    report.append((key, nP, nN, ln2[nP], ln2[nN], round(d, 3)))
for key in ["AM3"] + ORDER: route_pair(key)
# ---- breakout extras: row-A gap vias (GND / PRSNT), row-B GND vias, sideband escapes under the J1 body ----
J1 = [f for f in b.GetFootprints() if f.GetReference() == "J1"][0]
jp = {p.GetNumber(): (p.GetNetname(), mf(p.GetPosition())) for p in J1.Pads()}
for k in range(1, 38):
    na, (xa, ya) = jp["A%d" % k]; nb, (xb_, yb) = jp["B%d" % k]
    if na == "GND":
        seg("GND", L4, [(xa, ya), (xa, 22.55)], 0.2); via("GND", (xa, 22.55))
    if nb == "GND":
        seg("GND", L4, [(xb_, yb), (xb_, 25.35)], 0.2); via("GND", (xb_, 25.35))
for k in range(38, 63):                                             # lanes 8-15 region: GND pads only -> vias in the gap / above
    na, (xa, ya) = jp["A%d" % k]; nb, (xb_, yb) = jp["B%d" % k]
    if na == "GND" and k % 3 == 2: seg("GND", L4, [(xa, ya), (xa, 22.55)], 0.2); via("GND", (xa, 22.55))
    if nb == "GND" and k % 3 == 2: seg("GND", L4, [(xb_, yb), (xb_, 25.35)], 0.2); via("GND", (xb_, 25.35))
# PERST host inputs (row A) escape under the connector body on B, out past the body ends
xa = jp["A11"][1]; seg("PERST_A_HOST_N", L4, [xa, (xa[0], 19.3), (25.0, 19.3), (25.0, 26.0)], 0.15)
xb2 = jp["A29"][1]; seg("PERST_B_HOST_N", L4, [xb2, (xb2[0], 19.3), (69.0, 19.3), (69.0, 26.0)], 0.15)
# set B CLKREQ1#/WAKE1# (row B, boxed in by the slot-A socket verticals): gap via -> L1 under the body -> out right -> via -> B
for k, yl, xo, xe in (("B26", 17.9, 70.9, 84.7), ("B27", 18.6, 70.2, 84.0)):
    n, (x, y) = jp[k]
    seg(n, L4, [(x, y), (x, 22.575)], 0.15); via(n, (x, 22.575))
    seg(n, L1, [(x, 22.575), (x, yl), (xo, yl)], 0.15); via(n, (xo, yl)); seg(n, L4, [(xo, yl), (xe, yl), (xe, 24.0)], 0.15)
# socket odd-row GND pins -> via in front of the pin (between pairs)
for ref in ("J5", "J6"):
    f = [f for f in b.GetFootprints() if f.GetReference() == ref][0]
    for p in f.Pads():
        if p.GetNetname() == "GND" and p.GetNumber().isdigit() and int(p.GetNumber()) % 2 == 1 and int(p.GetNumber()) <= 57:
            x, y = mf(p.GetPosition()); seg("GND", L4, [(x, y), (x, 49.75)], 0.15); via("GND", (x, 49.75))
# ---- write ----
for n, layer, a, c, w in SEG:
    t = pcbnew.PCB_TRACK(b); t.SetStart(K(*a)); t.SetEnd(K(*c)); t.SetLayer(layer); t.SetWidth(MM(w)); t.SetNet(b.FindNet(n)); t.SetLocked(True); b.Add(t)
for n, p in VIA:
    v = pcbnew.PCB_VIA(b); v.SetPosition(K(*p)); v.SetWidth(pcbnew.F_Cu, MM(VD)); v.SetDrill(MM(VH)); v.SetNet(b.FindNet(n)); v.SetLocked(True); b.Add(v)
pcbnew.SaveBoard(DST, b)
print("%-6s %-18s %8s %8s %7s %s" % ("pair", "P net", "P mm", "N mm", "skew0", "final"))
for r in report: print("%-6s %-18s %8.3f %8.3f %7.3f %7.3f" % (r[0], r[1], r[3], r[4], r[5], r[3] - r[4]))
print("segments", len(SEG), "vias", len(VIA), "->", DST)
