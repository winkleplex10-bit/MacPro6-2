#!/usr/bin/env python3
"""MP62 I/O plate v2 rev A0 (new plastic plate; stock metal I/O frame stays). cadquery 2.8 + ezdxf.
Frame: stock BACK-VIEW frame of the I/O board (mm): origin at the board's bottom-left virtual corner, X to the right as seen
from behind the machine, Y up toward the MEG-array / base end. Z = 0 is the plate OUTER (visible) face, -Z goes into the
machine toward the I/O frame and the board.
Tilt handling = option (a): standard flat connectors; the plate absorbs any board-to-plate tilt with per-opening collars
(USB-A / RJ45 / HDMI) and outer spot-faces (USB-C) computed from TILT_AX_DEG / TILT_AY_DEG (set them from measurement
M-IOT1; both 0 until measured).  Usage: python build_plate.py [--eth2 open|blank] [--flex stock|none]
Rev 2026-10-02 ~09:10 ET (Aidan photos of the stock plate inside + the 821-2222 flex laid flat):
  * inner face = concentric cylinder R0 - SKIN (constant 1.2 wall); flat port lands are recessed pockets on the outside, backed by
    bosses on the inside (inboard edges ramped so a flex can drape over them);
  * FLEX = "stock": plate carries the I/O-wall flex 821-2222 (or the A1 replacement flex with the same outline) glued in a 0.2 mm
    pocket on the inner skin; no collars, no light-pipe bosses (the metal frame centre bar blocks board-side light pipes);
    light windows over the flex light-guide pads; rim notch for the flex neck; clips that collide with the flex are dropped."""
import json, math, os, sys
import cadquery as cq
import ezdxf
HERE = os.path.dirname(os.path.abspath(__file__))
ETH2 = "open"    # rev A0 default since 2026-10-02 (D-IO2: 2 x i226-V); "--eth2 blank" builds the old blank variant
if "--eth2" in sys.argv: ETH2 = sys.argv[sys.argv.index("--eth2") + 1]
FLEX = "stock"   # "stock": I/O-wall flex 821-2222 outline glued to the inner face (rev A0 default since 2026-10-02 09:10 ET); "none": old collars
if "--flex" in sys.argv: FLEX = sys.argv[sys.argv.index("--flex") + 1]
FJ = json.load(open(os.path.join(HERE, "flex_821-2222_trace.json")))
FLEX_T, PSA_T = 0.12, 0.05     # flex (polyimide + cover) and its PSA [Estimate, TO MEASURE]
FOAM_T = 1.0                    # stock foam over the flex, board side [Aidan ~1 mm, TO MEASURE]
FLEX_POCKET = 0.20              # glue pocket depth into the inner skin (leaves 1.0 of the 1.2 wall)
FLEX_CLR = 0.30                 # pocket outline = flex outline + this
RAMP_MIN_DEG = 45.0             # boss inboard ramp, steepened until >= 0.8 mm stays under the land edge

# ---------------- parameters ----------------
PL_C = (53.19, 77.07); PL_W, PL_H, PL_R = 51.9, 163.1, 11.5      # outline (fit of the stock plate scan; straight width 51.89)
SKIN = 1.2; RIM_H = 3.0; RIM_W = 1.2                             # skin, inner perimeter rim (tray)
TILT_AX_DEG = 0.0   # + = board farther from the plate outer face as Xb increases   (from M-IOT1)
TILT_AY_DEG = 0.0   # + = board farther from the plate outer face as Y increases    (from M-IOT1)
TILT_REF = (53.2, 65.45)                                          # pivot: centre of the USB-C block
COLLAR_L0 = 1.0; COLLAR_WALL = 1.0                               # nominal collar length behind the skin, wall
COLLAR_WALL_BY = {"ETH2": 0.8}   # ETH2 collar 14.6 x 12.3 must pass the 15.6 x 13.0 H-side frame slot
ETH_GUIDE_L = {"ETH2": COLLAR_L0}   # plug-guide length behind the land; extend toward the set-back jack face after M-IOF2 (stop 0.3 short of it)
USBC_FLUSH_TOL = 0.15                                            # spot-face only if a USB-C mouth would sit deeper than this
CLR = 0.3                                                        # design clearance per side already included in the sizes below
XH, XO = 42.6, 63.9; CROWS = (75.2, 65.45, 55.7)
OPEN = []   # (id, kind, cx, cy, w, h, r)
for i, y in enumerate(CROWS):
    OPEN.append(("C%d" % (i + 1), "USBC", XH, y, 9.6, 4.0, 1.8))
    OPEN.append(("C%d" % (i + 4), "USBC", XO, y, 9.6, 4.0, 1.8))
for n, (x, y) in zip(("A1", "A2", "A3", "A4"), ((43.3, 42.75), (43.3, 32.6), (64.05, 42.75), (64.05, 32.6))):
    OPEN.append((n, "USBA", x, y, 13.6, 6.0, 0.5))
