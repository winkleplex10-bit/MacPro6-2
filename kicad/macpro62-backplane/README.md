# MacPro6,2 backplane (BP) - KiCad 9 project, rev A floorplan

Topology: **HUB** (Aidan, 2026-10-01). The CPU board plugs into J1 (Amphenol Mini Cool Edge 224, ME1022410103011, vertical SMT) and the BP routes PCIe x16 to J9 (MCIO 124, Face P) and x4 to J10 (MCIO 124, Face S).

**Floorplan rev A-fp3 (2026-10-01):** uses Aidan's measurements M1 (GPU-board bottom edges ~15 mm above the BP) and M2 (GPU-board planes ~55 mm from the centre). J9/J10 are now **right-angle** MCIO 124 placeholders (`MP62_MCIO_124P_RightAngle_SMT_PLACEHOLDER`, est. ~9-10 mm high; straight plugs are 15.90 mm and do not fit) with the cable exiting radially under each face edge. J1 sits at the **estimated stock riser-slot chord y = -12.6** (TBD, M2b). The M.2, power and harness connectors moved to the PSU side (-y). The previous fp2 (d = 30 assumed) is archived in `variants/hub_fp2_d30_assumed/`.
**fp3a (2026-10-01, CPU-carrier cross-check):** the J1 placeholder had contact A1 at +x with the A row toward +y, which no real Mini Cool Edge has (top view, A row up: A1 is at -x). The placeholder now uses the real contact offsets from the Amphenol card drawing (incl. key F), and **J1 is rotated 180 deg**: A1 stays at disc +x (bay -> face mapping unchanged), the **A row (host TX) faces the PSU side** and the B row (host RX) faces the core. Layer use swaps: host RX on L1, host TX via to L6. Mates `/workspace/kicad/macpro62-cpu-carrier/` J1 fingers. The pre-fix state is in `/workspace/scratch/bp_before_fp3a/`.

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
python3 tools/cpulink_pinout.py
python3 tools/build_sch.py
kicad-cli sch erc --severity-all -o erc_report.txt backplane.kicad_sch
```
