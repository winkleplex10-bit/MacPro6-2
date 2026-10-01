# all_pcbs_v2.step: geometry summary

Source: `Mac Pro PCBs (no IO Board).step`, exported 2026-10-01 11:14 EDT by Fusion 360 (Autodesk Translation Framework v15.15, AP214). Product "Mac Pro PCBs v2". Copied to `/workspace/macpro62-cad/all_pcbs_v2.step`.
**Units:** mm. Loaded with CadQuery/OCP from `/workspace/cadenv`. Scripts: `scripts/step_inspect_v2.py`, `v2_analyze.py`, `v2_export_dxf.py`, `v2_render.py`. Raw dumps: `v2_inspect_raw.txt` (faces) and `v2_section_dump.txt` (mid-plane section edges in the board-local frames).

## 1. Bodies
The file has 4 solids in one component. They are named only Body1 to Body4. There are no sub-assemblies or placement transforms, and every body has the default "Steel - Satin" appearance.

| Body | Model bbox X / Y / Z | Size (mm) | Thick. | Volume (mm³) | Likely identity |
|---|---|---|---|---|---|
| Body1 | -51.500…51.456 / -79.050…79.966 / -2.0…1.2 | 102.956 × 159.016 | 1.200 (+2.0 bosses) | 19 250.835 | **PSU board**. Unchanged from v1. |
| Body2 | 74…196 / -56…66 / 0…1.0 | Ø122.000 | 1.000 | 11 664.734 | **Round base/logic board**. Unchanged from v1. |
| Body3 | 225…381 / -94…75 / 0…2.0 | 156.000 × 169.000 | 2.000 | 48 260.402 | **CPU board**: wide, edge-connector tab, 8-hole socket pattern. |
| Body4 | -220…-116 / -86…80 / 0…1.6 | 104.000 × 166.000 | 1.600 | 27 110.830 | **GPU board?** Plain board with 4 holes and no connector (see issues). |

**Changes from v1:** Body1 and Body2 are byte-for-byte the same geometry. Their 72 and 6 vertices match exactly (max difference 0.0), face counts and volumes are identical, and they sit at the same model positions. The only additions are Body3 and Body4.

## 2. Boards

### Body3: CPU board (origin = left end of the edge-connector tab tip, model (225.0, -94.0); +Y runs away from the connector)
- Overall **156.000 W × 169.000 H**, **2.000 mm thick**. The board/tab centreline is at x = 78.000.
- **Edge-connector (gold-finger) tab:** x 44.000 to 112.000, so **68.000 wide** and centred on the board. It runs from the tip at y 0 to the shoulder line at **y 16.063**, a **depth of 16.063 mm**. The tab tip corners are sharp. The tab-to-shoulder inside corners have **R2.5** concave fillets. No pads, finger bevel or chamfer are modelled.
  - **One key notch:** x 84.500 to 89.500, so **5.000 wide, centred at x 87.000**. That is **9.000 mm right of the tab centre**, 43.0 from the tab's left edge and 25.0 from its right edge. It has parallel sides and a **R2.5 semicircular end**, and it runs the **full tab depth**: straight sides to y 13.563, apex at y 16.063, which is tangent to the shoulder line. The finger segments are **40.500** (left) and **22.500** (right) wide.
- **Shoulder:** flat at y 16.063 from x 25.347 to 41.5 and from 114.5 to 130.653. The lower outer corners are **chamfered**, with a virtual chamfer line from (0, 30.000) to (24.000, 16.063), at **30.14°** to the edge, with **R5** fillets at both ends. It is mirrored on the right: (156, 30.000) to (132.000, 16.063). The straight sides run from y 32.878 to 164.000.
- **Top edge (y 169):** corners **R5**. There are **2 rectangular notches, each 24.000 wide × 5.000 deep**, at x 24 to 48 and x 108 to 132 (centres x 36 and 120, ±42 from the centreline). All 8 notch corners have **R1.3** fillets.
- **Holes:** 8 × **Ø5.000** through holes in 2 columns at x 40.000 and 109.500.

| Role (per user note) | Holes (x, y) local | Model (x, y) | Pattern |
|---|---|---|---|
| **Heatsink / thermal-core (OUTER)** | (40.0, 46.0) (109.5, 46.0) (40.0, 101.0) (109.5, 101.0) | (265, -48) (334.5, -48) (265, 7) (334.5, 7) | **69.500 X × 55.000 Y** (diag. 88.63) |
| **CPU retention bracket / ILM (INNER)** | (40.0, 58.0) (109.5, 58.0) (40.0, 89.0) (109.5, 89.0) | (265, -36) (334.5, -36) (265, -5) (334.5, -5) | **69.500 X × 31.000 Y** (diag. 76.11) |

  - Both patterns are concentric. **The socket centre (centre of the inner pattern) is at (74.750, 73.500) local, which is model (299.750, -20.500).** It is 73.500 mm from the tab tip and 57.437 mm above the shoulder line.
  - Within each column the inner and outer holes are 12.000 mm apart in Y. "Outer" and "inner" differ **only in Y**, because both patterns share the same two X columns.
  - The pattern centre is **3.250 mm left of the board/tab centreline**: the holes are 40.0 from the left edge and 46.5 from the right edge.

