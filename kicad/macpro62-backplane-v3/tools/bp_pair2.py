"""BP v3 coupled diff-pair router (generalised bp_pair.py): centerline A* on L1/L3/L4 with pair-via transitions,
configured by a JSON pair spec. Existing HS / SATA / USB2 / locked copper is never touched; unlocked low-speed copper in the
way is ripped and re-routed single-net (bp_fix.route_net, RIP=0) afterwards.
usage: python3 bp_pair2.py SRC DST SPEC.json
SPEC: {"P": net, "N": net, "reg": [x0,x1,y0,y1],
       "start": {"c": [x,y], "L": "L3", "dir": [dx,dy], "lead": mm, "pre": {"P": [items], "N": [items]}},
       "end":   {"c": [x,y], "L": ["L1"], "dir": [dx,dy], "tail": mm, "post": {"P": [items], "N": [items]}},
       "lays": ["L1","L3","L4"], "block": [["L3", x0,x1,y0,y1], ...], "lcost": {"L4": 1.4}}
  items: ["t", "L1", [[x,y],[x,y],...], w]  |  ["v", [x,y]]   (pre: pad -> ... -> join point = last point;
         post: join point = first point -> ... -> pad).  P is the right-hand net of travel (y down).
Rules: same-layer clearance CLR (0.12) to other copper, +HSX (0.2) to other HS copper; reference rule: an L3 pair needs no
foreign copper on L4 under it (+0.1), an L4 pair none on L3 (zone fills excepted); pair vias 0.45/0.25 at 0.8 pitch.
Env: VIAC (12), CLR, HSX, CS (coarse factor), MSTR (0.5), DRY=1, FORCE=1, WIN=x0,x1,y0,y1 (reach map on failure), SOFTC."""
import sys, os, math, heapq, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("RIP", "0")
os.environ.setdefault("HSX", "|SATA0_.*|USB2_.*")   # every USB2 / SATA pair is protected (hard, never ripped); USB_DM_M/USB_DP_M = RP2350 FS USB, routed as LS in A1
import numpy as np, pcbnew
from scipy import ndimage
import bp_fix as F
SRC, DST, SPECF = sys.argv[1], sys.argv[2], sys.argv[3]
SP = json.load(open(SPECF))
PN, NN = SP["P"], SP["N"]
LN = {"L1": F.L1, "L3": F.L3, "L4": F.L4, "LX": F.LX}
if F.BP6:   # JLC06161H-2116: outer 0.26/0.125 = 85.5 ohm, inner (In2/In3) 0.24/0.127 = 84.5-85.7 ohm (tools/zsolve, docs/impedance_v3_6L.json)
    GEO = {F.L1: (0.26, 0.125), F.L3: (0.24, 0.127), F.LX: (0.24, 0.127), F.L4: (0.26, 0.125)}
    LCOST = {F.L1: 1.0, F.L3: 1.0, F.LX: 0.9, F.L4: 1.2}
else:
    GEO = {F.L1: (0.26, 0.125), F.L3: (0.21, 0.127), F.L4: (0.26, 0.125)}
    LCOST = {F.L1: 1.0, F.L3: 1.0, F.L4: 1.2}
