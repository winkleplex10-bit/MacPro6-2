# Stock PSU board: calibrated scan trace

Inputs:
- `psu_board_solder_scan.jpeg`: solder side, sharp.
- `psu_board_component_scan.jpeg`: component side, defocused because of the tall parts.

Both are ≈ 100 dpi flatbed scans with rulers. Run, in order:
1. `trace_psu_board.py` (calibration and stage-1 rectification; its frame is superseded)
2. `trace_psu_board2.py` (registration hypotheses → `work/reg2.json`, `work/rect2_solder_compview.png`)
3. `finalize_psu.py` (outline, holes, lug pads → `psu_board.json`, DXF, overlay)

## Calibration and frame
- **Scale:** 3.9507 px/mm (X), 3.9348 px/mm (Y), ±0.22 %, from the ruler FFT.
- **Frame:** the CAD frame of `/workspace/macpro62-cad/psu_board_outline.dxf`, **viewed from the component side**. The solder scan is mirrored into it.
  - This assumes the CAD is drawn from the component side. If it is a solder-side drawing, x changes sign; the outline is symmetric to 0.4 mm, so geometry cannot decide.
- **Correction to stage 1:** the six screw holes alone fit the CAD equally well both ways round (rms 0.55 mm), because a 180° turn plus a 10.1 mm shift maps the pattern onto itself. The outline settles it: the tab widths and protrusions and the hole-to-edge distances (4/11 mm at one end, 17/20 at the other) only match the CAD end for end. **The lug-pad end is the CAD +y end** (top tab, holes at y 59). Stage 1's "bottom-tab = lug end" was wrong.

## Outline (scan vs CAD, ±0.5–1 mm; edge blur makes the scan read up to 1 mm small)
| Edge | Scan | CAD | Δ |
|---|---|---|---|
| Left / right | −51.00 / 50.50 | −51.50 / 51.456 | +0.50 / −0.96 |
| Main top L / R (lug end) | 76.00 / 75.62 | 75.966 | +0.03 / −0.34 |
| Top tab (y) / sides (x) | 78.62 / ±26.94 | 79.966 / −28.0…27.956 | −1.34 / ≈ +1.0 |
| Main bottom L / R | −73.00 / −73.25 | −72.55 / −72.952 | −0.45 / −0.30 |
| Bottom tab (y) / sides (x) | −80.12 / −38.69…37.62 | −79.05 / ±39.5 | −1.08 / +0.8 / −1.8 |
| **Width × height** | **101.5 × 158.75** (minAreaRect of the mask 102.4 × 157.9–159.2) | **102.96 × 159.02** | ≈ −1 / −0.3 |

- **Holes:** 6 screw heads (Ø ≈ 6.7–7.6, blurred), in the component-view CAD frame: (−47.82, −69.69), (47.44, −69.95), (−47.77, −5.19), (47.69, −4.93), (−47.40, 59.25), (47.73, 59.00). CAD is x ±48.0 / 47.956 at y −69.05…58.95; the spacing reads ≈ 0.5 mm small in X.
- The CAD outline overlays the scan within ≈ 1 mm everywhere (`psu_board_overlay_cad_frame.png`).

## 12 V output terminal pads ("lug pads"), at the +y (lug/tab) end
The pads are solder joints of large THT pins in **2 rows at y ≈ 70.9 and 65.4 (row pitch 5.5)**, in two groups:

| Group | Columns x (pins Ø 1.9–3.2) | Read as two terminals (2 × 2 pins each) | Terminal centres |
|---|---|---|---|
| Left | −47.0, −38.9, −34.0, −26.4 (+ extra joints at (−43.0, 67.3) and (−30.3, 66.8)) | (−47.0/−38.9) and (−34.0/−26.4) | **−42.95, −30.2** (12.75 apart) |
| Right | 27.96, 35.6, 40.6, 48.1 | (27.96/35.6) and (40.6/48.1) | **31.8, 44.35** (12.55 apart) |

- Group centres: **−36.6 and +38.1** (74.7 apart), centred on x ≈ +0.7.
- On the component side, the low-voltage electrolytics and the harness sit at this end, so it is the 12 V output end. The AC-input toroids are at the far (−y) end. The terminal bodies are too defocused to trace.
- **Against the CPU-board lugs** (`../cpu_board/summary.md`, back view, centre x = 78):
  - The CPU lugs sit at −50.2, −37.7 / +35.8, +47.5 from the board centre. That is two pairs **12.5 and 11.7 apart**, with pair centres −43.95 / +41.65 (85.6 apart).
  - The PSU terminals come in pairs 12.75 and 12.55 apart, so **the in-pair spacing matches (≈ 12.5)**. The pair centres do not: 74.7 apart against 85.6, i.e. ≈ 5.4 mm per side further in.
  - [Inference] Each PSU terminal pair (+12 V / GND) feeds one bus bar whose two lugs land 12.5 mm apart on a consumer board. The bus bars must jog ≈ 5 mm sideways (or be bent), so a PSU pair does not mate the CPU lugs directly. Which pair feeds which board is TO MEASURE.
  - If the CAD is a solder-side drawing, all x signs flip; the spacings stay the same.

## Harness (component scan, on the cable)
- **Wide connector:**
  - Body ≈ **22.6 × 7.4 mm**, at raw (510, 935).
  - **≈ 10 wires** enter it (9–12 resolved, defocused), at a wire pitch of **1.41 mm**. The body ribs repeat at **≈ 1.45–1.5 mm**.
  - Reading: **1.5 mm pitch class (Molex Pico-SPOX / JST ZH style), possibly 1.25 mm (PicoBlade / GH).** [Estimate; the blur is ±0.15 mm]
- **Small connector:** ≈ 8.4 × 7.3 mm including the wire entry, at raw (597, 895), with ≈ 3–4 wires. Pitch not resolvable.
- The harness leaves the board at the 12 V output end, ≈ x −10…−30 in this frame (±5).
- **Pin counts and pitch must be confirmed by eye or with calipers on the part.**

## Files
- `psu_board.json`
- `psu_board_cad_frame.dxf` (layers CAD_OUTLINE, SCAN_OUTLINE, HOLES, LUG_PADS, NOTES)
- `psu_board_overlay_cad_frame.png`
- `work/`: `rect2_solder_compview.png` (8 px/mm, X −62…62, Y −92…100), `reg2.json`, the lug crops `lugL.png` / `lugR.png`, `harness_zoom.png`, `comp_top.png` / `comp_bot.png`
