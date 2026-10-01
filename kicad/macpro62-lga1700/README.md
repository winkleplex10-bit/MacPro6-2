# MacPro6,2 LGA1700 CPU board (CB) - rev A part-level floorplan fl1

Primary CPU board since 2026-10-01 (Aidan: skip COM-HPC; the carrier `/workspace/kicad/macpro62-cpu-carrier/` is the archived fallback).
Plan / feasibility study: `/workspace/macpro62-lga1700-board-plan.md`. Spec: `macpro62-architecture-spec-v0.2.md` §6.

Rebuild (KiCad 9, system python3 with pcbnew; needs openpyxl, ezdxf, shapely and the Intel ballout xlsx in
`/workspace/mp62-spec-refs/lga1700/`):

    python3 tools/make_placeholders.py
    rm -f macpro62_lga1700.kicad_pcb macpro62_lga1700.kicad_pro macpro62_lga1700.kicad_prl
    python3 tools/build_pcb.py          # writes fitcheck_floorplan.txt
    python3 tools/postprocess.py        # 10L stackup + net classes
    kicad-cli pcb drc --severity-all -o drc_report.txt macpro62_lga1700.kicad_pcb    # 0 violations
    sh tools/render.sh macpro62_lga1700.kicad_pcb floorplan                          # floorplan.png / floorplan_notes.png

Frame: x 0..156 right, y up from the board bottom (tab tip 1.722, shoulder 12.982, top 169.5); FRONT = socket/core side.

Contents (no nets, not routed):
- Edge.Cuts: stock riser outline (mirror-invariant above the shoulder, checked: 0.000 mm2) + Mini Cool Edge 224 tab (as the carrier).
- U1 LGA1700 land pattern: 1700 land positions from Intel 743844-001_S_LGA_Ballout.xlsx (public); pad 0.45 [Estimate];
  orientation assumes the Intel X/Y are a top view -> VERIFY. Land groups drawn on Dwgs.User (DDR top, PCIe bottom-right,
  DMI right, DDI bottom-left, VCCGT left, VCCCORE left/bottom of the cavity).
- U2 PCH: 1045 ball positions from Intel 743835_001_Ballout.xlsx (B760/H770/Z790 share it); pad 0.25 [Estimate].
- H1-H4 core holes D5 (69.5 x 55, fixed), H5-H8 contact-frame seat screws (own pattern), MP62 contact frame on Eco1.User.
- VRM: 7 x SiC654 (5x5) + 7 x Eaton FP4 (10.2 x 6.8 x 5.0) = 6 core + 1 GT phases, RT3628AE area; VCCIN_AUX, 1P05/1P8, PCH rails,
  VDD2, 5 V VIN_BULK areas.
- Back: 2 x DDR5 SO-DIMM (UMAX 90415-4015SR) in the stock DIMM strips, M.2 2280, J3 MCIO RA (IOB-HS incl. 2 x DDI), BT1, bulk 12 V.
- Keep-outs: D12 around H1-H4 (no tracks/vias), backplate zone on B (no footprints), tab y < 6 (no vias/pour).
