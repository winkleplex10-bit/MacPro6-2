# MacPro6,2 AM5 CPU board (CB) - DRAFT rev A-am5, floorplan fp0 + block schematic bd0

**Separate sibling project** of `kicad/macpro62-lga1700` (2026-10-04, Aidan). The LGA1700 project is **not modified**;
its generator logic and placements were read and reused. Plan: `/workspace/macpro62-am5-board-plan.md`
(sync zip: `docs/macpro62-am5-board-plan.md`). Spec: `macpro62-architecture-spec-v0.2.md` changelog item 35.
Cost basis: `macpro62-cost-estimate.md` §10.

Target: **Ryzen 5 8600G / Ryzen 7 8700G (Phoenix)** at **cTDP 45 W** (Dasharo/openSIL boots only 8000G on AM5 today);
Ryzen 7000/9000 = later option (lanes 8-15 to Face P already routed). **PROM21** chipset (218-0891025 preferred),
**SVI3 3-rail VRM** (5 VDDCR + 2 VDDCR_SOC + 1 VDD_MISC), **4 x DDR5 UDIMM vertical, 2DPC**.

Rebuild (KiCad 9, system python3 with pcbnew; needs ezdxf + shapely + PIL; reads
`/workspace/bracket/cpu_board/cpu_board_outline_corrected.dxf`):

    python3 tools/make_pinouts.py       # docs/*_am5.csv + pinout_delta_summary.txt (reads the lga1700 CSVs read-only)
    python3 tools/make_placeholders.py  # MP62_AM5_Placeholders.pretty + docs/u1_am5_lands_PLACEHOLDER.csv
    rm -f macpro62_am5.kicad_pcb macpro62_am5.kicad_pro macpro62_am5.kicad_prl
    python3 tools/build_pcb.py          # writes fitcheck_floorplan.txt + placeholders_flagged.txt
    python3 tools/postprocess.py        # 10L stackup proposal + net classes
    kicad-cli pcb drc --severity-all -o drc_report.txt macpro62_am5.kicad_pcb    # 0 violations
    sh tools/render.sh macpro62_am5.kicad_pcb floorplan                          # floorplan.png / floorplan_notes.png
    python3 tools/build_sch.py          # block schematic (root + 10 stub sheets)
    kicad-cli sch erc --severity-all -o erc_report.txt macpro62_am5.kicad_sch    # 0 violations
    kicad-cli sch export pdf -o schematic_blockdiagram.pdf macpro62_am5.kicad_sch

Frame: x 0..156 right, y up from the board bottom (tab tip 1.722, shoulder 12.982, top 169.5); FRONT = socket/core side.
KiCad X = 60 + x, Y = 240 - y (identical to the LGA1700 CB).

## Reused unchanged from the LGA1700 CB (positions identical)
- Edge.Cuts (stock riser outline + Mini Cool Edge 224 tab), 1.6 mm, rules 0.09/0.09, via 0.25/0.15.
- H1-H4 core holes D5 at 69.5 x 55 (43.25/112.75, 46/101) + D12 boss keep-outs; H5-H8 frame seat screws (CX +-28, CY +-21).
- MP62 contact frame 71 x 54 + 4 ears (Eco1), steel backplate zone (B), pedestal (78.41, 73.25), black-plate 6.0 mm height zone.
- J1 CPU-LINK fingers, CAC1, J3 MCIO 124 RA (back, top), J8 M.2 2280 (back, bottom), 4 x DIMM (back, stock centrelines),
  LUG1/LUG2 + U11 eFuse + U15 INA228, GPU bus-bar pass-through keep-out, CB1/CB2, BT1 DNP, U14 DNP, EC/SPI/TPM/debug.

## New / changed for AM5
- **U1 Socket AM5 LGA1718 PLACEHOLDER**: 1718 SYNTHETIC lands on the sourced hex pitch 0.81 x 0.94 (Lotes brochure),
  package 40 x 40, housing 46 x 46 [Estimate], stock AM5 cooler 54 x 90 drawn on Dwgs only. **AMD land map = NDA -> do not fab.**
  Assumed land-group regions on Dwgs (DDR +y, PCIe -y) are [Inference].
- **U2 PROM21 PLACEHOLDER** FCBGA 19 x 19, 484 synthetic balls (ballout NDA), at the old PCH site (110, 133).
- VRM: 8 x SiC654 + 8 x FP4 (y 42-105), CIN1/COUT1 5 x 75, U3 SVI3 3-rail controller area (RAA229139 / MP2857) at (14, 117).
- Right column re-purposed: U4 CPU S5 rails, U5 sequencing/straps, U6 PROM21 rails, U7 5 V VIN_BULK, U8 VDDIO_MEM_S3.
- U16 VL822-Q7 USB 10G hub (90, 154), U17 PROM21 SPI (126, 150), Y1 48 MHz + 32 kHz.
- Pinouts: `docs/cpulink_224_pinout_am5.csv`, `docs/mp62-cb-j3_mcio124_host-end_am5.csv`, `docs/pinout_delta_summary.txt`
  (connector physicals + signal names unchanged -> BP / IOB need no change; delta vs ICD rev 3).

## Status
DRAFT floorplan: no nets, not routed. Every footprint carries an `MP62_STATUS` field; list in `placeholders_flagged.txt`
(PLACEHOLDER-NDA: U1, U2). Stackup is a proposal (placeholder dielectrics; take the JLC 10L table).
