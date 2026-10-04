> **Update ≈ 16:25 ET: centre screws are now the PRIMARY plate→frame fixing (Aidan, 16:14 ET: "the couple of holes near the centre definitely have screws"). The 4 corner M1.6 screws below are now secondary.**
>
> *Re-check of the centre features.* Scan 83f0b85e, `io_plate_v2_A0_screw_candidates.png`. The centre features are soft in the scan (out of the focus plane), so all of these are visual reads, ±0.5.
>
> | # | Scan | Flex 821-2222 hole (mirrored trace) | Frame trace (mirrored) | Confidence |
> |---|---|---|---|---|
> | K9 | soft ring Ø≈2.4, core ≈1.0, at (53.2, 76.1) | HOLE_C1 Ø3.30 at (53.64, 75.53) | HOLE_C1 Ø3.17 at (53.89, 75.41) | **high** that a screw is here (Aidan + 3 sources); position ±0.3 |
> | K10 | dark disc Ø≈4.5–5 with bright arcs, at (53.0, 58.6) | HOLE_C2 Ø5.08 at (53.46, 58.16) | HOLE_C2 Ø4.84 at (53.44, 58.38) | **high**; ±0.3 |
> | K11 | faint arc + bright blob at (52.6, 19.3) | PIN_C3 Ø5.67 at (53.44, 19.27) | PIN_C3 Ø3 at (52.33, 19.23), "dark ring, bright centre" | **low**: may be a light pipe or pin; built only with `--c3` |
> | — | small ring at (47.7, 112.2) | BTN_EAR_1 Ø1.8 | — | flex button-carrier locating ear, not a screw |
>
> The three flex holes are larger than the frame holes. They are the clearance holes the stock posts pass through.
>
> **How the plate reaches the frame.** The frame is not 16.5–18 mm away; that is the plate-to-board-top gap. Plate inner face → PSA 0.05 + flex 0.12 + foam 1.0 = **1.17** → frame front face.
> - At the crown: frame front at 18.0 − 1.17 = 16.83 above the board top, frame back at 15.83.
> - The module model has `frame_back_height` 15.50–15.56 at the port columns; this is the same concentric frame.
>
> So the stock plate reaches the frame with a **post on the inner face**:
> - It runs 1.17 to the frame front, plus 0.8 into the frame hole, which is shorter than the 1.0 frame so the washer clamps the frame.
> - Post length 1.97 below the inner face; **local wall 3.37** (the only local exception besides the seats and corner bosses).
> - If M-IOF2 shows a different frame height, set `CENTRE_GAP` = D0(x) − frame-front height.
>
> **Design** (`CENTRE_SCREWS` in `build_plate.py`). Positions are the midpoint of the flex-hole and frame-hole centres.
>
> | Screw | Position | Post | Radial margins | csk (default) | pt (`_screwpt`) |
> |---|---|---|---|---|---|
> | **SCR_C1** | (53.76, 75.47) | Ø2.6 | 0.21 in the flex hole, 0.71 in the foam hole, 0.15 in the frame hole | M1.6 × 6 ISO 7046 countersunk T5 from outside: Ø3.25 csk + Ø1.8 clearance, M1.6 nut + Ø4 washer on the frame back | M1.6 × 4 thread-forming pan T5 + Ø4 washer from the frame side into a blind Ø1.30 pilot, 0.45 skin left |
> | **SCR_C2** | (53.45, 58.27) | Ø4.2 | 0.33 flex, 0.83 foam, 0.21 frame | same; washer **Ø6** because the frame hole is Ø4.84 | same; washer Ø6 |
>
> In csk mode the heads are visible on the outer face between the C columns.
>
> **Clearance (default; pt in brackets where it differs).**
>
> | Check | SCR_C1 | SCR_C2 |
> |---|---|---|
> | Nearest plate opening | C4 3.54 (3.87) | W_TB window 3.54 (3.07) |
> | Flex light pad / LED | LED (53.3, 70.9) 2.69 | PAD_TB 1.26 |
> | Receptacle shells, in plan | C4 2.67 | C6 2.03 |
> | Flex neck | 34.9 | 23.0 |
> | Speaker | 20.3 | 19.0 |
> | J31 | 64.6 | 47.7 |
> | Coin cell | 57.1 | 71.5 |
> | CONN_C / J7 (B side) | 64.9 | 46.7 |
> | J8 (B side) | 56.5 | 38.8 |
>
> - Module paddles and JMs lie under the posts in plan, but they are ≤ 2.34 above the board. The fastener ends 13.73 (14.23) above the board, so there is no conflict.
> - **Needs action 1, module clamp plate C** (PA12 1.6, top 15.26 above the board, 0.57 below the frame back). Both centre fasteners hang into it:
>   - It needs a **Ø5.0 clearance hole at SCR_C1** and a **Ø7.0 hole at SCR_C2**.
>   - At SCR_C1, the C clamp-post M2 screw at (53.19, 70.80) leaves only ≈ 0.3 of web. Move the post (H21) to Y ≤ 69.8, or merge the hole into a slot.
> - **Needs action 2, main board H13.** The frame-centre standoff (53.38, 58.38) sits directly under SCR_C2.
>   - Either drop H13 and use the nut,
>   - or make H13 an M1.6 standoff reaching the frame back (15.8) and run SCR_C2 (csk, M1.6 × 6–8) plate → frame → H13, without the nut. That is not possible in pt mode.
>   - The board is unchanged pending M-IOC4.
> - Existing item noticed: the M2 clamp-post screw heads on the clamp-plate top (15.26) have only 0.57 under the frame centre bar. They need countersinking in the clamp plate or frame clearance.
> - The corner screws were re-checked against the same list:
>   - SCR_B−: the washer/nut footprint overlaps the J31 ZIF in plan by 0.34, but sits 12.7 above the board. J28 is 1.0 away in plan. Check the flex tail route from the neck to J31 clears the SCR_B− nut by ≥ 2.
>   - SCR_T−: 0.61 in plan to the BT1 holder, 4.0 to the cell, 12.7 above the board.
>   - Speaker ≥ 19.8; flex neck ≥ 11.6.
>
> **Wall:**
> - General 1.372–1.423 (exact 1.400).
> - Seats unchanged.
> - Bosses and posts 0.37 (csk lip) to 3.37.
> - All 4 variants are single solids; z extent −4.71..0.
>
> **Centre-screw measurements (M-IOC*)**
> - **M-IOC1:** centre hole positions on the plate from the plate edges and the AC opening (calipers), and on the frame. Diameters: frame C1 Ø3.17 and C2 Ø4.84 (trace), flex Ø3.30 / Ø5.08.
> - **M-IOC2:** the stock post. Is there a post on the inner face, and what are its OD and length (inner face → frame front)? Foam thickness, free and compressed.
> - **M-IOC3:** the stock screw. Which side it is driven from, head type, Ø and height, drive, thread (M1.4 / M1.6 / M2), length. What it threads into: a nut, a clinch nut, a tapped frame, or the plastic post.
> - **M-IOC4:** is the frame also screwed to the board at C2 (decides H13)? Frame thickness at the centre bar, and frame-back height above the board (M-IOF2).
> - **M-IOC5:** is there a third screw at K11, between the audio jacks? Are the centre screws visible from outside with the case on?

