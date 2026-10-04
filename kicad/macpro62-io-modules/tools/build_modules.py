"""Build + route the 3 port-module FPC boards (D-IO16 rev 2026-10-02 ~13:50 ET): mod_usbc (x6), mod_usba (x4), mod_hdmi (x1).
FLAT (unfolded) outline. Frame: x = u (toward the module's outboard edge / tail), y = -v. Geometry from ../modules.json (modules_geom.py).
Stackups (JLC 2-layer FPC, 12 um Cu, ENIG): MOD-C / MOD-H 50 um PI core 0.19 (solid L2 GND, 45 deg cross-hatch in the bend);
MOD-A 25 um core 0.11 (cross-hatched L2 along the whole tail; 90 ohm is not reachable over solid GND on 25 um). Pinout = PMI-50 v2 (../pmi50.py).
Stage "build": outline, footprints, nets, LOCKED controlled-impedance lanes (tail -> bend -> paddle -> header pads), VBUS strip, paddle GND vias,
ID-EEPROM wiring, rule areas; DSN export.  Stage "route": Freerouting (receptacle fan-out only; tail / paddle are keep-outs for it).
Stage "finish": SES import, zones (L2 GND solid + hatched, VBUS L1/L2, L1 GND on the stiffened areas), teardrops, fill, save. DRC with kicad-cli."""
import json, math, os, sys, subprocess
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE); LIB = os.path.join(PRJ, "MP62_MOD.pretty")
sys.path.insert(0, PRJ); import pmi50
MJ = json.load(open(os.path.join(PRJ, "modules.json"))); MODS = MJ["modules"]; TY = MJ["types"]
OX, OY = 100.0, 100.0
FR_JAR = "/workspace/tools/fr-2.1.0.jar"
def P(u, v): return VECTOR2I(FromMM(OX + u), FromMM(OY - v))
def UV(p): return (ToMM(p.x) - OX, OY - ToMM(p.y))
# ---------------- per-type electrical definition ----------------
# widths: (w, s) tail / bend; paddle pairs 0.075 / 0.075 (short, stiffened)
WS = {"USBC": dict(usb=((0.09, 0.10), (0.12, 0.10)), se=0.1), "HDMI": dict(tmds=((0.08, 0.15), (0.11, 0.15)), se=0.1),
      "USBA": dict(usb=((0.10, 0.10), (0.10, 0.10)), se=0.1)}
PAD_NETS = {
 "USBC": {"A1": "GND", "A2": "SSTX1_P", "A3": "SSTX1_N", "A4": "VBUS", "A5": "CC1", "A6": "D_P", "A7": "D_N", "A8": "SBU1", "A9": "VBUS", "A10": "SSRX2_N", "A11": "SSRX2_P", "A12": "GND",
          "B1": "GND", "B2": "SSTX2_P", "B3": "SSTX2_N", "B4": "VBUS", "B5": "CC2", "B6": "D_P", "B7": "D_N", "B8": "SBU2", "B9": "VBUS", "B10": "SSRX1_N", "B11": "SSRX1_P", "B12": "GND", "S": "GND"},
 "USBA": {"1": "VBUS", "2": "D_N", "3": "D_P", "4": "GND", "5": "SSRX_N", "6": "SSRX_P", "7": "GND", "8": "SSTX_N", "9": "SSTX_P", "S": "GND"},
 "HDMI": {"1": "D2_P", "2": "GND", "3": "D2_N", "4": "D1_P", "5": "GND", "6": "D1_N", "7": "D0_P", "8": "GND", "9": "D0_N", "10": "CK_P", "11": "GND", "12": "CK_N",
          "15": "DDC_SCL", "16": "DDC_SDA", "17": "GND", "18": "VBUS", "19": "HPD", "S": "GND"},
}
# tail lanes: (PMI lane roles (A[, B]), kind, tail centre v). Inner member = A (smaller k). VBUS strip: (v centre, L1 width, L2 width or 0)
LANES = {
 "USBC": [(("USB2_A", "USB2_B"), "usb", 0.93), (("LS_A1",), "se", 1.36), (("LS_A2",), "se", 1.66), (("HS3_A", "HS3_B"), "usb", 2.06), (("HS0_A", "HS0_B"), "usb", 2.6),
          (("LS_B1",), "se", -1.35), (("LS_B2",), "se", -1.65), (("HS2_A", "HS2_B"), "usb", -2.05), (("HS1_A", "HS1_B"), "usb", -2.6)],
 "USBA": [(("HS3_A", "HS3_B"), "usb", 1.3), (("HS0_A", "HS0_B"), "usb", 1.95), (("LS_B1", "LS_B2"), "usb", -1.3)],
 "HDMI": [(("LS_A2",), "se", 0.75), (("HS3_A", "HS3_B"), "tmds", 1.12), (("HS0_A", "HS0_B"), "tmds", 1.8),
          (("LS_B1",), "se", -0.75), (("LS_B2",), "se", -1.05), (("HS2_A", "HS2_B"), "tmds", -1.42), (("HS1_A", "HS1_B"), "tmds", -2.1)],
}
VB = {"USBC": (-0.3, 1.5, 1.3), "USBA": (0.0, 1.2, 1.0), "HDMI": (0.0, 0.3, 0.0)}
PORT_ROT = {"USBC": 0, "USBA": 0, "HDMI": 180}
VIA_D, VIA_P = 0.3, 0.55          # JLC FPC regular via
PAD_V = 1.3                       # DF40C-50DP pad-row centre |v| (placeholder: VERIFY Hirose land pattern)
LANE_V0, LANE_DP, LANE_DN = 1.7625, 0.15, 0.16   # paddle lane band: first trace centre, same-pair pitch, lane-to-lane pitch
KEEP = []
def shape(b, kind, a, c, layer, w=0.05, m=None):
    s = pcbnew.PCB_SHAPE(b)
    if kind == "L": s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*c))
    else: s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*a), P(*m), P(*c))
    s.SetLayer(layer); s.SetWidth(FromMM(w)); b.Add(s)
def rectd(b, u0, v0, u1, v1, layer, w=0.1):
    for a, c in (((u0, v0), (u1, v0)), ((u1, v0), (u1, v1)), ((u1, v1), (u0, v1)), ((u0, v1), (u0, v0))): shape(b, "L", a, c, layer, w)
