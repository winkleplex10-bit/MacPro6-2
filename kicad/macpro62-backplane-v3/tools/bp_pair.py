"""Coupled diff-pair router (centerline A* on L1/L3/L4 with pair-via transitions), BP rev A1.
usage: python3 bp_pair.py SRC DST            (config below: SATA0_RX J7-41/43 -> J1 HS escape vias)
Env: VIAC (via cost mm, default 12), CLR (clearance to other nets, 0.12), DRY=1 (no save), PLOT=png"""
import sys, os, math, heapq, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("RIP", "0")
import numpy as np, pcbnew
from scipy import ndimage
import bp_fix as F
SRC, DST = sys.argv[1], sys.argv[2]
PAIR = os.environ.get("PAIR", "RX")
PN, NN = {"RX": ("SATA0_RX_P", "SATA0_RX_N"), "TX": ("SATA0_TX_P", "SATA0_TX_N"), "USB2_SPARE": ("USB2_SPARE_N", "USB2_SPARE_P")}[PAIR]   # PN = right-hand net of travel
GEO = {F.L1: (0.26, 0.125), F.L3: (0.21, 0.127), F.L4: (0.26, 0.125)}   # 85R (bp_zreport): w, gap
LCOST = {F.L1: 1.0, F.L3: 1.0, F.L4: 1.4}
VIAC = float(os.environ.get("VIAC", "12")); CLR = float(os.environ.get("CLR", "0.12"))
VS = 0.40                       # pair-via half pitch (0.8 mm pitch), via 0.45/0.25
VD, VDR = 0.45, 0.25
REG = (114.0, 143.0, 107.0, 138.0)   # x0 x1 y0 y1 search crop
START = (123.95, 131.0, F.L1, (-1, 0))   # centerline start, heading west; P on right (north)
END = (138.4, 112.6)            # midpoint of locked J1 vias N(138.1) P(138.7); arrive heading north
TAIL = 0.9                      # fixed straight tail (north) into the J1 vias
ENDREL = 1.2; ENDLAY = None
if PAIR == "TX":
    # J7-47 (N, y132.25) / J7-49 (P, y132.75): L1 stubs west to a vertical via pair at x=123.3, then the L3 pair heads EAST
    # (direction reversal at the vias gives P on the right without a crossover). J1 A73 (P) / A74 (N) entered from the south on L1.
    TXV = {"SATA0_TX_P": (123.3, 132.9), "SATA0_TX_N": (123.3, 132.1)}
    START = (123.3, 132.5, F.L3, (1, 0))
    END = (137.74, float(os.environ.get("TXEY", "116.7"))); TAIL = float(os.environ.get("TXT", "0.6")); ENDREL = 0.0; ENDLAY = [F.L3]
    TXPAD = {"SATA0_TX_P": (138.04, 114.025), "SATA0_TX_N": (137.44, 114.025)}
if PAIR == "USB2_SPARE":
    # 90R pair: locked J1 B80(N)/B79(P) escape vias (133.57/134.17, 109.9) -> L3 south (right of south = west = N) -> J6-14 (N) / J6-13 (P), SMD on L1
    GEO = {F.L1: (0.24, 0.15), F.L3: (0.20, 0.15), F.L4: (0.24, 0.15)}
    REG = (114.0, 160.0, 107.0, 150.0)
    TXV = {"USB2_SPARE_N": (133.57, 109.9), "USB2_SPARE_P": (134.17, 109.9)}
    START = (133.87, 109.9, F.L3, (0, 1))
    END = (154.525, float(os.environ.get("SPEY", "145.3"))); TAIL = 0.6; ENDREL = float(os.environ.get("SPREL", "0.6")); ENDLAY = [F.L1]
    TXPAD = {"USB2_SPARE_N": (153.9, 146.85), "USB2_SPARE_P": (155.15, 146.85)}
FIX_RM = [("SATA0_TX_N", F.L1, (123.1, 130.9), (123.1, 131.65)), ("SATA0_TX_N", F.L1, (123.1, 131.65), (123.2, 131.75)),
          ("DVDD", F.L1, (121.635, 128.765), (122.725, 129.855))]   # dangling stubs (no far-end connection)
