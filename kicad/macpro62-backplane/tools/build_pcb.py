#!/usr/bin/env python3
"""Build the MacPro6,2 backplane rev-A first-pass floorplan with the KiCad 9 pcbnew API.
Run with the system python3 (KiCad 9.0.2). Coordinates in the comments are 'disc' coordinates:
origin = disc centre, +x right, +y up (as in the Fusion DXF). KiCad y points down."""
import json, math, os, sys
import pcbnew
from pcbnew import FromMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.abspath(os.path.join(HERE, ".."))
VARIANT = os.environ.get("VARIANT", "hub")
OUT = os.path.join(PRJ, "backplane.kicad_pcb") if VARIANT == "hub" else os.path.join(PRJ, "backplane_direct.kicad_pcb")
SYS = "/usr/share/kicad/footprints"
LOC = os.path.join(PRJ, "MP62_Placeholders.pretty")
CX, CY = 150.0, 100.0          # disc centre on the A4 sheet (mm)

dxf = json.load(open(os.path.join(HERE, "base_board_dxf.json")))
outline = [e for e in dxf if e.get("layer") == "OUTLINE"][0]
holes = [e for e in dxf if e.get("layer") == "HOLES"]
R = outline["r"]                 # 61.0
R_COMP = R - 3.0                 # component keep-out boundary (fillet / standoff margin, TBD)
HOLE_KO = 6.0                    # radius kept clear around each mounting hole (screw head + driver, TBD)

def P(x, y):
    return VECTOR2I(FromMM(CX + x), FromMM(CY - y))

board = pcbnew.NewBoard(OUT)
board.SetCopperLayerCount(6 if VARIANT == "hub" else 4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(FromMM(1.6))
# JLC 4-layer standard capabilities (conservative): 0.127/0.127 mm, via 0.3/0.6 (JLC min 0.15/0.25 at extra cost? keep std)
ds.m_TrackMinWidth = FromMM(0.127)
ds.m_MinClearance = FromMM(0.127)
ds.m_ViasMinSize = FromMM(0.45)
ds.m_MinThroughDrill = FromMM(0.3)
ds.m_CopperEdgeClearance = FromMM(0.5)
ds.m_HoleClearance = FromMM(0.25)
ds.m_HoleToHoleMin = FromMM(0.5)
ds.m_SilkClearance = FromMM(0.0)

tb = board.GetTitleBlock()
tb.SetTitle("MacPro6,2 Backplane (BP) - rev A floorplan " + ("v0.2 HUB" if VARIANT == "hub" else "v0.1 DIRECT (saved variant)"))
tb.SetRevision("A-fp5-hub" if VARIANT == "hub" else "A-fp1-direct")
tb.SetDate("2026-10-02")
tb.SetCompany("MacPro6,2 / Aidan Winkler")
tb.SetComment(0, "Edge.Cuts: D122 disc + 2x D4 holes at +/-49 mm from Fusion base_board_outline.dxf")
if VARIANT == "hub":
    tb.SetComment(1, "Stackup: JLC06161H-2116, 6L, 1.6 mm, ENIG. L1/L6 = 85-ohm PCIe microstrip, L2/L5 GND, L3/L4 power + low speed")
    tb.SetComment(2, "Topology: HUB. CPU board card edge (Mini Cool Edge 224) -> BP -> 2x MCIO 124 -> Face P x16 / Face S x4")
else:
    tb.SetComment(1, "Stackup: JLC04161H-7628, 4L, 1.6 mm, 1 oz outer / 0.5 oz inner (rev-A default)")
    tb.SetComment(2, "Topology: DIRECT (CPU board -> faces by MCIO). BP = power, MCU, low-speed only")
tb.SetComment(3, "PLACEHOLDER footprints marked *_PLACEHOLDER. Face chord positions are ASSUMED (TBD)")

# ---------------- Edge cuts ----------------
c = pcbnew.PCB_SHAPE(board)
c.SetShape(pcbnew.SHAPE_T_CIRCLE)
c.SetCenter(P(outline["cx"], outline["cy"]))
c.SetEnd(P(outline["cx"] + R, outline["cy"]))
c.SetLayer(pcbnew.Edge_Cuts)
c.SetWidth(FromMM(0.1))
board.Add(c)

def circle(x, y, r, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_CIRCLE)
    s.SetCenter(P(x, y)); s.SetEnd(P(x + r, y))
    s.SetLayer(layer); s.SetWidth(FromMM(w))
    board.Add(s)

def seg(x1, y1, x2, y2, layer, w=0.15):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2))
    s.SetLayer(layer); s.SetWidth(FromMM(w))
    board.Add(s)

