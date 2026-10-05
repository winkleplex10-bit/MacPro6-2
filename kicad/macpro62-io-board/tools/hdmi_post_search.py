"""Search a new position for the HDMI clamp post H25 (M2 SMT nut + cradle post + M2 clamp screw) that clears the plate's power-button ear 1
(M1.4 head + Ø3.0 boss), the button carrier (ring + ear lug), the HDMI module (stiffener / receptacle collar / JM) and the main-board F-side courtyards.
Rev 2026-10-04 ~15:50 ET (Aidan: move H25 from (50.82, 111.0) toward (52.3, 111.6)). Plan coordinates = plate back view (xb, y), mm.
Writes hdmi_post_search.json; prints the best candidate."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__)); WS = "/workspace"
FJ = json.load(open(WS + "/mechanical/io_plate_v2/flex_821-2222_trace.json")); MJ = json.load(open(WS + "/kicad/macpro62-io-modules/modules.json"))
PLC = json.load(open(os.path.join(HERE, "placement.json"))); FR = json.load(open(WS + "/bracket/io_frame/io_frame.json"))["features"]; XM = FJ["mirror"]["x_m"]
TARGET, OLD = (52.3, 111.6), (50.82, 111.0)
BTN = FJ["button"]; BC = (BTN["cx"], BTN["cy"]); RING_R = BTN["ring_d"] / 2
EAR1 = [(h["cx"], h["cy"]) for h in FJ["holes"] if h["id"] == "BTN_EAR_1"][0]
BOSS_R, M14_HEAD_R, LUG_HW = 1.5, 1.3, 1.5          # plate ear boss Ø3.0; M1.4 pan head Ø2.6; carrier ear lug half-width (assumed = boss)
HEAD_R, POST_R, CRT_R = 1.9, 2.0, 2.645             # M2 head dk 3.8 (pan ISO 7045 / csk ISO 7046 both 3.8); SMT standoff OD 4.0 (H25 footprint) under the printed post; H25 courtyard (5.29 box)
PLATE_EDGE_R = HEAD_R + 0.4                         # clamp-plate edge around the screw (csk: 0.4 web outside the countersink)
CLR = 0.3                                           # Aidan: >= 0.3 in plan (or >= 0.5 vertical)
H = [m for m in MJ["modules"] if m["kind"] == "HDMI"][0]; T = MJ["types"]["HDMI"]; ST = MJ["stack"]
STIFF = (H["stiffener_plan_x"][0], H["stiffener_plan_x"][1], H["y"] - T["sy"], H["y"] + T["sy"])
COLLAR = (H["seat_plan_x"] - T["shell"][0] / 2 - ST["sleeve_t"] - ST["collar_w"], H["seat_plan_x"] + T["shell"][0] / 2 + ST["sleeve_t"] + ST["collar_w"],
          H["y"] - T["shell"][1] / 2 - ST["sleeve_t"] - ST["collar_w"], H["y"] + T["shell"][1] / 2 + ST["sleeve_t"] + ST["collar_w"])
JM = (H["jm_x_range"][0], H["jm_x_range"][1], H["y"] - ST["rec"][1] / 2, H["y"] + ST["rec"][1] / 2)
OTHER = [tuple(p) for p in MJ["posts"]["HDMI"] if tuple(p) != OLD][0]
leg, xm = FR["BIG_L"], XM
LEG = (2 * xm - leg["x_range_leg"][1], 2 * xm - leg["x_range_leg"][0], leg["y_range_leg"][0], leg["y_range_leg"][1])
TOP = (2 * xm - leg["x_range_top"][1], 2 * xm - leg["x_range_top"][0], leg["y_range_top"][0], leg["y_range_top"][1])
s1 = FR["SMALL_R1"]; SLOT = (2 * xm - s1["cx"] - s1["w"] / 2, 2 * xm - s1["cx"] + s1["w"] / 2, s1["cy"] - s1["h"] / 2, s1["cy"] + s1["h"] / 2)
def bb(x, y, r): return math.hypot(max(r[0] - x, 0, x - r[1]), max(r[2] - y, 0, y - r[3]))
def inside(x, y, r): return min(x - r[0], r[1] - x, y - r[2], r[3] - y)
def seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy))); return math.hypot(px - ax - t * dx, py - ay - t * dy)
_u = ((EAR1[0] - BC[0]) / math.hypot(EAR1[0] - BC[0], EAR1[1] - BC[1]), (EAR1[1] - BC[1]) / math.hypot(EAR1[0] - BC[0], EAR1[1] - BC[1]))
LUG_A = (BC[0] + (RING_R - 0.8) * _u[0], BC[1] + (RING_R - 0.8) * _u[1])
FPARTS = {k: v for k, v in PLC.items() if v["side"] == "F" and k != "H25"}
def margins(x, y):
    d1 = math.hypot(x - EAR1[0], y - EAR1[1])
    m = dict(ear1_m14_head=round(d1 - HEAD_R - M14_HEAD_R, 3), ear1_boss=round(d1 - HEAD_R - BOSS_R, 3),
             ear1_head_vs_clamp_plate_edge=round(d1 - PLATE_EDGE_R - M14_HEAD_R, 3),
             carrier_ring=round(math.hypot(x - BC[0], y - BC[1]) - HEAD_R - RING_R, 3), carrier_ear1_lug=round(seg(x, y, *LUG_A, *EAR1) - HEAD_R - LUG_HW, 3),
             hdmi_stiffener=round(bb(x, y, STIFF) - POST_R, 3), hdmi_collar=round(bb(x, y, COLLAR) - POST_R, 3), hdmi_jm=round(bb(x, y, JM) - POST_R, 3),
             other_post=round(math.hypot(x - OTHER[0], y - OTHER[1]) - 2 * CRT_R, 3))
    near = sorted((round(bb(x, y, (v["xb"][0], v["xb"][1], v["y"][0], v["y"][1])) - CRT_R if not (v["xb"][0] - CRT_R < x < v["xb"][1] + CRT_R and v["y"][0] - CRT_R < y < v["y"][1] + CRT_R) else
                   -min(x - (v["xb"][0] - CRT_R), (v["xb"][1] + CRT_R) - x, y - (v["y"][0] - CRT_R), (v["y"][1] + CRT_R) - y), 3), k) for k, v in FPARTS.items())[:3]
    # approximate courtyard-to-courtyard gap (box vs circle-ish box): use box-box distance for the 5.29 courtyard
    bx = (x - CRT_R, x + CRT_R, y - CRT_R, y + CRT_R)
    cy_gap = sorted((round(math.hypot(max(v["xb"][0] - bx[1], 0, bx[0] - v["xb"][1]), max(v["y"][0] - bx[3], 0, bx[2] - v["y"][1])) if not (bx[0] < v["xb"][1] and v["xb"][0] < bx[1] and bx[2] < v["y"][1] and v["y"][0] < bx[3]) else -1.0, 3), k) for k, v in FPARTS.items())[:3]
    m["board_courtyard_gap"] = cy_gap
    m["head_in_frame_opening"] = round(max(inside(x, y, LEG), inside(x, y, TOP), inside(x, y, SLOT)) - HEAD_R, 3)
    return m
REQ = ["ear1_m14_head", "ear1_boss", "ear1_head_vs_clamp_plate_edge", "carrier_ring", "carrier_ear1_lug", "hdmi_stiffener", "hdmi_collar", "hdmi_jm", "other_post"]
def ok(m): return all(m[k] >= (CLR if k.startswith(("ear1", "carrier", "hdmi_s", "hdmi_c", "hdmi_j")) else 0.0) - 1e-9 for k in REQ) and m["board_courtyard_gap"][0][0] >= 0
best = None
for i in range(-160, 161):
    for j in range(-160, 161):
        x, y = TARGET[0] + i * 0.05, TARGET[1] + j * 0.05
        m = margins(x, y)
        if ok(m):
            d = math.hypot(x - TARGET[0], y - TARGET[1])
            if best is None or d < best[0] - 1e-9: best = (d, round(x, 2), round(y, 2))
res = dict(target=TARGET, old=OLD, other_hdmi_post=OTHER, criteria="plan clearance >= %.1f to the ear-1 M1.4 head (r %.1f), ear-1 boss (r %.1f), carrier ring (r %.3f) and ear lug (half-width %.1f) from the M2 head (r %.1f); "
           "clamp-plate edge (r %.1f) >= %.1f from the ear-1 head; cradle post (r %.1f) >= %.1f from the HDMI stiffener / collar / JM; H25 courtyard clear of all F courtyards" % (CLR, M14_HEAD_R, BOSS_R, RING_R, LUG_HW, HEAD_R, PLATE_EDGE_R, CLR, POST_R, CLR),
           old_margins=margins(*OLD), target_margins=margins(*TARGET), best=None if best is None else dict(x=best[1], y=best[2], dist_from_target=round(best[0], 2), margins=margins(best[1], best[2])),
           frame=dict(leg=[round(v, 2) for v in LEG], top=[round(v, 2) for v in TOP], hdmi_slot=[round(v, 2) for v in SLOT]), stiffener=[round(v, 3) for v in STIFF], collar=[round(v, 3) for v in COLLAR])
if best:
    for cand in [(round(best[1] + dx, 2), round(best[2] + dy, 2)) for dx in (0, 0.05, 0.1) for dy in (0, 0.05)]:
        res.setdefault("rounded_candidates", {})["%.2f,%.2f" % cand] = dict(ok=ok(margins(*cand)), margins=margins(*cand))
json.dump(res, open(os.path.join(HERE, "hdmi_post_search.json"), "w"), indent=1)
print(json.dumps(dict(old=res["old_margins"], target=res["target_margins"], best=res["best"]), indent=1))
