#!/usr/bin/env python3
"""TDR coupons for the D-IO16 port-module FPCs (JLC 2-layer FPC, 12 um Cu, ENIG, coverlay both sides, coverlay opened on the launch pads).
tdr_coupon_c50 = MOD-C / MOD-H stack (50 um PI core, 0.19 total): 90 ohm USB + 100 ohm TMDS over SOLID L2 and over the bend hatch (0.10 / 0.25),
                 plus a 50 ohm single-ended reference line (TDR calibration / er check).
tdr_coupon_a25 = MOD-A stack (25 um core, 0.11): 90 ohm USB over the 45 deg cross-hatched L2 (0.10 / 0.30), plus an SE line over the same hatch.
Every line is 50.0 mm between launches; GSSG / GSG launch, 1.00 mm pitch, GND pads tied to L2 with 0.55/0.3 vias; L2 solid under the launches.
Order the coupon on the SAME panel as the modules (JLC does not test FPC impedance) and measure with a 35 ps TDR (or a VNA + IFFT)."""
import os, sys, json, math
import pcbnew
from pcbnew import FromMM
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.dirname(HERE)
sys.argv = sys.argv[:1]; import build_modules as BM   # reuse helpers (net / trk / via / zone / shape / text, project writer conventions)
P = BM.P
L = 50.0; X0, X1 = 4.0, 4.0 + L; PITCH = 1.0
COUPONS = {
 "tdr_coupon_c50": dict(t=0.19, lines=[("USB90_SOLID", 0.09, 0.10, None, "90 ohm diff, solid L2 (tail)"),
                                        ("TMDS100_SOLID", 0.08, 0.15, None, "100 ohm diff, solid L2 (tail)"),
                                        ("USB90_HATCH", 0.12, 0.10, (0.10, 0.25), "90 ohm diff, L2 hatch 0.10/0.25 (bend)"),
                                        ("TMDS100_HATCH", 0.11, 0.15, (0.10, 0.25), "100 ohm diff, L2 hatch 0.10/0.25 (bend)"),
                                        ("SE50_SOLID", 0.09, None, None, "50 ohm SE reference, solid L2"),
                                        ("PADDLE_3MIL", 0.078, 0.078, None, "paddle lanes 0.078/0.078 (3-mil min, 2026-10-04), solid L2, est. 94 diff")]),
 "tdr_coupon_a25": dict(t=0.11, lines=[("USB90_XHATCH", 0.10, 0.10, (0.10, 0.30), "90 ohm diff, L2 cross-hatch 0.10/0.30 (MOD-A tail, est. 92)"),
                                        ("USB90_XHATCH_2", 0.10, 0.10, (0.10, 0.30), "repeat (panel spread)"),
                                        ("SE_XHATCH", 0.10, None, (0.10, 0.30), "SE 0.10 over the cross-hatch (er / hatch check)")]),
}
def pad_fp(b, ref, x, y, nets):
    f = pcbnew.FOOTPRINT(b); f.SetReference(ref); f.SetValue("TDR_LAUNCH"); f.SetPosition(P(x, y))
    for i, (dy, nm) in enumerate(nets):
        p = pcbnew.PAD(f); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD); p.SetShape(pcbnew.PAD_SHAPE_RECT); p.SetSize(pcbnew.VECTOR2I(FromMM(0.8), FromMM(0.5)))
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.F_Mask); p.SetLayerSet(ls)
        p.SetNumber(str(i + 1)); p.SetPosition(P(x, y + dy)); p.SetNet(BM.net(b, nm)); f.Add(p)
    f.Reference().SetVisible(False); f.Value().SetVisible(False); b.Add(f); return f
