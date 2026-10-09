# MacPro6,2 backplane (BP) - KiCad 9 project, rev A1 (routed, 4 layers)

## Rev A1 (2026-10-04, routed on 4 layers)

- **Stackup:** 4L JLC04161H-7628, 1.6 mm, ENIG (was 6L JLC06161H-2116). L1 `L1_SIG_RX` (host RX, microstrip 85 Ω, 83.1 Ω calc), L2 `L2_GND`, L3 `L3_SIG_TX_PWR` (host TX stripline 86.4 Ω + `L3_3V3_SB` plane), L4 `L4_GND_BRK` (GND + low-speed breakout). Through vias 0.45 / 0.25 only. Impedance: `docs/impedance_A1.json`; loss budget: `docs/loss_budget_A1.md`. Gen5 redrivers removed (Gen4 loss 9.5–16.8 dB of 28 dB).
- **Status:** `backplane.kicad_pcb` **DRC 0 violations, 0 unconnected, 0 schematic-parity issues** (`drc_report.txt`); **ERC 0 errors / 0 warnings** (`erc_report.txt`). JLC outputs in `jlc/` (16 Gerber/drill files, 44 BOM lines, 140 placed parts, all on F; 152 footprints incl. 9 DNP).
- **High-speed pairs:** all 40 FP/FS PCIe pairs (x16 + x4, TX and RX) + FP/FS REFCLK: intra-pair skew 0.000 mm, 2 vias per net (J1 escape + one layer change). **SATA0_RX** (J7 41/43 → J1): coupled 85 Ω pair, L1 → L3, 29.45 / 29.45 mm, 2/2 vias. **SATA0_TX** (J7 47/49 → J1 A73/A74): coupled pair, L1 stubs → L3 → L1, 27.70 / 27.70 mm, 2/2 vias. **USB2_SPARE** (J1 B79/B80 → J6 13/14): coupled 90 Ω pair, 57.04 / 57.04 mm, 4/4 vias (was 15/12). USB2 (net-by-net routed, skew incl. 1.6 mm per via): USB2_FACEP 78.6/78.3 mm, skew 0.34 mm, 2/2 vias; USB2_FACES 118.0/114.8 mm, skew 0.00 (4/6 vias); USB2_MCU 28.7/28.3 mm, skew −2.7 mm (3/5 vias, could not reach ≤ 1.5 mm).
- **Flow (tools/):** `build_bp.py` → `bp_hs.py` (HS patterns) → `bp_tune.py` (skew → 0; `TUNE_RE`) → Freerouting (low-speed) → `bp_fix.py route` (grid A* clean-up; footprint/board keep-outs dilated `KOD`, NPTH clearance `NPTHC`, SATA/USB2_SPARE protected via `HSX`; `drcfix` mode removes DRC-violating copper) → `bp_pair.py` (coupled-pair centre-line A* router, `PAIR=RX|TX|USB2_SPARE`) and `bp_hand.py` (hand-route spec with clearance check) → `bp_post.sh` / `bp_finish.py` (pours, GND fan-out, DRC) → `bp_clean2.py` (in-process dangling clean-up, refills first) / `bp_island.py` (GND island stitch vias) / `bp_fill.py` → `jlc_out.py`. Skew report `bp_skew.py`, zone report `bp_zreport.py`. Step log: `PROGRESS_A1.md`.
- **Needs Aidan's approval before ordering:** ICD 3.1 FS-lane reversal; INA226 replacing INA228; J7 M.2 DNP (and so the BIOS/OpenCore boot location); R27 → R33; RP2350B GPIO re-assignment (**firmware pin-map update needed**, `tools/gpio_map.json`); the U1 / Y1 / U2 moves.
- Cost: `/workspace/macpro62-cost-estimate.md` §6a (BP q1 $285–450 → $145–230, q5 $450–750 → $260–395).
- Previews: `docs/preview_A1_L1.png` (L1), `docs/preview_A1_L3.png` (L3) (also in `work/`).

## History (floorplan revisions)


Topology: **HUB** (Aidan, 2026-10-01). The CPU board plugs into J1 (Amphenol Mini Cool Edge 224, ME1022410103011, vertical SMT) and the BP routes PCIe x16 to J9 (MCIO 124, Face P) and x4 to J10 (MCIO 124, Face S).

**Floorplan rev A-fp3 (2026-10-01):** uses Aidan's measurements M1 (GPU-board bottom edges ~15 mm above the BP) and M2 (GPU-board planes ~55 mm from the centre). J9/J10 are now **right-angle** MCIO 124 placeholders (`MP62_MCIO_124P_RightAngle_SMT_PLACEHOLDER`, est. ~9-10 mm high; straight plugs are 15.90 mm and do not fit) with the cable exiting radially under each face edge. J1 sits at the **estimated stock riser-slot chord y = -12.6** (TBD, M2b). The M.2, power and harness connectors moved to the PSU side (-y). The previous fp2 (d = 30 assumed) is archived in `variants/hub_fp2_d30_assumed/`.
**fp3a (2026-10-01, CPU-carrier cross-check):** the J1 placeholder had contact A1 at +x with the A row toward +y, which no real Mini Cool Edge has (top view, A row up: A1 is at -x). The placeholder now uses the real contact offsets from the Amphenol card drawing (incl. key F), and **J1 is rotated 180 deg**: A1 stays at disc +x (bay -> face mapping unchanged), the **A row (host TX) faces the PSU side** and the B row (host RX) faces the core. Layer use swaps: host RX on L1, host TX via to L6. Mates `/workspace/kicad/macpro62-cpu-carrier/` J1 fingers. The pre-fix state is in `/workspace/scratch/bp_before_fp3a/`.

