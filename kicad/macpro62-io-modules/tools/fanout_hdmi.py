"""MOD-H hand fan-out (D-IO16 rev 2026-10-04 ~10:45 ET): HOAUC HYC79-HDMIA19-105 (real land pattern, tools/make_fp_hyc79.py) -> locked tail lanes.
Module frame (u, v), v = -KiCad y.  J1 at (0, 0) rot 0: ONE row of 19 SMD pads 0.30 x 2.00 at v -4.5 .. -2.5, pin n at u = -4.21 + 0.5 (n - 1)
(pin 1 D2+ at -4.21 ... pin 19 HPD at +4.79), 2 dummy pads at u -4.71 / -5.21; THT legs (GND) D1.9 at (+-7.25, -0.9) and (0, +2.4).
Why a new HDMI lane map (pmi50.ROLES["HDMI"], 2026-10-04): with one pad row every trace leaves the pad ends toward +v and turns toward the tail,
so the planar order at the tail is fixed by the pad order (pin 1 side on top): D2+ D2- D1+ D1- D0+ D0- CK+ CK- SCL SDA (+5V) HPD. The old map
(placeholder, two staggered rows) needed ~37 crossings for that order; the new one needs none: the four TMDS pairs take the eight GND-flanked
row-A positions k8/9 (CK, USB2_A/B), k11/12 (D0, LS_A1/2), k14/15 (D1, HS3), k17/18 (D2, HS0); DDC SCL / SDA / HPD take row-B k8 / k9 / k11
(LS_B1 / LS_B2 / SPARE_B1). The PMI-50 table itself (pmi50.PMI) is unchanged.
Topology: 1) staircase out of the pad row, levels below the centre leg (v <= 1.26 at u 0); a GND via 0.40/0.20 above every GND pad (pins 2 5 8 11 17);
2) the whole bundle climbs 1.59 at 45 deg after pin 19 and passes OVER the outboard leg (HPD hugs it at r 1.10); 3) the TMDS pairs run straight into
their tail lanes; SCL / SDA / HPD wrap down the leg's outboard side to the row-B lanes. +5V drops to L2 right at pin 18 and runs under the leg to the
L2 VBUS band (crossing only the slow SE lanes). Intra-pair skew: the P pad is 1.0 farther from the tail; it is matched on the N member's riser with
chamfered bumps toward the P riser (above the GND via; CK-: toward the NC CEC / UTIL pads) and a 45 deg chamfer on the P corner -> 0 port pad -> DF40 pad."""
import math
import pcbnew
from pcbnew import FromMM
import fanout_usbc as FC
W_HS, W_SE = 0.08, 0.10
VIA_S = (0.40, 0.20)
def pu(n): return -4.21 + 0.5 * (n - 1)
PAD_TOP = -2.5
PIN = {"D2_P": 1, "D2_N": 3, "D1_P": 4, "D1_N": 6, "D0_P": 7, "D0_N": 9, "CK_P": 10, "CK_N": 12, "DDC_SCL": 15, "DDC_SDA": 16, "VBUS": 18, "HPD": 19}
GND_PINS = (2, 5, 8, 11, 17)
LEG_O, LEG_C, R_LEG = (7.25, -0.9), (0.0, 2.4), 0.95
RISE = 1.59
# levels over the outboard leg (b) = tail lanes for the TMDS pairs; staircase levels a = b - RISE
B = {"HPD": 0.20, "DDC_SDA": 0.38, "DDC_SCL": 0.56, "CK_N": 0.90, "CK_P": 1.13, "D0_N": 1.46, "D0_P": 1.69, "D1_N": 2.02, "D1_P": 2.25, "D2_N": 2.58, "D2_P": 2.81}
ORDER = ["D2_P", "D2_N", "D1_P", "D1_N", "D0_P", "D0_N", "CK_P", "CK_N", "DDC_SCL", "DDC_SDA", "HPD"]      # top -> bottom
S_HPD = 5.0                       # HPD rise start (45 deg line clears the outboard leg at >= 1.10)
plen = FC.plen
def riser_bumps(u0, z0, z1, E, hmax, d=1):
    """chamfered bumps on a vertical riser at u0 (going up, z0 -> z1), pointing to -u (d = 1) or +u (d = -1), adding E"""
    pts, n, h = FC.solve_bumps(E, z0, z1, 0.0, d, hmax)
    return [(u0 - y, x) for (x, y) in pts], n, h
