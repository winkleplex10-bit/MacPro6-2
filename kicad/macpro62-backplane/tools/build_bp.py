#!/usr/bin/env python3
"""MP62 backplane rev A1 (BP-G4 cost-down) PCB builder, stage 'place': 4-layer JLC04161H-7628 board, outline + keep-outs (as fp6),
fixed interface connectors at their fp6/ICD positions, the rest placed by cluster packing, nets from bp_model.py.
Disc coordinates: origin = disc centre, +y = core side. Output: backplane.kicad_pcb (unrouted, stage 1)."""
import json, math, os, sys
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import bp_model as M
OUT = os.path.join(PRJ, "backplane.kicad_pcb")
CX, CY = 150.0, 100.0
SYSFP = "/usr/share/kicad/footprints"
LIBS = {"MP62_Placeholders": os.path.join(PRJ, "MP62_Placeholders.pretty"), "MP62_BP": os.path.join(PRJ, "MP62_BP.pretty")}
def P(x, y): return VECTOR2I(FromMM(CX + x), FromMM(CY - y))
def D(v): return (ToMM(v.x) - CX, CY - ToMM(v.y))
dxf = json.load(open(os.path.join(HERE, "base_board_dxf.json")))
outline = [e for e in dxf if e.get("layer") == "OUTLINE"][0]
R0 = outline["r"]; R_COMP = R0 - 3.0; HOLE_KO = 6.0
S_HOLES = [("S1", -52.64, 13.81), ("S2", -26.57, -46.65), ("S3", 26.49, -46.64), ("S4", -18.12, 50.70), ("S5", 18.49, 50.72), ("S6", 52.80, 13.88)]
FP6 = json.load(open(os.path.join(HERE, "fp6_positions.json")))
CU4 = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
KEEP = []

def new_board():
    b = pcbnew.NewBoard(OUT)
    b.SetCopperLayerCount(4)
    ds = b.GetDesignSettings()
    ds.SetBoardThickness(FromMM(1.6))
    ds.m_TrackMinWidth = FromMM(0.09); ds.m_MinClearance = FromMM(0.1); ds.m_ViasMinSize = FromMM(0.45); ds.m_MinThroughDrill = FromMM(0.25)
    ds.m_CopperEdgeClearance = FromMM(0.4); ds.m_HoleClearance = FromMM(0.2); ds.m_HoleToHoleMin = FromMM(0.2); ds.m_SilkClearance = FromMM(0.0)
    for i, nm in ((pcbnew.F_Cu, "L1_SIG_RX"), (pcbnew.In1_Cu, "L2_GND"), (pcbnew.In2_Cu, "L3_SIG_TX_PWR"), (pcbnew.B_Cu, "L4_GND_BRK")):
        b.SetLayerName(i, nm)
    tb = b.GetTitleBlock()
    tb.SetTitle("MacPro6,2 Backplane (BP) rev A1 'BP-G4' - routed, 4 layers")
    tb.SetRevision("A1"); tb.SetDate("2026-10-04"); tb.SetCompany("MacPro6,2 / Aidan Winkler")
    tb.SetComment(0, "Stackup JLC04161H-7628 4L 1.6 mm: L1 RX pairs + parts (85R: 0.26/0.125), L2 GND, L3 TX pairs + power (85R: 0.21/0.127, ref L4), L4 GND + short RX breakouts")
    tb.SetComment(1, "Gen4 only (redrivers removed, loss budget in README). FS lanes per ICD rev 3.1 proposal (reversed on CPU-LINK)")
    tb.SetComment(2, "MCU RP2350B, INA226, 2x TPS563201 (3V3_SB 3 A merged rail, 5V_SBY), HW PS_ON gate + thermal latch")
    tb.SetComment(3, "Interface connector positions = fp6 / ICD rev 3 (J1, J2, J3, J4, J6, J9, J10, H1, H2)")
    return b

