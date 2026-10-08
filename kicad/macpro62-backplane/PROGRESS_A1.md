# BP rev A1 (BP-G4) work log - resume notes (keep updated)
Archive of the fp6 6L floorplan: variants/fp6_floorplan_6L/.
Pipeline: tools/bp_pins.py (pin maps, FS lanes reversed = ICD rev 3.1 proposal) -> tools/bp_model.py (netlist+BOM) ->
tools/build_bp.py (4L board, keepouts, placement, nets) -> tools/bp_hs.py (PCIe/REFCLK coupled routing, locked) ->
Freerouting (low speed/power) -> tools/bp_finish.py (SES import, GND pours, DRC, JLC outputs) ; tools/build_bp_sch.py (schematic).
Stackup JLC04161H-7628: L1 RX pairs + parts (85R 0.26/0.125), L2 GND, L3 TX pairs (85R 0.21/0.127 ref L4) + power, L4 GND + short RX breakouts.
Connector breakout (local u along pins, v inward): TX vias (u_c,1.6)/(u_c,2.5), RX dive vias (u_c+0.9,1.6/2.5), between-row vias (u_P/u_N,-1.475),
GND bridge B->A + via at v=-4.1. Polarity self-corrects (P to far via).
Decisions: redrivers removed (Gen4 budget); RP2350B; INA226; 2x TPS563201; J7 M.2 + J8 SWD DNP; MOD LEDs on BP; BP EEPROM dropped (RP2350 OTP).
M.2 SATA: host TX -> pins 49(+)/47(-), host RX <- 41(+)/43(-) (confirmed vs PCI-SIG module table).
Status: placement stage done (14:32), next = HS router.

