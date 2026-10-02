#!/usr/bin/env python3
"""I/O plate stage 2: power button, plate width profile, DXF (board back-view frame) and overlays. Run after trace_io_plate.py."""
import json, os, sys, math
import cv2, numpy as np, ezdxf
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
d = json.load(open("io_plate.json")); SX, SY = d["calibration"]["SX"], d["calibration"]["SY"]
R = np.array(d["outer_to_board"]["R"]); t = np.array(d["outer_to_board"]["t"])
R2 = np.array(d["inner_to_outer"]["R"]); t2 = np.array(d["inner_to_outer"]["t"])
mm = lambda p: np.array([p[0] / SX, -p[1] / SY])
ob = lambda p: R.T @ (mm(p) - t); ib = lambda p: R.T @ ((R2 @ mm(p) + t2) - t)
btn_c = ob((416.1, 467.0)); btn_d = 2 * 24.5 / SX
d["openings_outer"] = [r for r in d["openings_outer"] if r["id"] != "POWER_BUTTON"] + [dict(id="POWER_BUTTON", kind="POWER_BUTTON", centre=btn_c.round(2).tolist(), w=round(btn_d, 2), h=round(btn_d, 2), note="button cap ring (faint gap ring), +-0.5")]
ol = np.load("work/outline_outer_board.npy"); oli = np.load("work/outline_inner_board.npy")
# width profile along Y (plate long axis ~ board Y)
prof = []
for y in np.arange(-4, 159, 4):
    s = ol[np.abs(ol[:, 1] - y) < 0.6]
    if len(s) >= 2: prof.append((float(y), round(float(s[:, 0].min()), 2), round(float(s[:, 0].max()), 2)))
d["plate"]["width_profile_y_xmin_xmax"] = prof
mid = [p for p in prof if 20 < p[0] < 140]; d["plate"]["straight_width"] = round(float(np.median([p[2] - p[1] for p in mid])), 2)
d["plate"]["x_straight"] = [round(float(np.median([p[1] for p in mid])), 2), round(float(np.median([p[2] for p in mid])), 2)]
# end radius: fit circle to top-end and bottom-end outline points (outside the straight band)
def fitc(P):
    A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]; b = (P ** 2).sum(1); c = np.linalg.lstsq(A, b, rcond=None)[0]
    return c[0], c[1], math.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)
ymax, ymin = ol[:, 1].max(), ol[:, 1].min(); xl, xr = d["plate"]["x_straight"]
for name, sel in (("top", ol[ol[:, 1] > ymax - 12]), ("bottom", ol[ol[:, 1] < ymin + 12])):
    for side, s2 in (("L", sel[sel[:, 0] < xl + 12]), ("R", sel[sel[:, 0] > xr - 12])):
        s3 = s2[(np.abs(s2[:, 0] - (xl if side == "L" else xr)) > 0.3) & (np.abs(s2[:, 1] - (ymax if name == "top" else ymin)) > 0.3)]
        if len(s3) > 10: cx, cy, r = fitc(s3); d["plate"]["corner_%s_%s_R" % (name, side)] = round(r, 1)
print({k: v for k, v in d["plate"].items() if k != "width_profile_y_xmin_xmax"})
json.dump(d, open("io_plate.json", "w"), indent=1, default=float)
# ---- DXF ----
doc = ezdxf.new("R2010"); msp = doc.modelspace()
for n, c in (("PLATE_OUTLINE_OUTER", 7), ("PLATE_OUTLINE_INNER", 8), ("OPENINGS_OUTER", 1), ("OPENINGS_INNER", 5), ("ICON_WINDOWS", 3), ("POWER_BUTTON", 2),
             ("IO_BOARD_REF", 9), ("NEW_PORT_MAP", 6), ("NOTES", 7)): doc.layers.add(n, color=c)
