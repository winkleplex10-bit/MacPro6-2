#!/usr/bin/env python3
"""JLC FPC assembly panels for the port modules (2026-10-04, cost review). Usage: python3 tools/make_panel.py
JLC builds one stack-up per FPC order, so the modules split by core:
  panel_c50 (50 um PI core, 0.19 total): 6 x MOD-C + 1 x MOD-H + tdr_coupon_c50  = one complete Mac Pro set of C/H modules
  panel_a25 (25 um PI core, 0.11 total): 4 x MOD-A + tdr_coupon_a25
JLC flex-panel rules (jlcpcb.com/blog/Design-Guidelines-for-Flex-PCB-Panels-on-JLCPCB, read 2026-10-04): 5 mm process edges, copper-poured
(1 mm clear round fiducials, 0.5 mm round tooling holes); 1 mm fiducials centred 3.85 mm from the edge, one per corner with one corner offset by 5 mm;
2 mm tooling holes per corner; 2 mm unit spacing (3 mm used: FR4 stiffeners); laser-cut bridge tabs 0.7-1.0 mm (1.0 used, all on stiffened areas);
one local fiducial per assembled unit. 'Different designs in one outline frame': <= 10 pieces, > 3 designs gets an audit
(jlcpcb.com/help/article/fpc-extra-charges s.8) -> 8 pieces / 3 designs and 5 pieces / 2 designs.
Every unit keeps its own nets (prefixed '<unit>/'), references get a '_<unit>' suffix (unique designators for the CPL)."""
import os, sys, json, math, shutil, re, subprocess
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE)
sys.argv = sys.argv[:1]; sys.path.insert(0, HERE); import build_modules as BM
EDGE, GAP, CH, TAB = 5.0, 3.0, 1.5, 1.0        # process edge, unit spacing, cut channel half (= GAP/2), tab width
KIND = {"mod_usbc": "USBC", "mod_usba": "USBA", "mod_hdmi": "HDMI"}
PANELS = {
 "panel_c50": dict(base="mod_usbc", rows=[[("mod_usbc", "C1"), ("mod_usbc", "C2")], [("mod_usbc", "C3"), ("mod_usbc", "C4")], [("mod_usbc", "C5"), ("mod_usbc", "C6")],
                                          [("mod_hdmi", "H"), None], [("tdr_coupon_c50", "T")]]),
 "panel_a25": dict(base="mod_usba", rows=[[("mod_usba", "A1")], [("mod_usba", "A2")], [("mod_usba", "A3")], [("mod_usba", "A4")], [("tdr_coupon_a25", "T")]]),   # 1 column: stays <= 100 x 100
}
def LOAD(f): return pcbnew.PCB_IO_MGR.Load(pcbnew.PCB_IO_MGR.KICAD_SEXP, f)
def src_path(n): return os.path.join(PRJ, "tdr", n, n + ".kicad_pcb") if n.startswith("tdr_") else os.path.join(PRJ, n, n + ".kicad_pcb")
def outline(b):
    ps = pcbnew.SHAPE_POLY_SET(); ok_ = b.GetBoardPolygonOutlines(ps); o = ps.COutline(0)
    return Polygon([(ToMM(o.CPoint(i).x), ToMM(o.CPoint(i).y)) for i in range(o.PointCount())])
def tabs_for(name, b, poly):
    """(x, y, dx, dy) tab roots on the source board (KiCad mm), on stiffened edges only."""
    x0, y0, x1, y1 = poly.bounds; cy = (y0 + y1) / 2
    if name.startswith("tdr_"):
        return [(x0, cy, -1, 0), (x1, cy, 1, 0)] + [(x0 + (x1 - x0) * f, y, 0, d) for f in (0.2, 0.8) for (y, d) in ((y0, -1), (y1, 1))]
    g = BM.geo(KIND[name]); hw = g["tw"] / 2; X = lambda u: BM.OX + u
    xs = X((g["sxo"] - g["sxi"]) / 2 - 0.0)          # middle of the port stiffener
    xp = X(g["uh"])                                  # DF40 header (paddle stiffener)
    return [(x0, cy, -1, 0), (x1, cy, 1, 0), (xs, cy - g["sy"], 0, -1), (xs, cy + g["sy"], 0, 1), (xp, cy - hw, 0, -1), (xp, cy + hw, 0, 1)]
