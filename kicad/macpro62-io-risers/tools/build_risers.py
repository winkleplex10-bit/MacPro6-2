"""Build the 3 column-riser PCBs (D-IO14, 2026-10-02 ~10:45 ET): riser_c (x2: RC_H, RC_O rotated 180 deg), riser_a (x2), riser_hdmi (x1).
JLC standard 4-layer 1.6 mm (JLC04161H-7628), ENIG (pogo targets). Placement-level A0: outline, port connectors (F), DF40C link (B), pogo targets (B), M2 holes.
Geometry from risers.json (computed by ../macpro62-io-board/tools/risers_geom.py from the plate stack)."""
import json, math, os
import pcbnew
from pcbnew import FromMM, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE); LIB = os.path.join(PRJ, "MP62_RISER.pretty")
RJ = {r["id"]: r for r in json.load(open(os.path.join(PRJ, "risers.json")))["risers"]}
H13 = (53.38, 58.38)
CONN = {"C": "MP62_USB_C_24P_Vertical_PLACEHOLDER", "A": "MP62_USB_A3_9P_Vertical_PLACEHOLDER", "HDMI": "MP62_HDMI_A_Vertical_PLACEHOLDER"}
OX, OY = 100.0, 100.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
def seg(b, a, c, w=0.05, layer=pcbnew.Edge_Cuts):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*c)); s.SetLayer(layer); s.SetWidth(FromMM(w)); b.Add(s)
def arc(b, a, m, c):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*a), P(*m), P(*c)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.05)); b.Add(s)
def text(b, t, x, y, layer=pcbnew.F_SilkS, size=0.8):
    tx = pcbnew.PCB_TEXT(b); tx.SetText(t); tx.SetPosition(P(x, y)); tx.SetLayer(layer); tx.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); tx.SetTextThickness(FromMM(0.12))
    if layer == pcbnew.B_SilkS: tx.SetMirrored(True)
    b.Add(tx)
def place(b, ref, name, x, y, rot=0, side="F", value=None):
    f = pcbnew.FootprintLoad(LIB, name); f.SetFPID(pcbnew.LIB_ID("MP62_RISER", name)); f.SetReference(ref); f.SetValue(value or name)
    f.SetPosition(P(x, y)); f.SetOrientationDegrees(rot); b.Add(f)
    if side == "B": f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.Reference().SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab)
    return f
def build(name, r, notches=(), title=""):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(4)
    ds = b.GetDesignSettings(); ds.m_TrackMinWidth = FromMM(0.09); ds.m_MinClearance = FromMM(0.09); ds.m_HoleClearance = FromMM(0.2)
    xl, hw = r["pcb_x"]; hl = r["riser_l"] / 2
    # outline (rectangle, optional semicircular notches r=3.0 on the +x' (inboard) edge for the I/O-frame centre standoff H13)
    pts = [(xl, -hl), (hw, -hl)]
    for dy in sorted(notches):
        pts.append((hw, dy - 3.0)); pts.append(("arc", (hw - 3.0, dy), (hw, dy + 3.0)))
    pts += [(hw, hl), (xl, hl), (xl, -hl)]
    cur = pts[0]
    for p in pts[1:]:
        if p[0] == "arc": arc(b, cur, p[1], p[2]); cur = p[2]
        else: seg(b, cur, p); cur = p
    tb = b.GetTitleBlock(); tb.SetTitle(title); tb.SetDate("2026-10-02"); tb.SetRevision("A0"); tb.SetCompany("MP62 I/O")
    yc = (r["y_range"][0] + r["y_range"][1]) / 2
    for k, (xc, dy) in enumerate(r["connector_centres_pcb"]):
        place(b, "J%d" % (1 + k), CONN[r["type"]], xc, dy, 0, "F", "%s %s (mouth %.2f above main board top)" % (r["ports"][k], r["conn"], r["mouth_heights"][k]))
    place(b, "J10", "MP62_Hirose_DF40C-%dDS-0.4V_PLACEHOLDER" % r["btb_pins"], r["btb_at_pcb"][0], r["btb_at_pcb"][1], 90, "B", "%s %s riser side (flex jumper to main JR)" % (r["btb"], r["btb_lcsc"]))
    for k, (xp, yp, net) in enumerate(r["pogo_pcb"]):
        place(b, "TP%d" % (1 + k), "MP62_Pogo_Target_D3.0", xp, yp, 0, "B", "pogo target %s" % net)
    for k, (xp, yp) in enumerate(r["screws_pcb"]):
        place(b, "H%d" % (1 + k), "MP62_Riser_Screw_M2", xp, yp, 0, "F", "M2 to the printed wedge cradle (heat-set insert)")
    text(b, "%s A0 %.1f deg" % (name, abs(r["tilt_deg"])), (xl + hw) / 2, -hl - 1.5, pcbnew.F_Fab, 0.8)
    out = os.path.join(PRJ, name); os.makedirs(out, exist_ok=True)
    fn = os.path.join(out, name + ".kicad_pcb"); b.Save(fn)
    open(os.path.join(out, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "MP62_RISER")(type "KiCad")(uri "${KIPRJMOD}/../MP62_RISER.pretty")(options "")(descr "MP62 riser footprints"))\n)\n')
    d = json.load(open(os.path.join(PRJ, "..", "macpro62-io-board", "macpro62-io-board.kicad_pro"))); d["meta"]["filename"] = name + ".kicad_pro"
    d.pop("sheets", None); d.pop("boards", None)
    for c in d["net_settings"]["classes"]:
        if c["name"] == "Default": c["clearance"] = 0.1; c["track_width"] = 0.1
    json.dump(d, open(fn.replace(".kicad_pcb", ".kicad_pro"), "w"), indent=2)
    print("saved", fn)
rc = RJ["RC_H"]; ycH = (rc["y_range"][0] + rc["y_range"][1]) / 2
build("riser_c", rc, notches=(round(H13[1] - ycH, 2), round(-(H13[1] - ycH), 2)), title="MP62 USB-C column riser (3 x USB-C 10.5) - fit x2: RC_H as drawn, RC_O rotated 180 deg")
build("riser_a", RJ["RA_H"], title="MP62 USB-A column riser (2 x USB-A 11.5) - fit x2: RA_H as drawn, RA_O rotated 180 deg")
build("riser_hdmi", RJ["RH"], title="MP62 HDMI riser (1 x HDMI-A 10.5)")
