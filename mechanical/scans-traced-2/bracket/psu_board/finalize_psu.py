#!/usr/bin/env python3
"""PSU board stage 3: outline extents, holes, lug-pad groups in the corrected CAD frame (component view); DXF + overlay.
Run after trace_psu_board2.py: /workspace/cadenv/bin/python finalize_psu.py"""
import json, os, sys
import cv2, numpy as np, ezdxf
from scipy.optimize import least_squares
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
reg = json.load(open("work/reg2.json")); rc = reg["rect"]; K, X0, Y1 = rc["K"], rc["X0"], rc["Y1"]
im = cv2.imread(rc["file"]); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(float)
toPX = lambda x, y: (int(round((x - X0) * K)), int(round((Y1 - y) * K)))
# ---- outline by edge profiles (sub-pixel: 50 % crossing between board ~23 and background ~125) ----
gb = cv2.GaussianBlur(g, (5, 5), 0); THR = (23 + 125) / 2
def col_edge(x, ya, yb):   # first crossing from ya (outside) to yb (inside)
    c = toPX(x, 0)[0]; r0, r1 = toPX(0, ya)[1], toPX(0, yb)[1]; step = 1 if r1 > r0 else -1
    p = gb[r0:r1:step, c - 2:c + 3].mean(1)
    k = int(np.argmax(p < THR)); return ya - step * (-1) * 0 + (-(k) / K if step > 0 else k / K) if False else (Y1 - (r0 + step * k) / K)
def row_edge(y, xa, xb):
    r = toPX(0, y)[1]; c0, c1 = toPX(xa, 0)[0], toPX(xb, 0)[0]; step = 1 if c1 > c0 else -1
    p = gb[r - 2:r + 3, c0:c1:step].mean(0); k = int(np.argmax(p < THR)); return X0 + (c0 + step * k) / K
E = {}
E["left"] = np.median([row_edge(y, -58, -45) for y in np.arange(-60, 50, 2)])
E["right"] = np.median([row_edge(y, 58, 45) for y in np.arange(-60, 50, 2)])
E["top_main_L"] = np.median([col_edge(x, 85, 65) for x in np.arange(-46, -31, 1)])
E["top_main_R"] = np.median([col_edge(x, 85, 65) for x in np.arange(31, 46, 1)])
E["top_tab"] = np.median([col_edge(x, 90, 70) for x in np.arange(-22, 23, 1)])
E["bot_main_L"] = np.median([col_edge(x, -86, -65) for x in np.arange(-46, -41, 0.5)])
E["bot_main_R"] = np.median([col_edge(x, -86, -65) for x in np.arange(41, 46, 0.5)])
E["bot_tab"] = np.median([col_edge(x, -90, -70) for x in np.arange(-34, 35, 1)])
E["top_tab_L_side"] = np.median([row_edge(y, -40, -20) for y in np.arange(77, 78.5, 0.25)])
E["top_tab_R_side"] = np.median([row_edge(y, 40, 20) for y in np.arange(77, 78.5, 0.25)])
E["bot_tab_L_side"] = np.median([row_edge(y, -48, -30) for y in np.arange(-79, -75, 0.5)])
E["bot_tab_R_side"] = np.median([row_edge(y, 48, 30) for y in np.arange(-79, -75, 0.5)])
CADE = dict(left=-51.5, right=51.456, top_main_L=75.966, top_main_R=75.966, top_tab=79.966, bot_main_L=-72.55, bot_main_R=-72.952,
            bot_tab=-79.05, top_tab_L_side=-28.0, top_tab_R_side=27.956, bot_tab_L_side=-39.5, bot_tab_R_side=39.456)
out = {k: dict(scan=round(float(v), 2), cad=CADE[k], delta=round(float(v) - CADE[k], 2)) for k, v in E.items()}
for k, v in out.items(): print("%-15s scan %7.2f cad %7.2f d %+5.2f" % (k, v["scan"], v["cad"], v["delta"]))
# ---- holes (screw heads) in this frame ----
R = np.array(reg["options"][reg["chosen"]]["R"]); t = np.array(reg["options"][reg["chosen"]]["t"]); SX, SY = reg["cal"]["SX"], reg["cal"]["SY"]
holes = {}
for k, (px, py, d) in reg["holes_px"].items():
    q = R.T @ (np.array([px / SX, -py / SY]) - t); holes[k] = [round(float(q[0]), 2), round(float(q[1]), 2)]
print("holes", holes)
# ---- lug-pad blobs (solder joints) ----
r0, r1 = toPX(0, 75)[1], toPX(0, 62)[1]; sub = cv2.GaussianBlur(g[r0:r1].astype(np.uint8), (7, 7), 0)
n, lab, st, cen = cv2.connectedComponentsWithStats((sub > 150).astype(np.uint8)); pads = []
for i in range(1, n):
    if st[i, 4] < 120: continue
    x = cen[i][0] / K + X0; y = Y1 - (cen[i][1] + r0) / K
    if abs(x) < 24: continue
    pads.append(dict(x=round(float(x), 2), y=round(float(y), 2), w=round(st[i, 2] / K, 1), h=round(st[i, 3] / K, 1)))
