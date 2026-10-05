"""Port-module geometry (D-IO16, rev 2026-10-02 ~13:30 ET: per-type JLC stackup, Hong Cheng 13.7 USB-A, loop fold for MOD-A, real DF40 + DFN-8 EEPROM paddle;
rev 2026-10-04 ~09:40 ET: MOD-C uses the real HOAUC HYCW417-USBC24-180B land pattern (EasyEDA C5342202): courtyard 6.25 x 3.65 and 4 THT shell legs 1.8 at u +/-4.1 (tht_tips checked)). Replaces risers_geom.py (column risers, D-IO14).
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
PSA_T, STIF_T = 0.05, 1.0                       # stiffener PSA, FR4 port stiffener
PSTIF_T = 0.6                                   # FR4 paddle stiffener (JLC 0.6; was 1.0) - more room under the port stiffener (MOD-A)
MATED = 1.5                                     # DF40C-50DS + DF40C-50DP mated height
HDR_BODY_L, HDR_BODY_W = 11.52, 2.97            # DF40C-50DP-0.4V(51) body (Hirose drawing); 25 pads/row at 0.4
REC_L, REC_W = 12.9, 4.4                        # DF40C-50DS courtyard on the main board
PADDLE_W = 6.5                                  # header paddle (stiffened) and tail width (rev 2026-10-04 ~10:30 ET 6.4 -> 6.5: the real DF40C-50DP pad rows end at |v| 1.685, 8 x 0.156 paddle lanes + 0.3 edge keep-out need 3.25); leaves 0.95 cradle ledges at |v| 3.45-4.4
STIF_M = 1.0                                    # JLC: stiffener >= 1.0 beyond pads (tail-entry side)
HDR_PAD_END = 5.45                              # outermost header pad edge from the header centre: Hirose DF40C-50DP corner fitting pads 0.35 at +-5.275 (catalogue layout, was 4.915 = last contact)
HDR_CRT = 6.01                                  # header courtyard half-length (body 11.52 / 2 + 0.25; the corner fitting pads end at 5.45, inside the body)
HDR_NEAR = STIF_M + HDR_PAD_END                 # paddle stiffener start -> header centre (6.45: JLC >= 1.0 beyond the pads incl. the fitting pads)
EE_CRT = 1.675                                  # BL24C02F-NTRC DFN-8 2 x 3 courtyard half-length along u (KiCad DFN-8-1EP_2x3mm, rotated 180)
EE_OFF = HDR_CRT + EE_CRT + 0.05                # header centre -> EEPROM centre (7.735)
HDR_FAR = EE_OFF + 1.375 + 0.3                  # header centre -> free paddle end (EEPROM pad end + 0.3 copper-to-edge) = 9.41
R_RULE, R_LOOP = 12.0, 15.0                     # bend radius rule: R >= 12 x t (JLC static >= 10 x t for 2-layer, + 20 %); loop-fold target 15 x t
FLOOR_CLR = 0.3                                 # loop bottom to main-board top (keep-out below)
LEDGE_CLR, WALL = 0.2, 0.8                      # tail / paddle clearance to the cradle ledges (full-height ledge walls at |v| >= tw/2 + 0.2), MJF PA12 min wall
PLATE_T, PLATE_CLR = 1.6, 0.3                   # clamp plate (MJF PA12, ribbed) thickness, gap below the metal frame back
SLEEVE_T, COLLAR_W = 0.2, 1.0                   # SUS304 sleeve wall, collar flange width
# fpc_t: JLC 2-layer 50 um PI core 0.19 (impedance stackup, 90/100 ohm on solid L2) or 25 um core 0.11 (MOD-A: loop fold, cross-hatched L2)
# sx_out / sx_in: stiffener half-length toward the outboard (tail) / inboard edge; tht: THT lead (u, protrusion below the seat) for the tip check
TYPES = {
 "USBC": dict(mod="MOD-C", conn="HOAUC HYCW417-USBC24-180B (C5342202) SMD + 4 THT shell legs 1.8", fp="HOAUC_HYCW417-USBC24-180B", crt=(6.25, 3.65), sx_out=6.0, sx_in=6.0, sy=4.4,
              tw=PADDLE_W, fpc_t=0.19, shell=(8.94, 3.26), tht=[(4.1, 1.8, "shell leg"), (-4.1, 1.8, "shell leg")], slots=["C1", "C2", "C3", "C4", "C5", "C6"]),
 "USBA": dict(mod="MOD-A", conn="Hong Cheng HC-USB3.0-L137-WJ (C7501870) THT, H 13.7; alt kinghelm KH-3.0AF180ZJ-11.5JB (C2979037, H 11.5)", fp="MP62_MOD_USB_A3_HC-USB3.0-L137-WJ",
              crt=(7.45, 3.75), sx_out=9.0, sx_in=8.4, sy=4.4, tw=PADDLE_W, fpc_t=0.11, shell=(13.3, 5.7),
              tht=[(6.575, 3.0, "shell leg"), (-6.575, 3.0, "shell leg"), (4.0, 2.0, "pin 5"), (-4.0, 2.0, "pin 9"), (3.5, 2.0, "pin 1")], slots=["A1", "A2", "A3", "A4"]),
 "HDMI": dict(mod="MOD-H", conn="HOAUC HYC79-HDMIA19-105 (C711353) 19 SMD (1 row, 0.5) + 3 THT legs D1.3", fp="HOAUC_HYC79-HDMIA19-105", crt=(8.9, 4.75), sx_out=9.6, sx_in=9.6, sy=4.85,
              tw=PADDLE_W, fpc_t=0.19, shell=(14.0, 4.55), tht=[(7.25, 2.2, "leg"), (-7.25, 2.2, "leg"), (0.0, 2.2, "centre leg")], slots=["HDMI"]),   # rev ~10:30 ET real land pattern (tools/make_fp_hyc79.py): pad row at |v| 2.5-4.5 -> sy 4.7 -> 4.85 (0.35 copper-to-edge; the FPC ends at the stiffener edge on the +-v sides, so the JLC 1.0 stiffener overhang applies on the tail-exit edge only; 5.5 would hit the HDMI clamp post at Y 114.6); legs ~2.0 below the seat (drawing scale, +0.2)
}
def stack_t(T): return T["fpc_t"] + PSA_T + STIF_T
H13 = (53.38, 58.38, 2.65)                      # I/O-frame centre standoff (courtyard r)
SPK = dict(x=(8.3, 31.5), y=(36.5, 97.0))       # stock speaker (F side), stadium
POSTS = {"C": [(53.19, 69.8), (53.19, 49.3)], "A": [(53.19, 49.3), (53.19, 25.5)], "HDMI": [(63.02, 114.6), (53.6, 114.35)]}   # rev ~14:25 ET: HDMI moved to the +X column (stock order, scan 83f0b85e) -> posts mirrored about the HDMI axis swap (were 43.8 / 56.0)   # clamp-screw posts (M2 SMT nut in the main board)
POST_R = 2.2
# rev 2026-10-04 ~15:50 ET (Aidan): clamp post HDMI -X (H25) (50.82, 111.0) -> (53.6, 114.35) (tools/hdmi_post_search.py: nearest spot (53.5, 114.25) to the asked (52.3, 111.6) + ~0.1 for the +-0.15 trace tolerance,
#   that clears the I/O-plate power-button ear-1 M1.4 head / Ø3.0 boss / carrier ring + ear lug by >= 0.3 in plan; the asked spot hits the HDMI stiffener end by 0.86).
#   Its M2 head now sits under the frame bar between the HDMI slot and the AC opening (like H24): COUNTERSUNK M2 (ISO 7046, top flush with the clamp plate) required.
POST_BODY_R = 2.0                               # SMT standoff OD 4.0 (H25 footprint) / printed post Ø3.8 / M2 head Ø3.8 (plan check vs the module stiffener and receptacle collar)
# rev 2026-10-04 ~12:35 ET (Aidan): clamp post C upper (H21) 70.8 -> 69.8 so its Ø3.8 post clears the plate SCR_C1 Ø5.0 clamp-plate hole at (53.76, 75.47): web 0.3 -> 1.3
def spk_halfw(y):   # stadium half-width at Y
    r = (SPK["x"][1] - SPK["x"][0]) / 2; c = (SPK["x"][0] + SPK["x"][1]) / 2
    if y < SPK["y"][0] or y > SPK["y"][1]: return None
    yc = min(max(y, SPK["y"][0] + r), SPK["y"][1] - r); d = abs(y - yc)
    return c, math.sqrt(max(r * r - d * d, 0.0))
def frame_back_h(x): u = x - PC; return -R0 + math.sqrt(R_FRB ** 2 - u * u) - ZB
LF_FIX = {}; L_FIX = {}
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
          t = T["fpc_t"]; ST_T = stack_t(T)
          E = P(xo * T["sx_out"], t / 2)                                  # FPC mid-plane at the outboard stiffener edge
          stiff_bot = [P(xo * T["sx_out"], ST_T), P(-xo * T["sx_in"], ST_T)]
          ht = MATED + t / 2                                              # tail FPC mid-plane over the mated header
          r_min = R_RULE * t
          best = None
          for k in range(0, 61):
              Lf = 0.5 + 0.1 * k
              if LF_FIX.get(kind) is not None: Lf = LF_FIX[kind]
              Fp = (E[0] + so * Lf * abs(ex[0]), E[1])
              d = Fp[1] - ht
              if d / 2 >= r_min: R, alpha, fmode = d / 2, 0.0, "C"            # plain 180 deg C-fold
              else:                                                            # loop fold: arc R over 180 + a, counter-arc a; drop 2R cos a = d
                  R = R_LOOP * t; alpha = math.acos(min(1.0, d / (2 * R))); fmode = "loop"
              if L_FIX.get(kind) is not None:                                  # one module design per type: fixed fold length -> solve R, a with R (pi + 2a) = L, 2 R cos a = d
                  Lx = L_FIX[kind]; lo, hi = 0.0, 1.2
                  for _ in range(60):
                      am = (lo + hi) / 2; Rm = Lx / (math.pi + 2 * am)
                      if 2 * Rm * math.cos(am) > d: lo = am
                      else: hi = am
                  alpha = (lo + hi) / 2; R = Lx / (math.pi + 2 * alpha); fmode = "C" if alpha < math.radians(2) else "loop"
              Lfold = R * (math.pi + 2 * alpha)
              x_fe = Fp[0] - so * 2 * R * math.sin(alpha)                     # fold end (lower leg starts, heading inboard)
              z_low = Fp[1] - 2 * R - t / 2 if fmode == "loop" else ht - t / 2  # lowest flex surface above the board
              x_s0 = x_fe - so * 0.5                                           # paddle stiffener starts 0.5 inboard of the fold end
              x_hc = x_s0 - so * HDR_NEAR
              x_p1 = x_hc - so * HDR_FAR                                       # free paddle end
              x_fold = Fp[0] + so * (R + t / 2)                                # outermost fold point
              y = s["y"]; ok = True; why = []
              xr = sorted([x_hc - REC_L / 2, x_hc + REC_L / 2])
              def hits(cx, cy, r): return (xr[0] - r < cx < xr[1] + r) and abs(y - cy) < REC_W / 2 + r
              if hits(H13[0], H13[1], H13[2]): ok = False; why.append("H13")
              for g, pl in POSTS.items():
                  for (px_, py_) in pl:
                      if hits(px_, py_, POST_R): ok = False; why.append("post")
              if z_low < FLOOR_CLR: ok = False; why.append("loop hits board")
              best = dict(Lf=round(Lf, 2), R=round(R, 3), alpha=round(math.degrees(alpha), 2), mode=fmode, Lfold=round(Lfold, 3), x_fe=round(x_fe, 3), z_low=round(z_low, 3),
                          x_fold=round(x_fold, 3), x_hc=round(x_hc, 3), x_p1=round(x_p1, 3), Fp=[round(Fp[0], 3), round(Fp[1], 3)], rec_x=[round(v, 3) for v in xr], ok=ok, why=why)
              if ok or LF_FIX.get(kind) is not None: break
          Lf, R = best["Lf"], best["R"]; alpha = math.radians(best["alpha"])
          # fold path in (plan X, height) - FPC mid-plane, with the unfolded u at each point (for the 3D pin-1 check)
          path = []
          u_E = T["sx_out"]
          for i in range(0, 11):
              uu = -T["sx_in"] + (u_E + T["sx_in"]) * i / 10; X_, Z_ = P(xo * uu, t / 2); path.append((round(uu, 3), round(X_, 3), round(Z_, 3)))
          Fp = best["Fp"]; u0 = u_E + Lf; path.append((round(u0, 3), Fp[0], Fp[1]))
          n1 = 36
          for i in range(1, n1 + 1):
              ph = (math.pi + alpha) * i / n1; path.append((round(u0 + R * ph, 3), round(Fp[0] + so * R * math.sin(ph), 3), round(Fp[1] - R + R * math.cos(ph), 3)))
          if alpha > 0:
              C2 = (Fp[0] - 2 * so * R * math.sin(alpha), Fp[1] - R - 2 * R * math.cos(alpha))
              for i in range(1, 9):
                  ph = alpha * (1 - i / 8); path.append((round(u0 + R * (math.pi + alpha) + R * alpha * i / 8, 3), round(C2[0] + so * R * math.sin(ph), 3), round(C2[1] + R * math.cos(ph), 3)))
          u_fe = u0 + best["Lfold"]; ul = u_fe + 0.5 + HDR_NEAR + HDR_FAR
          path.append((round(ul, 3), round(best["x_fe"] - so * (ul - u_fe), 3), round(ht, 3)))
          # THT lead tips vs the paddle top (the paddle stiffener is on top of the folded paddle)
          pad_top = MATED + t + PSA_T + PSTIF_T
          px = sorted([best["x_fe"] - so * 0.5, best["x_p1"]])
          tips = []
          for (ut, prot, nm) in T["tht"]:
              Xt, Zt = P(xo * ut, prot)                                      # lead tip (protrusion measured from the seat = FPC top)
              under = px[0] - 0.3 < Xt < px[1] + 0.3
              stub = prot - ST_T                                             # lead length below the stiffener
              trim = round(min(stub, stub - (0.3 - (Zt - pad_top))) if under else stub, 2)   # max stub keeping 0.3 to the paddle
              tips.append(dict(lead=nm, u=ut, tip_x=round(Xt, 3), tip_h=round(Zt, 3), over_paddle=under, clr=round(Zt - pad_top, 3) if under else round(Zt, 3), stub=round(stub, 2), trim_to=trim))
          # gap between the port-stiffener bottom and the paddle top, over the paddle
          sb_gap = []
          for i in range(0, 81):
              uu = -T["sx_in"] + (T["sx_in"] + T["sx_out"]) * i / 80; X_, Z_ = P(xo * uu, ST_T)
              if px[0] <= X_ <= px[1]: sb_gap.append(Z_ - pad_top)
          sb_gap = round(min(sb_gap), 3) if sb_gap else None
          # speaker clearance of the fold (F side stadium)
          sp = spk_halfw(s["y"]) if so < 0 else None; spk_clr = None   # speaker = H side only
          if sp: spk_clr = round((best["x_fold"] - (sp[0] + sp[1])) if so < 0 else ((sp[0] - sp[1]) - best["x_fold"]), 2)
          # flex electrical length (port pads -> header pins): half stiffener + flap + fold + header run
          L_flex = T["sx_out"] + Lf + best["Lfold"] + 0.5 + HDR_NEAR + 2.0
          # sleeve / collar / clamp plate heights (along the axis from the seat)
          sw, sh = T["shell"]; xs_out = s["x"] + so * (sw / 2 + SLEEVE_T + COLLAR_W)
          fb = frame_back_h(s["x"])                                         # at the axis: the collar plane is ~parallel to the frame back (axis normal to the plate)
          collar_top = fb - PLATE_CLR - PLATE_T                            # collar top = clamp plate underside
          seat_h = s["riser_top_height"]
          sleeve_len = round((collar_top - seat_h) / math.cos(a), 2)
          u_fe = T["sx_out"] + Lf + best["Lfold"]
          unfolded = dict(stiff_u=[-T["sx_in"], T["sx_out"]], stiff_v=[-T["sy"], T["sy"]], tail_w=T["tw"], fold_u=[round(T["sx_out"] + Lf, 3), round(u_fe, 3)],
                          hdr_stiff_u=[round(u_fe + 0.5, 3), round(u_fe + 0.5 + HDR_NEAR + HDR_FAR, 3)], paddle_w=PADDLE_W, hdr_centre_u=round(u_fe + 0.5 + HDR_NEAR, 3),
                          ee_centre_u=round(u_fe + 0.5 + HDR_NEAR + EE_OFF, 3), fpc_t=t)
          ko = None   # main-board keep-out under a loop fold: plan X range, Y range, max part height
          if best["mode"] == "loop":
              xs = sorted([best["x_fe"], best["x_fold"]])
              ko = dict(x=[round(xs[0] - 0.3, 2), round(xs[1] + 0.3, 2)], y=[round(s["y"] - T["tw"] / 2 - 0.3, 2), round(s["y"] + T["tw"] / 2 + 0.3, 2)], max_part_h=round(best["z_low"] - 0.2, 2))
          OUT.append(dict(slot=p, kind=kind, module=T["mod"], conn=T["conn"], side="H" if so < 0 else "O", tilt_deg=s["tilt_deg"], off_normal_deg=s.get("off_normal_deg", 0.0),
                          mouth_height=s["mouth_centre_height"], seat_height=round(seat_h, 3), seat_plan_x=round(Bx, 3), y=s["y"],
                          stiffener_bottom_heights=[round(stiff_bot[0][1], 3), round(stiff_bot[1][1], 3)], stiffener_plan_x=sorted([round(stiff_bot[0][0], 3), round(stiff_bot[1][0], 3)]),
                          flap=Lf, fold_r=R, fold_ratio=round(R / t, 1), fold_mode=best["mode"], fold_alpha_deg=best["alpha"], fold_len=best["Lfold"], fold_low_h=best["z_low"],
                          fold_ok=R >= r_min - 1e-6, fold_outer_x=best["x_fold"], speaker_clearance=spk_clr, fpc_t=t, stack_t=round(ST_T, 3),
                          paddle_x=[round(v, 3) for v in px], paddle_top_h=round(pad_top, 3), stiff_to_paddle_gap=sb_gap, tht_tips=tips, fold_keepout=ko, path=path,
                          jm_plan=[best["x_hc"], s["y"]], jm_rot=180 if so < 0 else 0, jm_x_range=best["rec_x"], jm_ok=best["ok"], jm_conflicts=best["why"],
                          flex_len=round(L_flex, 1), plug_standoff=s.get("plug_overmold_standoff", 0.0),
                          frame_back_height=round(fb, 2), collar_top_height=round(collar_top, 2), sleeve_len_axis=sleeve_len, unfolded=unfolded))
          CHK.append(dict(check="%s fold (%s) R %.2f = %.1f x t >= %.0f x t (JLC 10 x + 20 %%)" % (p, best["mode"], R, R / t, R_RULE), value=R, ok=R >= r_min - 1e-6))
          CHK.append(dict(check="%s fold lowest point above the main board >= %.1f" % (p, FLOOR_CLR), value=best["z_low"], ok=best["z_low"] >= FLOOR_CLR))
          if sb_gap is not None: CHK.append(dict(check="%s port stiffener bottom to paddle top >= 0.25" % p, value=sb_gap, ok=sb_gap >= 0.25))
          for tp in tips:
              if tp["over_paddle"]: CHK.append(dict(check="%s THT %s over the paddle: untrimmed clearance %.2f, trim stub (%.2f) to <= %.2f" % (p, tp["lead"], tp["clr"], tp["stub"], tp["trim_to"]), value=tp["trim_to"], ok=tp["trim_to"] >= 0.3))
          CHK.append(dict(check="%s JM receptacle clear of H13 / clamp posts (flap %.1f)" % (p, Lf), value=best["rec_x"], ok=best["ok"]))
          if spk_clr is not None: CHK.append(dict(check="%s fold to speaker body (X) clearance" % p, value=spk_clr, ok=spk_clr >= 0.5))
          CHK.append(dict(check="%s sleeve length along axis (seat -> collar) > 3" % p, value=sleeve_len, ok=sleeve_len > 3.0))
run()
for kind in TYPES: LF_FIX[kind] = max(o["flap"] for o in OUT if o["kind"] == kind)   # ONE module design per type: the largest flap needed by any slot
run()
for kind in TYPES: L_FIX[kind] = max(o["fold_len"] for o in OUT if o["kind"] == kind)  # ... and one fold length (the longest); the other slots take the slack in the loop
run()
for _it in range(20):   # a slot whose fold takes slack may move its JM into H13 / a post: lengthen that type's flap by 0.1 and re-solve
    bad = {o["kind"] for o in OUT if not o["jm_ok"]}
    _by = {o["slot"]: o for o in OUT}
    for a_, b_ in (("C1", "C4"), ("A1", "A3")):                              # opposite header paddles must keep >= 0.8 (cradle rib between them)
        if _by[b_]["paddle_x"][0] - _by[a_]["paddle_x"][1] < 0.8: bad.add(_by[a_]["kind"])
    bad = sorted(bad)
    if not bad: break
    for kind in bad: LF_FIX[kind] = round(LF_FIX[kind] + 0.1, 2); L_FIX[kind] = None
    run()
    for kind in bad: L_FIX[kind] = max(o["fold_len"] for o in OUT if o["kind"] == kind)
    run()
# neighbours: stiffener gap in Y (cradle wall between modules) and H/O inboard gap
by = {o["slot"]: o for o in OUT}
for a_, b_ in (("C1", "C2"), ("C2", "C3"), ("C4", "C5"), ("C5", "C6"), ("A1", "A2"), ("A3", "A4")):
    t = TYPES[by[a_]["kind"]]; pitch = abs(by[a_]["y"] - by[b_]["y"]); g = round(pitch - 2 * t["sy"], 2)
    CHK.append(dict(check="stiffener Y gap %s/%s (cradle wall %.1f + 2 x 0.1)" % (a_, b_, WALL), value=g, ok=g >= WALL + 0.2))
    lw = round(t["sy"] - (t["tw"] / 2 + LEDGE_CLR), 2); CHK.append(dict(check="cradle ledge bearing width under the stiffener edge %s/%s (tail/paddle %.1f + 2 x %.1f)" % (a_, b_, t["tw"], LEDGE_CLR), value=lw, ok=lw >= 0.8))
for o in OUT:   # rev 15:50 ET: every clamp post (Ø3.8 cradle post) vs every module's stiffener and receptacle collar in plan (>= 0.3)
    t = TYPES[o["kind"]]; sx = o["stiffener_plan_x"]; cx = o["seat_plan_x"]; cw = t["shell"][0] / 2 + SLEEVE_T + COLLAR_W; ch = t["shell"][1] / 2 + SLEEVE_T + COLLAR_W
    for g_, pl in POSTS.items():
        for (px_, py_) in pl:
            ds = math.hypot(max(sx[0] - px_, 0, px_ - sx[1]), max(o["y"] - t["sy"] - py_, 0, py_ - o["y"] - t["sy"])) - POST_BODY_R
            dc = math.hypot(max(cx - cw - px_, 0, px_ - cx - cw), max(o["y"] - ch - py_, 0, py_ - o["y"] - ch)) - POST_BODY_R
            if min(ds, dc) < 3.0: CHK.append(dict(check="clamp post %s (%.2f,%.2f) to %s stiffener / collar plan clearance >= 0.3" % (g_, px_, py_, o["slot"]), value=[round(ds, 2), round(dc, 2)], ok=min(ds, dc) >= 0.3))
for a_, b_ in (("C1", "C4"), ("A1", "A3")):
    g = round(by[b_]["stiffener_plan_x"][0] - by[a_]["stiffener_plan_x"][1], 2); CHK.append(dict(check="H/O stiffener inboard gap %s/%s" % (a_, b_), value=g, ok=g >= 1.0))
    g = round(by[b_]["paddle_x"][0] - by[a_]["paddle_x"][1], 2); CHK.append(dict(check="H/O header-paddle gap %s/%s" % (a_, b_), value=g, ok=g >= 0.8))
    g = round(by[b_]["jm_x_range"][0] - by[a_]["jm_x_range"][1], 2); CHK.append(dict(check="H/O JM receptacle courtyard gap %s/%s" % (a_, b_), value=g, ok=g >= 0.5))
for kind in TYPES: CHK.append(dict(check="%s module flap (one design for all slots)" % kind, value=LF_FIX[kind], ok=True))
for c_ in CHK: print("CHECK", "OK " if c_["ok"] else "NOK", c_["check"], c_["value"])
json.dump(dict(rev="2026-10-02 ~13:30 ET (D-IO16 port modules; axis %s)" % ("%.1f deg" % F["tilt"]["override_deg"] if F["tilt"]["override_deg"] else "normal to the plate"),
               stack=dict(fpc_t={k: T["fpc_t"] for k, T in TYPES.items()}, psa_t=PSA_T, stiffener_t=STIF_T, paddle_stiffener_t=PSTIF_T, stack_t={k: round(stack_t(T), 3) for k, T in TYPES.items()}, mated=MATED, hdr_body=[HDR_BODY_L, HDR_BODY_W], hdr_near=HDR_NEAR, hdr_far=HDR_FAR, r_rule=R_RULE, r_loop=R_LOOP, rec=[REC_L, REC_W], plate_t=PLATE_T, sleeve_t=SLEEVE_T, collar_w=COLLAR_W),
               types=TYPES, flap=LF_FIX, fold_len=L_FIX, posts=POSTS, checks=CHK, modules=OUT), open("/workspace/kicad/macpro62-io-modules/modules.json", "w"), indent=1)
for o in OUT: print(o["slot"], o["side"], "seat %.2f stiffbot %s" % (o["seat_height"], o["stiffener_bottom_heights"]), "flap", o["flap"], "R", o["fold_r"], "fold_x", o["fold_outer_x"],
                    "spk", o["speaker_clearance"], "JM", o["jm_plan"], o["jm_x_range"], o["jm_conflicts"], "Lflex", o["flex_len"], "fb", o["frame_back_height"], "sleeve", o["sleeve_len_axis"])
