"""S2X low-speed / power stage (adapted from macpro62-backplane/tools/bp_ls.py).
  python3 tools/s2x_ls.py fan     : work/s2x_hs -> GND fan-out vias (B pads) + +12V_IN pad vias + pre-FR pours (PH_A/B, 3V3_A/B on B,
                                     +12V_IN on L1) -> work/s2x_fan.kicad_pcb + patched work/s2x_fan.dsn
  python3 tools/s2x_ls.py route   : Freerouting (job_timeout) work/s2x_fan.dsn -> work/s2x_fan.ses   (run under nohup)
  python3 tools/s2x_ls.py import  : SES import -> work/s2x_routed.kicad_pcb
DSN patch: GND + HS nets dropped (HS copper / GND vias -> keepouts), In1/In2 = solid GND (power layers, no wires),
0.35 same-layer HS spacing keepouts, footprint-only rule areas removed, power classes narrowed for routing into fine-pitch pins
(the high-current paths are the pours)."""
import pcbnew, sys, re, math, os, subprocess, collections, json
from shapely.geometry import LineString, Point, box, Polygon
from shapely.ops import unary_union
from shapely import affinity
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W = "work/"
MM = pcbnew.FromMM; mm = pcbnew.ToMM
OX, OY = 60.0, 190.0
HS = re.compile(r"^(PCIE_[AB]_[HM]TX\d_[PN]|REFCLK_[AB]_[PN])$")
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
LAYN = {pcbnew.F_Cu: "F.Cu", pcbnew.In1_Cu: "In1.Cu", pcbnew.In2_Cu: "In2.Cu", pcbnew.B_Cu: "B.Cu"}
VIA_D, VIA_H = 0.45, 0.25
KEEPZ = []
def K(x, y): return pcbnew.VECTOR2I(MM(OX + x), MM(OY - y))
def KP(x, y): return (OX + x, OY - y)                  # module -> KiCad mm
def P(v): return (mm(v.x), mm(v.y))                   # KiCad mm
def R(x0, y0, x1, y1): return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
# ---- pre-FR pours (module coordinates) ----
PH_A = unary_union([R(17.0, 64.8, 27.6, 69.0), R(24.4, 64.8, 27.6, 74.6), R(17.0, 69.0, 19.0, 70.75)])
PH_B = Polygon([(88.6, 64.8), (94.2, 64.8), (94.2, 69.2), (91.7, 69.2), (91.7, 73.4), (94.4, 73.4), (94.4, 74.6), (88.6, 74.6)])
def v33(lx0, lx1, strip, col, band, notch, tabs):
    g = unary_union([R(lx0, 69.2, lx1, 77.7), R(*strip), R(*col), R(*band)] + [R(*t) for t in tabs])
    return g.difference(R(*notch))
P3A = v33(19.4, 22.4, (19.4, 75.0, 34.4, 77.7), (28.6, 59.6, 34.4, 77.7), (28.6, 59.6, 56.6, 63.9), (42.6, 62.2, 49.4, 64.5),
          [(36.6, 57.6, 41.4, 59.7), (53.6, 57.6, 55.4, 59.7)])
P3B = v33(83.4, 86.6, (79.6, 75.0, 90.4, 77.7), (80.4, 59.6, 83.0, 77.7), (58.6, 59.6, 83.0, 63.9), (66.6, 62.2, 73.4, 64.5),
          [(60.6, 57.6, 65.4, 59.7), (77.6, 57.6, 79.4, 59.7)])
