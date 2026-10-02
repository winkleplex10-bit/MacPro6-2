#!/usr/bin/env python3
"""MP62 I/O plate v2 rev A0 (new plastic plate; stock metal I/O frame stays). cadquery 2.8 + ezdxf.
Frame: stock BACK-VIEW frame of the I/O board (mm): origin at the board's bottom-left virtual corner, X to the right as seen
from behind the machine, Y up toward the MEG-array / base end. Z = 0 is the plate OUTER (visible) face, -Z goes into the
machine toward the I/O frame and the board.
Tilt handling = option (a): standard flat connectors; the plate absorbs any board-to-plate tilt with per-opening collars
(USB-A / RJ45 / HDMI) and outer spot-faces (USB-C) computed from TILT_AX_DEG / TILT_AY_DEG (set them from measurement
M-IOT1; both 0 until measured).  Usage: python build_plate.py [--eth2 open|blank]"""
import json, math, os, sys
import cadquery as cq
import ezdxf
HERE = os.path.dirname(os.path.abspath(__file__))
ETH2 = "blank"
if "--eth2" in sys.argv: ETH2 = sys.argv[sys.argv.index("--eth2") + 1]

# ---------------- parameters ----------------
PL_C = (53.19, 77.07); PL_W, PL_H, PL_R = 51.9, 163.1, 11.5      # outline (fit of the stock plate scan; straight width 51.89)
SKIN = 1.2; RIM_H = 3.0; RIM_W = 1.2                             # skin, inner perimeter rim (tray)
TILT_AX_DEG = 0.0   # + = board farther from the plate outer face as Xb increases   (from M-IOT1)
TILT_AY_DEG = 0.0   # + = board farther from the plate outer face as Y increases    (from M-IOT1)
TILT_REF = (53.2, 65.45)                                          # pivot: centre of the USB-C block
COLLAR_L0 = 1.0; COLLAR_WALL = 1.0                               # nominal collar length behind the skin, wall
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
if ETH2 == "open": LANDS.append(("LAND_ETH2", 42.5, 92.0, 14.2, 11.9, 1.0, 0.6))
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
plate = prism(PL_W, PL_H, PL_R).intersect(cyl(R0)).cut(cyl(R0 - SKIN))
rim = prism(PL_W, PL_H, PL_R).cut(prism(PL_W - 2 * RIM_W, PL_H - 2 * RIM_W, PL_R - RIM_W)).intersect(cyl(R0 - SKIN + 0.02)).cut(cyl(R0 - SKIN - RIM_H))
plate = plate.union(rim)
report = []; land_z = {}
for lid, x, y, w, h, r, b in LANDS:
    zl = min(zs(x - w / 2), zs(x + w / 2)) + dz(x, y)     # flat land at the lowest outer-surface point of its footprint
    land_z[lid] = zl
    boss = boxz(x, y, w + 2 * b, h + 2 * b, r + b, zl - LAND_T, zl + 0.5).intersect(cyl(R0))
    plate = plate.union(boss).cut(boxz(x, y, w, h, r, zl, 10.0))
    report.append((lid, "LAND", x, y, w, h, "flat land z=%.2f (crown=0); boss %.1f x %.1f; inboard pocket depth %.2f" % (zl, w + 2 * b, h + 2 * b, max(zs(x - w / 2), zs(x + w / 2)) - zl)))
def land_of(x, y):
    for lid, lx, ly, w, h, r, b in LANDS:
        if abs(x - lx) <= w / 2 and abs(y - ly) <= h / 2: return lid
    return None
for oid, kind, x, y, w, h, r in OPEN:
    lid = land_of(x, y)
    if lid:
        zface = land_z[lid] - FACE_SETBACK.get(kind, 0.0)
        report.append((oid, kind, x, y, w, h, "on %s; connector %s at z=%.2f below the crown (board-to-crown distance D0 from M-IOF2 minus this = required height)" %
                       (lid, "mouth" if kind == "USBC" else "face", -zface)))
    else:
        report.append((oid, kind, x, y, w, h, "through (no land)"))
    if kind in ("USBA", "RJ45", "HDMI") and lid:
        zl = land_z[lid]; L = COLLAR_L0
        plate = plate.union(boxz(x, y, w + 2 * COLLAR_WALL, h + 2 * COLLAR_WALL, r + COLLAR_WALL, zl - LAND_T - L, zl - LAND_T + 0.01))
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
zi = zs(FRAME_SCREW[0]) - SKIN
plate = plate.cut(cq.Workplane("XY").workplane(offset=zi - 0.01).center(*FRAME_SCREW).circle(SCREW_POCKET_D / 2).extrude(SCREW_POCKET_DEPTH + 0.01))
for nm, x, y, w, h in LEGEND:
    plate = plate.cut(boxz(x, y, w, h, 0.5, 10.0, -20.0).intersect(cyl(R0)).cut(cyl(R0 - 0.6)))
tag = "" if ETH2 == "blank" else "_eth2open"
step = os.path.join(HERE, "io_plate_v2_A0%s.step" % tag); stl = os.path.join(HERE, "io_plate_v2_A0%s.stl" % tag)
cq.exporters.export(plate, step); cq.exporters.export(plate, stl, tolerance=0.02, angularTolerance=0.1)
bb = plate.val().BoundingBox()
print("bbox", round(bb.xmin, 2), round(bb.xmax, 2), round(bb.ymin, 2), round(bb.ymax, 2), round(bb.zmin, 2), round(bb.zmax, 2), "vol", round(plate.val().Volume(), 1), "solids", len(plate.solids().vals()))