def txt(s, x, y, layer=pcbnew.Cmts_User, size=1.2, angle=0.0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s); t.SetPosition(P(x, y))
    t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
    t.SetTextThickness(FromMM(size * 0.15))
    t.SetTextAngleDegrees(angle)
    board.Add(t)

# component keep-out ring as a rule area (R_COMP .. R)
z = pcbnew.ZONE(board)
z.SetIsRuleArea(True)
z.SetDoNotAllowFootprints(True)
z.SetDoNotAllowVias(True)
z.SetDoNotAllowTracks(False)
z.SetDoNotAllowPads(True)
z.SetDoNotAllowCopperPour(False)
z.SetZoneName("EDGE_RING_KEEPOUT")
ls = pcbnew.LSET(); [ls.AddLayer(l) for l in (pcbnew.F_Cu, pcbnew.B_Cu)]
z.SetLayerSet(ls)
o = z.Outline(); o.NewOutline()
N = 96
for i in range(N):
    a = 2 * math.pi * i / N
    p = P((R + 1.0) * math.cos(a), (R + 1.0) * math.sin(a)); o.Append(p.x, p.y)
o.NewHole()
for i in range(N):
    a = -2 * math.pi * i / N
    p = P(R_COMP * math.cos(a), R_COMP * math.sin(a)); o.Append(p.x, p.y, 0, 0)
board.Add(z)
circle(0, 0, R_COMP, pcbnew.Cmts_User, 0.1)
txt("COMPONENT KEEP-OUT RING 3 mm (R58-R61): chassis fillet + standoff margin. Height limit inside R58 TBD (measure core-to-base gap)", 0, -59.6, size=0.9)

# ---------------- mounting holes (plated, GND/chassis) ----------------
gnd = pcbnew.NETINFO_ITEM(board, "GND"); board.Add(gnd)
placed = []
def place(ref, lib, name, x, y, rot=0.0, value=None, side="F", center=True):
    libpath = LOC if lib == "MP62_Placeholders" else os.path.join(SYS, lib + ".pretty")
    f = pcbnew.FootprintLoad(libpath, name)
    if f is None:
        sys.exit("missing footprint %s:%s" % (lib, name))
    f.SetFPID(pcbnew.LIB_ID(lib, name))
    f.SetReference(ref)
    f.SetValue(value or name)
    f.SetPosition(P(x, y))
    f.SetOrientationDegrees(rot)
    board.Add(f)
    if center:
        # shift so the courtyard (or bbox) centre lands on the requested point
        try:
            cb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
            cc = cb.GetCenter() if cb.GetWidth() > 0 else f.GetBoundingBox(False).GetCenter()
        except Exception:
            cc = f.GetBoundingBox(False).GetCenter()
        tgt = P(x, y)
        f.Move(VECTOR2I(tgt.x - cc.x, tgt.y - cc.y))
    if side == "B":
        f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    placed.append((ref, f, value or name))
    return f

for i, h in enumerate(holes):
    f = place("H%d" % (i + 1), "MountingHole", "MountingHole_4mm_Pad", h["cx"], h["cy"],
              value="MountingHole D4 plated (stock D4.000 at x=%+.0f)" % h["cx"], center=False)
    circle(h["cx"], h["cy"], HOLE_KO, pcbnew.Cmts_User, 0.1)

