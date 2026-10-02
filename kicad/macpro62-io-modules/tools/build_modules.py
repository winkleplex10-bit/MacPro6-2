"""Build the 3 port-module FPC boards (D-IO16, 2026-10-02 ~12:35 ET): mod_usbc (x6), mod_usba (x4), mod_hdmi (x1).
FLAT (unfolded) outline, JLC 2-layer FPC 0.11 mm, ENIG. Placement-level A0 (not routed): port receptacle (F) + sleeve GND ring, DF40C-50DP header (F, same face:
the 180 deg C-fold turns it face-down onto JMn), WLCSP-4 ID EEPROM + 0201 cap on the header paddle. Stiffeners (FR4 1.0, B side) on User.1, optional EMI film on
User.2, cradle ledge bands on User.3, bend zone on User.4 (+ rule area: no vias / parts). Frame: x = u (toward the module's outboard edge), y = -v.
Geometry from ../modules.json (computed by ../../macpro62-io-board/tools/modules_geom.py from the plate stack)."""
import json, math, os
import pcbnew
from pcbnew import FromMM, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE); LIB = os.path.join(PRJ, "MP62_MOD.pretty")
MJ = json.load(open(os.path.join(PRJ, "modules.json"))); MODS = MJ["modules"]; TY = MJ["types"]
OX, OY = 100.0, 100.0
def P(u, v): return VECTOR2I(FromMM(OX + u), FromMM(OY - v))
PINS = [("VBUS",) * 2] * 6 + [("GND", "GND")] * 2 + [("HS0_P", "HS2_P"), ("HS0_N", "HS2_N"), ("GND", "GND"), ("HS1_P", "HS3_P"), ("HS1_N", "HS3_N"), ("GND", "GND"),
        ("USB2_DP", "SBU1"), ("USB2_DN", "SBU2"), ("GND", "GND"), ("CC1", "HPD"), ("CC2", "UTIL"), ("GND", "GND"), ("ID_SCL", "ID_SDA"), ("3V3_MOD", "PRSNT#"),
        ("LED#", "GND"), ("GND", "GND"), ("GND", "GND")]
assert len(PINS) == 25
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
def shape(b, kind, a, c, layer, w=0.05, m=None):
    s = pcbnew.PCB_SHAPE(b)
    if kind == "L": s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*c))
    else: s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*a), P(*m), P(*c))
    s.SetLayer(layer); s.SetWidth(FromMM(w)); b.Add(s)
def rectd(b, u0, v0, u1, v1, layer, w=0.1):
    for a, c in (((u0, v0), (u1, v0)), ((u1, v0), (u1, v1)), ((u1, v1), (u0, v1)), ((u0, v1), (u0, v0))): shape(b, "L", a, c, layer, w)
def text(b, t, u, v, layer=pcbnew.Cmts_User, size=0.7):
    tx = pcbnew.PCB_TEXT(b); tx.SetText(t); tx.SetPosition(P(u, v)); tx.SetLayer(layer); tx.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); tx.SetTextThickness(FromMM(size * 0.14)); b.Add(tx)
def place(b, ref, name, u, v, rot=0, value=None):
    f = pcbnew.FootprintLoad(LIB, name); f.SetFPID(pcbnew.LIB_ID("MP62_MOD", name)); f.SetReference(ref); f.SetValue(value or name)
    f.SetPosition(P(u, v)); f.SetOrientationDegrees(rot); b.Add(f); f.Reference().SetLayer(pcbnew.F_Fab); return f
