# MacPro6,2 I/O board (IOB) rev A0 + I/O plate v2: plan

| Item | Value |
|---|---|
| Date | 2026-10-01, written ≈ 22:15 ET |
| Owner | Aidan Winkler (MacPro6,2 project) |
| Board | **IOB rev A0** replaces the stock I/O board. It is 101.0 × 173.6 mm, uses the 6 stock holes and the stock bosses, and keeps the stock port layout: AC, power button, HDMI, 2 × RJ45, 6 × USB-C in the old Thunderbolt slots, 4 × USB-A, 2 audio jacks. |
| Plate | **New plastic I/O plate v2**. The metal I/O frame stays. The plate is curved to the case, with flat port lands for straight connectors. It is ready to print as STEP + STL. |
| KiCad | `kicad/macpro62-io-board/` (KiCad 9). **Floorplan:** outline, holes, keep-outs, 6-layer stackup and 113 footprints, covering every IC, connector, crystal, inductor and bulk capacitor. **DRC 0 / 0** (`--severity-all`). **Schematic:** 387 symbol instances, ≈ 470 nets, ERC **0 errors / 0 warnings**. **Routing has not started.** Small passives are not placed yet. |
| Status | **Plan for review. Nothing ordered.** The stock PSU, audio and I/O-wall flex pin functions are **UNCONFIRMED** (probing procedures are in §9). Several land patterns are placeholders (§10). |

Tags: **[Sourced]**, **[Estimate]**, **[Inference]**, **[Unverified]**, **TO MEASURE**.

Coordinates use the stock **back-view frame**: origin at the board's bottom-left virtual corner, X to the right as seen from behind the machine, Y up toward the MEG end. The MEG end (Y ≈ 173) is the bottom of the machine, next to the BP. The audio end (Y ≈ 0) is the top, under the fan. KiCad shows the board from the front: x = 40 + (101.0 − Xb), y = 200 − Y.

---

## 1. Summary and recommendation

1. **Ports.** Same layout as stock. Each old Thunderbolt rectangle gets 3 USB-C ports (6 in total), all with **DP alt mode**:
   - C1 and C2: Face P GPU links 0 and 1, 4-lane each.
   - C3 and C4: GPU links 3 and 4, 2-lane each.
   - C5 and C6: iGPU DDI-B and DDI-C. **macOS cannot use these.**
   - HDMI: GPU link 2 (DP++) through a TDP158.
   - 4 × USB-A 10 G, with a TUSB1002A redriver on each port.
   - 1 × 2.5GbE (i226-V). The second RJ45 is a DNP site for the rev-B AQC107.
   - Audio uses the **stock audio jack flex** via a CM108B USB codec. The **stock speaker** runs from a PAM8302A amp.
2. **The stock ports really are angled (§4.4).** Each column of shells is tilted about **7° outward (±1.5°)**, mirror-symmetric about the centre bar. The I/O wall follows the case cylinder (R ≈ 82–84 mm).
   - **Recommendation: standard straight connectors on a flat board, with a curved plate that has flat "port lands" (§4.4).**
   - This is the cheapest option. The board, frame and connectors stay standard; all the compensation goes into a 3D-printed part.
   - Tilting the whole board cannot work: one board tilt cannot produce two opposite column angles.
   - Wedge sub-boards and angled-shell connectors cost more and add SI risk. No catalogue part exists for angled shells.
3. **Power button (§5.6).** The stock button is **not** on the stock I/O board and **not** on the 6-pin. It sits in the I/O wall (Apple 821-2222). It shares **one 14-contact flex with the port illumination**, which plugs into a ZIF at the board's bottom-right corner (F side).
   - Rev A provides both:
     - **J31**, a 14P 0.5 mm ZIF (HX FPC 0.5-14P HYH2.0, LCSC C7502869, double-sided contacts) at the stock position.
     - **SW1**, an on-board tact switch behind the plate's Ø12.4 opening.
   - Both drive PWRBTN_IN_N over IOB-LINK to the BP MCU, which pulses PWRBTN#.
4. **The 6-pin is the PSU data cable** [Sourced: iFixit IO-board guide step 22 + comment]. Two further connectors are now identified:
   - **CONN_C** (fine pitch, 2 threaded standoffs at the top edge): the **fan-assembly ribbon** from the interposer (fan + AirPort card). It is held by the bracket with the 2 captive T8 screws.
   - The long front socket: the **audio-jack ribbon**.
5. **Port lights on motion.** LIS2DH12 (U81) motion interrupt → IOB_INT_N → BP MCU fades the LEDs on for about 5 s. This drives the TLC59116 light-pipe LEDs and/or the stock I/O-wall LED MCUs on I²C through J31, whichever is populated.
6. **Power.** 12 V from the stock PSU DC-out header → TPS259824 eFuse → 2 × TPS56C215 (5V_C for USB-C, 5V_A for USB-A and the system) → TLV62585 3V3.
   - Every port gets 5 V / 3 A at attach.
   - The USB-C total is capped at **45–60 W** by firmware (D-IO1).
7. **Cost [Estimate].**
   - Parts: ≈ $105 per board. The ICs are ≈ $63, mostly the 3 × TPS65994AD and 6 × TUSB1046A.
   - 5 × 6-layer PCBs with 2 assembled at JLC: ≈ $700–900.
   - Plate: MJF PA12 ≈ $10–20 each.

### Decisions for Aidan

