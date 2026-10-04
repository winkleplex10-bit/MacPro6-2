#!/usr/bin/env python3
"""ICD O-10 (fp6) system fit check: BP J9/J10 <-> face J_PCIE MCIO 124 landing, ribbon corridors, cable path vs the face
cards and chassis, face-module connector band (template + SM-1). Run with the system python3 (KiCad 9 pcbnew + shapely).
Writes fitcheck_mcio_o10.txt next to backplane.kicad_pcb."""
import json, math, os
import pcbnew
from shapely.geometry import Polygon, Point
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.abspath(os.path.join(HERE, ".."))
KI = os.path.abspath(os.path.join(PRJ, ".."))
CX, CY = 150.0, 100.0
# --- sourced connector data (SFF-TA-1016 Rev 1.3 Tables 5-4, 6-2, 6-3) ---
PLUG_L = 13.2        # mating face -> plug body end (12.75 REF; Amphenol MCIO-124ST-01 L1 13.10) + tolerance
PADDLE_Z = 3.05      # RA receptacle: PCB -> card-slot centreline
LATCH_124, BODY_124, W_124N = 10.0, 7.86, 42.15 + 0.15   # latch top above plug bottom, body, narrow width max
LATCH_74, BODY_74, W_74N = 9.0, 6.86, 25.95 + 0.15
RIB_HALF_W, RIB_T = 19.3, 1.5   # ribbon half width (38.6 paddle), half stack thickness (2 layers of 0.6 + spacing)
R_BEND = 3.6                    # centreline bend radius (inner >= 3 mm)
BOARD_IN, BOARD_OUT = 55.0, 56.6
Y_MATE = 14.5
rep = []; ok_all = True
def chk(name, ok, detail):
    global ok_all
    ok_all &= bool(ok); rep.append("%-4s %-58s %s" % ("OK" if ok else "FAIL", name, detail))
def note(name, detail): rep.append("NOTE %-58s %s" % (name, detail))
def poly_of(f, layer=pcbnew.F_CrtYd, ox=CX, oy=CY):
    f.BuildCourtyardCaches(); p = f.GetCourtyard(layer); o = p.Outline(0)
    return Polygon([(pcbnew.ToMM(o.CPoint(i).x) - ox, oy - pcbnew.ToMM(o.CPoint(i).y)) for i in range(o.PointCount())]).convex_hull