KEEP = []
def build(name, kind, title):
    T = TY[kind]; ms = [m for m in MODS if m["kind"] == kind]; m = ms[0]; U = m["unfolded"]
    R = max(x["fold_r"] for x in ms); sx, sy, tw, pw = T["sx"], T["sy"], T["tw"], U["paddle_w"]
    f0 = U["fold_u"][0]; f1 = f0 + math.pi * R; p0 = f1 + 0.5; p1 = p0 + (U["hdr_stiff_u"][1] - U["hdr_stiff_u"][0]); uh = (p0 + p1) / 2
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    ds = b.GetDesignSettings(); ds.SetBoardThickness(FromMM(0.11)); ds.m_TrackMinWidth = FromMM(0.075); ds.m_MinClearance = FromMM(0.075); ds.m_HoleClearance = FromMM(0.2)
    ds.m_CopperEdgeClearance = FromMM(0.2)
    for L_, nm in ((pcbnew.User_1, "Stiffener_FR4_1.0_B"), (pcbnew.User_2, "EMI_Film_opt_F"), (pcbnew.User_3, "Cradle_Ledge"), (pcbnew.User_4, "Bend_Zone")): b.SetLayerName(L_, nm)
    V = [(-sx, -sy), (sx, -sy), (sx, -tw / 2), (p0, -tw / 2), (p0, -pw / 2), (p1, -pw / 2), (p1, pw / 2), (p0, pw / 2), (p0, tw / 2), (sx, tw / 2), (sx, sy), (-sx, sy)]
    for e in fillet_poly(V, 0.4):
        if e[0] == "L": shape(b, "L", e[1], e[2], pcbnew.Edge_Cuts)
        else: shape(b, "A", e[1], e[3], pcbnew.Edge_Cuts, m=e[2])
    rectd(b, -sx, -sy, sx, sy, pcbnew.User_1); rectd(b, p0, -pw / 2, p1, pw / 2, pcbnew.User_1)
    text(b, "FR4 1.0 stiffener (B, flush, PSA) under the port", 0, -sy - 1.0, pcbnew.User_1, 0.6); text(b, "FR4 1.0 stiffener (B) under the header paddle", uh, -pw / 2 - 1.0, pcbnew.User_1, 0.6)
    rectd(b, sx + 0.8, -tw / 2 + 0.3, p0 - 0.8, tw / 2 - 0.3, pcbnew.User_2); text(b, "optional silver EMI film (F), >= 0.8 from stiffeners, GND openings D1.0 at both ends", (sx + p0) / 2, tw / 2 + 0.8, pcbnew.User_2, 0.5)
    for sg in (-1, 1): rectd(b, -sx, sg * (tw / 2 + 0.3), sx, sg * sy, pcbnew.User_3)
    text(b, "cradle ledges (stiffener bottom bears here; no parts / THT tips in the bands)", 0, sy + 0.8, pcbnew.User_3, 0.5)
    rectd(b, f0, -tw / 2, f1, tw / 2, pcbnew.User_4); text(b, "C-fold 180 deg, R %.2f (bend zone: no vias, no parts, staggered traces)" % R, (f0 + f1) / 2, -tw / 2 - 0.8, pcbnew.User_4, 0.5)
    # rule area: bend zone (no vias, no footprints) on both copper layers
    z = pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetZoneName("BEND_ZONE"); z.SetDoNotAllowVias(True); z.SetDoNotAllowFootprints(True); z.SetDoNotAllowPads(True)
    z.SetDoNotAllowTracks(False); z.SetDoNotAllowCopperPour(False)
    ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); z.SetLayerSet(ls)
    ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
    for (u, v) in ((f0, -tw / 2), (f1, -tw / 2), (f1, tw / 2), (f0, tw / 2)): q = P(u, v); ps.Append(q.x, q.y)
    z.SetOutline(ps); b.Add(z); KEEP.extend([ps, z])
    place(b, "J1", T["fp"], 0, 0, 0, "%s - %s" % (T["mod"], T["conn"]))
    place(b, "G1", "MP62_MOD_Sleeve_GND_Ring_%s" % kind, 0, 0, 0, "sleeve GND ring (SUS304 0.2 sleeve, bonded to the shell)")
    place(b, "J2", "MP62_Hirose_DF40C-50DP-0.4V_PLACEHOLDER", uh, 0, 0, "DF40C-50DP-0.4V(51) C424645 -> main-board JMn DF40C-50DS (PMI-50 pinout)")
    place(b, "U1", "MP62_WLCSP-4_0.8x0.8_P0.4_EEPROM", uh + 3.5, 2.8, 0, "24C02 WLCSP-4 ID EEPROM @0x50 (MOD ID / type / rev / serial)")
    place(b, "C1", "C_0201_0603Metric", uh - 3.5, 2.8, 0, "100nF 0201 (3V3_MOD)")
    tb = b.GetTitleBlock(); tb.SetTitle(title); tb.SetDate("2026-10-02"); tb.SetRevision("A0"); tb.SetCompany("MP62 I/O - port modules (D-IO16)")
    tb.SetComment(0, "JLC FPC 2-layer 0.11 mm (PI 25 um, Cu 12/12 um + plating), ENIG, yellow coverlay. Stiffeners: FR4 1.0 (B) under the port and the header paddle")
    tb.SetComment(1, "L1 = signals (90 ohm USB / 100 ohm TMDS diff microstrip, VERIFY with the JLC FPC impedance calculator), L2 = solid GND + VBUS strip at the tail edge")
    tb.SetComment(2, "Fold: flat as drawn; C-fold 180 deg at Bend_Zone so J2 faces DOWN onto the main-board receptacle. Pinout = PMI-50 (plan 4.7.9)")
    notes = ["%s, unfolded. Port at (0,0); u -> outboard edge. Stiffener %.1f x %.1f; tail %.1f wide; flap %.1f; fold R %.2f; paddle %.1f x %.1f." % (T["mod"], 2 * sx, 2 * sy, tw, U["fold_u"][0] - sx, R, p1 - p0, pw),
             "Fits slots %s. Electrical length port pads -> header ~%.0f mm." % (", ".join(x["slot"] for x in ms), max(x["flex_len"] for x in ms)),
             "Plug loads: push -> connector body -> FPC -> FR4 stiffener -> cradle ledges; pull/side -> bonded SUS sleeve -> collar -> clamp plate -> screws. Not through solder or flex.",
             "PMI-50 (J2 odd/even): " + "; ".join("%d/%d %s/%s" % (2 * k + 1, 2 * k + 2, a, c) for k, (a, c) in enumerate(PINS) if k >= 6)[:400]]
    for i, s in enumerate(notes): text(b, s, (p1 - sx) / 2 - sx / 2, -sy - 3.0 - 1.2 * i, pcbnew.Cmts_User, 0.6)
    out = os.path.join(PRJ, name); os.makedirs(out, exist_ok=True)
    fn = os.path.join(out, name + ".kicad_pcb"); b.Save(fn)
    open(os.path.join(out, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "MP62_MOD")(type "KiCad")(uri "${KIPRJMOD}/../MP62_MOD.pretty")(options "")(descr "MP62 port-module footprints"))\n)\n')
    d = json.load(open(os.path.join(PRJ, "..", "macpro62-io-board", "macpro62-io-board.kicad_pro"))); d["meta"]["filename"] = name + ".kicad_pro"
    d.pop("sheets", None); d.pop("boards", None)
    for c in d["net_settings"]["classes"]:
        if c["name"] == "Default": c["clearance"] = 0.075; c["track_width"] = 0.075
    json.dump(d, open(fn.replace(".kicad_pcb", ".kicad_pro"), "w"), indent=2)
    print("saved", fn, "flat length %.1f" % (p1 + sx))
build("mod_usbc", "USBC", "MP62 port module MOD-C: 1 x USB-C 24P (10G + DP alt) on FPC - fit x6 (C1-C3 as drawn, C4-C6 rotated 180 deg)")
build("mod_usba", "USBA", "MP62 port module MOD-A: 1 x USB-A 3.2 Gen2 on FPC - fit x4 (A1/A2 as drawn, A3/A4 rotated 180 deg)")
build("mod_hdmi", "HDMI", "MP62 port module MOD-H: 1 x HDMI-A 2.0 on FPC - fit x1")