P12 = R(0.6, 141.2, 103.4, 154.0)
# PH / 3V3 pours were replaced by the locked power skeleton (tools/route_pwr.py): FR cut the B pours into islands.
POURS = [("+12V_IN", pcbnew.F_Cu, P12, 6)]
def add_pours(b):
    for net, L, g, pr in POURS:
        for poly in getattr(g, "geoms", [g]):
            z = pcbnew.ZONE(b); z.SetLayer(L); z.SetNet(b.FindNet(net)); z.SetAssignedPriority(pr); z.SetZoneName("P_" + net)
            z.SetLocalClearance(MM(0.2)); z.SetMinThickness(MM(0.2)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
            ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
            for q in list(poly.exterior.coords)[:-1]: ps.Append(K(*q))
            z.SetOutline(ps); b.Add(z); KEEPZ.extend([z, ps])

def pad_geom(p):
    L = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    try:
        sp = p.GetEffectivePolygon(L, pcbnew.ERROR_OUTSIDE); gs = []
        for i in range(sp.OutlineCount()):
            o = sp.Outline(i); gs.append(Polygon([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())]).buffer(0))
        if gs: return unary_union(gs)
    except Exception as e: pass
    c = P(p.GetPosition()); sx, sy = mm(p.GetSize().x), mm(p.GetSize().y)
    if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE: return Point(c).buffer(sx / 2, 12)
    g = box(c[0] - sx / 2, c[1] - sy / 2, c[0] + sx / 2, c[1] + sy / 2)
    ang = p.GetOrientation().AsDegrees()
    return affinity.rotate(g, -ang, origin=c) if abs(ang) > 0.01 else g