def text(b, t, u, v, layer=pcbnew.Cmts_User, size=0.7):
    tx = pcbnew.PCB_TEXT(b); tx.SetText(t); tx.SetPosition(P(u, v)); tx.SetLayer(layer); tx.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); tx.SetTextThickness(FromMM(size * 0.14)); b.Add(tx)
def fillet_poly(verts, r):
    n = len(verts); pts = []
    for i in range(n):
        V = verts[i]; A = verts[i - 1]; B = verts[(i + 1) % n]
        u1 = [(A[0] - V[0]), (A[1] - V[1])]; l1 = math.hypot(*u1); u1 = [u1[0] / l1, u1[1] / l1]
        u2 = [(B[0] - V[0]), (B[1] - V[1])]; l2 = math.hypot(*u2); u2 = [u2[0] / l2, u2[1] / l2]
        th = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1]))) / 2
        t = r / math.tan(th); T1 = (V[0] + u1[0] * t, V[1] + u1[1] * t); T2 = (V[0] + u2[0] * t, V[1] + u2[1] * t)
        bis = [u1[0] + u2[0], u1[1] + u2[1]]; lb = math.hypot(*bis); bis = [bis[0] / lb, bis[1] / lb]
        C = (V[0] + bis[0] * r / math.sin(th), V[1] + bis[1] * r / math.sin(th)); M = (C[0] - bis[0] * r, C[1] - bis[1] * r)
        pts.append((T1, M, T2))
    out = []
    for i in range(n): out.append(("A",) + pts[i]); out.append(("L", pts[i][2], pts[(i + 1) % n][0]))
    return out
def place(b, ref, name, u, v, rot=0, value=None):
    f = pcbnew.FootprintLoad(LIB, name); f.SetFPID(pcbnew.LIB_ID("MP62_MOD", name)); f.SetReference(ref); f.SetValue(value or name)
    f.SetPosition(P(u, v)); f.SetOrientationDegrees(rot); b.Add(f); f.Reference().SetLayer(pcbnew.F_Fab); return f
NETS = {}
def net(b, name):
    if name not in NETS: n = pcbnew.NETINFO_ITEM(b, name); b.Add(n); NETS[name] = n
    return NETS[name]
def trk(b, nm, pts, w, layer=pcbnew.F_Cu, lock=True):
    for a, c in zip(pts[:-1], pts[1:]):
        if math.hypot(a[0] - c[0], a[1] - c[1]) < 1e-4: continue
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(FromMM(w)); t.SetLayer(layer); t.SetNet(net(b, nm)); t.SetLocked(lock); b.Add(t)
def via(b, nm, u, v, lock=True):
    x = pcbnew.PCB_VIA(b); x.SetPosition(P(u, v)); x.SetDrill(FromMM(VIA_D)); x.SetWidth(FromMM(VIA_P)); x.SetNet(net(b, nm)); x.SetLocked(lock); b.Add(x)
def zone(b, nm, poly, layer, prio=0, hatch=None, name=None, clr=0.1, minw=0.075, rule=None, therm=True):
    z = pcbnew.ZONE(b)
    if rule:
        z.SetIsRuleArea(True); z.SetDoNotAllowVias(rule.get("vias", False)); z.SetDoNotAllowTracks(rule.get("tracks", False)); z.SetDoNotAllowFootprints(rule.get("fp", False))
        z.SetDoNotAllowPads(rule.get("pads", False)); z.SetDoNotAllowCopperPour(rule.get("pour", False))
    else:
        z.SetNet(net(b, nm)); z.SetAssignedPriority(prio); z.SetLocalClearance(FromMM(clr)); z.SetMinThickness(FromMM(minw))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if therm else pcbnew.ZONE_CONNECTION_FULL); z.SetThermalReliefGap(FromMM(0.1)); z.SetThermalReliefSpokeWidth(FromMM(0.15))
        if hatch:
            z.SetFillMode(pcbnew.ZONE_FILL_MODE_HATCH_PATTERN); z.SetHatchThickness(FromMM(hatch[0])); z.SetHatchGap(FromMM(hatch[1] - hatch[0])); z.SetHatchOrientation(pcbnew.EDA_ANGLE(45, pcbnew.DEGREES_T))
            z.SetHatchSmoothingLevel(0); z.SetHatchHoleMinArea(0.0)
    if name: z.SetZoneName(name)
    ls = pcbnew.LSET()
    for L_ in (layer if isinstance(layer, (list, tuple)) else [layer]): ls.AddLayer(L_)
    z.SetLayerSet(ls)
    ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
    for (u, v) in poly: q = P(u, v); ps.Append(q.x, q.y)
    z.SetOutline(ps); b.Add(z); KEEP.extend([ps, z]); return z
def offset_poly(pts, offs):
    """miter offset of a polyline; offs[i] = signed offset (left normal) at vertex i"""
    out = []; n = len(pts)
    for i in range(n):
        if i == 0: d = (pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]); L = math.hypot(*d); nn = (-d[1] / L, d[0] / L); out.append((pts[0][0] + nn[0] * offs[0], pts[0][1] + nn[1] * offs[0])); continue
        if i == n - 1: d = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); L = math.hypot(*d); nn = (-d[1] / L, d[0] / L); out.append((pts[i][0] + nn[0] * offs[i], pts[i][1] + nn[1] * offs[i])); continue
        d1 = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); l1 = math.hypot(*d1); n1 = (-d1[1] / l1, d1[0] / l1)
        d2 = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]); l2 = math.hypot(*d2); n2 = (-d2[1] / l2, d2[0] / l2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]; lb = math.hypot(bx, by); bx, by = bx / lb, by / lb; c = bx * n1[0] + by * n1[1]
        out.append((pts[i][0] + bx * offs[i] / c, pts[i][1] + by * offs[i] / c))
    return out