## Status 2026-10-04 (ET)
- HS routing COMPLETE: all 43 pairs (FP TX/RX 0-15, FS TX/RX 0-3, 2 REFCLK). FP_RX0 = L1 -> transition (-8.5,14) -> L4.
- Pipeline: build_bp.py -> bp_hs.py (work/bp_patterns) -> bp_tune.py work/bp_patterns.kicad_pcb work/bp_tuned.kicad_pcb (skew -> 0.000) -> DRC 0 errors (499 unconnected low-speed)
- bp_skew.py = length/skew report.
- NEXT: freerouting low-speed+power on work/bp_tuned -> zones -> DRC 0 -> schematic/ERC.
- 15:22 ET: tools/bp_ls.py fan (118 GND fan-out vias; skipped J7-73,U5-7,J1-A82/83,U1-62 -> L1 pour) ; route = fr-2.1.0.jar (Java 21; freerouting.jar needs Java 25) -> work/bp_fan.ses ; import -> work/bp_routed.kicad_pcb
- 15:24 ET: resumed. Freerouting (pid 1008331, 150 passes) still running -> no SES yet. Writing tools/build_bp_sch.py meanwhile.
- 15:26 ET: schematic done (tools/build_bp_sch.py, flat A0, old stub sheets -> variants/sch_blockdiagram_A/). fp-lib-table += MP62_BP. ERC: see erc_report.txt
- 15:29 ET: tools/bp_finish.py [src] [dst] works (tested on work/bp_fan -> work/test_fin): NC nets, refs->F.Fab, all fp silk removed, fps exported to MP62_BP.pretty + relinked MP62_BP:*, GND pours L1-L4, 3mm stitching, backplane.kicad_dru (pour >=0.5 from 85R pairs). Only via_dangling (unrouted LS) left. Waiting for Freerouting.
- schematic: footprints must be MP62_BP:<name> -> build_bp_sch.py maps fp lib to MP62_BP (TODO if not yet)
- 15:30 ET: sch footprints relinked to MP62_BP:*, JP/H in_bom no -> parity clean on test board; ERC 0
- 15:34 ET: tools/jlc_out.py (gerbers/drill/BOM/CPL) tested OK; tools/bp_zreport.py -> docs/impedance_A1.json (L1 83.1, L3 86.4, USB 90.0 ohm)
- 15:34 ET: first FR run killed (pass4: 261 unrouted, 3 min/pass). 3V3_SB/DVDD class -> 0.2/0.1 (0.4-pitch QFN). Diagnostic 3-pass run started.
- 15:35 ET: docs/loss_budget_A1.md written
- 15:39 ET: FR runs: HS nets dropped from DSN (were seen incomplete by FR), PWR 0.3 in DSN (0.5 cannot enter J1/J7 pins). 4-pass run started.
- 15:50 ET: FR 2.1 ignores --router.max_passes (ran >7 passes, 166 unrouted @7) -> use -mp N. 2-pass diagnostic run for unrouted analysis.
- 16:04 ET: FR 2.0.1/2.1.0 ignore -mp/max_passes -> testing job_timeout in /tmp/freerouting/freerouting.json (FRTIME env)
- 16:08 ET: job_timeout (--router.job_timeout=HH:MM:SS) stops FR and WRITES the SES -> use FRTIME to bound runs. 2.5-min run: 187 unrouted.
- 16:10 ET: ROOT CAUSE of FR failures: EDGE_RING via keepout exported as polygon+window -> FR blocked vias everywhere; replaced by 48 sectors; MCIO_RIBBON footprint-only areas removed from DSN. 3-min run (no L3 plane) started.
- 16:14 ET: 16:10 run finished (ses written 16:13): still 183 unrouted after 3 passes. Investigating.
- 16:15 ET: L2 -> (type power) in DSN instead of board-wide wire_keepout (suspected via blocker). FR pid 1043028, 2-min, log work/bp_route_run.log + /tmp/freerouting/freerouting.log, out work/bp_fan.ses -> work/bp_routed.kicad_pcb
- 16:19 ET: 2-min test with L2 power layer: vias used, 154 unrouted. Now L3 3V3_SB plane (south half, PLANE=1) + 12-min FR run pid 1044487 (FRTIME=00:12:00) -> work/bp_fan.ses -> work/bp_routed.kicad_pcb; log work/bp_route_run.log
- 16:20 ET: cost-down: R27 ext -> R33 basic (USB FS series R) in bp_model; bp_finish syncs value/LCSC from model; sch regenerated, ERC 0
- 16:32 ET: round 1 done (16:31): 53-58 unrouted -> checkpoint work/bp_routed_r1.kicad_pcb. Round 2 (redsn = resume from bp_routed) FR pid 1048921, FRTIME 12 min -> work/bp_routed.kicad_pcb
- 16:33 ET: bp_pro: PWR_FINE class (3V3_SB, DVDD 0.1/0.2), PWR track 0.3. bp_finish on r1 -> only via/track_dangling + starved_thermal + 69 unconnected (zone refill clears all clearance errs)
- 16:44 ET: Freerouting round 2 (pid 1048921, redsn resume, 12 min, log work/bp_route_run.log) done: 44 unrouted (from 59). Checkpoint work/bp_routed_r2.kicad_pcb
- 16:46 ET: round 3 (redsn resume from r2) FR pid 1054393, FRTIME 00:14:00, log work/bp_route_run.log + /tmp/freerouting/freerouting.log, out work/bp_fan.ses -> work/bp_routed.kicad_pcb
- 16:57 ET: tools/bp_fix.py (grid A* clean-up router, 0.05 mm grid, L1/L3/L4 + vias) written; first test: dense U1 (RP2350B) area needs rip-up -> adding rip-up/reroute
- 17:05 ET: round 3 (pid 1054393) finished 17:00, SES imported: 41 unrouted -> checkpoint work/bp_routed_r3.kicad_pcb. bp_fix: fixed float32 g-score bug (A* skipped nodes)
- 17:07 ET: bp_fix rip-up run on r3 started (pid 1063360, MAXIT 160, weighted A* HW 1.6), out work/bp_fix_r3.kicad_pcb (saved every 10 its), log work/bp_fix_r3.log
- 17:20 ET: bp_fix: A* replaced by skimage MCP (3 layers + via planes, ~10 s/net), fixed soft rip-up mask bug + 'rip own & retry from pads' fallback. Full run on r3: pid 1068868, MAXIT 250, out work/bp_fix_r3.kicad_pcb, log work/bp_fix_r3.log
- 17:28 ET: bp_fix r3 run at iteration ~50, 0 FAIL so far (rip-up cascades re-queue ripped nets)
- 17:42 ET: bp_fix r3 run stopped at it 123 (cascading rips, no convergence); checkpoint work/bp_fix_r3a.kicad_pcb (it 120). Added PathFinder history cost (HINC 15/rip, RIPC x(1+it/40)). New run pid 1075927, MAXIT 300, out work/bp_fix_r3b.kicad_pcb, log work/bp_fix_r3b.log
- 17:55 ET: bp_fix r3b run dead/stopped (no convergence, ~47 nets open). Per Aidan: stop custom router; fix congestion structurally (RP2350B GPIO reassignment + spread parts near U1), then bounded FR.
- 17:59 ET: STRUCTURAL FIX: tools/bp_gpio.py -> tools/gpio_map.json (47/48 RP2350B GPIOs re-assigned by escape side; I2C SDA/SCL + UART TX/RX pin-function constraints kept; escape cost 1919 -> 1728 mm); bp_model reads it. build_bp packer: anchor-nearest placement, 0.6 mm courtyard gap, 1.8 mm U1 ring (old packer: work/build_bp_revA_packer.py.bak). Placement rebuilt (151 parts, 0 fails)
- 18:00 ET: A1b chain: bp_hs 43/43 pairs + bp_tune + bp_ls fan (118 GND vias, L3 plane) done. FR round A1b-1 (fresh, new placement) pid 1083214, FRTIME 00:12:00, log work/bp_route_run.log + /tmp/freerouting/freerouting.log, out work/bp_fan.ses -> work/bp_routed.kicad_pcb
- 18:12 ET: FR A1b-1 done 18:12: 24 unrouted (old placement had ~55 after the same 12 min) -> checkpoint work/bp_routed_a1b_r1.kicad_pcb. FR A1b-2 (redsn resume) pid 1087419, FRTIME 00:12:00, out work/bp_fan.ses -> work/bp_routed.kicad_pcb, log work/bp_route_run.log
- 18:25 ET: FR A1b-2 (pid 1087419) done 18:25: 15 unrouted, stalled (passes 40-49 flat) -> checkpoint work/bp_routed_a1b_r2.kicad_pcb
- 18:26 ET: finish test on a1b_r2: 0 clearance errors; 25 unconnected (15 signal nets + 3V3_SB/GND plane stubs). Script-routing the 15 signal nets with bp_fix (RIP=0, no rip-up cascades), out work/bp_fix_a1b.kicad_pcb, log work/bp_fix_a1b.log
- 18:31 ET: bp_fix RIP=0 pass: 12/16 OK (out work/bp_fix_a1b.kicad_pcb); 4 U1 S/E nets needed rip-up: RIP=1 MAXIT 14 -> all OK, 11 ripped nets queued (out work/bp_fix_a1b2.kicad_pcb). Continuing RIP=1 MAXIT 60 on the queue -> work/bp_fix_a1b3.kicad_pcb, log work/bp_fix_a1b3.log
- 18:38 ET: bp_fix queue run (a1b3) still oscillating (9 nets) around U1 S/E side (J7 M.2 2 mm east of U1, Y1 under the S pins). Stopping script routing; second structural nudge: U1 (-36,-26.5)->(-39.5,-26.5), Y1 -> (-39.5,-34.2), U2 -> (-49.3,-20.5), U1 ring 1.8->2.2 mm, GAP 0.6->0.7; re-run bp_gpio on the new placement
- 18:40 ET: A1c placement chain done (HS 43/43 pairs, tuned, fan). ERC 0 after schematic regen. FR A1c-1 (fresh) pid 1096952, FRTIME 00:12:00, out work/bp_fan.ses -> work/bp_routed.kicad_pcb, log work/bp_route_run.log
- 18:46 ET: resumed; FR A1c-1 (pid 1096952) still running (pass 2 done)
- 18:52 ET: FR A1c-1 done 18:52: 32 unrouted (still improving) -> checkpoint work/bp_routed_a1c_r1.kicad_pcb. FR A1c-2 (redsn resume) pid 1101355, FRTIME 00:12:00, out work/bp_fan.ses -> work/bp_routed.kicad_pcb, log work/bp_route_run.log
- 19:05 ET: FR A1c-2 (pid 1101355) done 19:04: 25 unrouted, flat since pass ~30 -> checkpoint work/bp_routed_a1c_r2.kicad_pcb. No more FR rounds; script remainder.
- 19:08 ET: bp_fix RIP=0 on a1c_r2 remainder (22 nets): 13 OK, 9 fail -> work/bp_fix_a1c.kicad_pcb; one RIP=1 pass (MAXIT 20) next
- 19:13 ET: rip pass 1 (a1c2) + RIP=0 sweep (a1c3): 4 nets left (SATA0_RX_P, VREG_AVDD, EN_5V, FP_SMB_SDA); rip pass 2 limited to these 4