| # | Decision | Recommendation | If the other option is chosen |
|---|---|---|---|
| **D-IO1** | USB-C 5 V budget | Shared cap of 45–60 W. Extra ports drop to 1.5 A when the cap is reached. | 6 × 15 W = 90 W plus USB-A breaks the 40–50 W IOB allocation and the 405 W PSU rule. |
| **D-IO2** | Rev-A ETH2 | DNP site + blank plate land (`io_plate_v2_A0.step`) | Rev B adds the AQC107 and needs IOB-HS2 (MCIO 74, PCIe x4) plus the `_eth2open` plate. |
| **D-IO3** | **CR-CB-IO1** | Accept: new J3 pinout, i226 moves to the IOB, 1 × USB2, VBAT from the IOB, **Z790 required** for 10 × 10 G | With B760 only 6 of the 10 ports get SuperSpeed. |
| **D-IO4** | **CR-BP-IOB** | Accept the GH15 pinout (§5.5) and feed BP J2 through IOB J5 | – |
| **D-IO5** | Codec | CM108B now (UAC1, mono line-in); CM6646 later | Wait for CM6646 stock (UAC2, stereo line-in, S/PDIF in). |
| **D-IO6** | **Angled ports** | **(a) Straight connectors + curved plate with flat lands** (§4.4) | Wedge sub-boards: +2 boards, HBR3/10 G across mezzanines, ≈ +$60–120. Board tilt: does not work. |
| **D-IO7** | C5/C6 from the iGPU | Keep them (Windows/Linux displays; USB works in macOS) | Make them USB-only and drop U15/U16 mux functions. |
| **D-IO8** | Stackup | 6 layers, JLC06161H-2116 | 4 layers: loses the solid reference planes for 10 G + HBR3. |
| **D-IO9** | Fan + AirPort ribbon (CONN_C) | Rev A: **not reproduced.** The fan gets its own harness to BP J5 (spec §4.6). The CONN_C standoff positions are kept free. | Reproduce CONN_C on the IOB (needs M-IOC1) to keep the stock fan/AirPort blind-mate path. |
| **D-IO10** | Port illumination | **Populate both**: TLC59116 light pipes (new plate) and J31 for the stock I/O-wall flex | Stock wall flex only: drop D21–D26 and use the stock LED MCUs (I²C address unknown). |
| **D-IO11** | Plate process | **MJF PA12, dyed black** (JLC3DP or PCBWay) | SLA black resin: nicer surface, but the clips are brittle. CNC: best fit, ≈ 10× the price. |

---

## 2. Steering log (Aidan, 2026-10-01)

1. Keep the stock layout. USB-C × 6, 3 in each old Thunderbolt rectangle, with DP alt mode. No mini-DP or full-size DP.
2. New plastic plate with LED light pipes. The metal frame stays. Low cost, JLC turnkey, fewest layers.
3. Reuse the stock audio jack module (find its connector, place a codec); reuse the stock PSU connectors (headers at the same positions, with sequencing); reuse the stock speaker (2-pin + class-D amp); CR2032/BR2032 in the stock spot, wired to the PCH RTC.
4. Speaker screws: **M1.6 confirmed** → SMT nuts SMTSO1615MTJ (LCSC C2928168).
5. Ports are angled (≈ 21:12, 21:57 ET). Estimate the angle and pick the cheapest fix → §4.4.
6. Power-button connector (≈ 21:54 ET) and the **I/O-wall flex 821-2222** (≈ 21:56 ET: button + port LEDs on one ZIF; re-identify the 6-pin) → §5.6, §9.5.
7. Make the plate orderable at JLC3DP/PCBWay (STEP + STL, process, material, walls, clip tolerances) → §4.6.

---

## 3. Mechanical frame

- **Board:** 101.0 × 173.6, 6 holes. Each hole has a Ø3.8 drill and a Ø7.5 GND pad.

  | Hole | Position (X, Y) |
  |---|---|
  | TL | (4.13, 146.76) |
  | TR | (96.62, 146.40) |
  | ML | (4.06, 77.96) |
  | MR | (96.67, 77.85) |
  | BL | (4.11, 18.80) |
  | BR | (96.46, 18.59) |

- **AC cutout:** X 34.46–66.41, Y 119.57–142.55, filleted.
- **Keep-outs:**
  - B side: foam rails [0, 24.3, 11, 73], [0, 82, 11, 141.7], [90, 24.3, 101, 73], [90, 82, 101, 141.7].
  - Speaker stadium on F: X 8.3–31.5, Y 36.5–97.0.
  - AC inlet margins: 3 mm on B, 1 mm on F.
  - CONN_C bracket standoffs at (41.06, 5.17) and (59.92, 5.2), kept free.
- **Speaker:** M1.6 SMT nuts at (20.0, 93.9) and (20.0, 39.0), pitch 54.9 ± 0.6. J29 is a 2-pin JST SH at (17.8, 101.4).
- **Coin cell:** BT1 at (20.0, 136.8), Keystone 3034 footprint.
- **I/O-frame centre standoff:** H13 at (53.38, 58.38). This is the stock TB-bar screw point. Height is M-IOF2.

---

## 4. Ports, plate and tilt

### 4.1 Port grid (face centres; mean of the board front scan and the plate scan, ±0.5)

| Port | Position (X, Y) | Part (placeholder footprint) |
|---|---|---|
| USB-C C1–C3 (HDMI-side column) | X 42.6; Y 75.2 / 65.45 / 55.7 | Vertical 24P receptacle. Height chosen per §4.4. |
| USB-C C4–C6 (other column) | X 63.9; same Y | Same |
| USB-A A1/A2 | (43.3, 42.75), (43.3, 32.6) | Vertical USB 3.2 Std-A |
| USB-A A3/A4 | (64.05, 42.75), (64.05, 32.6) | Same |
| ETH1 | (63.5, 92.3) | Vertical RJ45 magjack, 2.5G |
| ETH2 (DNP) | (42.5, 92.0) | 10G magjack site (rev B) |
| HDMI | (42.4, 107.4) | Vertical type A |
| Power button SW1 | (63.02, 108.03) | PTS810 + printed clear cap. Power LED D20 at (63.0, 103.3). |
| Audio jacks | (43.4, 19.1), (64.65, 19.4) | On the stock audio-jack flex (J28) |