def geo(kind):
    T = TY[kind]; ms = [m for m in MODS if m["kind"] == kind]; U = ms[0]["unfolded"]
    g = dict(T=T, ms=ms, U=U, sxo=T["sx_out"], sxi=T["sx_in"], sy=T["sy"], tw=T["tw"], t=T["fpc_t"], f0=U["fold_u"][0], f1=U["fold_u"][1],
             p0=U["hdr_stiff_u"][0], p1=U["hdr_stiff_u"][1], uh=U["hdr_centre_u"], ue=U["ee_centre_u"])
    g["uk"] = lambda k: g["uh"] - 4.8 + 0.4 * (k - 1)
    return g
def build(name, kind, title):
    NETS.clear(); KEEP.clear()
    g = geo(kind); T, U, sxo, sxi, sy, tw, t, f0, f1, p0, p1, uh, ue = (g[k] for k in ("T", "U", "sxo", "sxi", "sy", "tw", "t", "f0", "f1", "p0", "p1", "uh", "ue"))
    uk = g["uk"]; hw = tw / 2
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    ds = b.GetDesignSettings(); ds.SetBoardThickness(FromMM(t)); ds.m_TrackMinWidth = FromMM(0.075); ds.m_MinClearance = FromMM(0.075); ds.m_HoleClearance = FromMM(0.2)
    ds.m_CopperEdgeClearance = FromMM(0.3)
    for L_, nm in ((pcbnew.User_1, "Stiffener_FR4_B"), (pcbnew.User_2, "EMI_Film_opt_F"), (pcbnew.User_3, "Cradle_Ledge"), (pcbnew.User_4, "Bend_Zone")): b.SetLayerName(L_, nm)
    p1 = p1 + 0.02
    V = [(-sxi, -sy), (sxo, -sy), (sxo, -hw), (p1, -hw), (p1, hw), (sxo, hw), (sxo, sy), (-sxi, sy)]
    for e in fillet_poly(V, 0.4):
        if e[0] == "L": shape(b, "L", e[1], e[2], pcbnew.Edge_Cuts)
        else: shape(b, "A", e[1], e[3], pcbnew.Edge_Cuts, m=e[2])
    rectd(b, -sxi, -sy, sxo, sy, pcbnew.User_1); rectd(b, p0, -hw, p1, hw, pcbnew.User_1)
    text(b, "FR4 1.0 stiffener (B, PSA) under the port", 0, -sy - 1.0, pcbnew.User_1, 0.6); text(b, "FR4 0.6 stiffener (B) under the header paddle", uh, -hw - 1.0, pcbnew.User_1, 0.6)
    for sg in (-1, 1): rectd(b, -sxi, sg * (hw + 0.2), sxo, sg * sy, pcbnew.User_3)
    text(b, "cradle ledges (stiffener bottom bears here, 1.0 wide)", 0, sy + 0.8, pcbnew.User_3, 0.5)
    m0 = g["ms"][0]; fm = "loop" if any(x["fold_mode"] == "loop" for x in g["ms"]) else "C"
    rectd(b, f0, -hw, f1, hw, pcbnew.User_4)
    text(b, "%s-fold 180 deg, R %.2f-%.2f = %.0f-%.0f x t (bend zone: no vias / parts, hatched L2)" % (fm, min(x["fold_r"] for x in g["ms"]), max(x["fold_r"] for x in g["ms"]),
         min(x["fold_ratio"] for x in g["ms"]), max(x["fold_ratio"] for x in g["ms"])), (f0 + f1) / 2, -hw - 0.8, pcbnew.User_4, 0.5)
    zone(b, None, [(f0, -hw), (f1, -hw), (f1, hw), (f0, hw)], [pcbnew.F_Cu, pcbnew.B_Cu], name="BEND_ZONE", rule=dict(vias=True, fp=True, pads=True))
    # ---- footprints + pad nets ----
    J1 = place(b, "J1", T["fp"], 0, 0, PORT_ROT[kind], "%s - %s" % (T["mod"], T["conn"]))
    for p in J1.Pads():
        nm = PAD_NETS[kind].get(p.GetNumber())
        if nm: p.SetNet(net(b, nm))
    J2 = place(b, "J2", "MP62_Hirose_DF40C-50DP-0.4V_PLACEHOLDER", uh, 0, 0, "DF40C-50DP-0.4V(51) C424645 -> JMn DF40C-50DS (PMI-50 v2)")
    R = pmi50.ROLES[kind]
    def pmi_net(role):
        if role == "VBUS": return "VBUS"
        if role in ("GND", "PRSNT#"): return "GND"
        if role in ("ID_SCL", "ID_SDA", "3V3_MOD"): return role
        return R.get(role)
    for p in J2.Pads():
        n_ = int(p.GetNumber()); k = (n_ + 1) // 2; role = pmi50.PMI[k - 1][0 if n_ % 2 else 1]; nm = pmi_net(role)
        if nm: p.SetNet(net(b, nm))
    U1 = place(b, "U1", "DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm", ue, 0, 180, "BL24C02F-NTRC (C2828222) 24C02 ID EEPROM @0x50")
    for p in U1.Pads():
        nm = {"5": "ID_SDA", "6": "ID_SCL", "8": "3V3_MOD"}.get(p.GetNumber(), "GND"); p.SetNet(net(b, nm))
    C1 = place(b, "C1", "C_0201_0603Metric", ue - 0.6, -2.4, 0, "100nF 0201 X5R 10V (3V3_MOD)")
    for p in C1.Pads(): p.SetNet(net(b, "3V3_MOD" if p.GetNumber() == "1" else "GND"))
    # ---- locked lanes ----
    ws = WS[kind]; us = sxo - 0.35; b0, b1, b2, b3 = f0 - 0.35, f0 - 0.25, f1 + 0.25, f1 + 0.35; uj0 = f1 + 0.4
    rows = {+1: [], -1: []}
    for roles, knd, vt in LANES[kind]:
        sd = 1 if vt > 0 else -1
        for r_ in roles: rows[sd].append((pmi50.kpos(r_)[0], r_))
    vp = {}
    for sd, lst in rows.items():
        lst.sort(); v = LANE_V0; prev = None
        for k, r_ in lst:
            if prev is not None: v += LANE_DP if (prev[1][:-1] == r_[:-1] and prev[1][-1] == "A" and r_[-1] == "B" and k == prev[0] + 1) else LANE_DN
            vp[r_] = sd * v; prev = (k, r_)
    LOG = []
    for roles, knd, vt in LANES[kind]:
        sd = 1 if vt > 0 else -1
        if knd == "se": (wt, st), (wb, sb) = (ws["se"], 0), (ws["se"], 0)
        else: (wt, st), (wb, sb) = ws[knd]
        wp = 0.075
        if len(roles) == 2: vpc = (vp[roles[0]] + vp[roles[1]]) / 2; ot, ob, op = (wt + st) / 2, (wb + sb) / 2, (wp + 0.075) / 2
        else: vpc = vp[roles[0]]; ot = ob = op = 0.0
        dv = vpc - vt; uj1 = uj0 + abs(dv)
        assert uj1 < uk(1) - 0.05, (kind, roles, uj1, uk(1))
        cl = [(us, vt), (b0, vt), (b1, vt), (b2, vt), (b3, vt), (uj0, vt)] + ([(uj1, vpc), (uj1 + 0.2, vpc)] if abs(dv) > 1e-3 else [(uj0 + 0.2, vt)])
        oo = [ot, ot, ob, ob, op, op, op] + ([op] if abs(dv) > 1e-3 else [])
        for i, r_ in enumerate(roles):
            nm = R[r_]; sgn = 0 if len(roles) == 1 else (-sd if i == 0 else sd)
            pts = offset_poly(cl, [o * sgn for o in oo]) if sgn else list(cl)
            k = pmi50.kpos(r_)[0]; ukk = uk(k); vpm = vp[r_]
            pts = pts + [(ukk, vpm), (ukk, sd * PAD_V)]
            wseg = [wt, wt, wb, wp, wp] + [wp] * (len(pts) - 6)    # per segment
            for j in range(len(pts) - 1): trk(b, nm, [pts[j], pts[j + 1]], wseg[j] if j < len(wseg) else wp)
            LOG.append((nm, k, round(vt, 3), round(vpm, 3)))
    # ---- VBUS strip (L1 track), paddle VBUS feed, stitching ----
    vv, w1, w2 = VB[kind]
    trk(b, "VBUS", [(us + w1 / 2 - 0.35, vv), (uk(1) - 0.3, vv)], w1)
    trk(b, "VBUS", [(uk(1) - 0.6, 0.0), (uk(6) - 0.3, 0.0)], 1.0 if kind != "HDMI" else 0.6)
    if abs(vv) > 1e-6: trk(b, "VBUS", [(uk(1) - 0.6, vv), (uk(1) - 0.6, 0.0)], min(w1, 1.0))
    for k in range(1, 7):
        for sd in (1, -1): trk(b, "VBUS", [(uk(k), sd * PAD_V), (uk(k), 0.0)], 0.2)
    if w2 > 0:
        for (uu, dvv) in ((sxo - 0.45, -0.35), (sxo - 0.45, 0.35), (p0 + 0.7, -0.35), (p0 + 0.7, 0.35)): via(b, "VBUS", uu, vv + dvv)
    # ---- paddle GND vias between the rows ----
    for k in (7, 10, 13, 16, 19, 21):
        du = 0.2 if k == 7 else (-0.1 if k == 21 else 0.0)
        via(b, "GND", uk(k) + du, 0.0)
        for sd in (1, -1): trk(b, "GND", [(uk(k), sd * PAD_V), (uk(k), sd * 0.6), (uk(k) + du, 0.0)], 0.15)
    via(b, "GND", uk(24) + 0.2, -2.4); trk(b, "GND", [(uk(24), -PAD_V), (uk(24), -2.0), (uk(24) + 0.2, -2.4)], 0.15); trk(b, "GND", [(uk(25), -PAD_V), (uk(25), -2.0), (uk(24) + 0.2, -2.4)], 0.15)
    via(b, "GND", uk(25), 2.4); trk(b, "GND", [(uk(25), PAD_V), (uk(25), 2.4)], 0.15)
    # ---- ID EEPROM wiring (PMI v2: k22 ID_SCL / PRSNT#(=GND), k23 ID_SDA / 3V3_MOD) ----
    uc = ue - 0.94
    trk(b, "ID_SCL", [(uk(22), PAD_V), (uk(22), 0.25), (uc, 0.25)], 0.1); trk(b, "ID_SDA", [(uk(23), PAD_V), (uk(23), 0.75), (uc, 0.75)], 0.1)
    trk(b, "GND", [(uk(22), -PAD_V), (uk(22), -0.25), (uc, -0.25), (ue, -0.25)], 0.1); trk(b, "3V3_MOD", [(uk(23), -PAD_V), (uk(23), -0.75), (uc, -0.75)], 0.1)
    trk(b, "3V3_MOD", [(uc, -0.75), (ue - 0.92, -2.4)], 0.1)
    via(b, "GND", ue + 0.94, 1.45); via(b, "GND", ue + 0.94, -1.45); via(b, "GND", ue + 0.5, -2.45)
    trk(b, "GND", [(ue + 0.94, 0.75), (ue + 0.94, 1.45)], 0.15); trk(b, "GND", [(ue + 0.94, -0.75), (ue + 0.94, -1.45)], 0.15)
    for vv_ in (0.25, -0.25): trk(b, "GND", [(ue + 0.94, vv_), (ue, vv_)], 0.15)
    trk(b, "GND", [(ue - 0.28, -2.4), (ue + 0.5, -2.45)], 0.15)
    # ---- port-side GND anchors ----
    if kind == "USBC":
        for su in (-1, 1):
            for sv in (-1, 1): via(b, "GND", su * 4.3, sv * 1.4)
    # ---- temporary keep-outs for the autorouter (removed in "finish"): tail + paddle on both layers ----
    zone(b, None, [(sxo - 0.15, -hw - 0.5), (p1 + 0.5, -hw - 0.5), (p1 + 0.5, hw + 0.5), (sxo - 0.15, hw + 0.5)], [pcbnew.F_Cu, pcbnew.B_Cu], name="TMP_FR_KEEPOUT", rule=dict(vias=True, tracks=True))
    tb = b.GetTitleBlock(); tb.SetTitle(title); tb.SetDate("2026-10-02"); tb.SetRevision("A1"); tb.SetCompany("MP62 I/O - port modules (D-IO16)")
    st = "JLC FPC 2-layer %.2f mm (PI %s um core, Cu 12/12 um), ENIG, coverlay PI %s" % (t, "50" if t > 0.15 else "25", "25 + 25 adh." if t > 0.15 else "12.5 + 15 adh.")
    tb.SetComment(0, st + ". Stiffeners: FR4 1.0 (B) under the port, FR4 0.6 (B) under the paddle")
    tb.SetComment(1, "L1 signals: 90 ohm USB / 100 ohm TMDS diff microstrip (2D FD solve, tools/zsolve.py; TDR coupon), L2 GND (hatched 45 deg in the bend%s)" % (" and the whole tail" if kind == "USBA" else ""))
    tb.SetComment(2, "Fold: flat as drawn; 180 deg at Bend_Zone so J2 faces DOWN onto the main-board JMn. Pinout = PMI-50 v2 (pmi50.py, plan 4.7.10)")
    out = os.path.join(PRJ, name); os.makedirs(out, exist_ok=True)
    fn = os.path.join(out, name + ".kicad_pcb"); b.Save(fn)
    open(os.path.join(out, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "MP62_MOD")(type "KiCad")(uri "${KIPRJMOD}/../MP62_MOD.pretty")(options "")(descr "MP62 port-module footprints"))\n)\n')
    d = json.load(open(os.path.join(PRJ, "..", "macpro62-io-board", "macpro62-io-board.kicad_pro"))); d["meta"]["filename"] = name + ".kicad_pro"
    d.pop("sheets", None); d.pop("boards", None)
    base = [c for c in d["net_settings"]["classes"] if c["name"] == "Default"][0]
    def cls(nm, w, c, dw=0.09, dg=0.1):
        x = dict(base); x.update(name=nm, track_width=w, clearance=c, via_diameter=VIA_P, via_drill=VIA_D, diff_pair_width=dw, diff_pair_gap=dg, priority=0 if nm != "Default" else 2147483647); return x
    d["net_settings"]["classes"] = [cls("Default", 0.075, 0.075), cls("HS", 0.09, 0.075), cls("SE", 0.1, 0.075), cls("PWR", 0.35, 0.075), cls("GNDC", 0.2, 0.075)]
    d["board"]["design_settings"]["rules"].update(min_track_width=0.075, min_clearance=0.075, min_via_diameter=0.4, min_through_hole_diameter=0.2, min_copper_edge_clearance=0.3, min_text_height=0.5)
    open(fn.replace(".kicad_pcb", ".kicad_dru"), "w").write('(version 1)\n(rule "diff pair gap (90/100 ohm lanes + 0.075 paddle)"\n  (condition "A.inDiffPair(\'*\')")\n  (constraint diff_pair_gap (min 0.075) (opt 0.1) (max 0.16)))\n'
        '(rule "via to track (JLC FPC 0.1)"\n  (condition "A.Type == \'Via\' && B.Type == \'Track\'")\n  (constraint clearance (min 0.1)))\n')
    d["net_settings"]["netclass_patterns"] = [dict(netclass="HS", pattern=p_) for p_ in ("SS*", "D[0-2]_*", "CK_*", "D_P", "D_N")] + \
        [dict(netclass="SE", pattern=p_) for p_ in ("CC*", "SBU*", "DDC_*", "HPD", "ID_*", "3V3_MOD")] + [dict(netclass="PWR", pattern="VBUS"), dict(netclass="GNDC", pattern="GND")]
    d["net_settings"]["netclass_assignments"] = None
    json.dump(d, open(fn.replace(".kicad_pcb", ".kicad_pro"), "w"), indent=2)
    json.dump(dict(lanes=LOG, vp=vp), open(os.path.join(out, "lanes.json"), "w"), indent=1)
    print("built", fn, "flat length %.1f" % (p1 + sxi))
    return fn
