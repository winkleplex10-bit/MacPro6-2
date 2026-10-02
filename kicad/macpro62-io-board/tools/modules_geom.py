"""Port-module geometry (D-IO16, rev 2026-10-02 ~12:35 ET). Replaces risers_geom.py (column risers, D-IO14).
Each USB-C / USB-A / HDMI port is its own swappable FLEX module: the receptacle is soldered straight onto a 2-layer FPC over a local FR4
stiffener (no rigid PCB), the FPC tail leaves the stiffener's OUTBOARD edge, C-folds 180 deg down and runs back under the module to a
Hirose DF40C-50DP header (on the same FPC face as the port, stiffened) that presses into a DF40C-50DS receptacle JMn on the main board F side.
Mechanics: the stiffener sits on the ledges of a printed cradle (insertion force -> stiffener -> ledges -> main board); a bonded sheet-metal
shield sleeve round the receptacle shell carries a collar that a screwed clamp plate holds down (withdrawal + side loads -> sleeve -> clamp
-> screws -> SMT nuts in the main board). Solder joints and flex carry no plug load.
Frames: plate/back-view (X, z) from io_plate_v2_A0_features.json (port axis normal to the plate by default). Module frame x' along ex
(same as the old risers), y' = board Y. Flat module PCB frame: u = x' toward the module's OUTBOARD edge, v = y' (one design per type; the
O-column copy is the same module rotated 180 deg about its axis -> its JM receptacle is rotated 180 deg too)."""
import json, math, sys
FEAT = "/workspace/mechanical/io_plate_v2/io_plate_v2_A0_features.json"
F = json.load(open(FEAT)); ST = {s["port"]: s for s in F["stack"]}
ZB = F["params"]["d0"]["board_top_z"]; PC = F["params"]["outline"]["centre"][0]; R0 = F["params"]["case_r"]
FP = F["params"]["flex"]
R_FRB = R0 - 1.2 + FP["pocket"] - FP["psa_t"] - FP["flex_t"] - FP["foam_t"] - FP["frame_t"]   # metal I/O frame back face radius
FPC_T, PSA_T, STIF_T = 0.11, 0.05, 1.0         # JLC 2-layer FPC 0.11 (PI 25 um + 2 x 12 um Cu + coverlay), stiffener PSA, FR4 stiffener
STACK_T = FPC_T + PSA_T + STIF_T                # = RISER_T in build_plate.py (1.16)
MATED = 1.5                                     # DF40C-50DS + DF40C-50DP mated height
HDR_L, HDR_W = 12.6, 4.2                        # DF40C-50DP envelope incl. fittings (0.4 x 24 + 2.6 + pads) [PLACEHOLDER, Hirose drawing]
REC_L, REC_W = 12.9, 4.4                        # DF40C-50DS courtyard on the main board
PADDLE_W = 8.4                                  # header paddle (stiffened) width: DF40C-50DP + WLCSP-4 ID EEPROM + 0201 cap; fits the cradle pocket between walls
STIF_M = 1.0                                    # JLC: stiffener >= 1.0 beyond pads
FOLD_RMIN = 1.0                                 # 2-layer 0.11 FPC, static C-fold (installed once per swap): R >= ~9 x t
LEDGE_CLR, WALL = 0.3, 0.8                      # tail clearance to the cradle ledges, MJF PA12 min wall
PLATE_T, PLATE_CLR = 1.6, 0.3                   # clamp plate (MJF PA12, ribbed) thickness, gap below the metal frame back
SLEEVE_T, COLLAR_W = 0.2, 1.0                   # SUS304 sleeve wall, collar flange width
TYPES = {   # port footprint courtyard half-extents (x', y'), stiffener half extents, tail width, flap before the fold
 "USBC": dict(mod="MOD-C", conn="HOAUC HYCW417-USBC24-180B (C5342202) all-SMD", fp="MP62_MOD_USB_C_24P_Vertical_SMD_PLACEHOLDER", crt=(5.0, 3.4), sx=6.0, sy=4.4, tw=6.5,
              shell=(8.94, 3.26), slots=["C1", "C2", "C3", "C4", "C5", "C6"]),
 "USBA": dict(mod="MOD-A", conn="kinghelm KH-3.0AF180ZJ-11.5JB (C2979037) THT", fp="MP62_USB_A3_9P_Vertical_PLACEHOLDER", crt=(7.6, 3.4), sx=8.4, sy=4.4, tw=6.5,
              shell=(13.2, 5.7), slots=["A1", "A2", "A3", "A4"]),
 "HDMI": dict(mod="MOD-H", conn="HOAUC HYC79-HDMIA19-105 (C711353) SMD + THT shell", fp="MP62_HDMI_A_Vertical_PLACEHOLDER", crt=(8.6, 3.7), sx=9.6, sy=4.7, tw=6.5,
              shell=(15.2, 5.5), slots=["HDMI"]),
}
H13 = (53.38, 58.38, 2.65)                      # I/O-frame centre standoff (courtyard r)
SPK = dict(x=(8.3, 31.5), y=(36.5, 97.0))       # stock speaker (F side), stadium
POSTS = {"C": [(53.19, 70.8), (53.19, 49.3)], "A": [(53.19, 49.3), (53.19, 25.5)], "HDMI": [(43.8, 114.6), (56.0, 111.0)]}   # clamp-screw posts (M2 SMT nut in the main board)
POST_R = 2.2
def spk_halfw(y):   # stadium half-width at Y
    r = (SPK["x"][1] - SPK["x"][0]) / 2; c = (SPK["x"][0] + SPK["x"][1]) / 2
    if y < SPK["y"][0] or y > SPK["y"][1]: return None
    yc = min(max(y, SPK["y"][0] + r), SPK["y"][1] - r); d = abs(y - yc)
    return c, math.sqrt(max(r * r - d * d, 0.0))
