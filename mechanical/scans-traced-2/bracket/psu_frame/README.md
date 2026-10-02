# psu_frame: scan 7 (I/O-board carrier frame on the PSU side)

The source is scan 7 (`psu_frame_scan.jpeg`, ≈100 dpi flatbed, same rulers as the other scans, SX 3.951 / SY 3.935 px/mm, ±0.2 %).

## What it is
- It is a rectangular sheet-metal frame with an open centre. A defocused PSU-like object is visible behind it, through the window.
- Its **6 bosses match the I/O board's 6 mounting holes**: rigid fit rms **0.28 mm**, every boss within 0.4 mm of its hole.
  - Pitch on the frame: 92.9 in X; 68.9 / 59.2 in Y.
  - Pitch on the I/O board: 92.5; 68.8 / 59.2.
- The PSU board's holes (95.3 × 64.5 / 64.7) do **not** match, so the PSU board does not screw to these bosses.
- **Reading:** this is the frame the I/O board screws onto, on its back (non-port) side, with the PSU behind it. The folder is named `psu_frame` per the task list. "I/O-board carrier on the PSU side" is the more exact name.
- The 6-point pattern alone cannot tell which face was on the glass (direct fit rms 0.22, mirrored 0.28). The sharp bosses suggest the boss face was down, so the data use the **mirrored** solution (boss face seen from the board). The frame is close to symmetric, so the choice moves features by less than 1 mm.

## Frame and files
- **Coordinates:** I/O board back-view frame (`bracket/io_board`). Origin is the bottom-left virtual corner, MEG-Array end at the top (Y+), mm. Overlay it directly on `io_board_outline.dxf`.
- `psu_frame.json`: all numbers below, plus the scan→frame transform.
- `psu_frame_ioboard_frame.dxf`. Layers: OUTLINE, BOSSES, BORES, CORNER_RINGS, BEADS, BLACK_PADS, FOAM_RAILS, WINDOW_APPROX, BOTTOM_FEATURE, IO_BOARD_REF (board outline and hole pads), NOTES.
- `psu_frame_overlay.png`: the trace drawn on the scan. Red is the outline and bosses; green is the registered I/O board outline and holes.
- Scripts: `edges7.py`, `screws7.py`, `finalize_frame7.py` (`trace_frame7.py` is the first gradient pass).

## Dimensions (±0.5 unless noted)
- **Outline:** **104.5 × 176.0**, X −1.83…102.63, Y −9.51…166.51. Corner R ≈ 3 (estimated, ±1).
  - The side edges have a 6–8 px soft ramp (bevel or flange), so take X ±1.
  - Relative to the I/O board (101.0 × 173.6), the frame overhangs 1.8 / 1.6 in X and extends **9.5 below the board's bottom edge**. The board's MEG-Array end sticks **7.1 beyond the frame top**.
- **Bosses:** 6 × face Ø**5.45** ±0.2, dark bore Ø**2.7** ±0.4. That suggests an M3-tapped (minor Ø≈2.5) or M2.5 boss; gauge it.

  | boss | X | Y | Δ to I/O hole |
  |---|---|---|---|
  | TL | 4.06 | 146.60 | −0.07 / −0.16 |
  | TR | 96.93 | 146.71 | +0.31 / +0.31 |
  | ML | 3.92 | 77.91 | −0.14 / −0.06 |
  | MR | 96.83 | 77.85 | +0.16 / 0.00 |
  | BL | 3.71 | 18.67 | −0.39 / −0.12 |
  | BR | 96.59 | 18.62 | +0.14 / +0.03 |

- **Black pads** around the bosses (insulator or foam, ±1). W × H at the centre:
  - top: 6.6–7.9 × 17.0–17.8 at Y≈150.4
  - middle: 6.6–8.1 × 7.6 at Y≈77.6
  - bottom: 6.8–7.9 × 26.9 at Y≈10.3
  - The X centres are 3.5–4.0 and 97.2–97.6.
- **Foam rails** (grey rounded strips between the pads, ±1.5): 11.4–11.9 wide, X centres ≈4.5–5.3 and 94.7–95.4.
  - Upper rails: Y 81.4…141.7.
  - Lower rails: Y 24.3…73.2.
  - The rails press on the **back of the I/O board along both long edges, about 11 mm in from each edge**.
- **Corner rings** (rivets or locating holes, Ø3.2–3.7 ±0.7): (2.45, 162.6), (100.0, 164.0), (1.9, −6.6), (98.1, −6.3).
- **Stiffening beads**, 3.6 wide:
  - top: Y≈163, X 4.4…95.3
  - bottom: Y≈−5.0, X 6.4…84.6
- **Open window**, approximate (±2): 77.2 × 147.4 centred at (49.8, 86.7).
- **Bottom feature:** a bright rounded rectangle, 72 × 14 at (50.2, 4.7), ±2. It is blurred, so it may be part of the object behind.

## Design consequences for a replacement I/O board
- Keep the 6 mounting holes at the stock positions. The frame bosses match them to 0.4 mm.
- Keep the back side clear wherever the frame touches it:
  - board-edge strips X 0…11 and X 90…101 along the foam rails
  - Ø8 around each hole, which matches the stock pads and the black pads
- Back-side parts in the centre must clear the frame window region and whatever sits behind it (PSU). Measure that depth (**M-IOF1**).
- The board's MEG-Array end extends 7.1 beyond the frame. Nothing on the frame constrains it there.