def export_dsn(fn):
    b = pcbnew.LoadBoard(fn); dsn = fn.replace(".kicad_pcb", ".dsn"); ok = pcbnew.ExportSpecctraDSN(b, dsn); print("dsn", ok, dsn)
    patch_dsn(dsn); return dsn
def patch_dsn(dsn):
    """pcbnew's DSN export (headless) writes the 0.2/0.2 KiCad defaults instead of the project net classes -> force the flex rules
    (0.09 fan-out width, 0.075 clearance, 0.55/0.3 via + 0.40/0.20 via) so Freerouting can reach the 0.4-pitch DF40 pads."""
    import re
    s = open(dsn).read()
    s = re.sub(r"\(rule\s*\(width 200\)\s*\(clearance 200\)\s*\(clearance 50 \(type smd_smd\)\)\s*\)", "(rule (width 90) (clearance 75) (clearance 75 (type smd_smd)))", s)
    s = re.sub(r"\(rule\s*\(width 200\)\s*\(clearance 200\)\s*\)", "(rule (width 90) (clearance 75))", s)
    s = s.replace('(use_via "Via[0-1]_600:300_um")', '(use_via "Via[0-1]_550:300_um" "Via[0-1]_400:200_um")')
    # 2nd via size 0.40/0.20 for the dense USB-C port fan-out: JLC 2-layer FPC charges extra only below a 0.15 hole (0.10/0.30);
    # 0.20 hole / 0.40 pad (pad = hole + 0.2) is standard (jlcpcb.com/help/article/fpc-extra-charges, 2026-10-02)
    m0 = re.search(r'    \(padstack "Via\[0-1\]_550:300_um"[\s\S]*?\n    \)\n', s)
    if m0 and 'padstack "Via[0-1]_400:200_um"' not in s:
        s = s[:m0.end()] + m0.group(0).replace("550:300", "400:200").replace("F.Cu 550)", "F.Cu 400)").replace("B.Cu 550)", "B.Cu 400)") + s[m0.end():]
        s = re.sub(r'\(via "Via\[0-1\]_\d+:\d+_um" "Via\[0-1\]_550:300_um"\)', '(via "Via[0-1]_550:300_um" "Via[0-1]_400:200_um")', s)
    # Freerouting only does the PORT fan-out (J1 pins -> locked lane starts / VBUS strip). The tail, bend and paddle copper is locked and
    # complete, so: (1) every routed net keeps only its J1 pins (+ its locked wires, which Freerouting treats as part of the net);
    # (2) GND (finished by pours + locked vias in `finish`) is removed as a net and its locked copper becomes keepouts (still obstacles);
    # (3) nets with no J1 pin (ID bus, 3V3_MOD) are dropped from the router input. VBUS gets a 0.3 class.
    def body(blk):
        mm = re.match(r"\(net (\S+)\n\s*\(pins ([^)]*)\)\n\s*\)", blk); return mm.group(1), mm.group(2).split()
    nets = {}
    for mm in re.finditer(r"\(net (\S+)\n\s*\(pins ([^)]*)\)\n\s*\)", s): nets[mm.group(1)] = mm.group(2).split()
    drop = [n for n, pins in nets.items() if n == "GND" or not any(q.startswith("J1-") for q in pins)]
    def repl(mm):
        n = mm.group(1)
        if n in drop: return ""
        return "(net %s\n      (pins %s)\n    )" % (n, " ".join(q for q in mm.group(2).split() if q.startswith("J1-")))
    s = re.sub(r"\(net (\S+)\n\s*\(pins ([^)]*)\)\n\s*\)", repl, s)
    ko = []
    kx0 = min(float(v) for v in re.search(r'\(keepout "" \(polygon F\.Cu 0\s+([-\d.\s]+)\)', s).group(1).split()[0::2])   # TMP_FR_KEEPOUT start (tail)
    def inside(xs): return min(xs) >= kx0 - 0.01   # fixed copper wholly in the tail/paddle keep-out is irrelevant to the fan-out
    def wire_fix(mm):
        pts = [float(v) for v in mm.group(3).split()]
        if inside(pts[0::2]): return ""
        return wire_ko(mm)
    def via_fix(mm):
        if inside([float(mm.group(2))]): return ""
        return via_ko(mm)
    def wire_ko(mm):
        lay, w, pts, n = mm.group(1), float(mm.group(2)), [float(v) for v in mm.group(3).split()], mm.group(4)
        if n not in drop: return mm.group(0)
        from shapely.geometry import LineString
        poly = LineString(list(zip(pts[0::2], pts[1::2]))).buffer(w / 2, cap_style=2, join_style=2)
        ko.append('    (keepout "" (polygon %s 0 %s))' % (lay, " ".join("%.0f %.0f" % c for c in poly.exterior.coords)))
        return ""
    s = re.sub(r"\(wire \(path (\S+) (\S+)\s+([-\d.\s]+)\)\(net (\S+)\)\(type fix\)\)", wire_fix, s)
    def via_ko(mm):
        n = mm.group(4)
        if n not in drop: return mm.group(0)
        d = float(re.search(r"_(\d+):", mm.group(1)).group(1)); x, y = float(mm.group(2)), float(mm.group(3))
        for lay in ("F.Cu", "B.Cu"): ko.append('    (keepout "" (circle %s %.0f %.0f %.0f))' % (lay, d, x, y))
        return ""
    s = re.sub(r'\(via "([^"]+)"\s+([-\d.]+) ([-\d.]+) \(net (\S+)\)\(type fix\)\)', via_fix, s)
    k = s.index("    (via ", s.index("(structure"))   # insert keepouts into the structure block
    s = s[:k] + "\n".join(ko) + "\n" + s[k:]
    mm = re.search(r"\(class kicad_default ([^(]*)", s)
    names = [n for n in mm.group(1).split() if n not in drop and n != "VBUS"]
    s = s[:mm.start()] + ("(class PWR VBUS\n      (circuit\n        (use_via \"Via[0-1]_550:300_um\")\n      )\n      (rule (width 300) (clearance 100))\n    )\n    " if "VBUS" in nets else "") + \
        "(class kicad_default " + " ".join(names) + "\n      " + s[mm.end():]
    print("patch_dsn: routed nets", sorted(n for n in nets if n not in drop), "keepouts", len(ko))
    open(dsn, "w").write(s)