OPEN.append(("ETH1", "RJ45", 63.5, 92.3, 13.0, 10.7, 0.5))
if ETH2 == "open": OPEN.append(("ETH2", "RJ45", 42.5, 92.0, 13.0, 10.7, 0.5))
OPEN.append(("HDMI", "HDMI", 42.4, 107.4, 15.4, 6.0, 0.8))
OPEN.append(("AC", "AC", 52.08, 129.95, 34.55, 24.65, 3.0))
ROUND = [("AUD_H", 43.4, 19.1, 4.8), ("AUD_O", 64.65, 19.4, 4.8), ("PWR_BTN", 63.02, 108.03, 12.4)]
PIPES = [("LP_HDMI", 46.2, 115.6), ("LP_ETH", 52.95, 92.9), ("LP_USBC_U", 53.25, 70.4), ("LP_USBC_L", 53.25, 62.6), ("LP_USB", 53.7, 49.4), ("LP_AUDIO", 53.8, 21.0)]
PIPE_BORE, PIPE_OD, PIPE_L = 2.2, 4.4, 2.0   # bore for a 2.0 mm PMMA rod / Bivar-type pipe; 1.1 mm wall
PADS = {p["id"]: p for p in FJ["light_pads"]}
# light windows through the skin over the flex light-guide pads (flex mode); (id, cx, cy, w, h, r) - VERIFY against the stock icon art
WINDOWS = [("W_HDMI", PADS["PAD_HDMI"]["cx"], PADS["PAD_HDMI"]["cy"], 7.0, 1.6, 0.6), ("W_ETH", PADS["PAD_ETH"]["cx"], PADS["PAD_ETH"]["cy"], 3.0, 5.0, 1.0),
           ("W_TB", PADS["PAD_TB"]["cx"], PADS["PAD_TB"]["cy"], 3.0, 5.0, 1.0), ("W_USB", PADS["PAD_USB"]["cx"], PADS["PAD_USB"]["cy"], 3.0, 6.0, 1.0),
           ("W_AUD_H", PADS["PAD_AUD_H"]["cx"], PADS["PAD_AUD_H"]["cy"], 4.0, 2.4, 0.8), ("W_AUD_O", PADS["PAD_AUD_O"]["cx"], PADS["PAD_AUD_O"]["cy"], 4.0, 2.4, 0.8)]
if FLEX == "stock": PIPES = []
else: WINDOWS = []
CLIPS_L = [(31.0, 140.0), (28.2, 90.0), (29.6, 30.3)]           # stock clip points (left), mirrored about the plate centre X
CLIP_B = [(44.1, 2.7)]
CLIPS = [(x, y, "x-") for x, y in CLIPS_L] + [(2 * PL_C[0] - x, y, "x+") for x, y in CLIPS_L] + \
        [(x, y, "y-") for x, y in CLIP_B] + [(2 * PL_C[0] - x, y, "y-") for x, y in CLIP_B]
CLIP_T, CLIP_W, CLIP_L, CLIP_HOOK = 1.2, 5.0, 6.0, 0.5   # MJF PA12: strain ~1.5*t*y/L^2 = 2.5 %
FRAME_SCREW = (53.38, 58.38); SCREW_POCKET_D, SCREW_POCKET_DEPTH = 6.0, 0.6     # frame centre screw head relief (M-IOF2)
LEGEND = [("blank ETH2 recess", 42.5, 92.0, 13.0, 10.7)] if ETH2 == "blank" else []


# ---- curvature (stock I/O wall follows the case cylinder; Aidan 2026-10-01 photo: shells fan outward ~6.5-7.5 deg per column) ----
CASE_R = 82.0          # outer-face radius about an axis parallel to Y through X = PL_C[0]; None = flat plate.  MEASURE M-IOT2.
LAND_T = 1.0           # material thickness under every flat port land
LANDS = [  # (id, cx, cy, w, h, r, border-to-boss)  flat lands parallel to the BOARD (straight connectors), one per port group
    ("LAND_C_H", XH, 65.45, 10.6, 24.5, 1.5, 0.6), ("LAND_C_O", XO, 65.45, 10.6, 24.5, 1.5, 0.6),
    ("LAND_A_H", 43.3, 37.675, 15.6, 18.15, 1.0, 0.6), ("LAND_A_O", 64.05, 37.675, 15.6, 18.15, 1.0, 0.6),
    ("LAND_ETH1", 63.5, 92.3, 14.2, 11.9, 1.0, 0.6), ("LAND_HDMI", 42.4, 107.4, 16.6, 7.2, 1.0, 0.6),
    ("LAND_AUD_H", 43.4, 19.1, 7.0, 7.0, 3.5, 0.6), ("LAND_AUD_O", 64.65, 19.4, 7.0, 7.0, 3.5, 0.6)]
if ETH2 == "open": LANDS.append(("LAND_ETH2", 42.5, 92.0, 13.8, 11.4, 1.0, 0.5))
if FLEX == "stock":   # audio bosses must pass the flex's Ø7.4 / Ø7.5 audio holes: land Ø6.4 + 0.3 border = Ø7.0
    LANDS = [(l[0], l[1], l[2], 6.4, 6.4, 3.2, 0.3) if l[0].startswith("LAND_AUD") else l for l in LANDS]   # boss 14.8 x 12.4 inside the H-side frame slot 15.6 x 13.0
FACE_SETBACK = {"USBC": 0.0, "USBA": LAND_T + 0.2, "RJ45": LAND_T + 0.2, "HDMI": LAND_T + 0.2}   # mouth / face below its land

def zs(x):   # outer surface height at X (0 at the crown)
    if not CASE_R: return 0.0
    u = x - PL_C[0]; return -(CASE_R - math.sqrt(CASE_R ** 2 - u * u))

def dz(x, y):   # residual board-to-plate tilt from M-IOT1 (0 until measured)
    return (x - TILT_REF[0]) * math.tan(math.radians(TILT_AX_DEG)) + (y - TILT_REF[1]) * math.tan(math.radians(TILT_AY_DEG))

