# Stock base board (logic-board disc): calibrated scan trace

Inputs: `base_board_bottom_scan.jpeg` (solder/bottom side) and `base_board_top_scan.jpeg` (top side). These are Aidan's flatbed scans at ≈ 100 dpi with rulers.
Run: `/workspace/cadenv/bin/python trace_base_board.py`, which writes `base_board.json`, the DXF and the overlays. `rectify_bp.py` writes the 8 px/mm rectified images in `work/`.

## Frame and calibration
- **Calibration:** ruler FFT, 3.951 px/mm (X) and 3.935 px/mm (Y), scale ±0.22 %. The MEG-Array pad pitch (FFT 1.272 / 1.264 mm against 1.27 nominal) independently checks the scale to ≈ 0.2 %.
- **BP frame:** top view, origin at the **midpoint of the two gold holes**.
  - +x points toward G2, at the socket's key end.
  - +y points toward the GPU connectors and the core; −y points toward the PSU.
  - The bottom scan is mirrored into this frame. The top and bottom scans register on the 8 holes with a proper rotation, rms 0.42 mm.
- **Accuracy:** features ±0.5 mm; blurred top-side bodies ±2 mm.

## Results
| Item | Value |
|---|---|
| Disc | **Ø 122.07 mm** (threshold spread 121.74–122.35, sd 0.16, max dev 0.41). A pure circle with no notches. |
| Disc centre vs hole midpoint | (0.00, −0.74) bottom scan / (0.05, −0.52) top scan. The **hole axis lies 0.6 ± 0.3 mm on the +y side of the disc centre**; the BP KiCad has it at 0. |
| Gold holes G1 / G2 | (∓49.13, 0). **Pitch 98.25 ± 0.3** (CAD 98.0). Gold ring Ø 8.1–8.5, hole Ø 4.0–4.4. These carry the **core's standoff screws**: they protrude ≈ 18.4 mm from the core end and the board seats on their tips (`../core_photo/README.md`). |
| 6 small plated holes (pad Ø ≈ 3.3, purpose unknown) | S1 (−52.64, 13.81), S2 (−26.57, −46.65), S3 (26.49, −46.64), S4 (−18.12, 50.70), S5 (18.49, 50.72), S6 (52.80, 13.88). They lie on r ≈ 53.6–54.6 at 165/−120/−60/110/70/15° and are mirror-symmetric about the y axis. |
| CPU riser socket | Top frame 78.69 × 12.95 at (−0.04, −12.14). Slot 68.43 × 4.86 at (−0.02, −12.57). End-peg pairs at x ±35.6 (span 71.32), with a peg centre at (−0.07, −12.49). Parallel to the hole axis within 0.06°. **Key at x +8.94**, matching the stock riser key (carrier front view 69.03, so BP x = 78 − 69.03 = +8.97). **Slot centreline y = −12.5 ± 0.3 from the hole axis** (−11.9 from the disc centre). |
| GPU connector fields (MEG-Array, bottom pads, 1.27 pitch) | **GPU_L** centre (−35.76, 31.89), 39.3 × 12.9, axis 46.5°, r 47.9 at 138°. **GPU_R** (35.63, 32.26), 38.4 × 13.0, axis −46.7°, r 48.1 at 42°. Tangential at r ≈ 48. The top bodies are ≈ 45 × 18 each. |
| PSU-side connector field | Centre (−1.73, −48.74), 44.3 × 17.3, axis 0.65°, x −23.4…19.1, y −57.4…−40.2. Probably the I/O link [Inference]. |
| Other | Dark round parts at (−0.1, −59.7) and (0.2, 50.5). Dark square at (−45.2, −14.2). Bottom IC ≈ 8 × 8 at (31, −35). White block at (45.7, −35). Top IC ≈ 10 × 12 at (1, 20) ±2. |

## Deltas against the MP62 backplane KiCad (`/workspace/kicad/macpro62-backplane`, disc-centre frame)
- **J1 (CPU-LINK) at (0, −12.6):** the measured slot is at −12.5 ± 0.3 from the hole axis and Δx −0.02. **No move needed.** In the disc-centre frame the slot is at y ≈ −11.9, because the holes are offset 0.6 from the disc centre; that is within the J1 tolerance.
- **H1 / H2 at (±49, 0):** measured pitch 98.25 (+0.25), and the axis is 0.6 mm off the disc centre. The Ø4 holes plus screw float absorb this. Proposed: keep ±49.1 and add the 0.6 offset if the outline is re-referenced.
- **6 small holes vs BP courtyards:** S2 lies **inside the U4 courtyard (1.15 mm)**. S3 is 1.9 mm from J6, S4 and S5 are 1.4 and 1.2 mm from J4 and J3, and S1 and S6 are 2.9 and 3.0 mm from J10 and J9. Change request: add Ø6 keep-outs at S1–S6 until their purpose is known, and move U4.
- **Stock GPU connector axes ±46.6°**, against BP J9 / J10 at ∓60° (face normals at 30°/150° assumed). This hints that the GPU face normals sit at ≈ ±45° from the hole axis, not 30°/150°. Measurement request; no change made.

## Files
- `base_board_bp_frame.dxf`, with layers DISC_OUTLINE, HOLES_GOLD_D4, HOLES_SMALL, CPU_SOCKET_FRAME/SLOT/PEGS/KEY, CONN_FIELDS, OTHER, BP_KICAD_REF, NOTES.
- `base_board_overlay_bottom_bpframe.png`, `base_board_overlay_top_bpframe.png`, `base_board_vs_bp_kicad.png`.
- `work/`: rectified images (8 px/mm), crops, `bp_kicad_fps.json` (BP courtyards in the disc frame).