# ---------------- CR-BP-1: six small stock holes S1-S6 (purpose unknown) -> D6 keep-outs ----------------
# Base-board scan, BP frame = midpoint of the gold holes (bracket/base_board/README.md). Not drilled on the BP.
S_HOLES = [("S1", -52.64, 13.81), ("S2", -26.57, -46.65), ("S3", 26.49, -46.64), ("S4", -18.12, 50.70), ("S5", 18.49, 50.72), ("S6", 52.80, 13.88)]
S_KO_R = 3.0
for nm, sx, sy in S_HOLES:
    zz = pcbnew.ZONE(board); zz.SetIsRuleArea(True)
    zz.SetDoNotAllowFootprints(True); zz.SetDoNotAllowVias(True); zz.SetDoNotAllowTracks(True)
    zz.SetDoNotAllowPads(True); zz.SetDoNotAllowCopperPour(True); zz.SetZoneName("CR-BP-1_KO_" + nm)
    lz = pcbnew.LSET(); [lz.AddLayer(l) for l in [pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu]]
    zz.SetLayerSet(lz)
    oz = zz.Outline(); oz.NewOutline()
    for i in range(32):
        a = 2 * math.pi * i / 32
        pp = P(sx + S_KO_R * math.cos(a), sy + S_KO_R * math.sin(a)); oz.Append(pp.x, pp.y)
    board.Add(zz)
    circle(sx, sy, S_KO_R, pcbnew.Cmts_User, 0.1)
    txt(nm + " stock hole: D6 keep-out (CR-BP-1)", sx, sy - 4.0, pcbnew.Cmts_User, 0.6)
# ---------------- face / CPU board planes (drawing only) ----------------
if VARIANT == "hub":
    # fp3: M2 measured (Aidan 2026-10-01): GPU boards ~55 mm from the disc centre; bottom edges ~15 mm above the BP (M1).
    # CPU board plane ESTIMATED at 12.6 mm from the service-guide photo of the stock logic-board riser slot (TBD).
    # fp5: face normals 45 / 135 deg (Aidan 2026-10-02, M2c ~45 deg; was assumed 30 / 150). CPU slot measured -12.5 +/- 0.3.
    CHORDS = (("CPU board plane (slot measured -12.5 +/- 0.3 on the scan, M2b)", -90.0, 12.6),
              ("Face P board plane ~55 mm (M2) at 45 deg (M2c, Aidan ~45), bottom edge ~15 mm above BP (M1)", 45.0, 55.0),
              ("Face S board plane ~55 mm (M2) at 135 deg (M2c, Aidan ~45), bottom edge ~15 mm above BP (M1)", 135.0, 55.0))
else:
    CHORDS = tuple((n, a, 30.0) for n, a in (("CPU face", -90.0), ("Face P (primary)", 30.0), ("Face S (secondary)", 150.0)))
for name, ang, D_FACE in CHORDS:
    a = math.radians(ang)
    nx, ny = math.cos(a), math.sin(a)
    tx, ty = -ny, nx
    half = math.sqrt(R * R - D_FACE * D_FACE)
    cxp, cyp = D_FACE * nx, D_FACE * ny
    seg(cxp - half * tx, cyp - half * ty, cxp + half * tx, cyp + half * ty, pcbnew.Dwgs_User, 0.3 if VARIANT == "hub" else 0.2)
    rot = math.degrees(math.atan2(ty, tx))
    if rot > 90: rot -= 180
    if rot < -90: rot += 180
    off = 1.8 if VARIANT == "hub" else 3.0
    lx, ly = cxp - off * nx, cyp - off * ny
    txt(name if VARIANT == "hub" else "%s bottom-edge chord ASSUMED d=%.0f mm (TBD)" % (name, D_FACE), lx, ly, pcbnew.Dwgs_User, 0.8 if VARIANT == "hub" else 1.0, rot)