# ---------------- BP ----------------
b = pcbnew.LoadBoard(os.path.join(PRJ, "backplane.kicad_pcb"))
FP = {f.GetReference(): f for f in b.GetFootprints()}
POLY = {r: poly_of(f) for r, f in FP.items() if not r.startswith("H")}
g = json.load(open(os.path.join(KI, "macpro62-face-template", "tools", "face_geom.json")))
XJ = g["J"]["J_PCIE"]["cx"]; XD = g["J"]["J_DISP"]["cx"]
faces = {"J9": ("Face P", 45.0), "J10": ("Face S", 135.0)}
cab = {}
for ref, (face, ang) in faces.items():
    f = FP[ref]; a = math.radians(ang); n = (math.cos(a), math.sin(a)); t = (-n[1], n[0])
    p = f.GetPosition(); x, y = pcbnew.ToMM(p.x) - CX, CY - pcbnew.ToMM(p.y)
    n_o, s_o = x * n[0] + y * n[1], x * t[0] + y * t[1]
    mate = n_o + 6.025; rear = mate + PLUG_L
    Xland = 52.0 - s_o
    chk("%s %s landing = module J_PCIE X %.1f (zero jog)" % (ref, face, XJ), abs(Xland - XJ) <= 0.5, "BP s %+.2f -> module X %.2f, jog %.2f mm (rot %.0f)" % (s_o, Xland, abs(Xland - XJ), f.GetOrientationDegrees()))
    # cable path, one 90 deg easy bend
    n_exit = BOARD_OUT + PADDLE_Z                     # module plug cable centre (n)
    for M1 in (15.0, 23.5):
        z_mod = M1 + Y_MATE - PLUG_L
        dn, dz = n_exit - rear, z_mod - PADDLE_Z
        free = dn + dz - (2 - math.pi / 2) * R_BEND
        chk("%s cable path at M1 %.1f (bend R_c %.1f fits)" % (ref, M1, R_BEND), dn > R_BEND + 1 and dz > R_BEND + 1,
            "plug rear n %.2f, dn %.2f, dz %.2f -> free %.1f mm, mating face <-> mating face %.1f mm" % (rear, dn, dz, free, free + 2 * PLUG_L))
        cab[(ref, M1)] = free + 2 * PLUG_L
    chk("%s BP plug inboard of the face board (no clash with the card)" % ref, rear < BOARD_IN - 5, "plug n %.2f-%.2f, latch z %.1f; board n %.1f-%.1f from z 15" % (mate, rear, LATCH_124, BOARD_IN, BOARD_OUT))
    chk("%s ribbon under the board bottom edge" % ref, PADDLE_Z + RIB_T < 15.0 - 5, "ribbon top z %.1f vs edge z 15 (23.5) -> %.1f mm (%.1f)" % (PADDLE_Z + RIB_T, 15 - PADDLE_Z - RIB_T, 23.5 - PADDLE_Z - RIB_T))
    corr = Polygon([(nn * n[0] + ss * t[0], nn * n[1] + ss * t[1]) for nn, ss in ((rear, s_o - RIB_HALF_W), (64, s_o - RIB_HALF_W), (64, s_o + RIB_HALF_W), (rear, s_o + RIB_HALF_W))])
    hits = sorted(((round(q.distance(corr), 2), r) for r, q in POLY.items() if r not in faces and q.distance(corr) < 0.3))
    near = min((round(q.distance(corr), 2), r) for r, q in POLY.items() if r not in faces)
    chk("%s ribbon corridor (n >= plug rear, s %+.1f +/- %.1f) free of parts" % (ref, s_o, RIB_HALF_W), not hits, "hits %s; nearest part %s %.2f mm" % (hits, near[1], near[0]))
    rmax = max(math.hypot(*c) for c in Polygon([(nn * n[0] + ss * t[0], nn * n[1] + ss * t[1]) for nn, ss in ((n_exit + RIB_T, s_o - RIB_HALF_W), (n_exit + RIB_T, s_o + RIB_HALF_W))]).exterior.coords) if False else max(math.hypot((n_exit + RIB_T) * n[0] + ss * t[0], (n_exit + RIB_T) * n[1] + ss * t[1]) for ss in (s_o - RIB_HALF_W, s_o + RIB_HALF_W))
    note("%s ribbon bend vs BP rim / base ring (M1b)" % ref, "bend outer face n %.1f, r <= %.1f at z %.1f-%.1f, beyond the BP rim (61.0): base ring / fillet clearance TO MEASURE (M1b)" % (n_exit + RIB_T, rmax, PADDLE_Z - RIB_T, PADDLE_Z + R_BEND + RIB_T))
    for nm, sx, sy in [("S1", -52.64, 13.81), ("S4", -18.12, 50.70), ("S5", 18.49, 50.72), ("S6", 52.80, 13.88)]:
        if corr.distance(Point(sx, sy)) < 3.0:
            note("%s ribbon over stock hole %s" % (ref, nm), "S-hole %s (%.1f, %.1f) %.1f mm from / under the ribbon (z >= %.1f): keep the BP surface flat there (no screw head) - CR-BP-1 purpose TO CHECK" % (nm, sx, sy, corr.distance(Point(sx, sy)), PADDLE_Z - RIB_T))
