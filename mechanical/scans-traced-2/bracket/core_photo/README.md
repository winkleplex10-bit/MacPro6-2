# Core photo: base-board standoff screws (the "rod")

Input: `core_flat_photo.jpg` (Aidan, 2026-10-01; 4032 × 3024). The thermal core lies flat on its CPU face with both GPU faces visible. A Flexi Ruler (cm scale reversed: 30 on the left, 0 on the right) lies beside it. Aidan says the base board mounts to the core on **long standoff screws sticking out of the core's bottom end**. These are the two black rods at the left of the core, and the "rod" from the GPU-face scan (face spec C-15).

## Scale
- **Ruler:** the scale varies along the ruler, ≈ 70 px/cm at the "30" end (x ≈ 1215) and ≈ 81 px/cm at the "1" end (x ≈ 3390). The phone was tilted and the ruler may not lie flat. The mean is 7.50 px/mm; interpolated at the rods (x ≈ 2090) it is ≈ 7.44 px/mm.
- **Local scale at the rods:** the rod centres sit at y = 1222 and 1949 px (727 px apart).
  - If they are the base-board gold holes G1/G2 (pitch 98.25 mm, base-board trace), the local scale is 7.40 px/mm. That matches the floor scale nearby, as it should, since the rods sit at the same height as each other and only ≈ 20–30 mm above the floor.
  - The only other mirror-symmetric hole pair, S1/S6 (105.4 mm), would give 6.90 px/mm. That is 7 % below the floor scale, which is impossible for objects above the floor. **So the rods are at G1/G2 (±49 mm).**
- The rods run along the core axis, parallel to the image, so they are not foreshortened.

## Measurements (local scale 7.40 px/mm)
| Item | Upper rod | Lower rod | Result |
|---|---|---|---|
| Tip x / core end-face x (px) | 2029 / 2163 | 2010 / 2148 | the core is turned ≈ 1.2° in the image |
| Visible length beyond the core end face | 134 px = 18.1 mm | 138 px = 18.7 mm | **18.4 ± 1.5 mm** (± includes the end-face edge position and perspective) |
| Shaft diameter | 34 px | 34 px | **Ø 4.6 ± 0.6 mm** (blur) |
| Collar/flange at the free tip | 42 × 10 px | ≈ 45 × 12 px | **Ø ≈ 5.7 × 1.4 mm** |

- The core's end frame is not flat. Near the ridge (apex between the GPU faces, with a screw at x 2120, y 1585) it reaches ≈ 5 mm further out than at the rods.
- The scan saw only 13.2 mm of rod (Y −10.3…−23.5). The extra ≈ 5 mm in the photo matches that frame bulge hiding the rod's base in the scan.
- **Interpretation [Inference]:** the BP's Ø4.0–4.4 gold holes are smaller than the shaft and collar. So the base board seats on the standoff tips (the gold ring Ø8.1–8.5 contacts the collar), and the stock T8 screws (923-0711) thread into the standoffs from below.
  - Hence: **core end face (at the holes) → BP top ≈ 18.4 ± 1.5 mm**.
  - In the module frame, the BP top is at Y ≈ −23.5 (scan rod tip), so the GPU-board bottom edge is ≈ 23.5 mm above the BP. Aidan's M1 says ≈ 15 mm, so this is **conflict C-16**. Measure with calipers (M1c).
- **Face angle:** the photo has strong perspective and tilt, so it cannot settle the GPU-face angle. The strip-pad apparent angles (27–37°, mean 32.5°) give θ ≈ 50°, but perspective biases that high. Inconclusive.

## Files
- `core_flat_photo.jpg` (input); `work_core_full.png`, `work_rod_top.png`, `work_rod_bot.png`, `work_ruler.png`, `z_rodT.png`, `z_rodB.png`, `z_end.png`, `z_r30.png`, `z_r1.png`: grid crops (full-image px).
