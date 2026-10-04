#!/usr/bin/env python3
"""Minimal LCSC/EasyEDA (std 6.x JSON) -> KiCad 9 SMD footprint converter (D-IO17, 2026-10-04).
Land patterns are the JLCEDA/EasyEDA Official Library (https://lceda.cn/ , https://easyeda.com) - credited in each footprint descr.
Handles SMD RECT (corner points) and OVAL (centre-line points + width) pads on the top layer; exposed pad = the largest pad (paste reduced to
~60 % area with 4 windows). The footprint is re-centred on the pad bounding box and rotated in 90 deg steps so pin 1 is the top pad of the
left column with the numbering running down that side (IPC / KiCad convention). EasyEDA unit = 10 mil = 0.254 mm."""
import json, math, os, sys
U = 0.254
def load(src):
    d = json.load(open(src))["result"]; pk = d["packageDetail"]; return d, pk, pk["dataStr"]
def pads_of(ds):
    out = []
    for s in ds["shape"]:
        f = s.split("~")
        if f[0] != "PAD" or f[6] != "1": continue
        shp, num = f[1], f[8]; pts = [float(v) for v in f[10].split()]
        P = [(pts[i] * U, pts[i + 1] * U) for i in range(0, len(pts), 2)]
        if shp == "RECT" or shp == "POLYGON":
            xs = [p[0] for p in P]; ys = [p[1] for p in P]
            out.append(dict(num=num, shape="rect", c=((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2), sx=max(xs) - min(xs), sy=max(ys) - min(ys)))
        elif shp == "OVAL":
            w = min(float(f[4]), float(f[5])) * U; (x1, y1), (x2, y2) = P[0], P[1]; L = math.hypot(x2 - x1, y2 - y1) + w
            horiz = abs(x2 - x1) > abs(y2 - y1)
            out.append(dict(num=num, shape="oval" if L > w + 1e-6 else "circle", c=((x1 + x2) / 2, (y1 + y2) / 2), sx=L if horiz else w, sy=w if horiz else L))
        else: raise ValueError(shp)
    return out
def normalise(pads):
    xs = [p["c"][0] - p["sx"] / 2 for p in pads] + [p["c"][0] + p["sx"] / 2 for p in pads]
    ys = [p["c"][1] - p["sy"] / 2 for p in pads] + [p["c"][1] + p["sy"] / 2 for p in pads]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    for p in pads: p["c"] = (p["c"][0] - cx, p["c"][1] - cy)
    def rot(p, k):   # k x 90 deg (KiCad y down): (x, y) -> (-y, x) per step
        x, y = p["c"]; sx, sy = p["sx"], p["sy"]
        for _ in range(k): x, y, sx, sy = -y, x, sy, sx
        return dict(p, c=(round(x / 0.01) * 0.01 + 0.0, round(y / 0.01) * 0.01 + 0.0), sx=round(sx, 3), sy=round(sy, 3))
    byn = lambda L, n: [q for q in L if q["num"] == n][0]
    for k in range(4):
        R = [rot(p, k) for p in pads]; p1, p2 = byn(R, "1"), byn(R, "2"); xmin = min(q["c"][0] for q in R if q["sx"] * q["sy"] < 4)
        if abs(p1["c"][0] - xmin) < 1e-3 and p2["c"][1] > p1["c"][1] and abs(p2["c"][0] - p1["c"][0]) < 1e-3: return R, k
    raise RuntimeError("pin-1 orientation not found")
def write(src, name, out_dir, descr, tags, lcsc, mpn):
    d, pk, ds = load(src); pads, k = normalise(pads_of(ds))
    ep = max(pads, key=lambda p: p["sx"] * p["sy"])
    L = ['(footprint "%s"' % name, '  (version 20241229)', '  (generator "mp62_io")', '  (layer "F.Cu")',
         '  (descr "%s Land pattern from the JLCEDA/EasyEDA Official Library (https://lceda.cn/ , https://easyeda.com), package %s, LCSC %s; converted by tools/easyeda_fp.py.")' % (descr, pk["title"], lcsc),
         '  (tags "%s")' % tags,
         '  (property "Reference" "REF**" (at 0 %.2f 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))' % (-max(abs(p["c"][1]) + p["sy"] / 2 for p in pads) - 1.0),
         '  (property "Value" "%s" (at 0 %.2f 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))' % (mpn, max(abs(p["c"][1]) + p["sy"] / 2 for p in pads) + 1.0),
         '  (property "LCSC" "%s" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 0.6 0.6) (thickness 0.1))))' % lcsc,
         '  (attr smd)']
    for p in sorted(pads, key=lambda q: int(q["num"])):
        if p is ep:
            L.append('  (pad "%s" smd rect (at %.3f %.3f) (size %.3f %.3f) (layers "F.Cu" "F.Mask") (zone_connect 2))' % (p["num"], *p["c"], p["sx"], p["sy"]))
            # 4 paste windows (~ 60 % of the EP)
            wx, wy = p["sx"] * 0.39, p["sy"] * 0.39
            for sx_ in (-1, 1):
                for sy_ in (-1, 1):
                    L.append('  (pad "" smd rect (at %.3f %.3f) (size %.3f %.3f) (layers "F.Paste"))' % (p["c"][0] + sx_ * p["sx"] / 4.1, p["c"][1] + sy_ * p["sy"] / 4.1, wx, wy))
        else:
            sh = "roundrect" if p["shape"] == "rect" else p["shape"]
            L.append('  (pad "%s" smd %s (at %.3f %.3f) (size %.3f %.3f) (layers "F.Cu" "F.Paste" "F.Mask")%s)' % (p["num"], sh, *p["c"], p["sx"], p["sy"], ' (roundrect_rratio 0.25)' if sh == "roundrect" else ""))
    body = float(pk["title"].split("_L")[1].split("-")[0]) if "_L" in pk["title"] else None
    bw = float(pk["title"].split("-W")[1].split("-")[0]) if "-W" in pk["title"] else body
    hx, hy = (body or 4) / 2, (bw or 4) / 2
    L.append('  (fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))' % (-hx, -hy, hx, hy))
    ext_x = max(abs(p["c"][0]) + p["sx"] / 2 for p in pads); ext_y = max(abs(p["c"][1]) + p["sy"] / 2 for p in pads)
    cx_, cy_ = max(ext_x, hx) + 0.25, max(ext_y, hy) + 0.25
    L.append('  (fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))' % (-cx_, -cy_, cx_, cy_))
    p1 = [p for p in pads if p["num"] == "1"][0]
    L.append('  (fp_circle (center %.3f %.3f) (end %.3f %.3f) (stroke (width 0.12) (type solid)) (fill yes) (layer "F.SilkS"))' % (p1["c"][0] - p1["sx"] / 2 - 0.35, p1["c"][1] - 0.35, p1["c"][0] - p1["sx"] / 2 - 0.25, p1["c"][1] - 0.35))
    L.append('  (fp_line (start %.3f %.3f) (end %.3f %.3f) (stroke (width 0.1) (type solid)) (layer "F.Fab"))' % (-hx, -hy + 0.6, -hx + 0.6, -hy))
    L.append('  (fp_text user "${REFERENCE}" (at 0 0 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.09))))')
    L.append(')')
    fn = os.path.join(out_dir, name + ".kicad_mod"); open(fn, "w").write("\n".join(L) + "\n")
    print("wrote", fn, "pads", len(pads), "rot90 x", k, "EP %.2f x %.2f" % (ep["sx"], ep["sy"]), "p1", p1["c"], "pad", (p1["sx"], p1["sy"]))
    return fn