def route(fn, passes=500):
    dsn = fn.replace(".kicad_pcb", ".dsn"); ses = fn.replace(".kicad_pcb", ".ses")
    r = subprocess.run(["java", "-jar", FR_JAR, "-de", dsn, "-do", ses, "--router.max_passes=%d" % passes, "-mt", "1", "--gui.enabled=false"], capture_output=True, text=True, timeout=2400)
    open(fn.replace(".kicad_pcb", "_freerouting.log"), "w").write(r.stdout + r.stderr); print("route", r.returncode, os.path.exists(ses))
def teardrops(b, outline_poly):
    """manual teardrops (KiCad 9 python has no teardrop generator): filled copper polygons on the pad/via side of each track end, kept only if
    >= 0.08 from all other-net copper and >= 0.3 from the board edge."""
    from shapely.geometry import LineString, Point, Polygon, box
    from shapely import affinity
    from shapely.ops import unary_union
    def pad_geom(p):
        c = UV(p.GetPosition()); sx, sy = ToMM(p.GetSize().x), ToMM(p.GetSize().y)
        ang = p.GetOrientation().AsDegrees()
        if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE: return Point(c).buffer(sx / 2, 16)
        g = box(c[0] - sx / 2, c[1] - sy / 2, c[0] + sx / 2, c[1] + sy / 2)
        return affinity.rotate(g, ang, origin=c) if abs(ang) > 0.01 else g
    cu = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}   # (netcode, geom, kind, obj)
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            g = Point(UV(t.GetPosition())).buffer(ToMM(t.GetWidth(pcbnew.F_Cu)) / 2, 16)
            for L in cu: cu[L].append((t.GetNetCode(), g, "via", t))
        else:
            a_, c_ = UV(t.GetStart()), UV(t.GetEnd())
            g = LineString([a_, c_]).buffer(ToMM(t.GetWidth()) / 2, 8) if a_ != c_ else Point(a_).buffer(ToMM(t.GetWidth()) / 2)
            cu[t.GetLayer()].append((t.GetNetCode(), g, "trk", t))
    for f in b.GetFootprints():
        for p in f.Pads():
            g = pad_geom(p)
            for L in cu:
                if p.IsOnLayer(L): cu[L].append((p.GetNetCode(), g, "pad", p))
    edge = Polygon(outline_poly).buffer(-0.3)
    added = 0
    for L, items in cu.items():
        anchors = [(nc, g, k, o) for (nc, g, k, o) in items if k in ("pad", "via") and nc > 0]
        for (nc, g, k, t) in [x for x in items if x[2] == "trk"]:
            w = ToMM(t.GetWidth())
            for end, other in ((UV(t.GetStart()), UV(t.GetEnd())), (UV(t.GetEnd()), UV(t.GetStart()))):
                for (anc, ag, ak, ao) in anchors:
                    if anc != nc or not ag.contains(Point(end)): continue
                    c = UV(ao.GetPosition()); d = (other[0] - end[0], other[1] - end[1]); Ls = math.hypot(*d)
                    if Ls < 0.15: continue
                    d = (d[0] / Ls, d[1] / Ls); pp = (-d[1], d[0])
                    # half-width of the anchor across the track and its extent along the track
                    ext_al = max((ag.intersection(LineString([c, (c[0] + d[0] * 5, c[1] + d[1] * 5)])).length), 0.05)
                    perp = ag.intersection(LineString([(c[0] - pp[0] * 5, c[1] - pp[1] * 5), (c[0] + pp[0] * 5, c[1] + pp[1] * 5)])).length
                    a_w = 0.85 * perp / 2
                    if a_w < 0.65 * w: continue
                    proj = (end[0] - c[0]) * d[0] + (end[1] - c[1]) * d[1]
                    Lt = min(0.5 * perp, 0.5 * (Ls + proj - ext_al), 0.6)
                    if Lt < 0.08: continue
                    T_ = (c[0] + d[0] * (ext_al + Lt), c[1] + d[1] * (ext_al + Lt)); a0 = ext_al * 0.3
                    C0 = (c[0] + d[0] * a0, c[1] + d[1] * a0)
                    poly = [(C0[0] + pp[0] * a_w, C0[1] + pp[1] * a_w), (T_[0] + pp[0] * w / 2, T_[1] + pp[1] * w / 2), (T_[0] - pp[0] * w / 2, T_[1] - pp[1] * w / 2), (C0[0] - pp[0] * a_w, C0[1] - pp[1] * a_w)]
                    tg = Polygon(poly)
                    if not tg.is_valid or not edge.contains(tg): continue
                    if any(onc != nc and og.distance(tg) < 0.08 for (onc, og, ok_, oo) in items): continue
                    s_ = pcbnew.PCB_SHAPE(b); s_.SetShape(pcbnew.SHAPE_T_POLY); s_.SetFilled(True); s_.SetLayer(L); s_.SetWidth(0)
                    ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
                    for q in poly: Q = P(*q); ps.Append(Q.x, Q.y)
                    s_.SetPolyShape(ps); s_.SetNetCode(nc); b.Add(s_); KEEP.append(ps); added += 1
                    items.append((nc, tg, "td", None))
                    break
    return added