All new connectors are **straight**: their mating axis is normal to the board. Because the grid is the face centres, the mouths line up with the plate openings without any offset.

### 4.2 Plate openings (outer)

| Opening | Size | Notes |
|---|---|---|
| USB-C | 9.6 × 4.0, R 1.8 | ≈ 0.33 per side around an ≈ 8.94 × 3.26 shell. The receptacle shell passes through, so the mouth is flush with its land. |
| USB-A | 13.6 × 6.0 | |
| RJ45 | 13.0 × 10.7 | |
| HDMI | 15.4 × 6.0 | These pass the plug: 0.75–0.8 per side. |
| AC | Stock window, 34.55 × 24.65 | |
| Audio | Ø4.8 | |
| Button | Ø12.4 | |
| Light pipes | Ø2.2 bores, Ø4.4 × 2 bosses | Six bores for Ø2.0 PMMA rods over D21–D26: HDMI label (46.2, 115.6), ETH icon (52.95, 92.9), USB-C icons (53.25, 70.4 / 62.6), USB icon (53.7, 49.4), audio (53.8, 21.0). |

### 4.3 In-plane alignment

- Board face columns are square to the board (0.2°).
- The plate and frame outline fits read 1.0–1.3° in-plane. However, the opening centroids match the faces within ±0.45 (HDMI +0.88 is the worst).
- That is a relative in-plane error of ≤ 0.5° at registration accuracy. It is absorbed by the 0.3+ mm per-side clearances. **M-IOP1** confirms with calipers.

### 4.4 Port angle: estimate and decision (D-IO6)

**Evidence.**

1. **Aidan's edge-on photo (726a1262…, 2026-10-01 ≈ 21:57 ET).** I fitted the lower lip of the top shell row with ≈ 15 edge samples per column:

   | Column | Measured lip angle |
   |---|---|
   | O column | 7.3° (residual 1.0 px) |
   | H column | ≈ 6.4° (noisier) |
   | Second row | 5.5° / 7.6° |

   The two columns lean in **opposite directions**, so the shells fan outward symmetrically about the centre bar. Each column's outboard edge stands farther out.
2. **Case geometry.** For a mouth normal to a cylinder of R 82–84 at the column offsets u = −10.6 / +10.7, the angle is asin(u/R) = **7.3–7.5°**. This agrees with the photo.
3. **Earlier front-scan blur fit.** It gave 1–1.5° per axis for the board against the face plane. A symmetric fan largely cancels in a single-plane fit, so this is consistent with the photo. The residual Y tilt is small, at most ≈ 1–1.5° [Estimate]. "Downward" in the photo is mostly perspective. **M-IOT1** measures it.
4. **Board trace.** The ports sit square on the board: the face columns are straight within 0.2°. So the angle comes from the stock **shells/housings themselves** (Apple custom parts, possibly with an angled footprint), not from a tilted board.

**Estimate:** each column ≈ **7° ± 1.5° outward**, with the axis parallel to Y. Residual tilt along Y is ≤ 1.5°.

**Options.**

| Option | What it needs | Cost | Verdict |
|---|---|---|---|
| **(a) Straight connectors, flat board, plate absorbs the angle** | Curved printed plate (R 82, M-IOT2) with a **flat land parallel to the board** under each port group. Each land is backed by a 1.0 mm boss that sits inside the frame slot. Frame unchanged. | ≈ $0 extra (it is all in the printed plate) | **Recommended** |
| (b) Angle the whole board on shims | ≈ 2.4–3.4 mm differential over the hole pattern | – | **Does not work.** Two columns need opposite angles. Shims would also misalign the PSU headers (J3/J4) and the HS1/J2 cable plugs. |
| (b′) Two 7° wedge sub-boards (one per column) | 2 extra boards; 10 G USB + HBR3 DP across board-to-board connectors at an angle; assembly jigs | ≈ +$60–120 per set plus SI risk | Not for rev A |
| (c) Angled-shell connectors | None in the catalogue (Apple custom). A custom shell needs tooling and MOQ. | High | Not available |

**How (a) works** (`io_plate_v2_A0_section.png`):

- The plate outer face follows the case cylinder. Each port group sits on a flat recessed **land** whose outboard edge is flush with the curve.
- The land is ≈ 1.4 mm deep at its inboard edge for USB-C, and ≈ 1.8–2.2 mm for USB-A, RJ45 and HDMI. It is backed by a boss into the frame slot.
- Every boss fits its stock frame slot:

  | Group | Boss | Frame slot |
  |---|---|---|
  | USB-C | 11.8 × 25.7 | TALL 12.2 × 30.2 |
  | USB-A | 16.8 × 19.3 | SQ 17.6 × 20.0 |
  | HDMI | 17.8 × 8.4 | 18.3 × 9.0 |
  | ETH1 | 15.4 × 13.1 | Leg, 16.7 wide |

- USB-C mouths sit flush with the land. USB-A, RJ45 and HDMI faces sit 1.2 mm behind the land, the same as the stock skin. Plug overmolds stop on a flat face, so plugs seat fully.
- The frame stays unmodified. Straight shells cross the frame plane within ≈ 0.25 mm of where the angled stock shells did, against ≥ 1.6 mm per-side slot clearance.