if VARIANT == "direct":
    # ---------------- connectors and blocks (saved DIRECT variant) ----------------
    place("J1", "MP62_Placeholders", "MP62_CPULINK_CEMx8_98P_Vertical_SMT_PLACEHOLDER", 0.0, -32.0, 0,
          "CPU-LINK: CEM x8-size 98P vertical (MP62 pinout) - CPU board edge tab")
    place("J2", "Connector_Molex", "Molex_Micro-Fit_3.0_43045-0812_2x04_P3.00mm_Vertical", -40.0, -25.0, 0,
          "PSU-IN: Micro-Fit 3.0 2x4 (12V x2, GND x3, 11V_SB, PS_ON#, PWR_OK)")
    place("J3", "Connector_JST", "JST_GH_BM14B-GHS-TBT_1x14-1MP_P1.25mm_Vertical", 34.6, 20.0, -60.0,
          "FACE-P AUX: JST GH 14P (PWR_EN, PWR_GOOD, SMBus, THERM, PRSNT, 3V3_AUX, USB2)")
    place("J4", "Connector_JST", "JST_GH_BM14B-GHS-TBT_1x14-1MP_P1.25mm_Vertical", -34.6, 20.0, 60.0,
          "FACE-S AUX: JST GH 14P (same pinout as J3)")
    place("J5", "Connector_JST", "JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical", 0.0, 46.0, 180.0,
          "FAN: GH 4P (12V, GND, PWM, FG) - harness to top interposer, stock pinout TBD")
    place("J6", "Connector_JST", "JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", 44.0, -21.0, 90.0,
          "IOB-LINK: GH 15P (PWRBTN, HALL x2, LED I2C, USB2, 3V3_SB, GND)")
    place("J7", "MP62_Placeholders", "MP62_M2_2242_MKey_SATA_PLACEHOLDER", 0.0, 6.0, 0,
          "OpenCore boot: M.2 M-key socket, SATA0, 2242 card")
    place("J8", "Connector_JST", "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical", 12.0, 34.0, 0,
          "SWD (3V3, SWCLK, SWDIO, GND)")
    place("U1", "Package_DFN_QFN", "QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm", 0.0, -17.0, 0, "RP2350A (LCSC C42411118)")
    place("U2", "Package_SON", "WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4.3mm", 9.0, -17.0, 0, "W25Q128 QSPI flash (part TBD)")
    place("Y1", "Crystal", "Crystal_SMD_3225-4Pin_3.2x2.5mm", -7.0, -17.0, 0, "12 MHz crystal")
    place("U3", "Package_SO", "VSSOP-8_3x3mm_P0.65mm", 0.0, 30.0, 0, "TMP1075 core-base temp sensor #1")
    place("U4", "Package_SO", "VSSOP-8_3x3mm_P0.65mm", -12.0, 30.0, 0, "TMP1075 core-base temp sensor #2")
    place("PS1", "MP62_Placeholders", "MP62_AREA_StandbyPower_22x12_PLACEHOLDER", -28.0, -12.5, 0, "Standby power + HW safety gate")
    place("PS2", "MP62_Placeholders", "MP62_AREA_MainPower_20x12_PLACEHOLDER", 27.0, -12.5, 0, "Main-rail power")
    place("SW1", "Button_Switch_SMD", "SW_Push_1P1T_XKB_TS-1187A", -16.0, 38.0, 0, "BOOTSEL")
    place("SW2", "Button_Switch_SMD", "SW_Push_1P1T_XKB_TS-1187A", 24.0, 36.0, 0, "Bench power button")
    for i, (x, lbl) in enumerate(((-6.0, "11V_SB"), (-2.0, "12V main"), (2.0, "S0"), (6.0, "FAULT"))):
        place("D%d" % (i + 1), "LED_SMD", "LED_0603_1608Metric", x, 40.0, 0, "LED " + lbl)

else:
    exec(open(os.path.join(HERE, "hub_floorplan.py")).read())