EXTRA_RM = [s for s in os.environ.get("RM", "").split(",") if s]   # extra unlocked nets to rip (re-route later with bp_fix)

b = pcbnew.LoadBoard(SRC)
KEEP = []
def mmv(v): return (v.x / 1e6, v.y / 1e6)
def near(a, c, tol=0.02): return abs(a[0] - c[0]) < tol and abs(a[1] - c[1]) < tol
for t in list(b.GetTracks()):
    n = t.GetNetname()
    rm = (n in (PN, NN) or n in EXTRA_RM) and not t.IsLocked()
    if t.Type() == pcbnew.PCB_TRACE_T:
        for fn, L, s, e in FIX_RM:
            if n == fn and t.GetLayer() == L and near(mmv(t.GetStart()), s) and near(mmv(t.GetEnd()), e): rm = True
    if rm: KEEP.append(t); b.Remove(t)
# local nudge: J7-39 GND fan-out via moved 0.3 mm north-west so the pair clears it (stub re-drawn, locked)
GMOVE = [((123.806, 130.292), (123.75, 130.0), [(124.7, 130.25), (123.95, 130.25), (123.75, 130.05)])]
if os.environ.get("NOMOVE") != "1":
    for old_c, new_c, stub in GMOVE:
        for t in list(b.GetTracks()):
            if t.GetNetname() != "GND": continue
            if t.Type() == pcbnew.PCB_VIA_T and near(mmv(t.GetPosition()), old_c):
                t.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(new_c[0]), pcbnew.FromMM(new_c[1])))
            elif t.Type() == pcbnew.PCB_TRACE_T and (near(mmv(t.GetEnd()), old_c) or near(mmv(t.GetStart()), old_c)):
                w, L, net = t.GetWidth(), t.GetLayer(), t.GetNet(); KEEP.append(t); b.Remove(t)
                for a, c in zip(stub, stub[1:]):
                    tr = pcbnew.PCB_TRACK(b); tr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]), pcbnew.FromMM(a[1]))); tr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(c[0]), pcbnew.FromMM(c[1])))
                    tr.SetWidth(w); tr.SetLayer(L); tr.SetNet(net); tr.SetLocked(True); b.Add(tr)
g = F.Grid(b)
nP, nN = g.nid(PN), g.nid(NN)
G = F.G
x0, x1, y0, y1 = REG
i0, i1 = int((x0 - g.x0) / G), int((x1 - g.x0) / G); j0, j1 = int((y0 - g.y0) / G), int((y1 - g.y0) / G)
LAY = [F.L1, F.L3, F.L4]
from PIL import Image, ImageDraw
padm = {L: Image.new("1", (i1 - i0, j1 - j0), 0) for L in LAY}
ownm = {L: Image.new("1", (i1 - i0, j1 - j0), 0) for L in LAY}
for f in b.GetFootprints():
    for p in f.Pads():
        q = p.GetPosition()
        if not (x0 - 2 < q.x / 1e6 < x1 + 2 and y0 - 2 < q.y / 1e6 < y1 + 2): continue
        own = p.GetNetname() in (PN, NN)
        for L in LAY:
            if not p.IsOnLayer(L): continue
            sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE); dr = ImageDraw.Draw(ownm[L] if own else padm[L])
            for o_ in range(sp.OutlineCount()):
                ol = sp.COutline(o_); dr.polygon([((ol.CPoint(k).x / 1e6 - g.x0) / G - i0, (ol.CPoint(k).y / 1e6 - g.y0) / G - j0) for k in range(ol.PointCount())], fill=1)
