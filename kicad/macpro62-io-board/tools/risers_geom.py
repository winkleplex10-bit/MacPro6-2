"""Column riser geometry (D-IO14, rev 2026-10-02 ~10:50 ET). Reads the plate stack from build_plate.py's features JSON.
Each port column sits on one small riser PCB tilted about Y so every port axis is radial (normal to the plate at its opening).
PCB frame: x' across the riser (in the tilt plane, -x' = outboard edge), y' along board Y. One PCB design per port type; the O-column copy
is the same PCB rotated 180 deg about its normal. Main-board plan = projection on the board top (back-view frame)."""
import json, math
F = json.load(open("/workspace/mechanical/io_plate_v2/io_plate_v2_A0_features.json"))
ST = {s["port"]: s for s in F["stack"]}
RISER_T = 1.6
TYPES = {   # x' extents, y margin beyond the outer port centres, DF40 link (x', y', rot), riser->cradle screws, pogo targets (x', y', net)
 "C":    dict(conn="SHOU HAN TYPE-C 24PLT-H10.5 (C3151750)", x=(-8.4, 8.4), ym=7.2, btb="DF40C-80DS-0.4V(51)", btb_lcsc="C312960", pins=80, btb_at=(0.0, 0.0),
              screws=[(0.0, -15.6), (0.0, 15.6)], pogo=[(-6.6, -12.8, "VBUS_C3"), (6.6, -12.8, "VBUS_C3"), (-6.6, 1.5, "VBUS_C2"), (6.6, -1.5, "VBUS_C2"),
              (-6.6, 12.8, "VBUS_C1"), (6.6, 12.8, "VBUS_C1"), (-6.6, -2.9, "GND"), (6.6, 2.9, "GND")]),
 "A":    dict(conn="kinghelm KH-3.0AF180ZJ-11.5JB (C2979037)", x=(-13.1, 8.3), ym=5.8, btb="DF40C-50DS-0.4V(51)", btb_lcsc="TBC", pins=50, btb_at=(-10.1, 0.0),
              screws=[(-10.1, -9.4), (-10.1, 9.4)], pogo=[]),
 "HDMI": dict(conn="HOAUC HYC79-HDMIA19-105 (C711353)", x=(-12.4, 12.4), ym=7.2, btb="DF40C-40DS-0.4V(51)", btb_lcsc="TBC", pins=40, btb_at=(0.0, 0.0),
              screws=[(-11.0, -3.0), (11.0, 3.0)], pogo=[]),
}
COLS = [("RC_H", "C", ["C1", "C2", "C3"]), ("RC_O", "C", ["C4", "C5", "C6"]), ("RA_H", "A", ["A1", "A2"]), ("RA_O", "A", ["A3", "A4"]), ("RH", "HDMI", ["HDMI"])]
OUT = []
for rid, typ, ports in COLS:
    T = TYPES[typ]; ss = [ST[p] for p in ports]; rot = ss[0]["x"] > 53.19          # O column: PCB rotated 180 deg
    a = math.radians(ss[0]["tilt_deg"]); n = (math.sin(a), math.cos(a)); ex = (math.cos(a), -math.sin(a))
    Bx, Bz = ss[0]["riser_top_centre"]; zb = F["params"]["d0"]["board_top_z"]
    ys = [s["y"] for s in ss]; y0, y1 = min(ys) - T["ym"], max(ys) + T["ym"]; yc = (y0 + y1) / 2
    def col(xp, yp):   # PCB frame -> column frame (x' along ex, dy)
        return (-xp, -yp) if rot else (xp, yp)
    def bot(xc): return (Bx + ex[0] * xc - n[0] * RISER_T, Bz + ex[1] * xc - n[1] * RISER_T)
    def plan(xp, yp):
        xc, dy = col(xp, yp); x, z = bot(xc); return [round(x, 3), round(yc + dy, 3), round(z - zb, 3)]
    xs = sorted([col(T["x"][0], 0)[0], col(T["x"][1], 0)[0]])
    px = [bot(xs[0])[0], bot(xs[1])[0], Bx + ex[0] * xs[0], Bx + ex[0] * xs[1]]
    gap = sorted([bot(xs[0])[1] - zb, bot(xs[1])[1] - zb])
    btb = plan(*T["btb_at"])
    OUT.append(dict(id=rid, type=typ, ports=ports, rot180=rot, tilt_deg=ss[0]["tilt_deg"], pcb_x=list(T["x"]), riser_w=round(T["x"][1] - T["x"][0], 2), riser_l=round(y1 - y0, 2),
                    y_range=[round(y0, 2), round(y1, 2)], plan_x_range=[round(min(px), 2), round(max(px), 2)], underside_gap_range=[round(gap[0], 2), round(gap[1], 2)],
                    connector_centres_pcb=[[0.0, round((s["y"] - yc) * (-1 if rot else 1), 3)] for s in ss], connector_centres_plan=[[round(Bx, 3), s["y"]] for s in ss],
                    mouth_heights=[s["mouth_centre_height"] for s in ss], conn=T["conn"], btb=T["btb"], btb_lcsc=T["btb_lcsc"], btb_pins=T["pins"], btb_at_pcb=list(T["btb_at"]),
                    btb_riser_plan=btb, btb_main_plan=btb[:2], btb_gap=btb[2],
                    screws_pcb=T["screws"], screws_riser_to_cradle=[plan(*p) for p in T["screws"]],
                    screws_cradle_to_main=([[round(Bx + t * 7.5, 3), round(yc + 4.3, 3)] for t in (-1, 1)] if typ == "HDMI" else
                                           [[round(Bx + (col(T["btb_at"][0], 0)[0] * 0), 3), round(yc + t * ((y1 - y0) / 2 - (2.6 if typ == "A" else 2.0)), 3)] for t in (-1, 1)]),
                    pogo_pcb=T["pogo"], pogo=[plan(xp, yp) + [net] for xp, yp, net in T["pogo"]]))
json.dump(dict(rev="2026-10-02 ~10:50 ET", riser_t=RISER_T, case_r=F["params"]["case_r"], risers=OUT), open("/workspace/kicad/macpro62-io-risers/risers.json", "w"), indent=1)
for r in OUT: print(r["id"], r["tilt_deg"], r["plan_x_range"], r["y_range"], r["underside_gap_range"], "btb", r["btb_main_plan"], r["btb_gap"])