def copy_board(dst, src, dx, dy, unit, keep):
    nets = {}
    def N(n):
        if n is None or n.GetNetCode() == 0: return None
        nm = unit + "/" + n.GetNetname()
        if nm not in nets:
            ni = pcbnew.NETINFO_ITEM(dst, nm); dst.Add(ni); nets[nm] = ni; keep.append(ni)
        return nets[nm]
    mv = VECTOR2I(FromMM(dx), FromMM(dy))
    for f in src.GetFootprints():
        c = f.Duplicate().Cast(); c.Move(mv); c.SetReference(f.GetReference() + "_" + unit); dst.Add(c); keep.append(c)
        if f.GetValue() == "TDR_LAUNCH": c.SetAttributes(c.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)   # bare coupon pads
        for p, q in zip(f.Pads(), c.Pads()):
            n = N(p.GetNet()); q.SetNet(n) if n else q.SetNetCode(0)
    for t in src.GetTracks():
        c = t.Duplicate().Cast(); c.Move(mv); n = N(t.GetNet()); dst.Add(c); keep.append(c)
        c.SetNet(n) if n else c.SetNetCode(0)
    for z in src.Zones():
        c = z.Duplicate().Cast(); c.Move(mv); dst.Add(c); keep.append(c)
        n = N(z.GetNet()); c.SetNet(n) if n else c.SetNetCode(0)
        if c.GetZoneName(): c.SetZoneName(unit + "/" + c.GetZoneName())
    for d in src.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts: continue
        if d.GetLayer() in (pcbnew.Cmts_User, pcbnew.Dwgs_User) and d.GetClass() in ("PCB_TEXT", "PCB_TEXTBOX"): continue   # build notes: once per panel is enough
        c = d.Duplicate().Cast(); c.Move(mv); dst.Add(c); keep.append(c)
def fp_from_lib(lib, name):
    return pcbnew.FootprintLoad(os.path.join("/usr/share/kicad/footprints", lib + ".pretty"), name)
