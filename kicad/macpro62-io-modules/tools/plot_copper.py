#!/usr/bin/env python3
"""2D copper preview of a module board (D-IO16): filled zones, tracks, pads, vias, holes, outline; F.Cu red / B.Cu blue.
python3 tools/plot_copper.py mod_usbc   -> dumps geometry with pcbnew, then re-runs itself under /workspace/cadenv/bin/python --plot
writes <mod>/preview_<mod>_copper.png (whole flat module) and <mod>/preview_<mod>_fanout.png (port fan-out zoom, labelled)."""
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE)
def dump(nm):
    import pcbnew
    from pcbnew import ToMM
    b = pcbnew.LoadBoard(os.path.join(PRJ, nm, nm + ".kicad_pcb"))
    U = lambda p: (ToMM(p.x) - 100.0, 100.0 - ToMM(p.y))
    D = dict(tracks=[], vias=[], pads=[], zones=[], edge=[], holes=[], shapes=[])
    L = {pcbnew.F_Cu: "F", pcbnew.B_Cu: "B"}
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA": D["vias"].append((U(t.GetPosition()), ToMM(t.GetWidth(pcbnew.F_Cu)), ToMM(t.GetDrillValue()), t.GetNetname()))
        else: D["tracks"].append((U(t.GetStart()), U(t.GetEnd()), ToMM(t.GetWidth()), L.get(t.GetLayer(), "?"), t.GetNetname()))
    for z in b.Zones():
        if z.GetIsRuleArea(): continue
        for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
            if not z.IsOnLayer(lay): continue
            ps = z.GetFilledPolysList(lay)
            for i in range(ps.OutlineCount()):
                o = ps.Outline(i); pts = [U(o.CPoint(k)) for k in range(o.PointCount())]
                holes = []
                for h in range(ps.HoleCount(i)):
                    hh = ps.Hole(i, h); holes.append([U(hh.CPoint(k)) for k in range(hh.PointCount())])
                D["zones"].append((L[lay], z.GetNetname(), pts, holes))
    for d in b.GetDrawings():
        if d.GetClass() == "PCB_SHAPE" and d.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu) and d.GetShape() == pcbnew.SHAPE_T_POLY:
            ps = d.GetPolyShape(); o = ps.Outline(0); D["shapes"].append((L[d.GetLayer()], [U(o.CPoint(k)) for k in range(o.PointCount())]))
        if d.GetLayer() == pcbnew.Edge_Cuts:
            sh = d.GetShape()
            if sh == pcbnew.SHAPE_T_SEGMENT: D["edge"].append([U(d.GetStart()), U(d.GetEnd())])
            elif sh == pcbnew.SHAPE_T_ARC:
                import math
                c = U(d.GetCenter()); r = ToMM(d.GetRadius()); a0 = d.GetArcAngleStart().AsDegrees(); da = d.GetArcAngle().AsDegrees()
                pts = [(c[0] + r * math.cos(math.radians(-(a0 + da * k / 12))), c[1] + r * math.sin(math.radians(-(a0 + da * k / 12)))) for k in range(13)]
                D["edge"].append(pts)
    for f in b.GetFootprints():
        for p in f.Pads():
            sh = p.GetEffectivePolygon(pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu, pcbnew.ERROR_INSIDE)
            o = sh.Outline(0); pts = [U(o.CPoint(k)) for k in range(o.PointCount())]
            lays = "".join(L[l] for l in (pcbnew.F_Cu, pcbnew.B_Cu) if p.IsOnLayer(l))
            D["pads"].append((lays, p.GetNetname(), pts, f.GetReference() + ":" + p.GetNumber(), U(p.GetPosition())))
            if p.GetDrillSizeX() > 0: D["holes"].append((U(p.GetPosition()), ToMM(p.GetDrillSizeX()), ToMM(p.GetDrillSizeY()), p.GetOrientation().AsDegrees()))
    fn = "/tmp/plot_%s.json" % nm; json.dump(D, open(fn, "w")); return fn