**Mouth/face depth below the plate crown** (from `io_plate_v2_A0_features.json`). The required connector height is D0 − depth, where D0 is the board-to-crown distance from M-IOF2.

| Port | Depth below crown |
|---|---|
| USB-C, H column | 1.55 |
| USB-C, O column | 1.58 |
| USB-A, H column | 3.13 |
| USB-A, O column | 3.35 |
| RJ45 | 3.07 |
| HDMI | 3.45 |

- Choose standard receptacle heights from these depths. Vertical USB-C mid-mounts come in about 0.5 mm steps.
- If the column-to-column USB-C difference exceeds 0.3 mm once measured, use the next height variant on one column. That is still option (a).

**Measurements for Aidan (M-IOT1, M-IOT2).**

1. **Inclinometer.** Use a phone app (bubble/level mode, zeroed first on the board).
   - Lay the stock board ports-up on a flat table and zero the phone on the bare PCB next to the port block.
   - Hold a flat card (credit card or steel rule) square across the **mouth of each column's top USB-A** and read the angle about the Y axis. Repeat on the bottom Thunderbolt port of each column.
   - Expect ≈ +7° on one column and ≈ −7° on the other. Also read the angle about the X axis (expected ≤ 1.5°).
2. **Square / caliper.** With the board flat, use the caliper depth rod to measure from each port face to the PCB top at the **inboard and outboard edge** of HDMI, ETH ×2, the 6 Thunderbolt ports and the 4 USB-A. Over ≈ 9–13 mm width, a 7° tilt gives ≈ 1.1–1.6 mm difference.
3. **M-IOT2, plate curvature.** Lay a steel rule across the stock plate's outer face at Y ≈ 65 (Thunderbolt block) and measure the gap at the centre bar with feeler gauges. Expected ≈ 4.1 mm over the 51.9 width for R 82: R = (w/2)² / (2·gap) + gap/2. Also measure the gap over each port column. Enter the result as `CASE_R`.
4. Enter the residual board-to-plate tilt as `TILT_AX_DEG` / `TILT_AY_DEG` and re-run `build_plate.py`. The lands re-level automatically.

### 4.5 Plate v2 CAD (`mechanical/io_plate_v2/`)

- Outline 51.9 × 163.1, R 11.5, at (53.19, 77.07).
- Skin 1.2. Perimeter rim 1.2 × 3.0.
- Outer face is a cylinder, `CASE_R` 82 (set to None for flat).
- The eight lands are listed in §4.4. Collars are 1.0 wall × 1.0 long behind the USB-A, RJ45 and HDMI lands.
- 8 snap clips at the stock clip points and their mirror images (VERIFY): (31.0, 140), (28.2, 90), (29.6, 30.3), (44.1, 2.7).
- Frame-screw relief Ø6 × 0.6.
- The ETH2 position gets a 0.6 mm cosmetic recess (blank), or an opening in the `_eth2open` variant.
- One solid, ≈ 10.2 cm³, bounding box 52.2 × 163.1 × 11.1.

| File | Content |
|---|---|
| `io_plate_v2_A0.step` / `.stl` | Rev A plate (ETH2 blank) |
| `io_plate_v2_A0_eth2open.step` / `.stl` | Rev B plate (ETH2 open) |
| `io_plate_v2_A0_openings_backview.dxf`, `…_frontview.dxf` | Planform. The front view is in the KiCad x frame. |
| `io_plate_v2_A0_features.json` | Per-feature report |
| `io_plate_v2_A0_preview.png`, `…_iso_inner.png`, `…_section.png` | Previews |
| `build_plate.py`, `section_plot.py` | Parametric sources |

### 4.6 Ordering the plate (JLC3DP or PCBWay) [D-IO11]

**Process and material.**

| Process / material | For | Against | Verdict |
|---|---|---|---|
| **MJF PA12 (HP Multi Jet Fusion), dyed black** | Tough and slightly flexible, so the snap clips survive repeated fitting. Isotropic. Heat-resistant to ≈ 175 °C HDT @ 0.45 MPa [Unverified: vendor sheet]. No supports, so lands and bosses print clean. ≈ $10–20 per part. | Grainy grey-black surface. Holes print slightly undersize. | **Recommended for rev A** (fit test and daily use) |
| SLA black resin (standard or "tough/ABS-like") | Best surface and sharpest Ø2.2 bores and icon edges. ≈ $5–15. | Standard resin is brittle (≈ 2–3 % strain), so the clips crack. It creeps and yellows near PSU heat. Supports mark the inner face. | Cosmetic second print only, with clip length 7 mm and hook 0.4 |
| CNC (ABS, PC or POM) | Best tolerance (±0.05) and real plastic | Curved face + pockets + clips need 3-axis + 4th-axis work. ≈ $80–200. | Only for a final batch after the fit is proven |
| Clear SLA resin, polished | **Power-button cap** (light passes to D20) | – | Order with the plate |

**Design rules applied** (vendor rules quoted from memory; check them on the order page) [Unverified]:

- **Walls:**
  - MJF minimum wall ≈ 0.8 mm (1.0 recommended). The plate uses: skin 1.2, rim 1.2, collars 1.0, land under-thickness 1.0, light-pipe boss wall 1.1, clip tabs 1.2.
  - SLA minimum ≈ 0.6–0.8 mm.
