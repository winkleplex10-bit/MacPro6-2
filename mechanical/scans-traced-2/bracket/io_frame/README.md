# io_frame: scan 8 (I/O plate carrier / trim frame)

The source is scan 8 (`io_frame_scan.jpeg`, ≈100 dpi, SX 3.951 / SY 3.935 px/mm, ±0.2 %).

## What it is
- It is a rounded frame the **same size as the I/O plate**: 51.7 × 164.0, R 11.8, against the plate's 51.9 × 163.1, R 11.3–12.
- Its openings form **the same port grid as the plate**.
- **Registration** is mirrored (the scan sees the inner face) plus a rigid fit of 7 opening centres to `io_plate.json`: TB columns, one USB pair, audio ×2, HDMI, ETH. rms **0.22 mm**, rotation 0.05°.
  - The HDMI-sized slot and the ETH slot only line up mirrored, which settles the side.
- **Reading:** the plate-side frame that the I/O plate clips into and that sits behind the plate in front of the I/O board (port bezel / carrier).
- The long dark rails on both sides and the ridged object on the right are **out of focus** (behind the frame). They are not part of it. The rails are traced as lines for reference only.

## Frame and files
- **Coordinates:** I/O board back-view frame, the same as `io_plate.json` and `bracket/io_board`, mm.
- `io_frame.json`: all numbers, the transform, and the plate-vs-frame margins.
- `io_frame_board_frame.dxf`. Layers:
  - OUTLINE
  - OPENINGS: traced contours (polyline, 0.35 mm simplification) plus the 2 round audio holes
  - HOLES
  - RAILS
  - PLATE_OPENINGS_REF: the io_plate openings, for comparison
  - NOTES
- `io_frame_overlay.png`: red = frame openings, green = registered plate openings, magenta = outline fit, blue = rails.
- Scripts: `outline8.py` (rounded-rect fit to the dark edge line, residual sd 0.17 mm), `finalize_frame8.py`.

## Dimensions (±0.5 unless noted)
- **Outline:** 51.66 × 164.02, corner R 11.83.
  - Centre (52.94, 76.34). Tilted 1.3° in the board frame, the same as the plate.
  - X 25.8…79.8, Y −6.4…158.5.
  - The plate is X 27.2…79.2, Y −4.5…158.6. The frame reaches about 2 mm lower than the plate at the bottom, which is within the plate's threshold uncertainty.
- **Openings:** centre, then W × H measured along the frame axes.

  | opening | centre | W × H | holds (plate opening) | min margin to plate opening |
  |---|---|---|---|---|
  | BIG_L (top, L-shaped) | (55.46, 120.19) | 37.6 × 58.7 overall | AC (top part X 33.1…70.3, Y 115.5…144.0) + power button + ETH_O1 (leg X 54.2…71.0, Y 85.3…115.5) | AC ≈0 (flush; rounded corners), button 1.65, ETH 0.59 |
  | SMALL_R1 | (41.93, 107.11) | 18.3 × 9.0 | HDMI | 1.17 |
  | SMALL_R2 | (42.41, 91.50) | 15.6 × 13.0 | ETH_H1 | 0.65 |
  | TALL_R | (42.56, 65.72) | 12.4 × 30.2 | TB_H1–3 | 1.46 |
  | TALL_L | (63.70, 66.20) | 12.2 × 30.2 | TB_O1–3 | 1.24 |
  | SQ_R | (43.06, 37.36) | 17.6 × 20.0 | USB_H1–2 | 1.59 |
  | SQ_L | (67.05, 37.99) | 22.7 × 20.1 (asymmetric, extends ≈2.3 mm further outward) | USB_O1–2 | 1.48 |
  | ROUND_R | (43.74, 18.88) | Ø6.36 | AUDIO_H | 0.41 |
  | ROUND_L | (64.48, 19.34) | Ø6.40 | AUDIO_O | 0.61 |
  | BOTTOM | (54.32, 3.24) | 46.9 × 10.4 | no plate port; lines up with the plate's bottom inner clip (44.1, 2.7) | – |

- **Holes:**
  - Corner holes Ø3.2–3.5 at (73.39, 149.63), (29.20, 148.43), (76.55, 14.22), (32.36, 13.08). Pattern ≈44.2 × 135.3, likely the frame's fixing screws.
  - Centre holes between the TB columns: Ø3.2 at (52.93, 75.41) and Ø4.8 at (53.38, 58.38).
  - A dark ring with a bright centre between the audio holes at ≈(53.0, 19.0), Ø≈3, possibly a pin or LED; manual ±0.5.
- **Rails** (behind, defocused, ±1): straight lines at X 22.2 and X 84.1, Y −6.7…159.2. They sit about 3.6 / 4.3 outside the frame edges.

## Design consequences for the new I/O board ports
- Every stock plate opening has **0.4–1.7 mm of clearance** inside the frame openings, except AC, which is flush.
- Any new connector whose body passes through the frame (not just the plate) must fit inside these frame openings. The binding ones are:
  - **TB column → USB-C:** a USB-C receptacle shell (≈8.9 × 3.2) fits the 12.2–12.4 × 30.2 slot, with 3 per column at the stock 9.8 pitch.
  - **ETH:** the slot is 15.6 × 13.0 (H side). A 2.5GbE RJ45 (≈15.9 wide at the shell) is **tight**: about 0.3 mm short on the H side. Use a low-profile or narrow RJ45 (≤15.2 wide), or keep the jack behind the frame and let only the plug pass. The O side is in the L-leg (16.8 wide), which is fine.
  - **USB-A** (14.5 wide shell incl. tabs): the 17.6 / 22.7 openings fit.
  - **HDMI** (≈15.0 × 5.6 shell): the 18.3 × 9.0 slot fits.
  - **Audio** jack nose Ø≤6.0 fits Ø6.36.
- The frame depth (thickness and stand-off from the board) was not measurable from a flatbed scan. Measure it (**M-IOF2**) to set the connector setback.