msp.add_lwpolyline(ol[::3].tolist(), close=True, dxfattribs={"layer": "PLATE_OUTLINE_OUTER"})
for r in d["openings_outer"]:
    (x, y), w, h = r["centre"], r["w"], r["h"]
    if r["kind"] in ("AUDIO_JACK", "POWER_BUTTON"): msp.add_circle((x, y), w / 2, dxfattribs={"layer": "POWER_BUTTON" if r["kind"] == "POWER_BUTTON" else "OPENINGS_OUTER"})
    else: msp.add_lwpolyline([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], close=True, dxfattribs={"layer": "OPENINGS_OUTER"})
    msp.add_text(r["id"], height=1.2, dxfattribs={"layer": "OPENINGS_OUTER"}).set_placement((x - w / 2, y + h / 2 + 0.6))
for r in d["features_inner"]:
    (x, y), w, h = r["centre"], r["w"], r["h"]; lay = "ICON_WINDOWS" if r["kind"] == "small/icon" else "OPENINGS_INNER"
    msp.add_lwpolyline([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], close=True, dxfattribs={"layer": lay})
try:
    ref = ezdxf.readfile("../io_board/io_board_ports.dxf")
    for e in ref.modelspace():
        try: e2 = e.copy(); e2.dxf.layer = "IO_BOARD_REF"; msp.add_entity(e2)
        except Exception: pass
except Exception as ex: print("ref", ex)
for i, s in enumerate(["Stock I/O plate (outer + inner scans) in the I/O BOARD back-view frame (bracket/io_board): overlays io_board_*.dxf.",
                       "Opening sizes = scan-axis bbox at 50 % threshold, +-0.3 (outer) / +-0.5 (inner). Registration to board ports rms 1.0 mm."]):
    msp.add_text(s, height=1.5, dxfattribs={"layer": "NOTES"}).set_placement((0, -12 - 2.5 * i))
doc.saveas("io_plate_board_frame.dxf")
# ---- overlay: outer scan with board-frame features mapped back ----
def b2px(p):  # board -> outer px
    s = R @ np.array(p) + t; return (int(round(s[0] * SX)), int(round(-s[1] * SY)))
for name, src, inv in (("outer", "io_plate_outer_scan.jpeg", None), ("inner", "io_plate_inner_scan.jpeg", True)):
    im = cv2.imread(src)
    def toimg(p):
        s = R @ np.array(p) + t
        if inv: s = np.linalg.solve(R2, s - t2)
        return (int(round(s[0] * SX)), int(round(-s[1] * SY)))
    try:
        for e in ref.modelspace():
            if e.dxftype() == "LWPOLYLINE":
                pts = np.array([toimg((x, y)) for x, y in e.get_points("xy")]); cv2.polylines(im, [pts], e.closed, (255, 140, 0), 1)
            elif e.dxftype() == "LINE": cv2.line(im, toimg((e.dxf.start.x, e.dxf.start.y)), toimg((e.dxf.end.x, e.dxf.end.y)), (255, 140, 0), 1)
            elif e.dxftype() == "CIRCLE": cv2.circle(im, toimg((e.dxf.center.x, e.dxf.center.y)), int(e.dxf.radius * SX), (255, 140, 0), 1)
    except Exception: pass
    for r in d["openings_outer"]:
        (x, y), w, h = r["centre"], r["w"], r["h"]
        if r["kind"] in ("AUDIO_JACK", "POWER_BUTTON"): cv2.circle(im, toimg((x, y)), int(w / 2 * SX), (0, 0, 255), 1)
        else: cv2.polylines(im, [np.array([toimg(q) for q in ((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2))])], True, (0, 0, 255), 1)
        cv2.putText(im, r["id"], toimg((x + w / 2 + 0.5, y)), 0, 0.3, (0, 0, 200), 1)
    crop = im[180:880, 180:660]; cv2.imwrite("io_plate_overlay_%s.png" % name, cv2.resize(crop, None, fx=1.5, fy=1.5))
print("ok")