# ---------------- solid ----------------
BIG = 400.0
def prism(w, h, r, z0=2.0, z1=-20.0):
    return cq.Workplane("XY").workplane(offset=z0).center(*PL_C).sketch().rect(w, h).vertices().fillet(r).finalize().extrude(z1 - z0)
def cyl(rad):
    if not CASE_R: return cq.Workplane("XY").workplane(offset=-(CASE_R_FLAT - rad)).center(*PL_C).rect(BIG, BIG).extrude(-BIG)
    return cq.Workplane("XZ").center(PL_C[0], -CASE_R).circle(rad).extrude(BIG, both=True)
CASE_R_FLAT = 1000.0
R0 = CASE_R or CASE_R_FLAT
def boxz(cx, cy, w, h, r, za, zb):
    return cq.Workplane("XY").workplane(offset=za).center(cx, cy).sketch().rect(w, h).vertices().fillet(max(r, 0.05)).finalize().extrude(zb - za)
from matplotlib.path import Path as MPath
FLEX_POLY = [tuple(p) for p in FJ["outline"]]
NECK = (74.6, 27.6, 81.5, 46.7)    # flex neck to the IC tab / ZIF tail leaves over the +X edge (trace: X 75.2-80.5, Y 28.2-46.1) -> rim notch
def _seg_d(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-12)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
def flex_dist(px, py):   # signed distance to the flex outline (negative inside)
    d = min(_seg_d(px, py, *FLEX_POLY[i], *FLEX_POLY[(i + 1) % len(FLEX_POLY)]) for i in range(len(FLEX_POLY)))
    inside = MPath(FLEX_POLY).contains_point((px, py)) or (NECK[0] <= px <= NECK[2] and NECK[1] <= py <= NECK[3])
    return -d if inside else d
dropped_clips = []
if FLEX == "stock":
    keep = []
    for x, y, o in CLIPS:
        if (x, y) in [(cx_, cy_) for cx_, cy_ in CLIPS_L + CLIP_B]: keep.append((x, y, o)); continue   # stock clip points always stay (the stock flex lived with them)
        hw, hh = ((CLIP_T + 2 * CLIP_HOOK) / 2, CLIP_W / 2) if o[0] == "x" else (CLIP_W / 2, (CLIP_T + 2 * CLIP_HOOK) / 2)
        dmin = min(flex_dist(x + i * hw, y + j * hh) for i in (-1, 0, 1) for j in (-1, 0, 1))
        (keep if dmin > FLEX_CLR + 0.2 else dropped_clips).append((x, y, o))
    CLIPS = keep

plate = prism(PL_W, PL_H, PL_R).intersect(cyl(R0)).cut(cyl(R0 - SKIN))      # constant 1.2 wall: inner face concentric with the outer cylinder
rim = prism(PL_W, PL_H, PL_R).cut(prism(PL_W - 2 * RIM_W, PL_H - 2 * RIM_W, PL_R - RIM_W)).intersect(cyl(R0 - SKIN + 0.02)).cut(cyl(R0 - SKIN - RIM_H))
plate = plate.union(rim)
report = []; land_z = {}; boss_info = {}
def ramp_cut(x_in, z_in, s, theta, y, ylen):
    run = 8.0 / math.tan(theta)
    pts = [(x_in, z_in + 0.02), (x_in - s * run, z_in - 8.0), (x_in, z_in - 8.0)]
    return cq.Workplane("XZ").polyline(pts).close().extrude(ylen / 2, both=True).translate((0, y, 0))
for lid, x, y, w, h, r, b in LANDS:
    zl = min(zs(x - w / 2), zs(x + w / 2)) + dz(x, y)     # flat land at the lowest outer-surface point of its footprint
    land_z[lid] = zl
    boss = boxz(x, y, w + 2 * b, h + 2 * b, r + b, zl - LAND_T, zl + 0.5).intersect(cyl(R0))
    s_in = 1.0 if x < PL_C[0] else -1.0                         # inboard = toward the centre bar
    x_in = x + s_in * (w / 2 + b); z_in = zs(x_in) - SKIN       # inner skin at the boss inboard edge
    p = z_in - (zl - LAND_T)                                     # how far the boss stands proud of the inner skin there
    theta = None
    if FLEX == "stock" and p > 0.05:
        theta = max(math.radians(RAMP_MIN_DEG), math.atan2(max(p - (LAND_T - 0.8), 0.0), b))
        boss = boss.cut(ramp_cut(x_in, z_in, s_in, theta, y, h + 2 * b + 0.2))
    plate = plate.union(boss).cut(boxz(x, y, w, h, r, zl, 10.0))
    boss_info[lid] = dict(boss_w=round(w + 2 * b, 2), boss_h=round(h + 2 * b, 2), proud_of_inner_skin=round(p, 2), ramp_deg=round(math.degrees(theta), 1) if theta else None,
                          ramp_run=round(p / math.tan(theta), 2) if theta else None, land_z=round(zl, 2), boss_bottom_z=round(zl - LAND_T, 2))
    report.append((lid, "LAND", x, y, w, h, "flat land z=%.2f (crown=0); boss %.1f x %.1f; inboard pocket depth %.2f; boss stands %.2f proud of the inner skin at its inboard edge%s" % (
        zl, w + 2 * b, h + 2 * b, max(zs(x - w / 2), zs(x + w / 2)) - zl, p, ("; inboard ramp %.0f deg" % math.degrees(theta)) if theta else "")))
def land_of(x, y):
    for lid, lx, ly, w, h, r, b in LANDS:
        if abs(x - lx) <= w / 2 and abs(y - ly) <= h / 2: return lid
    return None
