# Stock I/O plate (rear port cover): outer and inner scans

Inputs: `io_plate_outer_scan.jpeg` (outer face; the scan image is rotated 180°, so the "HDMI" label reads upside down) and `io_plate_inner_scan.jpeg` (inner face, with the illumination flex attached). Both are ≈ 100 dpi with rulers.
Run: `/workspace/cadenv/bin/python trace_io_plate.py`, then `finalize_io_plate.py`. Segmentation helper: `seg_plate.py`.

## Frame and registration
- **Frame:** the **I/O board back-view frame** of `../io_board/` (origin at the board's bottom-left, Y up toward the MEG-Array edge; front view X_f = 101 − X). The plate DXF therefore overlays `io_board_outline.dxf` and `io_board_ports.dxf` directly.
- **Outer → board:** the 14 port openings were matched to the traced board ports with a mirror plus rigid fit, **rms 1.0 mm**. The residuals of ≤ 1.2 mm are mostly the board's front-scan blur (±1).
- **Inner → outer:** 16 openings, mirror plus rigid fit, **rms 0.41 mm**.
- **Scale:** 3.9507 / 3.9348 px/mm, ±0.22 %.
- **Sizes:** opening sizes are the mean of the 70 and 90 thresholds, taken along the scan axes. They are good to ±0.3 mm (outer) and ±0.5 mm (inner, which reads ≈ 0.3–0.5 larger because of blur and the 4.5° scan tilt).

## Plate outline (outer face)
- **51.9 × 163.1 mm** at the 50 % edge (threshold 70). At threshold 90 it reads ≈ 2.5 mm wider, because the edge is soft (bevel?). Take **51.9 ± 1** and measure with calipers.
- **Corner radii ≈ R11.3–12.0.** The long edges are straight and parallel.
- **Position in the board frame:** X 27.2–79.2 (centre X ≈ 53.2), Y −4.5…158.6. That is centred on the two port columns (X 42.7 / 63.9, mid-line 53.3), not on the board centre (50.5). The plate long axis is tilted 0.9° against the board-port fit.

## Openings, outer face (board frame centre; W × H; stock board port; board − plate Δ)
| ID | Kind | Centre (X, Y) | W × H | Board port | Δ (board − plate) |
|---|---|---|---|---|---|
| AC | AC inlet | (52.08, 129.95) | 34.55 × 24.65 | power cutout (50.43, 131.06), 31.95 × 22.98 | (−1.65, +1.11) |
| POWER_BUTTON | round button cap | (63.02, 108.03) | Ø 12.4 | none on the board (button on its own part) | – |
| HDMI | HDMI | (41.92, 107.05) | 15.06 × 5.59 | HDMI | (+0.88, +0.75) |
| ETH_H1 / ETH_O1 | RJ45 | (42.20, 91.39) / (63.42, 91.74) | 12.91 × 10.55 / 13.04 × 10.67 | ETH_2 / ETH_1 | (+0.5, +1.2) / (+0.2, +1.2) |
| TB_H1–H3 | TB2 / mini-DP | X 42.5–42.9; Y 75.50 / 65.70 / 55.85 | 8.35–8.61 × 5.46–5.59 | TB_b1–b3 | ≤ 0.7 |
| TB_O1–O3 | TB2 / mini-DP | X 63.6–64.0; Y 75.89 / 66.00 / 56.21 | 8.48 × 5.46 | TB_a1–a3 | ≤ 1.2 (Y) |
| USB_H1 / H2 | USB-A | (43.07, 42.46) / (43.28, 32.41) | 13.54 / 13.42 × 5.85 | USB_b1 / b2 | ≤ 0.45 |
| USB_O1 / O2 | USB-A | (64.16, 42.84) / (64.38, 32.78) | 13.29 × 5.85 | USB_a1 / a2 | ≤ 0.6 |
| AUDIO_H / AUDIO_O | 3.5 mm jack | (43.41, 19.10) / (64.65, 19.42) | Ø 4.56 | not on the I/O board (jacks are on a flex, per iFixit) | – |

- **Pitches:**
  - Port columns 21.2 apart (X 42.7 / 63.9).
  - TB rows 9.8 apart.
  - USB rows 10.0 apart.
- **Printed/backlit icons:** the power and headphone icons sit under the audio jacks; there are also the Ethernet "<··>" icon between the RJ45s, the Thunderbolt bolt between the TB columns, the USB trident between the USB columns, and the "HDMI" text. The port groups have printed frames.
  - The **TB group's centre icon** sits at the board's TB centre-bracket screw (54.4, 57.5).

## Inner face (board frame)
- **Openings:** the same ports, 0.3–0.5 mm larger (blur). The AC inlet reads 35.7 × 26.2.
- **Light windows and small openings (backlit icons):**
  - HDMI label slot 6.8 × 1.3 at (46.2, 115.6).
  - Power-button LED/actuator window 3.0 × 2.3 at (62.4, 107.0).
  - Ethernet icon window 5.8 × 7.4 at (52.4, 92.9).
  - Gaps between TB rows at (44.3, 71.4) and (44.6, 61.7).
  - Slot between the USB rows, 10.9 × 3.0 at (40.8, 37.8).
- **Edge holes / clips** (Ø ≈ 2.3–3.8) at (31.0, 140.0), (28.2, 90.0), (29.6, 30.3) and (44.1, 2.7). Corner bosses or screw points are visible at about (29.1, 144.2), (26.8, 135.9), (31.8, 13.4) and (74.8, 12.5) (±1.5, not resolved).
  - A slot above the AC opening runs X ≈ 36.6–55.5 at Y ≈ 151.
  - The plate is a tray with a raised perimeter rim.
  - **What it mounts to:** probably the enclosure's I/O opening frame (scan 8, `../io_frame/`) via the edge clips and corner points [Inference].
- **Illumination flex** (port-illumination LEDs and motion/Hall sensor? [Inference]):
  - The rigid flex part spans **X 76.7–93.9, Y 31.9–68.3**, beside the "O" port column and partly **outside the plate outline** (it shows past the plate edge in the outer scan at Y 32–48).
  - It carries 3 ICs: ≈ 4 × 4 at (85.5, 62.5), and ≈ 5 × 5 at (87.1, 45.4) and (86.6, 36.5).
  - Its tail runs toward (116, 12), loose in the scan.

## Opening → new MP62 I/O port map [Proposal; fit checks are Estimates]
| Stock opening (count) | New port | Fit |
|---|---|---|
| USB-A (4) | **4 × USB-A** (USB 3.2 Gen 1/2) | 13.3–13.5 × 5.85 against the USB-A plug 12.0 × 4.5 (shell) and receptacle mouth 12.5 × 5.12: **fits**. Keep the receptacle positions within ±0.5 of the stock (X 43.3 / 64.2, Y 42.6 / 32.6). |
| TB2 (6) | **USB-C (DP alt-mode / USB4 where available)**, or mini-DP | 8.35–8.61 × 5.46–5.59 passes the USB-C plug shell (8.25 × 2.4). The receptacle shell (≈ 8.94 × 3.26) is wider than the slot, so it must sit **behind** the plate, with its mouth as close as possible to the outer face. **TO VERIFY:** plate thickness at the slots and USB-C plug-engagement margin (≈ 6.2–6.65 mm shell); a plate thicker than ≈ 1 mm may stop full mating. A mini-DP receptacle (the stock shape) fits natively. |
| RJ45 (2) | **1 × 2.5GbE** in one spot (the other spot: a second 2.5GbE/10GbE, or blanked) | 12.9–13.0 × 10.6 against the RJ45 plug 11.7 wide: **fits** a standard RJ45 jack placed at the stock position. |
| HDMI (1) | **HDMI** kept | 15.06 × 5.59: needs a stock-class HDMI receptacle (mouth 14.0 × 4.55 + shell) at the same position. |
| Audio (2) | **3.5 mm headphone + line-out (or combo)** | Ø 4.56 passes a 3.5 mm plug. The jack nose must sit behind the plate. |
| Power button (1) | **Power button** | Ø 12.4 cap. Reuse the stock button or a tactile switch with an actuator, plus a status LED behind the 3 × 2.3 window. |
| AC (1) | AC inlet (stock PSU) | 34.55 × 24.65; the board cutout is 31.95 × 22.98. |

## Checks against the I/O board trace (`../io_board/summary.md`)
- All 14 ports land within ≤ 1.2 mm. The plate is narrower (51.9 against the board's 101) and centred on the port columns.
- The board's latch slot (X 12.4–30.3), the coin cell (20.2, 136.1) and the unidentified square part (80.4, 141) all lie outside or at the edge of the plate.
- The board's power-plug cutout (X 34.46–66.41, Y 119.57–142.55) sits inside the plate AC opening (X 34.8–69.4, Y 117.6–142.3) to within the registration rms (1.0 mm). The margins are uneven (X 0.3 / 3.0) because of the fitted 1.7 mm offset, so check this on the hardware.

## Files
- `io_plate.json`
- `io_plate_board_frame.dxf` (layers PLATE_OUTLINE_OUTER, OPENINGS_OUTER, OPENINGS_INNER, ICON_WINDOWS, POWER_BUTTON, IO_BOARD_REF, NOTES)
- `io_plate_overlay_outer.png`, `io_plate_overlay_inner.png` (board ports in blue, plate openings in red)
- `work/` (masks, crops)