def frame_back_h(x): u = x - PC; return -R0 + math.sqrt(R_FRB ** 2 - u * u) - ZB
LF_FIX = {}
def run():
  global OUT, CHK
  OUT = []; CHK = []
  for kind, T in TYPES.items():
      for p in T["slots"]:
          s = ST[p]; a = math.radians(s["tilt_deg"]); n = (math.sin(a), math.cos(a)); ex = (math.cos(a), -math.sin(a))
          so = -1 if s["x"] < PC else 1                                  # outboard plan direction
          xo = so * (1 if ex[0] > 0 else -1)                             # sign of x' that points outboard
          Bx, Bz = s["riser_top_centre"]                                  # FPC top at the connector centre (seat)
          def P(xp, dn=0.0): return (Bx + ex[0] * xp - n[0] * dn, Bz + ex[1] * xp - n[1] * dn - ZB)   # plan X, height above board
          E = P(xo * T["sx"], FPC_T / 2)                                  # FPC mid-plane at the outboard stiffener edge
          stiff_bot = [P(xo * T["sx"], STACK_T), P(-xo * T["sx"], STACK_T)]
          ht = MATED + FPC_T / 2                                          # tail FPC mid-plane over the mated header
          # flap Lf (along the module plane) before the fold: smallest value keeping the header/receptacle clear of H13 and clamp posts
          best = None
          for k in range(0, 61):
              Lf = 0.5 + 0.1 * k
              if LF_FIX.get(kind) is not None: Lf = LF_FIX[kind]
              Fp = (E[0] + so * Lf * abs(ex[0]), E[1] - so * Lf * 0.0)
              R = (Fp[1] - ht) / 2.0
              x_s0 = Fp[0] - so * 0.5                                     # header stiffener starts 0.5 inboard of the fold end
              x_hc = x_s0 - so * (STIF_M + HDR_L / 2)
              x_in = x_hc - so * (REC_L / 2)                              # receptacle inboard courtyard end
              x_fold = Fp[0] + so * (R + FPC_T / 2)                        # outermost fold point
              y = s["y"]; ok = True; why = []
              if abs(y - H13[1]) < REC_W / 2 + H13[2] and (x_in - (H13[0] - H13[2])) * (-so) > -0.0 and abs(x_in - H13[0]) < H13[2] + 0.1 + (0 if so > 0 else 0):
                  pass
              # receptacle x-range vs H13 / posts
              xr = sorted([x_hc - REC_L / 2, x_hc + REC_L / 2])
              def hits(cx, cy, r): return (xr[0] - r < cx < xr[1] + r) and abs(y - cy) < REC_W / 2 + r
              if hits(H13[0], H13[1], H13[2]): ok = False; why.append("H13")
              for g, pl in POSTS.items():
                  for (px, py) in pl:
                      if hits(px, py, POST_R): ok = False; why.append("post")
              best = dict(Lf=round(Lf, 2), R=round(R, 3), x_fold=round(x_fold, 3), x_hc=round(x_hc, 3), rec_x=[round(v, 3) for v in xr], ok=ok, why=why)
              if ok or LF_FIX.get(kind) is not None: break
          Lf, R = best["Lf"], best["R"]
          # speaker clearance of the fold (F side stadium)
          sp = spk_halfw(s["y"]) if so < 0 else None; spk_clr = None   # speaker = H side only
          if sp: spk_clr = round((best["x_fold"] - (sp[0] + sp[1])) if so < 0 else ((sp[0] - sp[1]) - best["x_fold"]), 2)
          # flex electrical length (port pads -> header pins): half stiffener + flap + fold + header run
          L_flex = T["sx"] + Lf + math.pi * R + 0.5 + STIF_M + HDR_L / 2 + 2.0
          # sleeve / collar / clamp plate heights (along the axis from the seat)
          sw, sh = T["shell"]; xs_out = s["x"] + so * (sw / 2 + SLEEVE_T + COLLAR_W)
          fb = frame_back_h(s["x"])                                         # at the axis: the collar plane is ~parallel to the frame back (axis normal to the plate)
          collar_top = fb - PLATE_CLR - PLATE_T                            # collar top = clamp plate underside
          seat_h = s["riser_top_height"]
          sleeve_len = round((collar_top - seat_h) / math.cos(a), 2)
          unfolded = dict(stiff_u=[-T["sx"], T["sx"]], stiff_v=[-T["sy"], T["sy"]], tail_w=T["tw"], fold_u=[round(T["sx"] + Lf, 3), round(T["sx"] + Lf + math.pi * R, 3)],
                          hdr_stiff_u=[round(T["sx"] + Lf + math.pi * R + 0.5, 3), round(T["sx"] + Lf + math.pi * R + 0.5 + 2 * STIF_M + HDR_L, 3)],
                          paddle_w=PADDLE_W, hdr_centre_u=round(T["sx"] + Lf + math.pi * R + 0.5 + STIF_M + HDR_L / 2, 3))
          OUT.append(dict(slot=p, kind=kind, module=T["mod"], conn=T["conn"], side="H" if so < 0 else "O", tilt_deg=s["tilt_deg"], off_normal_deg=s.get("off_normal_deg", 0.0),
                          mouth_height=s["mouth_centre_height"], seat_height=round(seat_h, 3), seat_plan_x=round(Bx, 3), y=s["y"],
                          stiffener_bottom_heights=[round(stiff_bot[0][1], 3), round(stiff_bot[1][1], 3)], stiffener_plan_x=sorted([round(stiff_bot[0][0], 3), round(stiff_bot[1][0], 3)]),
                          flap=Lf, fold_r=R, fold_ok=R >= FOLD_RMIN, fold_outer_x=best["x_fold"], speaker_clearance=spk_clr,
                          jm_plan=[best["x_hc"], s["y"]], jm_rot=0 if so < 0 else 180, jm_x_range=best["rec_x"], jm_ok=best["ok"], jm_conflicts=best["why"],
                          flex_len=round(L_flex, 1), plug_standoff=s.get("plug_overmold_standoff", 0.0),
                          frame_back_height=round(fb, 2), collar_top_height=round(collar_top, 2), sleeve_len_axis=sleeve_len, unfolded=unfolded))
          CHK.append(dict(check="%s fold R %.2f >= %.1f" % (p, R, FOLD_RMIN), value=R, ok=R >= FOLD_RMIN))
          CHK.append(dict(check="%s JM receptacle clear of H13 / clamp posts (flap %.1f)" % (p, Lf), value=best["rec_x"], ok=best["ok"]))
          if spk_clr is not None: CHK.append(dict(check="%s fold to speaker body (X) clearance" % p, value=spk_clr, ok=spk_clr >= 0.5))
          CHK.append(dict(check="%s sleeve length along axis (seat -> collar) > 3" % p, value=sleeve_len, ok=sleeve_len > 3.0))
