# macpro62-storage-face-2x (S2X rev A0): Face S module, 2 x M.2 2280, switchless
Replaces the parked 4-drive ASM2824 board (`../macpro62-storage-face`, SM-1) for the first build. Same outline, holes, J1 MCIO 124 at X 47.0 and bus-bar lugs.

- J1 x8 → x4 slot A (lanes 0-3, REFCLK0/PERST0#) + x4 slot B (lanes 4-7, REFCLK1/PERST1#). Slot B needs host changes: `docs/ICD_CHANGES.md`.
- M.2 M-key: LOTES APCI0107-P001A (LCSC C841661) + SMTSO2030CTJ standoffs (2280).
- Power: TPS259470 eFuse, INA238 (0x40), 2 x TPS54331 buck (3 A per slot), TMP1075 0x48/0x49, M24C64 0x50, activity LEDs D3/D4.
- 4L JLC04161H-7628, 85 Ω pairs; all parts on B (JLC Economic, single-sided).

Checks (2026-10-08): DRC 0 / unconnected 0 / schematic parity 0 (kicad-cli, all severities), ERC 0 (`erc_report.txt`).
Fab/assembly: `jlc/` (gerbers zip, BOM 36 lines, CPL 81 parts, all Bottom). Previews: `docs/preview_2X_*.png`. Log: `PROGRESS.md`.
Deviations D-2X-1 (hot spot), D-2X-2 (data-lane polarity inversion), D-S1 (no X-bracket): `docs/ICD_CHANGES.md`.

Rebuild: tools/model.py → build_pcb.py → route_hs.py → route_pwr.py → s2x_ls.py fan → Freerouting (10 min) → s2x_ls.py import →
s2x_clean.py (loop) → s2x_finish.py → tools/drc.sh; schematic: build_sch.py.