def route(b, BM, START, LANE_L, us):
    T, V = [], []
    F, Bc = pcbnew.F_Cu, pcbnew.B_Cu
    rep = dict(pairs={}, notes=[])
    # HPD reference path (bottom of the bundle): horizontal at a, 45 deg rise from S_HPD, then over the leg; the rest are miter offsets of it
    aH = B["HPD"] - RISE
    ref = [(pu(PIN["HPD"]), aH), (S_HPD, aH), (S_HPD + RISE, B["HPD"]), (us - 0.6, B["HPD"])]
    path = {}
    for nm in ORDER:
        d = B[nm] - B["HPD"]
        off = BM.offset_poly(ref, [d] * len(ref))
        u0 = pu(PIN[nm]); a = B[nm] - RISE
        assert abs(off[0][1] - a) < 1e-6 and off[1][0] > u0 + 0.05, (nm, off[:2], u0)
        assert abs(off[1][1] - a) < 1e-6
        path[nm] = [(u0, PAD_TOP), (u0, a)] + off[1:]                     # riser, then the level a up to this trace's own 45 deg corner
    path = {k: [p for i, p in enumerate(v) if i == 0 or math.hypot(p[0] - v[i - 1][0], p[1] - v[i - 1][1]) > 1e-6] for k, v in path.items()}
    # ---- outboard end: TMDS straight into the lanes; SE wrap down the leg's outboard side (octagon tangents at r = 1.10 + offset) ----
    for nm in ORDER:
        p = path[nm]
        if nm in ("HPD", "DDC_SDA", "DDC_SCL"):
            d = B[nm] - B["HPD"]; r = 1.10 + d; cu_, cv_ = LEG_O
            k45 = cu_ + cv_ + r * math.sqrt(2)            # tangent u + v = k45
            p = [q for q in p if q[0] < k45 - B[nm] - 1e-6] + [(k45 - B[nm], B[nm])]
            uv = cu_ + r                                   # vertical tangent
            p += [(uv, k45 - uv)]
            vt = START[nm][1]
            p += [(uv, vt), START[nm]]
        else:
            p = [q for q in p if q[0] < START[nm][0] - 1e-6]
            assert abs(p[-1][1] - START[nm][1]) < 1e-6, (nm, p[-1], START[nm])
            p += [START[nm]]
        path[nm] = p
    # ---- intra-pair matching: P corner chamfer + N riser bumps (toward the P riser, above the GND via) ----
    for pr in ("D2", "D1", "D0", "CK"):
        nP, nN = pr + "_P", pr + "_N"
        P_, N_ = path[nP], path[nN]
        uP, uN = pu(PIN[nP]), pu(PIN[nN])
        x = 0.30                                          # P corner chamfer (riser -> level)
        aP = P_[1][1]; P_ = [P_[0], (uP, aP - x), (uP + x, aP)] + P_[2:]
        if math.hypot(P_[3][0] - P_[2][0], P_[3][1] - P_[2][1]) < 1e-6: P_ = P_[:3] + P_[4:]
        LP = plen(P_) + LANE_L[nP]; LN = plen(N_) + LANE_L[nN]; E = LP - LN
        assert E > 0, (pr, E)
        if pr == "CK":   # CK- riser: bumps to +u over the NC pads 13 / 14 (CEC / UTIL), below the SCL level, clear of the pad tops
            z0, z1, hm, dd = PAD_TOP + 0.20, N_[1][1] - 0.12, 1.10, -1
        else:            # toward the P riser, above the GND via (top at -1.95), below the N corner
            z0, z1, hm, dd = PAD_TOP + 0.70, N_[1][1] - 0.12, 0.82, 1
        bp, n, h = riser_bumps(uN, z0, z1, E, hm, dd)
        N_ = [N_[0]] + bp + N_[1:]
        path[nP], path[nN] = P_, N_
        LP2 = plen(P_) + LANE_L[nP]; LN2 = plen(N_) + LANE_L[nN]
        rep["pairs"][pr] = dict(fanout_P=round(plen(P_), 3), fanout_N=round(plen(N_), 3), lane_P=round(LANE_L[nP], 3), lane_N=round(LANE_L[nN], 3),
                                skew_before=round(E, 3), bumps=n, bump_h=round(h, 3), total_P=round(LP2, 3), total_N=round(LN2, 3), skew_P_minus_N=round(LP2 - LN2, 4))
    for nm in ORDER:
        p = path[nm]; p[0] = (pu(PIN[nm]), -3.5)              # start at the pad centre
        T.append((nm, F, p, W_HS if nm[:2] in ("D0", "D1", "D2", "CK") else W_SE))
    # ---- GND pads -> 0.40/0.20 via above each pad end ----
    for n in GND_PINS:
        u = pu(n); T.append(("GND", F, [(u, -3.5), (u, -2.15)], 0.2)); V.append(("GND", u, -2.15, VIA_S))
    # ---- +5V: pin 18 -> via -> L2 under the leg -> L2 VBUS band (finish) ----
    u18 = pu(PIN["VBUS"])
    T.append(("VBUS", F, [(u18, -3.5), (u18, -1.95)], 0.25)); V.append(("VBUS", u18, -1.95, VIA_S))
    T.append(("VBUS", Bc, [(u18, -1.95), (u18 + 0.2, -2.15), (5.6, -2.15), (5.8, -2.35), (8.6, -2.35), (8.9, -2.05), (8.9, 0.0), (9.1, 0.0)], 0.3))
    # ---- clearance audit (shapely, L1 / L2 + pads + legs) ----
    from shapely.geometry import LineString, Point, box
    cu = {F: [], Bc: []}
    for (n_, L_, p_, w_) in T: cu[L_].append((n_, LineString(p_).buffer(w_ / 2, 16)))
    for (n_, u_, v_, (d_, _)) in V:
        for L_ in cu: cu[L_].append((n_, Point(u_, v_).buffer(d_ / 2, 32)))
    pinnet = {v: k for k, v in PIN.items()}
    for n in range(1, 20):
        nm = pinnet.get(n, "GND" if n in GND_PINS else "NC%d" % n); cu[F].append((nm, box(pu(n) - 0.15, -4.5, pu(n) + 0.15, -2.5)))
    for x_ in (-4.71, -5.21): cu[F].append(("MP%.2f" % x_, box(x_ - 0.15, -4.5, x_ + 0.15, -2.5)))
    for c_ in (LEG_O, (-LEG_O[0], LEG_O[1]), LEG_C):
        for L_ in cu: cu[L_].append(("GND", Point(c_).buffer(R_LEG, 32)))
    worst = {}
    for L_, items in cu.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i][0] == items[j][0]: continue
                dd = items[i][1].distance(items[j][1]); key = "%s/%s" % tuple(sorted((items[i][0], items[j][0])))
                worst[key] = min(worst.get(key, 9), round(dd, 3))
    rep["min_clearance"] = min(worst.values()); rep["closest"] = sorted(worst.items(), key=lambda kv: kv[1])[:8]
    assert rep["min_clearance"] >= 0.078 - 1e-6, rep["closest"]
    for (nm, L, pts, w) in T: BM.trk(b, nm, pts, w, L)
    for (nm, u, v, (d, dr)) in V:
        x = pcbnew.PCB_VIA(b); x.SetPosition(BM.P(u, v)); x.SetDrill(FromMM(dr)); x.SetWidth(FromMM(d)); x.SetNet(BM.net(b, nm)); x.SetLocked(True); b.Add(x)
    rep["fanout_lengths"] = {nm: round(plen(p), 3) for (nm, L, p, w) in T if nm in PIN}
    rep["counts"] = dict(tracks=sum(len(p) - 1 for (_, _, p, _) in T), vias=len(V), signal_vias=0)
    return rep