run()
for kind in TYPES: LF_FIX[kind] = max(o["flap"] for o in OUT if o["kind"] == kind)   # ONE module design per type: the largest flap needed by any slot
run()
# neighbours: stiffener gap in Y (cradle wall between modules) and H/O inboard gap
by = {o["slot"]: o for o in OUT}
for a_, b_ in (("C1", "C2"), ("C2", "C3"), ("C4", "C5"), ("C5", "C6"), ("A1", "A2"), ("A3", "A4")):
    t = TYPES[by[a_]["kind"]]; pitch = abs(by[a_]["y"] - by[b_]["y"]); g = round(pitch - 2 * t["sy"], 2)
    CHK.append(dict(check="stiffener Y gap %s/%s (cradle wall %.1f + 2 x 0.1)" % (a_, b_, WALL), value=g, ok=g >= WALL + 0.2))
    gp = round(pitch / 2 - WALL / 2 - PADDLE_W / 2, 2); CHK.append(dict(check="header paddle to cradle wall %s/%s (per side)" % (a_, b_), value=gp, ok=gp >= 0.2))
for a_, b_ in (("C1", "C4"), ("A1", "A3")):
    g = round(by[b_]["stiffener_plan_x"][0] - by[a_]["stiffener_plan_x"][1], 2); CHK.append(dict(check="H/O stiffener inboard gap %s/%s" % (a_, b_), value=g, ok=g >= 1.0))