padm = {L: np.array(padm[L], bool) for L in LAY}
ownm = {L: np.array(ownm[L], bool) for L in LAY}
import re
HARDRE = os.environ.get("HARD", r"USB2_|USB_D|SATA0_TX")
SOFT = os.environ.get("SOFT", "1") == "1"; SOFTC = float(os.environ.get("SOFTC", "0.6"))
obs, dist, hsd, distA = {}, {}, {}, {}
for L in LAY:
    lab = g.lab[L][j0:j1, i0:i1]
    o = ((lab != 0) & (lab != nP) & (lab != nN)) | g.notrk[L][j0:j1, i0:i1] | padm[L]
    soft = g.rip[L][j0:j1, i0:i1] & ~padm[L] & (lab != nP) & (lab != nN) if SOFT else np.zeros_like(o)
    if HARDRE:
        hid = [g.netid[n] for n in g.netid if re.match(HARDRE, n)]
        soft &= ~np.isin(lab, hid)
    distA[L] = ndimage.distance_transform_edt(~o) * G
    obs[L] = o & ~soft; dist[L] = ndimage.distance_transform_edt(~obs[L]) * G
    hsd[L] = ndimage.distance_transform_edt(~(g.hs[L][j0:j1, i0:i1] & o)) * G
drill_o = (g.drill[j0:j1, i0:i1] & ~np.isin(g.lab[F.L1][j0:j1, i0:i1], [nP, nN]))
ddist = ndimage.distance_transform_edt(~drill_o) * G
novia = g.novia[j0:j1, i0:i1]
thr = {L: GEO[L][0] + GEO[L][1] / 2 + CLR + 0.04 for L in LAY}
ok = {L: dist[L] > thr[L] for L in LAY}
okA = {L: distA[L] > thr[L] for L in LAY}
for nm in [x for x in os.environ.get("LDIS", "").split(",") if x]:
    L = {"L1": F.L1, "L3": F.L3, "L4": F.L4}[nm]; ok[L][:] = False; okA[L][:] = False
# pair-via site (isotropic disc): both vias + clearance on every routing layer, hole-to-hole 0.25
vr1 = VD / 2 + CLR + 0.04
distV = {L: ndimage.distance_transform_edt(~(obs[L] | ownm[L])) * G for L in LAY}
distVA = {L: ndimage.distance_transform_edt(~(obs[L] | ownm[L] | (distA[L] == 0))) * G for L in LAY}
sv = np.logical_and.reduce([distV[L] > vr1 for L in LAY]) & (ddist > VDR / 2 + 0.25 + 0.05) & ~novia   # one via fits
svA = np.logical_and.reduce([distVA[L] > vr1 for L in LAY])
def shift(m, dj, di):
    o = np.zeros_like(m); H_, W_ = m.shape
    o[max(dj, 0):H_ + min(dj, 0), max(di, 0):W_ + min(di, 0)] = m[max(-dj, 0):H_ + min(-dj, 0), max(-di, 0):W_ + min(-di, 0)]
    return o
k4 = int(round(VS / G)); k4d = int(round(VS / G / 1.4142))
# pair-via sites keyed by travel direction (vias perpendicular to travel), centre must also be clear (own copper only)
VSITE = {}
for d in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
    pj, pi_ = d[1], -d[0]          # perpendicular (j,i) of travel (dj,di)
    kk = k4d if (pj and pi_) else k4
    VSITE[d] = shift(sv, -pj * kk, -pi_ * kk) & shift(sv, pj * kk, pi_ * kk) & np.logical_and.reduce([dist[L] > 0.2 for L in LAY])
    VSOFT = globals().setdefault("VSOFT", {}); VSOFT[d] = ~(shift(svA, -pj * kk, -pi_ * kk) & shift(svA, pj * kk, pi_ * kk))
vok = VSITE[(-1, 0)] | VSITE[(0, 1)]
def fij(x, y): return int(round((y - g.y0) / G)) - j0, int(round((x - g.x0) / G)) - i0
def fxy(j, i): return (g.x0 + (i + i0) * G, g.y0 + (j + j0) * G)
# own-start/end relief: allow centerline near own pads/vias at the two ends
if PAIR == "USB2_SPARE":   # no northward start
    jj, ii = fij(START[0], START[1]); r = int(1.0 / G)
    for L in LAY: ok[L][jj - r:jj - 1, ii - r:ii + r] = False