def outline_and_keepouts(b):
    c = pcbnew.PCB_SHAPE(b); c.SetShape(pcbnew.SHAPE_T_CIRCLE); c.SetCenter(P(outline["cx"], outline["cy"])); c.SetEnd(P(outline["cx"] + R0, outline["cy"]))
    c.SetLayer(pcbnew.Edge_Cuts); c.SetWidth(FromMM(0.1)); b.Add(c)
    def zone_rule(name, pts, layers, fp=True, vias=True, tracks=False, pads=True, pour=False, holes=None):
        z = pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetZoneName(name)
        z.SetDoNotAllowFootprints(fp); z.SetDoNotAllowVias(vias); z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowPads(pads); z.SetDoNotAllowCopperPour(pour)
        ls = pcbnew.LSET(); [ls.AddLayer(l) for l in layers]; z.SetLayerSet(ls)
        o = z.Outline(); o.NewOutline()
        for (x, y) in pts: v = P(x, y); o.Append(v.x, v.y)
        if holes:
            o.NewHole()
            for (x, y) in holes: v = P(x, y); o.Append(v.x, v.y, 0, 0)
        b.Add(z); return z
    N = 96
    zone_rule("EDGE_RING_KEEPOUT", [((R0 + 1) * math.cos(2 * math.pi * i / N), (R0 + 1) * math.sin(2 * math.pi * i / N)) for i in range(N)],
              [pcbnew.F_Cu, pcbnew.B_Cu], tracks=False, holes=[(R_COMP * math.cos(-2 * math.pi * i / N), R_COMP * math.sin(-2 * math.pi * i / N)) for i in range(N)])
    for nm, sx, sy in S_HOLES:
        zone_rule("CR-BP-1_KO_" + nm, [(sx + 3.0 * math.cos(2 * math.pi * i / 32), sy + 3.0 * math.sin(2 * math.pi * i / 32)) for i in range(32)], CU4,
                  tracks=True, pour=True)
    for nm, ang, rc, s in (("J9", 45.0, 33.0, 5.0), ("J10", 135.0, 29.5, 5.0)):
        a = math.radians(ang); n = (math.cos(a), math.sin(a)); t = (-n[1], n[0]); n0 = rc + 12.13
        pts = [(nn * n[0] + ss * t[0], nn * n[1] + ss * t[1]) for nn, ss in ((n0, s - 21.6), (63.0, s - 21.6), (63.0, s + 21.6), (n0, s + 21.6))]
        zone_rule("MCIO_RIBBON_" + nm, pts, [pcbnew.F_Cu], fp=True, vias=False, tracks=False, pads=True, pour=False)
    # drawings
    def txt(s, x, y, layer=pcbnew.Cmts_User, size=1.0):
        t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
        t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(size * 0.15)); b.Add(t)
    txt("MP62 BP rev A1 'BP-G4' (4 layers, Gen4, RP2350B). Not for fab before the ICD rev 3.1 FS-lane decision", 0, -62.5, size=1.0)

def load_fp(fpid):
    lib, name = fpid.split(":")
    path = LIBS.get(lib, os.path.join(SYSFP, lib + ".pretty"))
    f = pcbnew.FootprintLoad(path, name)
    if f is None: sys.exit("missing footprint " + fpid)
    f.SetFPID(pcbnew.LIB_ID(lib, name)); return f

def courtyard_bbox(f, pad=0.0):
    pts = []
    for g in f.GraphicalItems():
        if g.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            bb = g.GetBoundingBox(); pts += [D(VECTOR2I(bb.GetLeft(), bb.GetTop())), D(VECTOR2I(bb.GetRight(), bb.GetBottom()))]
    if not pts:
        bb = f.GetBoundingBox(False, False); pts = [D(VECTOR2I(bb.GetLeft(), bb.GetTop())), D(VECTOR2I(bb.GetRight(), bb.GetBottom()))]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad)