for kind in TYPES: CHK.append(dict(check="%s module flap (one design for all slots)" % kind, value=LF_FIX[kind], ok=True))
for c_ in CHK: print("CHECK", "OK " if c_["ok"] else "NOK", c_["check"], c_["value"])
json.dump(dict(rev="2026-10-02 ~12:35 ET (D-IO16 port modules; axis %s)" % ("%.1f deg" % F["tilt"]["override_deg"] if F["tilt"]["override_deg"] else "normal to the plate"),
               stack=dict(fpc_t=FPC_T, psa_t=PSA_T, stiffener_t=STIF_T, stack_t=STACK_T, mated=MATED, hdr=[HDR_L, HDR_W], rec=[REC_L, REC_W], plate_t=PLATE_T, sleeve_t=SLEEVE_T, collar_w=COLLAR_W),
               types=TYPES, flap=LF_FIX, posts=POSTS, checks=CHK, modules=OUT), open("/workspace/kicad/macpro62-io-modules/modules.json", "w"), indent=1)
for o in OUT: print(o["slot"], o["side"], "seat %.2f stiffbot %s" % (o["seat_height"], o["stiffener_bottom_heights"]), "flap", o["flap"], "R", o["fold_r"], "fold_x", o["fold_outer_x"],
                    "spk", o["speaker_clearance"], "JM", o["jm_plan"], o["jm_x_range"], o["jm_conflicts"], "Lflex", o["flex_len"], "fb", o["frame_back_height"], "sleeve", o["sleeve_len_axis"])