d9, d10 = POLY["J1"].distance(POLY["J9"]), POLY["J1"].distance(POLY["J10"])
chk("J1 (CPU-LINK) >= 1.0 mm from J9 / J10 courtyards", min(d9, d10) >= 1.0, "J9 %.2f mm, J10 %.2f mm" % (d9, d10))
chk("J9 <-> J10 courtyard gap (apex)", POLY["J9"].distance(POLY["J10"]) >= 0.5, "%.2f mm" % POLY["J9"].distance(POLY["J10"]))
fc = open(os.path.join(PRJ, "fitcheck_floorplan.txt")).read()
chk("BP floorplan fit check (rim 58 / gold hole 6 / S-hole 3, all parts)", "FAIL" not in fc, "%d parts in fitcheck_floorplan.txt" % len(fc.strip().splitlines()))
chk("Cable lengths equal-ish (one part number)", abs(cab[("J9", 15.0)] - cab[("J10", 15.0)]) < 5, "J9 %.1f / J10 %.1f mm mating face <-> mating face at M1 15 (%.1f / %.1f at 23.5): order %.0f mm nominal, +/-2" % (cab[("J9", 15.0)], cab[("J10", 15.0)], cab[("J9", 23.5)], cab[("J10", 23.5)], round((cab[("J9", 15.0)] + cab[("J10", 15.0)]) / 2)))
# ---------------- face template + SM-1 ----------------
def hout(x): return math.sqrt(g["R_I"] ** 2 - (x - g["X_AX"]) ** 2) - (g["D_FACE"] + g["T"]) - 1.0
for proj, pcbname, refs in (("macpro62-face-template", "macpro62-face-template.kicad_pcb", ("J1", "J2")), ("macpro62-storage-face", "macpro62-storage-face.kicad_pcb", ("J1",))):
    bb = pcbnew.LoadBoard(os.path.join(KI, proj, pcbname)); ax = bb.GetDesignSettings().GetAuxOrigin()
    ox, oy = pcbnew.ToMM(ax.x), pcbnew.ToMM(ax.y)
    F = {f.GetReference(): f for f in bb.GetFootprints()}
    PL = {}
    for r, f in F.items():
        f.BuildCourtyardCaches()
        for lay in (pcbnew.B_CrtYd, pcbnew.F_CrtYd):
            p = f.GetCourtyard(lay)
            if p.OutlineCount():
                PL[(r, lay)] = poly_of(f, lay, ox, oy)
    for r, want in zip(refs, (XJ, XD)):
        p = F[r].GetPosition(); X, Y = pcbnew.ToMM(p.x) - ox, oy - pcbnew.ToMM(p.y)
        chk("%s %s at X %.1f, mating face Y %.1f" % (proj.replace("macpro62-", ""), r, want, Y_MATE), abs(X - want) < 0.01 and abs(Y - 6.025 - Y_MATE) < 0.01, "X %.3f, peg line Y %.3f, side %s" % (X, Y, "B" if F[r].IsFlipped() else "F"))
        me = PL[(r, pcbnew.B_CrtYd)]
        others = [(round(me.distance(q), 2), k[0]) for k, q in PL.items() if k[0] != r and k[1] == pcbnew.B_CrtYd]
        nearest = min(others) if others else (99, "-")
        chk("%s %s courtyard clear on the outer side (B)" % (proj.replace("macpro62-", ""), r), nearest[0] > 0, "nearest %s %.2f mm" % (nearest[1], nearest[0]))
    if "J2" in refs:
        gap = (XD - W_74N / 2) - (XJ + W_124N / 2)
        chk("template J_PCIE <-> J_DISP narrow plug bodies", gap >= 0.5, "X %.2f / %.2f -> gap %.2f mm (flanged 124P would overlap by %.2f)" % (XJ + W_124N / 2, XD - W_74N / 2, gap, (XJ + 47.80 / 2) - (XD - W_74N / 2)))
for nm, cx, w, body, latch, lo in (("J_PCIE", XJ, W_124N, BODY_124, LATCH_124, 5.50), ("J_DISP", XD, W_74N, BODY_74, LATCH_74, 2.42)):
    e0, e1 = cx - w / 2, cx + w / 2
    hl = min(hout(cx - lo - 1), hout(cx + lo + 1))
    chk("%s outer envelope h(x) (plug body at the ends, latch at centre)" % nm, min(hout(e0), hout(e1)) >= body and hl >= latch,
        "h(%.1f) %.1f / h(%.1f) %.1f vs body %.2f; h at latch %.1f vs %.1f" % (e0, hout(e0), e1, hout(e1), body, hl, latch))
chk("Module plug inside the board outline (plug rear above the bottom edge)", Y_MATE - PLUG_L >= 0.5, "plug rear Y %.1f" % (Y_MATE - PLUG_L))
ka = g["AUX"]["ko"]; kj = g["J"]["J_PCIE"]["ko"]
chk("J_PCIE keep-out clear of J_AUX keep-out", kj[0] > ka[2], "J_AUX X %.1f-%.1f, J_PCIE X %.1f-%.1f" % (ka[0], ka[2], kj[0], kj[2]))
sm = pcbnew.LoadBoard(os.path.join(KI, "macpro62-storage-face", "macpro62-storage-face.kicad_pcb"))
chk("SM-1 M.2 cards clear of J1 (card bottom Y 28.5 vs body top Y %.2f)" % (Y_MATE + 10.07), 28.5 - (Y_MATE + 10.07) > 1.0, "%.2f mm" % (28.5 - (Y_MATE + 10.07)))
out = os.path.join(PRJ, "fitcheck_mcio_o10.txt")
open(out, "w").write("ICD O-10 / BP fp6 MCIO fit check (tools/fitcheck_o10.py)\n" + "\n".join(rep) + "\n" + ("ALL OK" if ok_all else "SOME FAIL") + "\n")
print("\n".join(rep)); print("ALL OK" if ok_all else "SOME FAIL")