# ---------------- DXF (openings, back view and front view) ----------------
if ETH2 == "blank":
    for view in ("backview", "frontview"):
        BW = 101.00496445740619
        fx = (lambda x: x) if view == "backview" else (lambda x: 40 + BW - x)   # front view = KiCad PCB frame x (y kept = Y; KiCad y = 200 - Y)
        doc = ezdxf.new("R2010"); msp = doc.modelspace()
        for ln in ("OUTLINE", "OPENINGS", "LIGHTPIPES", "CLIPS", "NOTES", "OPTIONAL_ETH2"): doc.layers.add(ln)
        def rrect(cx, cy, w, h, r, layer):
            r = min(r, w / 2, h / 2); pts = []
            for (ax, ay, a0) in ((cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)):
                for k in range(9):
                    t = math.radians(a0 + 90 * k / 8); pts.append((fx(ax + r * math.cos(t)), ay + r * math.sin(t)))
            msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
        rrect(PL_C[0], PL_C[1], PL_W, PL_H, PL_R, "OUTLINE")
        for oid, kind, x, y, w, h, r in OPEN:
            rrect(x, y, w, h, r, "OPENINGS"); msp.add_text(oid, dxfattribs={"layer": "NOTES", "height": 1.2}).set_placement((fx(x) - 2, y + h / 2 + 0.6))
        rrect(42.5, 92.0, 13.0, 10.7, 0.5, "OPTIONAL_ETH2")
        for oid, x, y, dd in ROUND: msp.add_circle((fx(x), y), dd / 2, dxfattribs={"layer": "OPENINGS"})
        for oid, x, y in PIPES: msp.add_circle((fx(x), y), PIPE_BORE / 2, dxfattribs={"layer": "LIGHTPIPES"})
        for x, y, o in CLIPS: msp.add_circle((fx(x), y), 1.0, dxfattribs={"layer": "CLIPS"})
        msp.add_text("MP62 IO plate v2 A0 - %s - mm - Y up = MEG/base end" % view, dxfattribs={"layer": "NOTES", "height": 2}).set_placement((fx(PL_C[0]) - 30, -12))
        doc.saveas(os.path.join(HERE, "io_plate_v2_A0_openings_%s.dxf" % view))
    json.dump(dict(params=dict(outline=dict(centre=PL_C, w=PL_W, h=PL_H, r=PL_R), case_r=CASE_R, land_t=LAND_T, clip=dict(t=CLIP_T, w=CLIP_W, l=CLIP_L, hook=CLIP_HOOK), skin=SKIN, rim_h=RIM_H, rim_w=RIM_W, tilt_ax_deg=TILT_AX_DEG, tilt_ay_deg=TILT_AY_DEG,
                   tilt_ref=TILT_REF, collar_l0=COLLAR_L0, clearance_per_side=CLR), features=[dict(id=a, kind=b, x=c, y=d, w=e, h=f, note=g) for a, b, c, d, e, f, g in report],
                   clips=CLIPS), open(os.path.join(HERE, "io_plate_v2_A0_features.json"), "w"), indent=1)
    # preview: outer view (2D) + isometric of the inner side
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Circle
    fig, ax = plt.subplots(figsize=(6, 13))
    ax.add_patch(FancyBboxPatch((PL_C[0] - PL_W / 2 + PL_R, PL_C[1] - PL_H / 2 + PL_R), PL_W - 2 * PL_R, PL_H - 2 * PL_R, boxstyle="round,pad=%g" % PL_R, fc="#dddddd", ec="k"))
    for oid, kind, x, y, w, h, r in OPEN:
        ax.add_patch(FancyBboxPatch((x - w / 2 + r, y - h / 2 + r), w - 2 * r, h - 2 * r, boxstyle="round,pad=%g" % r, fc="white", ec="k"))
        ax.text(x, y, oid, ha="center", va="center", fontsize=6)
    ax.add_patch(FancyBboxPatch((42.5 - 6.0, 92 - 4.85), 12.0, 9.7, boxstyle="round,pad=0.5", fc="#cccccc", ec="gray", ls="--")); ax.text(42.5, 92, "ETH2\n(blank)", ha="center", va="center", fontsize=6)
    for oid, x, y, dd in ROUND: ax.add_patch(Circle((x, y), dd / 2, fc="white", ec="k"))
    ax.text(63.02, 108.03, "button\n(clear cap,\nD20)", ha="center", va="center", fontsize=5)
    for oid, x, y in PIPES: ax.add_patch(Circle((x, y), 1.0, fc="yellow", ec="k"))
    for x, y, o in CLIPS: ax.plot(x, y, "b^", ms=5)
    ax.set_xlim(20, 86); ax.set_ylim(-8, 162); ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_title("IO plate v2 A0, OUTER face (back view)\nyellow = light pipes, blue = clips (verify)", fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "io_plate_v2_A0_outer.png"), dpi=150)
    iso = plate.translate((-PL_C[0], -PL_C[1], 0)).rotate((0, 0, 0), (0, 0, 1), 90).rotate((0, 0, 0), (1, 0, 0), 180)
    cq.exporters.export(iso, os.path.join(HERE, "_iso.svg"), opt={"projectionDir": (0.25, -0.45, 1.0), "showHidden": False, "width": 1600, "height": 700,
                                                                 "marginLeft": 40, "marginTop": 40, "strokeWidth": 0.15})
for row in report: print(row)