if PAIR == "TX":   # no westward start (would cross the stubs)
    jj, ii = fij(START[0], START[1]); r = int(1.0 / G)
    ok[F.L3][jj - r:jj + r, ii - r:ii - 1] = False
    for L in (F.L1, F.L4): ok[L][jj - r:jj + r, ii - r:ii + r] = False
for (x, y), rr_ in ((START[:2], float(os.environ.get("RELS", "0.3"))), (END, ENDREL)):
    if rr_ <= 0: continue
    jj, ii = fij(x, y); r = max(1, int(rr_ / G))
    for L in LAY:
        sub = ok[L][jj - r:jj + r, ii - r:ii + r]; d = dist[L][jj - r:jj + r, ii - r:ii + r]
        sub |= d > GEO[L][0] / 2 + CLR + 0.04 + 0.0   # only single-track clearance near terminals (checked by DRC after)
print("ok frac", {g.b.GetLayerName(L): round(float(ok[L].mean()), 3) for L in LAY}, "via sites", int(vok.sum()))
# coarse A*
S = int(os.environ.get("CS", "1")); CG = G * S
okc = {L: ok[L][::S, ::S] for L in LAY}; vokc = vok[::S, ::S]
H, W = okc[F.L1].shape
sj, si = [v // S for v in fij(*START[:2])]
GDIR = (1, 0) if PAIR == "USB2_SPARE" else (-1, 0)   # required final move (dj, di): south / north
tj, ti = [v // S for v in fij(END[0], END[1] - GDIR[0] * TAIL)]
pen = {L: np.where(hsd[L][::S, ::S] < 0.6, 0.6, 0.0) + np.where(okA[L][::S, ::S], 0.0, SOFTC / CG) for L in LAY}
if g.zone3 is not None: pen[F.L3] = pen[F.L3] + g.zone3[j0:j1, i0:i1][::S, ::S] * 0.5
LI = {L: k for k, L in enumerate(LAY)}
ENDL = [F.L3, F.L4, F.L1]
MSTR = int(float(os.environ.get("MSTR", "0.5")) / CG)
def hfun(j, i):
    if j == -1: return 0.0
    dj, di = abs(j - tj), abs(i - ti); return (max(dj, di) + 0.414 * min(dj, di)) * CG
best = {}; prev = {}
st = (LI[START[2]], sj, si); best[st] = 0; pq = [(hfun(sj, si), 0.0, st)]
nb = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
goal = None; pops = 0
while pq:
    f, c, s = heapq.heappop(pq); pops += 1
    if c > best.get(s, 1e9): continue
    k, j, i = s
    if j == -1: goal = s; break
    L = LAY[k]
    for dj, di in nb:
        jj, ii = j + dj, i + di
        if not (0 <= jj < H and 0 <= ii < W) or not okc[L][jj, ii]: continue
        if (jj, ii) == (tj, ti) and (dj, di) != GDIR: continue
        nc = c + (CG * (1.4142 if dj and di else 1.0)) * (LCOST[L] + pen[L][jj, ii])
        if (jj, ii) == (tj, ti) and ENDLAY and L not in ENDLAY: continue
        ns = (k, jj, ii) if (jj, ii) != (tj, ti) else (k, -1, -1)
        if nc < best.get(ns, 1e9): best[ns] = nc; prev[ns] = s; heapq.heappush(pq, (nc + hfun(jj, ii), nc, ns))
    pv = prev.get(s)
    if pv is not None and pv[0] == k:
        d = (j - pv[1], i - pv[2])
        straight = True; q = s
        for _ in range(MSTR):
            pq_ = prev.get(q)
            if pq_ is None or pq_[0] != k or (q[1] - pq_[1], q[2] - pq_[2]) != d: straight = (pq_ is None and q == st); break
            q = pq_
        if straight and VSITE[d][j * S, i * S]:
            for k2 in range(3):
                if k2 == k or not okc[LAY[k2]][j, i]: continue
                jj, ii = j + d[0] * MSTR, i + d[1] * MSTR
                if not (0 <= jj < H and 0 <= ii < W) or not all(okc[LAY[k2]][j + d[0] * m, i + d[1] * m] for m in range(1, MSTR + 1)): continue
                ns = (k2, jj, ii); nc = c + VIAC + MSTR * CG * (1.4142 if d[0] and d[1] else 1) * LCOST[LAY[k2]] + (8 * SOFTC if VSOFT[d][j * S, i * S] else 0)   # via + forced straight step on the new layer
                if nc < best.get(ns, 1e9): best[ns] = nc; prev[ns] = ("via", s); heapq.heappush(pq, (nc + hfun(jj, ii), nc, ns))
print("A* pops", pops, "goal", goal, "cost", round(best.get(goal, -1), 2) if goal else None)
if goal is None:
    if os.environ.get("WIN"):
        X0, X1, Y0, Y1 = map(float, os.environ["WIN"].split(","))
        reach = {k: set() for k in range(3)}
        for (k, j, i) in best: reach[k].add((j, i))
        for k, L in enumerate(LAY):
            print(b.GetLayerName(L))
            for y in np.arange(Y0, Y1, float(os.environ.get("STEP", "0.1"))):
                r = ""
                for x in np.arange(X0, X1, float(os.environ.get("STEP", "0.1"))):
                    jj, ii = fij(x, y)
                    c = "R" if (jj // S, ii // S) in reach[k] else ("V" if vok[jj, ii] and ok[L][jj, ii] else "o" if ok[L][jj, ii] else "#" if obs[L][jj, ii] else ".")
                    r += c
                print(f"{y:6.1f} {r}")
    sys.exit(2)
VIAS = []
path = [(goal[0], tj, ti)]; prev[path[0]] = prev[goal]
while path[-1] in prev:
    q = prev[path[-1]]
    if q[0] == "via":
        q = q[1]; a = path[-1]; dj, di = (a[1] - q[1]) // MSTR, (a[2] - q[2]) // MSTR
        for m in range(MSTR - 1, -1, -1): path.append((a[0], q[1] + dj * m, q[2] + di * m))
        VIAS.append((q[1], q[2], dj, di))
    path.append(q)
path = path[::-1]
# split into layer runs (xy in mm)
runs = []; cur = None
for (k, j, i) in path:
    xy = fxy(j * S, i * S)
    if cur is None or cur[0] != LAY[k]: cur = [LAY[k], []]; runs.append(cur)
    cur[1].append(xy)
runs[0][1][0] = START[:2]
runs[-1][1][-1] = (END[0], END[1] - GDIR[0] * TAIL)
print("layers", [(b.GetLayerName(L), len(p)) for L, p in runs])
json.dump([[b.GetLayerName(L), p] for L, p in runs], open(os.environ.get("RAW", "/tmp/pair_raw.json"), "w"))
# octilinear string-pulling on each run
def segok(L, a, c, thrL):
    n = max(2, int(math.hypot(c[0] - a[0], c[1] - a[1]) / 0.025))
    for t in np.linspace(0, 1, n):
        x, y = a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t
        jj, ii = fij(x, y)
        if not ok[L][jj, ii]: return False
    return True
def octi(a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]
    if abs(abs(dx) - abs(dy)) < 1e-6 or abs(dx) < 1e-6 or abs(dy) < 1e-6: return [[a, c]]
    m = min(abs(dx), abs(dy)); sx, sy = math.copysign(1, dx), math.copysign(1, dy)
    b1 = (a[0] + sx * m, a[1] + sy * m); b2 = (c[0] - sx * m, c[1] - sy * m)
    return [[a, b1, c], [a, b2, c]]
def pull(L, pts):
    out = [pts[0]]; i = 0
    while i < len(pts) - 1:
        bestj, bestp = i + 1, [pts[i], pts[i + 1]]
        for jx in range(len(pts) - 1, i + 1, -1):
            done = False
            for cand in octi(pts[i], pts[jx]):
                if all(segok(L, cand[q], cand[q + 1], None) for q in range(len(cand) - 1)):
                    bestj, bestp = jx, cand; done = True; break
            if done: break
        out += bestp[1:]; i = bestj
    # merge collinear
    res = [out[0]]
    for p in out[1:]:
        if len(res) >= 2:
            a, c = res[-2], res[-1]
            if abs((c[0] - a[0]) * (p[1] - c[1]) - (c[1] - a[1]) * (p[0] - c[0])) < 1e-6 and (c[0]-a[0])*(p[0]-c[0]) + (c[1]-a[1])*(p[1]-c[1]) > 0: res[-1] = p; continue
        if math.hypot(p[0] - res[-1][0], p[1] - res[-1][1]) > 1e-6: res.append(p)
    return res
def pullp(L, pts, head, tail):
    M = MSTR
    a = pts[:M + 1] if head else pts[:1]
    z = pts[-(M + 1):] if tail else pts[-1:]
    mid = pts[len(a) - 1: len(pts) - len(z) + 1]
    out = (a[:-1] + pull(L, mid) + z[1:]) if len(mid) > 1 else pts
    res = [out[0]]
    for p in out[1:]:
        if len(res) >= 2:
            a_, c_ = res[-2], res[-1]
            if abs((c_[0] - a_[0]) * (p[1] - c_[1]) - (c_[1] - a_[1]) * (p[0] - c_[0])) < 1e-6 and (c_[0]-a_[0])*(p[0]-c_[0]) + (c_[1]-a_[1])*(p[1]-c_[1]) > 0: res[-1] = p; continue
        if math.hypot(p[0] - res[-1][0], p[1] - res[-1][1]) > 1e-6: res.append(p)
    return res
runs = [[L, pullp(L, p, k > 0, k < len(runs) - 1)] for k, (L, p) in enumerate(runs)]
if TAIL > 0: runs[-1][1].append(END)
for L, p in runs: print(b.GetLayerName(L), [(round(x, 3), round(y, 3)) for x, y in p])
json.dump([[b.GetLayerName(L), p] for L, p in runs], open(os.environ.get("CL", "/tmp/pair_cl.json"), "w"))
# ---------------- build copper ----------------
from shapely.geometry import LineString, Point, Polygon as SPoly
from shapely.ops import unary_union
MM = pcbnew.FromMM
def unit(a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]; l = math.hypot(dx, dy); return (dx / l, dy / l)
def rnorm(d): return (-d[1], d[0])          # right-hand normal (y down): west -> north
def offset(pts, sft):
    out = []
    for k, p in enumerate(pts):
        if k == 0: n = rnorm(unit(pts[0], pts[1])); out.append((p[0] + n[0] * sft, p[1] + n[1] * sft)); continue
        if k == len(pts) - 1: n = rnorm(unit(pts[-2], pts[-1])); out.append((p[0] + n[0] * sft, p[1] + n[1] * sft)); continue
        n1 = rnorm(unit(pts[k - 1], p)); n2 = rnorm(unit(p, pts[k + 1]))
        na = (n1[0] + n2[0], n1[1] + n2[1]); l = math.hypot(*na); na = (na[0] / l, na[1] / l)
        f = sft / (na[0] * n1[0] + na[1] * n1[1]); out.append((p[0] + na[0] * f, p[1] + na[1] * f))
    return out
items = {PN: [], NN: []}   # (kind, layer, a, b, w)
viaP = []                   # (centre P, centre N, travel dir)
for k, (L, pts) in enumerate(runs):
    w, gp = GEO[L]; sft = (w + gp) / 2
    for net, sg in ((PN, +1), (NN, -1)):
        op = offset(pts, sg * sft)
        if k == 0 and PAIR in ("TX", "USB2_SPARE"):
            op = [TXV[net]] + op
        elif k == 0:   # J7 fan-out: pad centre -> along pad -> 45deg onto pair pitch
            py = 130.75 if net == PN else 131.25
            xk = op[0][0] + abs(op[0][1] - py)
            op = [(124.7, py), (xk, py)] + op
        if k > 0:    # from previous via
            vc = viaP[k - 1][0 if net == PN else 1]; op = [vc] + op
        if k < len(runs) - 1:
            d = unit(pts[-2], pts[-1]); n = rnorm(d)
            c = pts[-1]; vc = (c[0] + n[0] * sg * VS, c[1] + n[1] * sg * VS); op = op + [vc]
            if net == PN: viaP.append([vc, None, d])
            else: viaP[-1][1] = vc
        elif PAIR == "USB2_SPARE":
            op = op + [TXPAD[net]]
        elif PAIR == "TX":
            d = unit(pts[-2], pts[-1]); n = rnorm(d); c = pts[-1]
            vc = (round(c[0] + n[0] * sg * VS, 3), round(c[1] + n[1] * sg * VS, 3)); op = op + [vc]
            if net == PN: viaP.append([vc, None, d])
            else: viaP[-1][1] = vc
        else:
            op = op + [(138.7, 112.6) if net == PN else (138.1, 112.6)]
        for a, c in zip(op, op[1:]):
            if math.dist(a, c) > 1e-4: items[net].append(("t", L, a, c, w))
for vp, vn, d in viaP:
    items[PN].append(("v", None, vp, None, VD)); items[NN].append(("v", None, vn, None, VD))
if PAIR == "TX":
    for net in (PN, NN):
        pd = (124.7, 132.75) if net == PN else (124.7, 132.25); v = TXV[net]
        for a, c in zip([pd, (123.55, pd[1]), v][:-1], [(123.55, pd[1]), v]): items[net].append(("t", F.L1, a, c, 0.26))
        items[net].append(("v", None, v, None, VD))
        ve = viaP[-1][0 if net == PN else 1]; pe = TXPAD[net]
        items[net].append(("t", F.L1, ve, (pe[0], ve[1] - 0.6), 0.26)); items[net].append(("t", F.L1, (pe[0], ve[1] - 0.6), pe, 0.26))
def igeom(it, L):
    kd, l, a, c, w = it
    if kd == "v": return Point(a).buffer(w / 2, 16)
    if l != L: return None
    return LineString([a, c]).buffer(w / 2, 8)
newg = {L: unary_union([gg for net in items for it in items[net] for gg in [igeom(it, L)] if gg is not None]) for L in LAY}
for net in items:
    ln = sum(math.dist(it[2], it[3]) for it in items[net] if it[0] == "t")
    print(net, "new len %.2f mm" % ln, "vias", sum(1 for it in items[net] if it[0] == "v"))
# conflicts with existing copper (clearance 0.1 + 0.02)
CL2 = 0.12
conf = []; hardc = []
def tgeom(t, L):
    if t.Type() == pcbnew.PCB_VIA_T: return Point(mmv(t.GetPosition())).buffer(t.GetWidth(L) / 2e6, 16)
    if t.GetLayer() != L: return None
    return LineString([mmv(t.GetStart()), mmv(t.GetEnd())]).buffer(t.GetWidth() / 2e6, 8)
for t in b.GetTracks():
    n = t.GetNetname()
    if n in (PN, NN): continue
    for L in LAY:
        gg = tgeom(t, L)
        if gg is None or gg.distance(newg[L]) >= CL2: continue
        (conf if g.ripable(t) else hardc).append(t); break
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() in (PN, NN): continue
        for L in LAY:
            if not p.IsOnLayer(L): continue
            sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
            for o_ in range(sp.OutlineCount()):
                ol = sp.COutline(o_); pg = SPoly([(ol.CPoint(q).x / 1e6, ol.CPoint(q).y / 1e6) for q in range(ol.PointCount())])
                if pg.distance(newg[L]) < CL2 - 0.005: hardc.append(("pad", f.GetReference(), p.GetNumber(), p.GetNetname(), b.GetLayerName(L), round(pg.distance(newg[L]), 3)))
cn = sorted({t.GetNetname() for t in conf})
print("soft conflicts:", len(conf), "items, nets", cn)
print("hard conflicts:", [(x if isinstance(x, tuple) else (x.GetNetname(), "via" if x.Type() == pcbnew.PCB_VIA_T else b.GetLayerName(x.GetLayer()), mmv(x.GetPosition() if x.Type() == pcbnew.PCB_VIA_T else x.GetStart()))) for x in hardc])
if os.environ.get("DRY"): sys.exit(0)
if hardc and not os.environ.get("FORCE"): print("hard conflicts -> abort"); sys.exit(3)
for t in conf:
    if t in KEEP: continue
    g.remove_item(t)
netP, netN = b.FindNet(PN), b.FindNet(NN)
for net, nobj in ((PN, netP), (NN, netN)):
    for kd, l, a, c, w in items[net]:
        if kd == "t":
            tr = pcbnew.PCB_TRACK(b); tr.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); tr.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
            tr.SetWidth(MM(w)); tr.SetLayer(l); tr.SetNet(nobj); tr.SetLocked(True); b.Add(tr); g.add_item(tr)
        else:
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); v.SetWidth(MM(VD)); v.SetDrill(MM(VDR))
            v.SetNet(nobj); v.SetLocked(True); b.Add(v); g.add_item(v)
# GND stitching vias next to each new signal via (outside the pair, along the via axis, or beside it)
gnd = b.FindNet("GND"); added = []
def allcopper_ok(c, r):
    pt = Point(c).buffer(r)
    for L in LAY:
        jj, ii = fij(*c)
        if g.novia[jj + j0, ii + i0]: return False
    for t in b.GetTracks():
        if t.GetNetname() == "GND" and t.Type() != pcbnew.PCB_VIA_T: continue
        for L in LAY:
            gg = tgeom(t, L)
            if gg is not None and gg.distance(pt) < CL2: return False
        if t.Type() == pcbnew.PCB_VIA_T and math.dist(mmv(t.GetPosition()), c) < VD / 2 + t.GetWidth(F.L1) / 2e6 + 0.12: return False
    for f in b.GetFootprints():
        for p in f.Pads():
            q = mmv(p.GetPosition())
            if math.dist(q, c) > 4: continue
            for L in LAY:
                if not p.IsOnLayer(L): continue
                if p.GetNetname() == "GND" and p.GetDrillSize().x == 0: continue
                sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
                for o_ in range(sp.OutlineCount()):
                    ol = sp.COutline(o_); pg = SPoly([(ol.CPoint(q_).x / 1e6, ol.CPoint(q_).y / 1e6) for q_ in range(ol.PointCount())])
                    if pg.distance(pt) < CL2: return False
    return True
for vp, vn, d in viaP + ([[(138.7, 112.6), (138.1, 112.6), (0, -1)]] if PAIR == "RX" else [[TXV[PN], TXV[NN], (-1, 0)]]):
    n = rnorm(d)
    for c, sg in ((vp, +1), (vn, -1)):
        done = False
        for rr in (0.75, 0.85, 1.0, 1.15):
            for ang in (0, 30, -30, 60, -60, 90, -90, 120, -120):
                a = math.radians(ang); ox, oy = n[0] * sg, n[1] * sg
                ux, uy = ox * math.cos(a) - oy * math.sin(a), ox * math.sin(a) + oy * math.cos(a)
                q = (round(c[0] + ux * rr, 3), round(c[1] + uy * rr, 3))
                if allcopper_ok(q, VD / 2):
                    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(q[0]), MM(q[1]))); v.SetWidth(MM(VD)); v.SetDrill(MM(VDR))
                    v.SetNet(gnd); v.SetLocked(True); b.Add(v); added.append(q); done = True; break
            if done: break
        print("GND stitch for", c, "->", added[-1] if done else "NONE")
# re-route ripped nets (RIP=0, bp_fix router)
g2 = F.Grid(b); fails = []
for n in cn:
    a, okr = F.route_net(g2, n); print("reroute", n, okr, len(a))
    if not okr: fails.append(n)
print("reroute fails:", fails)
pcbnew.SaveBoard(DST, b); print("saved", DST)