## 19:26 ET: SATA0_RX pair local fixes, time limit reached, STOP
- Started from work/bp_fix_a1c5.kicad_pcb (1 unrouted: SATA0_RX_N). All runs RIP=0 unless noted, each under 1 min.
- Keep-out ring (0.6 mm) around RX_N copper, then route RX_P: P no path.
- Keep-out ring on the other pad's end only (0.5 / 0.9 mm), both orders: the first net then fails too, so both pads share one west exit.
- Rip pass (RIP=1, MAXIT=2) on RX_N: oscillates P<->N, also rips EN_5V. Stopped per the rip-up rule.
- Froze one net (locked) and RIP=1 the other, both ways: no path.
- Removed a dangling L1 stub on SATA0_TX_N (123.1,130.9-131.65): still no path for the second net.
- Hand stubs going west (N at y131.25, P at y130.75, three x lengths): second net still no path. The far end is also tight: locked J1-side HS vias 0.6 mm apart at (138.1/138.7,112.6) board coords.
- Result: best 4L checkpoint is still work/bp_fix_a1c5.kicad_pcb, with 1 unrouted net, SATA0_RX_N (the J7 M.2 SATA RX pair; J7 is DNP). work/bp_fix_a1c7.kicad_pcb is the inverse (RX_N routed, RX_P unrouted).
- Per the 40-min rule, stopped. bp_finish / DRC / jlc_out / cost / zips NOT run on this result. Nothing pushed.
- Options: (a) 6L JLC06161H-2116, +$25-35 per order fab-only ($50-80 vs $25-45 4L), PCBA Economic unchanged; (b) stay 4L and hand-route the RX pair as a coupled pair in the KiCad GUI, after moving the J1-side HS vias or the J7 TX_N via (123.1,131.8); (c) drop SATA0 from J7, which needs Aidan's OK.

