> **Rev 2026-10-04 ≈ 10:40 ET (real DF40C-50DS receptacle, new HDMI lane map; not pushed):**
> - **JM1–JM11 = real Hirose DF40C-50DS-0.4V(51)** (684-4009-0 51, LCSC **C424646**, 4,973 in stock, $0.550 @1 / $0.389 @30 on 2026-10-04 09:44 ET) from the Hirose DF40 land drawing + JLCEDA/EasyEDA Official Library (https://lceda.cn/ , https://easyeda.com) data (`tools/easyeda/`): 50 × 0.20 copper 1.24 at ±1.27, solderable 0.70 at ±1.54 (inner part under resist), courtyard 12.9 × 4.4. Footprint `MP62_Hirose_DF40C-50DS-0.4V` (`tools/make_fps_modules.py`); the placeholder is deleted. Mates with the module DF40C-50DP-0.4V(51) C424645.
> - **Placement:** the modules' flaps grew for the real plug / 6.5 paddle (`modules_geom.py`), so JM1–JM10 moved ±0.04 (C) / ±0.24 (A) and JM11 +0.535 in X; their ESD arrays and U60 / U61 follow. Nothing else moved (42 of 165 footprints).
> - **HDMI lane map changed** (`../macpro62-io-modules/pmi50.py` ROLES["HDMI"]; PMI-50 table unchanged) for the real single-row HDMI land: JM11 pins 15/17 = TMDS_CK−/+, 21/23 = D0−/+, 27/29 = D1−/+, 33/35 = D2−/+, 16 = HDMI_SCL, 18 = HDMI_SDA, 22 = HDMI_HPD. The schematic re-wires itself from ROLES (checked on the netlist).
> - **Checks:** DRC 0 violations / 0 unconnected / 0 footprint errors; ERC 0. Floorplan + 3D renders regenerated. MCIO 124P/74P footprints untouched (byte-identical; `make_fps.py` not run).

> **Rev 2026-10-04 ≈ 09:40 ET (cost-review footprint fixes; not pushed):**
> - **USB2 hubs U32–U35: CH334R → CH334F.** CH334R is QSOP-16 (LCSC C4154405). The old QFN-24 4 × 4 placeholder was really the CH334F footprint.
>   - Swapped to **CH334F (C5187527, QFN-24 4 × 4 P0.5, EP 2.8)**. This keeps the 4 × 4 placements. U33 and U35 sit only 6 mm apart, too close for a 6.0-wide QSOP.
>   - Cost: LCSC ≈ $0.54 vs $0.46 at 10 pcs, so ≈ +$0.31 per board.
>   - Footprint `MP62_WCH_CH334F_QFN-24-1EP_4x4_P0.5_EP2.8`.
> - **U91 ASM1182e: QFN-64 9 × 9 placeholder → QFN-48 7 × 7 P0.5, EP 5.4** (ASMedia data and LCSC C2833072; LCSC stock 0 on 2026-10-04). Footprint `MP62_ASMedia_ASM1182e_QFN-48-1EP_7x7_P0.5_EP5.4`.
> - **Footprint source:** both land patterns come from the JLCEDA/EasyEDA Official Library (https://lceda.cn/ , https://easyeda.com).
>   - Converted by `tools/easyeda_fp.py` (re-centred, pin 1 top-left, EP paste 4 windows ≈ 60 %). The raw JSON is in `tools/easyeda/`.
>   - Written by `make_fps.py`. The stale placeholders were removed. `make_fps_risers.py` no longer writes the QFN-64.
> - **Symbols:** pins are still LOGICAL. Map them from the WCH and ASMedia datasheets before routing.
> - **Checks:** the board was rebuilt (`build_pcb.py` + `postprocess.py`). Only U32–U35 and U91 changed (same positions, rotations and sides).
>   - DRC 0 violations / 0 unconnected / 0 footprint errors. ERC 0.
>   - Floorplan and 3D renders were regenerated.
> - **Not taken:** `make_fps.py` copies the MCIO 124P/74P footprints from `../macpro62-storage-face`. That project changed them on 2026-10-04 08:46 ET (narrower courtyard, "NARROW plug option"). The pushed MP62_IO copies were restored and kept, so pick that change up deliberately.

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
