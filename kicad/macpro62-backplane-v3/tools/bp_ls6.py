"""BP v3 6-layer low-speed (copy of bp_ls.py: 6L layer map, In2<->In3 broadside keep-outs, SATA0/USB2 fixed as HS obstacles, prep instead of fan).
BP low-speed / power routing stage.
  python3 tools/bp_ls.py fan     : work/bp_tuned -> GND fan-out vias -> work/bp_fan.kicad_pcb + patched work/bp_fan.dsn
  python3 tools/bp_ls.py route   : Freerouting work/bp_fan.dsn -> work/bp_fan.ses
  python3 tools/bp_ls.py import  : SES import -> work/bp_routed.kicad_pcb
Patch: GND dropped (pours + fan-out vias), L2 wire-keepout (solid GND), L4 wire-keepout under L3 HS copper,
L3 wire-keepout over L4 HS copper, 0.35 same-layer HS spacing keepouts (escape holes at non-HS pads/vias), 3V3_SB 0.3 class."""
import pcbnew, sys, re, math, os, subprocess, collections
from shapely.geometry import LineString, Point, box, Polygon
from shapely.ops import unary_union
from shapely import affinity
W = os.environ.get("W6", "work/ls6_")
L25 = [float(v) for v in os.environ["L25"].split(",")] if os.environ.get("L25") else None   # x0,y0,x1,y1 board mm
MM = pcbnew.FromMM; mm = pcbnew.ToMM
HS = re.compile(r"(FP|FS)_(TX|RX)\d+_[PN]$|(FP|FS)_REFCLK1?_[PN]$|SATA0_.*|USB2_.*")
LAY = {pcbnew.F_Cu: "L1_SIG_RX", pcbnew.In1_Cu: "L2_GND", pcbnew.In2_Cu: "L3_SIG_TX_PWR", pcbnew.In3_Cu: "L4_SIG_SLOTB", pcbnew.In4_Cu: "L5_GND", pcbnew.B_Cu: "L6_GND_BRK"}
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu, pcbnew.B_Cu]
VIA_D, VIA_H = 0.45, 0.25
KEEPZ = []

def P(v): return (mm(v.x), mm(v.y))
def pad_geom(p):
    c = P(p.GetPosition()); sx, sy = mm(p.GetSize().x), mm(p.GetSize().y)
    if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE: return Point(c).buffer(sx / 2, 12)
    g = box(c[0] - sx / 2, c[1] - sy / 2, c[0] + sx / 2, c[1] + sy / 2)
    ang = p.GetOrientation().AsDegrees()
    return affinity.rotate(g, -ang, origin=c) if abs(ang) > 0.01 else g

def copper(b):
    cu = {L: [] for L in CU}   # (net, geom)
    for t in b.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            g = Point(P(t.GetPosition())).buffer(mm(t.GetWidth(pcbnew.F_Cu)) / 2, 12)
            for L in CU: cu[L].append((t.GetNetname(), g))
        else:
            cu[t.GetLayer()].append((t.GetNetname(), LineString([P(t.GetStart()), P(t.GetEnd())]).buffer(mm(t.GetWidth()) / 2, 6)))
    for f in b.GetFootprints():
        for p in f.Pads():
            g = pad_geom(p)
            for L in CU:
                if p.IsOnLayer(L): cu[L].append((p.GetNetname(), g))
            if p.GetDrillSize().x > 0:
                for L in CU: cu[L].append((p.GetNetname() or "_hole", Point(P(p.GetPosition())).buffer(mm(p.GetDrillSize().x) / 2 + 0.1)))
    return cu

