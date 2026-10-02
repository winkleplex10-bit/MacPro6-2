# MacPro6,2 Face Module Specification, v0.1 ("MP62-FACE v0.1")

**An open, Framework-16-style module standard for the two non-CPU faces of the Mac Pro Late 2013 thermal core**

| Item | Value |
|---|---|
| Document | MP62-FACE Module Spec **v0.1** (draft for review) |
| Date | 2026-10-01 |
| Owner | Aidan Winkler (MacPro6,2 project) |
| Supersedes | §7 "OPEN FACE MODULE SPECIFICATION, v0.2" of `macpro62-architecture-spec-v0.2.md` for everything module-side. Host-side items (BP, CPU board) stay in the architecture spec; changes needed there are listed as change requests in §13. |
| Mechanical revision | **MP62-FACE-MECH 0x0001** (this document, §3). Written into every module EEPROM (§8). |
| Status | **Provisional.** Every dimension tagged **TO MEASURE** must be checked on a real core/enclosure before anyone fabricates a module. |
| Licence (proposal) | CC-BY-4.0 for this text and drawings; CERN-OHL-P-2.0 for the KiCad template. |

**Tags** (as in spec v0.2): **[Sourced]** = from a document, datasheet or CAD file named in §16 · **[Proposal]** = a decision made here · **[Estimate]** = a number derived from estimates · **[Inference]** = reasoning, not verified · **TBD** / **TO MEASURE** = open.
**Normative words:** *shall* = required for compliance, *should* = recommended, *may* = allowed.
**Numbering:** sections are versioned. A heading tagged `[v0.1]` was written or rewritten for this release; later releases will tag the sections they change.

**Deliverables in this package**

| File | What it is |
|---|---|
| `macpro62-face-module-spec-v0.1.md` | This document |
| `macpro62-face/macpro62-face-v0.1-mech.png` | Mechanical drawing: outline, holes, keep-outs on both sides, connector zones, outer height zones, section |
| `macpro62-face/macpro62-face-v0.1-system.png` | Link / power / display path diagram and power sequencing timing |
| `macpro62-face/macpro62-face-v0.1-outline.dxf` | DXF R2010, mm, layered: outline, holes, keep-outs, connector zones, height zones, core die/strip pads, bosses, plate, tab |
| `macpro62-face/pinouts/*.csv` | Full contact-level pinouts: MCIO 124 PCIe, MCIO 74 DISPLAY-LINK, AUX GH15, power |
| `macpro62-face/tools/` | Generators (single geometry source `face_geom.py`), EEPROM encoder/validator `mp62_eeprom.py` |
| `macpro62-face/eeprom_examples/*.bin` | Example ID EEPROM images (MXM RX 6600 carrier, ASM2824 storage) |
| `kicad/macpro62-face-template/` | KiCad 9 template: Edge.Cuts, 4 mounting holes, rule-area keep-outs (bracket, both bus-bar tongue zones KO-F2A/B, core tab KO-F5A/B), both lug sites wired in parallel (reference tracks), core contact zones on User.1, connector placeholders, JLC 6-layer stackup, netclasses. `kicad-cli pcb drc`: **0 violations, 0 unconnected** |
| `kicad/macpro62-storage-face/` + `macpro62-storage-board-plan.md` | Storage reference module SM-1 rev A0 (§11.3): floorplan PCB (DRC 0/0), schematic (ERC 0/0), plan with BOM, cost and RAID analysis |
| `bracket/core_gpu_face/` | Core GPU-face scan, calibrated and traced: `trace_core_gpu_face.py`, `core_gpu_face.json`, DXF in the module frame and in the scan frame, overlay PNGs (on the scan, and in the module frame) |

![MP62-FACE v0.1 mechanical drawing](macpro62-face/macpro62-face-v0.1-mech.png)

---

## 0. Revision history

