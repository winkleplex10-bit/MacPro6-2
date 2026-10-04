> **Rev 2026-10-02 ≈ 14:55 ET (plate corrections):**
> - **HDMI / button back to stock.** The flex trace and cover-scan frame were mirrored, so these moved:
>   - JM11 HDMI → (66.65, 107.07), rot 0, O side.
>   - SW1/D20 → X 43.02; J30 → (50.32, 104.5).
>   - U60/U61 next to JM11 (B); U80 → (28.5, 108.5) B.
>   - U30/U31 → X 34.8; HDMI pegs → (70.82, 111.9) / (55.62, 106.0).
>   - J31 → (24.0, 10.0); J9 → (24.0, 16.0).
>   - RJ45 ETH1 (63.664, 91.407) / ETH2 (43.145, 91.595), with T1/T2.
> - **`io_geom.json`:** openings_outer is mirrored; the originals are in `openings_outer_asscanned`.
> - **Checks:** DRC 0 / 0 unconnected; ERC 0 / 0.
> - **Renders:** floorplan, renders and schematic PNG regenerated (`/workspace/cadenv/bin/python tools/floorplan.py`, since system python has no matplotlib).

# MP62 I/O board (IOB) rev A0: KiCad 9 project

The plan, decisions and measurements are in `/workspace/macpro62-io-board-plan.md`. The plate CAD is in `/workspace/mechanical/io_plate_v2/`.

> **Rev 2026-10-02 ≈ 12:45 ET (D-IO16):** the USB-C / USB-A / HDMI receptacles and the riser connectors are gone from this board. The ports are **swappable flex port modules** (`/workspace/kicad/macpro62-io-modules/`, plan §4.7.9) that plug into **JM1–JM11** (DF40C-50DS, PMI-50 pinout) on F.
> - Mechanical parts: clamp-plate M2 SMT standoffs H21–H25 and cradle pegs H40–H45 (NPTH Ø1.6).
> - Module ID and presence: U95 / U96 TCA9548A (0x70 / 0x71) for the module ID EEPROMs, and U97 TCA9555 (0x27, on U96 ch3) for PRSNT#, INT# → PD_INT_N. All are on B.
> - Geometry: `tools/modules_geom.py` (reads the plate features JSON). Footprints: `tools/make_fps_modules.py`. `risers_geom.py` / `make_fps_risers.py` are superseded.
> - Checks: DRC 0 / 0 / 0, ERC 0 / 0.

## Status

| Area | State |
|---|---|
| Floorplan | Outline 101.0 × 173.6, 6 stock holes, keep-outs and 6-layer stackup (JLC06161H-2116) |
| Placement | 136 footprints placed (D-IO16: JM1–JM11, H21–H25, H40–H45, U95–U97) (2 × i226-V since 2026-10-02). All ICs, connectors, crystals, inductors and bulk caps are in; small passives are not. |
| Schematic | Flat sheet: 51 symbols, 478 instances, 586 nets |
| Checks | DRC 0 / 0 / 0 (`drc_report.txt`, `--severity-all`) and ERC 0 / 0 (`erc_report.txt`) |
| Routing | **Not started.** The netlist has not been pushed to the PCB yet. |

**Placeholders.** Several footprints are KiCad-library stand-ins and must be replaced from the datasheets before routing:
- JM1–JM11 DF40C-50DS and the M2 SMT standoffs (module receptacles and their land patterns are in the modules project); RJ45 J25/J26 now use the HanRun HR913790A pattern from its drawing; verify the row offsets)
- J28 (FPC 50P), J3, J4
- J31 (Hirose FH12-14S stand-in for HX FPC 0.5-14P C7502869)
- QFN bodies for the PD, redriver, hub, PHY and TDP158 parts

**Unconfirmed pinouts.** The PSU (J3/J4), audio (J28) and I/O-wall flex (J31) pinouts are UNCONFIRMED. J31 uses a 0R matrix: P3 → PWRBTN_IN_N and P6 → GND are fitted; every other link is DNP.

## Rebuild

```
python3 tools/modules_geom.py && python3 tools/make_fps.py && python3 tools/make_fps_modules.py && python3 tools/build_pcb.py && python3 tools/postprocess.py
kicad-cli pcb drc --severity-all -o drc_report.txt macpro62-io-board.kicad_pcb
python3 tools/build_sch.py && kicad-cli sch erc -o erc_report.txt macpro62-io-board.kicad_sch
/workspace/cadenv/bin/python tools/floorplan.py
```

## Files

| Path | Content |
|---|---|
| `tools/io_geom.json` | Measured stock geometry (back-view frame) |
| `tools/placement.json` | Placement table with courtyard boxes |
| `MP62_IO.pretty/` | Project footprints |
| `MP62_IO.kicad_sym` | Generated symbol library |
| `docs/mp62-iob-hs1_mcio124_pinout_v0.2.csv` | IOB-HS1 contact map |
| `docs/sch_netlist_summary.txt` | Net-to-pin summary |
| `render_port_side_F.png`, `render_psu_side_B.png`, `floorplan_iob_A0.png`, `schematic_overview.png` | Renders |
