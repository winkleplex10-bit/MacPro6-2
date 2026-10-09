# SM-2X (2 x M.2, switchless) face board: work log (keep updated; runs get interrupted)
Brief: 2026-10-04 22:12, restarted 2026-10-08 17:03 ET (first run lost; only /workspace/scratch/sm2x_lib survived).
Rules: small checkpoints, log every step, never touch kicad/macpro62-storage-face (parked) or macpro62-lga1700, do NOT push.

## 17:04 ET: restart
- Created project dir (tools/, work/, docs/). Reusing scratch/sm2x_lib (LCSC C841661 LOTES APCI0107-P001A footprint + 3D via easyeda2kicad).

## 17:10 ET: research checkpoint (no board yet)
- M.2 socket: LOTES APCI0107-P001A (LCSC C841661, ext, H4.05, Economic OK). No M.2 socket is JLC basic/preferred.
  Footprint = EasyEDA/LCSC (easyeda2kicad), matches the LOTES drawing p4 (scratch/sm2x_lib/lotes_APCI0107.pdf, pulled from LCSC).
  Card extends toward footprint +y (even-pin row side, pegs at y=+1.5); card ref plane = pegs - 1.75 -> y=-0.25; 2280 screw at +79 from it (fp y=+78.75).
  Card bottom 2.92 mm above PCB (LOTES p3) -> standoff SMTSO2030CTJ (C2915627, M2 x 3.0 mm, EasyEDA fp).