| Version | Date | Changes |
|---|---|---|
| v0.1 (sections in the architecture spec) | 2026-09 | Card-edge (SFF-TA-1002) concept, withdrawn in v0.2 |
| v0.2 (§7 of the architecture spec) | 2026-10-01 | MCIO 124 + GH14 AUX + bus-bar lugs; OCP FLEXIO logical map; IPMI FRU EEPROM; display TBD (OD-2) |
| **MP62-FACE v0.1 (this standalone spec)** | 2026-10-01 | First standalone release. Mechanical frame, outline, holes and keep-outs defined (§3), including core contact zones traced from the core scan and the measured 4.5 mm core gap. MCIO 124 confirmed as **one 16i connector per face**, SFF-9402 sideband positions (§4). AUX moves to **GH15** (adds MOD_LED#; USB2 primary) (§5). Power budget **Face P 150 W / Face S 40 W**, new classes, eFuse and sequencing rules (§6). Binary MP62 descriptor EEPROM (§8). **DISPLAY-LINK = second MCIO (74-pin, 8i) on the module with a twinax cable to the IOB** (§9). KiCad template, DXF and drawings. |
| MP62-FACE v0.1 update 1 | 2026-10-01 (≈ 17:45 ET) | **Mirrored bus-bar lugs (C-17):** both lug sites (A at X ≈ 97, B at X ≈ 7) on every module, wired in parallel; KO-F2B, KO-F5B and the mirrored rod added (§3.3, §6.4.1). **Rod identified (C-15)** as the base-board standoff screw; core-bottom spacing conflict with M1 logged (C-16). Drawing, DXF, KiCad template (J22/J23, rule areas, reference tracks; DRC 0/0) and power pinout updated. |
| MP62-FACE v0.1 update 2 | 2026-10-01 (≈ 18:30 ET) | Base-board scan: stock GPU connector axes ±46.6° → face-angle conflict **C-18** and measurement M2c logged (no module geometry change). Standoff screws confirmed at the base-board holes (pitch 98.25). |
| MP62-FACE v0.1 update 3 | 2026-10-01 (≈ 20:20 ET) | **Storage reference module SM-1** designed (plan `macpro62-storage-board-plan.md`, KiCad `kicad/macpro62-storage-face/`): §11.3 rewritten (ASM2824 on the die pad with a gap pad, 4 × 2280 on the outer side, bracketless). New conflicts **C-19** (bracketless modules / KO-B1), **C-20** (>2 W rule vs outer-side M.2 SSDs), **C-21** (THERM_ALERT# throttle for storage). New measurements MF-13, MF-14. Storage parts added to §15. RAID finding: no driverless bootable hardware RAID is orderable (§11.3). |
| MP62-FACE v0.1 update 3a | 2026-10-01 (≈ 20:30 ET) | Aidan approved bracketless SM-1 (C-19): 4 × 2280, module held by low-head screws (head + washer ≤ 1.6 mm); MF-13 redefined (thread/length for the screw part number). |
| MP62-FACE v0.1 update 4 | 2026-10-02 (≈ 13:15 ET) | ICD rev 2 (Aidan's decisions): **face normals ≈ 45° / 135°** (M2c answered, C-18 closed; module frame unchanged); BP J9/J10 re-placed (fp5) → cable jogs 13.7 mm (Face P) / 10.5 mm (Face S); **CR-2 closed by a flat-twinax jog cable** (§3.5, §3.6); **445 W system ceiling** replaces the 405 W rule (§6.3); new **§6.8 live power target** (12 V monitor INA228 @0x40 mandatory for modules > 3 W, power-target agent @0x58, THERM_ALERT# fast cap); SMBus map §8 updated. |

---

## 1. Scope [v0.1]

1. **What a module is.** A printed circuit board that replaces the stock D300/D500/D700 GPU board on one of the two non-CPU faces of the triangular thermal core. The enclosure, core, fan, stock 450 W PSU and the stock X-shaped retention bracket stay.
2. **Two slots [Proposal]:**
   - **Face P (primary):** PCIe up to **x16**, Gen4 (rev A). GPU slot. Has DISPLAY-LINK.
   - **Face S (secondary):** PCIe **x4** in host rev A; the cable and connector are x16-capable, and x8 is possible with a later host. Storage, NIC, capture, accelerators. Low power.
   - Both slots use the **same mechanical outline and the same connectors**, so a module that fits the power and lanes works in either (declared in the EEPROM `slot_mask`).
3. **Three host interfaces per module:**
   - **J_PCIE:** right-angle **MCIO 124** receptacle (SFF-TA-1016, 16i). Twinax cable from BP J9 (Face P) / J10 (Face S).
   - **J_AUX:** right-angle **JST GH 15-pin** receptacle. Management cable from BP J3 / J4.
   - **12 V input:** the stock PSU bus bar (primary), plus an optional PCIe 8-pin header (alternative). The stock GPU 2 board is a mirror image of GPU 1 at its 12 V screws, so the two faces' bus bars land on **opposite sides**. Every module therefore carries **two lug pairs, site A (X ≈ 97) and its mirror site B (X ≈ 7), wired in parallel**, and fits either face (§6.4.1).
   - GPU modules add **J_DISP:** right-angle **MCIO 74** receptacle (8i), with a twinax cable **directly to the I/O board (IOB)**.
4. **Rev-A defaults:** PCIe **Gen4**; Gen5 optional (needs the BP-G5 redriver build). S0/S5 only (no S3 for modules). No hot-plug. No USB4 and no 10GbE on face lanes (10GbE AQC107 goes on chipset lanes later).
5. **Non-goals for v0.1:** modules that need more than 150 W; fans on modules; display through the BP; module-to-module links.
6. **Cost rule [Proposal]:** use connectors JLCPCB/LCSC lists, standard JLC stackups and no exotic processes, so a hobbyist can order a module as JLC turnkey assembly. Prices are in §15.

## 2. System context and coordinate frame [v0.1]

![System diagram](macpro62-face/macpro62-face-v0.1-system.png)

- **Host** = CPU board (**CB**, own LGA1700 + Z790 board since 2026-10-01; the COM-HPC carrier CC is the archived fallback) + round base board (**BP**, Ø122, 6 layers). The BP is the PCIe hub. It routes **x16 to J9 (Face P)** and **x4 to J10 (Face S)**, both MCIO 124 right-angle receptacles with the SFF-TA-1016 footprint [Sourced: BP KiCad `backplane.kicad_pcb` fp4 (2026-10-02): J9 at s = +8.0 rot −60°, J10 at s = −5.0 rot +60°; see C-2 status in §13].
- **IOB** = the new rear I/O board. Planned rear ports: 2 × DP 1.4 + 1 × HDMI 2.1 from the GPU, and 4 × USB-C, 2 of them with DP alt-mode through a mux [Proposal, user brief].
- **Module frame (normative).** Origin at the bottom-left corner of the outline's bounding box, **seen from the core side**. +X runs along the bottom edge. +Y points up toward the fan. The bottom edge faces the BP.
  - **Core side = KiCad F (top) layer.** Outer side (toward the enclosure shell) = KiCad B (bottom) layer.
  - All coordinates in this document, the DXF and the KiCad template use this frame, including outer-side features, drawn see-through. A point seen from the outer side has x_outer = 104 − x.
  - The stock board scan in `bracket/gpu_board/` was traced from the **outer** (bracket) side. Asymmetric stock features (bus-bar standoffs, MEG-Array screws) are mirrored into this frame here [Inference: the scan is the back view, per `bracket/gpu_board/summary.md`]. The core GPU-face scan (`bracket/core_gpu_face/`) is consistent with this: its tab feature lands at X ≈ 100, the same side as the lug sites at X ≈ 97 (§3.3).
- **Face geometry [Sourced: spec v0.2, BP files].** The module's core-side surface sits in a plane about **55 mm from the enclosure axis** [Estimate]. The core plate surface lies **G = 4.5 ± 0.5 mm** further in, because the board rests on the core's standoff bosses [Sourced: Aidan, measured; §3.3]. Its bottom edge is about **15 mm above the BP top surface** (TO MEASURE M1b).
- **Lateral position [Inference].** The module centreline X = 52 is assumed to lie on the enclosure axis's projection (the BP draws the faces this way). The v0.2 plane-triangle model would put the face centre about 24.5 mm off-axis. That is geometrically impossible: at 55 mm from the axis the half-chord of an R 80 shell is only √(80² − 55²) = 58.1 mm. A 104 mm board therefore fits only if the offset is within **±6 mm** (core side), and within **±4.5 mm** at the outer surface. See conflict C-7 and measurement MF-3.


## 3. Mechanical (MP62-FACE-MECH 0x0001) [v0.1]

### 3.1 Outline

| Item | Value | Status |
|---|---|---|
| Size | **104.0 × 166.0 mm**, 1.6 mm reference thickness | [Sourced: Fusion `gpu_board_outline.dxf`; `bracket/gpu_board/summary.md`] |
| Bottom corners | Chamfer 17.0 (X) × 13.0 (Y), with **R10 blends** at both ends of each chamfer. Line from (3.925, 9.998) to (14.311, 2.056); flat bottom edge X 20.385–83.615 | [Sourced: Fusion DXF] |
| Top corners | R5 | [Sourced] |
| Thickness | 1.6 mm nominal (range 1.42–2.0 mm). The MCIO SMT receptacle needs ≥ 1.42 mm [v0.2 N41]. The stock board thickness is TO MEASURE (MF-12), because the screw/spring stack depends on it | [Proposal] |
| Edge band | 1.0 mm from the outline: **no components** either side. Copper ≥ 0.5 mm from the edge (template DRC) | [Proposal] |
| Outline tolerance | ±0.2 mm (JLC routing) | [Proposal] |

The outline is symmetric about X = 52, so whether the Fusion export was drawn from the core side or the outer side does not matter.

### 3.2 Mounting holes and retention

| Item | Value | Status |
|---|---|---|
| Holes | **4 × Ø5.0 mm** at **(15.0, 44.5), (89.0, 44.5), (15.0, 94.5), (89.0, 94.5)**: a 74.0 × 50.0 mm pattern centred on **(52.0, 69.5)** | [Sourced: Fusion DXF] |
| Plating | Should be plated (Ø9.0 pad both sides) and bonded to module GND, for chassis bonding through the core. May be NPTH if the module isolates GND (declare it in the documentation). | [Proposal] |
| Stock bracket | X-shaped spring bracket on the **outer side**. Eyelets **Ø5.66** at **(±37.15, ±24.85)** about the ring centre (74.3 × 49.7), eyelet OD 8.92. Centre ring ID 25.52 / OD 34.21. Arms 4.5 mm wide at ±33.8°. Envelope 83.48 × 58.89 | [Sourced: `bracket/summary.md`, scan fit] |
| Screws | Stock 4 × T10 (923-0708, 1.2 N·m) into core standoffs 923-0690, through the bracket eyelets [Sourced: v0.2 REF-S1 p.342]. Thread, length and shoulder diameter TO MEASURE (MF-5). | |
| Fit check | The board holes are 74.0 × 50.0 and the bracket holes 74.3 × 49.7. The ±0.15 mm differences are absorbed by the Ø5.66 eyelet versus the screw (≥ 0.3 mm float, assuming an M3-class shank) [Inference]. | |
| **Core standoff bosses** | 4 raised bosses on the core GPU face, **height 4.5 ± 0.5 mm** above the copper/plate surface, OD ≈ 9 mm, screw hole ≈ Ø3.3–3.5 (M3 class?). Traced positions (module frame): (14.40, 44.66), (89.67, 44.34), (14.44, 94.45), (89.49, 94.56). That is a **75.2 × 50.0 mm** pattern, against 74.0 × 50.0 for the board holes (+1.2 mm in X, ≈ 0.6 mm per side). An M3 shank in a Ø5.0 hole has 1.0 mm radial float, so the board still fits, but the board holes **shall not** be made smaller than Ø5.0. Confirm with calipers (conflict C-13). | Height [Sourced: Aidan, measured]; positions [Sourced: core scan `bracket/core_gpu_face/`, ±0.5 mm, scale ±0.4 %] |
| Hot-spot location | The module's **hot-spot centroid shall lie within a Ø6 mm circle (R3) around (52.0, 69.5)**. That is the centre of the bracket ring, which is the spring load point, and of the core contact area. Declared in the EEPROM (`hotspot_dx/dy`). | [Proposal] |

### 3.3 Core side (F): gap, contact zones, keep-outs and height

The core GPU face was traced from Aidan's flatbed scan (`bracket/core_gpu_face/`: calibrated against the rulers at 3.95 px/mm ≈ 100 dpi, scale ±0.4 %, features ±0.5 mm). It has a black plate carrying one **die pad** and four **45° strip pads**, plus four standoff bosses. Drawing panel (a) and the DXF layers `CORE_*` show them in the module frame.

> **Orientation [Inference, confirm with Aidan]:** the scan's top edge is the module's **bottom** edge (the BP end). Only in that orientation do the frame and flange extents match the 166 mm board, with the board sitting in the frame pocket at 1.4–2.1 mm lateral clearance. After rotation (0.58°) and registration of the boss centroid to (52.0, 69.5), the die pad centroid lands at (51.85, 69.43), within 0.2 mm of the bracket ring centre. That agreement supports the inference.

> **Mirrored faces [Sourced: Aidan, 2026-10-01; geometry Inference]:** the stock GPU 2 board is a mirror image of GPU 1 at its 12 V bus-bar screws, so the two faces have their lugs on opposite sides. The scan shows one face. Every asymmetric core-side zone traced from it (lug tongue KO-F2, core tab KO-F5, standoff rod) is therefore reserved **at both its traced position and its mirror about X = 52**. Which physical face (P or S) is the scanned one is TO MEASURE (M5b).

#### 3.3.1 Gap datum G

| Item | Value | Status |
|---|---|---|
| **G** (core-side PCB surface → core plate surface, with the board seated on the bosses) | **4.5 ± 0.5 mm** (G_min 4.0, G_max 5.0) | [Sourced: Aidan, standoff height measured] |
| **p**: protrusion of the copper pads above the black plate | Assumed **0 … 0.5 mm** until measured. Contact heights below use G − p. | **TO MEASURE D3** |
| G per core, to ±0.05 mm | Required before a die shim is machined (the shim tolerance stack is tighter than ±0.5) | **TO MEASURE** |
| Offset modules (§3.7) | Effective gap **G_eff = G + plane_offset** | [Proposal] |

#### 3.3.2 Core-side zones and rules

| ID | Zone (MP62 frame) | Rule | Status |
|---|---|---|---|
| **TZ1 / die pad** | Core die pad **23.6 × 21.7 mm**, centroid (51.85, 69.43); TZ1 = pad bbox + 1 mm = **X 39.1–64.7, Y 57.6–81.2** | **The module's main heat source (die, lid or spreader) contacts the die pad.** Stack: die/package (+ Cu shim) + TIM bondline must equal **G − p + δ**, with δ = **0.05–0.2 mm** interference so the bracket ring (behind the die, outer side) preloads the die before the board seats on the bosses. TIM: grease or phase-change, bondline 0.05–0.15 mm. Contact face flat to ≤ 0.05 mm. | [Sourced: scan]; δ [Proposal]; verify with pressure paper (Fuji Prescale LW) on P3 |
| **TZ3 / strip pads** | 4 strips, each ≈ **41 × 15 mm** at 45° (≈ 550 mm² each), centroids (28.5, 48.9), (75.2, 49.0), (28.4, 90.2), (75.1, 90.5). Ends are cut away around the bosses (copper-free radius ≈ 8.7 mm). Polygons in DXF layer `CORE_STRIP_PADS`. | **Secondary heat sources (VRAM, power stages, a bridge chip) couple to the strips through thermal pads.** Component top (+ optional Cu spreader) = **G − p − t_pad**, with compressed pad thickness t_pad **0.5–2.0 mm recommended**, 3.5 mm maximum. That puts the component/spreader top at **2.5–4.0 mm** above the PCB. Non-contact parts under a strip: **≤ 3.0 mm**. | [Sourced: scan]; t_pad [Proposal] |
| **H-CORE**: general height | Over the black plate, outside the die and strip pads | Parts **≤ 3.5 mm** (= G_min 4.0 − 0.5 mm margin). The EEPROM declares the module's actual maximum (`h_core_max`). | [Sourced: G]; margin [Proposal] |
| **H-CORE-OUT**: outside the plate | Board area outside the black plate X 7.5–95.5, Y 8.6–149.5 (the bottom strip Y 0–8.6, the side bands X 0–7.5 and 95.5–104, and the top Y 149.5–166) | Parts **≤ 1.0 mm** (provisional). The frame around the plate may stand higher than the plate. | **TO MEASURE MF-1** (frame/rim height relative to the plate) |
| **KO-F1** | **Ø11** around each mounting hole (boss OD ≈ 9 + 1 mm) | **No parts.** Plated-hole copper may touch the boss (GND bond, §3.2). Enforced by the F courtyard of the hole footprint. | [Sourced: scan]; boss OD TO MEASURE MF-5 |
| **KO-F2A / KO-F2B** | **A:** X 88–104, Y 139–166. **B (mirror):** X 0–16, Y 139–166. Each minus its two lug pads. | **Bus-bar tongue zones: no parts, on both sides of the board.** The stock bus bar comes through the core and lands on the core side of its lug site [Inference]. Face 1 uses site A and the other face uses site B (the stock GPU boards are mirrored, §6.4.1). Every module keeps **both** zones free. The lug centres lie **outside** the black plate (X 7.52–95.45); the Ø8.8 pads overlap the plate's top corners by ≤ 3.6 mm (X 92.9–95.5 at site A, X 7.5–11.1 at site B, Y 143–149.5). That is flat copper only, no height. Template rule areas. | TO MEASURE M5 / M5b |
| **KO-F5A / KO-F5B** | **A:** X 97.5–103.7, Y 122.4–138.4. **B (mirror):** X 0.3–6.5, same Y. | **No parts.** An unidentified raised tab on the scanned core face (X 98–102, Y 122.4–138.4), on the same side as lug site A: possibly a bus-bar contact or a grounding finger. The other face is presumed mirrored like the GPU boards, so the mirror zone is reserved too [Inference]. Template rule areas. | **TO MEASURE** (identity, height; is the other face mirrored?) |
| ~~KO-F3~~ | Former Ø8 at (26.4, 2.6) and (76.8, 2.5) | **Released.** The scan shows no bosses at the mirrored MEG-Array positions. Those points now fall in H-CORE-OUT (≤ 1.0 mm). | [Sourced: scan] |
| **Rod = base-board standoff screw** (outside the board) | Scanned face: X 83.9–87.5 (centre 85.7), tip at Y ≈ −23.5; visible Y −10.3…−23.5. The other face sees the mirror (X 16.5–20.1). | **Identified (Aidan, 2026-10-01; photo `bracket/core_photo/`):** one of the two long standoff screws that stick out of the core's bottom end and carry the base board at its gold holes G1/G2 (±49 mm). From the photo: shaft Ø ≈ 4.6 ± 0.6, a collar Ø ≈ 5.7 × 1.4 at the tip, and **≈ 18.4 ± 1.5 mm protrusion** beyond the core's end face. Not on the module. It sits in the J_DISP cable corridor (X 67.5–96.5) on one face and beside J_AUX on the other; route cables ≥ 3 mm clear. | [Sourced: Aidan]; dimensions [Estimate, photo]; C-15, C-16 |
| Plate notch | Rim notch at X 48.6–53.7, Y 8.1–11.5 | Inside H-CORE-OUT; no effect on v0.1. | [Sourced: scan] |

#### 3.3.3 Target heights: worked examples [Estimate]

Nominal G = 4.5 and p = 0 are used here. Recompute every stack with the measured G and p of the target core.

| Part | Typical height above PCB | Gap to the pad surface | Recommended stack |
|---|---|---|---|
| Navi 23 FCBGA, bare die (stock-type GPU module) | ≈ 2.5–2.8 mm (balls + substrate + die) | 4.5 − 2.6 + δ 0.1 = 2.0 | **Cu shim ≈ 1.9 mm** (1.4–2.4 over G 4.0–5.0) soldered or bonded to the die, with grease (0.05–0.15) on the core side. Alternatively a vapour-chamber "lid" at the same height. |
| ASM2824 / bridge-chip FCBGA (storage module) | ≈ 1.2–2.0 mm | ≈ 2.5–3.3 | Cu block of 2.0–2.5 mm plus grease, or a 1.0–1.5 mm pad directly on a 2.0 mm block |
| GDDR6 BGA (14 × 12 mm) | ≈ 1.1–1.2 mm | ≈ 3.3–3.4 to a strip | **2.0 mm Cu spreader + 1.0–1.5 mm pad** (≈ 1 K/W per package at 6 W/m·K), or a single 3.3 mm soft pad (≈ 3.3 K/W: acceptable below about 2 W per package) |
| DrMOS / SPS (5 × 6 mm, ≈ 1.0 mm) | ≈ 1.0 mm | ≈ 3.5 to a strip | **Shared Cu bar** over the row of stages (0.3–0.5 mm pad below, 0.5–1.0 mm pad above). A 3.5 mm pad alone gives ≈ 19 K/W per stage: too high. |
| Molded power inductors | 4.0–5.0 mm (common) | — | **Too tall for the core side.** Use ≤ 3.0 mm low-profile parts, or move them to the outer side. |
| Polymer caps (7343 D-case) | ≤ 2.8 mm | — | OK anywhere in H-CORE (≤ 3.5) |

**Rules**

- Every part that dissipates **> 2 W** shall sit under the die pad or a strip pad, and shall be thermally coupled to it.
- A module shall declare `hotspot_dx/dy` (§3.2) and `h_core_max` (§8). The value of `h_core_max` shall not exceed G_min + plane_offset − 0.5 mm.
- The thermal pads shall be soft enough that the full pad stack at G_min still lets the board seat on the bosses without exceeding the die preload. Recommend ≤ 30 Shore 00 at ≥ 6 W/m·K. Final values come from the P3 thermal test (§10).

### 3.4 Outer side (B): keep-outs and height

| ID | Zone | Rule | Status |
|---|---|---|---|
| **KO-B1** | Stock bracket outline **+1 mm**: polygon from `bracket/gpu_bracket_keepout.dxf` translated to (52, 69.5). Extent X 9.3–94.7, Y 39.25–100.1 | **No components.** Tented vias, tracks and silkscreen are allowed. Template rule area (footprints and pads disallowed on B.Cu). | [Sourced: bracket scan]; bracket height TO MEASURE (MF-4) |
| KO-B1 release (bracketless modules) | Whole KO-B1 | A module that does **not** fit the stock X-bracket (low-head screws straight into the bosses, no preload needed on its die-pad part, e.g. a gap pad) **may** use KO-B1 for parts within the envelope. It shall keep KO-B2 (the screw head and driver access) and state "bracketless" in its documentation. Anything that passes over a KO-B2 circle (e.g. an M.2 card) shall clear the screw head (MF-13). See C-19 | [Proposal, update 3] |
| **KO-B1v** | Ring interior Ø23.5 at (52, 69.5) | Parts **≤ 1.0 mm** (decoupling behind the die is allowed) | TBC MF-4: does the ring sit on the board, or above it? |
| **KO-B2** | Ø12 around each mounting hole | No parts: screw head, spring and driver access | [Proposal] |
| Lug screw heads | Ø10 around **each** lug site (sites A and B) | No parts | [Proposal] |
| **Connector band** | Y 0–26 across the full width | Reserved for J_PCIE, J_DISP, J_AUX and their plugs and cables (§3.5). Other parts only outside the connector keep-outs. | [Proposal] |
| **Height envelope (normative v0.1)** | Whole outer side | A part at lateral position x shall not exceed **h(x) = √(R_i² − (x − X_AX)²) − (55 + t) − 1.0 mm**, with R_i = 80 (shell inner radius) [Estimate], X_AX = 52 [Inference], t = PCB thickness. For t = 1.6 mm: **22.4 at the centre, 19.9 at x = 32/72, 14.3 at 17/87, 10.5 at 10/94, 8.5 at 7/97, 4.9 at 2/102, 3.2 at the edge.** | **TO MEASURE M1 (R_i, plane distance, X_AX)** |
| Simplified zones (always safe) | By \|x − 52\|: ≤ 20 → **19 mm**; 20–35 → **14 mm**; 35–42 → **10 mm**; 42–47 → **7 mm**; 47–52 → **3 mm** | A module that meets the zones meets the envelope. Both are shown in the drawing. | TO MEASURE |

> The envelope is a function of x only, because the shell is a straight cylinder over the module's height. Near the bottom edge the base ring/fillet (M1b) and the cable bends (§3.6) may reduce it further. Near the top, check clearance to the fan duct (MF-8).

### 3.5 Connector placement (outer side) [Proposal]

| Ref | Part | Position (MP62 frame) | Orientation | Keep-out (incl. plug) | Mated height | Envelope at the worst x |
|---|---|---|---|---|---|---|
| **J_PCIE** | MCIO 124 RA receptacle, Amphenol **G97R24332HR** (or JPC / Molex 2173463021 / TE equivalent) | Centre **X 43.5**. Mating face **Y 14.5**. Locating-peg line (footprint origin) Y 20.525 | Opening toward **−Y** (bottom edge) | X 20.5–66.5, Y 1.4–25.1 (46 wide: plug front 44.80, rear flanges 47.8 max) | **≈ 8.2 mm** (plug body 7.86 + latch 0.3; plug bottom flush with the PCB, because card centreline 3.05 = datum A to plug bottom 3.10) [Sourced: SFF-TA-1016 Table 5-4/6-3] | h(20.5) = 15.9 ✓ |
| **J_DISP** (GPU only) | MCIO 74 RA receptacle, Amphenol **G97R22332HR** (or JPC P947B0743313) | Centre **X 82.0**, mating face Y 14.5 | Opening −Y | X 67.5–96.5, Y 1.4–25.1 | ≈ 8.2 mm | h(96.5) = 8.9 ✓ (only 0.7 mm spare; MF-3) |
| **J_AUX** | JST **SM15B-GHS-TB(LF)(SN)** GH 1.25 mm 15-pin RA | Centre **(16.5, 26.5)**, pin row along Y | Opening toward **−X**; cable turns down beside the J_PCIE plug | X 7.5–20.0, Y 15.0–38.0 | ≈ 4.3 mm | h(7.5) = 8.9 ✓ |
| **J20 / J21** (site A) and **J22 / J23** (site B, mirror) | 12 V bus-bar lug sites (§6.4.1), **both fitted**, in parallel | A: **(97.26, 147.44)**, **(97.06, 159.13)**. B: **(6.74, 147.44)**, **(6.94, 159.13)** | Through-hole, screw from the outer side (only into the site in use) | Ø10 both sides plus KO-F2A/B | screw head ≈ 2–3 mm | h(97.3) = h(6.7) = 8.4 ✓ |
| **J_12V_ALT** (optional, DNP) | PCIe 8-pin RA, Molex **45586-0005** class (KiCad footprint `Molex_Mini-Fit_Jr_5569-08A2`) | Centre (52, 154), body X 43–61, Y 147.5–160.5 | Opening toward **+Y** (top edge) | body plus plug above the top edge | 12.8 mm | h(43) = 21.9 ✓; clearance above the top edge TO MEASURE MF-8 |

**Rules**

- J_PCIE and J_DISP **shall** use the positions above (±0.5 mm), because host cables are cut to fit them. J_AUX **should** use its position. A module without a display leaves J_DISP unpopulated, and its keep-out may be used for other parts within the envelope.
- **Footprints:** the SFF-TA-1016 Annex A recommended RA footprints (Table A-2, 124P: pads 0.35 × 1.40 at 0.60 pitch; rows A/B 0.575 / 3.525 behind datum Y; NPTH Ø1.10 locating holes 40.645 apart; 0.60 × 1.50 solder-pin slots 41.70 apart, at 1.775 and 4.325 from datum Y; A1/B1 18.90 from datum X; A38/B38 4.50 from datum X. Table A-1, 74P: 37 pins over 21.60, holes 24.445, slots 25.50). These are in the template library `MP62_Face.pretty`. **The side of datum Y the pad rows lie on is assumed; verify it against the Amphenol drawing before fabrication (OQ-5).**
- **BP cable landing [Sourced: BP fp5, ICD rev 2]:** with the faces at ≈ 45° / 135° (M2c, Aidan 2026-10-02) the two face boards meet at 90° and the two BP receptacles form a V; they cannot both sit at s = +8.5 (they collide at the apex, and J10 is limited by the G1 hole keep-out). BP fp5: **J9 at s = −5.2 (r_c 31.2), J10 at s = −2.0 (r_c 31.5)**. In the module frame the cables arrive at **X 57.2 (Face P)** and **X 54.0 (Face S)** against J_PCIE at X 43.5: lateral jogs of **13.7 mm and 10.5 mm**. **CR-2 is closed by the cable** (Aidan): a flat-twinax MCIO 124 assembly with a built-in lateral jog (§3.6). The module position X 43.5 stays normative.

### 3.6 Cable routing (both MCIO cables) [Inference]

- Path: BP J9/J10 plug (exits radially outward, plug rear at r ≈ 50 mm) → passes under the module's bottom edge (≥ 15 mm gap per M1; the standoff geometry suggests ≈ 23 mm, C-16) → turns 90° upward on the outer side → enters the J_PCIE plug travelling +Y.
- **Length between plug rears is only ≈ 12–20 mm with 15 mm plugs (≈ 30–60 mm in v0.1 before the fp5 check; ICD rev 2).** Commodity MCIO cables are ≥ 150 mm (typically 0.5 m), and there is no room to stow slack under the face. **Custom-length cables are needed** (or a later MECH revision moves Y_mate up, to at most 28.5 before the bracket keep-out). TO MEASURE M4; open question OQ-1.
- **Cable type (normative for hosts, ICD rev 2) [Proposal]:** MCIO 124 (16i) straight-plug ↔ straight-plug, rows crossed (SFF-9402), **85 Ω flat-ribbon twinax, 34 AWG** (Amphenol AssembleTech MCIO cable family or equal; custom lengths offered). Ribbon data [Sourced: Amphenol AssembleTech MCIO cable datasheet]: 34 AWG thickness 0.55–0.60 mm, 1.25 mm per pair, **bend radius ≥ 2.5 × ribbon thickness** (≈ 1.5 mm; 3.0 mm quoted for one layer). Design rule here: inside bend radius **≥ 3 mm per ribbon layer**, no creased folds across the twinax, ≤ 2 static bends.
- **Jog:** the assembly carries a pre-formed lateral offset of **13.7 mm (Face P) / 10.5 mm (Face S)**, ±1 mm, made by the vendor (ribbon split into ≤ 4-pair sub-ribbons in the jog zone, or skewed bends). PCIe Gen4 skew budget: intra-pair from the vendor's spec; inter-pair is not critical.
- **Space check (ICD rev 2) [Estimate]:** BP receptacle mating faces at n ≈ 43.3 / 43.6 mm (disc frame, along the face normal); plug body 8.2 mm high, so **6.8 mm clearance under the 15 mm board edge** (M1; 15.3 mm at 23.5, C-16). With an assumed **15 mm plug length** (mating face → cable exit, TBD from the plug drawing) the BP plug rear sits at n ≈ 58.3–58.6 and the module plug's cable exit at n ≈ 60.7 (outer surface 56.6 + 4.1), module Y ≈ −0.5. Free cable between plug rears: **≈ 12 mm at M1 = 15 mm, ≈ 20 mm at 23.5 mm**, with a single 90° bend of R ≈ 2.1–2.4 mm. **That is below the 3 mm bend rule and too short to absorb a 10–14 mm jog in a 20–25 mm wide ribbon.** Before ordering, M4 must confirm the plug length, M1c the edge height, and a vendor sample the jog. Mitigations, in order: shorter plugs or a BP-end side-exit plug (MCIO-124LS/RS class), BP receptacles moved inward (r_c ≥ 2 mm less, BP fp6), or a later MECH revision with Y_mate raised (≤ 28.5) to lengthen the vertical run. The envelope gives ≥ 15.9 mm across J_PCIE for the outer-side run.
- **J_DISP cable** to the IOB: 0.3–0.5 m, routed along the outer side. Path and length TO MEASURE M9.
- **Mating cycles:** MCIO is rated 250 cycles [Sourced: Amphenol]. That is fine for a module that is changed occasionally.

### 3.7 Offset modules (MXM carriers and similar)

- A module may sit its PCB **outward from the stock plane** by a declared `plane_offset` (EEPROM, 0.1 mm units), using spacers on top of the 4.5 mm core bosses and longer screws. Its outer envelope then shrinks by the same amount, and the core-side gap grows to G_eff = G + plane_offset.
- Example: an MXM 3.1 carrier with the MXM card on the core side. The carrier plane moves out by the MXM stack (≈ 4–6 mm [Estimate]). Outer envelope at the centre ≈ 16–18 mm.
- The bracket still clamps the carrier. The heat path is MXM die → core; the clamp force path must go through the MXM's own heatsink holes and spacers (§11.1).

### 3.8 Stackup and fabrication

- Template default: **JLC06161H-2116**, 6 layers, 1.6 mm, ENIG, the same stack as the BP.
- GPU modules (Navi 23 BGA, GDDR6) will need **8–10 layers** with via-in-pad. Keep the outline, holes and keep-outs, and change only the stackup.
- PCIe 85 Ω and display 100 Ω start values are in the template netclasses. Confirm them with the JLC impedance calculator.


## 4. PCIe interface: J_PCIE (MCIO 124, 16i) [v0.1]

### 4.1 One 16i connector, not 2 × 8i (resolution)

- **[Sourced]** SFF-TA-1016 Rev 1.3 defines the **74-contact** receptacle as the 8-lane ("8i") size and the **124-contact** receptacle as the 16-lane ("16i") size. Each row of the 124 carries 16 differential pairs plus two 5-contact sideband groups. Amphenol's selector lists 124 pin as "16X + sideband". Contacts 1–37 of the 124 are identical to the 74.
- **So x16 needs one 124-pin (16i) connector.** Two 8i (2 × 74) would also carry x16, but that means double the connectors, cables and footprint area, and the BP already has **one 124-pin RA receptacle per face (J9, J10)**.
- The brief's "MCIO 124-pin (8i)" is a misnomer: 124-pin is 16i. The earlier part TE **1-2381578-9** is a 124-position (16i) **vertical** receptacle, which is consistent in size. On the module it is unsuitable: vertical receptacle plus straight plug plus cable bend is ≈ 25 mm, more than the ≤ 22 mm envelope. **The module uses a right-angle 124.**
- **Face S uses the same 124 receptacle [Proposal; resolves v0.2 OD-3]:** modules are interchangeable between slots, x8 later needs no module change, and one part number serves both. Rev A wires only lanes 0–3 on the BP side (J10 x4).

### 4.2 Contact map (module end)

**Convention.** SFF-9402 assigns the host end: host TX on row B, host RX on row A, sideband set A at positions 8–12, set B at 26–30 [Sourced: SFF-9402 Rev 1.1; SFF-TA-1016 Fig. C-3]. A compliant cable **crosses the rows** (P1 B-n ↔ P2 A-n). At the **module end**, therefore, host TX arrives on **row A** and the module transmits on **row B**, and the sideband pins appear row-swapped. The tables below are **module-end**. The BP end is the same table with rows A and B exchanged. All positions not listed are **GND**.

**Lanes**

| Lane | Host TX -> module RX (module row A) | Module TX -> host RX (module row B, AC caps on module) | Used by |
|---|---|---|---|
| 0 | A2 PETp0 / A3 PETn0 | B2 PERp0 / B3 PERn0 | x1/x4/x8/x16 |
| 1 | A5 PETp1 / A6 PETn1 | B5 PERp1 / B6 PERn1 | x4/x8/x16 |
| 2 | A14 PETp2 / A15 PETn2 | B14 PERp2 / B15 PERn2 | x4/x8/x16 |
| 3 | A17 PETp3 / A18 PETn3 | B17 PERp3 / B18 PERn3 | x4/x8/x16 |
| 4 | A20 PETp4 / A21 PETn4 | B20 PERp4 / B21 PERn4 | x8/x16 |
| 5 | A23 PETp5 / A24 PETn5 | B23 PERp5 / B24 PERn5 | x8/x16 |
| 6 | A32 PETp6 / A33 PETn6 | B32 PERp6 / B33 PERn6 | x8/x16 |
| 7 | A35 PETp7 / A36 PETn7 | B35 PERp7 / B36 PERn7 | x8/x16 |
| 8 | A39 PETp8 / A40 PETn8 | B39 PERp8 / B40 PERn8 | x16 |
| 9 | A42 PETp9 / A43 PETn9 | B42 PERp9 / B43 PERn9 | x16 |
| 10 | A45 PETp10 / A46 PETn10 | B45 PERp10 / B46 PERn10 | x16 |
| 11 | A48 PETp11 / A49 PETn11 | B48 PERp11 / B49 PERn11 | x16 |
| 12 | A51 PETp12 / A52 PETn12 | B51 PERp12 / B52 PERn12 | x16 |
| 13 | A54 PETp13 / A55 PETn13 | B54 PERp13 / B55 PERn13 | x16 |
| 14 | A57 PETp14 / A58 PETn14 | B57 PERp14 / B58 PERn14 | x16 |
| 15 | A60 PETp15 / A61 PETn15 | B60 PERp15 / B61 PERn15 | x16 |

**Sideband (sets A and B)**

| Contact (module end) | Signal | Dir (module view) | Notes |
|---|---|---|---|
| A8 | PCIE_SMCLK | Bi (OD) | SFF-9402 2W-CLKA. Optional PCIe SMBus (device telemetry); NC on BP rev A; never the ID EEPROM |
| A9 | PCIE_SMDAT | Bi (OD) | SFF-9402 2W-DATAA. As above |
| A10 | GND | - | sideband ground |
| A11 | PERST0# | In | 3.3 V; = PLTRST# AND FACE_RDY from the BP |
| A12 | MCIO_PRSNT0# | Out | SFF-9402 CPRSNTA#. Module ties to GND (link/cable present) |
| B8 | CLKREQ0# | Out (OD) | SFF-9402 BP_TYPEA position. Optional; host pull-up, BP rev A ignores it (REFCLK free-running) |
| B9 | WAKE0# | Out (OD) | SFF-9402 CWAKEA#. Optional; host pull-up to 3V3_SB-side |
| B10 | GND | - | sideband ground |
| B11 | REFCLK0+ | In | 100 MHz HCSL, common clock, always on in S0 |
| B12 | REFCLK0- | In |  |
| A26 | RSVD_2WCLK1 | - | Set B 2-wire: reserved, NC |
| A27 | RSVD_2WDAT1 | - | Set B 2-wire: reserved, NC |
| A28 | GND | - |  |
| A29 | PERST1# | In | Set B: second link reset (x8x8). Not driven by BP rev A |
| A30 | MCIO_PRSNT1# | Out | Module ties to GND only if it uses set B |
| B26 | CLKREQ1# | Out (OD) | Set B, x8x8 modules only; otherwise NC |
| B27 | WAKE1# | Out (OD) | Set B; NC unless bifurcated |
| B28 | GND | - |  |
| B29 | REFCLK1+ | In | Set B: second link (x8x8). Not driven by BP rev A |
| B30 | REFCLK1- | In |  |

- **Mapping onto SFF-9402 names:**
  - REFCLK0± = REFCLKA±; PERST0# = PERSTA#; MCIO_PRSNT0# = CPRSNTA#; WAKE0# = CWAKEA#; CLKREQ0# occupies **BP_TYPEA**; PCIE_SMCLK/DAT = 2W-CLKA/DATA.
  - CLKREQ0# on BP_TYPEA is an MP62 assignment [Proposal]. Off-the-shelf SFF-9402 backplanes read BP_TYPE as a type strap, so a module **shall not** drive CLKREQ0# unless `clk_flags.bit2` is set. Hosts may ignore it: BP rev A runs REFCLK free-running.
- Full contact list: `macpro62-face/pinouts/mp62-face-v0.1_mcio124_pcie_module-end.csv`.
- **Cable requirement:**
  - Use SFF-TA-1016 straight-plug to straight-plug 124P cables with **all 32 pairs and all 20 sideband contacts wired**, crossed per Fig. C-3.
  - Many PCIe server cables wire only selected sidebands, or are "x8 + x8" splits. **Verify every cable type** (OQ-3). The BP shall also check MCIO_PRSNT0#.

### 4.3 Electrical rules [Proposal]

1. **Widths:** a module shall connect lanes contiguously from lane 0 (x1 → lane 0; x4 → 0–3; x8 → 0–7; x16 → 0–15). It shall train down to x1 and to Gen3. Lane reversal and polarity inversion are allowed by PCIe, but modules shall not need them: the host routes straight.
2. **AC coupling:** module TX (row B) gets **220 nF** (176–265 nF) 0201/0402 caps, close to the module's transmitter. Host TX is AC-coupled on the host [v0.2 §3.7].
3. **Impedance:** 85 Ω ±10 % differential (PCIe 4/5 and MCIO practice). Intra-pair skew ≤ 0.13 mm. GND reference void under the connector pads per the vendor drawing.
4. **Module loss budget** (endpoint package excluded), from v0.2 §3.6: **≤ 1.8 dB @ 8 GHz for Gen4** (≈ 3 in on JLC NP-155F). Gen5-capable modules: **≤ 4.5 dB @ 16 GHz**, and declare `pcie_gen_max = 5`. The host enables Gen5 only on a BP-G5 build (DS320PR810 redrivers); otherwise it forces Gen4.
5. **REFCLK:** 100 MHz HCSL, common-clock architecture, 85–100 Ω. SRIS is not required.
6. **PERST0#:** 3.3 V input, push-pull from the BP. The module shall not back-power it from 3V3_AUX or 12 V when off: use a back-drive-safe buffer or rely on the device's fail-safe input.
7. **Set B** (REFCLK1, PERST1#, CLKREQ1#, WAKE1#, MCIO_PRSNT1#) is reserved for **x8x8 bifurcated modules**. BP rev A does not drive set B. A module shall work with set B unconnected unless it declares `bifurcation = 1`, and then only on a host that supports it.

## 5. Management interface: J_AUX (JST GH 15-pin) [v0.1]

- **Part [Proposal]:** module **JST SM15B-GHS-TB(LF)(SN)** (RA, 1.25 mm, 1 A/contact; LCSC **C265027**, ≈ $0.87). Cable: GH 15-pin both ends, pin 1 ↔ pin 1, 26–28 AWG, ≤ 0.3 m.
- Pins 1–12 are **identical to the v0.2 GH14** so the BP logic carries over. 13–14 USB2 are now the **primary** USB2 path (SFF-9402 has no USB2 contacts). **15 = MOD_LED#** (new).

| Pin | Signal | Dir (module view) | Notes |
|---|---|---|---|
| 1 | 3V3_AUX | In (power) | From BP. <= 1.0 A per face in S0, <= 15 mA (50 mW) in S5; 2 pins x 1 A GH rating |
| 2 | 3V3_AUX | In (power) |  |
| 3 | GND | - |  |
| 4 | FACE_PRSNT# | Out | Module ties to GND |
| 5 | FACE_PWR_EN | In | 3.3 V push-pull from BP; high = module may enable its 12 V eFuse; module pull-down 100k |
| 6 | FACE_PWR_GOOD | Out (OD) | Released (high) when all module rails are good; host pull-up to 3V3_AUX |
| 7 | GND | - |  |
| 8 | FACE_SMB_CLK | In (OD) | Management SMBus, 3.3 V, 100 kHz (400 kHz optional); host 2.2k pull-ups |
| 9 | FACE_SMB_DAT | Bi (OD) | ID EEPROM 0x50, sensor 0x48, optional 0x40-0x47 / 0x20-0x27 / 0x60-0x6F |
| 10 | FACE_SMB_ALERT# | Out (OD) | SMBus alert (sensor ALERT, power monitor) |
| 11 | THERM_ALERT# | Bi (OD) | Host -> module: reduce power within 100 ms; module -> host: above T_warn |
| 12 | THERM_TRIP# | Out (OD) | Module -> host at T_crit, hardware only; latches the PSU off |
| 13 | USB2_D+ | Bi | Primary USB2 path for the face (module MCU / firmware update). Optional for modules |
| 14 | USB2_D- | Bi | 90 ohm; host provides the USB2 port (BP hub) |
| 15 | MOD_LED# | Out (OD) | Module status/activity, active low, <= 5 mA sink; BP mirrors it to the face LED |

- **I/O levels:** all signals are 3.3 V, powered from 3V3_AUX. Open-drain pull-ups are on the host side (2.2 kΩ for SMBus, 10 kΩ for the others). Module bus capacitance ≤ 50 pF.
- **Before FACE_PWR_GOOD** the module may only drive FACE_PRSNT# (strap), the SMBus devices on 3V3_AUX, FACE_SMB_ALERT# and THERM_TRIP#.
- **MOD_LED# [Proposal]:** low = module OK/active. Activity blinking is allowed. The BP maps it onto the face status LED. Blink codes: off = no module or no power; on = PG; BP-driven blink = fault or identify. *Identify* is a host function: the BP blinks its own LED, and modules with an SMBus controller may also expose an identify register (`led_caps.bit2`).

## 6. Power [v0.1]

### 6.1 Path decision: 12 V straight from the PSU [Proposal, consistent with v0.2 §5.1]

| Option | Verdict | Reason |
|---|---|---|
| **PSU → module directly via the stock bus bars** | **Chosen** | The stock PSU already feeds each GPU face through its own bus bar (2 × T8 lugs per face) [Sourced: v0.2 REF-S1 p.342]. Zero cable cost, high ampacity, no high current through the BP. |
| PSU → BP → MCIO / extra cable → module | Rejected | The BP takes only a ≤ 5 A harness (J2 Micro-Fit, fan and logic) [Sourced: v0.2 §4.4]. The MCIO carries no power contacts (0.5 A-class signal contacts). Routing 16 A (190 W) through the 6-layer controlled-impedance BP would need a new PSU harness and heavy copper. |
| Optional **PCIe 8-pin** on the module | Allowed (DNP by default) | For a non-stock PSU, a bench supply, or a missing bus bar. **Only one 12 V source per module may be connected** (no OR-ing in v0.1). |

### 6.2 Per-face budgets and power classes [Proposal]

| Class | Sustained (12 V input) | Peak (≤ 10 ms) | Face P | Face S (rev A) | Example |
|---|---|---|---|---|---|
| 0 | ≤ 3 W from 3V3_AUX only | 3.3 W | ✓ | ✓ | Sensor / test card |
| 1 | ≤ 40 W | 1.3 × | ✓ | ✓ (**slot max 40 W**) | ASM2824 + 4 × NVMe, NIC, capture |
| 2 | ≤ 75 W | 1.3 × | ✓ | Only if the host budget allows (CPU PL1 ≤ 65 W, §6.3) | Small GPU, accelerator |
| 3 | ≤ **150 W** | 1.3 × (≈ 195 W) | ✓ (**slot max 150 W**) | ✗ | Navi 23 GPU (RX 6600 TBP 132 W; RX 6600 XT 160 W needs a ≈ 7 % power limit; MXM RX 6600 ≈ 100 W) |

- **Averaging:** "sustained" is the average over any 1 s window, measured at the 12 V input. Thermally, the 60 s average shall stay ≤ sustained.
- **Face P 150 W, justified:**
  - The stock D700 drew ≈ 108–129 W per face [user data / v0.2].
  - In MP62 the other two faces carry far less than stock: CPU 35 W base / 92 W PL2 against the stock ≈ 130 W Xeon, and Face S ≤ 40 W against 129 W.
  - So the total heat into the core, ≤ 150 + 40 + 92 = **282 W**, stays well below the stock maximum of ≈ 388 W and the ~450 W rating. The aluminium core spreads heat between faces.
  - The per-face limit is therefore set by die heat flux and contact, not by core capacity. Until the P3 thermal test-module run passes, the host shall cap Face P at **130 W** (v0.2 Class 2). After that, Class 3 (150 W) is enabled [Proposal; validation required].
- **Face S 40 W, not 25 W:**
  - The reference storage module needs ≈ 35–41 W worst case: 4 × M.2 NVMe at up to ≈ 8 W each (3.3 V × 2.5 A max per M.2), plus ASM2824 ≈ 3–5 W, plus ≈ 90 % conversion.
  - 25 W would force NVMe power-state caps (PS1/PS2) that the host OS would have to enforce. 40 W costs only 15 W of PSU margin (§6.3).
  - A module may declare less (e.g. 25 W). The host budget uses the **declared** number.

### 6.3 PSU and core checks [Estimate]

| Load (sustained S0) | W | Source |
|---|---|---|
| CPU module i5-14500T at PL2 (PL1 35 W) | 92 | v0.2 §5.4 |
| CPU board regulators, NVMe | 8 | v0.2 |
| **Face P (Class 3)** | **150** | this spec |
| **Face S (Class 1)** | **40** | this spec |
| BP (MCU, 3V3_AUX × 2, SATA SSD) | 10 (+7 for BP-G5) | v0.2 |
| Fan | 10 | v0.2 (TBD) |
| IOB rev A | 40–50 | v0.2 |
| **Total** | **350–360 W** (367 W with BP-G5) | vs the **445 W ceiling** (ICD rev 2; PSU 450 W, Aidan: 445 W pushed is acceptable): **85–95 W margin** (78 W with BP-G5). With Face S at 25 W: 335–345 W. |

- **Current:** 360 W / 12.1 V = 29.8 A of the 37.2 A main [Sourced: PSU 12.1 V / 37.2 A].
- **Transients:** face peaks of 1.3 × for ≤ 10 ms add ≈ 57 W → ≈ 417 W < 445 W (28 W margin). PSU OCP and transient response are TO MEASURE (MF-11).
- **Host rule (normative for hosts):** the MCU sums the declared `p_sustained_w` of both faces with its own table and refuses FACE_PWR_EN for a module whose declared `p_sustained_w` would push the **static safe allocation** (§6.8) above **445 W**, or exceed the slot maximum (150 W Face P, 40 W Face S rev A). Above the static allocation the live power target (§6.8) governs.
- **Core heat:** Face P + Face S + CPU PL1 ≤ **225 W sustained** (282 W with the CPU at PL2) [Estimate]. This is to be validated with the thermal test module in P3.

### 6.4 12 V input connectors [Proposal]

| Input | Part | Rating | Notes |
|---|---|---|---|
| **Bus-bar lugs, site A J20 (+12V_IN) / J21 (GND) and site B J22 (+12V_IN) / J23 (GND)** | No part: four PTH lug pads (two mirrored pairs, §6.4.1), **Ø3.2 drill, Ø8.8 pad both sides**, 8 × Ø0.5 stitching vias, ≥ 2 oz outer copper recommended. Stock screws T8 **923-0716**, 1.2 N·m [Sourced: v0.2]. | Design **≥ 15 A per lug** (12.5 A at 150 W). Contact ampacity of the stock bus bar TO MEASURE (M5). | Site A (97.26, 147.44) / (97.06, 159.13) are the stock STANDOFF_1/2 from the board scan, mirrored into core view [Inference]. Site B (6.74, 147.44) / (6.94, 159.13) is their mirror about X = 52. **Polarity, thread and the exact positions are TO MEASURE (M5).** If the stock lug needs a threaded insert, use Würth REDCUBE **7466003R** (M3, SMT, 50 A, 5 mm high; not stocked at LCSC) on the **outer side only**: the core side at the lug sites is outside the black plate (≤ 1.0 mm, KO-F2A/B). |
| **J_12V_ALT** (optional) | **Molex 45586-0005**, PCIe 8-pin RA, Mini-Fit Jr (not stocked at LCSC; JLC global sourcing). Face S may use the 6-pin **Molex 45558-0003** (LCSC C7545781, ≈ $1.07). | 8-pin: 150 W per PCIe CEM (3 × 12 V contacts, 9 A/contact Mini-Fit Jr rating). 6-pin: 75 W. | Pins 1–3 +12V, 5/7/8 GND, 4/6 SENSE. Use only when the bus bar is not connected (`v12_src_mask`). |

#### 6.4.1 Lug sites on mirrored faces: one universal module [Proposal]

Aidan reports that the stock GPU 2 board is a mirror image of GPU 1 at its 12 V power-input screws, so the bus bar of one face lands at site A (X ≈ 97, core view) and that of the other face at site B (X ≈ 7). There are two ways to handle this:

| Option | For | Against | Verdict |
|---|---|---|---|
| **(1) Per-face lug zone:** a Face P module carries only its face's site, a Face S module only the mirror site | Saves ≈ 16 × 27 mm of board corner; no idle live copper | Two board variants of every carrier; a module is locked to one face. A module fitted to the wrong face leaves its bus-bar tongue pressing on bare board or parts, so a 12 V short is possible. **We do not yet know which face (P or S) uses which site (M5b)**, so a single-site module cannot be laid out correctly today. | Not allowed in v0.1 |
| **(2) Universal: both sites on every module**, wired in parallel | One layout fits either face, so the module needs no variant and no face-specific BOM. It doesn't depend on M5b or OD-6 (Face P assignment). The `slot_mask` stays a power/lane decision, not a mechanical one. Cost is small: the site B corner (X 0–16, Y 139–166) lies in H-CORE-OUT (≤ 1.0 mm on the core side) and in the 3–8 mm outer height zone, where few parts fit anyway. | One corner of board area lost; the idle site is live at 12 V; up to ≈ 50 mm of extra 12 V copper | **Chosen (normative v0.1)** |

**Rules (v0.1):**

- Every module **shall** carry both lug pairs: **site A** J20 (+12V_IN) at (97.26, 147.44) and J21 (GND) at (97.06, 159.13); **site B** J22 (+12V_IN) at (6.74, 147.44) and J23 (GND) at (6.94, 159.13). All four are Ø3.2 drill / Ø8.8 pad on both sides with 8 stitching vias.
- KO-F2A, KO-F2B, KO-F5A and KO-F5B **shall** stay free of parts on the core side. The Ø10 screw-head keep-outs on the outer side **shall** stay free at both sites.
- Sites A and B **shall** be wired in parallel ahead of the eFuse: J20 to J22 (+12V_IN) and J21 to J23 (GND). Only one bus bar lands on a module, so only one site carries current. Each site-to-eFuse path must carry ≥ 15 A.
  - Put the eFuse near the top centre (about X 40–64, Y 125–145) so that neither path is longer than ≈ 50 mm.
  - Example: ≥ 10 mm wide pours on two 2 oz layers. A 50 mm path is ≈ 0.6 mΩ per polarity, so the round trip drops ≈ 15 mV at 12.5 A [Estimate].
  - The KiCad template draws reference tracks: In1 for +12V_IN at Y 140, In4 for GND at Y 163.4. Replace them with pours.
- **The idle site is live** (12 V and GND pads exposed on both sides).
  - Do not use it as a test point.
  - Keep ≥ 0.5 mm copper-to-edge clearance; the site B pads come 2.3 mm from the left edge, the same as site A on the right.
  - If MF-1 finds a core feature within 1.0 mm of the board at the idle site, cover that site's core-side pads with polyimide tape (Kapton, 0.06 mm) on that face [Proposal].
- **Polarity:** a mirror image in X keeps the Y order, so the template assumes +12V_IN at the lower lug (Y 147.4) of both sites [Inference]. **The polarity of each face is TO MEASURE (M5).**
  - If the faces turn out to differ, only the net names at site B swap; the geometry stays the same.
  - The reverse-polarity rule (§6.5) protects a module built on a wrong guess.
- **Screws:** stock 2 × T8 923-0716 go into the site in use only.
- Single-site modules may be allowed in MECH 0x0002, once M5b says which face uses which site. Such a module would then set `slot_mask` to that face only.

### 6.5 Input protection, inrush, capacitance [Proposal]

- Every module drawing more than 3 W **shall** gate 12 V with an on-module **eFuse / hot-swap switch** enabled by **FACE_PWR_EN**. The bus bar is live whenever the PSU is on, and the host does not switch it.
  - Reference part: **TI TPS25982** (2.7–24 V, 15 A, integrated FET, adjustable I_LIM and dV/dt; LCSC **C2155766** TPS259824ONRGER ≈ $5.90; LNR variant C2155879 ≈ $4.34 with low stock).
  - For Face P, set I_LIM ≈ 1.3–1.5 × the class (≤ 16 A); for Face S, ≈ 5 A.
- **Capacitance ahead of the eFuse:** ≤ 47 µF (it is charged at PSU turn-on).
- **Inrush after EN:** ≤ 3 A (Face P) / ≤ 1 A (Face S), with dV/dt-limited soft-start. Declared in `inrush_da`.
- **Reverse polarity:** the module **shall survive** reversed lug polarity without damage, for example with an eFuse with blocking or a series ideal-diode controller. The stock lug polarity is still unmeasured, per face (§6.4.1). A polarity-agnostic input (ideal-diode bridge controller, LT4320-class, with 4 FETs) is optional [Proposal].
- **Overvoltage:** the module shall tolerate 10.8–13.2 V and survive 15 V.

### 6.6 3V3_AUX [Sourced: v0.2 §4.4, §7.8]

- Supplied by the BP over AUX pins 1–2: from 3V3_SB in S5, from 3V3_BP in S0.
- Limits: **≤ 1.0 A (3.3 W) in S0**; **≤ 15 mA / 50 mW in S5**.
- The ID EEPROM, temperature sensor and presence logic **shall** run on 3V3_AUX alone. Nothing on 3V3_AUX may back-feed the main rails.

### 6.7 Sequencing (power-button independent) [Proposal]

Modules never see the power button. The BP MCU and PCH handle it. A module reacts only to **3V3_AUX, FACE_PWR_EN and PERST0#**. See the timing diagram in `macpro62-face-v0.1-system.png`.

| Step | Event | Owner | Requirement |
|---|---|---|---|
| 1 | AC on → 3V3_AUX (S5 level) | BP | The module draws ≤ 50 mW and answers on SMBus within 50 ms (EEPROM 0x50, sensor 0x48). |
| 2 | BP reads and validates the EEPROM: magic, CRC, class, slot, budget | BP MCU | Invalid or missing EEPROM → FACE_PWR_EN stays low (dev-mode override on the BP only). |
| 3 | Power-on request → PSU on (PS_ON#) → 12 V present at the lugs | BP / PSU | The module tolerates 12 V without EN, drawing only the eFuse quiescent current. |
| 4 | BP raises **FACE_PWR_EN** (after PWR_OK) | BP | — |
| 5 | Module soft-starts and releases **FACE_PWR_GOOD** | Module | **≤ 150 ms** after EN (`t_pg_ms`). Drive no PCIe, display, USB or sideband signal before PG. |
| 6 | REFCLK0 running, stable for ≥ 100 µs | BP | — |
| 7 | **PERST0# deasserted ≥ 100 ms after PG** (T_PVPERL), as PLTRST# ∧ FACE_RDY | BP | The module's PCIe device starts link training. |
| 8 | Shutdown / S5: **PERST0# asserted first**, then FACE_PWR_EN low after ≥ 1 ms | BP | The module drops PG and turns off its rails within **10 ms**. 12 V may stay present (the PSU turns off later). |
| 9 | **Faults:** PG falling in S0; FACE_PRSNT# or MCIO_PRSNT0# changing; THERM_TRIP# | BP / hardware | PG loss → the BP asserts PERST0#, drops EN and logs FAULT; at most one retry after 1 s. THERM_TRIP# latches the PSU off in hardware. |

**Not supported in v0.1:** S3 (suspend-to-RAM) with modules powered, D3cold / L2 wake from 3V3_AUX, and hot-plug.

### 6.8 Live power target (module side) [Proposal, ICD rev 2]

The host (BP MCU with the CB EC) keeps the 12 V total ≤ **445 W** by setting a power target per consumer every 100 ms from predicted need (architecture spec §5.5, ICD §13.2). Module requirements:

| Item | Requirement |
|---|---|
| 12 V monitor | Every module drawing > 3 W **shall** carry a TI **INA228** (or register-compatible INA238) at **0x40** on FACE_SMB (A0 = A1 = GND), with a Kelvin shunt in the 12 V path (Face P: 1 mΩ; ≤ 5 A modules: 2 mΩ, 2512). VS from 3V3_AUX. Reference placement: template RS1/U5 (outer side, eFuse zone). |
| Alert | INA228 ALERT (open drain) **shall** be wired-OR onto FACE_SMB_ALERT# (with the eFuse FLT#). The host programs the power-limit register to the allocation + 10 % and the bus-overvoltage/undervoltage limits. |
| Power-target agent (modules with a management MCU) | SMBus target at **0x58**: register 0x00 `p_target_w` (u8, host → module), 0x01 `p_now_w` (u8), 0x02 `p_request_w` (u8, module's predicted need for the next 1 s), 0x03 `flags` (bit0 target applied, bit1 cannot meet target). The module **shall** settle below `p_target_w` within **100 ms** (GPU: power cap / DC-mode or PWR_LEVEL input; clocks follow). A heartbeat loss of > 1 s from the host → the module falls back to its declared `p_sustained_w`. |
| Modules without an MCU (SM-1) | Telemetry only (INA228). The host enforces the target through the OS (NVMe power-state limit via the macOS helper, C-21) and THERM_ALERT#. |
| Fast cap | THERM_ALERT# asserted by the host = **"cut ≥ 25 % within 100 ms"** (§10), also used by the power loop when the 12 V total crosses 445 W. |

## 7. Sideband summary [v0.1]

| Function | Signal(s) | Path | Rev-A host behaviour | Module requirement |
|---|---|---|---|---|
| Reference clock | REFCLK0± (REFCLK1± set B) | MCIO | Free-running 100 MHz HCSL in S0 | Shall use REFCLK0 (common clock) |
| Reset | PERST0# (PERST1#) | MCIO | PLTRST# ∧ FACE_RDY | Shall honour |
| Clock request | CLKREQ0# (BP_TYPE position) | MCIO | Pulled up, ignored | May drive only if `clk_flags.bit2` |
| Wake | WAKE0# | MCIO | Pull-up; ORed into WAKE0# on the BP | Optional (rev A has no S3) |
| Presence | FACE_PRSNT# (AUX), MCIO_PRSNT0# (MCIO), DLINK_PRSNT# (DISPLAY-LINK, to the IOB) | AUX / MCIO / display cable | Mismatch = FAULT (cable missing) | Shall tie to GND |
| Power control | FACE_PWR_EN, FACE_PWR_GOOD | AUX | §6.7 | Shall implement |
| Management | FACE_SMB_CLK/DAT/ALERT# | AUX | One segment per face, BP MCU master, 100 kHz | EEPROM 0x50 + sensor 0x48 mandatory; INA228 0x40 mandatory > 3 W; power-target agent 0x58 if an MCU (§6.8) |
| Device SMBus | PCIE_SMCLK/DAT | MCIO | NC in rev A | Optional; never the ID EEPROM |
| Thermal | THERM_ALERT# (bidirectional), THERM_TRIP# | AUX | Fan curve from the sensors; THERM_TRIP# latches the PSU off | Shall implement |
| Fan | — | — | **Host-owned** (BP fan control) | No fans on modules |
| LED | MOD_LED# | AUX | Mirrored to the face status LED | Should drive |
| USB2 | USB2_D± | AUX | BP USB2 hub port per face (TBD on the BP) | Optional (firmware update, MCU) |
| Display | DISPLAY-LINK | Separate cable to the IOB | — | §9 |


## 8. ID EEPROM and thermal sensor [v0.1]

### 8.1 Hardware

| Item | Rule | Part (LCSC) | Status |
|---|---|---|---|
| EEPROM | **24C64 class** (≥ 24C32; **16-bit word addressing is required**, so a 24C02/24C16 is not allowed) at **7-bit address 0x50** on the AUX SMBus (3V3_AUX domain). Readable in S5. | **BL24C64A-SFRC**, C111004, ≈ $0.19 | [Proposal] |
| Write protect | WP **shall** be strapped high (protected) on production modules, with a 0 Ω/jumper to unprotect for programming. `flags.bit3` declares it. | — | [Proposal] |
| Temperature sensor | LM75/TMP75 register-compatible at **0x48** (`sensor_addr`), placed at the hot zone (within 10 mm of the die-pad footprint or the hottest strip-pad part). ALERT output in comparator mode drives **THERM_ALERT#** (AUX). | **TMP1075DSGR**, C2870250, ≈ $0.50 | [Proposal] |
| Other SMBus devices | Allowed at 0x51–0x57 and 0x49–0x4F only. 0x50 and 0x48 are reserved for the items above. **ICD rev 2:** 0x40 = 12 V power monitor (INA228, mandatory > 3 W, §6.8), 0x41–0x47 extra power monitors, **0x58 = power-target agent** (§6.8). | — | [Proposal] |

### 8.2 Memory map

| EEPROM offset | Content |
|---|---|
| **0x0000** | **MP62 Module Descriptor v1** (§8.3), ≤ 512 B, CRC-protected. **Required.** |
| 0x0100 | Optional IPMI FRU (Platform Management FRU v1.0), for tools that expect one. It is informative only; the host uses the MP62 descriptor. (A descriptor longer than 256 B moves this to 0x0200.) |
| 0x0400 – end | Vendor area (calibration, VBIOS settings, logs). |

### 8.3 MP62 Module Descriptor v1 (little-endian)

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0x00 | 4 | `magic` | ASCII "MP62" (4D 50 36 32) |
| 0x04 | 1 | `desc_ver` | Descriptor format version = 0x01 |
| 0x05 | 1 | `spec_ver` | MP62-FACE spec version, BCD major.minor (0x01 = v0.1) |
| 0x06 | 2 | `length` | Total descriptor length L in bytes, including the CRC (<= 512) |
| 0x08 | 2 | `mech_rev` | MP62-FACE-MECH revision the module complies with (0x0001 = v0.1 outline/keep-outs) |
| 0x0A | 1 | `vid_space` | Vendor-ID namespace: 0 = development/unassigned, 1 = PCI-SIG VID, 2 = MP62 community registry |
| 0x0B | 1 | `rsvd0` | Reserved, 0 |
| 0x0C | 2 | `vendor_id` | Vendor ID in that namespace |
| 0x0E | 2 | `product_id` | Product ID (vendor assigned) |
| 0x10 | 1 | `hw_rev` | Hardware revision (vendor assigned) |
| 0x11 | 1 | `module_type` | 1 GPU, 2 storage, 3 NIC, 4 accelerator/FPGA, 5 capture, 6 adapter/bench, 7 thermal test, 0xFE other (0 invalid) |
| 0x12 | 1 | `slot_mask` | bit0 Face P allowed, bit1 Face S allowed |
| 0x13 | 1 | `pcie_width_max` | Max link width: 1/2/4/8/16 |
| 0x14 | 1 | `pcie_width_min` | Min width at which the module is still functional (usually 1) |
| 0x15 | 1 | `pcie_gen_max` | Max PCIe generation: 3/4/5 |
| 0x16 | 1 | `bifurcation` | 0 single link, 1 x8x8 (uses sideband set B), 2 x8x4x4, 3 x4x4x4x4 (rev-A hosts: 0 only) |
| 0x17 | 1 | `clk_flags` | bit0 needs REFCLK0, bit1 needs REFCLK1, bit2 drives CLKREQ#, bit3 SRIS capable, bit4 drives WAKE# |
| 0x18 | 1 | `power_class` | Power class 0-3 (section 6.2) |
| 0x19 | 1 | `v12_src_mask` | 12 V inputs fitted: bit0 bus-bar lugs (sites A+B, both mandatory in v0.1), bit1 PCIe 8-pin, bit2 PCIe 6-pin |
| 0x1A | 2 | `p_sustained_w` | Sustained 12 V input power, W |
| 0x1C | 2 | `p_peak_w` | Peak 12 V input power (<= 10 ms), W |
| 0x1E | 2 | `aux_s0_ma` | Max 3V3_AUX current in S0, mA (<= 1000) |
| 0x20 | 2 | `aux_s5_mw` | Max 3V3_AUX power in S5, mW (<= 50) |
| 0x22 | 1 | `t_pg_ms` | Max FACE_PWR_EN -> FACE_PWR_GOOD time, ms (<= 150) |
| 0x23 | 1 | `inrush_da` | Peak 12 V inrush after FACE_PWR_EN, units of 0.1 A |
| 0x24 | 1 | `t_target_c` | Fan-curve knee temperature, deg C (sensor reading) |
| 0x25 | 1 | `t_warn_c` | Warning temperature (module asserts THERM_ALERT#), deg C |
| 0x26 | 1 | `t_crit_c` | Critical temperature (module asserts THERM_TRIP#), deg C |
| 0x27 | 1 | `sensor_addr` | 7-bit address of the LM75-compatible sensor (0x48) |
| 0x28 | 1 | `hotspot_dx` | Hot-spot centroid offset from (52.0, 69.5), X, units 0.5 mm (|value| <= 6) |
| 0x29 | 1 | `hotspot_dy` | Hot-spot centroid offset, Y, units 0.5 mm (|value| <= 6) |
| 0x2A | 1 | `plane_offset` | Module PCB plane offset outward from the stock plane, units 0.1 mm (0 = stock; MXM carriers > 0) |
| 0x2B | 1 | `h_outer_max` | Tallest outer-side part used, units 0.1 mm |
| 0x2C | 1 | `h_core_max` | Tallest core-side part outside the die/strip contact stacks, units 0.1 mm (<= G_min + plane_offset - 0.5 = 3.5 mm for plane_offset 0) |
| 0x2D | 1 | `disp_count` | Number of display links on DISPLAY-LINK (0-5) |
| 0x2E | 1 | `disp_flags` | bit0 DISPLAY-LINK connector fitted, bit1 link3 is 4-lane (link4 absent), bit2 UEFI GOP boot display, bit3 HDMI FRL capable |
| 0x2F | 1 | `led_caps` | bit0 drives MOD_LED#, bit1 activity blink on MOD_LED#, bit2 SMBus identify register |
| 0x30 | 1 | `flags` | bit0 uses USB2 (AUX), bit1 requires THERM_ALERT# host support, bit2 pre-production/dev, bit3 EEPROM WP strapped, bit4 uses PCIe 2-wire bus |
| 0x31 | 3 | `rsvd1` | Reserved, 0 |
| 0x34 | 20 | `disp_links` | 5 x 4-byte display-link descriptors (link 0..4): type, lanes, max rate, flags (section 9.4) |
| 0x48 | 1 | `n_pci_ids` | Number N of PCI VID:DID entries (0-8) |
| 0x49 | 3 | `rsvd2` | Reserved, 0 |
| 0x4C | 4 x N | PCI IDs | N x (u16 VID, u16 DID), little-endian |
| ... | var | strings | 5 strings, each u8 length + ASCII: vendor name (<= 32), product name (<= 32), part number (<= 24), serial (<= 24), build date YYYYMMDD |
| L-2 | 2 | `crc16` | CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF, no reflection, xorout 0) over bytes 0 .. L-3 |

### 8.4 Host behaviour and validation

1. The host reads the descriptor in S5 (from 3V3_AUX), **before** asserting FACE_PWR_EN.
2. The host **shall refuse power** (it keeps FACE_PWR_EN low and blinks the slot LED) if any of these hold:
   - bad magic, length or CRC
   - `mech_rev` unknown
   - the slot bit is not set in `slot_mask`
   - `p_sustained_w` is above the slot budget (§6.2: Face P 150 W, or 130 W until P3 thermal validation; Face S 40 W)
   - `v12_src_mask` is 0
   - `aux_s5_mw` > 50 or `aux_s0_ma` > 1000
   - `t_pg_ms` > 150
   - `hotspot_dx/dy` outside R3
   - `h_core_max` > 35 + `plane_offset` (in 0.1 mm units: G_min + offset − 0.5)
3. A missing or blank EEPROM gives **Class 0 only** (3V3_AUX, no 12 V).
4. Reference implementation: `macpro62-face/tools/mp62_eeprom.py` (encoder, `check` validator, CRC-16/CCITT-FALSE). Examples are in `eeprom_examples/`:
   - `example_mxm_rx6600.bin`: 164 B, GPU, Face P, x8 Gen4, 110 W, 4 display links, plane_offset 5.0 mm.
   - `example_storage_asm2824.bin`: 159 B, storage, Face P or S, 40 W.
   Both pass `check`.
5. **Vendor IDs:** `vid_space` 0 is for development. A community registry (`vid_space` 2) is an open question (§14).

## 9. Display path (DISPLAY-LINK) [v0.1]

### 9.1 Decision [Proposal]

**DISPLAY-LINK is a second right-angle MCIO receptacle on the module, the 74-pin (8i) size: Amphenol G97R22332HR (LCSC C5433520, $7.94 @1 / $6.88 @10, stock 4).** A commodity **MCIO 8i twinax cable** (straight, 0.3–0.5 m; ≈ $46–52 retail for 0.5 m) runs straight from the module to the IOB. Display signals never pass through the BP.

Why this option:
- The connector family and 85/100 Ω twinax are already used for PCIe, so there is one footprint family, one cable vendor, and one assembly process.
- 16 differential pairs at ≥ 16 Gb/s (MCIO is rated to PCIe Gen5/6), which is enough for HBR3 and HDMI 2.1 FRL 12G.
- Plenty of sideband pins for AUX/HPD of 5 links.
- JLC can assemble it, and the low-profile RA part fits the outer envelope (8.2 mm mated; h(96.5) = 8.9).

### 9.2 Alternatives considered

| Option | For | Against | Verdict |
|---|---|---|---|
| **MCIO 74 RA + MCIO 8i cable (chosen)** | Same family as J_PCIE. Commodity cables. 16 pairs + sidebands. | LCSC stock is low (4). Cables cost ≈ $46–52. | **Chosen** |
| SlimSAS 8i (SFF-8654) RA, e.g. Amphenol U10A474240T | Cheaper cables (≈ $20); very common | Not at LCSC. Lower rated speed (12 Gb/s SAS). Taller. | Allowed as a v0.2 option |
| Custom flex / FPC | Thin and cheap at volume | Needs a custom design per path. 100 Ω control over 0.3–0.5 m is marginal at HBR3/FRL. Fragile. | Rejected |
| eDP-style micro-coax (I-PEX 40-pin class) | Thin, laptop-proven | ≤ 4 lanes per cable, so 2–3 cables are needed. Hand-terminated. | Rejected |
| Through the BP (spare MCIO pairs) | No extra cable | Puts display on the PCIe cable. Long path BP → CPU board → IOB. Needs BP changes and redrivers. | Rejected (non-goal, §1) |

### 9.3 Pinout (module end; IOB end row-swapped by the straight cable)

Main pairs (100 Ω, AC-coupled **on the module**):

| Pair | Module row B contacts | Signal | Module row A contacts | Signal |
|---|---|---|---|---|
| 0 | B2 / B3 | ML0p_0 / ML0n_0 | A2 / A3 | ML2p_0 / ML2n_0 |
| 1 | B5 / B6 | ML0p_1 / ML0n_1 | A5 / A6 | ML2p_1 / ML2n_1 |
| 2 | B14 / B15 | ML0p_2 / ML0n_2 | A14 / A15 | ML2p_2 / ML2n_2 |
| 3 | B17 / B18 | ML0p_3 / ML0n_3 | A17 / A18 | ML2p_3 / ML2n_3 |
| 4 | B20 / B21 | ML1p_0 / ML1n_0 | A20 / A21 | ML3p_0 / ML3n_0 |
| 5 | B23 / B24 | ML1p_1 / ML1n_1 | A23 / A24 | ML3p_1 / ML3n_1 |
| 6 | B32 / B33 | ML1p_2 / ML1n_2 | A32 / A33 | ML4p_0 / ML4n_0 |
| 7 | B35 / B36 | ML1p_3 / ML1n_3 | A35 / A36 | ML4p_1 / ML4n_1 |

Sideband (AUX ±, HPD, presence):

| Contact (module end) | Signal | Dir (module view) | Notes |
|---|---|---|---|
| A8 | AUX2+/DDC_SCL | Bi | Link 2: DP AUX+, or HDMI DDC SCL (DP++ convention) |
| A9 | AUX2-/DDC_SDA | Bi | Link 2: DP AUX-, or HDMI DDC SDA |
| A10 | GND | - |  |
| A11 | HPD0 | In | 3.3 V hot-plug detect from IOB (IOB buffers 5 V-tolerant) |
| A12 | HPD1 | In |  |
| B8 | AUX0+ | Bi | DP AUX link 0 (100 nF AC + source bias on module) |
| B9 | AUX0- | Bi |  |
| B10 | GND | - |  |
| B11 | AUX1+ | Bi | DP AUX link 1 |
| B12 | AUX1- | Bi |  |
| A26 | HPD2 | In |  |
| A27 | HPD3 | In |  |
| A28 | GND | - |  |
| A29 | HPD4 | In |  |
| A30 | DLINK_PRSNT# | Out | Module ties to GND; IOB detects the display cable |
| B26 | AUX3+ | Bi | DP AUX link 3 (to IOB PD/alt-mode controller path) |
| B27 | AUX3- | Bi |  |
| B28 | GND | - |  |
| B29 | AUX4+ | Bi | DP AUX link 4 |
| B30 | AUX4- | Bi |  |

- **Link 0** = DP 1.4 4-lane (rear DP #1). **Link 1** = DP 1.4 4-lane (rear DP #2).
- **Link 2** = HDMI 2.1 / DP++ 4-lane (rear HDMI, through the IOB retimer). Its AUX pins carry DDC under the DP++ convention.
- **Link 3** and **Link 4** = DP alt-mode 2-lane each (USB-C #1/#2, through the IOB mux). If `disp_flags.bit1` is set, Link 3 is 4-lane and Link 4 is absent.
- **DLINK_PRSNT#** (A30): the module ties it to GND, so the IOB can detect the cable.
- Full contact list: `pinouts/mp62-face-v0.1_mcio74_displaylink_module-end.csv`.
- Navi 23 has 5 display PHYs (DCN 3.0.2), so all 5 links can be driven [Sourced: Linux amdgpu `dcn302`]. Many MXM cards route fewer (`disp_count`).

### 9.4 Display-link descriptor (EEPROM 0x34, 5 × 4 bytes)

| Byte | Meaning | Codes |
|---|---|---|
| 0 | type | 0 none, 1 DP, 2 DP++ (dual-mode), 3 HDMI TMDS, 4 HDMI FRL, 5 DP alt-mode (USB-C) |
| 1 | lanes | 1, 2, 4 |
| 2 | max rate | DP: 1 RBR, 2 HBR, 3 HBR2, 4 HBR3, 5 UHBR10, 6 UHBR13.5, 7 UHBR20. HDMI: 0x10 TMDS 3.4G, 0x11 TMDS 6G, 0x12 FRL 3×3, 0x13 FRL 3×6, 0x14 FRL 4×6, 0x15 FRL 4×8, 0x16 FRL 4×10, 0x17 FRL 4×12 |
| 3 | flags | bit0 HPD wired, bit1 AUX/DDC wired, bit2 lane-polarity swap used, bit3 boot (GOP) display candidate |

### 9.5 Electrical rules

- 100 Ω ±10 % differential. AC caps (DP 75–200 nF) on the module, within 10 mm of the connector or the source.
- Module routing from the GPU to J_DISP **≤ 100 mm** [Estimate], with intra-pair skew ≤ 0.15 mm.
- AUX: 100 nF series caps and the source bias (DP 1.4) on the module.
- HPD: an input to the module at 3.3 V; the IOB level-shifts and buffers from 5 V-tolerant connectors.
- **No DP_PWR, no 5 V** on the cable; the IOB generates DP_PWR and HDMI 5 V.

### 9.6 IOB side (informative, host-side spec)

> **IOB rev A0 (2026-10-01):**
> - Links 0–4 are used: link 0 → C1 (4-lane), link 1 → C2 (4-lane), link 2 → HDMI via TDP158 (DP++ to TMDS, HDMI 2.0 class), link 3 → C3 (2-lane), link 4 → C4 (2-lane).
> - The TUSB1046A mux plus TPS65994AD PD handle USB-C. HPD0/1 come from PD #1, HPD3/4 from PD #2, HPD2 from the TDP158.
> - See `/workspace/macpro62-io-board-plan.md` §5.2.
> - **IOB-end contact table (2026-10-02, ICD):** `kicad/macpro62-io-board/docs/mp62-iob-j2_mcio74_displaylink_iob-end.csv` = §9.3 with rows A/B exchanged; IOB J2 is wired to it.

- HDMI 2.1 retimer on Link 2 (TI TDP2004-class [Unverified]); ESD on every port.
- DP_PWR and HDMI 5 V with current limit.
- USB-C: a DP alt-mode mux (TUSB1046-class) + PD controller, which takes Link 3/4 and the USB data.
- **Source selection** between the iGPU and the face GPU (architecture spec OD-2) stays an open host decision. DISPLAY-LINK does not depend on it.
- The IOB connector footprint is the same MCIO 74 RA. Row A on the module meets row B on the IOB (straight cable, SFF-9402 convention). Lay out the IOB from the row-swapped CSV.

## 10. Thermal [v0.1]

| Item | Rule | Status |
|---|---|---|
| Heat path | All module heat goes into the core through the **die pad** (main source) and the **4 strip pads** (secondary, §3.3). No module fans (§1). | [Sourced: scan]; [Proposal] |
| Hot spot | Centroid within **R3 of (52.0, 69.5)**. That is the die-pad centre (scan: 51.85, 69.43) and the bracket ring/spring load point. Declared as `hotspot_dx/dy`. | [Proposal] |
| TIM | Die pad: grease or phase-change, bondline 0.05–0.15 mm, preload from interference δ = 0.05–0.2 mm (§3.3.2). Strip pads: soft thermal pads ≥ 6 W/m·K, compressed thickness 0.5–2.0 mm. | [Proposal] |
| Dissipation rule | Every part dissipating > 2 W sits under a pad (§3.3.3). **Exception (C-20):** removable, self-throttling devices in standard sockets on the outer side (M.2 NVMe SSDs) may be air-cooled in the board-to-shell gap, optionally with heatsinks within h(x); airflow there is TO MEASURE (MF-14). | [Proposal] |
| Sensor | TMP1075 at 0x48, at the hot zone. The host reads it every ≤ 1 s and maps it onto the fan curve with the `t_target_c` knee. | [Proposal] |
| Limits | `t_target_c` (fan knee), `t_warn_c` (module asserts THERM_ALERT#), `t_crit_c` (module asserts THERM_TRIP#, the host drops FACE_PWR_EN within 100 ms). Defaults for a GPU: 70 / 90 / 100 °C. Storage: 55 / 70 / 85 °C. | [Proposal] |
| Throttle | When THERM_ALERT# is asserted, the module **shall** cut its own power by ≥ 25 % within **100 ms** (GPU power cap, or NVMe power state). The host raises the fan to 100 %. **Storage modules without a management MCU (C-21):** the host OS/firmware applies the NVMe power-state limit (and the SSDs throttle themselves); the module only reports through THERM_ALERT#/THERM_TRIP#. | [Proposal] |
| Power cap | Face P is capped at **130 W** until the P3 thermal test passes; then **150 W**. Face S: 40 W. Inside these caps the host's live power target (§6.8) may set a lower `p_target_w` at any time. | [Proposal] |
| P3 thermal test module | A module_type 7 board: resistive heaters on the die-pad footprint (≈ 24 × 22 mm) and on the four strip footprints, 0–150 W programmable, with 6 thermistors. Measures the core ΔT/W and the pad stack, and checks the pressure paper. Gate for raising the 130 W cap. | [Proposal] |

## 11. Reference modules (informative) [v0.1]

### 11.1 MXM 3.1 carrier (Face P): X-VSION RX 6600 (Navi 23) MXM

- The carrier PCB holds J_PCIE, J_DISP, J_AUX, the lug sites, eFuse, EEPROM and sensor. The MXM 3.1 Type-B card sits on the **core side** of the carrier, die facing the core.
- `plane_offset` ≈ 4–6 mm [Estimate], so that G_eff = 4.5 + plane_offset suits the MXM connector stack plus the card's die height. The die stack must then reach the die pad with a shim, using the §3.3.2 formula with G_eff.
- **The MXM die position is TO CHECK.** The MXM die must sit within R3 of (52, 69.5) with the card placed on the carrier. If it cannot, the carrier must shift the card (MXM 82 × 105 mm fits inside the plate area).
- Clamp path: the bracket clamps the carrier; the die load goes through the MXM card's own heatsink holes, with spacers to the carrier. Strips cool the MXM VRAM/VRM through pads if their positions line up; otherwise they need a Cu spreader.
- Lanes: x8 Gen4 (Navi 23 limit). Display: up to 4 links routed out of MXM (outputs and GOP TBD per card). Power: ≈ 100–110 W class 3.
- EEPROM example: `example_mxm_rx6600.bin`.

### 11.2 Native Navi 23 module (Face P)

- Layout as on a stock D-series board: the GPU at the centre of the die pad, GDDR6 and power stages under the strips (§3.3.3), and the Cu die shim ≈ 1.9 mm (from the measured G).
- 8–10 layers. Inductors either ≤ 3.0 mm on the core side or placed on the outer side within h(x).
- Lanes x8 Gen4. 5 display links. 130/150 W.

### 11.3 Storage module (Face S or P): SM-1, ASM2824 + 4 × M.2 [update 3]

Full design: `macpro62-storage-board-plan.md` and `kicad/macpro62-storage-face/` (rev A0 floorplan, DRC 0/0; schematic ERC 0/0; routing not started).

- **Why a switch:** Face S is CPU PEG60 Gen4 x4, which cannot bifurcate, so 4 SSDs need a switch. The **ASMedia ASM2824** (Gen3, x8 up / 4 × x4 down, internal downstream clock buffer, SRIS) is the only cheap, JLC-assemblable choice (JLC C9900092023; price TBD, ≈ $15–40 [Unverified]). Gen4 switches (PM40028, PEX88024) cost $164–323, are NDA, and have no stock. The upstream x8 is wired to J_PCIE lanes 0–7, so a future x8 host doubles throughput with no module change. Bandwidth today: Gen3 x4 ≈ 3.5 GB/s shared.
- **Core side:** the ASM2824 sits centred on the die pad with a **3.0 mm soft gap pad** (≈ 1.1 K/W, ≈ 5 K at 4 W), with no Cu block and no preload. Switch support parts (core buck, crystal, SPI flash, PERST# buffers, TMP1075 0x48) are all ≤ 2 mm tall.
- **Outer side:**
  - 3 × 2280 columns at X 26.5 / 52 / 77.5 (sockets at Y 108.5–115, cards toward −Y to Y 28.5) plus 1 × 2280 across the top (Y 115–137).
  - Sockets are LOTES APCI0107-P001A (H4.2, C841661), with SMT M2 standoffs at 2280 (2230/2242/2260 pads DNP).
  - Under-card host parts are ≤ 1.6 mm.
  - Standard M.2 sockets cannot go on the core side (≈ 4.65 mm > 3.5).
- **Bracketless (C-19, approved 2026-10-01):** 4 × 2280 fit only without the X-bracket. With the bracket, ≈ 2 × 2280 + 1 × 2260. SM-1 is held by 4 low-head screws (wafer / ultra-thin head, head + washer ≤ 1.6 mm) straight into the bosses, so the edges of SSD0/SSD2 clear the heads with any 2280 SSD. The part number follows MF-13 (thread, length).
- **J_AUX** moved to **(16.5, 20.5)**. That is the "should" position minus 6 mm in Y, to clear SSD0.
- **Power:**
  - lugs (both sites) → LM74700 + N-FET reverse block → TPS259824 (I_LIM ≈ 5 A, inrush ≤ 1 A) → TPS56C215 12 A buck → 3V3_SSD (4 × 2.5 A)
  - VDD_CORE from a 3 A buck; voltage per the ASM2824 datasheet (NDA)
  - Budget: ≈ 35.6 W worst sustained, ≈ 41.5 W 10 ms peak (≤ 52 W); declared **40 W, Class 1**.
- **Thermal sensors:** TMP1075 0x48 drives THERM_ALERT#. A second TMP1075 at **0x49** drives THERM_TRIP# from its power-on default (80 °C comparator), so it needs no software.
- **RAID:**
  - **No driverless, bootable hardware RAID chip is orderable.** The Marvell 88NR2241 presents one inbox-driver NVMe drive (HPE NS204i-p, Dell BOSS-N1, HighPoint SSD6202A), but it is NDA-only, has no distribution, and macOS is unverified.
  - Broadcom tri-mode and HighPoint parts need drivers that macOS lacks or that cannot boot.
  - macOS cannot boot AppleRAID/SoftRAID volumes (Big Sur and later).
  - **Reference configuration:** boot from one SSD; AppleRAID/SoftRAID across the others as data volumes. Each SSD behind the switch is individually bootable (native NVMe; Sonnet M.2 4x4 precedent).
  - A future 88NR2241 variant (SM-1R) keeps the outline, sockets and power band.
- J_DISP not fitted. EEPROM example: `example_storage_asm2824.bin`.

## 12. Compliance checklist [v0.1]

| # | Requirement | Section |
|---|---|---|
| 1 | Outline 104 × 166 mm, chamfers and blends as in the DXF; ±0.2 mm | 3.1 |
| 2 | 4 × Ø5.0 holes on 74.0 × 50.0 at (52, 69.5); not smaller than Ø5.0 (core bosses at 75.2) | 3.2 |
| 3 | Edge band 1.0 mm free of parts; copper ≥ 0.5 mm from the edge | 3.1 |
| 4 | Core side: parts ≤ 3.5 mm over the plate, ≤ 3.0 mm under strips (non-contact), ≤ 1.0 mm outside the plate | 3.3 |
| 5 | Die stack = G − p + δ (δ 0.05–0.2), checked against the measured G of the target core | 3.3 |
| 6 | Strip-contact parts: top = G − p − t_pad, t_pad 0.5–2.0 mm | 3.3 |
| 7 | KO-F1 Ø11, KO-F2A/B, KO-F5A/B free of parts | 3.3 |
| 8 | Outer side: KO-B1, KO-B2, KO-B1v rules | 3.4 |
| 9 | Outer height ≤ h(x) (or the simplified zones) | 3.4 |
| 10 | J_PCIE at X 43.5, mating face Y 14.5, opening −Y, ±0.5 mm | 3.5 |
| 11 | J_DISP (if fitted) at X 82.0, Y 14.5, opening −Y | 3.5 |
| 12 | J_AUX GH15 at (16.5, 26.5), opening −X | 3.5 |
| 13 | **Both** lug sites (A: J20/J21; B mirror: J22/J23) fitted, Ø3.2 / Ø8.8, wired in parallel, ≥ 15 A per path | 6.4.1 |
| 14 | PCIe lane and sideband map per SFF-9402 (§4 tables); AC caps on the module TX | 4 |
| 15 | Works at x1 minimum; trains at the width declared in the EEPROM | 4 |
| 16 | AUX pinout GH15 per §5; USB2 optional (`flags.bit0`) | 5 |
| 17 | Sustained/peak power within the class and the slot budget | 6.2 |
| 18 | 12 V eFuse (TPS25982-class), inrush ≤ the declared value, PG within 150 ms | 6.5 |
| 19 | 3V3_AUX: ≤ 1 A in S0, ≤ 50 mW in S5 | 6.6 |
| 20 | Power sequencing per §6.7; outputs high-Z when unpowered | 6.7 |
| 21 | EEPROM at 0x50 with a valid MP62 descriptor (passes `mp62_eeprom.py check`), WP strapped | 8 |
| 22 | Sensor at 0x48 at the hot zone; THERM_ALERT#/THERM_TRIP# behaviour | 8, 10 |
| 23 | Hot-spot centroid within R3 of (52, 69.5) | 3.2, 10 |
| 24 | Throttle ≥ 25 % within 100 ms of THERM_ALERT# | 10 |
| 25 | DISPLAY-LINK per §9 (pinout, 100 Ω, AC caps, DLINK_PRSNT#), declared in the descriptor | 9 |
| 26 | No fans; no 5 V or DP_PWR on DISPLAY-LINK | 1, 9 |
| 27 | Offset modules declare `plane_offset`, and keep within the reduced envelope | 3.7 |


## 13. Conflicts with spec v0.2 and host change requests [v0.1]

| ID | Conflict | Resolution in v0.1 | Action |
|---|---|---|---|
| **C-1** | v0.2 calls J_PCIE "124-pin (8i)". In SFF-TA-1016 the 124-position MCIO is the **16i** (2 × 62 contacts). v0.2's TE 1-2381578-9 is a 16i **vertical** part, which is too tall for a module (h ≈ 15–20 mm, and a vertical cable exit has no route). | One **MCIO 124 RA (16i)** per face (§4.1). | Fix v0.2 wording. |
| **C-2** | BP J9/J10 cable landings sit at ±4.6 mm from the face centreline, which is module X 47.4 (Face P) and X 56.6 (Face S), against J_PCIE at X 43.5. The BP placeholder footprint rows (3.4 / 5.2 mm) also differ from SFF Table A-2 (0.575 / 3.525). | Module position fixed at X 43.5. | **CR-2 CLOSED (ICD rev 2, Aidan 2026-10-02):** BP footprint replaced by the SFF one (fp4); the lateral offset (fp5 at 45°: 13.7 / 10.5 mm) is taken by a flat-twinax jog cable (§3.5–3.6). Feasibility of the jog in the short free length is open (M4, ICD O-6). |
| **C-3** | v0.2's OCP FLEXIO logical map does not match commodity MCIO cables. | **SFF-9402** sideband positions. USB2 moves to AUX; PWRBRK# dropped (§4, §7). | Update the BP schematic. |
| **C-4** | v0.2 AUX = GH14. | **GH15** (adds MOD_LED#). | BP J3/J4 and the `face_aux` schematic → SM15B-GHS-TB. |
| **C-5** | v0.2 power classes and limits (Face P 130 W / Face S 35 W). | Classes renumbered; **Class 3 = 150 W**; Face S 40 W (§6.2). | Update the architecture spec §5. |
| **C-6** | v0.2 total budget 325–335 W. | **350–360 W** sustained, ≤ **445 W ceiling** (ICD rev 2, was 405 W) (§6.3, §6.8). | Measure PSU OCP (MF-11). |
| **C-7** | v0.2 puts the face centre ≈ 24.5 mm off-axis. That cannot fit inside an R 80 shell at 55 mm from the axis. | X_AX = 52 assumed; tolerance ±6 mm (core side) / ±4.5 mm (outer side). | MF-3. |
| **C-8** | LCSC stock: MCIO 124 RA G97R24332HR has 0; MCIO 74 RA G97R22332HR has 4. | Keep the parts and allow JPC/Molex/TE equivalents. | Order early, or consign parts to JLC. |
| **C-9** | The cable length needed is ≈ 30–60 mm; commodity MCIO cables are ≥ 150 mm. **ICD rev 2 (fp5, 15 mm plugs assumed): ≈ 12 mm (M1 15) / ≈ 20 mm (23.5) between plug rears.** | Custom-length flat-twinax jog cables (OQ-1, §3.6). | M4 (plug length, sample fit). |
| **C-10** | v0.2 allowed ≤ 4 DP streams. | **5 links** on DISPLAY-LINK (Navi 23 has 5 PHYs). | IOB spec. |
| **C-11** | v0.2 used an IPMI FRU as the ID format. | Raw MP62 descriptor at 0x0000; FRU optional at 0x0100 (§8). | BP/EC firmware. |
| **C-12** | v0.2 gives the peak window as both 10 s and 10 ms. | **10 ms** (§6.2). | Fix v0.2. |
| **C-13** | Core boss pattern from the scan is **75.2 × 50.0 mm**, but the board holes are 74.0 × 50.0 and the bracket 74.3 × 49.7. | Keep Ø5.0 holes on 74.0 × 50.0. M3 float of 1.0 mm radial absorbs the +0.6 mm per side. | **Calipers** on the bosses and stock board holes. |
| **C-14** | The v0.2-era estimate Z_c ≈ 2.6 mm (core-side clearance) and TZ1 40 × 40 / TZ2 84 × 59. | Replaced by the **measured G = 4.5 ± 0.5 mm** and the traced die/strip pads (§3.3). Consequences: core-side parts ≤ 3.5 mm; a Navi 23 needs a ≈ 1.9 mm Cu die shim; VRAM and power stages need spreaders or thick pads. The bus-bar lug sites lie outside the black plate. | Measure G to ±0.05 mm and p (D3). |
| **C-15** | KO-F3 (mirrored MEG-Array bosses) was provisional. | **Released**: the scan shows no bosses there. New KO-F5 (core tab). **Rod resolved (Aidan, 2026-10-01):** it is one of the two long standoff screws at the core's bottom end that carry the base board at its gold holes G1/G2 (±49 mm). The photo's local scale matches the 98.25 mm hole pitch, and the other symmetric hole pair (S1/S6, 105.4 mm) does not fit. Scan orientation (scan top = module bottom) remains an inference. | Aidan to confirm the orientation and identify the tab. |
| **C-16** | M1 (Aidan: GPU-board bottom edges ≈ 15 mm above the BP) vs the standoff geometry. If the BP seats on the standoff tips, the scan puts the tip, and so the BP top, at module Y ≈ −23.5, i.e. the board edge ≈ 23.5 mm above the BP. The photo gives ≈ 18.4 ± 1.5 mm from the core end face to the tip. | Normative v0.1 keeps **≥ 15 mm** (worst case for the cable bend). Cable lengths (C-9, OQ-1) shall be checked at both 15 and 23.5 mm. | Calipers: standoff protrusion and the GPU-board edge → BP top on the assembled machine (M1c). |
| **C-17** | v0.1 draft and v0.2 put the bus-bar lugs at one position (X ≈ 97). Aidan: the stock GPU 2 board is mirrored, so the faces have their lugs on opposite sides. | **Both sites on every module** (site A + mirror site B, in parallel, §6.4.1). KO-F2B, KO-F5B and the mirrored rod added; template J22/J23 and rule areas added. | M5b: which face (P/S) uses which site; polarity per face (M5). |
| **C-18** | BP J9/J10 assumed face normals at 30° / 150°; the stock connector fields (±46.6°) hinted at ≈ 42° / 138°. | **CLOSED (ICD rev 2): Aidan measured ≈ 45° from the I/O-card bottom gaps (GPU cards presumed the same).** The module frame is face-relative, so no module change; BP J9/J10/J3/J4 re-placed (fp5). | Caliper check of each face (M2c residual). |
| **C-19** | KO-B1 forbids all parts under the stock X-bracket, and §11.3 originally assumed 4 × M.2 on the outer side. With the bracket fitted, only ≈ 2 × 2280 + 1 × 2260 fit (update 3 layout study). | **Bracketless modules may release KO-B1** (§3.4), keeping KO-B2. **SM-1 is bracketless (Aidan approved, 2026-10-01 ≈ 20:27 ET):** 4 × 2280 fitted; the module is held by 4 **low-head screws** straight into the bosses (wafer / ultra-thin head, **head + washer ≤ 1.6 mm**, so any 2280 SSD may pass over KO-B2); the switch couples through a gap pad (no preload). | MF-13: thread and length → low-head screw part number. MF-4 not needed for SM-1. |
| **C-20** | §10 "every part > 2 W sits under a pad" vs M.2 SSDs (2–8 W) on the outer side. | Exception for removable, self-throttling socketed devices on the outer side; air-cooled with optional heatsinks within h(x). | MF-14: outer-gap airflow/temperature under load. |
| **C-21** | §10 throttle: "the module shall cut its power by ≥ 25 % within 100 ms". A storage module without an MCU cannot change NVMe power states itself. | Storage modules without an MCU: the host OS/firmware applies the NVMe power limit on THERM_ALERT#; the SSDs throttle themselves; THERM_TRIP# is hardware (TMP1075 POR comparator). | Host firmware/OS tooling (MCU EC + macOS helper). |

**Host status of the CRs (2026-10-02, `/workspace/macpro62-interface-control.md`):**
- **C-2 / CR-2 — partly applied.** The BP now uses the SFF-TA-1016 RA footprint. J9 sits at s = +8.0 (0.5 mm short of +8.5 because of the S5 keep-out, CR-BP-1). **J10 cannot reach s = +8.5:** for s > −4.6 its courtyard enters the G1 gold-hole keep-out (6 mm), and moving it inward to r_c ≤ 24 collides with J1. J10 stays at s = −5.0, so the Face S cable needs a **13.5 mm in-plane jog** (open decision ICD O-1: jog cable / vertical receptacle at J10 / move J_PCIE to X 52 on all modules, which gives ≈ 5 mm jogs on both faces).
- **C-3 — applied** on the host side: no USB2 on the MCIO; USB2 for each face is on AUX 13/14 from the CB PCH (CPU-LINK USB2_FACEP / USB2_FACES).
- **C-4 — applied:** BP J3/J4 are GH15 (**BM15B-GHS-TBT vertical** on the BP; the module uses SM15B-GHS-TB RA; same GHR-15V-S cable housing), `face_aux` stub has MOD_LED_N.
- **C-5 — applied** in the architecture spec §5.3 / §7.8 (superseded note).
- **C-6 — resolved by the 445 W ceiling + live power target (ICD rev 2).** Sustained ≈ 330–345 W (100–115 W margin); the unmanaged worst case ≈ 431 W (≈ 451 W with Face P at 150 W) is held ≤ 445 W by the live power target (§6.8).


## 14. Open questions and measurements [v0.1]

### 14.1 Open questions

| ID | Question |
|---|---|
| OQ-1 | Custom-length MCIO 16i cable (30–60 mm): which vendor, MOQ, cost; or move Y_mate up in MECH 0x0002? |
| OQ-3 | Which sidebands do the commodity MCIO cables actually wire (per vendor and per part number)? |
| OQ-5 | MCIO RA footprint: confirm which side of datum Y the pad rows lie (Amphenol drawing), before fabrication. |
| OD-6 | Face P assignment: which physical face is P (the PSU-side face or the other)? This affects the bus-bar polarity and the cable runs. It no longer affects the lug layout (both sites are fitted, §6.4.1). |
| OQ-7 | Face S x8: which host revision provides x8, and from where (CPU or switch)? |
| OQ-8 | HDMI 2.1 retimer part for the IOB (TDP2004-class [Unverified]) and its FRL 12G support. |
| OQ-9 | MP62 community vendor-ID registry (`vid_space` 2): who runs it? |
| OQ-10 | Does the stock bus bar need a threaded insert on the module, and what is its ampacity? |

### 14.2 TO MEASURE

| ID | What | Why |
|---|---|---|
| **G** | Standoff height per core to **±0.05 mm** (now 4.5 ± 0.5) | Die shim and pad stack |
| **D3** | Pad protrusion **p** of the die and strip pads above the black plate; flatness | Contact heights (§3.3) |
| **MF-1** | Height of the frame/rim around the plate relative to the plate | H-CORE-OUT limit (provisional 1.0 mm) |
| Scan | Orientation of the core scan (top = module bottom?) | All core-side zones |
| Calipers | Boss pattern (75.2 × 50.0 from the scan) and boss OD; board holes on a stock board | C-13, KO-F1 |
| Tab | Identity and height of the tab (X 98–102, Y 122–138); is it mirrored on the other face? | KO-F5A/B |
| **M1c** | Base-board standoff screws: protrusion beyond the core end (photo ≈ 18.4), shaft/collar Ø, thread; GPU-board bottom edge → BP top on the assembled machine | C-16; cable bend room |
| **M1 / M1b** | Shell inner radius R_i, plane distance from the axis, base ring/fillet | Outer envelope h(x) |
| **MF-3** | Lateral offset X_AX of the face centreline from the axis | Envelope; J_DISP margin 0.7 mm |
| **M4** | BP → module cable path, bend radius, length; **MCIO plug length (mating face → cable exit) and a jog-cable sample fit (13.7 / 10.5 mm, ICD O-6)** | OQ-1 |
| **M5** | Lug positions, polarity **per face**, thread, ampacity | §6.4, KO-F2A/B |
| **M5b** | Which face (P or S, and the scanned one) has its bus bar at site A (X ≈ 97) vs site B (X ≈ 7) | §6.4.1; single-site modules (MECH 0x0002) |
| **M2c** | Face-normal angle of each GPU board from the base-board hole axis — **answered ≈ 45° / 135° (Aidan 2026-10-02, I/O-card gaps); residual: caliper check per GPU face** | C-18; BP J9/J10 placement and cable length |
| **MF-13** | Stock module screw: thread, pitch, length; bracket eyelet thickness | C-19: low-head screw part number and length for bracketless modules (head + washer ≤ 1.6 mm) |
| **MF-14** | Air temperature/flow in the board-to-shell gap under load (thermocouple on a dummy SSD, 10 min) | C-20; SSD cooling on SM-1 |
| **M9** | Display cable path from the module to the IOB | §9 |
| **MF-4** | Bracket height; does the ring touch the board? | KO-B1v |
| **MF-5** | Screw thread, length, shoulder; boss OD | §3.2 |
| **MF-8** | Clearance above the module top edge to the fan/duct | J_12V_ALT |
| **MF-11** | PSU OCP and transient response | §6.3 |
| **MF-12** | Stock board thickness | Screw/spring stack |
| MXM | Die position on the chosen MXM card, and GOP/output routing | §11.1 |
| ~~MF-2~~ | ~~Core flatness at MEG positions~~ | **Resolved by the core scan** (KO-F3 released) |

## 15. Parts and prices (LCSC, checked 2026-10-01) [v0.1]

| Function | Part | LCSC | Price | Stock |
|---|---|---|---|---|
| J_PCIE MCIO 124 RA | Amphenol G97R24332HR | C4867471 | $9.59 @1 / $9.37 @10 | **0** |
| J_DISP MCIO 74 RA | Amphenol G97R22332HR | C5433520 | $7.94 @1 / $6.88 @10 | 4 |
| J_AUX GH15 RA | JST SM15B-GHS-TB(LF)(SN) | C265027 | $0.87 | 1,130 |
| 12 V eFuse | TI TPS259824ONRGER (LNR variant C2155879, $4.34) | C2155766 | $5.90 | 1,916 |
| Temp sensor | TI TMP1075DSGR | C2870250 | $0.50 | — |
| ID EEPROM | BL24C64A-SFRC | C111004 | $0.19 | — |
| J_12V_ALT (optional) | Molex 45586-0005 PCIe 8-pin | not stocked | — | — |
| (6-pin alternative) | Molex 45558-0003 | C7545781 | $1.07 | — |
| Lug insert (if needed) | Würth REDCUBE 7466003R | not stocked | — | — |
| Cable, PCIe | MCIO 16i, custom length | — | ≈ $60–80 | — |
| Cable, display | MCIO 8i straight 0.5 m | — | ≈ $46–52 | — |

**Storage reference module SM-1 additions** (update 3; full BOM in `macpro62-storage-board-plan.md` §6):

| Function | Part | LCSC | Price | Stock |
|---|---|---|---|---|
| PCIe switch | ASMedia ASM2824 LFBGA-492 | JLC C9900092023 (LCSC C20612120: 0) | TBD (≈ $15–40 [Unverified]) | JLC "new arrival" |
| M.2 M-key socket H4.2 | LOTES APCI0107-P001A (alt. H3.2 APCI0079-P002A C841651) | C841661 | ≈ $0.6 [Estimate] | ≈ 1,592 |
| M.2 standoff SMT M2 | YIYUAN SMTSO family (SMTSOM225BTR = 2.5 mm) | C5301773 | ≈ $0.15 | — |
| 3V3_SSD buck 12 A | TI TPS56C215RNNR | C473372 | $1.06 | 360–2,406 |

**Interface kit** (connectors + eFuse + EEPROM + sensor, no cables): ≈ **$24 for a GPU module**, ≈ **$17 for a storage module**.

## 16. Sources [v0.1]

- SFF-TA-1016 Rev 1.3 (MCIO connector, cable, Annex A footprints, Tables 5-4/6-3/A-1/A-2).
- SFF-9402 Rev 1.1 (multi-protocol internal cable pinouts for SFF-TA-1016).
- JPC MCIO RA drawing; Amphenol G97R24332HR / G97R22332HR product pages (LCSC).
- `macpro62-architecture-spec-v0.2.md` §4, §5, §7 (the superseded face spec), REF-S1 (Apple service references: screws 923-0708, 923-0716, standoffs 923-0690).
- BP KiCad project `kicad/macpro62-backplane/` (J9/J10 positions, footprints, stackup).
- Fusion export `gpu_board_outline.dxf`; `bracket/gpu_board/summary.md`; `bracket/summary.md`; `bracket/gpu_bracket_keepout.dxf`.
- **Core GPU-face scan** (Aidan, 2026-10-01), traced in `bracket/core_gpu_face/` (script, JSON, DXF, overlays).
- **Aidan's measurement:** core standoff height 4.5 ± 0.5 mm (2026-10-01).
- **Aidan's information (2026-10-01):** the base board mounts on long standoff screws at the core's bottom end (photo `bracket/core_photo/core_flat_photo.jpg`, the scan's "rod"); the stock GPU 2 board is mirrored relative to GPU 1 at its 12 V bus-bar screws.
- Linux amdgpu DCN 3.0.2 (Navi 23 display controller: 5 PHYs).
- TI TPS25982, TMP1075; BL24C64A; JST GH datasheets.