# ---------------- placement ----------------
FIXED = ("J1", "J2", "J3", "J4", "J6", "J9", "J10", "H1", "H2")
MANUAL = {   # ref: (x, y, rot)   disc coords, footprint origin
    "U1": (-39.5, -26.5, 0.0), "U2": (-49.3, -20.5, 90.0), "Y1": (-39.5, -34.2, 0.0), "L3": (-28.6, -34.5, 0.0), "SW1": (-51.5, -12.0, 0.0),
    "U6": (33.0, -34.0, 0.0), "L1": (38.5, -34.0, 0.0), "U7": (33.0, -26.5, 0.0), "L2": (38.5, -26.5, 0.0),
    "D1": (-2.3, -41.0, 90.0), "D2": (1.6, -38.0, 90.0), "F1": (25.0, -38.5, 0.0), "D3": (30.5, -41.5, 0.0), "R100": (25.0, -36.0, 0.0), "U5": (28.5, -31.0, 0.0),
    "J7": (-20.0, -30.0, 90.0), "H3": (22.0, -30.0, 0.0),
    "U3": (47.5, -7.0, 0.0), "U4": (-30.0, -38.0, 0.0), "U8": (8.0, -43.0, 0.0), "SW2": (41.0, -20.0, 0.0), "JP1": (16.5, -43.0, 0.0),
}
CLUSTERS = {   # name: (xmin, xmax, ymin, ymax)
    "mcu": (-54.0, -23.0, -37.0, -18.2),
    "pwr": (21.0, 47.0, -44.0, -25.5),
    "gate": (-18.0, 21.0, -45.6, -32.0),
    "fp": (23.0, 54.0, -25.0, -18.2),
    "core": (44.0, 54.0, -10.0, -4.0),
    "left": (-57.0, -43.8, -16.8, -6.4),
    "under": (-18.0, 21.0, -32.0, -19.0),
}
FALLBACK = {"mcu": ["left", "under"], "fp": ["core", "pwr"], "gate": ["under"], "pwr": ["fp", "under", "gate"]}
def cluster_of(p):
    nets = set(p["nets"].values()) - {"GND", "3V3_SB"}
    has = lambda *pre: any(n.startswith(pre) for n in nets)
    if p["ref"] in ("C%d" % i for i in range(0)): pass
    if has("BST_", "SW_", "FB_", "EN_3V3", "EN_5V", "VIN", "5V_SBY"): return "pwr"
    if has("FP_", "AUXP", "3V3_AUX_P", "SW2"): return "fp"
    if has("ILK", "PSON", "HALL", "PS_ON_REQ", "TRIP_N", "LATCH", "THERM_LATCH", "BP_OTEMP", "PWRBTN_IN", "IOB_", "LED1", "M2_", "3V3_M2", "12V_MAIN", "11V_SB"):
        return "gate"
    return "mcu"

