"""MOD-C hand fan-out (D-IO16 rev 2026-10-04): HOAUC HYCW417-USBC24-180B (real LCSC/EasyEDA land pattern) -> locked tail lanes.
Module frame (u, v), v = -KiCad y.  J1 at (0, 0) rot 0: A row at v = +1.65 (A1 u -2.75 ... A12 u +2.75), B row at v = -1.65 (B1 u +2.75 ... B12 -2.75),
pads 0.27 x 1.30 (|v| 1.00 .. 2.30); THT shell slots (GND) at (+-4.10, +-1.47) pad 1.70 x 1.20; NPTH pegs 0.60 at (-5.5, +1.3) and (+5.5, -1.3).
Topology (all SS lanes on L1 over L2 GND, no vias on any SS lane):
  * the 4 SS pairs leave OUTWARD (A row up, B row down) and turn toward the tail; that gives the PMI order and polarity of every pair
    without a crossover (outer = B member of each lane: SSTX1_P, SSRX2_N, SSTX2_N, SSRX1_P).
  * SBU1, CC1, D+/D-, CC2, SBU2 run through the channel between the rows and the gap between the two outboard shell slots; CC1 and SBU2 take one
    L2 hop each (0.40/0.20 vias) to reach their PMI order; the B6/B7 contacts join D_P / D_N with an L1 stub (B6) and an L2 hop (B7).
  * VBUS: A4-B9 bar + 4 vias, A9 / B4 one 0.55/0.3 via each outward; L2 VBUS pour under the channel + gap; 0.55/0.3 vias at the tail start
    feed the L1 VBUS strip.
  * intra-pair skew (port fan-out + locked tail/paddle lanes) is cancelled on the INNER member near the pins with chamfered bumps."""
import math
import pcbnew
from pcbnew import FromMM
W_HS, S_HS, W_SE = 0.09, 0.10, 0.10
PITCH = W_HS + S_HS                      # 0.19 centre-centre in a pair
VIA_S = (0.40, 0.20)                     # signal hop via (JLC FPC standard, no surcharge)
VIA_V = (0.55, 0.30)                     # VBUS via
def A(n): return (-2.75 + 0.5 * (n - 1), 1.65)
def B(n): return (2.75 - 0.5 * (n - 1), -1.65)
def plen(pts): return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))
def bump_pts(x0, v0, d, n, h, fw=0.25, g=0.30, c=0.06):
    out = []; x = x0
    for i in range(n):
        out += [(x, v0), (x + c, v0 + d * c), (x + c, v0 + d * (h - c)), (x + 2 * c, v0 + d * h), (x + 2 * c + fw, v0 + d * h),
                (x + 3 * c + fw, v0 + d * (h - c)), (x + 3 * c + fw, v0 + d * c), (x + 4 * c + fw, v0)]
        x += 4 * c + fw + g
    return out
def bump_width(n, fw=0.25, g=0.30, c=0.06): return n * (4 * c + fw) + (n - 1) * g
def solve_bumps(E, z0, z1, v0, d, hmax, c=0.06):
    """n bumps of depth h centred in [z0, z1] that add exactly E (mm) of length"""
    if E < 0.005: return [], 0, 0.0
    for cc in (c, 0.045, 0.03):          # smaller chamfer for very small E (2026-10-04: 0.078 paddle lanes shrank the USB2 skew)
      for n in range(1, 8):
        h = (E / n + 8 * cc - 4 * cc * math.sqrt(2)) / 2
        if h <= hmax and h >= 2 * cc + 0.02 and bump_width(n, c=cc) <= z1 - z0:
            x0 = (z0 + z1) / 2 - bump_width(n, c=cc) / 2; pts = bump_pts(x0, v0, d, n, h, c=cc)
            ext = plen(pts) - (pts[-1][0] - pts[0][0]); assert abs(ext - E) < 1e-6, (ext, E)
            return pts, n, h
    raise RuntimeError("cannot fit %.3f mm of bumps in [%.2f, %.2f] (hmax %.2f)" % (E, z0, z1, hmax))