### Body4: GPU board? (origin = bottom-left bbox corner, model (-220.0, -86.0))
- **104.000 × 166.000**, **1.600 mm thick**. Top corners are **R5**. The bottom corners are chamfered **17.000 (X) × 13.000 (Y)**, from (0, 13) to (17, 0), at 37.41°, with **R10** fillets at both ends of the chamfer. The flat bottom runs from x 20.385 to 83.615 and the sides are straight from y 17.942 to 161.
- **4 × Ø5.000 holes** at (15.0, 44.5), (89.0, 44.5), (15.0, 94.5), (89.0, 94.5). That is **74.000 × 50.000**, centred at (52.0, 69.5) on the board centreline, 15.0 from each side. In model coordinates: (-205, -41.5), (-131, -41.5), (-205, 8.5), (-131, 8.5).
- There is no edge connector, notch or cutout.

### Body2: base board (origin = circle centre, model (135, 5)). Same as v1.
**Ø122.000**, **1.000 thick**, with **2 × Ø4.000 holes at (±49.000, 0)**, 98.000 apart centre to centre. There are no other features.

### Body1: PSU board (origin = model origin, as in v1). Same as v1.
**102.956 × 159.016** including the tabs, **1.200 thick**, corner R3.5, tab fillets R1.5. The top tab is 55.956 wide and +4.000 tall; the bottom tab is 78.956 wide.
There are **6 × Ø2.000 holes** at (-48.000, 58.950 / -5.050 / -69.050) and (47.956, 58.548 / -5.452 / -69.452), each with a Ø3 × 2 mm standoff boss on the underside. The rows have a 64.000 pitch and the columns are 95.956 apart. The v1 asymmetry (0.044 mm in X, 0.402 mm in Y) is still there.

## 3. Assembly relationships
**None. The boards are laid out flat.** All 4 bottom faces are at z = 0 (the PSU bosses go down to z -2), and the boards are spread along X: GPU?, then PSU, then base, then CPU. No board is rotated. So the file gives **no** face-to-face angles (60° triangle), no heights from the face-board edges to the base plane, no base-board position and no PSU placement. Assemble the boards in Fusion if you need these relationships.

## 4. Issues / ambiguity
1. **Only 4 bodies.** The expected set was base, PSU, CPU and 2 × GPU, and possibly an interposer. **There is only one GPU-like board and no interposer or other small boards.** The second GPU may be intended to reuse Body4, but the file doesn't say so.
2. **Body4's identity is inferred.** It is 166 mm long, not the roughly 210 to 220 mm estimated from the photo. It has no connector and only 4 holes, so its length and identity need checking. Body3 is taken as the CPU board because it has the edge-connector tab and the inner/outer 8-hole pattern described.
3. **Hole roles come from the user's note, applied geometrically.** Outer = farther from the pattern centre in Y (±27.5). Inner = ±15.5. Both share X = ±34.75. If the real heatsink and ILM patterns differ in X, the model doesn't show it. All 8 holes are the same Ø5.0, which is a placeholder-looking diameter.
4. **The CPU hole pattern is off the board centreline** by 3.25 mm, while the tab and top notches are symmetric about x 78. This may be intended, or it may be a sketch slip.
5. **Non-round values on the CPU board:** the shoulder/tab depth is 16.0634 and the chamfer angle is 30.143°, not 30°. They look like the result of a constraint, such as a chamfer from (0, 30) to (24, shoulder). Check that they are intended.
6. **Thicknesses are all different:** CPU 2.0, GPU 1.6, PSU 1.2, base 1.0. Check them, especially the CPU edge-connector thickness against the mating slot.
7. No gold-finger pads, components, connectors or mounting standoffs are modelled on the new boards. They are outline and hole geometry only.

## 5. Outputs (`/workspace/macpro62-cad/v2/`)
- DXF (R2010, $INSUNITS = 4 mm, 1:1, mid-thickness section, layers `OUTLINE` and `HOLES`). All outlines are closed (0 unmatched endpoints, checked with ezdxf):
  - `cpu_board_outline.dxf`: 21 lines + 17 arcs + 8 circles
  - `gpu_board_outline.dxf`: 6 lines + 6 arcs + 4 circles
  - `base_board_outline.dxf`: 1 circle + 2 holes
  - `psu_board_outline.dxf`: 12 lines + 12 arcs + 6 holes
- PNG: `all_pcbs_v2_iso.png`, `cpu_board_top.png` (heatsink holes in red, bracket holes in green, socket centre in magenta), `gpu_board_top.png`, `base_board_top.png`, `psu_board_top.png`
