#!/usr/bin/env python3
"""MP62 I/O plate v2 rev A0 (new plastic plate; stock metal I/O frame and the stock 821-2222-A I/O-wall flex are reused). cadquery 2.8 + ezdxf.
Frame: stock BACK-VIEW frame of the I/O board (mm): origin at the board's bottom-left virtual corner, X to the right as seen from behind
the machine, Y up toward the MEG-array / base end. Z = 0 is the crown of the plate OUTER (visible) face, -Z goes into the machine.
Usage: python build_plate.py [--eth2 open|blank]
Rev 2026-10-02 ~10:07 ET (Aidan flatbed scan of the 821-2222-A flex + measured D0):
  * port grid = centres of the stock flex cut-outs (scan trace flex_821-2222_trace.json); USB-C columns X 43.09 / 63.69;
  * NO lands, NO bosses: every opening goes straight through the curved 1.2 skin, the inner face is one smooth cylinder so the stock
    flex lies flat (bosses cannot fit inside the flex cut-outs: <= 0.4 mm/side); the flex sits in a 0.2 glue pocket;
  * curvature from D0 (board top -> cover inner face): 18.0 at the crown, 16.5 at |u| = D0_EDGE_U -> inner R ~80.8, outer R ~82.0;
  * clearance pockets on the inner face for the flex's plate-side LEDs and the button carrier, ear pins, Ø2.4 locating pins;
  * shallow outer spot-faces at the USB-C columns (plug overmold relief, >= 0.6 wall kept);
  * connector mouth heights / stack-up reported in io_plate_v2_A0_features.json ("stack")."""
import json, math, os, sys
import cadquery as cq
import ezdxf
from matplotlib.path import Path as MPath
HERE = os.path.dirname(os.path.abspath(__file__))
ETH2 = "open"    # rev A0 default (D-IO2: 2 x i226-V); "--eth2 blank" builds the single-Ethernet variant
if "--eth2" in sys.argv: ETH2 = sys.argv[sys.argv.index("--eth2") + 1]
TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else ""     # variant builds (e.g. --tilt 12.5 --tag _tilt12p5): own STEP/STL/features JSON, no DXF/PNG
FJ = json.load(open(os.path.join(HERE, "flex_821-2222_trace.json")))
CUT = {c["id"]: c for c in FJ["cutouts"]}
PADS = {p["id"]: p for p in FJ["light_pads"]}
BTN = FJ["button"]

