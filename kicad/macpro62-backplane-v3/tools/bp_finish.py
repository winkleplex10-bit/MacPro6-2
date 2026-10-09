"""BP finish: work/bp_routed.kicad_pcb -> NC-pad nets (schematic parity), refs -> F.Fab, GND pours L1-L4,
stitching vias, fill -> backplane.kicad_pcb.   python3 tools/bp_finish.py [src]"""
import pcbnew, sys, math, os
sys.path.insert(0, "tools")
import bp_model as M
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
SRC = sys.argv[1] if len(sys.argv) > 1 else "work/bp_routed.kicad_pcb"
DST = sys.argv[2] if len(sys.argv) > 2 else "backplane.kicad_pcb"
MM = pcbnew.FromMM; mm = pcbnew.ToMM
b = pcbnew.LoadBoard(SRC)
KEEP = []
# 1. unconnected-(REF-PIN-PadN) nets for no-connect pins (KiCad naming)
parts = {p["ref"]: p for p in M.PARTS}
nnc = 0
for f in b.GetFootprints():
    p = parts.get(f.GetReference())
    if not p: continue
    names = {n: nm for n, nm, _ in M.SYMS[p["sym"]]["pins"]}
    for pd in f.Pads():
        if pd.GetNetname() or pd.GetNumber() not in names or pd.GetNumber() in p["nets"]: continue
        nn = "unconnected-(%s-%s-Pad%s)" % (f.GetReference(), names[pd.GetNumber()], pd.GetNumber())
        ni = b.FindNet(nn)
        if not ni:
            ni = pcbnew.NETINFO_ITEM(b, nn); b.Add(ni); KEEP.append(ni)
        pd.SetNet(ni); nnc += 1
# 1b. values / LCSC fields synced from bp_model (cost-down value merges after placement)
for f in b.GetFootprints():
    p = parts.get(f.GetReference())
    if not p: continue
    f.SetValue(p["value"])
    if p["lcsc"]:
        if f.HasField("LCSC"): f.SetField("LCSC", p["lcsc"])
        else:
            fl = pcbnew.PCB_FIELD(f, f.GetFieldCount(), "LCSC"); fl.SetText(p["lcsc"]); fl.SetVisible(False); fl.SetLayer(pcbnew.F_Fab); f.AddField(fl)
# 2. reference designators -> F.Fab (assembly drawing), values hidden on Fab
for f in b.GetFootprints():
    r = f.Reference(); r.SetLayer(pcbnew.F_Fab if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_Fab)
    r.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8))); r.SetTextThickness(MM(0.12))
# 2b. GND fan-out vias closer than 0.16 to another net's pad -> remove (pad joins the L1 pour)
from shapely.geometry import box as _box, LineString
from shapely import affinity as _aff
def padg(p):
    c = (mm(p.GetPosition().x), mm(p.GetPosition().y)); sx, sy = mm(p.GetSize().x), mm(p.GetSize().y)
    g = _box(c[0] - sx / 2, c[1] - sy / 2, c[0] + sx / 2, c[1] + sy / 2); a = p.GetOrientation().AsDegrees()
    return _aff.rotate(g, -a, origin=c) if abs(a) > 0.01 else g