def build(name, cfg):
    BM.NETS.clear(); BM.KEEP.clear()
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    ds = b.GetDesignSettings(); ds.SetBoardThickness(FromMM(cfg["t"])); ds.m_TrackMinWidth = FromMM(BM.TMIN); ds.m_MinClearance = FromMM(BM.TMIN); ds.m_HoleClearance = FromMM(0.2); ds.m_CopperEdgeClearance = FromMM(0.3)
    n = len(cfg["lines"]); RP = 5.0; H = n * RP + 4.0; W = X1 + 4.0
    for a, c in (((0, -H), (W, -H)), ((W, -H), (W, 0)), ((W, 0), (0, 0)), ((0, 0), (0, -H))): BM.shape(b, "L", a, c, pcbnew.Edge_Cuts)
    BM.text(b, "%s  JLC FPC %.2f  L=%.1f mm  GSSG/GSG 1.00" % (name, cfg["t"], L), W / 2, -1.0, pcbnew.F_SilkS, 0.7)
    for i, (nm, w, s, hatch, label) in enumerate(cfg["lines"]):
        yc = -(3.0 + RP * i + RP / 2)
        band = [(0.3, yc - RP / 2), (W - 0.3, yc - RP / 2), (W - 0.3, yc + RP / 2), (0.3, yc + RP / 2)]
        BM.zone(b, "GND", band, pcbnew.B_Cu, prio=0, hatch=hatch, name="L2_%s" % nm, clr=0.1, therm=False)
        for xa, xb in ((0.3, X0 + 0.6), (X1 - 0.6, W - 0.3)):   # solid L2 under the launches (via landing)
            BM.zone(b, "GND", [(xa, yc - RP / 2), (xb, yc - RP / 2), (xb, yc + RP / 2), (xa, yc + RP / 2)], pcbnew.B_Cu, prio=1, name="L2_LAUNCH", clr=0.1, therm=False)
        BM.text(b, "%s: %s  w %.3f%s" % (nm, label, w, "" if s is None else " s %.3f" % s), W / 2, yc + RP / 2 - 0.9, pcbnew.F_SilkS, 0.6)
        if s is None:
            launch = [(-PITCH, "GND"), (0.0, nm), (PITCH, "GND")]
            for k, xl in enumerate((X0 - 1.6, X1 + 1.6)): pad_fp(b, "TP%d%s" % (i + 1, "AB"[k]), xl, yc, launch)
            BM.trk(b, nm, [(X0 - 1.2, yc), (X1 + 1.2, yc)], w, lock=False)
        else:
            sp = (w + s) / 2
            launch = [(-1.5 * PITCH, "GND"), (-0.5 * PITCH, nm + "_P"), (0.5 * PITCH, nm + "_N"), (1.5 * PITCH, "GND")]
            for k, xl in enumerate((X0 - 1.6, X1 + 1.6)): pad_fp(b, "TP%d%s" % (i + 1, "AB"[k]), xl, yc, launch)
            for sg, sfx in ((-1, "_P"), (1, "_N")):
                BM.trk(b, nm + sfx, [(X0 - 1.2, yc + sg * 0.5 * PITCH), (X0 - 0.2, yc + sg * 0.5 * PITCH), (X0 + 0.4, yc + sg * sp), (X1 - 0.4, yc + sg * sp), (X1 + 0.2, yc + sg * 0.5 * PITCH), (X1 + 1.2, yc + sg * 0.5 * PITCH)], w, lock=False)
        for xl in (X0 - 1.6, X1 + 1.6):
            for dy in ((-PITCH, PITCH) if s is None else (-1.5 * PITCH, 1.5 * PITCH)):
                xv = xl - 0.85 if xl < W / 2 else xl + 0.85
                BM.trk(b, "GND", [(xl, yc + dy), (xv, yc + dy)], 0.3, lock=False); BM.via(b, "GND", xv, yc + dy, lock=False)
    out = os.path.join(PRJ, "tdr", name); os.makedirs(out, exist_ok=True); fn = os.path.join(out, name + ".kicad_pcb"); b.Save(fn)
    b2 = pcbnew.LoadBoard(fn); pcbnew.ZONE_FILLER(b2).Fill(b2.Zones()); b2.Save(fn)   # fill on a reloaded board (in-memory fill segfaults)
    d = json.load(open(os.path.join(PRJ, "mod_usba", "mod_usba.kicad_pro"))); d["meta"]["filename"] = name + ".kicad_pro"
    d["net_settings"]["netclass_patterns"] = [dict(netclass="GNDC", pattern="GND")]
    json.dump(d, open(fn.replace(".kicad_pcb", ".kicad_pro"), "w"), indent=2)
    print("built", fn, "%.1f x %.1f" % (W, H)); return fn
if __name__ == "__main__":
    for nm, cfg in COUPONS.items(): build(nm, cfg)