- **Tolerances:** MJF ≈ ±0.2–0.3 mm or ±0.3 %, so ±0.5 mm over the 163 mm length. Openings carry ≥ 0.3 mm per side, which covers this. The USB-C opening (9.6 × 4.0 for an 8.94 × 3.26 shell) is the tightest fit.
- **Holes:** MJF holes come out ≈ 0.1–0.2 small, so the bores are Ø2.2 for Ø2.0 rods. Ream to size if needed.
- **Snap clips:** tab 1.2 thick × 5.0 wide × 6.0 long, hook 0.5.
  - Bending strain ≈ 1.5·t·y/L² = 1.5 × 1.2 × 0.5 / 36 = **2.5 %**. PA12 allows ≈ 4–5 % for occasional assembly [Estimate].
  - Hook-to-frame-lip clearance: design 0.0 nominal (interference = hook 0.5). If the clips are too stiff, file the hook. If they are loose, reprint with hook 0.6.
  - For SLA, use L 7.0 and hook 0.4, which gives ≈ 1.5 %.
- **Fit between plate and frame:** 0.2–0.3 mm per side clearance for MJF; the outline was fitted to the stock plate scan.
- **Orientation:** MJF needs none. For SLA, print with the outer face up so supports land on the inner face.
- **Order:**
  - Upload `io_plate_v2_A0.stl` (or the STEP). Material MJF PA12, colour dyed black, quantity 2, finish standard (bead-blast).
  - Add the button cap: clear SLA, polished. Its CAD is a simple Ø12.0 × 3 cap on a Ø6 stem and is a **TODO**.
  - **Not ordered.** Ordering is Aidan's call after M-IOT2 and M-IOF2.

---

## 5. Interconnects

### 5.1 IOB-HS1: MCIO 124 from CB J3 (CR-CB-IO1)

The pinout is in `kicad/macpro62-io-board/docs/mp62-iob-hs1_mcio124_pinout_v0.1.csv`. It uses the same physical contacts and GND pattern as MP62-FACE.

**Lane pairs (PET = CB TX):**

| Lanes | Use |
|---|---|
| k0–k5 | USB3 for C1–C6 |
| k6–k9 | USB3 for A1–A4 |
| k10 | i226 PCIe x1 |
| k11 / k12 | DDI-B ML0/1 and ML2/3 |
| k13 / k14 | DDI-C ML0/1 and ML2/3 |
| k15 | DDI-B AUX (PET) and DDI-C AUX (PER) |

**Sideband:**

| Contact | Signal |
|---|---|
| A8 / A9 | HPD_B / HPD_C |
| B8 / B9 / A11 | I226 CLKREQ# / WAKE# / PERST# |
| B11 / B12 | I226 REFCLK |
| A12 / A30 | PRSNT, tied to GND on the IOB |
| A26 | VBAT_RTC |
| A27 | USB_OC# |
| B29 / B30 | USB2 uplink to hub H1a |
| B26 / B27 / A29 | Spare |

- The CB plan changes:
  - The i226 (U13) moves to the IOB.
  - USB2 on J3 drops from 4 to 1.
  - CB BT1 becomes DNP. The CB keeps the BAT54C diode-OR with 3V3_DSW, 1 µF + 0.1 µF and the RTCRST# RC.
- **Z790 is required** for 10 × 10 G (HSIO 0–9 are dedicated USB 3.2 Gen2). B760 gives 4 × 10 G + 2 × 5 G.
- macOS: 15-port limit per xHCI, so a USBMap is needed.

### 5.2 Display link: MCIO 74 from Face P

| GPU link | Destination | Notes |
|---|---|---|
| Link 0 (4-lane) | C1 | |
| Link 1 (4-lane) | C2 | |
| Link 2 (DP++) | HDMI | Via TDP158. Lanes ML0→D2, ML1→D1, ML2→D0, ML3→CLK; AUX± = DDC SCL/SDA. |
| Link 3 (2-lane) | C3 | Can be 4-lane if link 4 is unused. |
| Link 4 (2-lane) | C4 | |

- HPD0/1 come from PD #1 GPIO0/1. HPD3/4 come from PD #2. HPD2 comes from the TDP158.
- DLINK_PRSNT# is read on PD #2 GPIO2. The GPU drives at most about 4 displays.

### 5.3 PSU headers

| Ref | Position | What it is | Pinout |
|---|---|---|---|
| J3 | (25.6, 5.8), B side | **PSU DC-out**, 12P, shrouded, ≈ 1.5 mm pitch | Provisional: 1–6 +12V, 7–12 GND |
| J4 | (8.75, 5.2), B side | **PSU data cable**, 6-pin header, ≈ 1.25 mm pitch. iFixit step 22 names it the "power supply data cable"; a reader comment notes exposed pins that later boards shroud. | Provisional: 1 11V_SB, 2 GND, 3 PS_ON#, 4 PWR_OK, 5/6 PSU SMBus? |

- J5 (Micro-Fit 2×4) passes these through to BP J2: 1–2 12V_MAIN, 3–5 GND, 6 PS_ON#, 7 11V_SB, 8 PWR_OK.
- The PSU SMBus reaches I2C_SYS only through DNP 0R links.
- **All of this is UNCONFIRMED; probe first (§9.1).**

### 5.4 Stock flex connectors (re-identified 2026-10-01 ≈ 22:00 ET)