## 19:28 ET: option (b) chosen: 4L, hand-route SATA0_RX pair from work/bp_fix_a1c5
- 19:45 new tool tools/bp_pair.py: centerline A* for a coupled pair (85R geometry: L1 0.26/0.125, L3 0.21/0.127), with pair-via sites keyed by travel direction and 0.5 mm straight runs before and after each via. Unlocked non-HS copper counts as soft (penalised, then ripped and re-routed with bp_fix RIP=0). Local nudges: DVDD dangling stub off C33-1, SATA0_TX_N dangling L1 stub, and the J7-39 GND fan-out via moved (123.806,130.292)->(123.75,130.0).
- 19:45 dry run, best result: L1 (J7) -> 1 via (123.0,129.35) -> L3 stripline 45deg -> J1 locked escape vias. That is 2 vias per net including the J1 escape. 0 hard conflicts; 16 soft items in 14 nets to re-route.
- 19:57 bp_pair real run -> work/bp_pair_try1 (13/14 re-routed; FS_PERST_N failed). bp_fix rip pass on FS_PERST_N oscillated with FP_PWR_EN (stopped after 2 passes). Fix: one rip pass on FS_PERST_N with FP_PWR_EN/USB/3V3/5V/FS_MCIO_PRSNT_N protected -> routed with nothing ripped -> work/bp_pair_try4