def finish(nm, kind):
    NETS.clear(); KEEP.clear()
    fn = os.path.join(PRJ, nm, nm + ".kicad_pcb"); ses = fn.replace(".kicad_pcb", ".ses")
    b = pcbnew.LoadBoard(fn)
    n0 = len([t for t in b.GetTracks()])
    ok = pcbnew.ImportSpecctraSES(b, ses)
    # SWIG wrappers go stale after the SES import / zone removal -> save, drop the TMP_FR_KEEPOUT zone in the file text, reload
    tmp_ = fn.replace(".kicad_pcb", "_ses_tmp.kicad_pcb"); pcbnew.SaveBoard(tmp_, b); KEEP.append(b)
    txt_ = open(tmp_).read(); out_ = []; i_ = 0
    while True:
        j_ = txt_.find("\n\t(zone", i_)
        if j_ < 0: out_.append(txt_[i_:]); break
        depth = 0; k_ = j_ + 1
        while True:
            ch = txt_[k_]
            if ch == "(": depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0: break
            k_ += 1
        blk = txt_[j_:k_ + 1]; out_.append(txt_[i_:j_])
        if '(name "TMP_FR_KEEPOUT")' not in blk: out_.append(blk)
        i_ = k_ + 1
    open(tmp_, "w").write("".join(out_)); b = pcbnew.LoadBoard(tmp_); os.remove(tmp_)
    def nt(name): return b.FindNet(name)
    g = geo(kind); sxo, sxi, sy, hw, f0, f1, p0, p1, uk = g["sxo"], g["sxi"], g["sy"], g["tw"] / 2, g["f0"], g["f1"], g["p0"], g["p1"] + 0.02, g["uk"]
    outline = [(-sxi, -sy), (sxo, -sy), (sxo, -hw), (p1, -hw), (p1, hw), (sxo, hw), (sxo, sy), (-sxi, sy)]
    td = teardrops(b, outline)
    def Z(netname, poly, layer, prio, hatch=None, name=None, therm=True):
        z = pcbnew.ZONE(b); z.SetNet(nt(netname)); z.SetAssignedPriority(prio); z.SetLocalClearance(FromMM(0.1)); z.SetMinThickness(FromMM(0.075))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if therm else pcbnew.ZONE_CONNECTION_FULL); z.SetThermalReliefGap(FromMM(0.1)); z.SetThermalReliefSpokeWidth(FromMM(0.15))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        if hatch:
            z.SetFillMode(pcbnew.ZONE_FILL_MODE_HATCH_PATTERN); z.SetHatchThickness(FromMM(hatch[0])); z.SetHatchGap(FromMM(hatch[1] - hatch[0])); z.SetHatchOrientation(pcbnew.EDA_ANGLE(45, pcbnew.DEGREES_T))
            z.SetHatchSmoothingLevel(0); z.SetHatchHoleMinArea(0.0)
        if name: z.SetZoneName(name)
        z.SetLayer(layer); ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
        for (u, v) in poly: q = P(u, v); ps.Append(q.x, q.y)
        z.SetOutline(ps); b.Add(z); KEEP.extend([ps, z]); return z
    Z("GND", outline, pcbnew.B_Cu, 0, name="L2_GND")
    hatch = (0.10, 0.30) if kind == "USBA" else (0.10, 0.25)
    hz0, hz1 = (sxo, p0) if kind == "USBA" else (f0 - 0.25, f1 + 0.25)
    Z("GND", [(hz0, -hw), (hz1, -hw), (hz1, hw), (hz0, hw)], pcbnew.B_Cu, 1, hatch=hatch, name="L2_GND_HATCH_BEND")
    vv, w1, w2 = VB[kind]
    if w2 > 0: Z("VBUS", [(sxo - 0.8, vv - w2 / 2), (uk(6) - 0.3, vv - w2 / 2), (uk(6) - 0.3, vv + w2 / 2), (sxo - 0.8, vv + w2 / 2)], pcbnew.B_Cu, 3, name="L2_VBUS", therm=False)
    Z("VBUS", [(uk(1) - 0.6, -1.0), (uk(6) + 0.2, -1.0), (uk(6) + 0.2, 1.0), (uk(1) - 0.6, 1.0)], pcbnew.F_Cu, 3, name="L1_VBUS_PADDLE", therm=False)
    Z("GND", [(-sxi, -sy), (sxo - 0.25, -sy), (sxo - 0.25, sy), (-sxi, sy)], pcbnew.F_Cu, 0, name="L1_GND_PORT", therm=False)
    Z("GND", [(p0, -hw), (p1, -hw), (p1, hw), (p0, hw)], pcbnew.F_Cu, 0, name="L1_GND_PADDLE")
    for z_ in b.Zones():
        if not z_.GetIsRuleArea(): z_.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    # coverlay flex: footprint silk that runs off the narrow tail / over the THT rings -> F.Fab (no legend ink on the module)
    holes_ = [(ToMM(t.GetPosition().x), ToMM(t.GetPosition().y), ToMM(t.GetDrill()) / 2) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"] + \
             [(ToMM(p.GetPosition().x), ToMM(p.GetPosition().y), ToMM(p.GetDrillSizeX()) / 2) for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSizeX() > 0]
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    # stitch every L1 GND island to L2 with one 0.55/0.3 via at a point >= 0.3 inside the island (port and paddle zones)
    from shapely.geometry import Polygon as _Poly
    n_st = 0
    for z_ in list(b.Zones()):
        if z_.GetIsRuleArea() or z_.GetNetname() != "GND" or not z_.IsOnLayer(pcbnew.F_Cu): continue
        fp_ = z_.GetFilledPolysList(pcbnew.F_Cu)
        for i_ in range(fp_.OutlineCount()):
            o_ = fp_.Outline(i_); pts_ = [(ToMM(o_.CPoint(k).x), ToMM(o_.CPoint(k).y)) for k in range(o_.PointCount())]
            if len(pts_) < 3: continue
            pg = _Poly(pts_).buffer(-0.3)
            if pg.is_empty or pg.area < 0.05: continue
            from shapely.geometry import Point as _Pt
            cands = [pg.representative_point()] + [_Pt(x0_ + (x1_ - x0_) * i / 8, y0_ + (y1_ - y0_) * j / 8) for (x0_, y0_, x1_, y1_) in [pg.bounds] for i in range(9) for j in range(9)]
            cands = [c for c in cands if pg.contains(c) and all(math.hypot(c.x - hx, c.y - hy) - hr - 0.15 >= 0.3 for hx, hy, hr in holes_)]
            if not cands: continue
            c_ = cands[0]; v_ = pcbnew.PCB_VIA(b); v_.SetPosition(pcbnew.VECTOR2I(FromMM(c_.x), FromMM(c_.y)))
            v_.SetWidth(FromMM(0.55)); v_.SetDrill(FromMM(0.3)); v_.SetNet(net(b, "GND")); b.Add(v_); n_st += 1
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); print("GND island stitch vias", n_st)
    pj_ = fn.replace(".kicad_pcb", ".kicad_pro")
    if os.path.exists(pj_):
        d_ = json.load(open(pj_)); d_.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rule_severities", {})["lib_footprint_mismatch"] = "ignore"
        json.dump(d_, open(pj_, "w"), indent=2)
    b.Save(fn)
    # length / skew report (track length per net, port pad -> header pad)
    L = {}
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA": continue
        L[t.GetNetname()] = L.get(t.GetNetname(), 0.0) + ToMM(t.GetLength())
    vias = {}
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA": vias[t.GetNetname()] = vias.get(t.GetNetname(), 0) + 1
    pairs = sorted({n[:-2] for n in L if n.endswith("_P") and n[:-2] + "_N" in L})
    rep = dict(module=nm, ses_import=bool(ok), tracks_before=n0, tracks_after=len(b.GetTracks()), teardrops=td,
               pairs={p_: dict(P=round(L[p_ + "_P"], 3), N=round(L[p_ + "_N"], 3), skew=round(L[p_ + "_P"] - L[p_ + "_N"], 3), vias_P=vias.get(p_ + "_P", 0), vias_N=vias.get(p_ + "_N", 0)) for p_ in pairs},
               singles={n: round(l, 2) for n, l in L.items() if not (n.endswith("_P") or n.endswith("_N"))})
    json.dump(rep, open(os.path.join(PRJ, nm, "route_report.json"), "w"), indent=1)
    print(nm, "ses", ok, "teardrops", td, json.dumps(rep["pairs"]))
if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "build"
    JOBS = [("mod_usbc", "USBC", "MP62 port module MOD-C: 1 x USB-C 24P (10G + DP alt) on FPC - fit x6 (C1-C3 as drawn, C4-C6 rotated 180 deg)"),
            ("mod_usba", "USBA", "MP62 port module MOD-A: 1 x USB-A 3.2 Gen2 (Hong Cheng HC-USB3.0-L137-WJ) on FPC - fit x4"),
            ("mod_hdmi", "HDMI", "MP62 port module MOD-H: 1 x HDMI-A 2.0 on FPC - fit x1")]
    only = sys.argv[2:] or [j[0] for j in JOBS]
    for nm, kd, ti in JOBS:
        if nm not in only: continue
        fn = os.path.join(PRJ, nm, nm + ".kicad_pcb")
        if stage == "build": build(nm, kd, ti); export_dsn(fn)
        elif stage == "route": route(fn)
        elif stage == "finish": finish(nm, kd)
