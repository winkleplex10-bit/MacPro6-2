# base_and_psu_v1.step: geometry summary

Source: `Mac Pro PCB (PSU & Bottom Board).step` (Fusion 360 / Autodesk Translation Framework, AP214), product "Mac Pro PCBs v1".
Loaded with CadQuery 2.8.0 (OCP), from a venv at `/workspace/cadenv`. Scripts are in `scripts/`. The raw face dump is in `inspect_raw.txt`.

**Units:** millimetres (`SI_UNIT(.MILLI.,.METRE.)`).
**Bodies:** 2 solids in one component, named only `Body1` and `Body2`. There are no separate screw or standoff bodies, and there is no assembly transform. Appearance is the default "Steel - Satin".

| Body | Shape | BBox X | BBox Y | BBox Z | Volume (mm³) | Likely identity |
|---|---|---|---|---|---|---|
| Body1 | Rounded rectangle with tabs + 6 standoffs | -51.500 … 51.456 | -79.050 … 79.966 | -2.000 … 1.200 | 19 250.8 | **PSU board** with its screw points (inferred, see "Ambiguity") |
| Body2 | Plain disc | 74.000 … 196.000 | -56.000 … 66.000 | 0.000 … 1.000 | 11 664.7 | **Round bottom/base board** |

## Body2: round base board
- Outline: a single circle, **Ø122.000 mm**. Its centre is at model (135.000, 5.000).
- Thickness **1.000 mm** (z 0 to 1).
- Holes, with the circle centre as origin: **2 × Ø4.000 through holes at (-49.000, 0.000) and (+49.000, 0.000)**. They are 98.000 mm apart centre to centre, and each hole edge is 10.000 mm from the board edge.
- **No central slot, cutouts, notches, fillets or chamfers are modelled.** The faces are just the top, the bottom, the outer cylinder and the 2 hole cylinders.

## Body1: rectangular board (PSU?)
Coordinates use the model origin. It sits at about the board centre; the bbox centre is (-0.022, 0.458).
- Thickness **1.200 mm** (z 0 to 1.2).
- Overall extents **102.956 × 159.016 mm**, tabs included.
- Main rectangle: x -51.500 to 51.456. y runs from 75.966 down to -72.550 on the left and to -72.952 on the right. Corner radius R3.5, centred on the corner holes.
- Top tab: +4.000 mm tall (to y 79.966). It is 55.956 wide at the base (x -28.000 to 27.956) and 52.956 wide at the flat top. R1.5 fillets, concave and convex.
- Bottom tab: down to y -79.050, 78.956 wide (x -39.500 to 39.456). It is 6.500 deep on the left and 6.098 deep on the right. R1.5 fillets.
- **6 × Ø2.000 through holes**, depth 3.2 mm through the board and the boss. Each is concentric with a **Ø3.000 OD × 2.000 mm tall standoff boss** on the underside (z -2 to 0):

| Hole | X | Y |
|---|---|---|
| L-top | -48.000 | 58.950 |
| L-mid | -48.000 | -5.050 |
| L-bot | -48.000 | -69.050 |
| R-top | 47.956 | 58.548 |
| R-mid | 47.956 | -5.452 |
| R-bot | 47.956 | -69.452 |

  Each column has a 64.000 mm pitch, and the columns are 95.956 mm apart. Each hole is 3.500 mm from the side edge.

## Relative placement
The boards are **not assembled or stacked**. They lie side by side in the same XY plane, with both bottom faces at z = 0.
The round board's centre is at (+135.000, +5.000) from Body1's origin. The X gap between the edge of Body1 (x 51.456) and the edge of the disc (x 74.000) is 22.544 mm.
So the file defines no mechanical relationship (height or offset) between the PSU and the base board.

## Ambiguity and issues
- Bodies are only named Body1/Body2. Which one is "PSU" is inferred from shape: the disc is the round board, so the rectangle with standoffs is taken as the PSU.
- **The round board is Ø122 mm, not about 160 mm** as estimated from the photo. Body1 is the part that is about 159 mm long.
- The round board has no central slot or other cutouts. It has only 2 holes.
- The "screw points" are bosses fused into Body1. They are not separate bodies, and there are no screws or threads.
- Body1 is slightly asymmetric, which looks like sketch imprecision. The right-hand features sit at x 47.956 / 51.456, against -48.000 / -51.500 on the left (0.044 mm off). The right hole column and the bottom-right edge are 0.402 mm lower in Y than the left. The top corner arcs are both at y 72.466.
- The 1.0 mm and 1.2 mm thicknesses are what is modelled. Check them against the real boards.

## Outputs
- `base_board_outline.dxf`: Ø122 circle + 2 × Ø4 holes. Origin is the circle centre. Mid-plane section at z 0.5. Units mm.
- `psu_board_outline.dxf`: outline (24 lines and arcs, closed) + 6 × Ø2 holes. Model origin. Section at z 0.6. Units mm.
- `psu_standoff_bosses.dxf`: Ø3 / Ø2 boss rings, sectioned at z -1.0. For reference only; don't import to Edge.Cuts.
- `assembly_iso.png`, `base_board_top.png`, `psu_board_top.png`, `psu_board_bottom_iso.png`