for oid, kind, x, y, w, h, r in OPEN:
    lid = land_of(x, y)
    if lid:
        zface = land_z[lid] - FACE_SETBACK.get(kind, 0.0)
        if kind == "RJ45":
            report.append((oid, kind, x, y, w, h, "on %s (land z=%.2f); plug passes the plate, the flex cut-out and the frame slot; HR913790A jack face SET BACK behind the frame back plane "
                           "(face depth >= frame-back depth from M-IOF2 + 0.3; both ETH jacks share one height, so D0 - 16.9 sets it)" % (lid, land_z[lid])))
        else:
            report.append((oid, kind, x, y, w, h, "on %s; connector %s at z=%.2f below the crown (board-to-crown distance D0 from M-IOF2 minus this = required height)" %
                       (lid, "mouth" if kind == "USBC" else "face", -zface)))
    else:
        report.append((oid, kind, x, y, w, h, "through (no land)"))
    if FLEX != "stock" and kind in ("USBA", "RJ45", "HDMI") and lid:   # collars only without the flex (they would pierce the flex rims)
        zl = land_z[lid]; L = ETH_GUIDE_L.get(oid, COLLAR_L0); cw = COLLAR_WALL_BY.get(oid, COLLAR_WALL)
        plate = plate.union(boxz(x, y, w + 2 * cw, h + 2 * cw, r + cw, zl - LAND_T - L, zl - LAND_T + 0.01))
    plate = plate.cut(boxz(x, y, w, h, r, 10.0, -20.0))
for oid, x, y, dd in ROUND:
    plate = plate.cut(cq.Workplane("XY").workplane(offset=10).center(x, y).circle(dd / 2).extrude(-30)); report.append((oid, "ROUND", x, y, dd, dd, "through"))
for oid, x, y in PIPES:
    zi = zs(x) - SKIN + dz(x, y)
    plate = plate.union(cq.Workplane("XY").workplane(offset=zi + 0.3).center(x, y).circle(PIPE_OD / 2).extrude(-(PIPE_L + 0.3)))
    plate = plate.cut(cq.Workplane("XY").workplane(offset=10).center(x, y).circle(PIPE_BORE / 2).extrude(-30))
    report.append((oid, "LIGHTPIPE", x, y, PIPE_BORE, PIPE_BORE, "boss OD %.1f, %.1f mm below the inner face at z=%.2f" % (PIPE_OD, PIPE_L, zi)))
for x, y, o in CLIPS:
    zi = zs(x) - SKIN
    if o[0] == "x":
        tab = cq.Workplane("XY").workplane(offset=zi + 0.3).center(x, y).rect(CLIP_T, CLIP_W).extrude(-(CLIP_L + 0.3))
        hook = cq.Workplane("XY").workplane(offset=zi - CLIP_L + 1.2).center(x + (-1 if o == "x-" else 1) * (CLIP_T / 2 + CLIP_HOOK / 2), y).rect(CLIP_HOOK, CLIP_W).extrude(-1.2)
    else:
        tab = cq.Workplane("XY").workplane(offset=zi + 0.3).center(x, y).rect(CLIP_W, CLIP_T).extrude(-(CLIP_L + 0.3))
        hook = cq.Workplane("XY").workplane(offset=zi - CLIP_L + 1.2).center(x, y - (CLIP_T / 2 + CLIP_HOOK / 2)).rect(CLIP_W, CLIP_HOOK).extrude(-1.2)
    plate = plate.union(tab).union(hook)
for x, y, o in dropped_clips: report.append(("CLIP_DROPPED", "CLIP", x, y, CLIP_T, CLIP_W, "mirrored clip collides with the 821-2222 flex/neck -> removed"))
zi = zs(FRAME_SCREW[0]) - SKIN
plate = plate.cut(cq.Workplane("XY").workplane(offset=zi - 0.01).center(*FRAME_SCREW).circle(SCREW_POCKET_D / 2).extrude(SCREW_POCKET_DEPTH + 0.01))
if FLEX == "stock":
    # glue pocket: flex outline + FLEX_CLR, FLEX_POCKET deep into the inner skin; land bosses (incl. audio) are kept; rim/clip material inside is removed
    fl = cq.Workplane("XY").workplane(offset=-20).polyline(FLEX_POLY).close().offset2D(FLEX_CLR).extrude(22)
    fl = fl.union(boxz((NECK[0] + NECK[2]) / 2, (NECK[1] + NECK[3]) / 2, NECK[2] - NECK[0], NECK[3] - NECK[1], 0.3, -20, 2))
    keep = None
    for lid, x, y, w, h, r, b in LANDS:
        k = boxz(x, y, w + 2 * b + 0.02, h + 2 * b + 0.02, r + b, -20, 2)
        keep = k if keep is None else keep.union(k)
    pocket = fl.intersect(cyl(R0 - SKIN + FLEX_POCKET)).cut(keep)
    plate = plate.cut(pocket)
    report.append(("FLEX_POCKET", "GLUE", PL_C[0], PL_C[1], 0, 0, "821-2222 glue pocket %.2f deep (outline + %.2f), wall left %.2f; foam allowance %.2f (TO MEASURE) behind the flex; rim notched for the neck X %.1f-%.1f, Y %.1f-%.1f" % (
        FLEX_POCKET, FLEX_CLR, SKIN - FLEX_POCKET, FOAM_T, NECK[0], NECK[2], NECK[1], NECK[3])))
    for wid, x, y, w, h, r in WINDOWS:
        plate = plate.cut(boxz(x, y, w, h, r, 10.0, -20.0))
        report.append((wid, "LIGHT_WINDOW", x, y, w, h, "through window over the flex light-guide pad (stock LEDs light it)"))