# ---------------- stack-up (z, mm; 0 = crown of the outer face) ----------------
SKIN = 1.2                                  # plate wall = stock cover wall [ASSUMED, MEASURE M-IOS1]
D0_CROWN, D0_EDGE = 18.0, 16.5            # Aidan 2026-10-02: board top -> cover inner face, crown / outermost port edge
D0_EDGE_SIDE = "mean"                        # Aidan 10:21 ET: 16.5 read at the outer edge of the outermost port columns -> "mean" | "H" | "O" | a number (|u| in mm)
_ce = [c for c in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flex_821-2222_trace.json")))["cutouts"] if "w" in c]
_uH = 53.19 - min(c["cx"] - c["w"] / 2 for c in _ce if c["cx"] < 53.19)   # H side: HDMI outer edge (X 34.89)
_uO = max(c["cx"] + c["w"] / 2 for c in _ce if c["cx"] > 53.19) - 53.19   # O side: USB-A outer edge (X 71.09)
D0_EDGE_U = {"mean": (_uH + _uO) / 2, "H": _uH, "O": _uO}.get(D0_EDGE_SIDE, D0_EDGE_SIDE) if isinstance(D0_EDGE_SIDE, str) else D0_EDGE_SIDE
_s = D0_CROWN - D0_EDGE
R_INNER = (D0_EDGE_U ** 2 + _s ** 2) / (2 * _s)     # 109.97 from D0 (rev 10:21 ET)
# Stock-cover phone scan (2026-10-02 11:07, ../io_cover_scan/io_cover_scan_check.json): inner-face fit R 101.7 (bootstrap 99.7-103.7,
# Y-bands 94-123, half-width 16-24 mm -> 77-102): consistent with the D0 value, rules out the old 82, but not tighter than D0 -> kept.
R_INNER_OVERRIDE = None                      # e.g. 101.7 to use the scan fit instead of D0 (one-line switch; risers.json/tilt follow)
if R_INNER_OVERRIDE: R_INNER = R_INNER_OVERRIDE
CASE_R = R_INNER + SKIN                      # 111.17 outer
Z_BOARD = -SKIN - D0_CROWN                   # stock board top at -19.2 (our board top assumed at the same plane: MEASURE M-IOS2)
FLEX_T, PSA_T = 0.12, 0.05                   # flex + its PSA [Estimate, MEASURE]
FOAM_T = 1.0                                 # stock foam behind the flex (board side) [Aidan ~1, MEASURE]
FRAME_T = 1.0                                # metal I/O frame thickness, assumed concentric with the plate [MEASURE M-IOF2]
FLEX_POCKET = 0.20                           # glue pocket depth into the inner skin
FLEX_CLR = 0.20                              # pocket outline = flex outline + this (also locates the flex: +-0.2)
LED_H, LED_CLR = 0.60, 0.25                  # plate-side LED chip height above the flex face [MEASURE], pocket clearance per side
BTN_CARRIER_H = 0.60                         # button carrier ring height above the flex face, plate side [MEASURE]
POCKET_GAP = 0.10                            # air gap above LEDs / carrier
MIN_WALL = 0.6                               # outer spot-faces keep at least this wall

# ---------------- outline, ports ----------------
PL_C = (53.19, 77.07); PL_W, PL_H, PL_R = 51.9, 163.1, 11.5      # outline (fit of the stock plate scan)
RIM_H = 3.0; RIM_W = 1.2
XH, XO = CUT["C1"]["cx"], CUT["C4"]["cx"]                        # USB-C columns from the flex cut-outs (43.09 / 63.69)
OPEN = []   # (id, kind, cx, cy, w, h, r)   plate opening = straight through the skin
for i in range(3):
    for cid in ("C%d" % (i + 1), "C%d" % (i + 4)):
        OPEN.append((cid, "USBC", CUT[cid]["cx"], CUT[cid]["cy"], 9.6, 4.0, 1.8))
for a in ("A1", "A2", "A3", "A4"):
    OPEN.append((a, "USBA", CUT[a]["cx"], CUT[a]["cy"], 14.0, 6.0, 0.6))
OPEN.append(("ETH1", "RJ45", CUT["ETH1"]["cx"], CUT["ETH1"]["cy"], 13.0, 10.4, 0.5))
if ETH2 == "open": OPEN.append(("ETH2", "RJ45", CUT["ETH2"]["cx"], CUT["ETH2"]["cy"], 13.0, 10.7, 0.5))
OPEN.append(("HDMI", "HDMI", CUT["HDMI"]["cx"], CUT["HDMI"]["cy"], 15.6, 5.7, 1.0))
OPEN.append(("AC", "AC", 52.08, 129.95, 34.55, 24.65, 3.0))
ROUND = [("AUD_H", 43.4, 19.1, 4.8), ("AUD_O", 64.65, 19.4, 4.8), ("PWR_BTN", BTN["cx"], BTN["cy"], 12.4)]   # audio = stock plate positions (stock audio module)
WINDOWS = [("W_HDMI", PADS["PAD_HDMI"]["cx"], PADS["PAD_HDMI"]["cy"], 7.0, 1.6, 0.6), ("W_ETH", PADS["PAD_ETH"]["cx"], PADS["PAD_ETH"]["cy"], 3.0, 5.0, 1.0),
           ("W_TB", PADS["PAD_TB"]["cx"], PADS["PAD_TB"]["cy"], 3.0, 5.0, 1.0), ("W_USB", PADS["PAD_USB"]["cx"], PADS["PAD_USB"]["cy"], 3.0, 6.0, 1.0),
           ("W_AUD_H", PADS["PAD_AUD_H"]["cx"], PADS["PAD_AUD_H"]["cy"], 4.0, 2.4, 0.8), ("W_AUD_O", PADS["PAD_AUD_O"]["cx"], PADS["PAD_AUD_O"]["cy"], 4.0, 2.4, 0.8)]
CLIPS_L = [(31.0, 140.0), (28.2, 90.0), (29.6, 30.3)]           # stock clip points (left), mirrored about the plate centre X
CLIP_B = [(44.1, 2.7)]
CLIPS = [(x, y, "x-") for x, y in CLIPS_L] + [(2 * PL_C[0] - x, y, "x+") for x, y in CLIPS_L] + \
        [(x, y, "y-") for x, y in CLIP_B] + [(2 * PL_C[0] - x, y, "y-") for x, y in CLIP_B]
CLIP_T, CLIP_W, CLIP_L, CLIP_HOOK = 1.2, 5.0, 6.0, 0.5
FRAME_SCREW = (53.38, 58.38); SCREW_POCKET_D, SCREW_POCKET_DEPTH = 6.0, 0.6
LOCATE_PINS = [("PIN_C1", 52.93, 75.41, 2.4), ("PIN_C3", 54.49, 19.23, 2.4)]; PIN_LEN = 2.5    # frame holes (frame scan); pass the flex holes Ø3.3 / Ø5.67
EAR_PINS = [(h["id"], h["cx"], h["cy"], 1.4) for h in FJ["holes"] if h["id"].startswith("BTN_EAR")]; EAR_PIN_LEN = 0.8   # locate the button end of the flex
NECK = (76.0, FJ["neck"]["y"][0] - 0.5, 81.5, FJ["neck"]["y"][1] + 0.5)   # rim notch where the flex neck leaves over the +X edge
# outer spot-faces (plug overmold relief) per USB-C column: (id, cx, cy, w, h, r); floor = flat, >= MIN_WALL everywhere
_cy = [CUT["C%d" % k]["cy"] for k in (1, 2, 3)]
RELIEF = []   # rev 10:30 ET: tilted ports, mouth tangent to the face -> no overmold spot-faces needed
TILT_KINDS = ("USBC", "USBA", "HDMI")        # these sit on tilted column risers, axis normal to the plate at the opening (D-IO14)
TILT_OVERRIDE_DEG = None                     # rev 12:35 ET (port modules, D-IO16): DEFAULT = axis normal to the plate at each opening (full plug seating).
                                             # Stock = 12.5 outward (M-IOT2, Aidan 11:47 ET): build with "--tilt 12.5 --tag _tilt12p5" for the comparison report.
                                             # None = surface normal from CASE_R (5.3-5.5 deg at R 110); any number forces |tilt| (sign = outward)
if "--tilt" in sys.argv: _tv = sys.argv[sys.argv.index("--tilt") + 1]; TILT_OVERRIDE_DEG = None if _tv == "normal" else float(_tv)
MOUTH_CLR = 0.05                             # no point of a tilted shell mouth closer than this to the outer surface (mouth never proud)
AXIS_SHIFT_OUT = {}                          # extra OUTBOARD axis shift at the flex plane (mm). Was {"USBA": 0.35} for the 12.5 deg column risers; port modules are separate -> none
AXIS_BALANCE = True                          # shift each tilted axis along X (at the flex plane) to maximise the smallest flex / foam / frame-slot margin
TILT_SEAT = True                             # flat plug seats on the OUTER face, perpendicular to the port axis (reduce the overmold stand-off of an off-normal port)
SEAT_CLR, SEAT_MIN_WALL = 0.25, 0.6          # seat = plug overmold + 2 x SEAT_CLR; the floor keeps >= SEAT_MIN_WALL of skin (inner face stays smooth for the flex)
RISER_T = 1.16                               # D-IO16 port module: stack below the connector seat = FPC 0.11 + stiffener PSA 0.05 + FR4 stiffener 1.0 (the "riser_*" keys keep their names)
CONN_H = {"USBC": 10.0, "USBA": 11.5, "HDMI": 10.5}   # catalogue heights of the riser connectors (mating face above the riser top)
LEGEND = [("blank ETH2 recess", CUT["ETH2"]["cx"], CUT["ETH2"]["cy"], 13.0, 10.7)] if ETH2 == "blank" else []
# connector envelopes: shell (passes plate + flex), overmold of the mating plug (spec max / typical)
SHELL = {"USBC": dict(shell=(8.94, 3.26), overmold=(12.35, 6.5)), "USBA": dict(shell=(13.2, 5.7), overmold=(16.0, 8.0)),
         "HDMI": dict(shell=(15.2, 5.5), overmold=(20.0, 10.5)), "RJ45": dict(body=(16.2, 17.0), plug=(11.7, 8.2))}
PARTS = {
    "USBC": dict(mpn="HOAUC HYCW417-USBC24-180B", lcsc="C5342202", h=10.0, note="USB 3.1 Type-C 24P vertical, ALL-SMD (signal + shell tabs) for FPC mounting, L 10.0 (VERIFY drawing: height / shell tabs); alt SHOU HAN TYPE-C 24PLT-H10.5 C3151750 (THT shell legs) with CONN_H 10.5"),
    "USBA": dict(mpn="kinghelm KH-3.0AF180ZJ-11.5JB", lcsc="C2979037", h=11.5, note="USB 3.0 Type-A 9P vertical, L 11.5, THT signal + shell legs -> through the FPC + drilled FR4 stiffener, JLC selective solder (no all-SMD vertical USB 3 A found on LCSC)"),
    "HDMI": dict(mpn="HOAUC HYC79-HDMIA19-105", lcsc="C711353", h=10.5, note="HDMI-A 19P vertical, SMD signals + THT shell legs (through the FR4 stiffener), H 10.5 (front shell must be <= 15.4 x 5.6 to pass the flex: verify); HDMI port module"),
    "RJ45": dict(mpn="Lingqiang ZJLQ-RJ45-SMD-PCB125-8P8C (vertical SMD, unshielded, no magnetics, no LED; height not on LCSC page: VERIFY <= 13.0) + JASN V24P05S 2.5G magnetics", lcsc="C55547809 + C2827281", h=12.0,
                 note="D-IO15: non-magnetic vertical RJ45 on the main board + discrete JASN V24P05S (SMD-24P 15.1 x 7.1, 1:1 CT, 180 uH, 1.5 kVrms, IEEE 802.3bz, LCSC $0.63 @10)")}

def zs(x):  # outer surface height at X (0 at the crown)
    u = x - PL_C[0]; return -(CASE_R - math.sqrt(CASE_R ** 2 - u * u))
def zi(x): return zs(x) - SKIN
def d0(x): return zi(x) - Z_BOARD

# ---------------- solid ----------------
BIG = 400.0
def prism(w, h, r, z0=2.0, z1=-20.0):
    return cq.Workplane("XY").workplane(offset=z0).center(*PL_C).sketch().rect(w, h).vertices().fillet(r).finalize().extrude(z1 - z0)
def cyl(rad): return cq.Workplane("XZ").center(PL_C[0], -CASE_R).circle(rad).extrude(BIG, both=True)
def boxz(cx, cy, w, h, r, za, zb):
    return cq.Workplane("XY").workplane(offset=za).center(cx, cy).sketch().rect(w, h).vertices().fillet(max(min(r, w / 2 - 0.01, h / 2 - 0.01), 0.05)).finalize().extrude(zb - za)
R0 = CASE_R
FLEX_POLY = [tuple(p) for p in FJ["outline"]]
def _seg_d(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-12)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
def flex_dist(px, py):   # signed distance to the flex outline (negative inside)
    d = min(_seg_d(px, py, *FLEX_POLY[i], *FLEX_POLY[(i + 1) % len(FLEX_POLY)]) for i in range(len(FLEX_POLY)))
    inside = MPath(FLEX_POLY).contains_point((px, py)) or (NECK[0] <= px <= NECK[2] and NECK[1] <= py <= NECK[3])
    return -d if inside else d
dropped_clips = []; keep = []
for x, y, o in CLIPS:
    if (x, y) in CLIPS_L + CLIP_B: keep.append((x, y, o)); continue     # stock clip points always stay (the stock flex lived with them)
    hw, hh = ((CLIP_T + 2 * CLIP_HOOK) / 2, CLIP_W / 2) if o[0] == "x" else (CLIP_W / 2, (CLIP_T + 2 * CLIP_HOOK) / 2)
    dmin = min(flex_dist(x + i * hw, y + j * hh) for i in (-1, 0, 1) for j in (-1, 0, 1))
    (keep if dmin > FLEX_CLR + 0.2 else dropped_clips).append((x, y, o))
CLIPS = keep

plate = prism(PL_W, PL_H, PL_R).intersect(cyl(R0)).cut(cyl(R0 - SKIN))      # constant wall, inner face concentric (one smooth cylinder)
rim = prism(PL_W, PL_H, PL_R).cut(prism(PL_W - 2 * RIM_W, PL_H - 2 * RIM_W, PL_R - RIM_W)).intersect(cyl(R0 - SKIN + 0.02)).cut(cyl(R0 - SKIN - RIM_H))
plate = plate.union(rim)
report = []
for x, y, o in CLIPS:
    z_ = zi(x)
    if o[0] == "x":
        tab = cq.Workplane("XY").workplane(offset=z_ + 0.3).center(x, y).rect(CLIP_T, CLIP_W).extrude(-(CLIP_L + 0.3))
        hook = cq.Workplane("XY").workplane(offset=z_ - CLIP_L + 1.2).center(x + (-1 if o == "x-" else 1) * (CLIP_T / 2 + CLIP_HOOK / 2), y).rect(CLIP_HOOK, CLIP_W).extrude(-1.2)
    else:
        tab = cq.Workplane("XY").workplane(offset=z_ + 0.3).center(x, y).rect(CLIP_W, CLIP_T).extrude(-(CLIP_L + 0.3))
        hook = cq.Workplane("XY").workplane(offset=z_ - CLIP_L + 1.2).center(x, y - (CLIP_T / 2 + CLIP_HOOK / 2)).rect(CLIP_W, CLIP_HOOK).extrude(-1.2)
    plate = plate.union(tab).union(hook)
for x, y, o in dropped_clips: report.append(("CLIP_DROPPED", "CLIP", x, y, CLIP_T, CLIP_W, "mirrored clip collides with the 821-2222 flex/neck -> removed"))
plate = plate.cut(cq.Workplane("XY").workplane(offset=zi(FRAME_SCREW[0]) - 0.01).center(*FRAME_SCREW).circle(SCREW_POCKET_D / 2).extrude(SCREW_POCKET_DEPTH + 0.01))
# glue pocket (flex outline + FLEX_CLR, FLEX_POCKET into the skin) + neck notch through the rim
fl = cq.Workplane("XY").workplane(offset=-20).polyline(FLEX_POLY).close().offset2D(FLEX_CLR).extrude(22)
fl = fl.union(boxz((NECK[0] + NECK[2]) / 2, (NECK[1] + NECK[3]) / 2, NECK[2] - NECK[0], NECK[3] - NECK[1], 0.3, -20, 2))
plate = plate.cut(fl.intersect(cyl(R0 - SKIN + FLEX_POCKET)))
report.append(("FLEX_POCKET", "GLUE", PL_C[0], PL_C[1], 0, 0, "821-2222-A glue pocket %.2f deep (outline + %.2f), wall left %.2f; inner face otherwise one smooth cylinder (no bosses); rim notched X %.1f-%.1f, Y %.1f-%.1f" % (
    FLEX_POCKET, FLEX_CLR, SKIN - FLEX_POCKET, NECK[0], NECK[2], NECK[1], NECK[3])))
# clearance pockets for the plate-side parts of the flex (LED chips, button carrier ring)
R_FLEXFACE = R0 - SKIN + FLEX_POCKET - PSA_T          # plate-side face of the flex
R_LEDPOCKET = R_FLEXFACE + LED_H + POCKET_GAP
R_BTNPOCKET = R_FLEXFACE + BTN_CARRIER_H + POCKET_GAP
led_cut = None
for k, l in enumerate(FJ["leds"]):
    b = boxz(l["cx"], l["cy"], l["w"] + 2 * LED_CLR, l["h"] + 2 * LED_CLR, 0.3, -20, 2)
    led_cut = b if led_cut is None else led_cut.union(b)
plate = plate.cut(led_cut.intersect(cyl(R_LEDPOCKET)))
plate = plate.cut(cq.Workplane("XY").workplane(offset=-20).center(BTN["cx"], BTN["cy"]).circle(BTN["ring_d"] / 2 + 0.3).extrude(22).intersect(cyl(R_BTNPOCKET)))
report.append(("LED_POCKETS", "POCKET", 0, 0, 0, 0, "%d pockets (chip + %.2f/side), %.2f above the flex face, wall left %.2f" % (len(FJ["leds"]), LED_CLR, LED_H + POCKET_GAP, R0 - R_LEDPOCKET)))
report.append(("BTN_CARRIER_POCKET", "POCKET", BTN["cx"], BTN["cy"], BTN["ring_d"] + 0.6, BTN["ring_d"] + 0.6, "Ø%.2f, %.2f above the flex face, wall left %.2f (carrier height TO MEASURE)" % (BTN["ring_d"] + 0.6, BTN_CARRIER_H + POCKET_GAP, R0 - R_BTNPOCKET)))
# outer spot-faces at the USB-C columns
relief_info = {}
for rid, x, y, w, h, r in RELIEF:
    u_near = min(abs(x - w / 2 - PL_C[0]), abs(x + w / 2 - PL_C[0]))
    zf = -(CASE_R - math.sqrt(CASE_R ** 2 - u_near ** 2)) - (SKIN - MIN_WALL)
    plate = plate.cut(boxz(x, y, w, h, r, zf, 5.0))
    relief_info[rid] = dict(floor_z=round(zf, 3), w=w, h=h, cx=round(x, 3), cy=round(y, 3))
    report.append((rid, "SPOTFACE", x, y, w, h, "flat floor z=%.2f (wall >= %.1f at the inboard edge); USB-C plug overmold relief" % (zf, MIN_WALL)))
R_FLEX = R0 - SKIN + FLEX_POCKET - PSA_T - FLEX_T / 2
def tilt_of(x):
    u = x - PL_C[0]; a = math.asin(u / R_FLEX)
    if TILT_OVERRIDE_DEG is not None: a = math.copysign(math.radians(TILT_OVERRIDE_DEG), u)
    return a
fr = json.load(open(os.path.join(HERE, "..", "..", "bracket", "io_frame", "io_frame.json")))["features"]
SLOT = {"USBC_H": "TALL_R", "USBC_O": "TALL_L", "USBA_H": "SQ_R", "USBA_O": "SQ_L", "HDMI": "SMALL_R1", "ETH2": "SMALL_R2"}
R_FB = R_FLEXFACE - FLEX_T; R_FOAM = R_FB - FOAM_T; R_FRB = R_FOAM - FRAME_T
_TG = {}
def tilt_geom(oid, kind, x, y, w):
    """Tilted port: axis direction n at tilt_of(x), through the flex cut-out centre (+ balance shift) at the flex mid-plane.
    Returns mouth plane, recesses, overmold stand-off (with / without seat), per-layer margins of the tilted shell."""
    if oid in _TG: return _TG[oid]
    c = CUT[oid]; side = "H" if x < PL_C[0] else "O"; sw, sh = SHELL[kind]["shell"]; ow, oh = SHELL[kind]["overmold"]
    ang = tilt_of(x); n = (math.sin(ang), math.cos(ang)); ex = (math.cos(ang), -math.sin(ang)); fslot = fr[SLOT[kind + ("" if kind == "HDMI" else "_" + side)]]
    def build(dx):
        u = x - PL_C[0] + dx; P0 = (u, -R0 + math.sqrt(R_FLEX ** 2 - u * u))
        def t_hit(xi, rho):
            qx, qz = P0[0] + xi * ex[0], P0[1] + xi * ex[1] + R0; b = qx * n[0] + qz * n[1]; cc = qx * qx + qz * qz - rho * rho
            return -b + math.sqrt(b * b - cc)
        def span(r_a, r_b):
            pts = []
            for rho in (r_a, r_b):
                for xi in (-sw / 2, sw / 2):
                    t = t_hit(xi, rho); qx, qz = P0[0] + xi * ex[0] + t * n[0], P0[1] + xi * ex[1] + t * n[1] + R0
                    pts.append(PL_C[0] + rho * math.atan2(qx, qz))
            return min(pts), max(pts)
        def marg(sp, lo, hi): return [round(sp[0] - lo, 3), round(hi - sp[1], 3)]
        m = dict(flex=marg(span(R_FLEXFACE, R_FB), c["cx"] - c["w"] / 2, c["cx"] + c["w"] / 2),
                 foam=marg(span(R_FB, R_FOAM), c["cx"] - c["w"] / 2 - 0.3, c["cx"] + c["w"] / 2 + 0.3),
                 frame=marg(span(R_FOAM, R_FRB), fslot["cx"] - fslot["w"] / 2, fslot["cx"] + fslot["w"] / 2))
        return P0, t_hit, m
    dx = 0.0
    if AXIS_BALANCE:
        _, _, m = build(0.0); lo = min(v[0] for v in m.values()); hi = min(v[1] for v in m.values()); dx = round((hi - lo) / 2, 3)
        if abs(dx) < 0.02: dx = 0.0
    dx = round(dx + math.copysign(AXIS_SHIFT_OUT.get(kind, 0.0), x - PL_C[0]), 3)
    P0, t_hit, m = build(dx)
    t_ax = t_hit(0.0, R0); t_m = min(t_hit(xi, R0 - MOUTH_CLR) for xi in (-sw / 2, sw / 2))
    rec_e = [t_hit(xi, R0) - t_m for xi in (-sw / 2, sw / 2)]
    xis = [w / 2 + k * (ow / 2 - w / 2) / 20 for k in range(21)] if ow > w else []
    stand0 = max([0.0] + [t_hit(sg * xi, R0) - t_m for xi in xis for sg in (-1, 1)])
    W = ow + 2 * SEAT_CLR
    t_seat = max(t_m, max(t_hit(sg * xi, R0 - SKIN + SEAT_MIN_WALL) for xi in [w / 2 + k * (W / 2 - w / 2) / 20 for k in range(21)] for sg in (-1, 1)))
    stand = min(stand0, t_seat - t_m) if TILT_SEAT else stand0
    seat_depth = max(0.0, max(t_hit(sg * W / 2, R0) for sg in (-1, 1)) - t_seat)
    g = dict(ang=ang, n=n, ex=ex, P0=P0, dx=dx, t_m=t_m, rec=t_ax - t_m, rec_e=rec_e, stand0=stand0, stand=stand, t_seat=t_seat, seat_w=W, seat_h=oh + 2 * SEAT_CLR,
             seat=(TILT_SEAT and stand0 - stand > 0.02), seat_depth=seat_depth, m=m, sw=sw, sh=sh,
             M=(P0[0] + t_m * n[0], P0[1] + t_m * n[1]), surface_normal=math.asin((x - PL_C[0]) / R_FLEX))
    _TG[oid] = g; return g
for oid, kind, x, y, w, h, r in OPEN:
    if kind in TILT_KINDS:
        tg = tilt_geom(oid, kind, x, y, w); a = tg["ang"]; xs, zf = tg["P0"][0] + PL_C[0], tg["P0"][1]   # axis through the flex cut-out centre (+ balance shift)
        hole = cq.Workplane("XY").box(w, h, 14.0).edges("|Z").fillet(min(r, w / 2 - 0.01, h / 2 - 0.01)).rotate((0, 0, 0), (0, 1, 0), math.degrees(a)).translate((xs, y, zf))
        plate = plate.cut(hole); report.append((oid, kind, x, y, w, h, "straight through-hole along the tilted port axis (%.2f deg, axis shift %+.2f), centred on the flex cut-out at the flex plane" % (math.degrees(a), tg["dx"])))
        if tg["seat"]:   # flat seat perpendicular to the axis, floor at t_seat along the axis
            fx, fz = tg["P0"][0] + tg["t_seat"] * tg["n"][0] + PL_C[0], tg["P0"][1] + tg["t_seat"] * tg["n"][1]
            seat = cq.Workplane("XY").box(tg["seat_w"], tg["seat_h"], 6.0).edges("|Z").fillet(1.0).translate((0, 0, 3.0)).rotate((0, 0, 0), (0, 1, 0), math.degrees(a)).translate((fx, y, fz))
            plate = plate.cut(seat); report.append((oid + "_SEAT", "SEAT", x, y, tg["seat_w"], tg["seat_h"], "flat plug seat perpendicular to the axis, %.2f deep at the high edge, wall >= %.1f" % (tg["seat_depth"], SEAT_MIN_WALL)))
    else:
        plate = plate.cut(boxz(x, y, w, h, r, 10.0, -20.0)); report.append((oid, kind, x, y, w, h, "through the curved skin (no land)"))
for oid, x, y, dd in ROUND:
    plate = plate.cut(cq.Workplane("XY").workplane(offset=10).center(x, y).circle(dd / 2).extrude(-30)); report.append((oid, "ROUND", x, y, dd, dd, "through"))
for wid, x, y, w, h, r in WINDOWS:
    plate = plate.cut(boxz(x, y, w, h, r, 10.0, -20.0)); report.append((wid, "LIGHT_WINDOW", x, y, w, h, "through window over the flex light-guide pad"))
for pid, x, y, dd in LOCATE_PINS:
    plate = plate.union(cq.Workplane("XY").workplane(offset=zi(x) + 0.3).center(x, y).circle(dd / 2).extrude(-(PIN_LEN + 0.3)).faces("<Z").chamfer(0.3))
    report.append((pid, "PIN", x, y, dd, dd, "locating pin Ø%.1f x %.1f into the frame hole, through the flex hole" % (dd, PIN_LEN)))
for pid, x, y, dd in EAR_PINS:
    plate = plate.union(cq.Workplane("XY").workplane(offset=zi(x) + FLEX_POCKET + 0.01).center(x, y).circle(dd / 2).extrude(-(EAR_PIN_LEN + FLEX_POCKET)).faces("<Z").chamfer(0.2))
    report.append((pid, "PIN", x, y, dd, dd, "flex locating pin Ø%.1f x %.1f in the button-carrier ear hole Ø1.8" % (dd, EAR_PIN_LEN)))
for nm, x, y, w, h in LEGEND:
    plate = plate.cut(boxz(x, y, w, h, 0.5, 10.0, -20.0).intersect(cyl(R0)).cut(cyl(R0 - 0.6)))
tag = "" if ETH2 == "open" else "_eth2blank"
tag += TAG
step = os.path.join(HERE, "io_plate_v2_A0%s.step" % tag); stl = os.path.join(HERE, "io_plate_v2_A0%s.stl" % tag)
cq.exporters.export(plate, step); cq.exporters.export(plate, stl, tolerance=0.02, angularTolerance=0.1)
bb = plate.val().BoundingBox()
print("bbox", round(bb.xmin, 2), round(bb.xmax, 2), round(bb.ymin, 2), round(bb.ymax, 2), round(bb.zmin, 2), round(bb.zmax, 2), "vol", round(plate.val().Volume(), 1), "solids", len(plate.solids().vals()))

# ---------------- stack-up: required connector heights (board top -> mouth) ----------------
def u_out(x, hw): return abs(x - PL_C[0]) + hw
def zs_u(u): return -(CASE_R - math.sqrt(CASE_R ** 2 - u * u))
def zface_max(x, hw): return zs_u(u_out(x, hw))      # mouth flush at the outboard shell edge (lowest outer-surface point of the footprint)
def relief_floor_at(x, y):
    for rid, ri in relief_info.items():
        if abs(x - ri["cx"]) <= ri["w"] / 2 and abs(y - ri["cy"]) <= ri["h"] / 2: return ri["floor_z"], rid
    return None, None
STACK = []; TILT_CHECK = []
for oid, kind, x, y, w, h, r in OPEN:
    if kind == "AC": continue
    c = CUT[oid]; side = "H" if x < PL_C[0] else "O"
    if kind in TILT_KINDS:   # tilted riser: axis through the flex cut-out centre at the flex mid-plane; NOT necessarily normal to the plate
        tg = tilt_geom(oid, kind, x, y, w); n = tg["n"]; Mx, Mz = tg["M"]; sw, sh = tg["sw"], tg["sh"]
        hc = CONN_H[kind]; Bx, Bz = Mx - n[0] * hc, Mz - n[1] * hc               # riser top face at the connector centre
        _tc = dict(port=oid, tilt_deg=round(math.degrees(tg["ang"]), 2), surface_normal_deg=round(math.degrees(tg["surface_normal"]), 2),
                   off_normal_deg=round(math.degrees(tg["ang"] - tg["surface_normal"]), 2), axis_shift_x=tg["dx"],
                   flex_margin=tg["m"]["flex"], flex_margin_untilted=round((c["w"] - sw) / 2, 3), flex_margin_y=round((c["h"] - sh) / 2 - abs(y - c["cy"]), 3),
                   foam_margin=tg["m"]["foam"], frame_slot_margin=tg["m"]["frame"], plate_opening_margin=round((w - sw) / 2, 3),
                   overmold_standoff_no_seat=round(tg["stand0"], 2), overmold_standoff=round(tg["stand"], 2), seat=tg["seat"], seat_depth_max=round(tg["seat_depth"], 2))
        TILT_CHECK.append(_tc)
        STACK.append(dict(port=oid, kind=kind, x=round(x, 3), y=round(y, 3), tilt_deg=_tc["tilt_deg"], off_normal_deg=_tc["off_normal_deg"], axis_shift_x=tg["dx"],
                          mouth_centre=[round(Mx + PL_C[0], 3), round(Mz, 3)],
                          mouth_centre_height=round(Mz - Z_BOARD, 2), mouth_recess=round(tg["rec"], 2), mouth_recess_edges=[round(v, 2) for v in tg["rec_e"]],
                          plug_recess=round(tg["stand"], 2), plug_overmold_standoff=round(tg["stand"], 2), d0_at_port=round(d0(x), 3),
                          riser_top_centre=[round(Bx + PL_C[0], 3), round(Bz, 3)], riser_top_height=round(Bz - Z_BOARD, 2), riser_bottom_height=round(Bz - RISER_T * n[1] - Z_BOARD, 2),
                          conn_h=hc, shell_in_flex_cutout_margin=round(min(tg["m"]["flex"] + [_tc["flex_margin_y"]]), 2), part=PARTS[kind]["mpn"], part_h=PARTS[kind]["h"],
                          required_height=round(Mz - Z_BOARD, 2), riser_needed=None, relief=None,
                          overmold_standoff_no_seat=_tc["overmold_standoff_no_seat"],
                          seat_floor=([[round(tg["P0"][0] + tg["t_seat"] * n[0] + sg * tg["seat_w"] / 2 * tg["ex"][0] + PL_C[0], 3),
                                        round(tg["P0"][1] + tg["t_seat"] * n[1] + sg * tg["seat_w"] / 2 * tg["ex"][1], 3)] for sg in (-1, 1)] if tg["seat"] else None)))
        continue
    if kind in ("USBC", "USBA", "HDMI"):
        sw, sh = SHELL[kind]["shell"]; ow, oh = SHELL[kind]["overmold"]
        z_m = zface_max(x, sw / 2)
        u_in = max(abs(x - PL_C[0]) - ow / 2, 0.0)
        zr, rid = relief_floor_at(x, y)
        z_om = zs_u(u_in) if zr is None else max(zr, zs_u(abs(x - PL_C[0]) + ow / 2))
        req = z_m - Z_BOARD; part = PARTS[kind]
        sm = min((c["w"] - sw) / 2 - abs(x - c["cx"]), (c["h"] - sh) / 2 - abs(y - c["cy"]))
        STACK.append(dict(port=oid, kind=kind, x=round(x, 3), y=round(y, 3), mouth_z=round(z_m, 3), d0_at_port=round(d0(x), 3), required_height=round(req, 2),
                          plug_overmold_stop_z=round(z_om, 3), plug_recess=round(z_om - z_m, 2), relief=rid, shell_in_flex_cutout_margin=round(sm, 2),
                          part=part["mpn"], part_h=part["h"], riser_needed=round(req - part["h"], 2)))
    else:   # RJ45: body cannot pass the frame slot or the flex cut-out -> face behind the frame back plane
        bw, bh = SHELL["RJ45"]["body"]
        z_frame_back = zi_u = zs_u(u_out(x, bw / 2)) - SKIN + FLEX_POCKET - PSA_T - FLEX_T - FOAM_T - FRAME_T
        zf = z_frame_back - 0.3
        pw, ph = SHELL["RJ45"]["plug"]
        sm = min((c["w"] - pw) / 2 - abs(x - c["cx"]), (c["h"] - ph) / 2 - abs(y - c["cy"]))
        STACK.append(dict(port=oid, kind=kind, x=round(x, 3), y=round(y, 3), face_z_max=round(zf, 3), max_height=round(zf - Z_BOARD, 2), plug_in_flex_cutout_margin=round(sm, 2),
                          note="jack body 16.2 x 17.0 cannot pass the frame slot (H: SMALL_R2 15.6 x 13.0; O: BIG_L leg X 54.2-70.9, Y 85.3-115.5) nor the flex cut-out: face >= 0.3 behind the frame back plane",
                          part=PARTS["RJ45"]["mpn"], part_h=PARTS["RJ45"]["h"]))
# HDMI fallback if the receptacle shell does not pass the 5.83 flex cut-out
hd = [s for s in STACK if s["port"] == "HDMI"][0]
hd["fallback_face_behind_flex_max_height"] = round(zs_u(u_out(hd["x"], SHELL["HDMI"]["shell"][0] / 2)) - SKIN + FLEX_POCKET - PSA_T - FLEX_T - 0.1 - Z_BOARD, 2)
for s in STACK: print("STACK", s)
for t in TILT_CHECK: print("TILTCHECK", t)

# ---------------- flex check: shells/plugs vs cut-outs, LEDs vs plate features ----------------
def margins(cx, cy, w, h, c):
    return dict(xm=round((cx - w / 2) - (c["cx"] - c["w"] / 2), 2), xp=round((c["cx"] + c["w"] / 2) - (cx + w / 2), 2),
                ym=round((cy - h / 2) - (c["cy"] - c["h"] / 2), 2), yp=round((c["cy"] + c["h"] / 2) - (cy + h / 2), 2))
THRU = {"USBC": SHELL["USBC"]["shell"], "USBA": SHELL["USBA"]["shell"], "HDMI": SHELL["HDMI"]["shell"], "RJ45": SHELL["RJ45"]["plug"]}
FLEX_CHECK = []
for oid, kind, x, y, w, h, r in OPEN:
    if oid not in CUT: continue
    c = CUT[oid]; tw, th = THRU[kind]
    mt = margins(x, y, tw, th, c); mo = margins(x, y, w, h, c)
    FLEX_CHECK.append(dict(port=oid, flex_cutout=dict(cx=c["cx"], cy=c["cy"], w=c["w"], h=c["h"]), offset=[round(x - c["cx"], 2), round(y - c["cy"], 2)],
                           through=("plug" if kind == "RJ45" else "receptacle shell"), through_size=[tw, th], through_min_margin=min(mt.values()), plate_opening_min_margin=min(mo.values()),
                           boss=None, inner_face="flush (no boss)"))
for aid in ("AUD_H", "AUD_O"):
    c = CUT[aid]; o = [q for q in ROUND if q[0] == aid][0]; off = math.hypot(o[1] - c["cx"], o[2] - c["cy"])
    FLEX_CHECK.append(dict(port=aid, flex_cutout=dict(cx=c["cx"], cy=c["cy"], d=c["d"]), offset=[round(o[1] - c["cx"], 2), round(o[2] - c["cy"], 2)],
                           through="Ø4.8 opening / jack nose (Ø6.0 assumed)", through_min_margin=round(c["d"] / 2 - 4.8 / 2 - off, 2), jack_nose_margin=round(c["d"] / 2 - 3.0 - off, 2), boss=None, inner_face="flush (no boss)"))
for hid, (pid, px_, py_, pd) in (("HOLE_C1", LOCATE_PINS[0]), ("PIN_C3", LOCATE_PINS[1])):
    hh = [q for q in FJ["holes"] if q["id"] == hid][0]
    FLEX_CHECK.append(dict(port=pid, flex_hole=hh, pin_d=pd, radial_margin=round(hh["d"] / 2 - pd / 2 - math.hypot(px_ - hh["cx"], py_ - hh["cy"]), 2)))
# LEDs against plate features (rectangles grown by LED_CLR; circles by radius)
def rect_hit(l, x, y, w, h, g=0.0):
    return abs(l["cx"] - x) < (l["w"] + w) / 2 + g and abs(l["cy"] - y) < (l["h"] + h) / 2 + g
LED_CHECK = []
feats = [(o[0], o[2], o[3], o[4], o[5]) for o in OPEN] + [(q[0], q[1], q[2], q[3], q[3]) for q in ROUND] + [(q[0], q[1], q[2], q[3], q[4]) for q in WINDOWS] + \
        [(q[0], q[1], q[2], q[3] + 0.6, q[3] + 0.6) for q in LOCATE_PINS + EAR_PINS] + [("FRAME_SCREW_RELIEF", FRAME_SCREW[0], FRAME_SCREW[1], SCREW_POCKET_D, SCREW_POCKET_D)] + \
        [("CLIP", x, y, (CLIP_T + 2 * CLIP_HOOK) if o[0] == "x" else CLIP_W, CLIP_W if o[0] == "x" else CLIP_T + 2 * CLIP_HOOK) for x, y, o in CLIPS] + \
        [("RIM_NECK_NOTCH", (NECK[0] + NECK[2]) / 2, (NECK[1] + NECK[3]) / 2, NECK[2] - NECK[0], NECK[3] - NECK[1])]
for k, l in enumerate(FJ["leds"]):
    hits = [f[0] for f in feats if rect_hit(l, f[1], f[2], f[3], f[4], LED_CLR)]
    in_rim = (l["cx"] - l["w"] / 2 < PL_C[0] - PL_W / 2 + RIM_W + 0.3) or (l["cx"] + l["w"] / 2 > PL_C[0] + PL_W / 2 - RIM_W - 0.3)
    rel = [rid for rid, ri in relief_info.items() if rect_hit(l, ri["cx"], ri["cy"], ri["w"], ri["h"], LED_CLR)]
    btn = math.hypot(l["cx"] - BTN["cx"], l["cy"] - BTN["cy"]) < BTN["ring_d"] / 2
    if btn: hits = [h_ for h_ in hits if h_ != "PWR_BTN"]   # button LEDs sit under the button cap by design (they light it)
    LED_CHECK.append(dict(led=k, cx=l["cx"], cy=l["cy"], w=l["w"], h=l["h"], conflicts=hits + (["RIM"] if in_rim else []) + rel, in_button_pocket=btn,
                          ok=not (hits or in_rim or rel)))
for row in FLEX_CHECK: print("FLEXCHECK", row)
for row in LED_CHECK:
    if not row["ok"]: print("LED CONFLICT", row)

# ---------------- trace DXF, foam DXF, check image (ETH2 open build only) ----------------
def rr_pts(cx, cy, w, h, r, n=9):
    r = min(r, w / 2, h / 2); pts = []
    for (ax_, ay_, a0) in ((cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)):
        for k in range(n):
            t = math.radians(a0 + 90 * k / (n - 1)); pts.append((ax_ + r * math.cos(t), ay_ + r * math.sin(t)))
    return pts
if ETH2 == "open" and not TAG:
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for ln, col in (("FLEX_OUTLINE", 30), ("FLEX_CUTOUTS", 30), ("FLEX_HOLES", 30), ("FLEX_LIGHT_PADS", 5), ("FLEX_LEDS", 2), ("FLEX_BUTTON", 6), ("FLEX_TAIL", 8), ("FLEX_CONTACTS", 40),
                    ("FLEX_SILVER_FRAMES", 9), ("IGNORED_BLACK_TAB", 251), ("REF_PLATE_OUTLINE", 7), ("REF_PLATE_OPENINGS", 7), ("REF_LIGHT_WINDOWS", 2), ("REF_LED_POCKETS", 1), ("NOTES", 7)):
        doc.layers.add(ln, color=col)
    def rr(cx, cy, w, h, r, layer): msp.add_lwpolyline(rr_pts(cx, cy, w, h, r), close=True, dxfattribs={"layer": layer})
    msp.add_lwpolyline(FLEX_POLY, close=True, dxfattribs={"layer": "FLEX_OUTLINE"})
    msp.add_lwpolyline([tuple(p) for p in FJ["tail"]], close=True, dxfattribs={"layer": "FLEX_TAIL"})
    ce = FJ["contact_end"]; cc = ce["contacts"]
    for k in range(cc["n"]):
        x0 = (cc["x"][0] + cc["x"][1]) / 2 - (cc["n"] - 1) * cc["pitch"] / 2 + k * cc["pitch"]
        msp.add_lwpolyline([(x0 - 0.15, cc["y"][0]), (x0 + 0.15, cc["y"][0]), (x0 + 0.15, cc["y"][1]), (x0 - 0.15, cc["y"][1])], close=True, dxfattribs={"layer": "FLEX_CONTACTS"})
    it = FJ["ignored_tab"]; rr((it["x"][0] + it["x"][1]) / 2, (it["y"][0] + it["y"][1]) / 2, it["x"][1] - it["x"][0], it["y"][1] - it["y"][0], 0.5, "IGNORED_BLACK_TAB")
    for c in FJ["cutouts"]:
        if "d" in c: msp.add_circle((c["cx"], c["cy"]), c["d"] / 2, dxfattribs={"layer": "FLEX_CUTOUTS"})
        else: rr(c["cx"], c["cy"], c["w"], c["h"], c["r"], "FLEX_CUTOUTS")
        msp.add_text(c["id"], dxfattribs={"layer": "NOTES", "height": 1.0}).set_placement((c["cx"] - 1.5, c["cy"]))
    for hh in FJ["holes"]: msp.add_circle((hh["cx"], hh["cy"]), hh["d"] / 2, dxfattribs={"layer": "FLEX_HOLES"})
    for p in FJ["light_pads"]: rr(p["cx"], p["cy"], p["w"], p["h"], 0.3, "FLEX_LIGHT_PADS"); msp.add_text(p["id"], dxfattribs={"layer": "NOTES", "height": 0.8}).set_placement((p["cx"] - 2, p["cy"] + p["h"] / 2 + 0.3))
    for l in FJ["leds"]: rr(l["cx"], l["cy"], l["w"], l["h"], 0.05, "FLEX_LEDS"); rr(l["cx"], l["cy"], l["w"] + 2 * LED_CLR, l["h"] + 2 * LED_CLR, 0.3, "REF_LED_POCKETS")
    for f in FJ["silver_frames"]: rr(f["cx"], f["cy"], f["w"], f["h"], 0.5, "FLEX_SILVER_FRAMES")
    msp.add_circle((BTN["cx"], BTN["cy"]), BTN["ring_d"] / 2, dxfattribs={"layer": "FLEX_BUTTON"}); msp.add_circle((BTN["cx"], BTN["cy"]), BTN["dome_d"] / 2, dxfattribs={"layer": "FLEX_BUTTON"})
    rr(PL_C[0], PL_C[1], PL_W, PL_H, PL_R, "REF_PLATE_OUTLINE")
    for oid, kind, x, y, w, h, r in OPEN: rr(x, y, w, h, r, "REF_PLATE_OPENINGS")
    for oid, x, y, dd in ROUND: msp.add_circle((x, y), dd / 2, dxfattribs={"layer": "REF_PLATE_OPENINGS"})
    for wid, x, y, w, h, r in WINDOWS: rr(x, y, w, h, r, "REF_LIGHT_WINDOWS")
    msp.add_text("821-2222-A I/O-wall flex trace (plate-facing side, back view, mm) from Aidan flatbed scan 06ea8deb (200 dpi, ruler-calibrated, idealised); +-0.15; VERIFY by caliper",
                 dxfattribs={"layer": "NOTES", "height": 1.6}).set_placement((20, -26))
    doc.saveas(os.path.join(HERE, "flex_821-2222_trace.dxf"))
    # foam / insulator die-cut (board side of the flex): flex outline, minus cut-outs + 0.3, minus holes + 0.5, minus the button ring + 0.5
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for ln in ("CUT_OUTER", "CUT_INNER", "NOTES"): doc.layers.add(ln)
    msp.add_lwpolyline(FLEX_POLY, close=True, dxfattribs={"layer": "CUT_OUTER"})
    for c in FJ["cutouts"]:
        if "d" in c: msp.add_circle((c["cx"], c["cy"]), c["d"] / 2 + 0.3, dxfattribs={"layer": "CUT_INNER"})
        else: msp.add_lwpolyline(rr_pts(c["cx"], c["cy"], c["w"] + 0.6, c["h"] + 0.6, c["r"] + 0.3), close=True, dxfattribs={"layer": "CUT_INNER"})
    for hh in FJ["holes"]:
        if not hh["id"].startswith("BTN_EAR"): msp.add_circle((hh["cx"], hh["cy"]), hh["d"] / 2 + 0.5, dxfattribs={"layer": "CUT_INNER"})
    msp.add_circle((BTN["cx"], BTN["cy"]), BTN["ring_d"] / 2 + 0.5, dxfattribs={"layer": "CUT_INNER"})
    msp.add_text("MP62 IO flex foam / insulator A0 (back view, mm, scan-based outline): 1.0 PE/PORON foam with PSA (stock-like) OR 0.25 Formex GK-10; laser/die cut; VERIFY against the flex",
                 dxfattribs={"layer": "NOTES", "height": 1.6}).set_placement((20, -12))
    doc.saveas(os.path.join(HERE, "io_flex_foam_insulator_A0.dxf"))
    # check image
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly, Circle as MCirc, Rectangle as MRect, FancyBboxPatch as FBP
    fig, ax = plt.subplots(figsize=(9.5, 15))
    ax.add_patch(FBP((PL_C[0] - PL_W / 2 + PL_R, PL_C[1] - PL_H / 2 + PL_R), PL_W - 2 * PL_R, PL_H - 2 * PL_R, boxstyle="round,pad=%g" % PL_R, fc="#f4f4f4", ec="k", lw=0.8))
    ax.add_patch(MPoly(FLEX_POLY, fc="#ffd98a", ec="#c07000", lw=0.8))
    ax.add_patch(MPoly([tuple(p) for p in FJ["tail"]], fc="#ffe9b8", ec="#c07000", lw=0.6))
    ax.add_patch(MRect((it["x"][0], it["y"][0]), it["x"][1] - it["x"][0], it["y"][1] - it["y"][0], fc="#dddddd", ec="#888888", ls="--", lw=0.6)); ax.text((it["x"][0] + it["x"][1]) / 2, (it["y"][0] + it["y"][1]) / 2, "black tab\n(ignored)", fontsize=6, ha="center", color="#666666")
    ax.add_patch(MRect((ce["x"][0], ce["y"][0]), ce["x"][1] - ce["x"][0], ce["y"][1] - ce["y"][0], fc="#e0a040", ec="#805000", lw=0.6))
    for c in FJ["cutouts"]:
        ax.add_patch(MCirc((c["cx"], c["cy"]), c["d"] / 2, fc="w", ec="#c07000") if "d" in c else MPoly(rr_pts(c["cx"], c["cy"], c["w"], c["h"], c["r"]), fc="w", ec="#c07000"))
    for hh in FJ["holes"]: ax.add_patch(MCirc((hh["cx"], hh["cy"]), hh["d"] / 2, fc="w", ec="#c07000"))
    for p in FJ["light_pads"]: ax.add_patch(MRect((p["cx"] - p["w"] / 2, p["cy"] - p["h"] / 2), p["w"], p["h"], fc="#b8c8ff", ec="b", lw=0.5))
    for row, l in zip(LED_CHECK, FJ["leds"]): ax.add_patch(MRect((l["cx"] - l["w"] / 2, l["cy"] - l["h"] / 2), l["w"], l["h"], fc="#fff200" if row["ok"] else "#ff3030", ec="k", lw=0.3))
    ax.add_patch(MCirc((BTN["cx"], BTN["cy"]), BTN["ring_d"] / 2, fc="none", ec="m", lw=0.8))
    for k, v in fr.items():
        if k.startswith(("SQ", "TALL", "SMALL", "ROUND", "BIG")): ax.add_patch(MRect((v["cx"] - v["w"] / 2, v["cy"] - v["h"] / 2), v["w"], v["h"], fc="none", ec="g", lw=0.6, ls=":"))
    for oid, kind, x, y, w, h, r in OPEN: ax.add_patch(MPoly(rr_pts(x, y, w, h, r), fc="none", ec="k", lw=0.6))
    for s in STACK:
        if "shell_in_flex_cutout_margin" in s:
            sw, sh = SHELL[s["kind"]]["shell"]; ax.add_patch(MRect((s["x"] - sw / 2, s["y"] - sh / 2), sw, sh, fc="none", ec="r", lw=0.7, ls="--"))
    for oid, x, y, dd in ROUND: ax.add_patch(MCirc((x, y), dd / 2, fc="none", ec="k", lw=0.6))
    for wid, x, y, w, h, r in WINDOWS: ax.add_patch(MRect((x - w / 2, y - h / 2), w, h, fc="#ffff80", ec="k", lw=0.6))
    for pid, x, y, dd in LOCATE_PINS + EAR_PINS: ax.add_patch(MCirc((x, y), dd / 2, fc="#4040ff", ec="k", lw=0.4))
    for x, y, o in CLIPS: ax.plot(x, y, "b^", ms=6)
    for x, y, o in dropped_clips: ax.plot(x, y, "rx", ms=9, mew=2)
    for row in FLEX_CHECK:
        if "flex_cutout" not in row: continue
        c = row["flex_cutout"]; st = [s for s in STACK if s["port"] == row["port"]]
        ht = ("\nH %.2f" % st[0]["required_height"]) if st and "required_height" in st[0] else (("\nH<=%.1f" % st[0]["max_height"]) if st else "")
        ax.text(c["cx"], c["cy"] - (1.2 if "d" in c else 0), "%s\n%+.2f%s" % (row["port"], row["through_min_margin"], ht), fontsize=5, ha="center", va="center", color="darkred")
    ax.set_xlim(22, 120); ax.set_ylim(-24, 160); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_title("821-2222-A flex (scan trace) vs plate v2 A0, back view, mm.  Inner face flush: no bosses, flex sits flat.\n"
                 "orange = flex, white = flex cut-outs/holes, black = plate openings, red dashed = receptacle shells, green dotted = metal frame slots,\n"
                 "blue pads = light guides, yellow chips = LEDs (red = conflict), yellow = light windows, blue dots = pins.\n"
                 "label: min margin of shell/plug in the flex cut-out, H = required board-top-to-mouth height (RJ45: max)", fontsize=6.5)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "flex_821-2222_check.png"), dpi=170); plt.close(fig)