opads = [(p.GetNetname(), padg(p)) for f in b.GetFootprints() for p in f.Pads()]
rm = 0; _gone = set()
for v in ([] if os.environ.get("BPF_STAGE") == "B" else [t for t in b.GetTracks() if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND"]):
    q = Point(mm(v.GetPosition().x), mm(v.GetPosition().y)).buffer(mm(v.GetWidth(pcbnew.F_Cu)) / 2)
    stubs = [t for t in b.GetTracks() if not isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND" and (t.GetStart() == v.GetPosition() or t.GetEnd() == v.GetPosition())]
    sg = [LineString([(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]).buffer(mm(t.GetWidth()) / 2) for t in stubs if t.GetLength() > 0]
    if any(n != "GND" and (g.distance(q) < 0.16 or any(g.distance(x) < 0.16 for x in sg)) for n, g in opads):
        for t in stubs:
            k = t.m_Uuid.AsString()
            if k not in _gone: _gone.add(k); KEEP.append(t); b.Remove(t)
        KEEP.append(v); b.Remove(v); rm += 1
print("removed GND fan-out vias (clearance)", rm)
if os.environ.get("BPF_STAGE") == "A": pcbnew.SaveBoard(DST, b); sys.exit(0)   # KiCad 9: SWIG types go stale after this pass; stage B runs in a fresh process
for f in b.GetFootprints():
    if f.GetReference() in ("J7", "J1", "J9", "J10"):
        for p in f.Pads():
            if p.GetNetname() == "GND": p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
# QFN GND pins without a fan-out (U1 VREG_PGND pin 62): 0.2 mm L1 dog-leg inward to the exposed pad, collision-checked
for f in b.GetFootprints():
    if f.GetReference() != "U1": continue
    ep = f.FindPadByNumber("81"); ec = (mm(ep.GetPosition().x), mm(ep.GetPosition().y)); eh = mm(ep.GetSize().x) / 2 - 0.15
    obs = []
    for t in b.GetTracks():
        if t.GetNetname() == "GND": continue
        if isinstance(t, pcbnew.PCB_VIA): obs.append(Point(mm(t.GetPosition().x), mm(t.GetPosition().y)).buffer(mm(t.GetWidth(pcbnew.F_Cu)) / 2))
        elif t.GetLayer() == pcbnew.F_Cu: obs.append(LineString([(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]).buffer(mm(t.GetWidth()) / 2))
    for q in f.Pads():
        if q.GetNetname() != "GND": obs.append(padg(q))
    obsu = unary_union(obs)
    for p in f.Pads():
        if p.GetNetname() != "GND" or p.GetNumber() == "81": continue
        pc = (mm(p.GetPosition().x), mm(p.GetPosition().y)); dx, dy = ec[0] - pc[0], ec[1] - pc[1]
        inw = (math.copysign(1, dx), 0) if abs(dx) > abs(dy) else (0, math.copysign(1, dy))
        done = False
        for d0 in (0.9, 1.2, 1.5, 0.7):
            a = (pc[0] + inw[0] * d0, pc[1] + inw[1] * d0)
            tgt = (min(max(a[0], ec[0] - eh), ec[0] + eh), min(max(a[1], ec[1] - eh), ec[1] + eh))
            for path in ([pc, a, tgt], [pc, a, (tgt[0], a[1]), tgt] if inw[1] else [pc, a, (a[0], tgt[1]), tgt]):
                g = LineString(path).buffer(0.1 + 0.11)
                if g.intersects(obsu.difference(padg(p).buffer(0.01))): continue
                for u, v in zip(path, path[1:]):
                    if math.hypot(u[0] - v[0], u[1] - v[1]) < 1e-3: continue
                    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(u[0]), MM(u[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(v[0]), MM(v[1])))
                    t.SetWidth(MM(0.2)); t.SetLayer(pcbnew.F_Cu); t.SetNet(b.FindNet("GND")); b.Add(t)
                done = True; break
            if done: break
        print("U1 GND pin", p.GetNumber(), "-> EP stub", "OK" if done else "FAILED (no clear path)")
# pads flagged starved_thermal in earlier DRC runs (list in env STARVED="REF-PAD,...") -> solid zone connection
for rp in [x for x in os.environ.get("STARVED", "").split(",") if x]:
    r_, n_ = rp.split("-"); f_ = b.FindFootprintByReference(r_)
    if f_ and f_.FindPadByNumber(n_): f_.FindPadByNumber(n_).SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
# 3. zones
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and z.GetZoneName() != "L3_3V3_SB": KEEP.append(z); b.Remove(z)
bb = b.GetBoardEdgesBoundingBox(); cx, cy = mm(bb.GetCenter().x), mm(bb.GetCenter().y); R = mm(bb.GetWidth()) / 2
gnd = b.FindNet("GND")
def zone(layer, prio, name):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd); z.SetAssignedPriority(prio); z.SetZoneName(name)
    z.SetLocalClearance(MM(0.2)); z.SetMinThickness(MM(0.2)); z.SetThermalReliefGap(MM(0.25)); z.SetThermalReliefSpokeWidth(MM(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
    for k in range(128):
        a = 2 * math.pi * k / 128; ps.Append(MM(cx + (R + 1) * math.cos(a)), MM(cy + (R + 1) * math.sin(a)))
    z.SetOutline(ps); b.Add(z); KEEP.extend([ps, z]); return z
if b.GetCopperLayerCount() == 6:   # BP v3 6L: In1 / In4 solid GND planes, signal-layer GND pours on L1/L3/L4/L6
    ZL = ((pcbnew.F_Cu, "L1_GND"), (pcbnew.In1_Cu, "L2_GND"), (pcbnew.In2_Cu, "L3_GND"), (pcbnew.In3_Cu, "L4_GND"), (pcbnew.In4_Cu, "L5_GND"), (pcbnew.B_Cu, "L6_GND"))
else:
    ZL = ((pcbnew.F_Cu, "L1_GND"), (pcbnew.In1_Cu, "L2_GND"), (pcbnew.In2_Cu, "L3_GND"), (pcbnew.B_Cu, "L4_GND"))
Z = {L: zone(L, 0, n) for L, n in ZL}
Z[pcbnew.In1_Cu].SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
if pcbnew.In4_Cu in Z: Z[pcbnew.In4_Cu].SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
def fill():
    f = pcbnew.ZONE_FILLER(b); f.Fill(b.Zones())
fill()
# 4. stitching vias on a 3 mm grid where all four GND fills are present (+ margin)
def filled(L):
    sp = Z[L].GetFilledPolysList(L); g = []
    for i in range(sp.OutlineCount()):
        o = sp.Outline(i); ext = [(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())]
        holes = []
        for h in range(sp.HoleCount(i)):
            hh = sp.CHole(i, h); holes.append([(mm(hh.CPoint(k).x), mm(hh.CPoint(k).y)) for k in range(hh.PointCount())])
        if len(ext) > 2: g.append(Polygon(ext, holes).buffer(0))
    return unary_union(g)
F = {L: filled(L) for L in Z}
both = F[pcbnew.F_Cu]
for L_ in Z:
    if L_ != pcbnew.F_Cu: both = both.intersection(F[L_])
ex = [Point(mm(t.GetPosition().x), mm(t.GetPosition().y)) for t in b.GetTracks() if isinstance(t, pcbnew.PCB_VIA)]
holes = [Point(mm(p.GetPosition().x), mm(p.GetPosition().y)).buffer(mm(p.GetDrillSize().x) / 2) for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSize().x > 0]
hu = unary_union(holes) if holes else Polygon()
kozs = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
def in_ko(x, y):
    for z in kozs:
        for dx, dy in ((0, 0), (0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5)):
            if z.Outline().Contains(pcbnew.VECTOR2I(MM(x + dx), MM(y + dy))): return True
    return False
ns = 0
step = 3.0
for i in range(-30, 31):
    for j in range(-30, 31):
        x, y = cx + i * step, cy + j * step
        q = Point(x, y)
        if not both.contains(q.buffer(0.225 + 0.25)): continue
        if any(q.distance(e) < 0.9 for e in ex) or hu.distance(q) < 0.6 or in_ko(x, y): continue
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(MM(0.45)); v.SetDrill(MM(0.25)); v.SetNet(gnd); b.Add(v); ex.append(q); ns += 1
fill()
# 5. silk: footprint silk outlines removed (dense 0402 field; JLC CPL + F.Fab assembly drawing carry the refs).
#    The exact in-board footprints are written to MP62_BP.pretty and every footprint is relinked to MP62_BP:<name>
#    so the board, the schematic and the project library agree (no lib_footprint_mismatch).
import os
nsilk = 0
for f in b.GetFootprints():
    for it in list(f.GraphicalItems()):
        if it.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS): f.Remove(it); nsilk += 1
    f.Value().SetLayer(pcbnew.F_Fab); f.Value().SetVisible(False)
    for fl in f.GetFields():
        if fl.GetName() not in ("Reference",): fl.SetLayer(pcbnew.F_Fab); fl.SetVisible(False)
        fl.SetTextAngle(f.GetOrientation()); fl.SetFPRelativePosition(pcbnew.VECTOR2I(0, 0))
LIB = os.path.abspath("MP62_BP.pretty")
io = pcbnew.PCB_IO_MGR.PluginFind(pcbnew.PCB_IO_MGR.KICAD_SEXP)
seen = set()
for f in sorted(b.GetFootprints(), key=lambda f: (round(f.GetOrientation().AsDegrees()) % 90 != 0)):
    nm = str(f.GetFPID().GetLibItemName())
    if nm not in seen:
        seen.add(nm)
        g = pcbnew.FOOTPRINT(f); g.SetParent(None)
        g.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T)); g.SetPosition(pcbnew.VECTOR2I(0, 0))
        for p in g.Pads(): p.SetNetCode(0)
        g.SetReference("REF**"); g.SetFPID(pcbnew.LIB_ID("", nm))
        io.FootprintSave(LIB, g); KEEP.append(g)
    f.SetFPID(pcbnew.LIB_ID("MP62_BP", nm))
print("silk removed", nsilk, "footprints exported", len(seen))
pcbnew.SaveBoard(DST, b)
print("nc nets", nnc, "stitch vias", ns, "saved", DST)
