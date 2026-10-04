"""MOD-A hand fan-out (D-IO16 rev 2026-10-04 ~10:30 ET): Hong Cheng HC-USB3.0-L137-WJ (THT, 2.0 pitch) -> locked tail lanes, replacing the
Freerouting fan-out (which left SSRX +2.77 / SSTX +2.64 / D -2.65 mm of intra-pair skew).
Module frame (u, v), v = -KiCad y.  J1 at (0, 0) rot 0: SS row (pins 9 8 7 6 5 = SSTX_P SSTX_N GND SSRX_P SSRX_N) at v +0.8, u -4 -2 0 2 4;
USB2 row (pins 1 2 3 4 = VBUS D_N D_P GND) at v -0.8, u -3.5 -1 1 3.5; pads D1.25 (drill 0.75); shell legs (GND) D2.8 at (+-6.575, -0.65).
Topology (all signal copper on L1, no vias on any signal):
  * every pair leaves its row OUTWARD (SS up, USB2 down) and turns toward the tail; the pin nearer the tail becomes the inner member, which is the
    PMI lane order (inner = SSRX_N / SSTX_N / D_P), so there is no crossover. The pairs couple (0.10 / 0.10) once both members are on the pair line.
  * the 2.0 mm THT pitch makes the outer member ~2 mm longer; with the locked lane lengths the inner member is short by 2.6-3.4 mm. It is matched
    on the INNER member right after its pin (inside the stiffened port area, before the pair couples) with chamfered bumps pulled away from the
    outer member (tools/fanout_usbc.py bump geometry) -> intra-pair skew 0 port pad -> DF40 pad.
  * SSRX runs at v 1.9 / 2.1 (bumps down toward the shell leg), SSTX at 2.55 / 2.75 over it (bumps down over the GND pin), USB2 at -2.45 / -2.65 under
    the shell leg (bumps up between the pins / shell); all three jog to their tail lanes just before the stiffener edge.
  * VBUS: pin 1 -> L1 0.8 strip under the USB2 pair -> 2 x 0.55/0.3 vias -> L2 0.5 riser -> the L2 VBUS band / L1 strip at the tail start (the USB2 pair
    crosses the 0.5 riser once at 45 deg - its only reference gap).
  * L2 under the port is the same 0.10 / 0.30 cross-hatch as the tail (25 um core: 90 ohm at 0.10 / 0.10, a25 coupon)."""
import math
import pcbnew
from pcbnew import FromMM
import fanout_usbc as FC
W, S = 0.10, 0.10
PITCH = W + S
VIA_V = (0.55, 0.30)
PINS = {"VBUS": (-3.5, -0.8), "D_N": (-1.0, -0.8), "D_P": (1.0, -0.8), "GND4": (3.5, -0.8),
        "SSTX_P": (-4.0, 0.8), "SSTX_N": (-2.0, 0.8), "GND7": (0.0, 0.8), "SSRX_P": (2.0, 0.8), "SSRX_N": (4.0, 0.8)}
SHELL = [(-6.575, -0.65), (6.575, -0.65)]
R_PIN, R_SHELL = 0.625, 1.4
plen = FC.plen
def bump_cap(z0, z1, hmax, c=0.06):
    n = 0
    while FC.bump_width(n + 1, c=c) <= z1 - z0: n += 1
    return n * (2 * hmax - (8 * c - 4 * c * math.sqrt(2))), n
def multi_bumps(E, zones, v0, d):
    """distribute E over zones [(z0, z1, hmax)], left to right; returns bump points (sorted by u) + per-zone (n, h)"""
    out, info, rest = [], [], E
    for i, (z0, z1, hm) in enumerate(zones):
        if rest < 0.005: break
        cap, nmax = bump_cap(z0, z1, hm)
        take = rest if (rest <= cap or i == len(zones) - 1) else cap * 0.999
        pts, n, h = FC.solve_bumps(take, z0, z1, v0, d, hm)
        out.append(pts); info.append((round(z0, 2), round(z1, 2), n, round(h, 3), round(take, 3))); rest -= take
    pts = [p for blk in sorted(out, key=lambda b_: b_[0][0]) for p in blk]
    return pts, info