def copper(b):
    cu = {L: [] for L in CU}
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
    b = pcbnew.LoadBoard(W + os.environ.get("FANSRC", "s2x_pwr.kicad_pcb"))
    for t in b.GetTracks(): t.SetLocked(True)
    g = json.load(open("/workspace/kicad/macpro62-storage-face/tools/face_geom.json"))
    edge = Polygon([KP(*q) for q in g["outline_poly"]]).buffer(-0.7)
    die = Polygon([KP(*q) for q in g["DIE_PAD"]]).buffer(0.3)
    cu = copper(b)
    # other-net pours are obstacles for fan-out vias (keeps the pours whole)
    pours_k = {net: affinity.scale(affinity.translate(pg, 0, 0), 1, 1) for net, L, pg, pr in POURS}
    def kpoly(pg): return unary_union([Polygon([KP(*q) for q in p.exterior.coords]) for p in getattr(pg, "geoms", [pg])])
    pk = {net: kpoly(pg) for net, L, pg, pr in POURS}
    added = collections.Counter(); skipped = []
    def place(net, f, p, nvia, layer_stub=pcbnew.B_Cu, avoid_die=False):
        c = P(p.GetPosition()); sx, sy = mm(p.GetSize().x), mm(p.GetSize().y); pg = pad_geom(p)
        ob = unary_union([gg for L in CU for n, gg in cu[L] if n != net])
        fc = P(f.GetPosition()); d0 = (c[0] - fc[0], c[1] - fc[1])
        if math.hypot(*d0) < 0.05: d0 = (0, 1)
        got = 0; mine = []
        for r in (0.0, 0.25, 0.5, 0.8, 1.2):
            for k in range(16):
                a = math.atan2(d0[1], d0[0]) + (k // 2) * (1 if k % 2 else -1) * math.pi / 8
                e = (max(sx, sy) / 2 + VIA_D / 2 + 0.12 + r) if max(sx, sy) < 2.0 else (min(sx, sy) / 2 + VIA_D / 2 + 0.12 + r)
                q = (c[0] + math.cos(a) * e, c[1] + math.sin(a) * e)
                vg = Point(q).buffer(VIA_D / 2 + 0.11, 12)
                if any(math.hypot(q[0] - m0[0], q[1] - m0[1]) < 0.9 for m0 in mine): continue
                if not edge.contains(Point(q)) or vg.intersects(ob) or (avoid_die and vg.intersects(die)): continue
                # stub: from pad edge point to via, 0.3 wide
                st = LineString([c, q]).buffer(0.15 + 0.11)
                if st.intersects(ob.difference(pg.buffer(0.001))): continue
                v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(q[0]), MM(q[1]))); v.SetWidth(pcbnew.F_Cu, MM(VIA_D)); v.SetDrill(MM(VIA_H))
                v.SetNet(b.FindNet(net)); v.SetLocked(True); b.Add(v)
                t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(c[0]), MM(c[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(q[0]), MM(q[1])))
                t.SetWidth(MM(0.3)); t.SetLayer(layer_stub); t.SetNet(b.FindNet(net)); t.SetLocked(True); b.Add(t)
                for L in CU: cu[L].append((net, Point(q).buffer(VIA_D / 2)))
                cu[layer_stub].append((net, LineString([c, q]).buffer(0.15)))
                # keep the next via of the same pad >= 0.9 away
                for L in CU: cu[L].append(("_sp", Point(q).buffer(0.2)))
                got += 1; added[net] += 1; mine.append(q)
                if got >= nvia: return got
        if not got: skipped.append(f.GetReference() + "-" + p.GetNumber())
        return got
    isl = {}
    for z in b.Zones():
        if z.GetZoneName() in ("L3_3V3_A", "L3_3V3_B"):
            o = z.Outline(); isl[z.GetNetname()] = Polygon([P(o.CVertex(i)) for i in range(o.TotalVertices())]).buffer(-0.5)
    gvias = [P(t.GetPosition()) for t in b.GetTracks() if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND"]
    gtr = [t for t in b.GetTracks() if not isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND"]
    for f in b.GetFootprints():
        if f.GetReference() in ("J1",): continue          # J1 GND handled in route_hs
        for p in f.Pads():
            n = p.GetNetname()
            if p.GetDrillSize().x > 0 or not p.IsOnLayer(pcbnew.B_Cu): continue
            if n == "GND":
                pg = pad_geom(p)
                if any(pg.buffer(0.05).contains(Point(v)) for v in gvias): continue
                if any(pg.buffer(0.02).intersects(LineString([P(t.GetStart()), P(t.GetEnd())])) for t in gtr): continue
                if f.GetReference().startswith("MH"): continue  # standoff: PTH barrel
                a = mm(p.GetSize().x) * mm(p.GetSize().y)
                place("GND", f, p, 3 if a > 4 else (2 if a > 1.2 else 1))
            elif n == "+12V_IN" and pk["+12V_IN"].contains(Point(P(p.GetPosition()))) and f.GetReference() != "U1":
                place(n, f, p, 2)
            elif n in ("3V3_A", "3V3_B") and f.GetReference()[0] in "CRQ" and f.GetReference() not in ("R14", "R17") \
                    and isl[n].contains(Point(P(p.GetPosition()))) and not any(Point(P(p.GetPosition())).distance(Point(P(t.GetStart()))) < 0.05
                    or Point(P(p.GetPosition())).distance(Point(P(t.GetEnd()))) < 0.05 for t in b.GetTracks() if t.GetNetname() == n):
                place(n, f, p, 1, avoid_die=True)
    print("fan-out vias", dict(added), "skipped", skipped)
    add_pours(b)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(W + "s2x_fan.kicad_pcb", b)
    b2 = pcbnew.LoadBoard(W + "s2x_fan.kicad_pcb"); dsn = W + "s2x_fan.dsn"
    print("dsn", pcbnew.ExportSpecctraDSN(b2, dsn)); patch(dsn, b2)

def patch(dsn, b):
    s = open(dsn).read()
    nets = {m_.group(1): m_.group(2).split() for m_ in re.finditer(r"\(net (\S+)\n\s*\(pins ([^)]*)\)\n\s*\)", s)}
    drop = {"GND"} | {n for n in nets if HS.match(n)}
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
        for lay in LAYN.values(): ko.append('    (keepout "" (circle %s %.0f %.0f %.0f))' % (lay, d, x, y))
        return ""
    s = re.sub(r'\(via "([^"]+)"\s+([-\d.]+) ([-\d.]+) \(net (\S+)\)\(type fix\)\)', via_ko, s)
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
        hx = g.interiors[0].centroid.x; x0, y0, x1, y1 = g.bounds; out = []
        for bx in (box(x0 - 1, y0 - 1, hx, y1 + 1), box(hx, y0 - 1, x1 + 1, y1 + 1)): out += nohole(g.intersection(bx))
        return out
    nko = collections.Counter()
    for L, gs in hs.items():
        u = unary_union(gs)
        for gg in nohole(u.buffer(350, join_style=2).difference(holes).difference(u.buffer(1))):
            if gg.area < 1e4: continue
            gg = gg.simplify(20)
            if gg.geom_type != "Polygon": continue
            ko.append('    (wire_keepout "" (polygon %s 0 %s))' % (LAYN[L], " ".join("%.0f %.0f" % c for c in gg.exterior.coords))); nko[LAYN[L]] += 1
    for L in ("In1.Cu", "In2.Cu"):
        s = s.replace("(layer %s\n      (type signal)" % L, "(layer %s\n      (type power)" % L)
    # footprint-only rule areas -> remove from DSN
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
    nrm = 0
    for z in b.Zones():
        if not z.GetIsRuleArea() or z.GetDoNotAllowTracks() or z.GetDoNotAllowVias(): continue
        o = z.Outline(); tag = "%.0f" % D(P(o.CVertex(0)))[0]
        for key in ('(keepout ""', '(via_keepout ""', '(wire_keepout ""'):
            for (j, k) in reversed(blocks(s, key)):
                if tag in s[j:k]: s = s[:j] + s[k:]; nrm += 1
    print("keepouts", len(ko), dict(nko), "fp-only rule areas removed", nrm)
    k = s.index("    (via ", s.index("(structure"))
    s = s[:k] + "\n".join(ko) + "\n" + s[k:]
    # class widths for routing (pours carry the current)
    def setrule(cls, w, c):
        nonlocal s
        m_ = re.search(r"\(class %s [^(]*\(circuit[^)]*\)[^)]*\)\s*\(rule\s*\(width [\d.]+\)\s*\(clearance [\d.]+\)" % re.escape(cls), s)
        if not m_: print("class not found", cls); return
        blk = re.sub(r"\(width [\d.]+\)", "(width %d)" % w, m_.group(0)); blk = re.sub(r"\(clearance [\d.]+\)", "(clearance %d)" % c, blk)
        s = s[:m_.start()] + blk + s[m_.end():]
    setrule("PWR_12V", 500, 100); setrule("PWR_3V3", 500, 150); setrule("PWR_AUX", 300, 120)
    open(dsn, "w").write(s)

def route():
    """kept for reference; FR 2.1 takes job_timeout / max_passes from /tmp/freerouting/freerouting.json (CLI flags are overridden).
    Preferred: run java directly under nohup (see PROGRESS.md)."""
    passes = int(os.environ.get("PASSES", "100")); tmo = os.environ.get("FRTIME", "00:10:00")
    cfg = os.path.expanduser("/tmp/freerouting/freerouting.json")
    if os.path.exists(cfg):
        d = json.load(open(cfg)); d.setdefault("router", {})["max_passes"] = passes; d["router"]["job_timeout"] = tmo
        d["router"].setdefault("optimizer", {})["max_passes"] = int(os.environ.get("OPT", "2")); d.setdefault("gui", {})["enabled"] = False
        json.dump(d, open(cfg, "w"), indent=2)
    cmd = ["java", "-jar", "/workspace/tools/fr-2.1.0.jar", "-de", W + "s2x_fan.dsn", "-do", W + "s2x_fan.ses", "--router.max_passes=%d" % passes,
           "--router.job_timeout=%s" % tmo, "-mt", "1", "--gui.enabled=false"]
    print(" ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=7000)
    open(W + "s2x_freerouting.log", "w").write(r.stdout + r.stderr); print("route", r.returncode, os.path.exists(W + "s2x_fan.ses"))

def imp():
    b = pcbnew.LoadBoard(W + "s2x_fan.kicad_pcb")
    print("ses", pcbnew.ImportSpecctraSES(b, W + "s2x_fan.ses"))
    pcbnew.SaveBoard(W + "s2x_routed.kicad_pcb", b)

if __name__ == "__main__":
    {"fan": fan, "route": route, "import": imp}[sys.argv[1]]()