### 20:09 — SATA0_RX tuned → work/bp_pair_try5.kicad_pcb
- bp_tune TUNE_RE=SATA0_RX_P: 6 bumps (a=0.128, L3). SATA0_RX P/N 29.45/29.45 mm, skew 0.000, 2/2 vias (incl. J1 escape).
- Collateral: SATA0_TX_P 72.5 mm/11 vias, USB2_MCU 8/4 vias, USB2_SPARE 6/13 vias (FR re-route victims).
- Rejected: bp_pair_b1 (L1→L3→L4, RX 3 vias, TX_P fail), bp_pair_c1 (RX 44 mm, 4 fails).

### 20:09 — victim re-route → work/bp_pair_t6.kicad_pcb
- /tmp/rip3 on SATA0_TX_P, USB2_MCU_P/N, USB2_SPARE_P/N: 0 fails but TX skew +7.9 mm (6/5 vias) — unacceptable for 6 Gb/s.

### 20:09 — SATA0_TX as coupled pair → work/bp_pair_tx1.kicad_pcb
- bp_pair generalised (PAIR=TX): J7-47/49 L1 stubs → via pair x=123.3 → L3 85R pair east under J7, 45° NE parallel to RX (3.4 mm apart) → north tail → vias (137.34/138.14,117.0) → L1 to J1 A74/A73.
- TX P/N 27.70/27.14 mm, 2/2 vias, 0 hard conflicts; 17 soft items ripped, re-routed; fail: 3V3_SB (2 comps, check pour).