def plot(nm, fn):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MP, Circle, FancyBboxPatch
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    D = json.load(open(fn))
    col = {"F": "#d03030", "B": "#2050d0"}
    def draw(ax, lw_scale, label):
        for lay, alpha in (("B", 0.45), ("F", 0.55)):
            for (zl, net, pts, holes) in D["zones"]:
                if zl != lay: continue
                verts = pts + [pts[0]]; codes = [Path.MOVETO] + [Path.LINETO] * (len(pts) - 1) + [Path.CLOSEPOLY]
                for h in holes: verts += h + [h[0]]; codes += [Path.MOVETO] + [Path.LINETO] * (len(h) - 1) + [Path.CLOSEPOLY]
                c = {"GND": col[lay], "VBUS": "#e0a000" if lay == "F" else "#00a0a0"}.get(net, col[lay])
                ax.add_patch(PathPatch(Path(verts, codes), facecolor=c, edgecolor="none", alpha=0.18 if net == "GND" else 0.35))
            for (sl, pts) in D["shapes"]:
                if sl == lay: ax.add_patch(MP(pts, closed=True, facecolor=col[lay], edgecolor="none", alpha=0.7))
            for (a, c, w, tl, net) in D["tracks"]:
                if tl != lay: continue
                ax.plot([a[0], c[0]], [a[1], c[1]], color=col[lay] if net not in ("VBUS",) else ("#c08000" if lay == "F" else "#008080"),
                        lw=w * lw_scale, solid_capstyle="round", alpha=0.95 if lay == "F" else 0.8, zorder=3 if lay == "F" else 2)
        for (lays, net, pts, ref, c) in D["pads"]:
            ax.add_patch(MP(pts, closed=True, facecolor="#b0b0b0" if "B" in lays else "#e8c050", edgecolor="k", lw=0.3, zorder=4))
        for (c, d, dr, net) in D["vias"]:
            ax.add_patch(Circle(c, d / 2, facecolor="#808080", edgecolor="k", lw=0.3, zorder=5)); ax.add_patch(Circle(c, dr / 2, facecolor="white", zorder=6))
        for (c, sx, sy, rot) in D["holes"]:
            if abs(sx - sy) < 1e-3: ax.add_patch(Circle(c, sx / 2, facecolor="white", edgecolor="k", lw=0.3, zorder=6))
            else:
                w_, h_ = (sx, sy) if abs(rot % 180) < 1 else (sy, sx)
                ax.add_patch(FancyBboxPatch((c[0] - w_ / 2 + h_ / 2, c[1] - h_ / 2), w_ - h_, h_, boxstyle="round,pad=0,rounding_size=%.3f" % (h_ / 2 - 1e-4), mutation_aspect=1,
                                            facecolor="white", edgecolor="k", lw=0.3, zorder=6))
        for e in D["edge"]: ax.plot([p[0] for p in e], [p[1] for p in e], color="k", lw=0.8)
        ax.set_aspect("equal"); ax.grid(True, lw=0.2, alpha=0.4)
    out = os.path.join(PRJ, nm)
    fig, ax = plt.subplots(figsize=(22, 5.5)); draw(ax, 9.0, False)
    xs = [p[0] for e in D["edge"] for p in e]; ys = [p[1] for e in D["edge"] for p in e]
    ax.set_xlim(min(xs) - 0.5, max(xs) + 0.5); ax.set_ylim(min(ys) - 0.5, max(ys) + 0.5)
    ax.set_title("%s - flat copper (F.Cu red, B.Cu blue; VBUS pours amber/teal; GND pours light) - module frame u, v [mm]" % nm, fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(out, "preview_%s_copper.png" % nm), dpi=160); plt.close(fig)
    if nm == "mod_usbc":
        fig, ax = plt.subplots(figsize=(16, 11)); draw(ax, 33.0, True)
        ax.set_xlim(-6.4, 7.4); ax.set_ylim(-4.7, 4.7)
        lab = {}
        for (a, c, w, tl, net) in D["tracks"]:
            if tl == "F" and abs(a[0] - 6.4) < 0.01 and abs(c[0] - 6.4) > 0.05 and net not in lab: lab[net] = a
        for net, p in lab.items(): ax.text(7.0, p[1], net, fontsize=7, va="center", ha="left", color="k", zorder=9)
        for (lays, net, pts, ref, c) in D["pads"]:
            if ref.startswith("J1:") and ref != "J1:S" and ref != "J1:": ax.text(c[0], c[1], ref[3:], fontsize=5.5, ha="center", va="center", rotation=90, zorder=9)
        ax.set_title("MOD-C port fan-out (hand-routed) - HOAUC HYCW417-USBC24-180B real land pattern; F.Cu red, B.Cu blue, vias grey; u, v [mm]", fontsize=10)
        fig.tight_layout(); fig.savefig(os.path.join(out, "preview_mod_usbc_fanout.png"), dpi=170); plt.close(fig)
        fig, ax = plt.subplots(figsize=(10, 9)); draw(ax, 60.0, True); ax.set_xlim(3.0, 7.6); ax.set_ylim(-3.6, 3.6)
        for net, p in lab.items(): ax.text(7.0, p[1] + 0.03, net, fontsize=7, va="bottom", ha="left", color="k", zorder=9)
        ax.set_title("MOD-C tail start: outboard shell slots, NPTH peg (5.5, -1.3), lane starts u = 6.4, VBUS feed vias", fontsize=10)
        fig.tight_layout(); fig.savefig(os.path.join(out, "preview_mod_usbc_tailstart.png"), dpi=150); plt.close(fig)
    print("plots written")
if __name__ == "__main__":
    if "--plot" in sys.argv: plot(sys.argv[1], sys.argv[3])
    else:
        nm = sys.argv[1]; fn = dump(nm)
        subprocess.run(["/workspace/cadenv/bin/python", os.path.abspath(__file__), nm, "--plot", fn], check=True)