def build():
    b = new_board(); outline_and_keepouts(b)
    nets = {}
    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(b, name); b.Add(n); nets[name] = n
        return nets[name]
    placed = {}
    boxes = []   # (ref, bbox)
    for nm, sx, sy in S_HOLES: boxes.append((nm, (sx - 3.2, sx + 3.2, sy - 3.2, sy + 3.2)))
    for h in ("H1", "H2"):
        x, y = FP6[h]["x"], FP6[h]["y"]; boxes.append((h + "_KO", (x - HOLE_KO, x + HOLE_KO, y - HOLE_KO, y + HOLE_KO)))
    def put(p, x, y, rot, center=False):
        f = load_fp(p["fp"]); f.SetReference(p["ref"]); f.SetValue(p["value"][:120])
        f.SetPosition(P(x, y)); f.SetOrientationDegrees(rot); b.Add(f)
        if p.get("side") == "B": f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        for pad in f.Pads():
            n = p["nets"].get(pad.GetNumber())
            if n: pad.SetNet(net(n))
        f.SetField("LCSC", p["lcsc"]) if p["lcsc"] else None
        if p["dnp"]:
            f.SetDNP(True); f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
        f.Reference().SetTextSize(VECTOR2I(FromMM(0.6), FromMM(0.6))); f.Reference().SetTextThickness(FromMM(0.1))
        f.Value().SetVisible(False)
        placed[p["ref"]] = f; boxes.append((p["ref"], courtyard_bbox(f, 0.15)))
        return f
    byref = {p["ref"]: p for p in M.PARTS}
    for ref in FIXED:
        q = FP6[ref]; put(byref[ref], q["x"], q["y"], q["rot"])
    for ref, (x, y, rot) in MANUAL.items(): put(byref[ref], x, y, rot)
    def inside_board(bb):
        for (x, y) in ((bb[0], bb[2]), (bb[0], bb[3]), (bb[1], bb[2]), (bb[1], bb[3])):
            if math.hypot(x, y) > R_COMP - 0.3: return False
        return True
    def free(bb):
        for r, o in boxes:
            if bb[0] < o[1] and bb[1] > o[0] and bb[2] < o[3] and bb[3] > o[2]: return False
        return inside_board(bb)
    rest = [p for p in M.PARTS if p["ref"] not in placed]
    # rev A1 packer: routing room. Parts keep GAP (0.6 mm) between courtyards, nothing within U1_RING of U1's courtyard,
    # and each part goes to the free spot nearest its anchor (mean of already-placed pads on its signal nets;
    # U1 decoupling -> U1) instead of first-fit raster order.
    GAP = float(os.environ.get("BP_GAP", "0.7")); U1_RING = float(os.environ.get("BP_U1RING", "2.2"))
    ub = courtyard_bbox(placed["U1"], 0.0); boxes.append(("U1_RING", (ub[0] - U1_RING, ub[1] + U1_RING, ub[2] - U1_RING, ub[3] + U1_RING)))
    PWRN = {"GND", "3V3_SB", "5V_SBY", "VIN", "12V_MAIN_IN", "11V_SB_IN"}
    def padpos(f):
        return [(pd.GetNetname(), D(pd.GetPosition())) for pd in f.Pads()]
    def anchor(p):
        sig = set(p["nets"].values()) - PWRN
        pts = []
        for r, f in placed.items():
            for n, q in padpos(f):
                if n in sig: pts.append(q)
        if not pts and set(p["nets"].values()) <= {"3V3_SB", "GND", "DVDD"} and cluster_of(p) == "mcu":
            pts = [D(placed["U1"].GetPosition())]
        if not pts: return None, 0
        return (sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)), len(pts)
    fails = []
    while rest:
        sc = [(anchor(p)[1], -len(p["nets"]), p["ref"], p) for p in rest]
        sc.sort(key=lambda t: (-t[0], t[1], t[2]))
        p = sc[0][3]; rest.remove(p)
        anc, _ = anchor(p)
        ok = False
        for cname in [cluster_of(p)] + FALLBACK.get(cluster_of(p), []):
            if ok: break
            cl = CLUSTERS[cname]
            a0 = anc if anc else ((cl[0] + cl[1]) / 2, (cl[2] + cl[3]) / 2)
            cands = []
            for rot in (0.0, 90.0):
                f = load_fp(p["fp"]); f.SetOrientationDegrees(rot); bb0 = courtyard_bbox(f, 0.15)
                w, h = bb0[1] - bb0[0], bb0[3] - bb0[2]
                rx0, ry1 = bb0[0] + CX, bb0[3] - CY
                yy = cl[3]
                while yy - h >= cl[2]:
                    xx = cl[0]
                    while xx + w <= cl[1]:
                        cx_, cy_ = xx + w / 2, yy - h / 2
                        cands.append((math.hypot(cx_ - a0[0], cy_ - a0[1]), rot, xx, yy, w, h, rx0, ry1))
                        xx += 0.5
                    yy -= 0.5
            cands.sort(key=lambda t: t[0])
            for (_, rot, xx, yy, w, h, rx0, ry1) in cands:
                bbg = (xx - GAP / 2, xx + w + GAP / 2, yy - h - GAP / 2, yy + GAP / 2)
                if free(bbg) and inside_board((xx, xx + w, yy - h, yy)):
                    if rot == 0.0:
                        put(p, xx - rx0, yy - ry1, 0.0)
                    else:
                        f = put(p, 0.0, 0.0, 90.0); bbz = courtyard_bbox(f, 0.15)
                        f.SetPosition(P(xx - bbz[0], yy - bbz[3])); boxes[-1] = (p["ref"], courtyard_bbox(f, 0.15))
                    ok = True; break
        if not ok: fails.append(p["ref"])
    print("placed", len(placed), "fails", fails)
    return b, placed, nets

if __name__ == "__main__":
    b, placed, nets = build()
    pcbnew.SaveBoard(OUT, b)
    print("saved", OUT)