# locating pins at the frame's HOLE_C1 / PIN_C3 (the stock plate shows round bosses there); they pass the flex holes (Ø3.4 / Ø4.6) and
# locate plate + flex on the frame.  Length TO VERIFY against the frame thickness (M-IOF2).
LOCATE_PINS = [("PIN_C1", 52.93, 75.41, 2.7), ("PIN_C3", 54.49, 19.23, 2.7)]; PIN_LEN = 2.5
for pid, x, y, dd in LOCATE_PINS:
    zi = zs(x) - SKIN
    plate = plate.union(cq.Workplane("XY").workplane(offset=zi + 0.3).center(x, y).circle(dd / 2).extrude(-(PIN_LEN + 0.3)).faces("<Z").chamfer(0.3))
    report.append((pid, "PIN", x, y, dd, dd, "locating pin Ø%.1f x %.1f into the frame hole (frame scan Ø3.0-3.1), through the flex hole" % (dd, PIN_LEN)))
for nm, x, y, w, h in LEGEND:
    plate = plate.cut(boxz(x, y, w, h, 0.5, 10.0, -20.0).intersect(cyl(R0)).cut(cyl(R0 - 0.6)))
tag = "" if ETH2 == "open" else "_eth2blank"
step = os.path.join(HERE, "io_plate_v2_A0%s.step" % tag); stl = os.path.join(HERE, "io_plate_v2_A0%s.stl" % tag)
cq.exporters.export(plate, step); cq.exporters.export(plate, stl, tolerance=0.02, angularTolerance=0.1)
bb = plate.val().BoundingBox()
print("bbox", round(bb.xmin, 2), round(bb.xmax, 2), round(bb.ymin, 2), round(bb.ymax, 2), round(bb.zmin, 2), round(bb.zmax, 2), "vol", round(plate.val().Volume(), 1), "solids", len(plate.solids().vals()))

# ---------------- 821-2222 flex: clearance check, trace DXF, foam/insulator DXF, A1 replacement-flex cut-outs ----------------
THRU = {"USBC": (8.94, 3.26, "receptacle shell (mouth flush with the land, so it crosses the flex plane)"), "USBA": (12.0, 4.5, "plug (receptacle face sits behind the flex plane)"),
        "RJ45": (11.7, 8.2, "plug body [latch excluded]"), "HDMI": (13.9, 4.45, "plug (receptacle face behind the flex plane)")}
CUT = {c["id"]: c for c in FJ["cutouts"]}
OPEN2CUT = {"C1": "C1", "C2": "C2", "C3": "C3", "C4": "C4", "C5": "C5", "C6": "C6", "A1": "A1", "A2": "A2", "A3": "A3", "A4": "A4", "ETH1": "ETH1", "ETH2": "ETH2", "HDMI": "HDMI"}
LAND_OF_OPEN = {o[0]: land_of(o[2], o[3]) for o in OPEN}
FLEX_CHECK = []
def margins(cx, cy, w, h, c):   # per-side margins of a w x h box at (cx,cy) inside flex cut-out c (+ = clear)
    return dict(xm=round((cx - w / 2) - (c["cx"] - c["w"] / 2), 2), xp=round((c["cx"] + c["w"] / 2) - (cx + w / 2), 2),
                ym=round((cy - h / 2) - (c["cy"] - c["h"] / 2), 2), yp=round((c["cy"] + c["h"] / 2) - (cy + h / 2), 2))
for oid, kind, x, y, w, h, r in OPEN:
    if oid not in OPEN2CUT: continue
    c = CUT[OPEN2CUT[oid]]; tw, th, what = THRU[kind]
    mt = margins(x, y, tw, th, c); mo = margins(x, y, w, h, c)
    lid = LAND_OF_OPEN[oid]; bi = boss_info.get(lid, {})
    L_ = LANDS[[l[0] for l in LANDS].index(lid)] if lid else None
    mb = margins(L_[1], L_[2], bi["boss_w"], bi["boss_h"], c) if lid else None
    grouped = lid in ("LAND_C_H", "LAND_C_O", "LAND_A_H", "LAND_A_O")
    FLEX_CHECK.append(dict(port=oid, flex_cutout=dict(cx=c["cx"], cy=c["cy"], w=c["w"], h=c["h"]), offset=[round(x - c["cx"], 2), round(y - c["cy"], 2)],
                           through=what, through_size=[tw, th], through_min_margin=min(mt.values()), plate_opening_min_margin=min(mo.values()),
                           boss=lid, boss_overlap_max=round(-min(mb["xm"], mb["xp"], *(() if grouped else (mb["ym"], mb["yp"]))), 2) if mb else None,
                           flex_bars_on_boss=grouped, boss_proud=bi.get("proud_of_inner_skin")))
for aid, lid in (("AUD_H", "LAND_AUD_H"), ("AUD_O", "LAND_AUD_O")):
    c = CUT[aid]; L = [l for l in LANDS if l[0] == lid][0]; bd = L[3] + 2 * L[6]
    FLEX_CHECK.append(dict(port=aid, flex_cutout=dict(cx=c["cx"], cy=c["cy"], d=c["d"]), offset=[round(L[1] - c["cx"], 2), round(L[2] - c["cy"], 2)], through="3.5 mm plug / Ø4.8 opening",
                           through_min_margin=round(c["d"] / 2 - 4.8 / 2 - math.hypot(L[1] - c["cx"], L[2] - c["cy"]), 2), boss=lid,
                           boss_overlap_max=round(bd / 2 + math.hypot(L[1] - c["cx"], L[2] - c["cy"]) - c["d"] / 2, 2), boss_proud=boss_info[lid]["proud_of_inner_skin"]))
