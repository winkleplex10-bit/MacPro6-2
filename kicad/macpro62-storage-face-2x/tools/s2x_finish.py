"""S2X finish (adapted from backplane bp_finish.py): work/s2x_clean.kicad_pcb -> NC-pad nets (schematic parity), values/LCSC sync,
refs -> Fab, GND pours on all 4 layers (pre-FR power pours kept), thermal via arrays (gap-pad areas on B, die pad on L1), stitching vias,
footprint silk removed, in-board footprints exported to MP62_S2X.pretty + relinked, filled -> macpro62-storage-face-2x.kicad_pcb.
  python3 tools/s2x_finish.py [src] [dst]"""
import pcbnew, sys, math, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import model as M
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from s2x_ls import pad_geom, copper, CU, KP
SRC = sys.argv[1] if len(sys.argv) > 1 else "work/s2x_clean.kicad_pcb"
DST = sys.argv[2] if len(sys.argv) > 2 else "macpro62-storage-face-2x.kicad_pcb"
MM = pcbnew.FromMM; mm = pcbnew.ToMM
b = pcbnew.LoadBoard(SRC); KEEP = []
gnd = b.FindNet("GND")
# 1. NC nets
parts = {p["ref"]: p for p in M.PARTS}; nnc = 0
for f in b.GetFootprints():
    p = parts.get(f.GetReference())
    if not p: continue
    names = {n: nm for n, nm, _ in M.SYMS[p["sym"]]["pins"]}
    for pd in f.Pads():
        if pd.GetNetname() or pd.GetNumber() not in names or pd.GetNumber() in p["nets"]: continue
        nn = "unconnected-(%s-%s-Pad%s)" % (f.GetReference(), names[pd.GetNumber()], pd.GetNumber())
        ni = b.FindNet(nn)
        if not ni: ni = pcbnew.NETINFO_ITEM(b, nn); b.Add(ni); KEEP.append(ni)
        pd.SetNet(ni); nnc += 1
# 1b. values / LCSC
for f in b.GetFootprints():
    p = parts.get(f.GetReference())
    if not p: continue
    f.SetValue(p["value"])
    if p["lcsc"]: f.SetField("LCSC", p["lcsc"])
# 2. refs on Fab
for f in b.GetFootprints():
    r = f.Reference(); r.SetLayer(pcbnew.F_Fab if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_Fab)
    r.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8))); r.SetTextThickness(MM(0.12))