**fp6 (2026-10-04 ≈ 09:10 ET, ICD rev 3, O-10 approved by Aidan):** zero-jog straight-straight MCIO cable with **narrow plugs**.
- `tools/hub_floorplan.py`: **J9 r_c 31.2 → 33.0, s −5.2 → +5.0** (origin (20.62, 13.27) → (14.68, 21.75), ≈ 10.4 mm); **J10 r_c 31.5 → 29.5, s −2.0 → +5.0** (origin (−15.74, 18.57) → (−19.28, 12.20), ≈ 7.3 mm). s = +5.0 = module J_PCIE X 47.0 (face spec update 6), so neither cable jogs. Narrow-plug courtyard (±21.6, `make_footprints.py` in the face template): J9–J10 gap 4.28 mm, **J1–J10 2.33 mm**, J1–J9 11.88 mm.
- **J3 (Face P AUX) (0, 51.4) rot 0 → (42.5, 13.5) rot 45** (≈ 55 mm; beyond J9's outer end, Face-P s ≈ −20.5) and **J4 (Face S AUX) (−38.0, 2.5) rot 135 → (−2.5, 43.5) rot 45** (≈ 54 mm; apex wedge, Face-S s ≈ −28.6). A full free-space search found no other GH15 site; each AUX cable runs along its own face's bottom edge above the MCIO ribbon (≈ 56 mm lateral Face P, ≈ 64 mm Face S; lengths M9).
- **U3 (0, 41.6) → (−7.5, 49.0)** (≈ 10.5 mm). Redriver row **U10–U14 +2.5 mm in x** (U14 (−19.35, −3.5) → (−16.85, −3.5), 0.51 mm to J10).
- New F.Cu rule areas `MCIO_RIBBON_J9` / `MCIO_RIBBON_J10` (no footprints/pads) from the courtyard outer edge to n 63, s ± 21.6.
- Not routed (placeholders only), so nothing to re-route. Fit check ALL OK (27 parts), **DRC 0 violations / 0 unconnected**. System fit check `tools/fitcheck_o10.py` → `fitcheck_mcio_o10.txt` (ALL OK; notes: bend beyond the BP rim r ≤ 65.8 → base ring M1b; S5 under the J9 ribbon, CR-BP-1). Previous fp5 board/scripts: `/workspace/scratch/o10/`.

**fp5 (2026-10-02 ≈ 13:15 ET, ICD rev 2, Aidan: face normals ≈ 45° / 135°):**
- `tools/hub_floorplan.py` (`FACE_P_ANG` / `FACE_S_ANG`): J9 at r_c 31.2, s −5.2, rot −45°; J10 at r_c 31.5, s −2.0, rot +45° (apex gap 1.3 mm). At 90° between faces both receptacles cannot sit at s = +8.5 (they collide at the apex; J10 is bounded by the G1 keep-out), so **CR-2 is closed by a flat-twinax jog cable** (jogs 13.7 / 10.5 mm, face spec §3.6, feasibility ICD O-6).
- J3 (0, 51.4) apex wedge; J4 (−38.0, 2.5) rot 135° beyond J10's lower-left end (6.3 mm from G1). Redrivers U10–U14, U1 (0, 15.3), U2 (−9, 6), Y1 (−2.6, 6), U3 (0, 41.6) re-packed in the V; SW1 (30.5, −34) and J8 (−40, −34) moved to the PSU side.
- `build_pcb.py` chords at 45° / 135°; drawings (corridors, plane triangle incentre (0, 24.8), lane estimate Face P 39–65 mm / Face S 40–43 mm) updated.
- CPU-LINK **A105 = PWR_ALERT#** (was RSVD_LS1; CB INA228 + eFuse FLT#, BP 10k pull-up); schematic stubs `MOD_PWR_ALERT_N`, `PWR_ALERT_BP_N`, BP INA228 0x40 note, LPT + EMC2101 reload text on the MCU sheet.
- Fit check ALL OK (27 parts, max r 57.8), DRC 0/0, ERC 0.

**fp4 (2026-10-02, interface audit, `/workspace/macpro62-interface-control.md`):**
- **CR-BP-1 applied:** the six small stock holes S1-S6 (base-board scan, `bracket/base_board/`) get D6 rule-area keep-outs (`CR-BP-1_KO_S1..S6`, all copper layers, no footprints/tracks/vias/pours) and are part of the fit check (courtyard >= 3.0 mm from each S centre). **U4** moved from (-27, -46.5) (S2 inside its courtyard) to (-30, -38). **J6** moved to x 11.4 (S3), **J3** to the apex V at (0, 51) rot 0 and **J4** parallel to the J10 inner side at (-15.9, 14.95) rot 60 (S4/S5 and the new J9 position); **J8** SWD to (0, 44.6), **U3** to (0, 39.8), **Y1** to (-6.4, 14.0).
- **J3/J4 are GH 15P** (`JST_GH_BM15B-GHS-TBT`, face spec C-4: pin 15 MOD_LED#, pins 13/14 USB2 primary); pinout 1:1 with `macpro62-face/pinouts/mp62-face-v0.1_aux_gh15.csv`.
- **J9/J10 use the SFF-TA-1016 RA footprint** `MP62_MCIO_124P_RA_SFF-TA-1016` (copied from the face template by `make_placeholders.py`). CR-2 (s = +8.5 on both faces) is **only partly possible**: J9 at s = +8.0 / r_c 36.5 (0.5 mm short, S5 keep-out); J10 at s > -4.6 enters the G1 gold-hole keep-out (6 mm), so it stays at s = -5.0 / r_c 37.2 and the **Face S cable needs a 13.5 mm lateral jog** (open decision, ICD O-1).
- **J5 (fan GH4) removed:** the fan is driven by the IOB EMC2101 (0x4C, I2C_SYS) on IOB CONN_C; the BP MCU writes the CB fan demand (CPU-LINK FAN_PWMOUT) to it. `fan.kicad_sch` deleted.
- **Schematic stubs** gained IOB-LINK `IOB_INT_N`, `IOB_PRSNT_N`, `IOB_USB_DP/DN` (CPU-LINK USB2_SPARE), face `MOD_LED_N`, CPU-LINK `MOD_I2C0` (CB ID EEPROM 0x57); each stub sheet now holds one non-BOM `#BLKn` symbol (passive pins, `MP62_BP_Stubs.kicad_sym`) so **ERC is 0 violations**.
- `docs/cpulink_224_pinout_draft.csv` has a **CB mapping column** (LGA1700/Z790 PCH + RP2350 EC net, direction seen from the CB).

Spec: `/workspace/macpro62-architecture-spec-v0.2.md` (sections 3 and 4.9). Interfaces: `/workspace/macpro62-interface-control.md`.

| File | What |
|---|---|
| `backplane.kicad_pcb` / `.kicad_pro` | HUB floorplan, 6 layers, JLC06161H-2116 stackup, placeholders only (not routed) |
| `floorplan.png` / `.svg` | Render of the hub floorplan |
| `drc_report.txt` | `kicad-cli pcb drc --severity-all`: 0 violations, 0 unconnected |
| `fitcheck_floorplan.txt` | r_max <= 58 mm, gold-hole distance >= 6 mm and S1-S6 distance >= 3 mm per footprint |
| `fitcheck_mcio_o10.txt` | O-10 system fit check (`tools/fitcheck_o10.py`, system python3): zero jog, J1 clearance, ribbon corridors, cable lengths, face envelope, SM-1 |
| `lane_length_estimate.txt` | Estimated BP PCIe lane lengths (J1 -> MCIO) |
| `docs/cpulink_224_pinout_draft.csv` | CPU-LINK 224 pin list draft with the CB mapping (from `tools/cpulink_pinout.py`) |
| `backplane_direct.kicad_pcb` | Saved DIRECT variant (4L JLC04161H-7628, no PCIe on BP) |
| `variants/` | Direct fit check, DRC and render; archived all-MCIO hub fit check; `hub_fp2_d30_assumed/` (previous hub floorplan) |
| `backplane.kicad_sch` + sheets | Block-diagram stubs (hierarchical labels + non-BOM stub symbols); `erc_report.txt`: 0 violations |
| `MP62_Placeholders.pretty/` | Placeholder footprints (outer dimensions from vendor drawings) + the SFF-TA-1016 MCIO RA footprint |
| `MP62_BP_Stubs.kicad_sym`, `sym-lib-table` | Stub symbols written by `tools/build_sch.py` |

Rebuild (from this folder):

```
python3 tools/make_placeholders.py
rm -f backplane.kicad_pcb backplane.kicad_pro backplane.kicad_prl
python3 tools/build_pcb.py          # VARIANT=direct for backplane_direct.kicad_pcb
python3 tools/postprocess.py        # VARIANT=direct for the 4L stackup
kicad-cli pcb drc --severity-all -o drc_report.txt backplane.kicad_pcb
tools/render.sh backplane.kicad_pcb floorplan
python3 tools/fitcheck_o10.py       # needs ../macpro62-face-template and ../macpro62-storage-face
python3 tools/cpulink_pinout.py
python3 tools/build_sch.py
kicad-cli sch erc --severity-all -o erc_report.txt backplane.kicad_sch
```