for k, v in SP.get("lcost", {}).items(): LCOST[LN[k]] = v
VIAC = float(os.environ.get("VIAC", SP.get("viac", 12))); CLR = float(os.environ.get("CLR", "0.12")); HSX = float(os.environ.get("HSX2", SP.get("hsx", 0.2)))
VS = 0.40; VD, VDR = 0.45, 0.25
x0, x1, y0, y1 = SP["reg"]
ST, EN = SP["start"], SP["end"]
def dvec(d): l = math.hypot(*d); return (d[0] / l, d[1] / l)
SD, ED = dvec(ST["dir"]), dvec(EN["dir"])
S0 = tuple(ST["c"]); S1 = (S0[0] + SD[0] * ST.get("lead", 0), S0[1] + SD[1] * ST.get("lead", 0))
E0 = tuple(EN["c"]); E1 = (E0[0] - ED[0] * EN.get("tail", 0), E0[1] - ED[1] * EN.get("tail", 0))
LAY = [LN[l] for l in SP.get("lays", ["L1", "L3", "L4"])]
b = pcbnew.LoadBoard(SRC)
def mmv(v): return (v.x / 1e6, v.y / 1e6)
g = F.Grid(b)
nP, nN = g.nid(PN), g.nid(NN)
G = F.G
i0, i1 = int((x0 - g.x0) / G), int((x1 - g.x0) / G); j0, j1 = int((y0 - g.y0) / G), int((y1 - g.y0) / G)
from PIL import Image, ImageDraw
ALLL = list(F.RL)
padm = {L: Image.new("1", (i1 - i0, j1 - j0), 0) for L in ALLL}
ownm = {L: Image.new("1", (i1 - i0, j1 - j0), 0) for L in ALLL}
for f in b.GetFootprints():
    for p in f.Pads():
        q = p.GetPosition()
        if not (x0 - 3 < q.x / 1e6 < x1 + 3 and y0 - 3 < q.y / 1e6 < y1 + 3): continue
        own = p.GetNetname() in (PN, NN)
        for L in ALLL:
            if not (p.IsOnLayer(L) or p.GetDrillSize().x > 0): continue
            sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE) if p.IsOnLayer(L) else None
            dr = ImageDraw.Draw(ownm[L] if own else padm[L])
            if sp is None:   # NPTH on a layer without copper: hole + 0.2
                c = mmv(p.GetPosition()); r = p.GetDrillSize().x / 2e6 + 0.2
                dr.ellipse([((c[0] - r - g.x0) / G - i0, (c[1] - r - g.y0) / G - j0), ((c[0] + r - g.x0) / G - i0, (c[1] + r - g.y0) / G - j0)], fill=1); continue
            for o_ in range(sp.OutlineCount()):
                ol = sp.COutline(o_); dr.polygon([((ol.CPoint(k).x / 1e6 - g.x0) / G - i0, (ol.CPoint(k).y / 1e6 - g.y0) / G - j0) for k in range(ol.PointCount())], fill=1)
padm = {L: np.array(padm[L], bool) for L in ALLL}
ownm = {L: np.array(ownm[L], bool) for L in ALLL}
# soft = unlocked low-speed copper (rip + re-route later); also free-standing unlocked GND stitch vias (deleted, re-stitched later)
gvia = np.zeros((j1 - j0, i1 - i0), bool); GVIAS = []
gtr = [t for t in b.GetTracks() if t.GetNetname() == "GND" and t.Type() == pcbnew.PCB_TRACE_T]
gends = {(round(mmv(t.GetStart())[0], 2), round(mmv(t.GetStart())[1], 2)) for t in gtr} | {(round(mmv(t.GetEnd())[0], 2), round(mmv(t.GetEnd())[1], 2)) for t in gtr}
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == "GND" and not t.IsLocked():
        c = mmv(t.GetPosition())
        if not (x0 < c[0] < x1 and y0 < c[1] < y1): continue
        if (round(c[0], 2), round(c[1], 2)) in gends: continue
        GVIAS.append(t); jj, ii = int(round((c[1] - g.y0) / G)) - j0, int(round((c[0] - g.x0) / G)) - i0; r = int(0.24 / G) + 1
        yy, xx = np.ogrid[-r:r + 1, -r:r + 1]; disc = (yy * yy + xx * xx) * G * G <= 0.235 ** 2
        sl = gvia[max(jj - r, 0):jj + r + 1, max(ii - r, 0):ii + r + 1]; sl |= disc[:sl.shape[0], :sl.shape[1]]
SOFTC = float(os.environ.get("SOFTC", "0.6"))
obs, dist, hsd, distA, okR, softR = {}, {}, {}, {}, {}, {}
for L in ALLL:
    lab = g.lab[L][j0:j1, i0:i1]
    oth = (lab != 0) & (lab != nP) & (lab != nN)
    o = oth | g.notrk[L][j0:j1, i0:i1] | padm[L]
    soft = ((g.rip[L][j0:j1, i0:i1] & oth) | gvia) & ~padm[L]
    distA[L] = ndimage.distance_transform_edt(~o) * G
    obs[L] = o & ~soft; dist[L] = ndimage.distance_transform_edt(~obs[L]) * G
    hsd[L] = ndimage.distance_transform_edt(~(g.hs[L][j0:j1, i0:i1] & oth)) * G