# notes
notes = ([
    "MP62 BACKPLANE rev A - FIRST-PASS FLOORPLAN, HUB TOPOLOGY (not routed)",
    "J1 = CPU-LINK: Amphenol Mini Cool Edge 224 vertical; CPU board card edge (1.57 mm), MP62 pinout.",
    "PCIe: J1 -> (opt. DS320PR810 x5) -> J9 MCIO 124 Face P x16 / J10 MCIO 124 Face S x4 (AUX: J3 / J4).",
    "No AC caps on BP: host-TX caps on module/CPU board, device-TX caps on face module.",
    "12 V main to CPU board and faces: bus bars / lugs, NOT through the edge.",
] if VARIANT == "hub" else [
    "MP62 BACKPLANE rev A - FIRST-PASS FLOORPLAN (not routed) - SAVED DIRECT VARIANT",
    "No PCIe on this board: CPU board -> Face P/S by MCIO cable (direct).",
    "J1 = CPU-LINK card edge (low-speed + SATA0 + USB2 + 5V_SBY).",
    "12 V main to CPU board and faces: bus bars / lugs, NOT through BP.",
    "Placeholders: J1, J7, PS1, PS2 (outer dims from datasheets).",
])
for i, s in enumerate(notes):
    txt(s, 0, 74 - i * 2.2, pcbnew.Cmts_User, 1.2)
txt("Disc D122 (Fusion base_board_outline.dxf), holes D4 at (+/-49, 0)", 0, -66, pcbnew.Cmts_User, 1.2)

# ---------------- fit check ----------------
report = []
ok = True
for ref, f, val in placed:
    if ref.startswith("H"):
        continue
    cy = f.GetCourtyard(pcbnew.F_Cu) if hasattr(f, "GetCourtyard") else None
    bb = f.GetBoundingBox(False)
    pts = []
    try:
        poly = f.GetCourtyard(pcbnew.F_CrtYd)
        if poly.OutlineCount() > 0:
            ol = poly.COutline(0)
            pts = [(pcbnew.ToMM(ol.CPoint(i).x) - CX, CY - pcbnew.ToMM(ol.CPoint(i).y)) for i in range(ol.PointCount())]
    except Exception:
        pts = []
    if not pts:
        pts = [(pcbnew.ToMM(bb.GetLeft()) - CX, CY - pcbnew.ToMM(bb.GetTop())),
               (pcbnew.ToMM(bb.GetRight()) - CX, CY - pcbnew.ToMM(bb.GetBottom()))]
    rmax = max(math.hypot(x, y) for x, y in pts)
    # min distance from the bbox of the courtyard to each hole centre
    dmin = 1e9
    def _segd(px, py, ax, ay, bx, by):
        vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy
        t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / L2))
        return math.hypot(px - ax - t * vx, py - ay - t * vy)
    def _inside(px, py, P):
        c = False
        for i in range(len(P)):
            (x1, y1), (x2, y2) = P[i], P[(i + 1) % len(P)]
            if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1): c = not c
        return c
    if len(pts) == 2:   # bbox fallback -> rectangle
        (xa, ya), (xb, yb) = pts; pts = [(xa, ya), (xb, ya), (xb, yb), (xa, yb)]
    for h in holes:
        d = 0.0 if _inside(h["cx"], h["cy"], pts) else min(_segd(h["cx"], h["cy"], *pts[i], *pts[(i + 1) % len(pts)]) for i in range(len(pts)))
        dmin = min(dmin, d)
    smin = 1e9
    for nm, sx, sy in S_HOLES:
        d = 0.0 if _inside(sx, sy, pts) else min(_segd(sx, sy, *pts[i], *pts[(i + 1) % len(pts)]) for i in range(len(pts)))
        smin = min(smin, d)
    good = rmax <= R_COMP and dmin >= HOLE_KO and smin >= S_KO_R
    ok &= good
    report.append("%-4s rmax=%5.1f (limit %.0f)  hole-dist=%5.1f (min %.0f)  S-dist=%5.1f (min %.0f)  %s  %s" % (ref, rmax, R_COMP, dmin, HOLE_KO, smin, S_KO_R, "OK" if good else "FAIL", val))
open(os.path.join(PRJ, "fitcheck_floorplan.txt") if VARIANT == "hub" else os.path.join(PRJ, "variants", "fitcheck_direct.txt"), "w").write("\n".join(report) + "\n")
print("\n".join(report))
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "ALL OK" if ok else "SOME FAIL")