if FLEX == "stock" and ETH2 == "open":
    for row in FLEX_CHECK: print("FLEXCHECK", row)
    # trace DXF (back view, plate frame)
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for ln, col in (("FLEX_OUTLINE", 30), ("FLEX_CUTOUTS", 30), ("FLEX_FRAME_HOLES", 30), ("FLEX_LIGHT_PADS", 5), ("FLEX_LEDS", 2), ("FLEX_BUTTON", 6), ("FLEX_TAIL_APPROX", 8),
                    ("FLEX_SILVER_FRAMES", 9), ("REF_PLATE_OUTLINE", 7), ("REF_PLATE_OPENINGS", 7), ("REF_LAND_BOSSES", 1), ("REF_LIGHT_WINDOWS", 2), ("A1_FLEX_CUTOUTS_PROPOSED", 3), ("NOTES", 7)):
        doc.layers.add(ln, color=col)
    def rr(cx, cy, w, h, r, layer):
        r = min(r, w / 2, h / 2); pts = []
        for (ax_, ay_, a0) in ((cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)):
            for k in range(9):
                t = math.radians(a0 + 90 * k / 8); pts.append((ax_ + r * math.cos(t), ay_ + r * math.sin(t)))
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
    msp.add_lwpolyline(FLEX_POLY, close=True, dxfattribs={"layer": "FLEX_OUTLINE"})
    for c in FJ["cutouts"]:
        if "d" in c: msp.add_circle((c["cx"], c["cy"]), c["d"] / 2, dxfattribs={"layer": "FLEX_CUTOUTS"})
        else: msp.add_lwpolyline([tuple(p) for p in c["poly"]], close=True, dxfattribs={"layer": "FLEX_CUTOUTS"})
        msp.add_text(c["id"], dxfattribs={"layer": "NOTES", "height": 1.0}).set_placement((c["cx"] - 1.5, c["cy"]))
    for hh in FJ["holes"]: msp.add_circle((hh["cx"], hh["cy"]), hh["d"] / 2, dxfattribs={"layer": "FLEX_FRAME_HOLES"})
    for p in FJ["light_pads"]: rr(p["cx"], p["cy"], p["w"], p["h"], 0.3, "FLEX_LIGHT_PADS"); msp.add_text(p["id"], dxfattribs={"layer": "NOTES", "height": 0.8}).set_placement((p["cx"] - 2, p["cy"] + p["h"] / 2 + 0.3))
    for l in FJ["leds"]: rr(l["cx"], l["cy"], l["w"], l["h"], 0.05, "FLEX_LEDS")
    for f in FJ["silver_frames"]: rr(f["cx"], f["cy"], f["w"], f["h"], 0.5, "FLEX_SILVER_FRAMES")
    bt = FJ["button"]; msp.add_circle((bt["cx"], bt["cy"]), bt["ring_d"] / 2, dxfattribs={"layer": "FLEX_BUTTON"}); msp.add_circle((bt["cx"], bt["cy"]), bt["dome_d"] / 2, dxfattribs={"layer": "FLEX_BUTTON"})
    msp.add_lwpolyline([tuple(p) for p in FJ["tail_approx"]], close=True, dxfattribs={"layer": "FLEX_TAIL_APPROX"})
    it = FJ["ic_tab_from_plate_scan"]; rr((it["x"][0] + it["x"][1]) / 2, (it["y"][0] + it["y"][1]) / 2, it["x"][1] - it["x"][0], it["y"][1] - it["y"][0], 0.2, "FLEX_TAIL_APPROX")
    rr(PL_C[0], PL_C[1], PL_W, PL_H, PL_R, "REF_PLATE_OUTLINE")
    for oid, kind, x, y, w, h, r in OPEN: rr(x, y, w, h, r, "REF_PLATE_OPENINGS")
    for oid, x, y, dd in ROUND: msp.add_circle((x, y), dd / 2, dxfattribs={"layer": "REF_PLATE_OPENINGS"})
    for lid, x, y, w, h, r, b in LANDS:
        rr(x, y, w + 2 * b, h + 2 * b, r + b, "REF_LAND_BOSSES")
        rr(x, y, w + 2 * b + 0.6, h + 2 * b + 0.6, r + b + 0.3, "A1_FLEX_CUTOUTS_PROPOSED")   # A1 replacement flex: boss + 0.3 per side
    for wid, x, y, w, h, r in WINDOWS: rr(x, y, w, h, r, "REF_LIGHT_WINDOWS")
    msp.add_text("821-2222 I/O-wall flex trace (plate-facing side, back view, mm) from Aidan photo 3ea4e6e5; homography rms 0.41 mm; VERIFY by caliper", dxfattribs={"layer": "NOTES", "height": 1.6}).set_placement((20, -22))
    doc.saveas(os.path.join(HERE, "flex_821-2222_trace.dxf"))
    # foam / insulator die-cut (board side of the flex): flex outline + neck, minus land bosses + 0.3, minus frame holes/pin + 0.5, minus button ring
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for ln in ("CUT_OUTER", "CUT_INNER", "NOTES"): doc.layers.add(ln)
    rr_layer = lambda *a: rr(*a)
    msp.add_lwpolyline(FLEX_POLY, close=True, dxfattribs={"layer": "CUT_OUTER"})
    for lid, x, y, w, h, r, b in LANDS: rr(x, y, w + 2 * b + 0.6, h + 2 * b + 0.6, r + b + 0.3, "CUT_INNER")
    for hh in FJ["holes"]: msp.add_circle((hh["cx"], hh["cy"]), hh["d"] / 2 + 0.5, dxfattribs={"layer": "CUT_INNER"})
    msp.add_circle((bt["cx"], bt["cy"]), bt["ring_d"] / 2 + 0.5, dxfattribs={"layer": "CUT_INNER"})
    msp.add_text("MP62 IO flex foam / insulator A0 (back view, mm): 1.0 PE/PORON foam with PSA (stock-like) OR 0.25 Formex GK-10 / fish paper; laser or die cut; VERIFY against the flex", dxfattribs={"layer": "NOTES", "height": 1.6}).set_placement((20, -22))
    doc.saveas(os.path.join(HERE, "io_flex_foam_insulator_A0.dxf"))
    # check image
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly, Circle as MCirc, Rectangle as MRect, FancyBboxPatch as FBP
    fr = json.load(open(os.path.join(HERE, "..", "..", "bracket", "io_frame", "io_frame.json"))) if os.path.exists(os.path.join(HERE, "..", "..", "bracket", "io_frame", "io_frame.json")) else None
    fig, ax = plt.subplots(figsize=(8.5, 15))
    ax.add_patch(FBP((PL_C[0] - PL_W / 2 + PL_R, PL_C[1] - PL_H / 2 + PL_R), PL_W - 2 * PL_R, PL_H - 2 * PL_R, boxstyle="round,pad=%g" % PL_R, fc="#f4f4f4", ec="k", lw=0.8))
    ax.add_patch(MPoly(FLEX_POLY, fc="#ffd98a", ec="#c07000", lw=0.8, label="821-2222 flex (trace)"))
    ax.add_patch(MPoly([tuple(p) for p in FJ["tail_approx"]], fc="#ffe9b8", ec="#c07000", ls="--", lw=0.6))
    for c in FJ["cutouts"]:
        ax.add_patch(MCirc((c["cx"], c["cy"]), c["d"] / 2, fc="w", ec="#c07000") if "d" in c else MPoly(c["poly"], fc="w", ec="#c07000"))
    for hh in FJ["holes"]: ax.add_patch(MCirc((hh["cx"], hh["cy"]), hh["d"] / 2, fc="w", ec="#c07000"))
    for p in FJ["light_pads"]: ax.add_patch(MRect((p["cx"] - p["w"] / 2, p["cy"] - p["h"] / 2), p["w"], p["h"], fc="#b8c8ff", ec="b", lw=0.5))
    for l in FJ["leds"]: ax.add_patch(MRect((l["cx"] - l["w"] / 2, l["cy"] - l["h"] / 2), l["w"], l["h"], fc="#fff200", ec="k", lw=0.3))
    ax.add_patch(MCirc((bt["cx"], bt["cy"]), bt["ring_d"] / 2, fc="none", ec="m", lw=0.8))
    if fr:
        for k, v in fr["features"].items():
            if k.startswith(("SQ", "TALL", "SMALL", "ROUND", "BIG")): ax.add_patch(MRect((v["cx"] - v["w"] / 2, v["cy"] - v["h"] / 2), v["w"], v["h"], fc="none", ec="g", lw=0.6, ls=":"))
    for lid, x, y, w, h, r, b in LANDS: ax.add_patch(MRect((x - (w + 2 * b) / 2, y - (h + 2 * b) / 2), w + 2 * b, h + 2 * b, fc="none", ec="r", lw=0.9))
    for oid, kind, x, y, w, h, r in OPEN: ax.add_patch(MRect((x - w / 2, y - h / 2), w, h, fc="none", ec="k", lw=0.5))
    for oid, x, y, dd in ROUND: ax.add_patch(MCirc((x, y), dd / 2, fc="none", ec="k", lw=0.5))
    for wid, x, y, w, h, r in WINDOWS: ax.add_patch(MRect((x - w / 2, y - h / 2), w, h, fc="#ffff80", ec="k", lw=0.6))
    for x, y, o in CLIPS: ax.plot(x, y, "b^", ms=6)
    for x, y, o in dropped_clips: ax.plot(x, y, "rx", ms=9, mew=2)
    for row in FLEX_CHECK:
        c = row["flex_cutout"]
        ax.text(c["cx"], c["cy"], "%s\nthru %+.2f\nboss +%.1f%s\nlift %.1f" % (row["port"], row["through_min_margin"], row["boss_overlap_max"] or 0, "+bars" if row.get("flex_bars_on_boss") else "", row["boss_proud"] or 0), fontsize=4.6, ha="center", va="center", color="darkred")
    ax.set_xlim(22, 118); ax.set_ylim(-16, 160); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_title("821-2222 flex trace vs plate v2 A0 (back view, mm)\norange = flex, white = flex cut-outs, red = our land bosses, black = plate openings, green dotted = metal frame slots,\n"
                 "blue = light-guide pads, yellow chips = LEDs, yellow = plate light windows, x = dropped clip.  'thru' = min margin of shell/plug in the cut-out,\n"
                 "'boss +' = how far our boss overlaps the flex rim, 'lift' = boss height proud of the inner skin (the rim would have to fold into the frame slot)", fontsize=6.5)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "flex_821-2222_check.png"), dpi=170)