# 3. GND zones on all layers (whole outline), pre-FR power pours (priority 6) kept
g = json.load(open("/workspace/kicad/macpro62-storage-face/tools/face_geom.json"))
outline = [KP(*q) for q in g["outline_poly"]]
def zone(layer, name, prio=0, net=gnd, poly=None):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net); z.SetAssignedPriority(prio); z.SetZoneName(name)
    z.SetLocalClearance(MM(0.2)); z.SetMinThickness(MM(0.2)); z.SetThermalReliefGap(MM(0.25)); z.SetThermalReliefSpokeWidth(MM(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
    for q in (poly or outline): ps.Append(MM(q[0]), MM(q[1]))
    z.SetOutline(ps); b.Add(z); KEEP.extend([ps, z]); return z
Z = {L: zone(L, "GND_" + n) for L, n in ((pcbnew.F_Cu, "L1"), (pcbnew.In1_Cu, "L2"), (pcbnew.In2_Cu, "L3"), (pcbnew.B_Cu, "L4"))}
Z[pcbnew.In1_Cu].SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); Z[pcbnew.In2_Cu].SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
# thermal pads + die pad: solid connection
for z in [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() != "GND"]: z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
for f in b.GetFootprints():
    if f.GetReference() in ("J1", "J5", "J6", "MH1", "MH2", "H1", "H2", "H3", "H4", "J21", "J23"):
        for p in f.Pads():
            if p.GetNetname() == "GND": p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
for rp in [x for x in os.environ.get("STARVED", "").split(",") if x]:
    r_, n_ = rp.split("-"); f_ = b.FindFootprintByReference(r_)
    if f_ and f_.FindPadByNumber(n_): f_.FindPadByNumber(n_).SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
def fill(): pcbnew.ZONE_FILLER(b).Fill(b.Zones())
fill()
def filled(z, L):
    sp = z.GetFilledPolysList(L); gg = []
    for i in range(sp.OutlineCount()):
        o = sp.Outline(i); ext = [(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())]
        holes = [[(mm(sp.CHole(i, h).CPoint(k).x), mm(sp.CHole(i, h).CPoint(k).y)) for k in range(sp.CHole(i, h).PointCount())] for h in range(sp.HoleCount(i))]
        if len(ext) > 2: gg.append(Polygon(ext, holes).buffer(0))
    return unary_union(gg)
# 4. thermal via arrays + stitching: via where all four GND fills contain it (+margin), away from holes / other vias
def add_vias(region, step, margin=0.45, name="", skipL3=False):
    """skipL3: thermal arrays may pierce the L3 3V3 islands (the island refills around the via; no tracks on L3)"""
    F = {L: filled(Z[L], L) for L in Z}
    allg = F[pcbnew.F_Cu].intersection(F[pcbnew.In1_Cu]).intersection(F[pcbnew.B_Cu])
    if not skipL3: allg = allg.intersection(F[pcbnew.In2_Cu])
    allg = allg.intersection(region)
    ex = [(mm(t.GetPosition().x), mm(t.GetPosition().y)) for t in b.GetTracks() if isinstance(t, pcbnew.PCB_VIA)]
    hs = unary_union([Point(mm(p.GetPosition().x), mm(p.GetPosition().y)).buffer(mm(p.GetDrillSize().x) / 2)
                      for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSize().x > 0])
    x0, y0, x1, y1 = region.bounds; n = 0
    y = y0 + step / 2
    while y < y1:
        x = x0 + step / 2
        while x < x1:
            q = Point(x, y)
            if allg.contains(q.buffer(0.225 + margin)) and all(math.hypot(x - e[0], y - e[1]) > 0.9 for e in ex) and hs.distance(q) > 0.6:
                v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(pcbnew.F_Cu, MM(0.45)); v.SetDrill(MM(0.25))
                v.SetNet(gnd); b.Add(v); ex.append((x, y)); n += 1
            x += step
        y += step
    print("vias", name, n); return n
thermal = []
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetZoneName().startswith("THERMAL"):
        o = z.Outline(); thermal.append(Polygon([(mm(o.CVertex(i).x), mm(o.CVertex(i).y)) for i in range(o.TotalVertices())]).buffer(0))
nth = sum(add_vias(t, 1.5, 0.2, "thermal", skipL3=True) for t in thermal)
fill()
bbx = Polygon(outline).buffer(-1.0)
nst = add_vias(bbx, 3.0, 0.3, "stitch")
fill()
# 5. silk: footprint silk removed (B-side single-sided assembly, refs on B.Fab); board texts on silk kept only if clear of copper
nsilk = 0
for f in b.GetFootprints():
    for it in list(f.GraphicalItems()):
        if it.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS): f.Remove(it); nsilk += 1
    f.Value().SetLayer(pcbnew.F_Fab if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_Fab); f.Value().SetVisible(False)
    for fl in f.GetFields():
        if fl.GetName() not in ("Reference",): fl.SetLayer(pcbnew.F_Fab if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_Fab); fl.SetVisible(False)
for d in list(b.GetDrawings()):
    if d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and isinstance(d, pcbnew.PCB_TEXT) and d.GetText() in ("SSD A", "SSD B"):
        d.SetLayer(pcbnew.B_Fab)
# 6. footprint export + relink (board == library)
LIB = os.path.abspath(M.LIBN + ".pretty")
io = pcbnew.PCB_IO_KICAD_SEXPR(); seen = set()
for f in sorted(b.GetFootprints(), key=lambda f: (f.IsFlipped(), round(f.GetOrientation().AsDegrees()) % 360 != 0)):
    nm = str(f.GetFPID().GetLibItemName())
    if nm not in seen:
        seen.add(nm)
        gf = pcbnew.FOOTPRINT(f); gf.SetParent(b)   # Flip() needs the board (segfaults parentless in 9.0.2)
        if gf.IsFlipped(): gf.Flip(gf.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        gf.SetParent(None)
        gf.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T)); gf.SetPosition(pcbnew.VECTOR2I(0, 0))
        for p in gf.Pads(): p.SetNetCode(0)
        gf.SetReference("REF**"); gf.SetFPID(pcbnew.LIB_ID("", nm))
        io.FootprintSave(LIB, gf); KEEP.append(gf)
    f.SetFPID(pcbnew.LIB_ID(M.LIBN, nm))
fill()
pcbnew.SaveBoard(DST, b)
print("nc nets", nnc, "thermal vias", nth, "stitch", nst, "silk removed", nsilk, "fps exported", len(seen), "->", DST)