pads.sort(key=lambda p: (p["x"] > 0, -p["y"], p["x"]))
for p in pads: print(p)
grp = {}
for side, sel in (("L", [p for p in pads if p["x"] < 0]), ("R", [p for p in pads if p["x"] > 0])):
    xs = [p["x"] for p in sel]; grp[side] = dict(n=len(sel), x_min=min(xs), x_max=max(xs), centre_x=round((min(xs) + max(xs)) / 2, 2),
                                             rows_y=sorted(set(round(p["y"]) for p in sel)))
print(grp)
res = dict(frame=reg["rect"]["note"] + "; CAD = /workspace/macpro62-cad/psu_board_outline.dxf. Lug-pad end = CAD +y (top tab).",
           calibration=reg["cal"], registration=reg["options"], chosen=reg["chosen"], edges=out,
           width=round(E["right"] - E["left"], 2), height=round(E["top_tab"] - E["bot_tab"], 2), holes=holes, lug_pads=pads, lug_groups=grp)
json.dump(res, open("psu_board.json", "w"), indent=1)
# ---- DXF ----
doc = ezdxf.new("R2010"); msp = doc.modelspace()
for n_, c_ in (("CAD_OUTLINE", 8), ("SCAN_OUTLINE", 1), ("HOLES", 5), ("LUG_PADS", 2), ("NOTES", 7)): doc.layers.add(n_, color=c_)
cad = ezdxf.readfile("/workspace/macpro62-cad/psu_board_outline.dxf")
for e in cad.modelspace():
    try: e2 = e.copy(); e2.dxf.layer = "CAD_OUTLINE"; msp.add_entity(e2)
    except Exception: pass
L, Rr = E["left"], E["right"]
poly = [(L, E["bot_main_L"]), (E["bot_tab_L_side"], E["bot_main_L"]), (E["bot_tab_L_side"], E["bot_tab"]), (E["bot_tab_R_side"], E["bot_tab"]),
        (E["bot_tab_R_side"], E["bot_main_R"]), (Rr, E["bot_main_R"]), (Rr, E["top_main_R"]), (E["top_tab_R_side"], E["top_main_R"]),
        (E["top_tab_R_side"], E["top_tab"]), (E["top_tab_L_side"], E["top_tab"]), (E["top_tab_L_side"], E["top_main_L"]), (L, E["top_main_L"])]
msp.add_lwpolyline([(float(a), float(b)) for a, b in poly], close=True, dxfattribs={"layer": "SCAN_OUTLINE"})
for k, (x, y) in holes.items(): msp.add_circle((x, y), 1.0, dxfattribs={"layer": "HOLES"}); msp.add_circle((x, y), 3.35, dxfattribs={"layer": "HOLES"})
for p in pads: msp.add_circle((p["x"], p["y"]), max(p["w"], p["h"]) / 2, dxfattribs={"layer": "LUG_PADS"})
for i, s in enumerate(["PSU board, CAD frame, COMPONENT-side view (solder scan mirrored) [Assumption: CAD drawn from component side].",
                       "Lug-pad end = CAD +y (top tab). SCAN_OUTLINE = traced rectilinear outline (corner radii not traced). +-0.5 mm."]):
    msp.add_text(s, height=1.6, dxfattribs={"layer": "NOTES"}).set_placement((-50, -90 - 3 * i))
doc.saveas("psu_board_cad_frame.dxf")
# ---- overlay ----
ov = im.copy()
for e in cad.modelspace():
    if e.dxftype() == "LINE": cv2.line(ov, toPX(e.dxf.start.x, e.dxf.start.y), toPX(e.dxf.end.x, e.dxf.end.y), (255, 160, 0), 2)
    elif e.dxftype() == "ARC":
        a0, a1 = e.dxf.start_angle, e.dxf.end_angle; a1 = a1 + 360 if a1 < a0 else a1
        pts = [toPX(e.dxf.center.x + e.dxf.radius * np.cos(np.radians(a)), e.dxf.center.y + e.dxf.radius * np.sin(np.radians(a))) for a in np.linspace(a0, a1, 20)]
        cv2.polylines(ov, [np.array(pts)], False, (255, 160, 0), 2)
    elif e.dxftype() == "CIRCLE": cv2.circle(ov, toPX(e.dxf.center.x, e.dxf.center.y), int(e.dxf.radius * K), (255, 160, 0), 2)
cv2.polylines(ov, [np.array([toPX(a, b) for a, b in poly])], True, (0, 0, 255), 2)
for k, (x, y) in holes.items(): cv2.circle(ov, toPX(x, y), int(3.35 * K), (0, 255, 0), 2)
for p in pads: cv2.circle(ov, toPX(p["x"], p["y"]), int(max(p["w"], p["h"]) / 2 * K), (0, 255, 255), 2)
for xm in range(-60, 61, 10): cv2.putText(ov, str(xm), (toPX(xm, 0)[0] - 8, 20), 0, 0.6, (0, 0, 255), 2)
for ym in range(-90, 101, 10): cv2.putText(ov, str(ym), (4, toPX(0, ym)[1] + 6), 0, 0.6, (0, 0, 255), 2)
cv2.putText(ov, "orange = CAD outline/holes, red = traced outline, green = screw heads, yellow = lug pads (component view)", (10, ov.shape[0] - 12), 0, 0.5, (0, 0, 255), 1)
cv2.imwrite("psu_board_overlay_cad_frame.png", ov)
print("width %.2f height %.2f" % (res["width"], res["height"]))