def fan():
    b = pcbnew.LoadBoard(W + "bp_tuned.kicad_pcb")
    for t in b.GetTracks(): t.SetLocked(True)
    edge = Polygon([(150 + 76.5 * math.cos(a / 90 * math.pi), 100 + 76.5 * math.sin(a / 90 * math.pi)) for a in range(180)])
    bb = b.GetBoardEdgesBoundingBox(); R = mm(bb.GetWidth()) / 2 - 0.6
    cx, cy = mm(bb.GetCenter().x), mm(bb.GetCenter().y)
    edge = Point(cx, cy).buffer(R, 64)
    cu = copper(b)
    # keep-out shapes (no vias): rule-area zones
    kos = []
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias():
            o = z.Outline(); pts = [P(o.CVertex(i)) for i in range(o.TotalVertices())]
            if len(pts) > 2: kos.append(Polygon(pts).buffer(0))
    ko = unary_union(kos) if kos else Polygon()
    gnd = b.FindNet("GND")
    vias_existing = [P(t.GetPosition()) for t in b.GetTracks() if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND"]
    tracks_gnd = [t for t in b.GetTracks() if not isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND"]
    added = 0; skipped = []
    allob = {L: unary_union([g for n, g in cu[L] if n != "GND"]) for L in CU}
    for f in b.GetFootprints():
        if f.IsDNP() and f.GetReference() in ("J7", "J8"): pass
        for p in f.Pads():
            if p.GetNetname() != "GND" or p.GetDrillSize().x > 0 or not p.IsOnLayer(pcbnew.F_Cu): continue
            g = pad_geom(p)
            if any(g.buffer(0.05).contains(Point(v)) for v in vias_existing): continue
            if any(g.buffer(0.02).intersects(LineString([P(t.GetStart()), P(t.GetEnd())])) for t in tracks_gnd if t.GetLayer() == pcbnew.F_Cu): continue
            c = P(p.GetPosition()); sx, sy = mm(p.GetSize().x), mm(p.GetSize().y)
            big = sx * sy > 4.0   # EP / big pads: via in pad (tented) is fine -> several
            cand = []
            if big:
                cand = [c]
            else:
                fc = P(f.GetPosition()); d0 = (c[0] - fc[0], c[1] - fc[1]); n0 = math.hypot(*d0) or 1
                for r in (0.0, 0.25, 0.5, 0.75, 1.0, 1.3):
                    for k in range(16):
                        a = math.atan2(d0[1], d0[0]) + (k // 2) * (1 if k % 2 else -1) * math.pi / 8
                        e = (max(sx, sy) / 2 + VIA_D / 2 + 0.12 + r)
                        cand.append((c[0] + math.cos(a) * e, c[1] + math.sin(a) * e))
            ok = None
            for q in cand:
                vg = Point(q).buffer(VIA_D / 2 + 0.12, 12)
                if not edge.contains(Point(q)) or vg.intersects(ko): continue
                if any(vg.intersects(allob[L]) for L in CU): continue
                tg = LineString([c, q]).buffer(0.15 + 0.1)
                if q != c and tg.intersects(allob[pcbnew.F_Cu]): continue
                ok = q; break
            if not ok: skipped.append(f.GetReference() + "-" + p.GetNumber()); continue
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(ok[0]), MM(ok[1]))); v.SetWidth(MM(VIA_D)); v.SetDrill(MM(VIA_H)); v.SetNet(gnd); b.Add(v)
            if ok != c:
                t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(c[0]), MM(c[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(ok[0]), MM(ok[1])))
                t.SetWidth(MM(0.3)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t); t.SetLocked(True)
                allob[pcbnew.F_Cu] = allob[pcbnew.F_Cu]  # GND copper is not an obstacle for GND
            v.SetLocked(True); vias_existing.append(ok); added += 1
            # new via is an obstacle for the next fan-outs of other nets? (only same net GND -> keep spacing between GND vias)
            for L in CU: allob[L] = allob[L].union(Point(ok).buffer(VIA_D / 2 + 0.05))
    print("GND fan-out vias added", added, "skipped", len(skipped), skipped)
    # L3 3V3_SB plane over the south (low-speed) half: y_pcb >= 116.2 (south of the J1 A-row TX vias at 115.4)
    if os.environ.get("PLANE", "1") == "1":
        z = pcbnew.ZONE(b); z.SetLayer(pcbnew.In2_Cu); z.SetNet(b.FindNet("3V3_SB")); z.SetAssignedPriority(5); z.SetZoneName("L3_3V3_SB")
        z.SetLocalClearance(MM(0.25)); z.SetMinThickness(MM(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        pts = [(cx + (R + 0.2) * math.cos(a / 64 * math.pi), cy + (R + 0.2) * math.sin(a / 64 * math.pi)) for a in range(129)]
        poly = Polygon(pts).intersection(box(cx - R - 1, 116.2, cx + R + 1, cy + R + 1))
        ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
        for q in list(poly.exterior.coords)[:-1]: ps.Append(MM(q[0]), MM(q[1]))
        z.SetOutline(ps); b.Add(z); KEEPZ.extend([z, ps])
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(W + "fan.kicad_pcb", b)
    dsn = W + "fan.dsn"
    b2 = pcbnew.LoadBoard(W + "fan.kicad_pcb")
    print("dsn", pcbnew.ExportSpecctraDSN(b2, dsn))
    patch(dsn, b2)

def patch(dsn, b):
    s = open(dsn).read()
    nets = {mm_.group(1): mm_.group(2).split() for mm_ in re.finditer(r"\(net (\S+)\n\s*\(pins ([^)]*)\)\n\s*\)", s)}
    drop = {"GND"} | {n for n in nets if HS.match(n)}   # HS nets are complete (locked) -> obstacles only
    s = re.sub(r"\(net (\S+)\n\s*\(pins ([^)]*)\)\n\s*\)", lambda m_: "" if m_.group(1) in drop else m_.group(0), s)
    ko = []
    def wire_ko(m_):
        lay, w, pts, n = m_.group(1), float(m_.group(2)), [float(v) for v in m_.group(3).split()], m_.group(4)
        if n not in drop: return m_.group(0)
        poly = LineString(list(zip(pts[0::2], pts[1::2]))).buffer(w / 2, cap_style=2, join_style=2)
        ko.append('    (keepout "" (polygon %s 0 %s))' % (lay, " ".join("%.0f %.0f" % c for c in poly.exterior.coords))); return ""
    s = re.sub(r"\(wire \(path (\S+) (\S+)\s+([-\d.\s]+)\)\(net (\S+)\)\(type fix\)\)", wire_ko, s)
    def via_ko(m_):
        if m_.group(4) not in drop: return m_.group(0)
        d = float(re.search(r"_(\d+):", m_.group(1)).group(1)); x, y = float(m_.group(2)), float(m_.group(3))
        for lay in [LAY[L] for L in ((pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu, pcbnew.B_Cu) if L25 else (pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.B_Cu))]: ko.append('    (keepout "" (circle %s %.0f %.0f %.0f))' % (lay, d, x, y))
        return ""
    s = re.sub(r'\(via "([^"]+)"\s+([-\d.]+) ([-\d.]+) \(net (\S+)\)\(type fix\)\)', via_ko, s)
    # HS copper keep-outs (DSN units um, y flipped)
    def D(pt): return (pt[0] * 1000, -pt[1] * 1000)
    hs = collections.defaultdict(list); holes = []
    for t in b.GetTracks():
        n = t.GetNetname()
        if isinstance(t, pcbnew.PCB_VIA):
            if not HS.match(n) and n != "GND": holes.append(Point(D(P(t.GetPosition()))).buffer(700))
            continue
        if HS.match(n): hs[t.GetLayer()].append(LineString([D(P(t.GetStart())), D(P(t.GetEnd()))]).buffer(mm(t.GetWidth()) * 500))
    for f in b.GetFootprints():
        for p in f.Pads():
            n = p.GetNetname()
            if n and not HS.match(n) and n != "GND": holes.append(Point(D(P(p.GetPosition()))).buffer(700 + 500 * max(mm(p.GetSize().x), mm(p.GetSize().y))))
    holes = unary_union(holes)
    def nohole(g):
        if g.geom_type != "Polygon": return [x for q in getattr(g, "geoms", []) for x in nohole(q)]
        if not g.interiors: return [g]
        hx = g.interiors[0].centroid.x
        x0, y0, x1, y1 = g.bounds
        out = []
        for bx in (box(x0 - 1, y0 - 1, hx, y1 + 1), box(hx, y0 - 1, x1 + 1, y1 + 1)):
            out += nohole(g.intersection(bx))
        return out
    def emit(geom, lay, kind="wire_keepout"):
        geoms = nohole(geom)
        k = 0
        for g in geoms:
            if g.area < 1e4: continue
            g = g.simplify(20)
            if g.geom_type != "Polygon": continue
            for ring in [g.exterior]:
                ko.append('    (%s "" (polygon %s 0 %s))' % (kind, lay, " ".join("%.0f %.0f" % c for c in ring.coords))); k += 1
        return k
    nko = collections.Counter()
    for L, gs in hs.items():
        u = unary_union(gs)
        nko[LAY[L]] += emit(u.buffer(350, join_style=2).difference(holes).difference(u.buffer(1)), LAY[L])   # same-layer spacing ring
        # broadside rule (6L): In2 and In3 are adjacent signal layers -> no LS wires over/under HS copper on the other one
        if L == pcbnew.In2_Cu: nko["L4_SIG_SLOTB"] += emit(u.buffer(600, join_style=2).difference(holes), "L4_SIG_SLOTB")
        if L == pcbnew.In3_Cu: nko["L3_SIG_TX_PWR"] += emit(u.buffer(600, join_style=2).difference(holes), "L3_SIG_TX_PWR")
    bb = b.GetBoardEdgesBoundingBox()
    x0, y0, x1, y1 = mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())
    if L25:
        # L2/L5 (GND planes) may carry LS wires locally: only inside the L25 window and >= 0.6 mm off HS copper on the
        # adjacent signal layers (L2: L1 + L3, L5: L4 + L6), so no HS pair loses its reference.
        wx0, wy0, wx1, wy1 = L25
        outside = box(D((x0 - 2, y1 + 2))[0], D((x0 - 2, y1 + 2))[1], D((x1 + 2, y0 - 2))[0], D((x1 + 2, y0 - 2))[1]).difference(
            box(D((wx0, wy1))[0], D((wx0, wy1))[1], D((wx1, wy0))[0], D((wx1, wy0))[1]))
        for gnd, adj in (("L2_GND", (pcbnew.F_Cu, pcbnew.In2_Cu)), ("L5_GND", (pcbnew.In3_Cu, pcbnew.B_Cu))):
            g = unary_union([outside] + [unary_union(hs[L]).buffer(600, join_style=2) for L in adj if hs.get(L)])
            nko[gnd] += emit(g.difference(holes), gnd)
    else:
        s = s.replace("(layer L2_GND\n      (type signal)", "(layer L2_GND\n      (type power)")
        s = s.replace("(layer L5_GND\n      (type signal)", "(layer L5_GND\n      (type power)")   # solid GND plane: no wires (a board-wide wire_keepout also blocked vias in FR)
    # rule areas: (a) the EDGE_RING via keep-out is a ring (polygon + window) -> FR ignores the window and blocks vias on the
    # whole board -> replace by 48 hole-free annular sectors; (b) footprint-only rule areas (MCIO ribbon) must not block wires.
    def blocks(txt, key):
        out = []; i = 0
        while True:
            j = txt.find(key, i)
            if j < 0: return out
            d = 0; k = j
            while True:
                if txt[k] == "(": d += 1
                elif txt[k] == ")":
                    d -= 1
                    if d == 0: break
                k += 1
            out.append((j, k + 1)); i = k + 1
    for z in b.Zones():
        if not z.GetIsRuleArea(): continue
        o = z.Outline(); v0 = D(P(o.CVertex(0)))
        tag = "%.0f %.0f" % v0
        for key in ('(keepout ""', '(via_keepout ""', '(wire_keepout ""'):
            for (j, k) in reversed(blocks(s, key)):
                blk = s[j:k]
                if tag.split()[0] not in blk: continue
                if not z.GetDoNotAllowTracks() and not z.GetDoNotAllowVias():
                    s = s[:j] + s[k:]
                elif "(window" in blk:
                    lay = blk.split("(polygon ")[1].split()[0]
                    oc = [P(o.COutline(0).CPoint(q)) for q in range(o.COutline(0).PointCount())]
                    hc = [P(o.CHole(0, 0).CPoint(q)) for q in range(o.CHole(0, 0).PointCount())]
                    ring = Polygon(oc, [hc]).buffer(0)
                    ccx, ccy = mm(z.GetBoundingBox().GetCenter().x), mm(z.GetBoundingBox().GetCenter().y)
                    rep = []
                    for sct in range(48):
                        a0, a1 = 2 * math.pi * sct / 48, 2 * math.pi * (sct + 1) / 48
                        wedge = Polygon([(ccx, ccy)] + [(ccx + 200 * math.cos(a0 + (a1 - a0) * t / 4), ccy + 200 * math.sin(a0 + (a1 - a0) * t / 4)) for t in range(5)])
                        g = ring.intersection(wedge)
                        if g.geom_type == "Polygon" and g.area > 0:
                            rep.append('    (via_keepout "" (polygon %s 0 %s))' % (lay, " ".join("%.0f %.0f" % D(c) for c in g.exterior.coords)))
                    s = s[:j] + "\n".join(rep) + s[k:]
    print("keepouts", len(ko), dict(nko))
    k = s.index("    (via ", s.index("(structure"))
    s = s[:k] + "\n".join(ko) + "\n" + s[k:]
    # 3V3_SB / DVDD -> own 0.3 class (0.4-pitch QFN pins)
    m_ = re.search(r"\(class PWR ([^(]*)", s)
    names = m_.group(1).split()
    keep = [n for n in names if n not in ("3V3_SB",)]
    s = s[:m_.start()] + "(class PWR " + " ".join(keep) + "\n      " + s[m_.end():]
    s = re.sub(r"\(rule\s*\(width 500\)\s*\(clearance 150\)\s*\)", "(rule (width 300) (clearance 150))", s)   # FR cannot neck down into 0.5/0.6-pitch pins; widened after routing
    m2 = re.search(r"\(class kicad_default ([^(]*)", s)
    dn = [n for n in m2.group(1).split() if n not in ("DVDD",)]
    if "(class PWR_FINE" in s: m2 = None
    if m2: s = s[:m2.start()] + '(class PWR3 3V3_SB DVDD\n      (circuit\n        (use_via "Via[0-3]_450:250_um")\n      )\n      (rule (width 200) (clearance 100))\n    )\n    ' + \
        "(class kicad_default " + " ".join(dn) + "\n      " + s[m2.end():]
    open(dsn, "w").write(s)

def route(passes=int(os.environ.get("PASSES", "200"))):
    import json as _j
    cfg = "/tmp/freerouting/freerouting.json"   # FR 2.1 takes max_passes from its settings file (CLI value ignored)
    d = _j.load(open(cfg)); d["router"]["max_passes"] = passes; d["router"].setdefault("optimizer", {})["max_passes"] = int(os.environ.get("OPT", "3")); d["gui"]["enabled"] = False
    d["router"]["job_timeout"] = os.environ.get("FRTIME", "00:08:00")
    _j.dump(d, open(cfg, "w"), indent=2)
    jar = "/workspace/tools/fr-2.1.0.jar"
    r = subprocess.run(["java", "-jar", jar, "-de", W + "fan.dsn", "-do", W + "fan.ses", "--router.max_passes=%d" % passes, "--router.job_timeout=%s" % os.environ.get("FRTIME", "00:08:00"), "-mt", "1", "--gui.enabled=false"],
                       capture_output=True, text=True, timeout=7000)
    open(W + "freerouting.log", "w").write(r.stdout + r.stderr); print("route", r.returncode, os.path.exists(W + "fan.ses"))

def imp():
    b = pcbnew.LoadBoard(W + "fan.kicad_pcb")
    print("ses", pcbnew.ImportSpecctraSES(b, W + "fan.ses"))
    pcbnew.SaveBoard(W + "routed.kicad_pcb", b)

def redsn():
    """resume: work/bp_routed (previous FR result, LS wires unlocked) -> bp_fan.kicad_pcb + DSN, so the next FR run continues from it"""
    import shutil
    shutil.copy(W + "routed.kicad_pcb", W + "fan.kicad_pcb")
    b2 = pcbnew.LoadBoard(W + "fan.kicad_pcb"); dsn = W + "fan.dsn"
    print("dsn", pcbnew.ExportSpecctraDSN(b2, dsn)); patch(dsn, b2)

if __name__ == "__main__":
    {"fan": fan, "route": route, "import": imp, "redsn": redsn}[sys.argv[1]]()
