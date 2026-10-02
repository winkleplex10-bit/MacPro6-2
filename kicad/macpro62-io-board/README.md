# MP62 I/O board (IOB) rev A0: KiCad 9 project

The plan, decisions and measurements are in `/workspace/macpro62-io-board-plan.md`. The plate CAD is in `/workspace/mechanical/io_plate_v2/`.

## Status

| Area | State |
|---|---|
| Floorplan | Outline 101.0 × 173.6, 6 stock holes, keep-outs and 6-layer stackup (JLC06161H-2116) |
| Placement | 117 footprints placed (2 × i226-V since 2026-10-02). All ICs, connectors, crystals, inductors and bulk caps are in; small passives are not. |
| Schematic | Flat sheet: 42 symbols, 410 instances, about 500 nets |
| Checks | DRC 0 / 0 / 0 (`drc_report.txt`, `--severity-all`) and ERC 0 / 0 (`erc_report.txt`) |
| Routing | **Not started.** The netlist has not been pushed to the PCB yet. |

**Placeholders.** Several footprints are KiCad-library stand-ins and must be replaced from the datasheets before routing:
- USB-C, USB-A, HDMI (RJ45 J25/J26 now use the HanRun HR913790A pattern from its drawing; verify the row offsets)
- J28 (FPC 50P), J3, J4
- J31 (Hirose FH12-14S stand-in for HX FPC 0.5-14P C7502869)
- QFN bodies for the PD, redriver, hub, PHY and TDP158 parts

**Unconfirmed pinouts.** The PSU (J3/J4), audio (J28) and I/O-wall flex (J31) pinouts are UNCONFIRMED. J31 uses a 0R matrix: P3 → PWRBTN_IN_N and P6 → GND are fitted; every other link is DNP.

## Rebuild

```
python3 tools/make_fps.py && python3 tools/build_pcb.py && python3 tools/postprocess.py
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