def route(b, BM, START, LANE_L, us):
    T, V = [], []      # (net, layer, pts, width) / (net, u, v, (d, drill))
    F, Bc = pcbnew.F_Cu, pcbnew.B_Cu
    rep = dict(pairs={}, notes=[])
    # (name, outer net, inner net, side, pair-line centre v, x_a (pair line start), x_j (jog start), outer pre-route, inner pre-route, bump zones, P is outer)
    PR = [("SSRX", "SSRX_P", "SSRX_N", +1, 2.00, 4.40, 7.75, [PINS["SSRX_P"], (2.0, 1.6), (2.5, 2.1)], [PINS["SSRX_N"], (4.0, 1.5), (4.4, 1.9)],
           [(4.75, 7.55, 0.85)], True),
          ("SSTX", "SSTX_P", "SSTX_N", +1, 2.65, -1.60, 7.75, [PINS["SSTX_P"], (-4.0, 2.15), (-3.4, 2.75)], [PINS["SSTX_N"], (-2.0, 2.15), (-1.6, 2.55)],
           [(-1.35, 1.72, 0.85)], True),
          ("D", "D_N", "D_P", -1, -2.55, 1.40, 7.20, [PINS["D_N"], (-1.0, -1.85), (-0.2, -2.65)], [PINS["D_P"], (1.0, -2.05), (1.4, -2.45)],
           [(1.72, 2.78, 0.82), (4.25, 5.00, 0.95)], False)]
    for (nm, no, ni, sd, vc, xa, xj, opre, ipre, zones, p_out) in PR:
        so_, si_ = START[no], START[ni]; vt = (so_[1] + si_[1]) / 2
        assert abs(abs(so_[1]) - abs(si_[1]) - PITCH) < 1e-3, (nm, so_, si_)
        dv = abs(vc - vt)
        cl = [(xa, vc), (xj, vc), (xj + dv, vt), (us, vt)]
        oo = BM.offset_poly(cl, [sd * PITCH / 2] * 4); ii = BM.offset_poly(cl, [-sd * PITCH / 2] * 4)
        oo[-1] = so_; ii[-1] = si_
        assert math.hypot(oo[0][0] - opre[-1][0], oo[0][1] - opre[-1][1]) < 1e-6 or abs(oo[0][1] - opre[-1][1]) < 1e-6, (nm, oo[0], opre[-1])
        assert math.hypot(ii[0][0] - ipre[-1][0], ii[0][1] - ipre[-1][1]) < 1e-6, (nm, ii[0], ipre[-1])
        outer = opre + oo; inner0 = ipre; inner1 = ii[1:]
        Lo = plen(outer) + LANE_L[no]; Li = plen(inner0 + inner1) + LANE_L[ni]
        E = Lo - Li; assert E > -1e-6, (nm, E)
        assert max(z[1] for z in zones) < ii[1][0] - 0.1, (nm, zones, ii[1])
        bp, info = multi_bumps(E, zones, ii[0][1], -sd)
        inner = inner0 + bp + inner1
        T.append((no, F, outer, W)); T.append((ni, F, inner, W))
        Lo2 = plen(outer) + LANE_L[no]; Li2 = plen(inner) + LANE_L[ni]
        P2, N2 = (Lo2, Li2) if p_out else (Li2, Lo2)
        rep["pairs"][nm] = dict(outer=no, inner=ni, fanout_outer=round(plen(outer), 3), fanout_inner=round(plen(inner), 3), lane_outer=round(LANE_L[no], 3),
                                lane_inner=round(LANE_L[ni], 3), skew_before=round(E, 3), bumps=info, total_P=round(P2, 3), total_N=round(N2, 3),
                                skew_P_minus_N=round(P2 - N2, 4))
    # ---- VBUS: pin 1 -> L1 strip under the USB2 pair -> vias -> L2 riser -> L2 VBUS band (finish) / tail vias (build) ----
    T.append(("VBUS", F, [PINS["VBUS"], (-3.5, -3.35), (8.25, -3.35)], 0.8))
    for u_ in (7.65, 8.25): V.append(("VBUS", u_, -3.35, VIA_V))
    T.append(("VBUS", Bc, [(7.65, -3.35), (8.25, -3.35), (8.45, -3.15), (8.45, -0.35)], 0.5))
    # ---- clearance audit (L1 + L2, shapely): every signal / VBUS copper vs other-net copper ----
    from shapely.geometry import LineString, Point
    cu = {F: [], Bc: []}
    for (n_, L_, p_, w_) in T: cu[L_].append((n_, LineString(p_).buffer(w_ / 2, 16)))
    for (n_, u_, v_, (d_, _)) in V:
        for L_ in cu: cu[L_].append((n_, Point(u_, v_).buffer(d_ / 2, 32)))
    for k_, (u_, v_) in PINS.items():
        for L_ in cu: cu[L_].append(("GND" if k_.startswith("GND") else k_, Point(u_, v_).buffer(R_PIN, 32)))
    for (u_, v_) in SHELL:
        for L_ in cu: cu[L_].append(("GND", Point(u_, v_).buffer(R_SHELL, 32)))
    worst = {}
    for L_, items in cu.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i][0] == items[j][0]: continue
                dd = items[i][1].distance(items[j][1]); key = "%s/%s" % tuple(sorted((items[i][0], items[j][0])))
                worst[key] = min(worst.get(key, 9), round(dd, 3))
    mn = min(worst.values()); rep["min_clearance"] = mn; rep["closest"] = sorted(worst.items(), key=lambda kv: kv[1])[:6]
    assert mn >= 0.078 - 1e-6, rep["closest"]
    # ---- emit ----
    for (nm, L, pts, w) in T: BM.trk(b, nm, pts, w, L)
    for (nm, u, v, (d, dr)) in V:
        x = pcbnew.PCB_VIA(b); x.SetPosition(BM.P(u, v)); x.SetDrill(FromMM(dr)); x.SetWidth(FromMM(d)); x.SetNet(BM.net(b, nm)); x.SetLocked(True); b.Add(x)
    rep["fanout_lengths"] = {}
    for (nm, L, pts, w) in T: rep["fanout_lengths"][nm] = round(rep["fanout_lengths"].get(nm, 0) + plen(pts), 3)
    rep["counts"] = dict(tracks=sum(len(p) - 1 for (_, _, p, _) in T), vias=len(V), signal_vias=0)
    return rep
# L2 cross-hatch GND under the whole port stiffener (finish stage, priority 1 over the solid L2 GND); 25 um core -> 90 ohm at 0.10 / 0.10 (a25 coupon)
L2_HATCH_PORT = [(-8.4, -4.4), (9.0, -4.4), (9.0, 4.4), (-8.4, 4.4)]
