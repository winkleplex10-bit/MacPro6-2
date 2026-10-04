# MP62 Face S storage module SM-1 rev A0: KiCad 9 project

4 × M.2 2280 NVMe behind an ASMedia ASM2824 PCIe Gen3 switch, on the MP62-FACE v0.1 outline. The plan, BOM, cost and RAID analysis are in `/workspace/macpro62-storage-board-plan.md`. The spec is `macpro62-face-module-spec-v0.1.md` §11.3 (update 3).

**Status: FLOORPLAN, not routed.**
- PCB: outline, holes, stackup (JLC06161H-2116, 6 layers), rule areas (both-side bus-bar keep-outs, core tab, J_PCIE plug zone), and every IC, connector, socket, standoff, inductor and bulk capacitor placed. Only the lug nets are on the PCB.
- `kicad-cli pcb drc`: **0 violations, 0 unconnected, 0 footprint errors**.
- Schematic (`macpro62-storage-face.kicad_sch`, one flat A0 sheet, label connectivity, 154 symbols): `kicad-cli sch erc`: **0 errors, 0 warnings**.

## Frame
- Same as the template. Module frame origin at the outline's bottom-left, viewed from the **core side**. Spec (X, Y) → KiCad (60 + X, 190 − Y).
- **F = core side** (ASM2824 on the die pad, switch support parts ≤ 2 mm).
- **B = outer side** (J_PCIE, J_AUX, 4 × M.2, power band).

## PLACEHOLDERS (replace before routing)
| Footprint | Why |
|---|---|
| `MP62_M2_MKey_SMT_H4.2_PLACEHOLDER` | Generic 67-pad M-key pattern (0.5 mm per row, rows offset 0.25), hold-downs and pegs are guesses. Use the LOTES APCI0107-P001A (LCSC C841661) drawing. The card-edge datum (origin) and the 2280 outline on F.Fab are correct per the M.2 form factor |
| `MP62_BGA-492_21x21mm_Layout25x25_P0.8mm_PLACEHOLDER` | ASM2824 ball map under NDA; 0.8 mm pitch assumed |
| `MP62_TI_RNN0018A_VQFN-HR-18_3.5x3.5mm_PLACEHOLDER` | TPS56C215 HotRod pads; use TI RNN0018A |
| `MP62_M2_Standoff_SMT_M2_Pad5.0` | Round pad; height must match the socket's card-bottom height (≈ 3.5 mm for H4.2, verify) |

Symbols with **logical** pin numbering: ASM2824, TPS259824, TPS56C215, TLV62585. Real pinouts: M.2 M-key, MCIO 124 (from the spec CSV), GH15, BL24C64A, TMP1075, 74LVC2G07, SPI NOR, LM74700.

## Layers
- User.1: core contact zones.
- User.2: outer height-zone lines.
- User.3: connector band.
- **User.4: M.2 card outlines** (host parts under a card ≤ 1.6 mm).
- Dwgs.User: stock X-bracket (**not fitted**, deviation D-S1 / spec C-19).
- Cmts.User: notes.

## Rebuild
```
python3 tools/make_footprints.py        # template footprints (MP62_Face.pretty)
python3 tools/make_storage_fps.py       # MP62_Storage.pretty
python3 tools/build_storage.py          # PCB floorplan (KiCad 9 pcbnew python)
python3 tools/postprocess.py            # stackup + netclasses (PCIE_85R, REFCLK_85R, PWR_12V, PWR_3V3)
python3 tools/build_sch.py              # MP62_Storage.kicad_sym + schematic
kicad-cli pcb drc --severity-all -o drc_report.txt macpro62-storage-face.kicad_pcb
kicad-cli sch erc --severity-all -o erc_report.txt macpro62-storage-face.kicad_sch
/workspace/cadenv/bin/python tools/floorplan.py   # floorplan_storage_SM1.png
```

## ICD rev 2 (2026-10-02)
- **U13 INA228** (VSSOP-10, FACE_SMB 0x40, ALERT → FACE_SMB_ALERT#) + **R520** 2 mΩ 2512 between +12V_PROT and +12V_PROT_S (ahead of U2) + C520; B side at (51.5, 143) / (44, 143) / (51.5, 140.5). DRC 0/0, ERC 0, 157 schematic instances. Renders not refreshed.

## ICD rev 3 / O-10 (2026-10-04 ≈ 09:10 ET, Aidan approved)
- **J1 (J_PCIE, MCIO 124 RA) X 43.5 → 47.0** (+3.5 mm), narrow-plug courtyard (±21.6). Zero-jog landing at BP fp6 s = +5.0. Nearest B courtyard MH080 0.34 mm; M.2 card bottom Y 28.5 vs J1 body top Y 24.57 (3.9 mm). `tools/floorplan.py` reads J_PCIE X from `face_geom.json`.
- Nothing routed besides the lug nets, so no re-route. DRC 0/0/0, ERC 0/0 (schematic unchanged). `floorplan_storage_SM1.png`, `render_core_side_F.png`, `render_outer_side_B.png` regenerated (kicad-cli svg + rsvg-convert).

## Next steps
1. Get the ASM2824 datasheet and ball map, plus the LOTES drawing.
2. Replace the placeholders.
3. Update the PCB from the schematic and place the ≈ 120 small passives.
4. Route: PCIe Gen3, ≤ 2 vias per lane; 3V3_SSD on the L4 plane plus B-side pours; 12 V pours.
5. Run DRC and get a JLC quote.