- Host check (ICD rev 3 + CB plan + Intel ADL-S datasheet vol1 PCIe table): Face S today = CPU PEG60 x4 (cannot bifurcate). PEG x16 = 1x16 or 2x8 only
  (no x8+x4+x4 on 12th-14th gen). => x4 + x4 on Face S needs: slot A = PEG60 x4 (J1 lanes 0-3, as today), slot B = PEG port 011 (2x8 mode, trains x4)
  on J1 lanes 4-7, Face P drops to x8. Set B sideband (REFCLK1, PERST1#, CLKREQ1#, WAKE1#) on J1 already exists in the face pinout but BP rev A does not drive it.
- Decision: slot A <- J1 set A (REFCLK0/PERST0#/CLKREQ0#/WAKE0#), slot B <- J1 set B (REFCLK1/PERST1#/CLKREQ1#/WAKE1#). No clock buffer (no part, no ext fee);
  the host change that adds lanes 4-7 must add REFCLK1 + PERST1# anyway (ICD change list in docs/ at the end).
- Parts (JLC API via tools/jlcq.py): buck TPS54331DR C9865 (JLC basic/preferred class, 3 A, 3.5-28 V) x2 + SS34 C8678 (basic) + SWPA6045S4R7MT C78804 (ext, 4.7 uH 5.5 A).
  eFuse TPS259470ARPWR C3662799 (ext $1.28; -15 V reverse polarity + reverse blocking + EN + FLT) replaces LM74700+FET+TPS259824 (~$11).
  12 V monitor INA238AIDGSR C2868250 (spec 6.8: INA228 or INA238; INA228 C2887910 has 0 JLC stock). INA226 C49851 ($0.76) = cost option, needs approval.
  EEPROM M24C64-RMN6TP C79988 (preferred). TMP1075DGKR C2864807. MCIO J1 keeps the SFF-TA-1016 Annex A footprint (no EasyEDA fp for C4867471).
- No PCIe AC caps on the face: the M.2 SSD carries its own TX caps (M.2 spec); host TX caps are on the CB.
- 17:12 ET: box was reset (no KiCad, no Java). apt install kicad kicad-footprints openjdk-21-jre-headless librsvg2-bin started (log scratch/apt_kicad.log).

## 17:15 ET: tools back (KiCad 9.0.2, OpenJDK 21) + J1 geometry verified
- J1 pads (module frame, from SM-1 board, read-only): An at y 21.10, Bn at y 24.05; contact n<=37 at X = 28.1 + 0.6(n-1).
  Slot A = lanes 0-3 (X 28.7-38.3) + set A sideband (B8/B9/A11/B11/B12/A12, X 32.3-34.7);
  slot B = lanes 4-7 (X 39.5-49.1) + set B (B26/B27/A29/B29/B30/A30, X 43.1-45.5).
- Finding: B-side socket (odd row toward J1, card +Y) puts socket lanes in order L3..L0,REFCLK (X increasing) while J1 has L0,L1,CLK,L2,L3 -> lane order is
  reversed between the MCIO and M.2 pinouts. Without relying on PCIe lane reversal (optional in the base spec), a planar layer can keep only one
  module-TX pair + REFCLK in order. Plan: host-TX (row A) 2 vias/net (forced by the row-A escape anyway), reordered on L1 with a via column;
  REFCLK + one module-TX pair via-free on B; the other 3 module-TX pairs hop L1 (2 vias/net). Lower bound for this pinout, documented in docs/.

## 17:20 ET: plan fixed + library
- Pair routing plan (tools/order_solve.py, order_dag.py): Manhattan 2-via scheme. J1-side verticals (B for module-TX/REFCLK, L1 for host-TX after
  the row-A gap via), one L1 horizontal per pair, B verticals into the socket. Feasible only with both sockets right of their J1 groups:
  socket A X 46, socket B X 70 (cards X 35-57 / 59-81), socket origin Y 55 (card ref plane 54.75, 2280 standoff Y 133.75).
  Height order bottom->top: BH3 BH2 BH1 BH0 BM0 AH3 AM3 BM1 AH2 AM2 ACLK BM2 BM3 BCLK AH1 AH0 AM0 AM1 (H = host TX, M = module TX).
  Every PCIe/REFCLK net = exactly 2 vias. Data-lane P/N polarity follows the geometry (PCIe receivers must support lane polarity inversion);
  REFCLK polarity kept with a crossed via pair.
- Hot-spot centroid lands near X 58 / Y 75 (face spec R3 around (52, 69.5) is a [Proposal]) -> deviation D-2X-1 to document.
- MP62_S2X.pretty built by tools/make_lib.py (stock KiCad + SM-1 MCIO/hole/lug/GH + LCSC LOTES M.2, SMTSO2030CTJ, SWPA6045S, TI RPW).

## ~17:23 ET: placement + schematic checkpoint
- tools/model.py (89 parts, 83 nets) -> tools/build_pcb.py -> work/s2x_placed.kicad_pcb (orientation asserts OK: J1 A2 (28.7,21.1), sockets pin 1 at X-9.25,
  odd row toward J1, J_AUX opening -X). No courtyard overlaps (tools/cy_check.py).
- tools/make_pro.py: netclasses PCIE_85R 0.26/0.13, PWR_12V 0.8, PWR_3V3 0.8, PWR_AUX 0.3; JLC 4L rules (0.1 clr, via 0.45/0.25); .kicad_dru pour clearance 0.4 to 85R.
- tools/build_sch.py -> macpro62-storage-face-2x.kicad_sch: ERC 0 violations (first pass).

## 17:26 ET: HS pairs routed deterministically (tools/route_hs.py)
- Lane polarity inversion applied in model.py (socket PETp/n and PERp/n swapped per lane; REFCLK not swapped). PCIe receivers must support polarity inversion (Base spec §4.2.4). Documented as deviation D-2X-2.
- 18 pairs (8 lanes x 2 slots + 2 REFCLK): 17 L1 levels from Y 26.65 (pitch 1.25, +0.6 gap after BM0/BCLK where via corners clash), AM3 straight on B with 0 vias; every other net has exactly 2 vias.
- Skew by construction: data pairs 0.000 mm; REFCLK 1.400 mm on the crossed corner -> trimmed with bumps to -0.001 mm.
- Breakout: GND vias for J1 rows A/B and socket odd-row GND pins; PERST_A/B_HOST under the J1 body on B; CLKREQ_B/WAKE_B via L1 under J1 to X 70-71.
- PG logic moved to (15-23, 57) (was too close to the slot-A M0 vertical). PWR_12V clearance 0.12 (TPS259470 RPW pad gaps 0.15).
- DRC on work/s2x_hs.kicad_pcb: 0 clearance/crossing/hole errors; remaining = dangling (pending FR), silk (finish step), lib table (work dir only).

## 17:30 ET: fan-out + pre-FR pours + DSN (tools/s2x_ls.py fan)
- 101 GND fan-out vias (B pads, accurate pad polygons, >=0.9 mm via spacing per pad), 6 +12V_IN vias into the L1 +12V_IN pour; U2-7 skipped (B GND pour / pin 1-2 later).
- Pre-FR pours (B): PH_A, PH_B switch nodes; 3V3_A / 3V3_B from L to socket 3V3 pins (notched around TMP1075); L1 +12V_IN band Y 141.2-154 (lug to eFuse). Exported to DSN as planes.
- DSN patch: GND + 36 HS nets dropped -> keepouts; In1/In2 power (solid GND); 0.35 HS spacing keepouts; PWR classes 0.5 mm for routing.
- DRC on work/s2x_fan.kicad_pcb: 0 clearance / hole errors.
- Next: Freerouting under nohup (job_timeout 10 min), log work/fr_run.out.

## 18:08 ET: FR run 1 imported -> power redesign, FR run 2 started
- FR run 1 (18:04): SES imported (work/s2x_routed.kicad_pcb, now superseded). After refill: 3 x 0.12 clearance (+12V class) and 6 non-GND unconnected:
  +12V_IN / +12V_SW at U1 (FR "maze search could not be created" at the 0.45-pitch RPW pads), +12V_S trunk to both bucks unrouted, and the
  pre-FR B pours (3V3_A/B, PH_A) cut into islands by FR traces.
- Fix: tools/route_pwr.py = locked deterministic power skeleton with a shapely collision check (>= 0.15 to every other-net item):
  PH_A/B 1.2 mm; 3V3_A/B 1.8 mm trunks L -> 47 uF -> y 61 -> socket 3V3 pin combs (0.8); +12V_SW U1 OUT -> shunt 0.8; +12V_S shunt -> 22 uF ->
  2 vias -> L1 trunk 1.0 mm at y 138.5 down both board edges (x 3 / x 101) -> via -> Cin + VIN of each buck; INA238 VBUS/IN- sense 0.25 with one
  L1 hop; U1 IN -> 2 vias into the L1 +12V_IN pour; INA238 GND pin 7 stub + via.
- Shunt R5 rotated 180 in model.py (placement only, schematic unchanged) so its +12V_SW pad faces the eFuse.
- PWR_12V clearance 0.1 (make_pro.py). Pre-FR pours now only the L1 +12V_IN band.
- Rebuilt: build_pcb -> route_hs -> route_pwr (0 collisions) -> fan (GND 101 vias, 0 skipped) -> DSN; DRC on s2x_fan: 0 clearance errors.
- FR run 2 started 18:08 under nohup (job_timeout 10 min in /tmp/freerouting/freerouting.json).

## 18:10 ET: 3V3 moved to L3 islands, FR run 3 started
- Run-2 DSN check: the B-side 3V3 trunk at y 61 boxed in the even-row signal pins (DAS, PERST, CLKREQ, WAKE) and slot-A CLKREQ/WAKE had no path
  (FR "new connection could not be inserted"); stopped run 2 after 1 min.
- New 3V3 scheme: 3V3_A / 3V3_B = In2 (L3) islands X 1-57.6 / 58.4-103, Y 55-81 (HS copper ends at Y 51.3; L2 stays solid GND under everything).
  Buck L -> 47 uF bar (1.8 mm) with 2 vias; each socket 3V3 pin group -> 0.6 combs up under the socket body -> bar -> 0.6/0.3 via
  (F side of every 3V3 via is outside the die-pad mask opening). Cap 3V3 pads get island vias in the fan step (C26-1/C27-1 sit in the die-pad
  window -> routed on B). U1 IN/OUT stubs now start at the pad centres.
- route_pwr: 0 collisions; fan: GND 101, 3V3 10, +12V_IN 6 vias; DSN planes: +12V_IN (L1), 3V3_A/B (In2). DRC s2x_fan: 0 clearance errors.
- FR run 3 started under nohup (10 min).

## 18:15 ET: FR run 4 started
- Run 3 (killed once the unroutable set was clear): FR cannot reach a plane on a power layer ("layers are disabled") -> R14/R17 (PERST pull-ups),
  Q6/Q7 gates unrouted; WAKE_B pre-route stub boxed in under the slot-B socket-side vias.
- Fixes: R14/R17 -> 0.3 B traces + island vias in route_pwr; Q pads get island vias in the fan step; Q7 (PG, gate 3V3_B) moved to (85, 58.5)
  inside island B (PG_M becomes a long LS net; placement only); CLKREQ_B/WAKE_B pre-routes now leave the L1 hop at X 70-71 to the right on B
  (X 84/84.7) before turning up. No courtyard overlaps; route_pwr 0 collisions.

## 18:26 ET: step 1 done, FR run 4 imported
- FR run 4 18:15-18:25 (10 min job_timeout; FR ignores max_passes and keeps optimising until the timeout). SES written 18:23, 89 vias,
  FR clearance violations 0. FR's 3-4 "unrouted" counts were GND-only (GND is left to the finish-step pours/stitching).
- s2x_ls.py import -> work/s2x_routed.kicad_pcb; refilled; DRC: 0 clearance/short/hole errors; unconnected 150, all GND (no GND zones yet on the
  work board); non-GND unconnected 0. Dangling: 170 vias + 4 track stubs (PERST_A_HOST, CLKREQ_B, WAKE_B pre-route tails, one +12V_SW stub) -> cleanup.

## 18:27 ET: step 2 done, cleanup (work/s2x_clean.kicad_pcb)
- First cleanup pass deleted whole locked pre-route segments that FR had joined part-way (PERST_A_HOST tail at X 25, U2.10 stub) -> 2 non-GND
  unconnected. Fixed tools/s2x_clean.py: a dangling track touched part-way is TRIMMED back to the last junction; a non-GND via is kept only if it
  joins >= 2 copper layers (removes the now-unused CLKREQ_B/WAKE_B B-side hop vias); compared items by UUID (SWIG wrappers are not identical).
- Re-ran from s2x_routed: 2 trims + 6 removals over 3 passes, converged. No rip-up, no re-route, no single-net passes.
- DRC: 0 clearance/short; remaining = 150 unconnected + 170 dangling vias, ALL GND (finish step adds GND pours); 7 silk (finish step).
- HS protected: 36 HS nets identical to work/s2x_hs (508 items, 1652.849 mm, 68 vias).

## 18:28 ET: steps 3-4 done, finish + checks (macpro62-storage-face-2x.kicad_pcb)
- tools/s2x_finish.py: 85 NC nets (parity), values/LCSC synced, refs -> B.Fab, GND pours L1-L4 (L2/L3 solid connection; 3V3 islands L3 kept),
  904 thermal vias (1.5 mm grid: die-pad window on L1 151, gap-pad areas A 387 / B 366; thermal arrays may pierce the L3 3V3 islands, which
  refill around them; no L3 tracks), 821 stitching vias (3 mm), 243 footprint silk items removed, 21 footprints exported to MP62_S2X.pretty + relinked.
- Fix: FOOTPRINT.Flip() on a parentless copy segfaults in KiCad 9.0.2 -> flip with the board as parent, then detach.
- DRC (kicad-cli, --schematic-parity, all severities): 0 violations, 0 unconnected, 0 parity, 0 footprint errors.
- build_sch.py re-run (Q7 move is placement only); ERC 0 violations (erc_report.txt).

## 18:29 ET: step 5a, jlc_out + cost estimate
- jlc_out.py -> jlc/: 16 gerber/drill files (4 Cu), macpro62-storage-face-2x_gerbers.zip, BOM 36 lines, CPL 81 placed, 81 Bottom / 0 Top
  (Economic single-sided OK). Joints ~484 SMT. Unique extended (feeder fee): 9; preferred 6; J1 MCIO C4867471 has 0 LCSC stock (global source/consign).
- BOM priced via JLC parts API: $26.36/board at qty-1 prices (MCIO $9.58, INA238 $8.32 = 68 %).
- Cost md backed up to work/cost-estimate.before-2x.md; docs/cost_spec_2X.json -> cost_update.py: SM-1 group replaced by
  "Storage face board (S2X 2-drive switchless, Face S)": q1 $335-535 -> $118-200 (-$217-335), q5 $510-865 -> $215-345 (-$295-520);
  duty -$77-119 / -$105-186. Totals: before duty $4,100-9,900 / $7,200-16,700; grand $5,200-12,100 / $9,000-20,200 (was $5,500-12,600 / $9,400-20,900).
  §1 board row, §7 MCIO/INA228 rows, §8 SSD row, §5 ASM2824 row, §6 item 7 updated by hand; change log §6b added.

## 18:31 ET: step 5b, previews + docs + sync zip
- Previews (docs/): preview_2X_B.png (B copper + fab), preview_2X_L1.png, preview_2X_L2.png, preview_2X_L3.png (3V3 islands), preview_2X_HS.png (HS routing, from work/s2x_hs).
- README.md + docs/ICD_CHANGES.md (host changes, D-2X-1, D-2X-2 polarity inversion, D-S1, INA238/INA226, AC caps). ICD / CB / BP files NOT modified.