# ---------------- DXF (openings, back view and front view), features JSON, previews ----------------
if ETH2 == "open" and TAG:
    json.dump(dict(params=dict(case_r=round(CASE_R, 3), tag=TAG, d0=dict(board_top_z=Z_BOARD)), parts=PARTS, tilt=dict(override_deg=TILT_OVERRIDE_DEG, check=TILT_CHECK), stack=STACK),
              open(os.path.join(HERE, "io_plate_v2_A0%s_features.json" % TAG), "w"), indent=1)
if ETH2 == "open" and not TAG:
    for view in ("backview", "frontview"):
        BW = 101.00496445740619
        fx = (lambda x: x) if view == "backview" else (lambda x: 40 + BW - x)   # front view = KiCad PCB frame x (y kept = Y; KiCad y = 200 - Y)
        doc = ezdxf.new("R2010"); msp = doc.modelspace()
        for ln in ("OUTLINE", "OPENINGS", "LIGHT_WINDOWS", "SPOTFACES", "CLIPS", "PINS", "NOTES"): doc.layers.add(ln)
        def rrect(cx, cy, w, h, r, layer): msp.add_lwpolyline([(fx(a), b) for a, b in rr_pts(cx, cy, w, h, r)], close=True, dxfattribs={"layer": layer})
        rrect(PL_C[0], PL_C[1], PL_W, PL_H, PL_R, "OUTLINE")
        for oid, kind, x, y, w, h, r in OPEN:
            rrect(x, y, w, h, r, "OPENINGS"); msp.add_text(oid, dxfattribs={"layer": "NOTES", "height": 1.2}).set_placement((fx(x) - 2, y + h / 2 + 0.6))
        for oid, x, y, dd in ROUND: msp.add_circle((fx(x), y), dd / 2, dxfattribs={"layer": "OPENINGS"})
        for wid, x, y, w, h, r in WINDOWS: rrect(x, y, w, h, r, "LIGHT_WINDOWS")
        for rid, x, y, w, h, r in RELIEF: rrect(x, y, w, h, r, "SPOTFACES")
        for x, y, o in CLIPS: msp.add_circle((fx(x), y), 1.0, dxfattribs={"layer": "CLIPS"})
        for pid, x, y, dd in LOCATE_PINS + EAR_PINS: msp.add_circle((fx(x), y), dd / 2, dxfattribs={"layer": "PINS"})
        msp.add_text("MP62 IO plate v2 A0 - %s - mm - Y up = MEG/base end" % view, dxfattribs={"layer": "NOTES", "height": 2}).set_placement((fx(PL_C[0]) - 30, -12))
        doc.saveas(os.path.join(HERE, "io_plate_v2_A0_openings_%s.dxf" % view))
    json.dump(dict(params=dict(outline=dict(centre=PL_C, w=PL_W, h=PL_H, r=PL_R), case_r=round(CASE_R, 3), r_inner=round(R_INNER, 3), skin=SKIN, rim_h=RIM_H, rim_w=RIM_W,
                               d0=dict(crown=D0_CROWN, edge=D0_EDGE, edge_u=D0_EDGE_U, board_top_z=Z_BOARD, note="board top -> plate inner face; 16.5 read at the outer edge of the outermost port columns (Aidan 10:21 ET)"),
                               cover_scan=dict(file="../io_cover_scan/io_cover_scan_check.json", R_inner_fit=101.7, scale=0.931, opening_rms=0.49,
                                               outline_width=52.4, outline_length=160.3, verdict="2D layout confirmed (+-0.5); R 100-110 consistent; ends, clips, pins, wall below resolution -> geometry unchanged"),
                               clip=dict(t=CLIP_T, w=CLIP_W, l=CLIP_L, hook=CLIP_HOOK), port_grid=dict(usbc_x=[XH, XO], source="flex 821-2222-A cut-out centres (scan)"),
                               flex=dict(flex_t=FLEX_T, psa_t=PSA_T, foam_t=FOAM_T, frame_t=FRAME_T, pocket=FLEX_POCKET, pocket_clr=FLEX_CLR, neck_notch=NECK, led_h=LED_H, led_clr=LED_CLR,
                                         btn_carrier_h=BTN_CARRIER_H, inner_face="smooth cylinder, no bosses")),
                   parts=PARTS, tilt=dict(override_deg=TILT_OVERRIDE_DEG, source="M-IOT2 Aidan 2026-10-02 11:47 ET: outward 12.5 deg, mirrored" if TILT_OVERRIDE_DEG else "surface normal (D-IO16 default: full plug seating; stock 12.5 in io_plate_v2_A0_tilt12p5_features.json)", mouth_clr=MOUTH_CLR, axis_balance=AXIS_BALANCE, axis_shift_out=AXIS_SHIFT_OUT, seat=TILT_SEAT, seat_clr=SEAT_CLR, seat_min_wall=SEAT_MIN_WALL, check=TILT_CHECK), stack=STACK, spotfaces=relief_info, flex_check=FLEX_CHECK, led_check=LED_CHECK,
                   features=[dict(id=a, kind=b, x=round(c, 3), y=round(d, 3), w=e, h=f, note=g) for a, b, c, d, e, f, g in report], clips=CLIPS),
              open(os.path.join(HERE, "io_plate_v2_A0_features.json"), "w"), indent=1)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Circle
    fig, ax = plt.subplots(figsize=(6, 13))
    ax.add_patch(FancyBboxPatch((PL_C[0] - PL_W / 2 + PL_R, PL_C[1] - PL_H / 2 + PL_R), PL_W - 2 * PL_R, PL_H - 2 * PL_R, boxstyle="round,pad=%g" % PL_R, fc="#dddddd", ec="k"))
    for rid, x, y, w, h, r in RELIEF: ax.add_patch(FancyBboxPatch((x - w / 2 + r, y - h / 2 + r), w - 2 * r, h - 2 * r, boxstyle="round,pad=%g" % r, fc="#c8c8c8", ec="#777777", ls="--"))
    for oid, tg in _TG.items():
        if tg["seat"]:
            cx_ = tg["P0"][0] + tg["t_seat"] * tg["n"][0] + PL_C[0]; cy_ = CUT[oid]["cy"]; sw_, sh_ = tg["seat_w"] * math.cos(tg["ang"]), tg["seat_h"]
            ax.add_patch(FancyBboxPatch((cx_ - sw_ / 2 + 1.0, cy_ - sh_ / 2 + 1.0), sw_ - 2.0, sh_ - 2.0, boxstyle="round,pad=1.0", fc="#cfc4e6", ec="m", ls="--", lw=0.6))
    for oid, kind, x, y, w, h, r in OPEN:
        ax.add_patch(FancyBboxPatch((x - w / 2 + r, y - h / 2 + r), w - 2 * r, h - 2 * r, boxstyle="round,pad=%g" % r, fc="white", ec="k"))
        ax.text(x, y, oid, ha="center", va="center", fontsize=6)
    for oid, x, y, dd in ROUND: ax.add_patch(Circle((x, y), dd / 2, fc="white", ec="k"))
    ax.text(BTN["cx"], BTN["cy"], "button\n(cap on the\nflex dome)", ha="center", va="center", fontsize=5)
    for wid, x, y, w, h, r in WINDOWS: ax.add_patch(FancyBboxPatch((x - w / 2 + r, y - h / 2 + r), w - 2 * r, h - 2 * r, boxstyle="round,pad=%g" % r, fc="yellow", ec="k"))
    for x, y, o in CLIPS: ax.plot(x, y, "b^", ms=5)
    ax.set_xlim(20, 86); ax.set_ylim(-8, 162); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_title("IO plate v2 A0, OUTER face (back view)\nyellow = light windows, blue = clips, violet = flat plug seats; USB-C/USB-A/HDMI holes along the port-module axes (%s)" % ("%.1f deg" % TILT_OVERRIDE_DEG if TILT_OVERRIDE_DEG else "normal to the plate"), fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "io_plate_v2_A0_outer.png"), dpi=150); plt.close(fig)
    iso = plate.translate((-PL_C[0], -PL_C[1], 0)).rotate((0, 0, 0), (0, 0, 1), 90).rotate((0, 0, 0), (1, 0, 0), 180)
    cq.exporters.export(iso, os.path.join(HERE, "_iso.svg"), opt={"projectionDir": (0.25, -0.45, 1.0), "showHidden": False, "width": 1600, "height": 700,
                                                                 "marginLeft": 40, "marginTop": 40, "strokeWidth": 0.15})
for row in report: print(row)