| Stock connector | Position | Function | Rev-A IOB |
|---|---|---|---|
| CONN_A, 6-pin | (9.9, 5.2), B | PSU data cable | J4 |
| CONN_B, 12P | (25.6, 5.8), B | PSU DC-out | J3 |
| CONN_C, fine pitch + 2 threaded standoffs | (49.7, 5.0), B | **Fan-assembly ribbon** (interposer: fan 12 V/PWM/FG + AirPort Wi-Fi/BT), held by the bracket with 2 captive T8 screws [Sourced: iFixit steps 5–7] | **Not reproduced (D-IO9).** Standoff positions kept free. M-IOC1. |
| Fan antenna coax | near the top edge | AirPort antenna | Not on rev A |
| Long front socket (≈ 34 × 5, ~45–50 contacts) | (50.9, 10.4), F | **Audio-jack ribbon** (821-1776): "squeeze and pull" latch [iFixit step 30] | J28, 50P 0.5 placeholder |
| **I/O-shield ZIF, 14P** | ≈ (82.8, 10.0), F, bottom-right corner near the 2R2 inductor and barcode F5K610200 | **I/O wall 821-2222 flex: power button + port illumination** [iFixit step 29; Aidan photos] | **J31** (§5.6) |
| MEG-Array | Y ≈ 173 | IO-board data cable to the interconnect board | Replaced by IOB-HS1 + J2 |

### 5.5 IOB-LINK GH15 J6 to BP J6 (CR-BP-IOB)

| Pin | Signal |
|---|---|
| 1, 2 | 3V3_SB |
| 3, 7, 11, 12, 15 | GND (pin 11 = IOB_PRSNT_N, tied to GND) |
| 4 | PWRBTN_IN_N |
| 5 | HALL_A_N |
| 6 | HALL_B_N |
| 8 | I2C_SYS_SCL |
| 9 | I2C_SYS_SDA |
| 10 | IOB_INT_N |
| 13 / 14 | USB2_LINK D+ / D− (to hub H2) |

### 5.6 Power button, I/O-wall flex and port lights

**Stock wiring** [Sourced]:

- The button is part of the **I/O wall** (Apple 821-2222, service 661-7541, "I/O wall … includes the power button"). It is not on the stock I/O board.
- Its signals run I/O wall flex → I/O board → I/O flex → SMC. The community says pins 3 and 6 act as the power button [Unverified].
- The illumination LED flex carries LED microcontrollers on I²C. The motion sensing that lights the ports was done by the SMC with the logic-board accelerometer.

**Flex count from Aidan's photos (0174df35…, c8cedefc…):**

- The flex tip shows **14 gold fingers**. Intensity profiles gave 14 / 14 / 15 peaks with even spacing.
- The board ZIF shows **14 tails** on the solder side.
- Pitch: the Ø7.77 mounting-hole pad in the same photo gives ≈ 38–42 px/mm. The tail spacing is ≈ 22.5 px, so ≈ **0.53–0.60 mm, i.e. 0.5 mm pitch** (±15 % from perspective).
- Body ≈ 8–10 mm long. The actuator faces the board's Y = 0 (top) edge, so the flex enters from the top end.
- Aidan's "15–20 at 0.3–0.5" bracket is consistent. **0.3 mm is unlikely**: 14 contacts at 0.3 would span only 3.9 mm.

**Rev-A design:**

- **J31** = HX FPC 0.5-14P HYH2.0 (LCSC C7502869): 0.5 mm, flip-top, **double-sided contacts**, so it works whichever way the flex contacts face. It sits at the stock position (82.8, 10.0), F side, tails toward +Y.
  - The land pattern is a Hirose FH12-14S placeholder; check it against the HX drawing.
  - Alternates: Kinghelm KH-FG0.5-H2.0-14P (C5441651, bottom contact) and Megastar ZX-0.5FPC-FWX-H2-14P (C7544634).
- **Jumper matrix:** every J31 pin goes to its own WALL_Pn net, then through a 0402 0R to a candidate net.
  - **Populated:** P3 → PWRBTN_IN_N and P6 → GND, the community button pair.
  - **DNP until probed:** P1/2/11/13/14 → GND, P4/5 → 3V3_SB, P7/8 → I2C_SYS SCL/SDA, P9 → IOB_INT_N, P10 → 5V_A, P12 → 3V3.
  - Probing (§9.5) decides which links to fit. That is a rework of 0402s; no re-spin.
- **SW1:** PTS810 tact switch at the button centre, behind the plate's Ø12.4, with a printed clear cap. It is wired-OR with J31 to PWRBTN_IN_N. D31 is an ESD TVS and C has 100 nF debounce; the pull-up is on the BP.
- **J30** (DNP, JST SH 2P at (56.5, 104.5) F): optional remote or stock button in parallel.
- **Behaviour (BP MCU firmware):**
  - PWRBTN_IN_N falling edge → pulse PWRBTN# 400 ms (S5→S0, or the OS sleep request in S0). A 4 s hold forces off.
  - Power/sleep LED D20 on TLC59116 OUT8: on in S0, breathing in sleep.
  - **Port lights:** LIS2DH12 (U81, 0x18) runs at 10 Hz low power with an INT1 wake-up threshold of ≈ 63 mg / 1 sample. INT1 → IOB_INT_N.
  - The MCU reads INT1_SRC and fades in the six light-pipe LEDs (TLC59116 OUT9–14) and/or commands the stock wall LED MCUs. It holds them for 5 s after the last motion, then fades out over 1 s.
  - This works in S0 and S5 because U80, U81 and the LEDs are on 3V3_SB.
  - Hall interlock U30/U31 → HALL_A_N/HALL_B_N. With the case off, the lights stay on while the case is open (stock-like service light).

---

## 6. Electrical blocks (schematic `macpro62-io-board.kicad_sch`)