drill_o = (g.drill[j0:j1, i0:i1] & ~np.isin(g.lab[F.L1][j0:j1, i0:i1], [nP, nN]))
ddist = ndimage.distance_transform_edt(~drill_o) * G
novia = g.novia[j0:j1, i0:i1]
thr = {L: GEO[L][0] + GEO[L][1] / 2 + CLR + 0.04 for L in ALLL}
ok = {L: (dist[L] > thr[L]) & (hsd[L] > thr[L] + HSX) for L in ALLL}
okA = {L: distA[L] > thr[L] for L in ALLL}
# reference rule (L3 <-> L4): foreign non-GND copper on the reference layer
gid = g.nid("GND")
REFOK = {}
for La, Lr in F.XPAIRS:
    labr = g.lab[Lr][j0:j1, i0:i1]
    fr = (labr != 0) & (labr != gid) & (labr != nP) & (labr != nN)
    frh = fr & ~g.rip[Lr][j0:j1, i0:i1]
    dh = ndimage.distance_transform_edt(~frh) * G; da = ndimage.distance_transform_edt(~fr) * G
    rr = GEO[La][0] + GEO[La][1] / 2 + 0.1 + float(os.environ.get("REFM", "0.06"))   # + raster / pull-tight margin
    ok[La] &= dh > rr; okA[La] &= da > rr
    REFOK[La] = dh > rr
for L in ALLL:
    if L not in LAY: ok[L][:] = False
def fij(x, y): return int(round((y - g.y0) / G)) - j0, int(round((x - g.x0) / G)) - i0
def fxy(j, i): return (g.x0 + (i + i0) * G, g.y0 + (j + j0) * G)
for bl in SP.get("block", []):
    L = LN[bl[0]]; ja, ia = fij(bl[1], bl[3]); jb, ib = fij(bl[2], bl[4]); ok[L][max(ja, 0):jb, max(ia, 0):ib] = False
# own fixed pre/post vias are obstacles for the pair body (P/N are different nets: a leg must not graze the partner's via)
for part in (ST.get("pre", {}), EN.get("post", {})):
    for key in ("P", "N"):
        for it in part.get(key, []):
            if it[0] != "v": continue
            vj, vi = fij(*it[1])
            for L in ALLL:
                rr_ = VD / 2 + CLR + GEO[L][0] / 2 + (GEO[L][0] + GEO[L][1]) / 2; r = int(rr_ / G) + 1
                yy, xx = np.ogrid[-r:r + 1, -r:r + 1]; disc = (yy * yy + xx * xx) * G * G <= rr_ * rr_
                ja_, ia_ = vj - r, vi - r
                if ja_ < 0 or ia_ < 0: continue
                sub = ok[L][ja_:ja_ + 2 * r + 1, ia_:ia_ + 2 * r + 1]; sub &= ~disc[:sub.shape[0], :sub.shape[1]]
# terminal relief (single-track clearance near the two ends, DRC re-checks)
for (x, y), rr_ in ((S1, float(ST.get("rel", 0.3))), (E1, float(EN.get("rel", 0.6)))):
    if rr_ <= 0: continue
    jj, ii = fij(x, y); r = max(1, int(rr_ / G))
    for L in LAY:
        sub = ok[L][jj - r:jj + r, ii - r:ii + r]; d = dist[L][jj - r:jj + r, ii - r:ii + r]
        sub |= d > GEO[L][0] / 2 + CLR + 0.04
        if L in REFOK: sub &= REFOK[L][jj - r:jj + r, ii - r:ii + r]   # relief never overrides the broadside rule
vr1 = VD / 2 + CLR + 0.04
distV = {L: ndimage.distance_transform_edt(~(obs[L] | ownm[L])) * G for L in ALLL}
distVA = {L: ndimage.distance_transform_edt(~(obs[L] | ownm[L] | (distA[L] == 0))) * G for L in ALLL}
hsV = np.logical_and.reduce([hsd[L] > vr1 + HSX for L in ALLL])
sv = np.logical_and.reduce([distV[L] > vr1 for L in ALLL]) & (ddist > VDR / 2 + 0.25 + 0.05) & ~novia & hsV
svA = np.logical_and.reduce([distVA[L] > vr1 for L in ALLL])
def shift(m, dj, di):
    o = np.zeros_like(m); H_, W_ = m.shape
    o[max(dj, 0):H_ + min(dj, 0), max(di, 0):W_ + min(di, 0)] = m[max(-dj, 0):H_ + min(-dj, 0), max(-di, 0):W_ + min(-di, 0)]
    return o