def build(pname, cfg):
    keep = []
    base = src_path(cfg["base"]); out_dir = os.path.join(PRJ, "panel", pname); os.makedirs(out_dir, exist_ok=True)
    fn = os.path.join(out_dir, pname + ".kicad_pcb")
    srcs = {}
    for row in cfg["rows"]:
        for cell in row:
            if cell and cell[0] not in srcs: srcs[cell[0]] = LOAD(src_path(cell[0])); keep.append(srcs[cell[0]])
    bb = srcs[cfg["base"]]; dst = pcbnew.BOARD()     # inherit stack-up, layer names, design rules from the base module
    dst.SetCopperLayerCount(2); dst.SetEnabledLayers(bb.GetEnabledLayers())
    sd, dd = bb.GetDesignSettings(), dst.GetDesignSettings()
    dd.SetBoardThickness(sd.GetBoardThickness()); dd.m_TrackMinWidth = sd.m_TrackMinWidth; dd.m_MinClearance = sd.m_MinClearance
    dd.m_HoleClearance = sd.m_HoleClearance; dd.m_CopperEdgeClearance = sd.m_CopperEdgeClearance; dd.m_ViasMinSize = sd.m_ViasMinSize; dd.m_MinThroughDrill = sd.m_MinThroughDrill
    for L_ in (pcbnew.User_1, pcbnew.User_2, pcbnew.User_3, pcbnew.User_4): dst.SetLayerName(L_, bb.GetLayerName(L_))
    # ---- place units (row-major, left-aligned, GAP spacing) ----
    placed = []; y = EDGE + GAP
    widths = []
    for row in cfg["rows"]:
        x = EDGE + GAP; hmax = 0.0
        for cell in row:
            if cell is None: continue
            nm, unit = cell
            b = srcs[nm]; poly = outline(b); bx0, by0, bx1, by1 = poly.bounds
            dx, dy = x - bx0, y - by0
            placed.append(dict(name=nm, unit=unit, dx=dx, dy=dy, poly=Polygon([(px + dx, py + dy) for px, py in poly.exterior.coords]),
                               tabs=[(tx + dx, ty + dy, ux, uy) for tx, ty, ux, uy in tabs_for(nm, b, poly)]))
            x += (bx1 - bx0) + GAP; hmax = max(hmax, by1 - by0)
        widths.append(x); y += hmax + GAP
    W = max(max(widths) - GAP + GAP + EDGE, 70.0); H = max(y + EDGE, 70.0)
    for p in placed: copy_board(dst, srcs[p["name"]], p["dx"], p["dy"], p["unit"], keep)
    # ---- outline: frame minus cut channels, bridged by tabs ----
    units = unary_union([p["poly"] for p in placed])
    chan = unary_union([p["poly"].buffer(CH, join_style=2) for p in placed]).difference(units)
    tabs = []
    for p in placed:
        for (tx, ty, ux, uy) in p["tabs"]:
            L = CH * 2 + 0.6
            if ux: tabs.append(box(min(tx, tx + ux * L), ty - TAB / 2, max(tx, tx + ux * L), ty + TAB / 2))
            else: tabs.append(box(tx - TAB / 2, min(ty, ty + uy * L), tx + TAB / 2, max(ty, ty + uy * L)))
    cut = chan.difference(unary_union(tabs))
    mat = box(0, 0, W, H).difference(cut).simplify(0.0005)
    assert mat.geom_type == "Polygon", ("panel material not one piece", mat.geom_type)
    def ring(coords):
        pts = list(coords)
        for a, c in zip(pts[:-1], pts[1:]):
            if math.hypot(c[0] - a[0], c[1] - a[1]) < 0.002: continue
            s = pcbnew.PCB_SHAPE(dst); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(VECTOR2I(FromMM(a[0]), FromMM(a[1]))); s.SetEnd(VECTOR2I(FromMM(c[0]), FromMM(c[1])))
            s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.05)); dst.Add(s); keep.append(s)
    ring(mat.exterior.coords)
    for hole in mat.interiors: ring(hole.coords)
    # ---- fiducials / tooling holes / rail copper ----
    fids = [(10.0, 3.85), (W - 10.0, 3.85), (10.0, H - 3.85), (W - 15.0, H - 3.85)]     # top-right corner offset by 5 mm (orientation)
    tools_ = [(2.5, 2.5), (W - 2.5, 2.5), (2.5, H - 2.5), (W - 7.5, H - 2.5)]
    locs = []
    for p in placed:
        if p["name"].startswith("tdr_"): continue
        x0, y0, x1, y1 = p["poly"].bounds
        locs.append(((x0 + x1) / 2, y0 - 0.0) if False else None)
    # local fiducial per assembled unit: on the side rail level with the unit (left column -> left rail, right column -> right rail)
    locs = []
    for p in placed:
        if p["name"].startswith("tdr_"): continue
        x0, y0, x1, y1 = p["poly"].bounds; cy = (y0 + y1) / 2
        locs.append((2.5, cy) if x0 < W / 2 - 10 else (W - 2.5, cy))
    n_f = 0
    for i, (fx, fy) in enumerate(fids + locs):
        f = fp_from_lib("Fiducial", "Fiducial_1mm_Mask2mm"); f.SetPosition(VECTOR2I(FromMM(fx), FromMM(fy))); f.SetReference("FID%d" % (i + 1))
        f.SetAttributes(f.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES); f.Reference().SetVisible(False); dst.Add(f); keep.append(f); n_f += 1
    for i, (hx, hy) in enumerate(tools_):
        f = pcbnew.FOOTPRINT(dst); f.SetReference("TH%d" % (i + 1)); f.SetValue("TOOLING_2.0"); f.SetPosition(VECTOR2I(FromMM(hx), FromMM(hy)))
        pd = pcbnew.PAD(f); pd.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); pd.SetShape(pcbnew.PAD_SHAPE_CIRCLE); pd.SetSize(VECTOR2I(FromMM(2.0), FromMM(2.0)))
        pd.SetDrillSize(VECTOR2I(FromMM(2.0), FromMM(2.0))); ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Mask); ls.AddLayer(pcbnew.B_Mask); pd.SetLayerSet(ls); pd.SetPosition(f.GetPosition()); f.Add(pd)
        f.SetAttributes(pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES); f.Reference().SetVisible(False); f.Value().SetVisible(False); dst.Add(f); keep.append(f)
    # rail copper: 4 simple strips per layer (KiCad zone outlines cannot carry holes) + no-copper rule areas round fiducials (1.0) / tooling (0.5)
    strips = [box(0, 0, W, EDGE), box(0, H - EDGE, W, H), box(0, EDGE, EDGE, H - EDGE), box(W - EDGE, EDGE, W, H - EDGE)]
    def poly_zone(gpoly, layer, rule=False):
        z = pcbnew.ZONE(dst); z.SetLayer(layer)
        if rule:
            z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        else:
            z.SetNetCode(0); z.SetZoneName("RAIL_CU"); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER); z.SetMinThickness(FromMM(BM.TMIN)); z.SetLocalClearance(FromMM(0.3))
        ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
        for (px, py) in list(gpoly.exterior.coords)[:-1]: ps.Append(FromMM(px), FromMM(py))
        z.SetOutline(ps); dst.Add(z); keep.extend([z, ps])
    for L_ in (pcbnew.F_Cu, pcbnew.B_Cu):
        for st in strips: poly_zone(st, L_)
        for q in fids + locs: poly_zone(Point(*q).buffer(0.5 + 1.0, 16), L_, rule=True)
        for q in tools_: poly_zone(Point(*q).buffer(1.0 + 0.5, 16), L_, rule=True)
    # notes
    t = pcbnew.PCB_TEXT(dst); t.SetText("%s  %s  %.1f x %.1f mm  (%s)" % (pname, " ".join(p["unit"] for p in placed), W, H, "JLC FPC 2L 12 um Cu ENIG, coverlay both sides, FR4 stiffeners per User.1"))
    t.SetPosition(VECTOR2I(FromMM(W / 2), FromMM(H + 2.0))); t.SetLayer(pcbnew.Cmts_User); t.SetTextSize(VECTOR2I(FromMM(1.0), FromMM(1.0))); dst.Add(t); keep.append(t)
    pcbnew.PCB_IO_MGR.Save(pcbnew.PCB_IO_MGR.KICAD_SEXP, fn, dst)
    # project: the base module's rules; net-class patterns widened for the '<unit>/' prefix
    pj = json.load(open(base.replace(".kicad_pcb", ".kicad_pro"))); pj["meta"]["filename"] = pname + ".kicad_pro"
    for pat in pj.get("net_settings", {}).get("netclass_patterns", []) or []: pat["pattern"] = "*/" + pat["pattern"]
    json.dump(pj, open(fn.replace(".kicad_pcb", ".kicad_pro"), "w"), indent=2)
    dru = base.replace(".kicad_pcb", ".kicad_dru")
    if os.path.exists(dru): shutil.copy(dru, fn.replace(".kicad_pcb", ".kicad_dru"))
    fl = os.path.join(os.path.dirname(base), "fp-lib-table")
    if os.path.exists(fl): open(os.path.join(out_dir, "fp-lib-table"), "w").write(open(fl).read().replace("${KIPRJMOD}/..", "${KIPRJMOD}/../.."))
    stiff = sum(1 for d in dst.GetDrawings() if d.GetLayer() == pcbnew.User_1)
    fill_q.append(fn)
    # unit areas (for the cost comparison)
    rep = dict(panel=pname, size_mm=[round(W, 2), round(H, 2)], units=[p["unit"] for p in placed], designs=sorted({p["name"] for p in placed}),
               pieces=len(placed), unit_area_mm2={p["unit"]: round(p["poly"].area, 1) for p in placed}, panel_area_mm2=round(W * H, 1),
               utilisation=round(units.area / (W * H), 3), fiducials=n_f, tooling_holes=len(tools_), tabs=len(tabs), user1_stiffener_shapes=stiff)
    json.dump(rep, open(os.path.join(out_dir, pname + "_report.json"), "w"), indent=1)
    print(json.dumps(rep)); return fn
fill_q = []
if __name__ == "__main__":
    if len(sys.argv) > 1 and False: pass
    for k, v in PANELS.items(): build(k, v)
    # zone fill in a fresh process per panel (project-managed load; filling the hand-assembled BOARD() segfaults)
    for f_ in fill_q:
        subprocess.run([sys.executable, "-c", "import pcbnew; b = pcbnew.LoadBoard(%r); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(%r, b); print('filled', %r)" % (f_, f_, f_)], check=True)