| Block | Parts | Notes |
|---|---|---|
| USB-C ×6 | J11–J16; TUSB1046A U11–U16 (I²C on each PD's I2C3, 0x12/0x13); 220 nF AC caps (connector TX, host RX); 220 pF CC caps | DP lanes are AC-coupled at the source (Face P / CB). |
| PD | 3 × TPS65994AD U1–U3 (PD1 = C1/C2, PD2 = C3/C4, PD3 = C5/C6); flashes U4/U6/U7 (8 Mbit); ADCIN straps | I2C1 → I2C_PD (behind the TCA9517 U83, enabled by PG_3V3). IRQs → U84 74LVC1G07 → IOB_INT_N. |
| USB-A ×4 | J21–J24; TUSB1002A U21–U24; 1.5 A switches U25–U28 (FLT# → USB_OC#); 100 µF bulk per port | |
| USB2 | CH334R: H1a U34 (C1–C3 + H1b), H1b U32 (C4–C6 + codec), H2 U33 (A1–A4, uplink from IOB-LINK); 12 MHz Y1–Y3 | |
| Ethernet | i226-V U50 + NVM U51 + 25 MHz Y4 + SVR L44; J25 magjack; J26 DNP | |
| HDMI | TDP158 U60 + 1V1 LDO U61; 0.5 A PTC on +5V; DDC 1.8 k pull-ups | |
| Audio | CM108B U70 + Y5. HP_L/R → J28; line-in L+R mixed into the mono ADC; S/PDIF TX to J28; optical RX not supported | CM6646 is the upgrade path. |
| Speaker | PAM8302A U71 (mono sum); SD# from CM108B GPIO3; J29 | |
| Management | TLC59116 U80 (diag D1–D8, power D20, light pipes D21–D26); LIS2DH12 U81; ID EEPROM BL24C64A U82 (0x51); Halls U30/U31; SW2 DIAG | |
| RTC | BT1 → R30 1 k → D30 BAT54WS → VBAT_RTC (HS1 A26) | |
| Power | §7 | |

---

## 7. Power tree and budget

- **Chain:** J3 +12V_MAIN → U40 TPS259824 (ILIM ≈ 10 A, UVLO ≈ 10.5 V) → +12V_IOB, which feeds:
  - U41 TPS56C215 → **5V_C** (USB-C PP5V).
  - U42 TPS56C215 → **5V_A** (USB-A, hubs, codec, amp, HDMI 5 V).
  - U43 TLV62585 → **3V3** (from 5V_A).
- **Standby:** 3V3_SB comes from the BP over IOB-LINK (U80–U83, LEDs, Halls).
- **Budget:**

  | Load | Power |
  |---|---|
  | USB-C, 6 × 15 W | 90 W |
  | USB-A, 4 × 4.5–7.5 W | 18–30 W |
  | Logic | ≈ 8 W |
  | Worst case at 12 V | ≈ 116–126 W |

- **Recommendation (D-IO1):** 5 V / 3 A is advertised at attach, with a 45–60 W USB-C pool. The BP MCU sets the TPS65994 source PDOs over I²C and drops extra ports to 1.5 A.

---

## 8. PCB

- **Stackup:** 6 layers, JLC06161H-2116.
- **Netclasses:** USB3_90R, DP_100R, PCIE_85R, USB2_90R, MDI_100R, PWR_5V, PWR_12V. Default clearance 0.1.
- **Placement:** see `floorplan_iob_A0.png`, `render_port_side_F.png` and `render_psu_side_B.png`.
- **2026-10-01 changes:** J30 and J31 added on F. U83/U84/L44 placed on B. The duplicate PD flash (old U5) was removed. J2 moved to Y 150.6 to clear the AC keep-out. J6 moved to Xb 80. J4 moved to Xb 8.75.
- **DRC:** 0 violations, 0 unconnected, 0 footprint errors (`drc_report.txt`).
- **ERC:** 0 / 0 (`erc_report.txt`).
- The netlist has not been pushed to the PCB yet, so pads are unassigned; routing comes next.

---

## 9. Probing procedures for Aidan (stock board + PSU)

> Safety: the PSU has mains on the primary side. Probe only the low-voltage headers with the PSU in its cage. After unplugging, hold the power button for 10 s to discharge (iFixit).

### 9.1 PSU 6-pin data cable (J4) and 12P DC-out (J3)

1. Count the contacts and measure the pitch with calipers across the end pins: (n − 1) × pitch. Photograph both connectors face-on with a ruler. **Confirm the 11 vs 12 count on the DC-out.**
2. Unplugged, check continuity from each pin to the PSU chassis/GND.
3. With mains in and the PSU off (standby), measure every pin to GND. Expect one ≈ 11–12 V standby pin. PWR_OK should read ≈ 0 V; PS_ON# reads pulled up.
4. Through a 1 k resistor, ground each candidate pin briefly. The one that brings up 12 V main on the DC-out pins is **PS_ON#**. Then find the pin that rises to 3.3–5 V about 100–500 ms later: that is **PWR_OK**.
5. A pair that idles at 3.3 V with pull-ups is probably **SMBus**. Do not drive it.
6. Fill in the table in `docs/` and re-run `build_sch.py` with the confirmed map.

### 9.2 Audio-jack ribbon (J28)

- Count the contacts and measure the pitch.
- With a 3.5 mm plug inserted: find the tip, ring and sleeve continuity to the flex contacts, and the jack-detect switch (it opens or closes on insertion).
- Optical: find the TX LED supply and data, and the RX module supply and output.

### 9.3 Speaker

- Check the speaker connector pitch: 1.0 mm (SH) or 1.25 mm (GH).
- Measure the speaker DC resistance (expect 4–8 Ω).

### 9.4 Fan-assembly ribbon (CONN_C), M-IOC1

- Count the contacts and measure the pitch.
- With the stock machine running, find 12 V/11 V, GND, PWM (25 kHz-class square wave) and FG (tach pulses) on the fan side.
- Photograph the bracket and standoffs.

### 9.5 I/O-wall flex 821-2222 (J31)

1. **Count:** confirm 14 contacts. **Pitch:** measure across pins 1–14 (13 × pitch: 6.5 mm at 0.5 mm, 3.9 mm at 0.3 mm). **Contact side:** note whether the gold fingers face toward or away from the PCB when inserted. Photograph with a ruler.
2. **Button, unpowered, flex unplugged:** on a multimeter in continuity mode, press the button and find the pair that closes. Check the community claim of pins 3 and 6. Then check whether either pin of that pair is continuous to any other pin, which would identify the GND pins.
3. **GND:** the flex shield or stiffener to each pin. List all pins at 0 Ω.
4. **Powered, stock machine, flex plugged in, back-probing the ZIF tails with fine needles:**
   - Record the DC voltage on every pin in sleep and in S0.
   - Find the I²C pair: 3.3 V idle with bursts on a scope when the machine is moved.
   - Find the LED supply: 3.3 V, 5 V or 12 V.
   - Look for any IRQ.
5. Fit the matching 0R links on J31 (§5.6). **Do not populate the DNP links before this table exists.**

---

## 10. Placeholders and risks

| Item | Risk | Mitigation |
|---|---|---|
| Land patterns for USB-C, USB-A, RJ45, HDMI, J28, J3, J4 and J31; QFN placeholders for TPS65994AD, TUSB1046A, TUSB1002A, CH334R, i226-V, TDP158 | Wrong pads | Replace them with the datasheet or JLC footprints before routing. |
| Logical pin numbers on the IC symbols | Schematic-to-footprint mismatch | Map every pin from its datasheet. |
| Stock pinouts (PSU, audio, wall flex) | Wrong function | Probe per §9; 0R matrices and DNP links. |
| Plate curvature R and D0 | Ports recessed or proud | M-IOT2 and M-IOF2 before ordering; parametric rebuild. |
| Clip positions | Plate does not latch | VERIFY on the stock plate; print one test plate. |
| i226-V availability | Ethernet missing | AQC107 rev B; check JLC/LCSC stock. |
| macOS USB / i226 support | Driver issues | USBMap; AppleIGC caveat (spec §8.4). |

---

## 11. BOM and cost [Estimate]

| Group | Per board |
|---|---|
| ICs (3 × TPS65994AD ≈ $15, 6 × TUSB1046A ≈ $18, 4 × TUSB1002A ≈ $7, i226-V ≈ $6–9, TDP158 ≈ $3.5, 3 × CH334R ≈ $1.5, CM108B ≈ $1.2, power ≈ $5, management ≈ $3, flashes ≈ $1.3) | ≈ $63 |
| Connectors (MCIO 124 ≈ $8–12, MCIO 74 ≈ $6–9, 6 × USB-C ≈ $5, 4 × USB-A ≈ $2, RJ45 ≈ $2–4, HDMI, Micro-Fit, GH15, ZIF ≈ $0.3, FPC 50P, stock headers ≈ $2–6) | ≈ $35 |
| Passives, inductors, crystals, nuts, holder | ≈ $7 |
| **Total parts** | **≈ $105** |
| 5 × 6-layer PCBs + 2 assembled (JLC turnkey, extended-part fees) | ≈ $700–900 total |
| Plate, MJF PA12 × 2 + clear SLA button cap | ≈ $25–45 plus shipping |

---

## 12. Measurement list

| ID | What |
|---|---|
| **M-IOT1** | Port-face angle per column with a phone inclinometer (zeroed on the PCB), plus caliper inboard/outboard face heights (§4.4). |
| **M-IOT2** | Plate outer-face curvature: steel rule plus feeler gauges at the centre bar and at each column → `CASE_R`. |
| M-IOF1 | Back depth from the board B side to the PSU frame window. |
| M-IOF2 | Plate thickness; frame depth; board-to-plate-crown distance D0 (sets the connector heights); standoff height H13; frame centre-screw head height. |
| M-IOF3 | Front height envelope outside the plate for the power stage (U40–U42, L41/L42). |
| M-IOF4 | HS1 (J1) and J2 plug clearance over the psu_frame top bead (Y ≈ 163) and window top (Y ≈ 160). |
| M-IOH1 | Hall sensor positions and magnet polarity (stock: magnet ≈ 1 inch right of the power button overrides the interlock). |
| M-IOP1 | Port grid with calipers (the face centres in §4.1). |
| M-IOC1 | Fan-assembly ribbon (CONN_C): count, pitch, fan signals (§9.4). |
| M-IOB1 | I/O-wall flex J31: count, pitch, contact side, button pair, GND, I²C, LED supply (§9.5). |
| PSU | §9.1 (also confirm the 11/12 contact count). |
| Audio | §9.2. |
| Speaker | §9.3. |
| Board | Stock board thickness (expected 1.6). |

---

## 13. Files

| Path | Content |
|---|---|
| `kicad/macpro62-io-board/` | KiCad project, `MP62_IO.pretty` (footprints), `MP62_IO.kicad_sym`, `tools/` (make_fps, build_pcb, build_sch, postprocess, floorplan, io_geom.json, placement.json), `docs/` (HS1 pinout CSV, netlist summary), DRC/ERC reports, renders |
| `mechanical/io_plate_v2/` | Plate STEP/STL ×2, DXF ×2, features JSON, previews, sources, README |
| `macpro62-io-board.zip` | Everything above plus this plan |