> **Rev 2026-10-02 ≈ 16:10 ET: corner screws replace the glue (Aidan's suggestion, 15:55 ET).**
>
> *Evidence (`screw_candidates.py` → `io_plate_v2_A0_screw_candidates.png`).* Positions are back-view mm, read with the outer-face mapping of scan 83f0b85e.
>
> | # | Scan feature | Position (X, Y) | Size | Confidence | Interpretation / what it fastens to |
> |---|---|---|---|---|---|
> | K1 | sharp ring, image top-left | (74.77, 150.08) | dark core Ø1.0–1.3, ring Ø2.3–2.8 | high that it is a fixing point; X ±0.5, Y ±0.3 | stock plate→metal I/O frame fixing at frame hole CORNER (Ø3.16–3.50) |
> | K2 | sharp ring, image top-right | (29.84, 149.82) | same, ring partly in the corner shadow | high / ±0.5 | same |
> | K3 | sharp ring, image bottom-left | (74.60, 15.05) | same | high / ±0.5 | same |
> | K4 | ring, image bottom-right, half off the scan edge | (29.54, 13.93) | not measurable | medium / ±0.8 | same (inferred by symmetry) |
> | K5 | dark round hole at the +X edge, glue residue | (79.52, 140.89) | Ø≈2.4 | low | clip / latch window, not a screw |
> | K6–K8 | C-shaped hook marks | (30.61, 140.70), (76.61, 23.24), (28.96, 21.08) | 3–4 mm arcs | medium | stock clip points (CLIPS_L), not screws |
> | K9 | soft ring, centre column | (53.4, 75.4) | Ø≈2.5 | medium | frame HOLE_C1 (Ø3.2) locating hole, not a plate screw |
> | K10 | soft dark ring, centre column | (53.4, 58.4) | Ø≈5 | medium | frame centre screw HOLE_C2 (Ø4.85), which goes **frame → board standoff H13**. The plate does not reach it, so it is unchanged. |
>
> **What the four rings are.** K1–K4 form a 44.9–45.2 × 135.3–135.9 rectangle. That matches the frame-trace corner holes (44.2 × 135.3, Ø3.16 / 3.39 / 3.30 / 3.50).
> - The core (Ø1.0–1.3) fits either an M1.4/M1.6 screw recess (T4/T5 Torx) or a Ø1.1–1.3 threaded or pilot hole.
> - The ring (Ø2.3–2.8) fits an M1.4 head (dk 2.6–2.8) or an M1.6 countersunk head (dk 3.0).
> - The scan cannot tell a screw head from a brass insert or a hollow heat stake, so the fastener type has **low** confidence.
> - **Design choice: M1.6**, the middle of the M1.4–M2 range. It is a 3.0 head in a Ø3.2–3.5 frame hole.
>
> **Design (`FIX = "screws"`, `SCREWS`, `SCREW_MODE` in `build_plate.py`).** There are 4 screws, symmetric about the plate centre line, at a 45.1 × 135.25 pitch:
> - SCR_T− (30.64, 149.95)
> - SCR_T+ (75.74, 149.95)
> - SCR_B− (30.64, 14.70)
> - SCR_B+ (75.74, 14.70)
>
> Why symmetric: a symmetric pattern lands in the same place whichever face the scan shows, so the open inner/outer-face question does not move it. The scan rings are symmetric to within about 0.5 mm. The axes are radial, ±11.7°.
> - **Default `csk`:**
>   - Screw: M1.6 × 5 ISO 7046 / DIN 965 countersunk T5, driven from the outer face.
>   - Plate: 90° countersink Ø3.25, so the head sits 0.12 below the face; Ø1.80 clearance hole.
>   - Spigot: Ø2.8 × 0.8 on the inner face, locating in the frame corner hole. It is shorter than the 1.0 frame, so the washer bears on the frame.
>   - Frame back: DIN 125 washer Ø4 × 0.3 + M1.6 nut, or the stock clinch nut if the frame has one.
>   - Local wall 2.2; the lowest fastener point is z −6.71, which leaves 12.7 to the board top.
> - **Variant `--screw pt --tag _screwpt`:**
>   - Screw: M1.6 × 3 thread-forming-for-plastics pan/wafer T5, driven from the frame side.
>   - Plate: blind Ø1.30 pilot with 0.45 skin left, so the outer face is unbroken; same spigot.
>   - Engagement is ≈ 1.75, which is short. Use this variant only for light clamping.
> - **Glue band kept as a fallback:** DXF layer `GLUE_LANDS_OPTIONAL`, one land of 963 mm², now also 0.6 clear of the screw spigots.
>   - New DXF layers: `SCREWS` (countersink, clearance or pilot) and `SCREW_BOSSES` (spigots).
>   - New features-JSON entries: `fixing.screws` (per-screw checks) and `kind = "BOSS"`.
>
> **Clearance (all four screws OK):**
>
> | Check | Clearance |
> |---|---|
> | Outline edge, outer face | ≥ 1.29 (csk) |
> | Outline edge, inner face | ≥ 1.52 |
> | Flex outline (bottom pair) | 3.63 / 4.17 |
> | Flex outline (top pair) | > 30 |
> | Flex neck | ≥ 11.6 |
> | Nearest opening (AC, AUD_H, W_AUD_O) | ≥ 8.4 |
> | Port modules (A2 / A4 at the bottom) | ≥ 9.1 |
> | Fastener stack to board top | 12.7 vertical |
>
> Nearest F-side board parts: BT1 coin holder 2.6 in XY (SCR_T−), J31 flex ZIF 1.7 in XY (SCR_B−), L41 4.2 (SCR_T+). All are well below the nut, which sits 12.7 above the board top.
>
> **Wall:**
> - Outside the bosses: 1.372–1.423, which is STL faceting; exact 1.400.
> - Seats unchanged: 1.09–1.42 default, 0.61–1.75 tilt.
> - Bosses (allowed local exception): 0.37 at the countersink lip up to 2.2 at the spigot.
>
> **Variants rebuilt:** `io_plate_v2_A0`, `_tilt12p5`, `_eth2blank`, `_screwpt` (STEP + STL), with thickness PNGs and iso renders for each.
>
> **Disagreement to resolve.** The 100 dpi frame trace, mirrored as used, puts its corner holes 0.6–2.8 mm from the design screws: X 33.4 / 77.6 at the top, 30.3 / 74.5 at the bottom. It is a 1.3° parallelogram, which is probably scan skew.
>
> **Measurements (before printing):**
> - **M-IOS1:** frame corner-hole centres from the frame edges, and the pitch (X and Y), by caliper. Also the hole Ø, and whether the holes are plain, tapped, or carry clinch nuts or inserts.
> - **M-IOS2:** gap from the plate inner face to the frame front face at the corners (set `CORNER_GAP`), and the frame thickness (M-IOF2).
> - **M-IOS3:** the stock fastener: head type (pan / countersunk / wafer), head Ø and height, drive, thread Ø and pitch (M1.4 × 0.3 / M1.6 × 0.35 / M2 × 0.4), length, and which side it is driven from. Or it may be a heat stake or insert.
> - **M-IOS4:** the plate corner features measured on the part. Ring and core Ø, centres from the plate edges, and whether the hole is through or blind. Is it visible on the outer face with the case on?
> - **M-IOS5:** which face the scan 83f0b85e shows (open). Weak hint: the corner rings are sharp while the centre features are soft, which on a flatbed would favour the concave inner face being on the glass. The translucent light guides blur anyway.

> **Rev 2026-10-02 ≈ 14:40 ET (Aidan's plate corrections, 13:37 ET):**
> - **HDMI and power button are back in the stock positions.** In the back view (design frame), HDMI is at **+X (63.86, 107.07)** and the button at **−X (43.02, 108.11)**.
>   - Root cause: the 821-2222-A flex trace was digitised from its board-facing side, so it was mirrored. `mirror_flex_trace.py` mirrors it about **X_M = 53.408** (least-squares over the port cut-outs; ports move ≤ 0.064). The original is kept as `flex_821-2222_trace_asscanned.json`.
>   - The frame features (`io_frame.json`) were registered to the same grid. They are mirrored on load in `build_plate.py` and `section_plot.py`.
>   - The stock cover openings were mirrored the same way, so the **audio holes move** to (42.17, 19.42) and (63.41, 19.10).
>   - **AC** = (53.30, 130.15), taken from the new scan.
> - **Glued, not clipped.**
>   - `GLUED = True`, so `CLIPS = []`. The 3.0 × 1.2 rim, the Ø2.4 frame/ear pins, the LED/button-carrier pockets, the frame-screw relief and the 0.2 flex pocket are all removed.
>   - The flex is PSA-bonded flat on the inner face.
>   - **Glue lands:** a perimeter band from 0.4 to 3.4 mm in from the edge, kept 0.6 clear of the flex, its neck and every opening. It is one continuous land of 992 mm². It is flat inner face with **no added material**, drawn on the DXF layer `GLUE_LANDS` and in the PNGs.
>   - Land width (−X/+X): 1.9–3.0 mm along the sides and 4.5 at the ends. The −X side is interrupted at Y 28–48 by the flex neck.
> - **1.4 everywhere, edges included.** `SKIN = 1.4`, `RIM_H = RIM_W = 0`.
>   - Check (`check_thickness.py`, STL ray-cast along the skin normal at 0.5 mm pitch over 18,661 points): 1.372–1.423. The ±0.03 is STL faceting.
>   - The exact B-rep probe gives **1.400 normal** at the crown, at the long edges (27.35 / 79.05) and at the ends (Y −4.45 / 158.6).
>   - The only departures are the port-attachment exception, the flat plug seats under USB-C/USB-A/HDMI:
>     - default variant: 1.09–1.40;
>     - `_tilt12p5`: 0.61–1.75 (wall ≥ 0.6).
>   - The Z extent is 4.51 (curvature + 1.4), so there is no rim or edge lip.
> - **Scan check** (`scan_overlay.py` → `io_plate_v2_A0_scan_overlay.png`):
>   - Order from the top matches: AC → HDMI slot + round button → ETH pair → 3 USB-C rows → 2 USB-A rows → audio holes → audio light windows.
>   - Outline 163.0 × 52.0 matches the design's 163.1 × 51.9; the curved +X edge is lifted and shadowed.
>   - Scan positions: button blob (42.49, 107.06); HDMI (63.75, 106.87); audio (42.18, 19.38) and (63.41, 19.31).
> - **Variants:** `io_plate_v2_A0.{step,stl}`, `_tilt12p5`, `_eth2blank`.
> - **Previews:** `_outer.png`, `_iso_inner.png`, `_section.png` (4 rows, now including the button/HDMI row), `_thickness.png`, `_scan_overlay.png`, `_preview.png`.
> - **Render scripts:** `render_plate.py` (shaded STL), `check_thickness.py`.
> - **Open (inside-face scan pending):** LED / button-carrier side of the flex, glue footprint on the stock frame, frame-screw head height (M-IOF2) and the AUD_H jack-nose margin (0.04 at an assumed Ø6.0).

> **Rev 2026-10-02 ≈ 12:45 ET (D-IO16 swappable flex port modules):**
> - **Default axes:** port axes are **normal to the plate** (`TILT_OVERRIDE_DEG = None`: C −5.27 / +5.47°, A −5.25 / +5.51°, HDMI −5.33°). Plugs seat fully: overmold stand-off 0.0 with the seats, 0.03–0.04 without. Mouths are 18.40–18.59 above the board.
> - **Stock-tilt variant:** `--tilt 12.5 --tag _tilt12p5` writes `io_plate_v2_A0_tilt12p5.{step,stl}` and `_features.json` (no DXF / PNG). Its stand-off with the seats is C 0.68–0.72, A 1.14–1.21, HDMI 1.43; without them C 1.27–1.31, A 1.73–1.80, HDMI 2.02. Its frame slot is ≥ 0.19 (HDMI).
> - **Settings:** `AXIS_SHIFT_OUT = {}`. `RISER_T` = 1.16 is now the module stack under the connector seat (FPC 0.11 + PSA 0.05 + FR4 stiffener 1.0). USB-C is the HYCW417 (H 10.0, all SMD).
> - **Section plot:** `section_plot.py` now draws the modules: stiffener, FPC, SUS sleeve + collar, clamp plate (top = frame back − 0.3), cradle, C-fold and the DF40 pair. Module geometry is in `/workspace/kicad/macpro62-io-modules/modules.json`.
> - **Superseded text:** the riser text below is superseded.

> **Rev 2026-10-02 ≈ 12:00 ET (measured stock tilt, M-IOT2: 12.5° outward, mirrored):**
> - `TILT_OVERRIDE_DEG = 12.5` (None = radial 5.3–5.5°). The ports are **7.0–7.25° off the plate normal** at R 110, so the axis/mouth code no longer assumes radial axes: exact axis–surface intersection, mouth with no point proud (`MOUTH_CLR` 0.05), per-layer clearance of the tilted shell (flex, foam +0.3, frame slot) in `features.json → tilt.check`.
> - `AXIS_BALANCE` (HDMI −0.22 mm to clear the frame slot) and `AXIS_SHIFT_OUT = {"USBA": 0.35}` (USB-A riser edge clearance).
> - New `TILT_SEAT`: flat plug seats perpendicular to each axis on the OUTER face (overmold + 2 × 0.25, floor keeps ≥ 0.6 skin). Overmold stand-off USB-C 1.3 → 0.7, USB-A 1.7 → 1.1–1.2, HDMI 2.0 → 1.4 mm (open risk, M-IOT3 / M-IOC2).
> - Mouth centres 17.46–18.03 above the board (were 18.41–18.59). Flex margins ≥ 0.17 (HDMI Y, unchanged), X ≥ 0.19; frame slots ≥ 0.19. Inner face unchanged (smooth, flex flat).
> - Previews: `io_plate_v2_A0_section.png` (seat floors in violet), `io_plate_v2_A0_outer.png` (seats), `io_plate_v2_A0_preview.png` (flex check + outer + section).

> **Rev 2026-10-02 ≈ 11:30 ET (stock cover phone scan check, no geometry change):**
> - Scan (`../io_cover_scan/`, Gaussian-splat PLY) registered to the plate at **0.49 mm RMS** over 13 openings after a 0.931 rescale. Outline width ≈ 52.4 vs 51.9 (blur ≈ 0.5), centre and corners agree: **outline kept**.
> - Inner radius from the scan ≈ 101.7 (bootstrap 99.7–103.7, band spread 77–123) vs **109.97 from D0**: consistent, D0 kept. New switch `R_INNER_OVERRIDE = None` (set 101.7 to use the scan fit); `params.cover_scan` in the features JSON records the check.
> - Clips, ribs, bosses, pins, glue pocket and wall thickness are below the scan's resolution: unchanged. STEP/STL/DXF/PNGs regenerated (identical geometry).

> **Rev 2026-10-02 ≈ 10:50 ET:**
> - Plate radius re-derived from D0 (18.0 crown / 16.5 at the outer edge of the outermost port columns, |u| 18.1): **R 111.17 outer**.
> - USB-C / USB-A / HDMI openings are **straight through-holes along the tilted port axes** (±5.25–5.51°, D-IO14 column risers). The USB-C spot-faces are removed.
> - The smooth inner face and the flex fit are unchanged. Shell-in-cut-out margins: USB-C 0.45, USB-A 0.34, HDMI 0.17.
> - Mouth centres sit 18.41–18.59 above the main board.
> - Section: `io_plate_v2_A0_section.png`. Riser geometry: `/workspace/kicad/macpro62-io-risers/risers.json`.
> - Text below that mentions spot-faces, R 82 or straight port risers is superseded.

# MP62 I/O plate v2 rev A0 (new plastic plate; stock metal I/O frame and stock 821-2222-A flex kept)

Generated by `build_plate.py` (cadquery 2.8 + ezdxf): `/workspace/cadenv/bin/python build_plate.py [--eth2 open|blank]`, then `section_plot.py`.
The flex trace comes from `bracket/io_stock_photos/scan/bake_scan.py`.

**Rev 2026-10-02 ≈ 10:07 ET (flatbed scan of the 821-2222-A flex + measured D0):**
- No lands, bosses or ramps. The inner face is one smooth cylinder, so the stock flex lies flat in its 0.2 glue pocket.
- The port grid is the set of flex cut-out centres.
- The curvature comes from D0 (18.0 at the crown, 16.5 at |u| = 15.5): outer R 82.03.
- Connector heights and stack-up are in `io_plate_v2_A0_features.json` → `stack`. See IOB plan §4.7.1–4.7.4.

Coordinates are in the stock back-view frame: X to the right seen from behind, Y up toward the MEG/base end (audio at the bottom), Z = 0 at the outer crown, −Z into the machine. The board top is at z −19.2.

| File | Content |
|---|---|
| `io_plate_v2_A0.step` / `.stl` | Rev A0 default, ETH2 open (2 × RJ45) |
| `io_plate_v2_A0_eth2blank.step` / `.stl` | ETH2 blank (0.6 cosmetic recess), `--eth2 blank` |
| `io_plate_v2_A0_openings_backview.dxf` / `_frontview.dxf` | Outline, openings, windows, spot-faces, clips and pins. The front view uses the KiCad x frame (x = 40 + 101.0 − Xb). |
| `io_plate_v2_A0_features.json` | Parameters (incl. D0), parts, `stack` (required heights, plug recess, risers), `flex_check`, `led_check`, features |
| `io_plate_v2_A0_preview.png` | Outer face plus inner isometric |
| `io_plate_v2_A0_section.png` | Sections through the USB-C, USB-A and RJ45 rows: plate, flex, foam, frame, board top, connectors on risers |
| `io_plate_v2_A0_outer.png`, `io_plate_v2_A0_iso_inner.png` | Extra previews |
| `flex_821-2222_trace.dxf` / `.json` | Scan-based, idealised trace of the plate-facing side: outline, cut-outs, holes, pads, silver frames, 19 LEDs, button, tail + contacts, `IGNORED_BLACK_TAB`, reference layers. ±0.15; VERIFY by caliper |
| `flex_821-2222_scan_vs_photo_deltas.md` | Deltas against the 09:06 photo trace |
| `flex_821-2222_check.png` | Flex against openings, shells, frame slots, LEDs, pins and clips, with margins and required heights |
| `io_flex_foam_insulator_A0.dxf` | Foam / Formex die-cut: flex outline minus cut-outs + 0.3, holes + 0.5, button ring + 0.5 |

## Geometry (mm)

- **Outline:** 51.9 × 163.1, R 11.5 at (53.19, 77.07).
- **Body:** constant 1.2 wall. Outer R 82.03, inner face concentric. Rim 1.2 × 3.0, notched at X 76.0–81.5 / Y 27.7–47.6 for the flex neck.
- **Openings:** straight through, no lands.
  - USB-C 9.6 × 4.0 R 1.8 at X 43.09 / 63.69, Y 75.76 / 65.84 / 55.97.
  - USB-A 14.0 × 6.0 at X 43.12 / 63.76, Y 42.64 / 32.54.
  - ETH1 13.0 × 10.4 at (63.67, 91.60); ETH2 13.0 × 10.7 at (43.15, 91.41).
  - HDMI 15.6 × 5.7 at (42.96, 107.07). AC stock window.
  - Audio Ø4.8 at the stock positions. Button Ø12.4 at (63.79, 108.11).
- **Flex seat:**
  - Glue pocket 0.2 deep (outline + 0.2).
  - 19 LED pockets and a Ø16.17 button-carrier pocket, 0.70 above the flex face (wall 0.35; `LED_H`, `BTN_CARRIER_H` TO MEASURE).
  - Light windows on the scanned pads.
  - Locating pins Ø2.4 × 2.5 at (52.93, 75.41) / (54.49, 19.23); ear pins Ø1.4 × 0.8.
- **Outer spot-faces** at the two USB-C columns: 12.8 × 26.8, floor z −0.68 / −0.70, wall ≥ 0.6.
- **Clips:** 7. The mirrored clip at (76.78, 30.3) is dropped because of the flex neck. The stock clip points stay.
- **Required board-top-to-mouth heights:**
  - USB-C 17.90 (H) / 17.82 (O).
  - USB-A 17.49 / 17.38.
  - HDMI 17.24 (the shell must be ≤ 15.4 × 5.6 to pass the flex).
  - RJ45 face ≤ 13.6 / 13.7.
- **Plug recess:** USB-C 0.62–0.67, USB-A 1.69–1.78, HDMI 1.96.
- **Rebuild:** if D0, the wall, foam, frame or LED heights change, edit the parameters at the top of `build_plate.py` and rebuild.
- `--flex none` (collars, light pipes) is retired.

## Process, material, tolerances (ordering at JLC3DP or PCBWay)

| Process | Use | Notes |
|---|---|---|
| **MJF PA12, dyed black** | **Recommended (rev A)** | Tough, clips survive, no supports. About $10–20 each. |
| SLA black resin (tough/ABS-like) | Cosmetic second print | Best surface. Brittle clips: use L 7.0, hook 0.4. Supports go on the inner face. |
| CNC (ABS, PC, POM) | Final batch only | ±0.05, about $80–200 (curved face + pockets + clips). |
| Clear SLA, polished | Power-button cap | Light passes through to D20. Cap CAD is TODO (Ø12.0 × 3 on a Ø6 stem). |

**Design values:**
- Skin 1.2 (1.0 under the glue pocket); rim 1.2 × 3.0; land backing 1.0 (≥ 0.8 at the ramps); pins Ø2.7; clip tab 1.2.
- MJF minimum wall is about 0.8 (1.0 recommended); SLA about 0.6–0.8 [vendor rules, check on the order page].
- Tolerance about ±0.2–0.3 mm or ±0.3 % (±0.5 over the 163 mm length). Openings carry ≥ 0.3 per side; USB-C is 9.6 × 4.0 R1.8 around an 8.94 × 3.26 shell.
- MJF holes print 0.1–0.2 small: light-pipe bores are Ø2.2 for Ø2.0 PMMA rods (ream if tight).
- **Snap clips:** 1.2 t × 5.0 w × 6.0 L, hook 0.5, so bending strain ≈ 1.5·t·y/L² = 2.5 % (PA12 OK). Too stiff: file the hook. Loose: hook 0.6.
- Plate-to-frame clearance is 0.2–0.3 per side.

**Order:**
- Upload `io_plate_v2_A0.stl` (or `.step`): MJF PA12, dyed black, qty 2, standard bead-blast finish, no supports.
- Order `io_plate_v2_A0.*` (ETH2 open). The `_eth2blank` file is only for a single-Ethernet build.
- **Not ordered.** Measure M-IOT2 (curvature) and M-IOF2 (D0) first.
