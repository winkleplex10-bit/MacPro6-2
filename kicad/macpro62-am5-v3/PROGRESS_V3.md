# AM5 CB v3 work log
Copy of kicad/macpro62-am5 (original untouched; checksums /workspace/scratch/v2_baseline/am5_original.sha256).
Goal: PROM21 free Gen4 x4 downstream port -> CPU-LINK ex-RSVD pins (slot B x2), slot A on CPU GPP x4 unchanged.

## 19:49 ET: v3 copy made from kicad/macpro62-am5

## 20:2x-20:45 ET: retargeted to Ryzen 7000/9000 (Raphael / Granite Ridge), slot B on CPU GPP#2 (CPU-LINK v3, 4 lanes)
- tools/build_sch.py / build_pcb.py: target text, lane blocks (GFX x16 live, GPP#1 -> FS 0-3, GPP#2 -> FS 4-7 + GPP_CLK_FSB -> FS_REFCLK1,
  PROM21 x4 chipset link, J8 M.2 boot -> PROM21 free Gen4 x4 via PCIE_PROM21_M2_X4 / PROM21_CLK_M2). Placeholder footprints unchanged.
- tools/make_pinouts_v3.py -> docs/cpulink_224_pinout_am5_v3.csv (21 contacts re-pinned per CPU-LINK v3; v1 CSVs untouched).
- Rebuilt (README sequence): DRC 0 violations / 0 unconnected / 0 footprint errors; ERC 0 (same as v1). floorplan.png + schematic_blockdiagram.pdf regenerated.
- docs/v3_lane_cpu_research.md: lanes, Phoenix vs Raphael, TDP/VRM/PSU budget, display plan, CPU prices.

## 21:15 ET: BP v3 went 6L / slot B x4 (Aidan 20:43)
- docs/cpulink_224_pinout_am5_v3.csv regenerated from the BP v3 draft CSV: RX7 polarity B54 = FS_PER7_N, B55 = FS_PER7_P (BP-side route choice; CPU-LINK v3 is a new pinout); lanes 6-7 no longer "NC on BP v3".
- CB board/schematic unaffected (J1 is block-level; the CSV is documentation). research doc lane table: slot B x4.