k4 = int(round(VS / G)); k4d = int(round(VS / G / 1.4142))
VSITE, VSOFT = {}, {}
for d in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
    pj, pi_ = d[1], -d[0]
    kk = k4d if (pj and pi_) else k4
    VSITE[d] = shift(sv, -pj * kk, -pi_ * kk) & shift(sv, pj * kk, pi_ * kk) & np.logical_and.reduce([dist[L] > 0.2 for L in ALLL])
    VSOFT[d] = ~(shift(svA, -pj * kk, -pi_ * kk) & shift(svA, pj * kk, pi_ * kk))
print("ok frac", {b.GetLayerName(L): round(float(ok[L].mean()), 3) for L in LAY}, "via sites", int((VSITE[(-1, 0)] | VSITE[(0, 1)]).sum()))
S = int(os.environ.get("CS", SP.get("cs", 1))); CG = G * S
okc = {L: ok[L][::S, ::S] for L in ALLL}
H, W = okc[F.L1].shape
sj, si = [v // S for v in fij(*S1)]
GDIR = (int(round(ED[1] * 1.0001 / max(abs(ED[0]), abs(ED[1])))), int(round(ED[0] * 1.0001 / max(abs(ED[0]), abs(ED[1])))))
tj, ti = [v // S for v in fij(*E1)]
pen = {L: np.where(hsd[L][::S, ::S] < 0.8, 0.5, 0.0) + np.where(okA[L][::S, ::S], 0.0, SOFTC / CG) for L in ALLL}
if g.zone3 is not None: pen[F.L3] = pen[F.L3] + g.zone3[j0:j1, i0:i1][::S, ::S] * 0.3
LI = {L: k for k, L in enumerate(ALLL)}
ENDL = [LN[l] for l in EN.get("L", ["L1", "L3", "L4"])]
MSTR = int(float(os.environ.get("MSTR", SP.get("mstr", 0.5))) / CG)
SDIR = (int(round(SD[1] / max(abs(SD[0]), abs(SD[1])))), int(round(SD[0] / max(abs(SD[0]), abs(SD[1])))))
def hfun(j, i):
    if j == -1: return 0.0
    dj, di = abs(j - tj), abs(i - ti); return (max(dj, di) + 0.414 * min(dj, di)) * CG
best = {}; prev = {}
st = (LI[LN[ST["L"]]], sj, si); best[st] = 0; pq = [(hfun(sj, si), 0.0, st)]
nb = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
goal = None; pops = 0
TURN = float(os.environ.get("TURN", "0.15"))
MINRUN = int(os.environ.get("MINRUN", SP.get("minrun", 6)))   # grid steps of straight run required before a turn (no tight 45-45 zig-zags / U-loops)
def run_ok(s, din):
    q = s
    for _ in range(MINRUN - 1):
        pq_ = prev.get(q)
        if pq_ is None or pq_[0] == "via": return True      # start / just after a via: allowed
        if pq_[0] != q[0] or (q[1] - pq_[1], q[2] - pq_[2]) != din: return False
        q = pq_
    return True
NEARD = float(os.environ.get("NEARD", SP.get("neard", 3.0)))   # direction-aware states near the end (45-deg-only arrival)
while pq:
    f, c, s = heapq.heappop(pq); pops += 1
    if c > best.get(s, 1e9): continue
    k, j, i = s[:3]
    if j == -1: goal = s; break
    L = ALLL[k]
    pv = prev.get(s)
    if pv is not None and pv[0] == "via": din = ((j - pv[1][1]) // MSTR, (i - pv[1][2]) // MSTR)
    else: din = (j - pv[1], i - pv[2]) if (pv is not None and pv[0] == k) else (SDIR if s == st else None)
    for dj, di in nb:
        if din is not None and din[0] * dj + din[1] * di < 0: continue       # no U-turns
        if din is not None and din[0] * dj + din[1] * di == 0 and bool(dj and di) == bool(din[0] and din[1]): continue   # no 90 deg (octilinear 45 only)
        if s == st and (dj, di) != SDIR: continue
        if din is not None and (dj, di) != din and MINRUN > 1 and not run_ok(s, din): continue
        jj, ii = j + dj, i + di
        if not (0 <= jj < H and 0 <= ii < W) or not okc[L][jj, ii]: continue
        if (jj, ii) == (tj, ti) and ((dj, di) != GDIR or L not in ENDL): continue
        nc = c + (CG * (1.4142 if dj and di else 1.0)) * (LCOST[L] + pen[L][jj, ii]) + (TURN if din is not None and (dj, di) != din else 0)
        ns = ((k, jj, ii, dj, di) if max(abs(jj - tj), abs(ii - ti)) * CG < NEARD else (k, jj, ii)) if (jj, ii) != (tj, ti) else (k, -1, -1)
        if nc < best.get(ns, 1e9): best[ns] = nc; prev[ns] = s; heapq.heappush(pq, (nc + hfun(jj, ii), nc, ns))
    if pv is not None and pv[0] == k and pv[0] != "via":
        d = (j - pv[1], i - pv[2])
        straight = True; q = s
        for _ in range(MSTR):
            pq_ = prev.get(q)
            if pq_ is None or pq_[0] != k or (q[1] - pq_[1], q[2] - pq_[2]) != d: straight = (pq_ is None and q == st); break
            q = pq_
        if straight and VSITE[d][j * S, i * S]:
            for k2 in range(len(ALLL)):
                if k2 == k or ALLL[k2] not in LAY or not okc[ALLL[k2]][j, i]: continue
                jj, ii = j + d[0] * MSTR, i + d[1] * MSTR
                if not (0 <= jj < H and 0 <= ii < W) or not all(okc[ALLL[k2]][j + d[0] * m, i + d[1] * m] for m in range(1, MSTR + 1)): continue
                ns = (k2, jj, ii); nc = c + VIAC + MSTR * CG * (1.4142 if d[0] and d[1] else 1) * LCOST[ALLL[k2]] + (8 * SOFTC if VSOFT[d][j * S, i * S] else 0)
                if nc < best.get(ns, 1e9): best[ns] = nc; prev[ns] = ("via", s); heapq.heappush(pq, (nc + hfun(jj, ii), nc, ns))
print("A* pops", pops, "goal", goal, "cost", round(best.get(goal, -1), 2) if goal else None)
if goal is None:
    if os.environ.get("WIN"):
        X0, X1, Y0, Y1 = map(float, os.environ["WIN"].split(","))
        reach = {k: set() for k in range(len(ALLL))}
        for s_ in best: reach[s_[0]].add((s_[1], s_[2]))
        stp = float(os.environ.get("STEP", "0.2"))
        for k, L in enumerate(ALLL):
            if L not in LAY: continue
            print(b.GetLayerName(L))
            for y in np.arange(Y0, Y1, stp):
                r = ""
                for x in np.arange(X0, X1, stp):
                    jj, ii = fij(x, y)
                    r += "R" if (jj // S, ii // S) in reach[k] else ("o" if ok[L][jj, ii] else "#" if obs[L][jj, ii] else ".")
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
path = [p[:3] for p in path[::-1]]
runs = []; cur = None
for (k, j, i) in path:
    xy = fxy(j * S, i * S)
    if cur is None or cur[0] != ALLL[k]: cur = [ALLL[k], []]; runs.append(cur)
    cur[1].append(xy)
runs[0][1][0] = S1
runs[-1][1][-1] = E1
def segok(L, a, c):
    n = max(2, int(math.hypot(c[0] - a[0], c[1] - a[1]) / 0.025))
    for t in np.linspace(0, 1, n):
        jj, ii = fij(a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t)
        if not ok[L][jj, ii]: return False
    return True
def octi(a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]
    if abs(abs(dx) - abs(dy)) < 1e-6 or abs(dx) < 1e-6 or abs(dy) < 1e-6: return [[a, c]]
    m = min(abs(dx), abs(dy)); sx, sy = math.copysign(1, dx), math.copysign(1, dy)
    b1 = (a[0] + sx * m, a[1] + sy * m); b2 = (c[0] - sx * m, c[1] - sy * m)
    return [[a, b1, c], [a, b2, c]]
def ang_ok(pts):   # no corner sharper than 45 deg turn
    for k in range(1, len(pts) - 1):
        u = (pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]); v = (pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        if lu < 1e-9 or lv < 1e-9: continue
        if (u[0] * v[0] + u[1] * v[1]) / lu / lv < 0.70: return False
    return True
def merge(out):
    res = [out[0]]
    for p in out[1:]:
        if len(res) >= 2:
            a, c = res[-2], res[-1]
            if abs((c[0] - a[0]) * (p[1] - c[1]) - (c[1] - a[1]) * (p[0] - c[0])) < 1e-6 and (c[0]-a[0])*(p[0]-c[0]) + (c[1]-a[1])*(p[1]-c[1]) > 0: res[-1] = p; continue
        if math.hypot(p[0] - res[-1][0], p[1] - res[-1][1]) > 1e-6: res.append(p)
    return res
def pull(L, pts, pre=None, post=None):
    out = [pts[0]]; i = 0
    while i < len(pts) - 1:
        bestj, bestp = i + 1, [pts[i], pts[i + 1]]
        for jx in range(len(pts) - 1, i + 1, -1):
            done = False
            for cand in octi(pts[i], pts[jx]):
                nxt = pts[jx + 1] if jx + 1 < len(pts) else post
                chk = (out[-2:-1] if len(out) >= 2 else ([pre] if pre else [])) + cand + ([nxt] if nxt else [])
                if ang_ok(merge(chk)) and all(segok(L, cand[q], cand[q + 1]) for q in range(len(cand) - 1)):
                    bestj, bestp = jx, cand; done = True; break
            if done: break
        out += bestp[1:]; i = bestj
    return merge(out)
def pullp(L, pts, head, tail, pre=None, post=None):
    M = MSTR
    a = pts[:M + 1] if head else pts[:1]
    z = pts[-(M + 1):] if tail else pts[-1:]
    mid = pts[len(a) - 1: len(pts) - len(z) + 1]
    if head: pre = a[-2]
    if tail: post = z[1]
    out = (a[:-1] + pull(L, mid, pre, post) + z[1:]) if len(mid) > 1 else pts
    return merge(out)
PRE0 = (S1[0] - SD[0] * 0.05, S1[1] - SD[1] * 0.05); POST0 = E0 if EN.get("tail", 0) > 0 else None
runs = [[L, pullp(L, p, k > 0, k < len(runs) - 1, PRE0 if k == 0 else None, POST0 if k == len(runs) - 1 else None)] for k, (L, p) in enumerate(runs)]
if ST.get("lead", 0) > 0: runs[0][1].insert(0, S0)
if EN.get("tail", 0) > 0: runs[-1][1].append(E0)
runs = [[L, merge(p)] for L, p in runs]
for L, p in runs: print(b.GetLayerName(L), [(round(x, 3), round(y, 3)) for x, y in p])
from shapely.geometry import LineString, Point, Polygon as SPoly
from shapely.ops import unary_union
MM = pcbnew.FromMM
def unit(a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]; l = math.hypot(dx, dy); return (dx / l, dy / l)
def rnorm(d): return (-d[1], d[0])
def offset(pts, sft):
    out = []
    for k, p in enumerate(pts):
        if k == 0: n = rnorm(unit(pts[0], pts[1])); out.append((p[0] + n[0] * sft, p[1] + n[1] * sft)); continue
        if k == len(pts) - 1: n = rnorm(unit(pts[-2], pts[-1])); out.append((p[0] + n[0] * sft, p[1] + n[1] * sft)); continue
        n1 = rnorm(unit(pts[k - 1], p)); n2 = rnorm(unit(p, pts[k + 1]))
        na = (n1[0] + n2[0], n1[1] + n2[1]); l = math.hypot(*na); na = (na[0] / l, na[1] / l)
        f = sft / (na[0] * n1[0] + na[1] * n1[1]); out.append((p[0] + na[0] * f, p[1] + na[1] * f))
    return out
def conv(itlist):
    out = []
    for it in itlist:
        if it[0] == "v": out.append(("v", None, tuple(it[1]), None, VD))
        else:
            pts = [tuple(p) for p in it[2]]
            for a, c in zip(pts, pts[1:]): out.append(("t", LN[it[1]], a, c, it[3]))
    return out
def lastpt(itlist):
    it = itlist[-1]; return tuple(it[1]) if it[0] == "v" else tuple(it[2][-1])
def firstpt(itlist):
    it = itlist[0]; return tuple(it[1]) if it[0] == "v" else tuple(it[2][0])
items = {PN: [], NN: []}; viaP = []
for net, key in ((PN, "P"), (NN, "N")):
    items[net] += conv(ST.get("pre", {}).get(key, [])) + conv(EN.get("post", {}).get(key, []))
for k, (L, pts) in enumerate(runs):
    w, gp = GEO[L]; sft = (w + gp) / 2
    for net, key, sg in ((PN, "P", +1), (NN, "N", -1)):
        op = offset(pts, sg * sft)
        if k == 0 and ST.get("pre", {}).get(key): op = [lastpt(ST["pre"][key])] + op
        if k > 0: op = [viaP[k - 1][0 if net == PN else 1]] + op
        if k < len(runs) - 1:
            d = unit(pts[-2], pts[-1]); n = rnorm(d); c = pts[-1]
            vc = (round(c[0] + n[0] * sg * VS, 3), round(c[1] + n[1] * sg * VS, 3)); op = op + [vc]
            if net == PN: viaP.append([vc, None, d])
            else: viaP[-1][1] = vc
        elif EN.get("post", {}).get(key): op = op + [firstpt(EN["post"][key])]
        for a, c in zip(op, op[1:]):
            if math.dist(a, c) > 1e-4: items[net].append(("t", L, a, c, w))
for vp, vn, d in viaP:
    items[PN].append(("v", None, vp, None, VD)); items[NN].append(("v", None, vn, None, VD))
def igeom(it, L):
    kd, l, a, c, w = it
    if kd == "v": return Point(a).buffer(w / 2, 16)
    if l != L: return None
    return LineString([a, c]).buffer(w / 2, 8)
newg = {L: unary_union([gg for net in items for it in items[net] for gg in [igeom(it, L)] if gg is not None]) for L in ALLL}
# reference footprint of the new pair copper (for the L3<->L4 rule)
refg = {Lr: (newg[La].buffer(0.1) if not newg[La].is_empty else None) for La, Lr in F.XPAIRS}
viag = unary_union([Point(it[2]).buffer(VD / 2) for net in items for it in items[net] if it[0] == "v"]) if any(it[0] == "v" for net in items for it in items[net]) else None
LEN = {}
for net in items:
    ln = sum(math.dist(it[2], it[3]) for it in items[net] if it[0] == "t"); nv = sum(1 for it in items[net] if it[0] == "v"); LEN[net] = (ln, nv)
    print(net, "len %.2f mm" % ln, "vias", nv)
print("skew (P-N, vias 1.6) %.3f" % (LEN[PN][0] - LEN[NN][0] + 1.6 * (LEN[PN][1] - LEN[NN][1])))
CL2 = 0.12
conf = []; hardc = []
def tgeom(t, L):
    if t.Type() == pcbnew.PCB_VIA_T: return Point(mmv(t.GetPosition())).buffer(t.GetWidth(L) / 2e6, 16)
    if t.GetLayer() != L: return None
    return LineString([mmv(t.GetStart()), mmv(t.GetEnd())]).buffer(t.GetWidth() / 2e6, 8)
for t in b.GetTracks():
    n = t.GetNetname()
    if n in (PN, NN): continue
    hit = False
    for L in ALLL:
        gg = tgeom(t, L)
        if gg is None: continue
        cl = CL2 + (HSX if F.HS.match(n) else 0) - 0.02
        if not newg[L].is_empty and gg.distance(newg[L]) < cl: hit = True; break
        if t.Type() != pcbnew.PCB_VIA_T and n != "GND" and refg.get(L) is not None and gg.intersects(refg[L]): hit = True; break
    if hit: (conf if (g.ripable(t) or t in GVIAS) else hardc).append(t)
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() in (PN, NN): continue
        for L in ALLL:
            if not p.IsOnLayer(L): continue
            sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
            for o_ in range(sp.OutlineCount()):
                ol = sp.COutline(o_); pg = SPoly([(ol.CPoint(q).x / 1e6, ol.CPoint(q).y / 1e6) for q in range(ol.PointCount())])
                if not newg[L].is_empty and pg.distance(newg[L]) < CL2 - 0.005: hardc.append(("pad", f.GetReference(), p.GetNumber(), p.GetNetname(), b.GetLayerName(L), round(pg.distance(newg[L]), 3)))
        if p.GetDrillSize().x > 0 and viag is not None and Point(mmv(p.GetPosition())).distance(viag) < p.GetDrillSize().x / 2e6 + 0.25:
            hardc.append(("hole", f.GetReference(), p.GetNumber()))
cn = sorted({t.GetNetname() for t in conf if t.GetNetname() != "GND"})
ngv = sum(1 for t in conf if t.GetNetname() == "GND")
print("soft conflicts:", len(conf), "items, nets", cn, "GND stitch vias", ngv)
print("hard conflicts:", [(x if isinstance(x, tuple) else (x.GetNetname(), "via" if x.Type() == pcbnew.PCB_VIA_T else b.GetLayerName(x.GetLayer()), mmv(x.GetPosition() if x.Type() == pcbnew.PCB_VIA_T else x.GetStart()))) for x in hardc])
json.dump({"runs": [[b.GetLayerName(L), p] for L, p in runs], "len": LEN, "soft": cn, "hard": len(hardc)}, open(os.environ.get("CL", "/tmp/pair2_cl.json"), "w"))
if os.environ.get("DRY"): sys.exit(0)
if hardc and not os.environ.get("FORCE"): print("hard conflicts -> abort"); sys.exit(3)
# rip every unlocked item of a conflicting LS net (whole net re-routed from pads)
for t in list(b.GetTracks()):
    if (t.GetNetname() in cn and g.ripable(t)) or (t in conf and t.GetNetname() == "GND"):
        b.Remove(t); F.KEEPALIVE.append(t)
for net in (PN, NN):
    nobj = b.FindNet(net)
    for kd, l, a, c, w in items[net]:
        if kd == "t":
            tr = pcbnew.PCB_TRACK(b); tr.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); tr.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
            tr.SetWidth(MM(w)); tr.SetLayer(l); tr.SetNet(nobj); tr.SetLocked(True); b.Add(tr)
        else:
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); v.SetWidth(MM(VD)); v.SetDrill(MM(VDR))
            v.SetNet(nobj); v.SetLocked(True); b.Add(v)
# GND stitching vias next to each new pair via
gnd = b.FindNet("GND"); added = []
def allcopper_ok(c, r):
    pt = Point(c).buffer(r)
    jj, ii = fij(*c)
    if novia[jj, ii]: return False
    for t in b.GetTracks():
        for L in ALLL:
            gg = tgeom(t, L)
            if gg is not None and gg.distance(pt) < CL2 + (HSX if F.HS.match(t.GetNetname()) else 0) and not (t.GetNetname() == "GND" and t.Type() == pcbnew.PCB_TRACE_T): return False
        if t.Type() == pcbnew.PCB_VIA_T and math.dist(mmv(t.GetPosition()), c) < VD / 2 + t.GetWidth(F.L1) / 2e6 + 0.12: return False
    for f in b.GetFootprints():
        for p in f.Pads():
            q = mmv(p.GetPosition())
            if math.dist(q, c) > 4: continue
            if p.GetDrillSize().x > 0 and math.dist(q, c) < p.GetDrillSize().x / 2e6 + VDR / 2 + 0.3: return False
            for L in ALLL:
                if not p.IsOnLayer(L): continue
                if p.GetNetname() == "GND" and p.GetDrillSize().x == 0: continue
                sp = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
                for o_ in range(sp.OutlineCount()):
                    ol = sp.COutline(o_); pg = SPoly([(ol.CPoint(q_).x / 1e6, ol.CPoint(q_).y / 1e6) for q_ in range(ol.PointCount())])
                    if pg.distance(pt) < CL2: return False
    return True
vlist = list(viaP) + [tuple(x) for x in SP.get("stitch", [])]
if os.environ.get("NOSTITCH") == "1": vlist = []   # 6L chain: return vias are added after all pairs (they were blocking later pairs' escapes)
for vp, vn, d in vlist:
    n = rnorm(d)
    for c, sg in ((vp, +1), (vn, -1)):
        done = False
        for rr in (0.75, 0.85, 1.0, 1.15, 1.3):
            for ang in (0, 30, -30, 60, -60, 90, -90, 120, -120):
                a = math.radians(ang); ox, oy = n[0] * sg, n[1] * sg
                ux, uy = ox * math.cos(a) - oy * math.sin(a), ox * math.sin(a) + oy * math.cos(a)
                q = (round(c[0] + ux * rr, 3), round(c[1] + uy * rr, 3))
                if allcopper_ok(q, VD / 2):
                    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(q[0]), MM(q[1]))); v.SetWidth(MM(VD)); v.SetDrill(MM(VDR))
                    v.SetNet(gnd); v.SetLocked(True); b.Add(v); added.append(q); done = True; break
            if done: break
        print("GND stitch for", c, "->", added[-1] if done else "NONE")
RIPF = os.environ.get("RIPLOG", os.path.join(os.path.dirname(DST), "v3_ripped.txt"))
if os.environ.get("NOREROUTE"):
    old = set(open(RIPF).read().split()) if os.path.exists(RIPF) else set()
    open(RIPF, "w").write("\n".join(sorted(old | set(cn))) + "\n"); print("ripped (re-route later):", sorted(old | set(cn)))
    cn = []
g2 = F.Grid(b); fails = []
for n in cn:
    a, okr = F.route_net(g2, n); print("reroute", n, okr, len(a))
    if not okr: fails.append(n)
print("reroute fails:", fails)
pcbnew.SaveBoard(DST, b); print("saved", DST)