# ---------------- DXF (openings, back view and front view) ----------------
if ETH2 == "open":
    for view in ("backview", "frontview"):
        BW = 101.00496445740619
        fx = (lambda x: x) if view == "backview" else (lambda x: 40 + BW - x)   # front view = KiCad PCB frame x (y kept = Y; KiCad y = 200 - Y)
        doc = ezdxf.new("R2010"); msp = doc.modelspace()
        for ln in ("OUTLINE", "OPENINGS", "LIGHTPIPES", "LIGHT_WINDOWS", "CLIPS", "NOTES", ): doc.layers.add(ln)
        def rrect(cx, cy, w, h, r, layer):
            r = min(r, w / 2, h / 2); pts = []
            for (ax, ay, a0) in ((cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)):
                for k in range(9):
                    t = math.radians(a0 + 90 * k / 8); pts.append((fx(ax + r * math.cos(t)), ay + r * math.sin(t)))
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
        rrect(PL_C[0], PL_C[1], PL_W, PL_H, PL_R, "OUTLINE")
        for oid, kind, x, y, w, h, r in OPEN:
            rrect(x, y, w, h, r, "OPENINGS"); msp.add_text(oid, dxfattribs={"layer": "NOTES", "height": 1.2}).set_placement((fx(x) - 2, y + h / 2 + 0.6))
        for oid, x, y, dd in ROUND: msp.add_circle((fx(x), y), dd / 2, dxfattribs={"layer": "OPENINGS"})
        for oid, x, y in PIPES: msp.add_circle((fx(x), y), PIPE_BORE / 2, dxfattribs={"layer": "LIGHTPIPES"})
        for wid, x, y, w, h, r in WINDOWS: rrect(x, y, w, h, r, "LIGHT_WINDOWS")
        for x, y, o in CLIPS: msp.add_circle((fx(x), y), 1.0, dxfattribs={"layer": "CLIPS"})
        msp.add_text("MP62 IO plate v2 A0 - %s - mm - Y up = MEG/base end" % view, dxfattribs={"layer": "NOTES", "height": 2}).set_placement((fx(PL_C[0]) - 30, -12))
        doc.saveas(os.path.join(HERE, "io_plate_v2_A0_openings_%s.dxf" % view))
    json.dump(dict(params=dict(outline=dict(centre=PL_C, w=PL_W, h=PL_H, r=PL_R), case_r=CASE_R, land_t=LAND_T, clip=dict(t=CLIP_T, w=CLIP_W, l=CLIP_L, hook=CLIP_HOOK), skin=SKIN, rim_h=RIM_H, rim_w=RIM_W, tilt_ax_deg=TILT_AX_DEG, tilt_ay_deg=TILT_AY_DEG,
                   tilt_ref=TILT_REF, collar_l0=COLLAR_L0 if FLEX != "stock" else 0.0, clearance_per_side=CLR,
                   flex=dict(mode=FLEX, flex_t=FLEX_T, psa_t=PSA_T, foam_t=FOAM_T, pocket=FLEX_POCKET, pocket_clr=FLEX_CLR, neck_notch=NECK)), bosses=boss_info, flex_check=FLEX_CHECK, features=[dict(id=a, kind=b, x=c, y=d, w=e, h=f, note=g) for a, b, c, d, e, f, g in report],
                   clips=CLIPS), open(os.path.join(HERE, "io_plate_v2_A0_features.json"), "w"), indent=1)
    # preview: outer view (2D) + isometric of the inner side
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Circle
    fig, ax = plt.subplots(figsize=(6, 13))
    ax.add_patch(FancyBboxPatch((PL_C[0] - PL_W / 2 + PL_R, PL_C[1] - PL_H / 2 + PL_R), PL_W - 2 * PL_R, PL_H - 2 * PL_R, boxstyle="round,pad=%g" % PL_R, fc="#dddddd", ec="k"))
    for oid, kind, x, y, w, h, r in OPEN:
        ax.add_patch(FancyBboxPatch((x - w / 2 + r, y - h / 2 + r), w - 2 * r, h - 2 * r, boxstyle="round,pad=%g" % r, fc="white", ec="k"))
        ax.text(x, y, oid, ha="center", va="center", fontsize=6)
    for oid, x, y, dd in ROUND: ax.add_patch(Circle((x, y), dd / 2, fc="white", ec="k"))
    ax.text(63.02, 108.03, "button\n(clear cap,\nD20)", ha="center", va="center", fontsize=5)
    for oid, x, y in PIPES: ax.add_patch(Circle((x, y), 1.0, fc="yellow", ec="k"))
    for wid, x, y, w, h, r in WINDOWS: ax.add_patch(FancyBboxPatch((x - w / 2 + r, y - h / 2 + r), w - 2 * r, h - 2 * r, boxstyle="round,pad=%g" % r, fc="yellow", ec="k"))
    for x, y, o in CLIPS: ax.plot(x, y, "b^", ms=5)
    ax.set_xlim(20, 86); ax.set_ylim(-8, 162); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_title("IO plate v2 A0, OUTER face (back view)\nyellow = light windows over the 821-2222 flex pads, blue = clips (verify)", fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "io_plate_v2_A0_outer.png"), dpi=150)
    iso = plate.translate((-PL_C[0], -PL_C[1], 0)).rotate((0, 0, 0), (0, 0, 1), 90).rotate((0, 0, 0), (1, 0, 0), 180)
    cq.exporters.export(iso, os.path.join(HERE, "_iso.svg"), opt={"projectionDir": (0.25, -0.45, 1.0), "showHidden": False, "width": 1600, "height": 700,
                                                                 "marginLeft": 40, "marginTop": 40, "strokeWidth": 0.15})
for row in report: print(row)