def route(b, BM, START, LANE_L, us):
    """START[net] = (u, v) lane start at u = us; LANE_L[net] = locked lane length us -> header pad. Returns (report dict, wedge via list)."""
    T = []      # (net, layer, pts, width)
    V = []      # (net, u, v, (d, drill))
    F, Bc = pcbnew.F_Cu, pcbnew.B_Cu
    rep = dict(pairs={}, notes=[])
    # ---------------- SS pairs (outward) ----------------
    # (name, outer net, outer pad, inner net, inner pad, side, h_inner, a_inner (start of the 45 deg turn into the lane), bump zone, hmax)
    SS = [("SSTX1", "SSTX1_P", A(2), "SSTX1_N", A(3), +1, 3.25, 5.029, (-1.50, 0.70), 0.45),
          ("SSRX2", "SSRX2_N", A(10), "SSRX2_P", A(11), +1, 2.75, 4.85, (2.42, 4.60), 0.32),
          ("SSTX2", "SSTX2_N", B(3), "SSTX2_P", B(2), -1, 2.75, 4.85, (2.42, 4.60), 0.32),
          ("SSRX1", "SSRX1_P", B(11), "SSRX1_N", B(10), -1, 3.25, 5.029, (-1.50, 0.70), 0.45)]
    for (nm, no, po, ni, pi, sd, hi, ai, zone, hmax) in SS:
        ho = hi + PITCH; ao = ai + (PITCH * math.sqrt(2) - PITCH)
        lo, li = START[no], START[ni]
        assert abs(abs(lo[1]) - abs(li[1]) - PITCH) < 1e-3, (nm, lo, li)
        outer = [po, (po[0], sd * ho), (ao, sd * ho), (ao + (ho - abs(lo[1])), lo[1]), lo]
        inner0 = [pi, (pi[0], sd * hi)]; inner1 = [(ai, sd * hi), (ai + (hi - abs(li[1])), li[1]), li]
        Lo = plen(outer) + LANE_L[no]; Li = plen(inner0 + inner1) + LANE_L[ni]
        E = Lo - Li
        assert E > -1e-6, (nm, "outer shorter than inner", E)
        bp, n, h = solve_bumps(E, zone[0], zone[1], sd * hi, -sd, hmax)
        inner = inner0 + bp + inner1
        T.append((no, F, outer, W_HS)); T.append((ni, F, inner, W_HS))
        Lo2 = plen(outer) + LANE_L[no]; Li2 = plen(inner) + LANE_L[ni]
        rep["pairs"][nm] = dict(outer=no, inner=ni, fanout_outer=round(plen(outer), 3), fanout_inner=round(plen(inner), 3), lane_outer=round(LANE_L[no], 3),
                                lane_inner=round(LANE_L[ni], 3), skew_before=round(E, 3), bumps=n, bump_h=round(h, 3), total_outer=round(Lo2, 3),
                                total_inner=round(Li2, 3), skew=round(Lo2 - Li2, 4))
    # ---------------- channel nets ----------------
    us_ = us
    # 2026-10-04: shell pads grown 1.70 x 1.20 -> 1.80 x 1.30 (0.25 ring) -> the SBU1 / CC1 45-deg risers move right by DK_S / DK_C so SBU1 keeps >= 0.08 to the slot pad
    # and CC1 >= 0.08 to SBU1 and D_N (D pair unchanged: keeps room for both VBUS wedge vias)
    DK_S, DK_C = 0.045, 0.02
    # USB2: main path from the A-row contacts (A6 D_P, A7 D_N); B6 joins D_P (L1 stub), B7 joins D_N (L2 hop to a via on the A7 riser)
    dP = START["D_P"]; dN = START["D_N"]
    dp_main = [A(6), (-0.25, -0.10), (4.675, -0.10), (4.675 + (dP[1] + 0.10), dP[1]), dP]
    dn_a = [A(7), (0.25, 0.09)]; dn_b = [(4.596, 0.09), (4.596 + (dN[1] - 0.09), dN[1]), dN]
    LP = plen(dp_main) + LANE_L["D_P"]; LN = plen(dn_a + dn_b) + LANE_L["D_N"]
    E = LP - LN
    if E >= 0: bp, n, h = solve_bumps(E, 1.70, 2.55, 0.09, +1, 0.17); dn_main = dn_a + bp + dn_b
    else: n, h = 0, 0.0; dn_main = dn_a + dn_b; rep["notes"].append("D_N longer than D_P by %.3f (no bump)" % -E)
    T.append(("D_P", F, dp_main, W_HS)); T.append(("D_N", F, dn_main, W_HS))
    b6 = [B(6), (0.25, -0.10)]; T.append(("D_P", F, b6, W_HS))
    b7a = [B(7), (-0.25, -0.70)]; b7l2 = [(-0.25, -0.70), (0.25, 0.65)]
    T.append(("D_N", F, b7a, W_HS)); T.append(("D_N", Bc, b7l2, W_HS)); V += [("D_N", -0.25, -0.70, VIA_S), ("D_N", 0.25, 0.65, VIA_S)]
    # orientation lengths (contact -> header pad)
    i_dp = 2   # dp_main index of (2.70,-0.10); B6 joins at (0.25,-0.10) on the horizontal (-0.25,-0.10)->(2.70,-0.10)
    dP_A = plen(dp_main) + LANE_L["D_P"]; dN_A = plen(dn_main) + LANE_L["D_N"]
    dP_B = plen(b6) + plen([(0.25, -0.10)] + dp_main[2:]) + LANE_L["D_P"]
    dN_B = plen(b7a) + plen(b7l2) + plen([(0.25, 0.65)] + dn_main[1:]) + LANE_L["D_N"]
    rep["pairs"]["D (USB2)"] = dict(orientation_A=dict(P=round(dP_A, 3), N=round(dN_A, 3), skew=round(dP_A - dN_A, 4)),
                                    orientation_B=dict(P=round(dP_B, 3), N=round(dN_B, 3), skew=round(dP_B - dN_B, 4)), bumps=n, bump_h=round(h, 3),
                                    stub_A_side_in_B=round(plen([A(7), (0.25, 0.65)]), 3), stub_B_side_in_A=dict(D_P=round(plen(b6), 3), D_N=round(plen(b7a) + plen(b7l2), 3)))
    # SBU1 (L1)
    s1 = START["SBU1"]
    T.append(("SBU1", F, [A(8), (0.75, 0.82), (2.70, 0.82), (2.92, 0.60), (4.54 + DK_S, 0.60), (4.54 + DK_S + (s1[1] - 0.60), s1[1]), s1], W_SE))
    # CC1: A5 -> via -> L2 under the A row -> via -> L1 between SBU1 and D_N
    c1 = START["CC1"]
    T.append(("CC1", F, [A(5), (-0.75, 0.70)], W_SE)); V.append(("CC1", -0.75, 0.70, VIA_S))
    T.append(("CC1", Bc, [(-0.75, 0.70), (-0.75, 1.45), (1.25, 1.45), (1.25, 0.45)], W_SE)); V.append(("CC1", 1.25, 0.45, VIA_S))
    T.append(("CC1", F, [(1.25, 0.45), (2.70, 0.45), (2.75, 0.40), (4.623 + DK_C, 0.40), (4.623 + DK_C + (c1[1] - 0.40), c1[1]), c1], W_SE))
    # CC2 (L1) over the outboard peg
    c2 = START["CC2"]
    T.append(("CC2", F, [B(5), (0.75, -0.33), (5.43, -0.33), (5.50, -0.40), (6.136, -0.664), (c2[0], -1.30), c2], W_SE))
    # SBU2: B8 -> via -> L2 under the B row -> via -> L1 below CC2, hugging the peg (inner of CC2)
    s2 = START["SBU2"]
    T.append(("SBU2", F, [B(8), (-0.75, -0.70)], W_SE)); V.append(("SBU2", -0.75, -0.70, VIA_S))
    T.append(("SBU2", Bc, [(-0.75, -0.70), (-0.75, -1.45), (1.50, -1.45), (1.50, -0.70)], W_SE)); V.append(("SBU2", 1.50, -0.70, VIA_S))
    T.append(("SBU2", F, [(1.50, -0.70), (2.60, -0.70), (2.77, -0.53), (5.35, -0.53), (5.50, -0.68), (5.938, -0.862), (6.12, -1.30), (6.12, -1.45),
                          (6.12 + (abs(s2[1]) - 1.45), s2[1]), s2], W_SE))
    # ---------------- VBUS ----------------
    T.append(("VBUS", F, [A(4), B(9)], 0.27))
    for (u, v) in ((-1.9, 0.42), (-1.9, -0.42), (-2.5, 0.42), (-2.5, -0.42)): V.append(("VBUS", u, v, VIA_V))
    for v in (0.42, -0.42): T.append(("VBUS", F, [(-2.5, v), (-1.25, v)], 0.4))
    T.append(("VBUS", F, [A(9), (1.25, 2.55)], 0.25)); V.append(("VBUS", 1.25, 2.55, VIA_V))
    T.append(("VBUS", F, [B(4), (1.25, -2.55)], 0.25)); V.append(("VBUS", 1.25, -2.55, VIA_V))
    # ---------------- GND pads -> shell slots ----------------
    for p, q in ((A(1), (-3.55, 1.50)), (B(12), (-3.55, -1.50)), (A(12), (3.55, 1.50)), (B(1), (3.55, -1.50))): T.append(("GND", F, [p, q], 0.25))
    # ---------------- tail-start VBUS feed vias (searched in the free wedge between the rising top group and the CC2/SBU2 wrap) ----------
    from shapely.geometry import LineString, Point
    obst = [LineString(p).buffer(w / 2) for (nm, L, p, w) in T if nm != "VBUS" and L == F]
    obst += [Point(u, v).buffer(s[0] / 2) for (nm, u, v, s) in V if nm != "VBUS"]
    peg = Point(5.5, -1.3)
    wedge = []
    VW = VIA_S                       # 0.40/0.20: the wedge is narrow; vias kept >= 0.25 inside the stiffener edge (u <= 5.75)
    cands = [(round(4.95 + 0.025 * i, 3), round(-0.6 + 0.025 * j, 3)) for i in range(33) for j in range(49)]
    cands.sort(key=lambda c: (-c[0], abs(c[1] + 0.05)))
    for (u, v) in cands:
        pt = Point(u, v); r = VW[0] / 2
        if any(o.distance(pt) < r + 0.11 for o in obst): continue
        if peg.distance(pt) < 0.3 + VW[1] / 2 + 0.3: continue
        if any(math.hypot(u - a, v - c) < VW[1] + 0.28 for (a, c) in wedge): continue
        # stay off the outboard shell slot copper (oval 1.70 x 1.20 at (4.10, +-1.47)) by 0.15
        if any(LineString([(3.85, sv * 1.47), (4.35, sv * 1.47)]).buffer(0.6).distance(pt) < r + 0.15 for sv in (1, -1)): continue
        wedge.append((u, v))
        if len(wedge) == 4: break
    for (u, v) in wedge:
        V.append(("VBUS", u, v, VW)); T.append(("VBUS", F, [(u, v), (7.2, -0.3)], 0.3))
    rep["wedge_vias"] = wedge
    # ---------------- emit ----------------
    for (nm, L, pts, w) in T: BM.trk(b, nm, pts, w, L)
    for (nm, u, v, (d, dr)) in V:
        x = pcbnew.PCB_VIA(b); x.SetPosition(BM.P(u, v)); x.SetDrill(FromMM(dr)); x.SetWidth(FromMM(d)); x.SetNet(BM.net(b, nm)); x.SetLocked(True); b.Add(x)
    rep["fanout_lengths"] = {}
    for (nm, L, pts, w) in T: rep["fanout_lengths"][nm] = round(rep["fanout_lengths"].get(nm, 0) + plen(pts), 3)
    rep["counts"] = dict(tracks=sum(len(p) - 1 for (_, _, p, _) in T), vias=len(V), signal_hop_vias=sum(1 for x in V if x[0] not in ("VBUS",)))
    return rep
# L2 VBUS pour under the channel / gap / tail start (finish stage, priority 3; the filler clears the CC1 / SBU2 / B7 hops and the GND slots)
L2_VBUS_PORT = [(-2.9, -2.2), (0.95, -2.2), (0.95, -2.75), (1.55, -2.75), (1.55, -2.2), (3.15, -2.2), (3.15, -0.8), (5.0, -0.8), (5.2, -0.95), (6.3, -0.95),
                (6.3, 0.45), (5.6, 0.45), (4.9, 0.8), (3.15, 0.8), (3.15, 2.2), (1.55, 2.2), (1.55, 2.75), (0.95, 2.75), (0.95, 2.2), (-2.9, 2.2)]
L1_VBUS_BAR = [(-2.85, -0.88), (-1.05, -0.88), (-1.05, 0.88), (-2.85, 0.88)]
# FR4 port stiffener openings (drawn on User_1): shell legs + pegs
STIFF_HOLES = dict(slots=[(sx * 4.10, sy * 1.47, 2.0, 1.5) for sx in (1, -1) for sy in (1, -1)], pegs=[(-5.5, 1.3, 0.9), (5.5, -1.3, 0.9)])