### 20:13 — TX tune + USB2 attempts → CHECKPOINT work/bp_routed_a1c_sata.kicad_pcb
- bp_tune TUNE_RE=SATA0_TX: 5 bumps (a=0.135, L3) on TX_N → SATA0_TX 27.70/27.70 mm, skew 0.000, 2/2 vias.
- SATA0_RX 29.45/29.45, skew 0.000, 2/2 vias. All FP/FS HS pairs + REFCLK still 0.000 skew, 2/2 vias (bp_skew).
- USB2_MCU / USB2_SPARE: rip3 retries (t7, t8a, t8b) no better (net-by-net router can't couple them); a1c5 routes collide with the SATA L3 corridor. Kept tx1 routing: MCU 27.1/28.9 (4/6 vias), SPARE 77.2/61.8 (15/12 vias) — FLAG, follow-up (coupled re-route of USB2_SPARE to J6).
- Next: bp_post → backplane.kicad_pcb.

### 20:18 — first bp_post attempt (superseded)
- bp_post work/bp_routed_a1c_sata → backplane.kicad_pcb: DRC 134 errors/warnings + 26 unconnected (keepouts inside footprints ignored by bp_fix, NPTH clearance 0.15<0.2, U1-62 stub failed, 3V3_SB stitches unreachable).
- bp_fix.py patched (backup work/bp_fix.py.bak_a1c): footprint rule areas now obstacles, NPTH clearance NPTHC=0.22, PIXMF env, new mode drcfix (removes unlocked non-HS/SATA copper with DRC errors).
- Interrupted ~20:15 during clean loop on work/bp_post2. Resuming from work/bp_routed_a1c_sata.kicad_pcb.

### 20:25 — USB2_SPARE coupled pair → CHECKPOINT work/bp_routed_a1c_sata2.kicad_pcb
- bp_pair PAIR=USB2_SPARE (90R 0.24/0.15 L1/L4, 0.20/0.15 L3; goal-direction GDIR + tail fix): J1 B80/B79 locked escape vias → L3 → L4 (y114.2) → L3 (x150) → L1 → J6-14/13.
- Hand-cleaned N jog at J6 (bp_hand), bp_tune 1 bump L4. USB2_SPARE 57.06/57.06 mm, skew 0.000, 4/4 vias (bp_skew) — was 77.2/61.8, 15/12. KEPT.
- Victims re-routed: CB_THERMTRIP_N, FP_SMB_SDA OK; 3V3_SB still 2 comps (next step).

### 20:32 — finish + cleanup on a1c_sata2 → work/bp_fin3.kicad_pcb
- bp_finish + stitch → work/bp_fin.kicad_pcb (13 unconnected, 51 dangling tracks, 48 keepout, 27 hole-clr, 19 clr). (bp_post also run into backplane.kicad_pcb; superseded by this staged flow.)
- bp_clean.py: keeps vias that join ≥2 own-net track ends (backup work/bp_clean.py.bak_a1c). New tools/bp_clean2.py: in-process dangling-track removal (pcbnew connectivity) + dangling-via handling (bridge same-layer joins, drop unused escape stubs).
- bp_fix drcfix removed 91 violating items (17 nets). After cleaners: DRC 12 via_dangling, 2 clr, 2 starved, 1 hole_to_hole, 1 trk dangling; 39 unconnected → route next.

### 21:05 — re-route → work/bp_fin5.kicad_pcb
- First bp_fix route RIP=1 cascaded (37 nets left in queue, ripped SATA0_TX tune bumps) → discarded. bp_fix HS regex now also protects SATA0_* / USB2_SPARE_* (env HSX).
- RIP=0 PIXMF=0.9 route: 26/30 nets OK → work/bp_fin4. One rip pass each (tools/bp_rip1.py) on AUXS_EN_N, CB_I2C0_SDA, AUXP_EN_N, 3V3_SB: all OK (victims FS_HOLD, 3V3_M2, FP_HOLD, ILK_A, CB_FAN_PWM re-routed) → work/bp_fin5. 3V3_SB split fixed.

### 21:20 — bp_fin5 check → work/bp_fin6 (refilled)
- DRC on unrefilled routed boards hangs (>150 s: new copper over stale pours). New tools/bp_fill.py; refill first.
- bp_fin6 (= fin5 refilled): 119 keepout (router used centre-line keepout masks), 19 hole-clr, 10 clr, 14 trk + 3 via dangling, 2 starved, 1 hole_to_hole, 10 unconnected, parity 0.
- bp_fix: rule-area masks now dilated KOD=0.22 mm. work/scripts/fixpass.sh = drcfix → clean2 → route RIP=0 → clean2 → DRC. Running fin6 → fin7.

### 21:39 — fin7 → hand fixes → work/bp_fin8
- fin7 (fixpass): keepouts 0; left 29 hole-clr (NPTH pads were skipped by bp_fix: IsOnLayer true) , 8 clr, 8 via-dangling, 3 starved, 1 hole_to_hole, 8 unconnected.
- bp_fix: NPTH pads now always stamped (NPTHC). bp_clean2 refills before DRC.
- Hand (work/scripts/hand7.py): USB2_SPARE head at J1 vias re-drawn (P cleared N via), CB_THERMTRIP_N duplicate via merged, Y1-2/U5-7/U1-62 zone connection FULL.
- Next: fixpass fin8 → fin9.

### 21:44 — fin9 → hand fixes → work/bp_fin11
- fixpass fin8 → fin9: DRC 4 clr + 2 dangling warnings, 5 unconnected (4 GND L1 islands, AUXS_EN_N), parity 0.
- Hand (scripts/hand9.py, hand10.py): PSU_PWR_OK_M at U1-20 re-drawn (stub was 0.075 from pad 19; duplicate stubs removed), EN_5V jog at J2-8 straightened.
- New tools/bp_island.py: GND pour islands without a through-via get a GND via (6 added).
- ERC: 0 errors / 0 warnings.
- Next: fixpass fin11 → fin12.

### 21:49 — DRC 0 → CHECKPOINT backplane.kicad_pcb (= work/bp_fin17.kicad_pcb)
- fixpass fin11 → fin12: 1 GND L1 island (J7-51 lost its fan-out via to a 3V3_SB re-route) + 1 dangling.
- scripts/hand12.py: J7-51 GND via (123.75,133.55) + stub restored (locked), 3V3_SB re-routed RIP=0 → fin13. hand13/bp_hand: FP_MCIO_PRSNT_N route restored from fin12, dead-end stub trimmed, junction bridged → fin15. Dangling 3V3_SB via removed → fin16. bp_tune USB2_SPARE (4 bumps L3) → fin17.
- Note: DRC parity in work/ was a no-op (no matching .kicad_sch); verified in project folder.
- backplane.kicad_pcb: DRC 0 violations, 0 unconnected, 0 parity, 0 footprint errors (drc_report.txt). ERC 0 errors / 0 warnings (erc_report.txt). pro/dru restored from work/pro_backup.
- Pairs: SATA0_RX 29.45/29.45 (2/2 vias), SATA0_TX 27.70/27.70 (2/2), USB2_SPARE 57.04/57.04 (4/4), all FP/FS HS + REFCLK skew 0.000, 2/2.

### 21:50 — jlc_out + cost_update
- jlc_out: 4 layers, 16 gerber files, 44 BOM lines, 140 placed, 0 bottom → jlc/ (gerbers zip, BOM, CPL).
- cost spec: board row 152 footprints (140 placed, 9 DNP), 44 BOM lines; GPIO-remap note added. cost_update: BP q1 $285–450 → $145–230 (−$140–220), q5 $450–750 → $260–395 (−$190–355); duty −$49–77 / −$66–124; grand total q1 $5.6–12.8k → $5.5–12.6k, q5 $9.7–21.4k → $9.4–20.9k. Backup work/macpro62-cost-estimate.md.bak_a1.

### 21:51 — README + previews
- README: rev A1 section at top (stackup, DRC/ERC status, pair stats, flow tools incl. bp_pair/bp_hand/bp_clean2/bp_island, approval flags). Backup work/README.md.bak_a1.
- Previews: work/preview_A1_L1.png, work/preview_A1_L3.png (copies in docs/ so they ship in the zip).

### 21:52 — zips (DONE, nothing pushed)
- /workspace/kicad/macpro62-backplane.zip rebuilt: 145 files, top folder macpro62-backplane/, no work/ or __pycache__ (old copy in work/macpro62-backplane.zip.bak_pre_a1c).
- /workspace/macpro62-sync-icd.zip rebuilt: 182 entries kept, kicad/macpro62-backplane/* (145) + kicad/macpro62-backplane.zip replaced; 328 entries, testzip OK. backplane.kicad_pro / backplane_direct.kicad_pro in the zip are the box versions (overwrite the iMac rewrite in 49f3805). Old zip: work/macpro62-sync-icd.zip.bak_pre_a1c.
- Final re-check: DRC 0 / 0 unconnected / parity 0, ERC 0.
- Next: SM-1 (kicad/macpro62-storage-face, own progress file).

## USB2 touch-up (started 21:53, budget 25 min)
- Backup: work/bp_A1_final.kicad_pcb (= backplane.kicad_pcb, DRC 0).
- bp_tune patched (backup work/bp_tune.py.bak_usb): TUNE_VIA (via-aware skew like bp_skew), TUNE_PART (partial bumps per segment, loop TUNE_IT), TUNE_MINSEG.
- Tune FACEP/FACES/MCU → work/bp_u1, bp_u2: FACES −6.3 → 0.000; FACEP −17.9 → −6.5; MCU −5.0 → −2.7 (segments exhausted).
- USB2_FACEP_N ripped + RIP=0 re-route → FACEP 78.63/78.29, skew +0.34, 2/2 vias. MCU_N / MCU_P re-route tries: −6.7 (3/7) / −2.5 (5/5) → kept −2.7 (3/5). → work/bp_u3.
- 21:57 backplane.kicad_pcb = work/bp_u3: DRC 0 / 0 unconnected / parity 0. All 44 HS/SATA/SPARE pairs unchanged (0 skew). jlc_out re-run. README USB2 line updated.
