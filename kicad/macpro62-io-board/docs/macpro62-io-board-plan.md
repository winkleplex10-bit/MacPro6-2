# MacPro6,2 I/O board (IOB) rev A0 + I/O plate v2: plan

| Item | Value |
|---|---|
| Date | 2026-10-01, written ≈ 22:15 ET; **rev 2026-10-02 ≈ 08:30 ET: D-IO2 resolved, 2 × 2.5GbE (2 × i226-V) on rev A0**; **≈ 09:10 ET: stock edge/plate/flex photos → plate v2 reworked for the 821-2222 flex, D0 re-estimated (§4.7)**; **≈ 10:15 ET: flatbed scan of the 821-2222-A flex + measured D0 18.0 / 16.5 → no lands or bosses (the stock flex lies flat), port grid = flex cut-outs, USB-C columns X 43.09 / 63.69, port risers and non-magnetic RJ45 proposed (§4.7.1–4.7.4)** |
| Owner | Aidan Winkler (MacPro6,2 project) |
| Board | **IOB rev A0** replaces the stock I/O board. It is 101.0 × 173.6 mm, uses the 6 stock holes and the stock bosses, and keeps the stock port layout: AC, power button, HDMI, 2 × RJ45, 6 × USB-C in the old Thunderbolt slots, 4 × USB-A, 2 audio jacks. |
| Plate | **New plastic I/O plate v2**. The metal I/O frame stays, and the stock 821-2222-A flex is reused. The plate is curved to the case (outer R 82.0 from the measured D0). Since 2026-10-02 ≈ 10:15 ET it has **no lands or bosses**: the inner face is smooth so the flex lies flat, and the openings go straight through. It is ready to print as STEP + STL. |
| KiCad | `kicad/macpro62-io-board/` (KiCad 9). **Floorplan:** outline, holes, keep-outs, 6-layer stackup and 117 footprints, covering every IC, connector, crystal, inductor and bulk capacitor. **DRC 0 / 0** (`--severity-all`). **Schematic:** 410 symbol instances, ≈ 500 nets, ERC **0 errors / 0 warnings**. **Routing has not started.** Small passives are not placed yet. |
| Status | **Plan for review. Nothing ordered.** The stock PSU, audio and I/O-wall flex pin functions are **UNCONFIRMED** (probing procedures are in §9). Several land patterns are placeholders (§10). |

Tags: **[Sourced]**, **[Estimate]**, **[Inference]**, **[Unverified]**, **TO MEASURE**.

Coordinates use the stock **back-view frame**: origin at the board's bottom-left virtual corner, X to the right as seen from behind the machine, Y up toward the MEG end. The MEG end (Y ≈ 173) is the bottom of the machine, next to the BP. The audio end (Y ≈ 0) is the top, under the fan. KiCad shows the board from the front: x = 40 + (101.0 − Xb), y = 200 − Y.

---

## 1. Summary and recommendation

> **Update 2026-10-02 ≈ 12:45 ET (D-IO16, Aidan 12:13 / 12:17 ET): swappable flex port modules replace the risers (§4.7.9).** Each USB-C / USB-A / HDMI receptacle is soldered straight to its own JLC FPC with an FR4 stiffener (no rigid PCB). The tail C-folds under the module to a DF40C-50 (PMI-50 pinout) into JM1–JM11 on the main board. Plug loads go into printed cradles (push) and a screwed clamp plate via a bonded SUS sleeve (pull). Axes are normal to the plate by default, so plugs seat fully (stock 12.5° = 0.7–1.4 mm short even with seats). SI ≈ 1.4–2.1 dB per lane after the redrivers, so no extra redrivers.
>
> **Update 2026-10-02 ≈ 12:00 ET (M-IOT2 measured: stock ports lean outward 12.5°, mirrored):** USB-C / USB-A / HDMI risers now tilt **±12.5°** (`TILT_OVERRIDE_DEG = 12.5`), which is **7.0–7.25° off the plate normal** at R 110. Mouths 17.46–18.03 above the board, flat plug seats on the outer face, risers re-shaped (§4.7.5, "Rev 12:00 ET"). Main stake: plug overmold stand-off 0.7 (USB-C) / 1.1–1.2 (USB-A) / 1.4 (HDMI) mm (M-IOT3, M-IOC2).
>
> **Update 2026-10-02 ≈ 10:50 ET:**
> - Ports on 5 tilted column risers (§4.7.5): R 111.2 from D0, tilt ±5.3–5.5°, mouths 18.4–18.6 above the board.
> - Non-magnetic RJ45 + V24P05S (§4.7.6).
> - CONN_C fan + AirPort reproduced on the IOB with EMC2101 + ASM1182e + a 4th USB2 hub (§4.7.7).

1. **Ports.** Same layout as stock. Each old Thunderbolt rectangle gets 3 USB-C ports (6 in total), all with **DP alt mode**:
   - C1 and C2: Face P GPU links 0 and 1, 4-lane each.
   - C3 and C4: GPU links 3 and 4, 2-lane each.
   - C5 and C6: iGPU DDI-B (4-lane) and DDI-C (**2-lane since 2026-10-02**, its ML2/ML3 pair slot now carries the second i226). **macOS cannot use these.**
   - HDMI: GPU link 2 (DP++) through a TDP158.
   - 4 × USB-A 10 G, with a TUSB1002A redriver on each port.
   - **2 × 2.5GbE (2 × i226-V, U50 → ETH1, U52 → ETH2)**. The HanRun HR913790A magjacks (16.9) are **too tall for the measured D0**: the jack face must be ≤ 13.6. D-IO15 proposes a non-magnetic vertical RJ45 ≤ 13 plus discrete 2.5G magnetics (§4.7.4). The AQC107 10 G becomes a later variant (§5.1.1).
   - Audio uses the **stock audio jack flex** via a CM108B USB codec. The **stock speaker** runs from a PAM8302A amp.
2. **The stock ports really are angled (§4.4).** Each column of shells is tilted about **7° outward (±1.5°)**, mirror-symmetric about the centre bar. The I/O wall follows the case cylinder (R ≈ 82–84 mm).
   - **Recommendation (rev 2026-10-02 ≈ 10:15 ET): standard straight connectors on a flat board, and a curved plate *without* lands, because the stock flex must lie flat (§4.7.3).** Each mouth is flush at its shell's outboard edge. USB-C, USB-A and HDMI need 17.2–17.9 mm from the board top, so they sit on **port risers** (D-IO14, §4.7.4). (The 2026-10-01 flat-land design below is superseded.)
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
5. **Port lights on motion.** LIS2DH12 (U81) motion interrupt → IOB_INT_N → BP MCU fades the LEDs on for about 5 s.
   - **Since 2026-10-02 the lights come from the I/O-wall flex 821-2222 on J31** (its own LEDs, light-guide pads and LED MCUs, glued to the plate as stock). The board-side light pipes D21–D26 are **DNP**: the metal I/O frame's centre bar sits right over 5 of the 6 pipe positions (§4.7).
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
| **D-IO2** | Rev-A ETH2 | **RESOLVED (Aidan, 2026-10-02 ≈ 08:05 ET): 2 × 2.5GbE.** i226-V #2 on PCH RP4 / HSIO 13 via HS1 k14 (§5.1.1); ETH2 jack set back behind the frame (§4.1); plate ETH2 opened (`io_plate_v2_A0.step`). | AQC107 10 G = later variant: needs PCIe x4 on a new IOB-HS2 cable (J3 has no free pairs) and replaces i226 #2. |
| **D-IO3** | **CR-CB-IO1** | Accept: new J3 pinout, i226 moves to the IOB, 1 × USB2, VBAT from the IOB, **Z790 required** for 10 × 10 G | With B760 only 6 of the 10 ports get SuperSpeed. |
| **D-IO4** | **CR-BP-IOB** | Accept the GH15 pinout (§5.5) and feed BP J2 through IOB J5 | – |
| **D-IO5** | Codec | CM108B now (UAC1, mono line-in); CM6646 later | Wait for CM6646 stock (UAC2, stereo line-in, S/PDIF in). |
| **D-IO6** | **Angled ports** | **(a) Straight connectors + curved plate**. **Since 2026-10-02 ≈ 10:15 ET: no lands** (stock flex), mouths flush at the outboard edge; plug recess USB-C 0.62–0.67, USB-A ≈ 1.7–1.8, HDMI ≈ 2.0 (§4.7.3) | Wedge sub-boards: +2 boards, HBR3/10 G across mezzanines, ≈ +$60–120. Board tilt: does not work. |
| **D-IO7** | C5/C6 from the iGPU | Keep them (Windows/Linux displays; USB works in macOS) | Make them USB-only and drop U15/U16 mux functions. |
| **D-IO8** | Stackup | 6 layers, JLC06161H-2116 | 4 layers: loses the solid reference planes for 10 G + HBR3. |
| **D-IO9** | Fan + AirPort ribbon (CONN_C) | **Superseded 2026-10-02 ≈ 10:50 ET: reproduced on the IOB** at the stock position, B side, centred between the stock standoffs (41.06, 5.17) / (59.92, 5.20): J7, 2 × 20 @ 0.5 mm (DF12-40DS-0.5V(86) footprint candidate, C431048). Fan via EMC2101 (U90), AirPort PCIe via an ASM1182e switch (U91) on the i226 #2 lane, Bluetooth USB2 via a 4th CH334R (U35). The BP J5 fan harness is dropped (§5.7). **11:30 ET:** + J8 U.FL for the fan-assembly antenna cable (2nd fan-assembly cable, iFixit 21222 step 8) at the photo position (38.4, 16.0) B, optional DNP pass-through J9; T8 fan-cable bracket keep-out X 38.06–62.92, Y 0–10.5 on B (only J7/H14/H15 inside, checked by `build_pcb.py`). | Pinout and mating are unconfirmed until M-IOC1 / M-IOC3; antenna receptacle type/position M-IOA1. |
| **D-IO10** | Port illumination | **Revised 2026-10-02: the flex on J31 only.** D21–D26 DNP, plate light pipes removed, light windows over the flex pads. TLC59116 stays (D20, diag LEDs, and the A1 flex below). | Board light pipes: need Ø2.5 holes drilled in the frame centre bar (5 of 6 positions blocked). |
| **D-IO12** | Which flex on the plate | **Revised 2026-10-02 ≈ 10:15 ET: reuse the stock 821-2222-A; no replacement flex for now.** The plate has no bosses, the ports are centred on the flex cut-outs (USB-C +0.44 per side), and there are pockets for the plate-side LEDs and the button carrier (§4.7.2–4.7.3). *Earlier text:* **Rev A0: fit-test the stock 821-2222** (glue pocket, windows, pins all ready). **Plan an A1 replacement flex** (same outline, cut-outs = our bosses + 0.3, LEDs driven by U80 through J31) if the stock flex does not lie flat (§4.7). | Trim the stock flex cut-outs by 1.0–1.8 mm per side: cuts into the LED/trace margins, not recommended. |
| **D-IO13** | Insulation between board and frame | **No shroud.** Keep (or replace) the 1 mm foam over the flex; a 0.25 Formex GK-10 die-cut from `io_flex_foam_insulator_A0.dxf` is the drop-in alternative. | Printed PA12 shroud: eats D0 height and buys nothing; our port shells are meant to touch the frame (chassis GND). |
| **D-IO14** | Connector heights (measured D0 18.0 / 16.5) | **Resolved 2026-10-02 ≈ 10:50 ET: tilted column risers** (§4.7.5): 5 small 4-layer risers (2 × USB-C, 2 × USB-A, 1 × HDMI), each tilted 5.25–5.51° so that every port axis is radial. Link: DF40C receptacles + a C-fold flex jumper. USB-C VBUS runs on pogo pins. The risers sit on printed wedge cradles. | **12:00 ET: tilt = measured stock 12.5° (M-IOT2)**, not the surface normal; `TILT_OVERRIDE_DEG = None` restores the radial 5.3–5.5° build. |
| **D-IO15** | RJ45 | **Approved 2026-10-02**: non-magnetic vertical SMD RJ45 (Lingqiang ZJLQ-RJ45-SMD-PCB125-8P8C, C55547809; height ≤ 13.0 still to be confirmed from its datasheet) + JASN V24P05S 2.5G magnetics (C2827281, $0.63 @10) on the B side + Bob-Smith network. | M-IOR1: jack height and latch side. |
| **D-IO16** | Port mounting | **2026-10-02 ≈ 12:45 ET: swappable flex port modules** (§4.7.9): receptacle soldered to a JLC FPC + FR4 stiffener, C-fold tail to DF40C-50 (PMI-50), printed cradle + screwed clamp plate take the plug loads, axes normal to the plate. | Supersedes D-IO14 risers; stock 12.5° build kept as `--tilt 12.5 --tag _tilt12p5`. |
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

### 4.1 Port grid (rev 2026-10-02 ≈ 10:15 ET: centres of the stock 821-2222-A flex cut-outs from the flatbed scan, ±0.15)

> Rev 12:45 ET: positions unchanged; the parts / risers column is superseded by the D-IO16 modules (§4.7.9).

| Port | Position (X, Y) | Part / height (§4.7.4) |
|---|---|---|
| USB-C C1–C3 (H column) | X **43.09**; Y 75.76 / 65.84 / 55.97 | FG-ST-C-24P-VT-SMT-15.0 (C51911913) on a +2.90 riser; mouth 17.90 above the board |
| USB-C C4–C6 (O column) | X **63.69**; same Y | Same part, +2.82 riser; mouth 17.82 |
| USB-A A1/A2 | (43.12, 42.64), (43.12, 32.54) | KH-3.0AF180WJ-15JB (C2979045), +2.49 riser; mouth 17.49 |
| USB-A A3/A4 | (63.76, 42.64), (63.76, 32.54) | Same, +2.38; mouth 17.38 |
| ETH1 | (63.67, 91.60) | Non-magnetic vertical RJ45 ≤ 13.0 + V24P05S (D-IO15); face ≤ 13.6 |
| ETH2 | (43.15, 91.41) | Same; face ≤ 13.7 |
| HDMI | (42.96, 107.07) | Vertical H15 (JLC C9900153431), +2.24 riser; mouth 17.24 (the shell must pass the 5.83 flex cut-out) |
| Button | (63.79, 108.11) = flex button-carrier centre | Cap on the flex dome (J31). SW1 / D20 are DNP. |
| Audio jacks | (43.4, 19.1), (64.65, 19.4) | Stock audio flex (unchanged) |

Moves against the 2026-10-01 grid: USB-C H +0.49 / O −0.21 in X, rows +0.4…+0.56; USB-A −0.18…−0.29 X, −0.06…−0.11 Y; ETH +0.65 / +0.17 X, −0.6…−0.7 Y; HDMI (+0.56, −0.33); button (+0.77, +0.08).

*Superseded grid (2026-10-01; face centres, mean of the board front scan and the plate scan, ±0.5):*

| Port | Position (X, Y) | Part (placeholder footprint) |
|---|---|---|
| USB-C C1–C3 (HDMI-side column) | X 42.6; Y 75.2 / 65.45 / 55.7 | Vertical 24P receptacle. Height chosen per §4.4. |
| USB-C C4–C6 (other column) | X 63.9; same Y | Same |
| USB-A A1/A2 | (43.3, 42.75), (43.3, 32.6) | Vertical USB 3.2 Std-A |
| USB-A A3/A4 | (64.05, 42.75), (64.05, 32.6) | Same |
| ETH1 | (63.5, 92.3) | **HanRun HR913790A** vertical magjack, 2.5G/5G (body 16.2 × 17.0, 16.9 tall). O side: the frame L-leg (16.8 wide) passes the body. |
| ETH2 | (42.5, 92.0) | **HanRun HR913790A**, same part. The H-side frame slot is only **15.6 × 13.0**, smaller than any vertical 2.5G magjack (all ≈ 16 × 13.5–17), and narrow non-magnetic jacks are still ≥ 13.45 × 15.9. So the jack is **set back**: its face sits ≥ 0.3 mm behind the frame back plane and only the plug (11.7 × 8 + latch) passes the 13.0 × 10.7 plate opening and the slot. Both jacks share one height, so ETH1 sits at the same plane. |
| HDMI | (42.4, 107.4) | Vertical type A |
| Power button SW1 | (63.02, 108.03) | PTS810 + printed clear cap. Power LED D20 at (63.0, 103.3). |
| Audio jacks | (43.4, 19.1), (64.65, 19.4) | On the stock audio-jack flex (J28) |

All new connectors are **straight**: their mating axis is normal to the board. Because the grid is the face centres, the mouths line up with the plate openings without any offset.

### 4.2 Plate openings (outer)

**Rev 2026-10-02 ≈ 10:15 ET** (all go straight through the curved skin, with no lands):

- USB-C 9.6 × 4.0 R 1.8 (shell 8.94 × 3.26 passes, 0.11 inside the flex cut-out).
- USB-A 14.0 × 6.0 R 0.6 (the shell passes).
- HDMI 15.6 × 5.7 R 1.0.
- ETH1 13.0 × 10.4, ETH2 13.0 × 10.7.
- Audio Ø4.8 (stock).
- Button Ø12.4 at (63.79, 108.11).
- Light windows re-centred on the scanned pads: HDMI (43.41, 113.09), ETH (53.41, 92.27), TB (53.36, 65.94), USB (53.46, 37.92), audio (43.39, 12.40) / (63.61, 12.40).
- Outer spot-faces at the USB-C columns (§4.7.3).

*Earlier table (2026-10-01/02 09:10):*

| Opening | Size | Notes |
|---|---|---|
| USB-C | 9.6 × 4.0, R 1.8 | ≈ 0.33 per side around an ≈ 8.94 × 3.26 shell. The receptacle shell passes through, so the mouth is flush with its land. |
| USB-A | 13.6 × 6.0 | |
| RJ45 | 13.0 × 10.7 | |
| HDMI | 15.4 × 6.0 | These pass the plug: 0.75–0.8 per side. |
| AC | Stock window, 34.55 × 24.65 | |
| Audio | Ø4.8 | |
| Button | Ø12.4 | |
| Light windows (since 2026-10-02) | Rounded slots through the skin | Over the flex light-guide pads: HDMI 7.0 × 1.6 at (41.5, 113.7), ETH 3 × 5 at (52.5, 91.9), TB 3 × 5 at (52.9, 66.3), USB 3 × 6 at (53.5, 36.5), audio 4 × 2.4 at (43.4, 13.0) / (63.9, 13.5). VERIFY against the stock icon art. The old Ø2.2 light-pipe bores are gone (`--flex none` rebuilds them). |

### 4.3 In-plane alignment

- Board face columns are square to the board (0.2°).
- The plate and frame outline fits read 1.0–1.3° in-plane. However, the opening centroids match the faces within ±0.45 (HDMI +0.88 is the worst).
- That is a relative in-plane error of ≤ 0.5° at registration accuracy. It is absorbed by the 0.3+ mm per-side clearances. **M-IOP1** confirms with calipers.

### 4.4 Port angle: estimate and decision (D-IO6)

> **Partly superseded (2026-10-02 ≈ 10:15 ET).** The flat lands and bosses below were removed because the stock flex must lie flat and bosses cannot fit inside its cut-outs. The angle evidence still holds. Heights now come from the measured D0 (§4.7.4), and the depth table below is obsolete.

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
  | ETH2 | 14.8 × 12.4 (collar 14.6 × 12.3, 0.8 wall) | H-side slot 15.6 × 13.0 |

- USB-C mouths sit flush with the land. USB-A, RJ45 and HDMI faces sit 1.2 mm behind the land, the same as the stock skin. Plug overmolds stop on a flat face, so plugs seat fully.
- The frame stays unmodified. Straight shells cross the frame plane within ≈ 0.25 mm of where the angled stock shells did, against ≥ 1.6 mm per-side slot clearance.

**Mouth/face depth below the plate crown** (from `io_plate_v2_A0_features.json`). The required connector height is D0 − depth, where D0 is the board-to-crown distance from M-IOF2.

| Port | Depth below crown |
|---|---|
| USB-C, H column | 1.55 |
| USB-C, O column | 1.58 |
| USB-A, H column | 3.13 |
| USB-A, O column | 3.35 |
| RJ45 | 3.07 / 3.11 (land −1.87 / −1.91); the **jack face is set back** behind the frame back plane, see §4.1 |
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

> **Rev 2026-10-02 ≈ 10:15 ET:** `build_plate.py` was rewritten.
> - D0 parameters (`D0_CROWN` 18.0, `D0_EDGE` 16.5, `D0_EDGE_U` 15.5) set CASE_R 82.03; the board top is at z −19.2.
> - Constant 1.2 wall with a smooth inner face. No lands, bosses or ramps.
> - Port grid from the flex trace JSON.
> - 0.2 glue pocket (outline + 0.2), 19 LED pockets and a button-carrier pocket (wall 0.35).
> - Ø2.4 locating pins, Ø1.4 ear pins, USB-C outer spot-faces, rim notch X 76.0–81.5.
> - The `stack`, `parts`, `flex_check` and `led_check` blocks are in the features JSON.
> - 8.5 cm³, one solid, bbox 52.2 × 163.2 × 11.1.
> - `section_plot.py` now shows the full stack down to the board, with the risers. `--flex none` is retired.
>
> The bullets below describe the 09:10 build.

- Outline 51.9 × 163.1, R 11.5, at (53.19, 77.07). Perimeter rim 1.2 × 3.0.
- **Constant 1.2 wall:** the outer face is a cylinder (`CASE_R` 82; None = flat) and the inner face is the concentric cylinder R0 − 1.2, as on the stock plate.
- **Flat port lands** (§4.4) are pockets on the outside, backed by bosses on the inside. The bosses stand 0.6–2.0 proud of the inner skin at their inboard edge. Since 2026-10-02 that inboard edge is **ramped 60–72°** (steep enough to keep ≥ 0.8 under the land edge), so a flex can drape over it.
- **821-2222 flex seat (`FLEX = "stock"`, default):**
  - Glue pocket 0.20 deep over the traced flex outline + 0.3 (1.0 wall left). `FOAM_T` = 1.0 allowance behind the flex (TO MEASURE).
  - Rim notch at the flex neck: X 74.6–81.5, Y 27.6–46.7. The neck runs to the IC tab (3 LED MCUs) beside the O column, then to the ZIF.
  - Locating pins Ø2.7 × 2.5 at the frame holes HOLE_C1 (52.93, 75.41) and PIN_C3 (54.49, 19.23). They pass the flex holes and locate both plate and flex. Length VERIFY.
  - No collars (they would pierce the flex rims) and no light-pipe bosses. Six light windows sit over the flex pads (§4.2).
  - Audio bosses shrunk to Ø7.0 (land Ø6.4) so they pass the flex's Ø7.4 audio holes.
  - The mirrored clip at (76.8, 30.3) collides with the flex neck and is dropped, leaving 7 clips. The stock clip points stay.
  - `--flex none` rebuilds the pre-flex variant with collars and light pipes.
- Frame-screw relief Ø6 × 0.6. ETH2 open by default (`--eth2 blank` for the single-Ethernet variant).
- One solid, ≈ 9.0 cm³, bounding box 52.2 × 163.1 × 11.1.

| File | Content |
|---|---|
| `io_plate_v2_A0.step` / `.stl` | **Rev A0 plate, ETH2 open** (2 × RJ45) |
| `io_plate_v2_A0_eth2blank.step` / `.stl` | Old variant with ETH2 blank (single-Ethernet build) |
| `io_plate_v2_A0_openings_backview.dxf`, `…_frontview.dxf` | Planform. The front view is in the KiCad x frame. |
| `io_plate_v2_A0_features.json` | Per-feature report |
| `io_plate_v2_A0_preview.png`, `…_iso_inner.png`, `…_section.png` | Previews. The section now shows the constant wall, ramped bosses, flex, foam and a schematic frame. |
| `flex_821-2222_trace.dxf` / `.json` | **Flex trace from the flatbed scan (rev 10:15 ET)** (plate-facing side, back view): outline, cut-outs, holes, light-guide pads, silver frames, 19 LEDs, button ring/dome, tail + 14 contacts, `IGNORED_BLACK_TAB`, reference plate/opening/window/LED-pocket layers |
| `flex_821-2222_scan_vs_photo_deltas.md` | Delta table, scan trace against the 09:06 photo trace |
| `flex_821-2222_check.png` | Flex trace against our ports, bosses and frame slots, with the clearance numbers |
| `io_flex_foam_insulator_A0.dxf` | Foam / Formex die-cut (scan outline): flex outline, minus the flex cut-outs + 0.3, holes + 0.5 and the button ring + 0.5 |
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
  - MJF minimum wall ≈ 0.8 mm (1.0 recommended). The plate uses: skin 1.2 (1.0 under the flex glue pocket), rim 1.2, land under-thickness 1.0 (≥ 0.8 at the ramped boss edges), locating pins Ø2.7, clip tabs 1.2. Collars and light-pipe bosses only in the `--flex none` variant.
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

### 4.7 Stock photos 2026-10-02: board edge, plate inside, 821-2222 flex (≈ 09:10 ET)

Sources: two edge-on photos of the stock I/O board (one with a cm ruler), the stock plate seen from inside, and the 821-2222 flex laid flat next to a cm ruler. Photo analysis is in `bracket/io_stock_photos/`.

**Edge photos [Estimate; perspective-corrected, ±10–15 %]**

| Item | Estimate | How |
|---|---|---|
| Stock board thickness | **≈ 2.0 mm (1.8–2.2)**, not 1.6 | 30 px at 14.6 px/mm (ruler, photo 2). 70 px against a Ø6.3 cap can (≈ 33–35 px/mm, photo 1). |
| Black plastic shroud over the port group | ≈ 13–15 mm above the board top, ≈ 85–95 mm long (USB-A…HDMI span) | Photo 2 corrected for the shroud sitting ≈ 30 mm behind the front edge |
| Metal cover on top | ≈ 5.5–6 mm side wall | Both photos agree |
| **Stack top above the board top** | **≈ 20–23 mm** | – |
| Tall parts in front of the shroud | Polymer cans Ø6.3 × ≈ 5.5–6 (with base); 2 grey blocks (inductor/module) ≈ 4–6 tall, ≈ 9 and ≈ 12 wide; SMD ≤ 1.5 | Photo 1 |

**M-IOF2 refined [Estimate].**
- The stock port faces sit at about the stack top. So **D0 (board top to plate crown) ≈ 22–25 mm**: the stack, plus about 1.5 for the USB-C mouth depth under the crown. Before these photos, D0 was only bounded below (≥ 20.5).
- The frame back plane sits ≈ D0 − 3.3: skin 1.2 + flex 0.12 + foam 1.0 + frame ≈ 1.0 (TO MEASURE). That puts it ≈ 18.7–21.7 above the board.
- **ETH set-back:** the HR913790A face (16.9) sits **≈ 1.8–4.8 behind the frame back plane**, so the 0.3 gate passes over the whole range. It sits **≈ 3.2–6.2 below the plate land** (D0 − 1.9 − 16.9). The plug stands ≈ 8 out of the jack face, so ≈ 1.8–4.8 of it remains outside the land.
  - Fine up to D0 ≈ 24.
  - Above that, the latch gets hard to reach. Raise both jacks on a 2–3 mm spacer, or stay with the 5 mm limit in §10.
- **New top mechanical risk:** required heights become USB-C ≈ D0 − 1.55 = **20.5–23.5**, USB-A ≈ 18.7–21.9, HDMI ≈ 18.6–21.6. Typical vertical receptacles are much shorter [Unverified: catalogue check pending].
  - USB-C plugs need the mouth within ≈ 0.6 of the land.
  - **Measure D0 by caliper before any connector or footprint choice** (§12).
  - If D0 is confirmed, the options are tall/extended vertical parts or a raised port carrier. Both need a separate decision.
- **Board thickness:** our stackup is 1.6. If the board is located on the stock bosses from the B side, F sits 0.4 lower than stock and every required height grows by 0.4. Either order 2.0 mm or add 0.4 to the heights; VERIFY which face touches the bosses.

**Plate inside (stock).**
- The inner face is curved, concentric with the outside.
- Every opening has a raised collar.
- Round bosses sit at the frame holes HOLE_C1 / PIN_C3.
- The flex is glued along the inside, with its IC tab peeled up beside the O column.

The new plate copies all of this except the collars (see below).

**821-2222 flex trace (`flex_821-2222_trace.dxf/.json`, `flex_821-2222_check.png`).**
- **Method:** homography fitted to 16 stock port and frame-hole centres, rms 0.41 mm. Scale 18.3–18.6 px/mm, which matches the ruler (17.9–18.7). Positions ±0.4, sizes ±0.3; **VERIFY by caliper** (M-IOW1).
- The photo shows the **plate-facing side**: no mirror, so the LEDs and silver light guides face the plate.
- **Shape:** frame-shaped, 51.7 × 106.8 (X 28.3–80.0, Y 9.9–116.7). Port cut-outs follow the stock layout.
  - HDMI 15.8 × 6.2.
  - ETH 13.5 × 11.9 (H) and 14.3 × 11.1 (O).
  - TB 9.1–9.8 × 5.8–6.4.
  - USB-A 14.3–14.7 × 6.3–6.5.
  - Audio Ø7.4 / Ø7.5.
  - Frame-hole clearances Ø3.4 / Ø4.5 / Ø4.6.
- **Lighting parts:**
  - About 30 bright chips around the three silver light-guide frames (ETH, TB, USB-A). Most are side-view LEDs (≈ 4.7 × 1.1); a few may be reflector tabs.
  - 6 light-guide pads: HDMI (41.5, 113.7); ETH (52.5, 91.9); TB (52.9, 66.3); USB (53.5, 36.5); audio (43.4, 13.0) and (63.9, 13.5).
- **Button:** dome Ø4.5 in an Ø11.8 ring at (62.25, 107.7), with two LEDs flanking it. That is the stock power LED, so D20 is redundant when a flex is fitted.
- **Neck and tail:** the neck (X 75–80.5, Y 28–46) runs to the rigid IC tab with the 3 LED MCUs (X ≈ 77–94, Y ≈ 32–68, beside the plate). The tail then goes to J31.
- **Light holes:** the plate windows sit on the pad centres. **Recommendation (D-IO10): drop the TLC59116 light pipes D21–D26** (now DNP in the schematic). The flex lights every group and icon, and **the frame centre bar blocks 5 of the 6 old pipe positions**: ETH, both TB, USB and audio sit on solid frame, and HDMI is on a slot edge. J31 stays the primary path for button and lights.

**Our ports against the flex cut-outs.**

| Port | Through-part | Min margin per side | Note |
|---|---|---|---|
| USB-C C1 / C2 / C3 | Shell 8.94 × 3.26 | −0.07 / −0.11 / −0.11 | Flex holes sit ≈ 0.25 inboard of our X 42.6 / 63.9 |
| USB-C C4 / C5 / C6 | Shell 8.94 × 3.26 | −0.05 / +0.19 / +0.32 | Same |
| USB-A ×4 | Plug 12.0 × 4.5 (the face is behind the flex) | +0.47 … +0.71 | OK |
| ETH1 / ETH2 | Plug 11.7 × 8.2 | +0.66 / +0.73 | Our centres are 0.7–0.8 higher in Y; the flex edge shows ≤ 0.6 inside the opening (cosmetic) |
| HDMI | Plug 13.9 × 4.45 | +0.29 | X offset 0.66 |
| Audio ×2 | Ø4.8 opening | +1.0 | OK |
| Button | Dome inside our Ø12.4 | 0.85 off centre | OK |

- **Plan view:** everything clears except the USB-C shells, which are marginal (≤ 0.11 interference, inside the trace accuracy). Cheapest fix if the caliper confirms: **shift both USB-C columns ≈ 0.25 inboard** (X 42.85 / 63.65). Frame-slot margins stay ≥ 1.0.
- **The real conflict is in Z.** Our land bosses exist because straight connectors sit in a curved plate. They are 1.0–1.8 per side larger than the flex cut-outs, and the TB / USB-A bars between ports lie across them. They stand **1.2 (USB-C), 1.6 (ETH), 1.7–1.9 (USB-A) and 2.0 (HDMI)** proud of the inner skin. A stock flex glued flat would have to fold that far into each frame slot, with only ≈ 0.25–0.4 of run at the slot edge.
  - The plate ramps the boss edges at 60–72°, which helps but does not remove the fold.
  - Shifting ports cannot fix this.
  - Trimming the flex means 1.0–1.8 per side plus the bars, cutting into the margins where LED traces run. That is irreversible on an obsolete part; **not recommended**.
- **Recommendation (D-IO12):**
  - Rev A0 plate as built: glue pocket, windows, pins, ramps, rim notch. Gently fit-test the stock flex, and stop if it does not lie flat.
  - Plan an **A1 replacement flex**: 2-layer polyimide with the stock outline and cut-outs = our bosses + 0.3 (DXF layer `A1_FLEX_CUTOUTS_PROPOSED`). Side-view LEDs and pads at the traced positions, a dome at the button, and a 14P 0.5 tail into J31 with our own pinout (PWRBTN, GND, 3V3_SB, LED anode, LED channels from U80).
  - Cost ≈ $40–90 for 5 plus parts [Estimate]. It also removes the unknown stock LED-MCU protocol.
- **Button:** with any flex fitted, the dome sits behind the Ø12.4 opening, so the cap presses the dome (J31) and cannot reach SW1. SW1 / D20 remain the no-flex fallback. **The dome needs a backstop** (stock: unknown, M-IOW3).

**Insulation (D-IO13).**
- The stock black shroud with its metal cover is Apple's port housing / EMI can. Our board has none.
- Nothing of ours comes near the frame except the port shells, which should touch it (chassis GND), and the ETH jack tops, which have grounded shields and sit ≥ 1.8 below the frame.
- The PA12 plate is itself an insulator. The only metal-to-circuit interface is the flex LED side against the frame, and the stock **1 mm foam** covers it.
- **So: no printed shroud.** Reuse the stock foam, or cut a new one from `io_flex_foam_insulator_A0.dxf`:
  - 1.0 closed-cell PE/PORON with PSA, ≈ $2–5 laser-cut; or
  - 0.25 Formex GK-10 / fish paper (UL94 V-0), ≈ $3–8 one-off, < $1 in volume [Estimate].
- Add Kapton dots only if a caliper check finds anything < 0.5 from the frame.

### 4.7.1 Flex 821-2222-A from the flatbed scan (2026-10-02 ≈ 10:15 ET; supersedes the photo trace above)

Source: Aidan's flatbed scan (200 dpi, flex flat on the glass, L-shaped ruler). Scripts and intermediate images are in `bracket/io_stock_photos/scan/` (`ticks.py`, `frameF.py`, `rr110.py`, `bake_scan.py`, `deltas.py`, `overlay.py`).

- **Scale:** both ruler arms are mm scales (no separate inch scale was found). The ticks give **7.8935 px/mm across** (rms 0.4 px over 147 mm) and **7.8735 px/mm along** (rms 0.6–0.7 px over 209 mm). The two agree to 0.24 %, and the nominal 200 dpi is 7.874, so there is no perspective. Use the per-axis values.
- **Flatness:** the long frame edges are straight to 0.03 mm and parallel, so the frame lay flat. Only the free tail drifts about 3° in-plane; it is idealised as straight.
- **Idealisation:** straight edges, arcs and symmetric groups. The TB, USB-A and audio cut-outs share one size and one column pair; the rows are the measured means. Edges were read at threshold 110–150 (±0.15 mm). The **wide black stiffened tab beside the tail is ignored**: it is glued to the metal plate and sits on DXF layer `IGNORED_BLACK_TAB` for reference only.
- **Placement in the plate frame:** rotation 0, plus the least-squares translation onto the stock port grid (rms 0.58; a free rotation of 0.65° would give 0.48, inside the grid's ±1° uncertainty). Flex holes against frame holes: HOLE_C1 Δ (+0.25, +0.12); HOLE_C2 Δ (−0.03, −0.22).
- **Result** (`flex_821-2222_trace.json/.dxf`, plate frame):
  - Frame 45.60 wide (X 30.53–76.13), Y 10.0–115.9, plus the neck X 76.13–80.58 / Y 28.22–47.13.
  - Cut-outs: TB 9.83 × 6.10 R 2.25 at X 43.09 / 63.69, Y 75.76 / 65.84 / 55.97. USB-A 14.66 × 6.39 R 1.64 at X 43.12 / 63.76, Y 42.64 / 32.54. ETH2 14.14 × 11.37 at (43.15, 91.41). ETH1 14.20 × 10.73 at (63.67, 91.60): the two ETH heights really differ. HDMI 16.14 × 5.83 at (42.96, 107.07). Audio Ø8.05 at (43.06, 19.03) / (63.74, 19.03).
  - Holes: HOLE_C1 Ø3.3 (low confidence, partly shadowed) at (53.18, 75.53); HOLE_C2 Ø5.08 at (53.35, 58.16); PIN_C3 Ø5.67 at (53.38, 19.27). Two button-carrier ear holes Ø1.8.
  - Button carrier ring Ø15.57 at (63.79, 108.11), dome Ø≈4. **19 LED chips** (≈ 1.0–1.25 × 3.6–5.2) are on the plate-facing side, 2 of them flank the button. 6 light-guide pads and 3 silver frames.
  - Tail: 4.75 wide, ≈ 83 mm from the neck to the end, contact end 8.25 wide with 14 × 0.5 gold contacts (exposed ≥ 1.8 long).
- **Deltas against the 09:06 photo trace** (full table: `mechanical/io_plate_v2/flex_821-2222_scan_vs_photo_deltas.md`). The overall scale agrees (similarity fit 1.0033, rms 0.30), but individual features moved:
  - TB cut-outs +0.05…+0.75 wider, centres +0.12…+0.43 higher in Y; the H column is 0.12–0.35 farther outboard in X. USB-A +0.2…0.4 in Y.
  - HDMI (+1.22, −0.34), 5.83 tall (was 6.23). ETH +0.5 X. Audio holes Ø8.05 (was 7.4/7.5).
  - Button ring Ø15.57 (was 11.8) at +1.54 X. HOLE_C2 Ø5.08 (was 4.5), PIN_C3 Ø5.67 (was 4.6).
  - The frame is 45.6 wide with straight edges (the photo outline was 51.7 wide including the wavy edges and neck). 19 LEDs instead of the 34 photo "chips" (the photo also counted reflector tabs).

### 4.7.2 Fit check against the stock flex (scan trace)

`flex_821-2222_check.png`; numbers in `io_plate_v2_A0_features.json` (`flex_check`, `led_check`).

| Item | Result |
|---|---|
| USB-C shells 8.94 × 3.26 in the 9.83 × 6.10 cut-outs | **+0.44 / +0.45 per side** once the columns move to X 43.09 / 63.69 (+0.49 / −0.21). At the old X 42.6 the H column was −0.05 (interference). |
| USB-A shells (13.2 × 5.7 assumed) in 14.66 × 6.39 | +0.34 per side |
| HDMI shell (15.2 × 5.5 assumed) in 16.14 × 5.83 | +0.17 per side. **The receptacle shell must be ≤ 15.4 × 5.6 to pass**; otherwise see the fallback in §4.7.4. |
| RJ45 plug 11.7 × 8.2 in the ETH cut-outs | +1.22 / +1.25 |
| Audio (stock jacks, stock plate positions) | Ø4.8 opening +1.28 / +0.64; jack nose (Ø6 assumed) +0.68 / **+0.04**. AUD_O is the flex hole that sits 0.91 off the stock plate hole: check M-IOW1. |
| Old land bosses against the cut-outs | **Impossible.** The room inside the cut-outs is ≤ 0.45 per side (USB-C), 0.34 (USB-A) and 0.17 (HDMI), and the HDMI cut-out (5.83) is smaller than the old opening (6.0). So the plate now has **no bosses**: the inner face is flush, and the flex lies flat. |
| Locating pins Ø2.4 in the flex holes | C1 +0.18 radial; C3 +0.53 |
| LEDs against plate features | 17 clear. The 2 button LEDs sit under the button cap by design. No LED is under a pin, clip, rim, screw relief, spot-face or window edge. |

### 4.7.3 Plate redesign (rev 2026-10-02 ≈ 10:15 ET)

- **No lands and no bosses.** Every opening goes straight through the curved 1.2 skin. The inner face is one smooth cylinder (outer R 82.03, inner R 80.83, from D0), and the flex lies in a 0.2 glue pocket (outline + 0.2, which also locates the flex to ±0.2).
- **Port grid = the flex cut-out centres** (§4.1). The USB-C columns move to X 43.09 / 63.69. Openings: USB-C 9.6 × 4.0; USB-A 14.0 × 6.0 (the shell passes); HDMI 15.6 × 5.7; ETH1 13.0 × 10.4; ETH2 13.0 × 10.7. Audio stays at the stock positions.
- **Pockets for the plate-side parts of the flex.** There are 19 LED pockets (chip + 0.25 per side) and a Ø16.17 pocket for the button carrier, each 0.70 above the flex face (LED/carrier height 0.6 assumed, TO MEASURE). They leave a 0.35 wall.
- **Pins:** Ø2.4 × 2.5 locating pins at the frame holes (52.93, 75.41) and (54.49, 19.23). Ø1.4 × 0.8 ear pins in the button-carrier ear holes locate the button end.
- **Spot-faces:** shallow flat spot-faces on the outer face at the two USB-C columns (12.8 × 26.8, floor z −0.68 / −0.70, wall ≥ 0.6) let a USB-C overmold get within 0.62–0.67 of the mouth. USB-A and HDMI cannot get spot-faces: the USB LED and the HDMI LED/window sit where their overmolds land.
- **Unchanged:** rim notch X 76.0–81.5 / Y 27.7–47.6 for the neck. Light windows re-centred on the scanned pads. The mirrored clip at (76.78, 30.3) is dropped (the stock clip points stay, 7 clips). Frame-screw relief.
- **Plug seating is now set by the curvature**, not by lands:
  - The mouth is flush at the outboard edge of each shell, which is the lowest point of the curved face over the port.
  - The plug overmold stops on the highest point under it.
  - The difference is the plug recess: USB-C 0.62–0.67 (with the spot-face), USB-A 1.69–1.78, HDMI ≈ 1.96. Treat USB-A and HDMI as fit-test items.
- One solid, 8.5 cm³. The `--flex none` mode, collars and light-pipe bosses are retired.

### 4.7.4 Measured D0, stack-up and connector heights

**Input (Aidan, 2026-10-02):** D0 = I/O PCB top to the plastic cover's inner surface = **18.0 at the crown**, **16.5 at the farthest edges**. It replaces the 22–25 photo estimate.

- **Curvature:** the 16.5 reading is taken to be at |u| ≈ 15.5 from the centre (the outer edges of the USB-C/TB openings). Then R_inner = (15.5² + 1.5²)/(2 × 1.5) = **80.83**, so R_outer = 82.03, which matches the case-cylinder estimate. If the 16.5 was read at the plate edge (|u| ≈ 25), R would be ≈ 210 and every height below changes by up to 1.5 mm. **Confirm where it was read (M-IOD0).**
- **Stack-up (z from the outer crown, at the crown):**
  - Outer face 0.
  - Inner face −1.2 (stock wall assumed 1.2, M-IOS1).
  - Glue pocket 0.2, then PSA 0.05 + flex 0.12. The board-side face of the flex is at −1.17.
  - Foam 1.0, then the metal frame 1.0 (assumed concentric). The frame back plane is at −3.37 at the crown and ≈ −5.3 at the RJ45 outboard edges.
  - **Board top −19.2.** D0 at the port columns is 17.33–17.38.
- **Required heights:** board top to mouth, with the mouth flush at the outboard shell edge.

| Port | Needs | Mouth below crown | Plug recess | Chosen part (JLC/LCSC) | Part height | Riser |
|---|---|---|---|---|---|---|
| USB-C C1–C3 (H) | **17.90** | 1.31 | 0.62 | **FG-ST-C-24P-VT-SMT-15.0, LCSC C51911913** (24P vertical SMT, the tallest catalogue part found) | 15.0 | **+2.90** |
| USB-C C4–C6 (O) | **17.82** | 1.38 | 0.67 | same | 15.0 | **+2.82** |
| USB-A A1/A2 (H) | **17.49** | 1.71 | 1.69 | **kinghelm KH-3.0AF180WJ-15JB, LCSC C2979045** (USB 3.0 9P vertical THT; LCSC stock low. Alternatives: CHIN-BAN USB30-AF-006 JLC C50285702, Kangmo CMUSB661034A) | 15.0 | **+2.49** |
| USB-A A3/A4 (O) | **17.38** | 1.82 | 1.78 | same | 15.0 | **+2.38** |
| HDMI | **17.24** (the shell passes the flex) | 1.96 | 1.96 | **"HDMI_180_H=15mm", JLC C9900153431** (JLC-assembly vertical HDMI; confirm the datasheet and the shell size ≤ 15.4 × 5.6). Alternative: HOAUC HYC79-HDMIA19-105 C711353 (10.5). | 15.0 | **+2.24** |
| HDMI fallback (the shell does not pass 5.83) | face ≤ 15.97 | – | ≈ 3.2–4.2 | the same part directly on the board | 15.0 | none (a poor plug seat) |
| RJ45 ETH1 / ETH2 | **face ≤ 13.6 / 13.7** (≥ 0.3 behind the frame back plane; the body cannot pass the frame slot or the flex) | – | – | **non-magnetic vertical RJ45 ≤ 13.0** (candidates, heights TBC: Lingqiang ZJLQ-RJ45-SMD-PCB125-8P8C C55547809, KRJ-18111NL) + **Jansum V24P05S 2.5G discrete magnetics** (LCSC C20071250, 24-pin SMD, 15.1 × 10.0 × 4.0; verify) | ≤ 13.0 | none |

- **Catalogue check:** no vertical USB-C, USB-A 3.0 or HDMI receptacle taller than ≈ 15 mm was found at JLC/LCSC (USB-C 9.3–15.0, USB-A 3.0 vertical 11.5–15, HDMI 8.5–15). **HR913790A (16.9) no longer fits**: vertical magjacks are 16.5–16.9 tall, and the face must be ≤ 13.6.
- **Proposal D-IO14: port risers.**
  - Mount the USB-C, USB-A and HDMI receptacles on small **riser PCBs, one per column group**: a USB-C ×3 riser on each side, a USB-A ×2 riser on each side, and an HDMI riser.
  - Each riser stands on a fine-pitch board-to-board mezzanine. Target Δ: USB-C 2.85 (e.g. 0.8 riser + 2.0 stack), USB-A 2.4 and HDMI 2.2 (0.8 + 1.5 stack, mouth within ±0.15 of flush).
  - The mezzanine must carry DP HBR3 (8.1 Gb/s), USB 10 G, USB2, CC/SBU and 5 V / 3 A per port. Use a Hirose DF40-class or Molex SlimStack-class high-speed pair and verify its SI rating, or a solder-down castellated/LGA riser.
  - Cost ≈ +$15–30 per board in connectors and riser PCBs [Estimate], plus SI risk on the 10 G and HBR3 lanes.
  - Raising the whole board does not work: the board is 101 wide inside an R ≈ 81 case cylinder, so its edges would hit the wall.
  - Ordering a 2.0 board does not help unless our board top sits lower than the stock top (M-IOS2).
- **Proposal D-IO15: RJ45.** Replace HR913790A with a non-magnetic vertical RJ45 ≤ 13.0 plus discrete 2.5G magnetics per port. This costs ≈ +$1–2 and ≈ 15 × 10 mm of B- or F-side area per port. The footprint and nets change before routing.
- **KiCad (done):**
  - Ports moved to the new grid: J11–J16, J21–J24, J25/J26, J27.
  - SW1 and D20 moved to the ring centre and set DNP (the flex dome and LEDs replace them). D21–D26 are DNP.
  - D22 moved to X 53.42 to clear J26.
  - Part numbers and heights are in the value fields. Footprints remain placeholders; the RJ45 and riser footprints wait for D-IO14/15.
  - DRC 0 / 0 / 0.

---


### 4.7.5 Tilted column risers (D-IO14, rev 2026-10-02 ≈ 10:50 ET)

> **Superseded 2026-10-02 ≈ 12:45 ET by §4.7.9 (D-IO16 flex port modules, axes normal to the plate).** Kept for the record.

**Rev 12:00 ET: measured stock tilt 12.5° (M-IOT2, Aidan 11:47 ET).** The stock ports lean **outward 12.5° from vertical** (taken as the board normal), the other column mirrored. `build_plate.py` now uses `TILT_OVERRIDE_DEG = 12.5` for USB-C, USB-A and HDMI; everything downstream (plate holes, seats, stack, `risers.json`, riser PCBs, main-board JR/pogo/cradle holes, section) is regenerated from it.

- **Curvature vs tilt.** At the port columns (|u| ≈ 10.1) the plate normal is 5.3–5.5° for R 110 (6.9° even for the 83.8 case cylinder). A 12.5° normal would need R ≈ 47, which no measurement supports (D0 → 110, phone scan → 102, case → 84). So **the stock ports are not normal to the cover; they sit 7.0–7.25° off-normal** and Apple angled them for another reason [Inference]: splaying the cables / plugs of the two columns apart (overmolds 12–21 mm on a 20.6 mm column pitch), easier plug access from the side, or matching an internal frame/flex geometry. A second possibility is that the stock cover has local flat seats around the openings (the phone-scan residual map shows ≈ +1 mm rings round the C/A/HDMI openings, but it is below the scan's reliability) — **M-IOT3**. Please also confirm the 12.5° was taken against the board, not gravity.
- **Axis.** Each axis still passes through its flex cut-out centre at the flex mid-plane (the flex must lie flat and is the tightest layer). `AXIS_BALANCE` shifts an axis along X to equalise the worst flex / foam / frame-slot margins (HDMI −0.22). `AXIS_SHIFT_OUT = {"USBA": 0.35}` moves the USB-A axes outboard so the H/O USB-A risers clear each other.
- **Mouth.** Rule kept: no point of the shell mouth proud of the outer face (`MOUTH_CLR` 0.05). With the face 7° off the surface, one edge is flush and the other deep.
- **Plug seats.** An off-normal mouth makes the plug overmold land on the skin before it seats. `TILT_SEAT = True` cuts a flat seat perpendicular to the axis (overmold + 2 × 0.25) on the OUTER face only, floor ≥ 0.6 of skin left (the inner face stays smooth). This recovers ≈ 0.6 mm; a full seat would need > 1.2 skin.

| Column | Tilt (off normal) | Mouth centre above board (was) | Mouth recess, flush edge / deep edge | Overmold stand-off, no seat → seat | Flex X margin (untilted) | Foam / frame-slot min margin |
|---|---|---|---|---|---|---|
| RC_H C1–C3 | −12.5° (−7.23°) | 18.03 (18.59) | 0.05 / 1.17 | 1.31 → **0.72** | 0.39 (0.45) | 0.48 / 0.69 |
| RC_O C4–C6 | +12.5° (+7.03°) | 18.01 (18.55) | 0.05 / 1.14 | 1.27 → **0.68** | 0.39 (0.45) | 0.48 / 1.12 |
| RA_H A1, A2 | −12.5° (−7.25°), axis −0.35 | 17.65 (18.49) | 0.05 / 1.67 | 1.75 → **1.16** | 0.32 (0.73); Y 0.35 | 0.65 / 1.96 |
| RA_O A3, A4 | +12.5° (+6.99°), axis +0.35 | 17.63 (18.44) | 0.05 / 1.61 | 1.69 → **1.10** | 0.32 (0.73); Y 0.35 | 0.65 / 1.29 |
| RH HDMI | −12.5° (−7.17°), axis −0.22 | 17.46 (18.41) | 0.05 / 1.92 | 2.02 → **1.43** | 0.19 (0.47); Y 0.17 | 0.52 / **0.19** |

- **Flex / foam / frame.** The tilted shell crosses the flex at 7° so its footprint grows by sw (1/cos 7° − 1) + t tan 7° ≈ 0.06–0.10 and drifts 0.13 mm per mm of depth. **The stock flex still lies flat; every shell clears its cut-out** (min 0.17 on HDMI in Y, unchanged; X ≥ 0.19). The foam die-cut (+0.3) clears by ≥ 0.48. The I/O-frame slots clear by ≥ 0.19 (HDMI inboard edge; without the balance shift it was −0.03 = interference). The frame slot positions come from a photo, so HDMI is the one to check (M-IOF2).
- **Risers (rev 12:00 ET).** 12.5° pulls each connector base ≈ 1.3 mm further inboard than at 5.4°, so the H and O risers' inboard edges collided (USB-C 0.9 mm, USB-A 1.2 mm overlap):
  - riser_c: x′ −8.4…**+7.3** (was +8.4), the inboard pogos move to x′ 5.5 (y′ ±15.0, ±3.4), H13 notches r 3.0 re-centred on the standoff at the tilted position. H/O edge gap **1.29**.
  - riser_a: x′ −13.1…**+7.7** (shell pegs + 0.3) plus the 0.35 outboard axis shift. H/O edge gap **0.67** (tight: one shared printed twin cradle for RA_H + RA_O is suggested).
  - riser_a DF40: the underside gap at the outboard strip fell to 2.7 (< 4.4 for the C-fold), so the DF40C-50 moves to the **riser top (F)** and the jumper makes a U-turn round the outboard edge to JR3/JR4, now at (28.96, 31.59) / (77.93, 31.59) (H side kept clear of the speaker keep-out).
  - Underside gaps: riser_c 4.4–7.8 (DF40 6.2 ✓), riser_a 2.0–6.5, riser_hdmi 3.0–8.3 (DF40 5.65 ✓).
  - Pogo working heights split into two lengths: **P-S 4.8** (outboard row) and **P-L 7.4** (inboard row); 7.4 is above the old 4.6–7.3 class, so a longer pogo is needed for the inboard row.
  - Main board: JR/PG/cradle holes follow `risers.json`. **D21–D26 (DNP light-pipe LEDs) were removed**: their spots now sit under the riser inboard edges, and the flex lights the icons anyway (TLC59116 OUT9–14 spare). DRC 0, ERC 0, riser DRC 0 ×3.
  - Neighbours: RH inboard edge now reaches X 57.5 (J30 JST SH under it with ≥ 7.5 gap: cradle window). RH −Y edge stays 0.34 / 0.15 mm in plan from the J26 / J25 RJ45 bodies (unchanged, tight). RC/RA risers 0.33 apart in Y (unchanged). Riser outboard edges at X ≥ 32.5 are far below the frame and plate rim; case-wall clearance is not the limit.

*(Text below this point describes the 10:50 ET radial-tilt build; numbers for tilt, mouth heights, gaps and riser widths are superseded by the table above.)*

**Curvature from D0.** Aidan took the 16.5 mm reading at the outer edge of the outermost port columns. In the scan trace, the outer edges are the HDMI cut-out (X 34.89, |u| 18.30) on the H side and the USB-A cut-out (X 71.09, |u| 17.90) on the O side, so |u| = 18.10 on average. Then R_inner = (u² + 1.5²) / (2 × 1.5) = **109.97**, R_outer **111.17**. That is flatter than the old 82.0 (case-cylinder) assumption, so the I/O cover is not on the case cylinder. The value is parametric in `build_plate.py` (`D0_EDGE_SIDE` = "mean" / "H" / "O" / a number).

**Tilt.** Each port axis is radial through its flex cut-out centre at the flex plane:

| Column | Ports | Tilt | Mouth centre above board top | Mouth recess | Shell-in-flex-cut-out margin |
|---|---|---|---|---|---|
| RC_H | C1–C3 | −5.27° | 18.59 | 0.14 | 0.45 |
| RC_O | C4–C6 | +5.47° | 18.55 | 0.14 | 0.45 |
| RA_H | A1, A2 | −5.25° | 18.49 | 0.25 | 0.34 |
| RA_O | A3, A4 | +5.51° | 18.44 | 0.25 | 0.34 |
| RH | HDMI | −5.33° | 18.41 | 0.31 | 0.17 |

The stock-photo estimate was 6.4–7.3° outward per column (§4.4). That is 1–2° more than the surface normal. Setting `TILT_OVERRIDE_DEG = 7.0` forces the stock value instead.

**Plate.** The USB-C / USB-A / HDMI openings are now straight through-holes along each tilted axis, centred on the flex cut-out at the flex plane. The mouth is tangent to the outer face, so the USB-C overmold spot-faces are gone. The inner face stays smooth and the flex fit is unchanged (the axis passes through the cut-out centres).

**Riser stack** (per column, `kicad/macpro62-io-risers/risers.json`):
- Connector on the riser top: USB-C SHOU HAN TYPE-C 24PLT-H10.5 (C3151750, 10.5), USB-A kinghelm KH-3.0AF180ZJ-11.5JB (C2979037, 11.5), HDMI HOAUC HYC79-HDMIA19-105 (C711353, 10.5).
- Riser PCB: JLC 4-layer 1.6 (JLC04161H-7628), ENIG. One design per type. The O-column copy is the same PCB rotated 180°.

| Riser | Size (mm) | Underside gap above the board | Link | Power |
|---|---|---|---|---|
| riser_c (× 2) | 16.8 × 34.2, two r3 notches for the I/O-frame centre standoff H13 | 5.7–7.3 | DF40C-80DS-0.4V(51) (C312960, $0.76 @10) | 6 × VBUS + 2 × GND SMD pogo pins (≥ 3 A each, working height 5.9–7.1) |
| riser_a (× 2) | 21.4 × 21.7; the DF40 sits in the outboard strip because the USB-A THT field blocks the underside | 4.1–6.2 | DF40C-50DS | VBUS 1.5 A/port through 5 DF40 pins |
| riser_hdmi | 24.8 × 14.4 | 5.2–7.5 | DF40C-40DS | — |

- **Link.** A riser-side DF40C receptacle sits directly above a main-board DF40C receptacle (JR1–JR5). They are joined by a C-fold 2-layer FPC jumper with a DF40C-xxDP plug on each end (mated 1.5 + 1.5, static bend R ≥ 1.2 in the 4.4–6.5 gap). Pinning is G-S-S-G with 90 Ω coplanar pairs over an L2 ground.
- **Mounting.** One printed PA12 wedge cradle per riser (JLC3DP with the plate). It is fixed to the main board with 2 × M2 (NPTH H21–H30) and holds the riser with 2 × M2 into heat-set inserts. The cradle has windows for the flex fold and the pogo pins.
- **Cost per board set** (5 risers) [Estimate]: DF40 parts ≈ $13, riser PCBs + assembly ≈ $5–8, 5 FPC jumpers ≈ $10–20, 16 pogo pins ≈ $3–5, 5 cradles ≈ $5–10, screws/inserts ≈ $1. **≈ $37–57 per set**, plus one-time JLC setup/stencil/FPC fixture fees ≈ $60–120. The 10.5/11.5 connectors are cheaper than the 15.0 parts they replace (−$0.3 each).

**Signal integrity** [Estimate]. Added per lane: riser trace 10–20 mm (≈ 0.3 dB @ 5 GHz), 2 × DF40 mated pairs (≈ 0.2–0.3 dB each), 20–25 mm FPC (≈ 0.6–0.9 dB). That is ≈ 1.3–1.8 dB at 5 GHz (USB 10G Nyquist) and ≈ 1.1–1.5 dB at 4.05 GHz (HBR3). The main-board segment after the TUSB1046A / TUSB1002A / TDP158 (all on B, next to their columns) stays 15–35 mm (≈ 0.4–0.9 dB). The total post-redriver channel of ≈ 2–2.7 dB is within the ≈ 4–5 dB board-to-receptacle allowance usually budgeted after a linear redriver. **No extra redrivers are needed.** Conditions:
- G-S-S-G DF40 pinning.
- Impedance-controlled or TDR-checked FPC.
- EQ re-tuned on the first articles (eye/compliance test with a USB 3.2 Gen2 and an HBR3 sink).
- The DF40 rating (Hirose: 16 Gb/s-class differential) covers both protocols.

**Stock reference (side photo 10:21).** The stock USB-A ports are tall single receptacles soldered straight to the main board, with no riser. In the photo the shells look essentially upright on the board. Any outward lean is small and not obvious from the side, which differs from the 6.4–7.3° front-scan estimate. Treat the stock tilt as unconfirmed (M-IOT2). The risers reproduce the stock reach (≈ 18.5 above the board) with stocked 10.5–11.5 parts.

### 4.7.6 RJ45 (D-IO15)
J25 / J26 are Lingqiang ZJLQ-RJ45-SMD-PCB125-8P8C (vertical SMD, no magnetics, no LED, C55547809). The face stays ≤ 13.0 behind the frame. That height is **not stated** on the LCSC page and must be confirmed from the drawing, otherwise use any ≤ 13.0 vertical non-magnetic jack on the same placeholder footprint. The magnetics are T1 / T2, JASN V24P05S 2.5GBASE-T (SMD-24P 15.1 × 7.1, 1CT:1CT, 180 µH, 1.5 kVrms, IEEE 802.3bz), on the B side 7.6 mm off the jack posts. The Bob-Smith network is 4 × 75 Ω + 1 nF 2 kV. The jack LEDs are gone: the flex ETH light pad is lit by the flex itself. Added cost ≈ +$1 per port.

### 4.7.7 CONN_C fan + AirPort (rev 2026-10-02 ≈ 10:50 ET)
- **Stock connector** (photo a802…, 10:22). Dual-row press-fit B2B, **2 × 20 = 40 contacts**. The pitch measures 0.49 mm (31.7 px against 65 px/mm from the 18.86 standoff spacing), so 0.5 mm. Body ≈ 12.6 long. It is centred between the two threaded standoffs, giving a centre of **(50.49, 5.18)** on the B side (the earlier estimate was 49.7, 5.0).
- **Footprint candidate.** Hirose **DF12-40DS-0.5V(86)** receptacle (A 12.1 / B 9.5 / 40 pos; LCSC C431048, but LCSC showed "not available now" at the time of the search; Digi-Key/Mouser stock DF12(3.0)-40DS-0.5V(86)). Apple usually uses Panasonic / JAE / Hirose 0.5 mm B2B in this class. **Mating with the stock plug is not verified** (M-IOC3): read the markings on the cable plug and measure the mated height, the pin-1 side and the boss/peg positions.
- **Wireless card (Aidan, 11:21 ET).** The card plugs into the AirPort adapter board in the fan assembly, **not into the IOB**, so it does not change CONN_C mechanically. It uses the Apple 12+6 gold-finger edge, the same as the iMac 2017 card (BCM94360CD / BCM943602CDP / BCM94360NG class). Aidan's Sonoma-compatible iMac card fits the same socket. It is longer, with a 4 × U.FL row and 2 screw holes in the top section; that section can be trimmed (no traces there).
  - Photo check (`39d538…jpg`): edge marked **P1** at the 12-finger end and **P18** at the 6-finger end, 12 + key + 6 fingers on the visible face. This matches the public BCM94360 pinout [pinoutguide.com, after the tonymacx86 thread]: 1 3V3 WiFi, 2 LED_WLAN#, 3 GND, 4/5 PETp0/n0, 6 GND, 7/8 REFCLK±, 9 GND, 10/11 PERp0/n0, 12 GND | key | 13 WAKE#, 14 PERST#, 15 CLKREQ#, 16/17 USB D−/D+, 18 3V3 Bluetooth. The card has **no** W_DISABLE#, BT_DISABLE# or SMBus pins.
  - The Mac Pro has **4 antenna leads** (3 Wi-Fi + 1 BT) to the card's 4 U.FL. The iMac card's U.FL row sits higher (in the trimmable top section), so check that the stock leads reach it and are routed without strain (**M-IOA2**). Lead order on the stock card: note it before unplugging.
  - Access: the black plastic top cap is held by **3 adhesive strips** (not clips) and must come off to reach the card; budget new strips (3M 467MP/VHB-class, cut to the stock shapes).
- **Signals (CONN_C is the adapter-board ribbon; its pin order is still UNCONFIRMED, but the signal set now follows the card)**:
  - AirPort PCIe x1: TX ± (host → card PERp/n), RX ± (card PETp/n → host), REFCLK ±, PERST#, CLKREQ#, WAKE#.
  - Bluetooth USB 2.0: D+ / D−.
  - 3V3_WL (load-switched, 4 pins) for card P1, and 3V3_BT (card P18). **ICD rev 2 (Aidan 2026-10-02): 3V3_BT is on the S0 rail** — R149 (0R from 3V3) fitted, R148 (0R from 3V3_SB) DNP — because BT had no wake path anyway (the USB2 hubs are S0-only and S3 is unsupported); this saves S5 standby power. Fitting R148 instead of R149 restores the old behaviour.
  - LED_WLAN# (card P2, DNP pull-up, unused). Former W_DISABLE# / BT_DISABLE# / SMBus pins are now NC29 / NC31 / NC33 (the adapter board may still carry parts: M-IOC1).
  - Fan: 12 V (3 pins, 1.5 A PTC), PWM, TACH.
  - ≈ 14 GND.
  - Working pin map: `CONNC` in `tools/build_sch.py`.
- **Fan control.** EMC2101 (U90, SMBus 0x4C; 0x4C is free on the IOB bus). **Since the ICD (2026-10-02) U90 sits on I2C_PD behind the TCA9517 U83**, because its VDD is 3V3 (S0 only); on the 3V3_SB I2C_SYS segment an unpowered EMC2101 could clamp the bus in S5. The logical address map is unchanged; the fan is off in S5 anyway. The BP MCU must write the EMC2101 fan LUT / TCRIT fail-safe at every S0 entry (**approved, ICD rev 2**: LUT, TCRIT, PWM frequency and fan-fail settings reloaded on every 3V3 power-good, then verified by read-back) (the stock "PWM floats → full speed" fail-safe no longer applies, because the 4k7 pull-up is on 3V3 and the EMC2101 drives PWM). PWM is open-drain with a 4k7 pull-up, TACH has a 10k pull-up. Fan power is +12V_IOB → F90. The BP J5 fan harness (spec §4.6) is no longer needed.
- **Interconnect budget.** HS1 (MCIO 124) has no spare pins, and IOB-LINK (GH15) cannot carry PCIe. Cheapest fix: **ASM1182e** PCIe Gen2 1:2 switch (U91, ≈ $4–5 + a 25 MHz crystal) on the existing HS1 k14 lane (PCH RP4), with downstream 0 = i226-V #2 and downstream 1 = AirPort.
  - No cable or CB change.
  - Shared Gen2 x1 (≈ 4 Gb/s) for 2.5 GbE + 3 × 3 ac (≈ 0.6–1.3 Gb/s). It only saturates when both run flat-out in the same direction.
  - Rejected: a second HS cable (+$10–20, CB connector, PCH lane), or USB Wi-Fi (not native).
  - Bluetooth: a 4th CH334R (U35, H3) on H2 port 4 carries A4 + BT + 2 spare ports (+$0.6).
- **macOS.** Plan for the iMac 2017-style card (Aidan has a Sonoma-compatible one that fits the stock socket), so native Wi-Fi + BT with Handoff / AirDrop and no root patches. *(11:21 ET: the earlier OCLP / Wi-Fi caveat for the stock BCM94360CD on macOS 14+ is dropped.)*
- **Probing (M-IOC1, stock board powered, DMM + scope).** Probe on the stock IOB connector pads:
  1. GND continuity map, unpowered.
  2. Resistance-to-GND signature of every pin, unpowered.
  3. 12 V pins with the fan running.
  4. 3.3 V pins in S0 and S5.
  5. PWM: ≈ 25 kHz, duty follows the fan speed.
  6. TACH pulses: 2 per revolution.
  7. PCIe pairs: diode-mode symmetry, the AC caps beside the connector, REFCLK 100 MHz.
  8. USB D+/D− (15 k pull-downs on the host side, 1.5 k / J-K at enumeration).
  9. PERST# toggling at boot; CLKREQ# / WAKE# pull-ups.
  10. W_DISABLE / BT_DISABLE levels.
  11. Any SMBus pair (pull-ups to 3.3 V).

- **Fan-assembly antenna cable (11:30 ET).** iFixit 21222 step 4 / 8: the fan assembly has **two** cables on the IOB side: the ribbon (CONN_C) and an **antenna cable** that plugs into the IO board. The card itself carries the 4 antennas (above), so this cable most likely brings one card antenna (or the fan-assembly antenna) out to an element that radiates through the **plastic I/O cover**, the only RF window in the aluminium case [Inference]. Without it the card still works, but one chain (or BT) is weaker.
  - **J8**: Hirose U.FL-R-SMT-1(10) (LCSC **C88373**; reel (80) C88374) on B at **(38.4, 16.0)**, the silver ≈ 2.9 × 1.5 SMD part seen in the stock fan-side photo (crop `bracket/io_stock_photos/scan/fan_right.png`). Type and position are **UNCONFIRMED** (the iFixit text gives no type; the guide photos could not be read): **M-IOA1**. Own footprint `MP62_UFL_Hirose_U.FL-R-SMT-1` (KiCad U.FL land pattern without the In5/In6 keep-out zone).
  - **J9** (DNP): second U.FL on F at (24.0, 14.0) joined to J8 by a 50 Ω CPW (net RF_ANT_FAN), for a pass-through to an FPC antenna behind the plastic cover if the stock IOB turns out to have its own element. If M-IOA1 shows the stock IOB has a PCB antenna, copy it instead.
  - Moved to make room: U70 CM108B (38.0, 22.0) → **(38.0, 24.5)**.
- **T8 fan-cable bracket (11:30 ET).** iFixit steps 5–6: a bracket held by **2 captive T8 screws** presses the ribbon plug onto CONN_C. The screws go into the two stock standoffs flanking CONN_C, which H14 / H15 already reproduce at (41.06, 5.17) / (59.92, 5.20) (OD ≈ 4.1 from the photo, M2-class thread; the screws stay in the bracket, so only the threaded standoff is on the IOB).
  - Keep-out on B: **X 38.06–62.92, Y 0–10.5** (standoffs ± 3 mm, drawn on B.Fab + Dwgs.User). Only J7, H14, H15 inside; `build_pcb.py` prints the check ("violations: none").
  - Moved out of it: U90 EMC2101 (44.0, 11.0) (courtyard reached Y ≈ 9.2) → **(65.0, 5.0), rot 90**.
  - Still to measure (**M-IOB2**): bracket outline and thickness, standoff height and thread, whether the bracket needs a ground pad.

### 4.7.8 Stock I/O cover phone scan (2026-10-02 ≈ 11:30 ET)
- **Data.** `Untitled scan.ply` is a **Gaussian-splat** PLY (3DGS: 156,788 splats, SH degree 3, no mesh), inner/back face only. Script `mechanical/io_cover_scan/scan_overlay.py` → `io_cover_scan_check.json`, `io_cover_scan_overlay.png`.
- **Scale and layout.** Mirrored similarity fit of 13 opening centroids to the plate openings: scale **0.931** (raw scan 7.4 % oversize, normal phone scale drift), rotation 2.85°, **RMS 0.49 mm**. The AC opening, not used in the fit, lands within 0.86 mm. Affine fit: 0.934 / 0.917 (≈ 1.8 % anisotropy), RMS 0.46.
- **Outline.** Width ≈ 52.4 at 50 % density (51.5–53.0; splat blur adds ≈ 0.5) vs 51.9; centre 53.0–53.5 vs 53.19; length ≈ 160.3 (ends fuzzy, top touches the table) vs 163.1; corners consistent with r 11.5. **No outline change**; the flatbed-based outline stays.
- **Curvature.** Inner face, |u| < 22: R ≈ **101.7** (bootstrap 99.7–103.7), but Y bands give 94–123 and the half-width choice 77–102 (height noise MAD 1.36 mm, median splat 0.76 mm). It rules out the old 82 and agrees with the D0-derived **R_inner 110.0** (at |u| = 20 the two differ by ≈ 0.2 mm, below the scan noise). **Kept R from D0**; `R_INNER_OVERRIDE` in `build_plate.py` (default None) switches to 101.7 if a measurement says so. Tilt unchanged.
- **Not resolvable.** Clips, ribs, bosses, pins, glue-pocket area and wall thickness (one-sided, noisy scan). Only a right-edge rim band (X ≈ 78, Y 64–116) and one weak blob (29.1, 19.9) stand out > 1 mm.
- **Better measurements:** a radius gauge or card profile across the cover at the USB-C rows (M-IOT2); wall thickness by caliper at an opening edge (M-IOS1); clip positions by caliper from the cover edge (M-IOK1).

### 4.7.9 Swappable flex port modules (D-IO16, rev 2026-10-02 ≈ 12:45 ET; supersedes the risers in §4.7.5)

**Brief (Aidan, 12:13 / 12:17 ET).**
- Every USB-C, USB-A and HDMI port becomes its own swappable module, held by the printed parts with screws. RJ45 stays on the main board.
- **No rigid PCB:** the receptacle is soldered straight to a flex, as the stock audio jack is. The flex has a local stiffener under the port and a press connector at the main-board end.
- Plug forces go into the printed cradle or plate through the shell and stiffener, never through the flex or the solder joints.

KiCad: `/workspace/kicad/macpro62-io-modules/` (README, `mod_usbc`, `mod_usba`, `mod_hdmi`, `modules.json`). Geometry and checks: `kicad/macpro62-io-board/tools/modules_geom.py`.

**Axis and plug seating.** The default build has each axis normal to the plate at its opening (`TILT_OVERRIDE_DEG = None`; C −5.27 / +5.47°, A −5.25 / +5.51°, HDMI −5.33°). The stock 12.5° is kept as a variant: `build_plate.py --tilt 12.5 --tag _tilt12p5`.

| | Normal (default) | Stock 12.5° (7.0–7.25° off-normal) |
|---|---|---|
| Plug overmold stand-off, with outer-face seats | **0.0** (C / A / HDMI) | C 0.68–0.72, A 1.14–1.21, HDMI 1.43 |
| Stand-off, without seats | 0.03–0.04 | C 1.27–1.31, A 1.73–1.80, HDMI 2.02 |
| Mouth centre above the board | 18.40–18.59 | 17.46–18.03 |
| Mouth recess (centre / edges) | 0.14 C, 0.25 A, 0.31 HDMI / 0.05 | 0.69–1.25 |
| Shell in the flex cut-out (min, X / Y) | C 0.42 / 1.42, A 0.70 / 0.35, HDMI 0.38 / 0.17 | C 0.39 / 1.42, A 0.65 / 0.35, HDMI 0.19 / 0.17 |
| Frame-slot margin (min) | C 1.0, A 1.27, HDMI 0.38 | C 0.69, A 0.94, HDMI 0.19 |

At 12.5° a plug cannot seat fully: it stops 0.7–1.4 mm short even with seats, and 1.3–2.0 mm without. Contact engagement is the problem there, USB-C most of all. Normal axes seat fully.

**Module construction.**
- **Flex:** JLC 2-layer PI FPC, 0.11 mm. L1 carries the signals (microstrip), L2 is solid GND, and the VBUS strip is on L2 at the tail edge.
- **Port stiffener:** FR4 1.0 under the port on the B side, flush with the module outline. Stack under the seat: 1.16 mm (FPC 0.11 + PSA 0.05 + FR4 1.0).
- **Tail:** 6.5 mm wide, leaving the module's outboard edge. The flap is 1.5 mm on C and 0.5 mm on A / HDMI. It then makes a 180° C-fold (R 3.2 C, 2.3 A, 2.7 HDMI) and returns under the module.
- **Paddle:** 8.4 mm wide, with an FR4 1.0 stiffener. It carries the DF40C-50DP header (on the port's face, so it faces down after the fold), a 24C02 ID EEPROM (WLCSP-4, 0x50) and 100 nF.
- **Length:** electrical flex length port → header about 26–28.5 mm.
- **Single design per type:** one design per port type. The O-column copies are the same part rotated 180°.

| Module | Receptacle (LCSC) | Mounting on the flex | Unit price | Stock (12:45 ET) |
|---|---|---|---|---|
| MOD-C × 6 | HOAUC HYCW417-USBC24-180B (C5342202), vertical, **all SMD**, L 10.0 | SMT only | $1.13 (1), $0.84 (30) | **196** |
| MOD-A × 4 | kinghelm KH-3.0AF180ZJ-11.5JB (C2979037) | THT signal pins + shell legs, through FPC + drilled FR4, selective solder | $0.16 | **2 (4 needed)** → alt. Hong Cheng HC-USB3.0-L137-WJ (C7501870, 645, H 13.7: needs re-geometry) |
| MOD-H × 1 | HOAUC HYC79-HDMIA19-105 (C711353) | SMD signals + THT shell legs, selective solder | $0.49 | 2,365 |

No stocked all-SMD vertical USB-A 3.0 or HDMI receptacle was found. JLC FPC assembly supports THT on flex (wave or selective solder, fixture $23.57). Stiffener rules: FR4 0.1–1.6, PI 0.1–0.25 or SUS 0.1–0.3 on either side; ≥ 1.0 beyond the pads; minimum width FR4 3 / PI 2 / SUS 1. JLC builds no rigid-flex and does not measure FPC impedance.

**Board-to-flex connector.** Hirose DF40C-50DP-0.4V(51) on the module (C424645, ≈ $0.55) and DF40C-50DS-0.4V(51) on the main board (C424646, 3,359 in stock, $0.84 / $0.40 at 1k). Ratings: 0.3 A per pin, 16 Gb/s-class differential, ≈ 30 mating cycles, 1.5 mated height.

Rejected:
- DF40 60-pin: too long under the module.
- Panasonic A4S/P4S: 1 A power pins and 10 G, but not stocked at LCSC.
- BM28: 5 A power, stock unknown.
- CABLINE / FFC ZIF: 10 G on ZIF is marginal, and the cable is a second part.

**Force path.**
- **Push** (USB-C ≤ 20 N, USB-A ≤ 35 N, HDMI ≤ 44 N): receptacle body in compression on the FPC → stiffener → ledges of a printed MJF PA12 cradle (one per group). The ledges are 0.85 wide (C/A) or 1.15 (HDMI) along both long sides, about 1 MPa, with 0.8 walls and the pocket clearing the paddle by 0.33–0.45 per side.
- **Pull and side:** shell → SUS304 0.2 shield sleeve (bonded: solder for tin-plated shells, epoxy for stainless, **M-IOP1**) → 1.0 collar → screwed clamp plate (MJF PA12 1.6, top 0.3 below the frame back) → 2 × M2 per group → blind M2 SMT standoffs on the main board (H21–H25).
- **Sleeve and frame back:** sleeve length from seat to collar is C 5.0, A 6.65, HDMI 5.7. Frame back is 15.5–15.6 above the board.
- **Fixings:** cradle pegs H40–H45 (NPTH Ø1.6). Clamp posts C (53.19, 70.8) + (53.19, 49.3, shared with A), A (53.19, 25.5), HDMI (43.8, 114.6) + (56.0, 111.0).
- **What the flex and joints see:** the flex, the receptacle solder joints and the DF40 carry no plug load. Plate deflection estimate: 0.24 mm at 20 N mid-span between the C posts.

**Shielding.**
- **Sleeve:** each sleeve is grounded to a GND ring on the module (coverlay opening, `MP62_MOD_Sleeve_GND_Ring_*`) and has a spring finger to the metal I/O frame.
- **Silver film (optional):** EMI silver film over L1 (User.2) needs ≥ 2 openings Ø ≥ 1.0 to GND about every 30 mm, ≥ 0.8 from pads, and none under the stiffeners. It changes the trace widths.

**PMI-50 standard module interface** (DF40 50-pin, row A odd / row B even):
- **k 1–6:** VBUS × 12.
- **k 7–8:** GND.
- **k 9–10:** HS0 (A) / HS2 (B).
- **k 11:** GND.
- **k 12–13:** HS1 / HS3.
- **k 14:** GND.
- **k 15–16:** USB2 D± / SBU1–2.
- **k 17:** GND.
- **k 18:** CC1 / HPD.
- **k 19:** CC2 / UTIL.
- **k 20:** GND.
- **k 21:** ID_SCL / ID_SDA.
- **k 22:** 3V3_MOD / PRSNT#.
- **k 23:** LED# / GND.
- **k 24–25:** GND.

Totals: 12 VBUS (3.6 A; USB-C 3 A = 83 % per pin), 17 GND, 21 signals.

Role mapping:
- **C:** HS0 TX1, HS1 RX1, HS2 TX2, HS3 RX2.
- **A:** HS0 SSTX, HS1 SSRX.
- **HDMI:** HS0 D2, HS1 D1, HS2 D0, HS3 CLK; SBU = DDC; HPD; UTIL = CEC (not connected); VBUS = +5V.

Main board:
- **JM1–JM11:** DF40C-50DS on F (C1–C6, A1–A4, HDMI).
- **U95 / U96 (TCA9548A, 0x70 / 0x71):** give each slot's ID EEPROM its own channel.
- **U97 (TCA9555, 0x27):** reads PRSNT# on U96 channel 3, a private segment, so 0x20–0x27 stays off I2C_PD (TPS65994AD I2C1 range). Its INT# goes to PD_INT_N.
- **LED#:** not connected in A0.

**SI budget per lane at 5 GHz (USB 10 G Nyquist; HBR3 4.05 GHz is easier), after the existing redrivers (TUSB1046A / TUSB1002A / TDP158) [Estimate]:**

| Segment | Loss |
|---|---|
| Main board, redriver → JM | 0.4–0.9 dB |
| DF40 mated pair | 0.2–0.3 dB |
| Flex about 28 mm (≈ 0.35 dB/in, 2-layer PI, 90/100 Ω) | 0.4–0.6 dB |
| Receptacle + pads | ≈ 0.3 dB |
| **Total** | **≈ 1.4–2.1 dB** |

This is better than the riser design (one connector instead of two DF40s plus a jumper) and well inside the post-redriver budget. **No extra redrivers.** Order a JLC impedance coupon and TDR it, because JLC does not measure FPC impedance.

**Swap (system off).** Remove 2 clamp screws → lift the plate → lift the module → unplug the DF40.

**Cost per module [Estimate].**
- **MOD-C:** about $3.9–5.9: receptacle 1.13, DF40 pair 1.4, EEPROM + cap 0.2, sleeve 1–3, FPC share.
- **MOD-A / MOD-H:** about $2.9–5.3.
- **Per order:** JLC FPC about $15–30 per design for 5–10 pcs, the SMT setup and the THT fixture $23.57.
- **Main board:** 11 DF40C-50DS (≈ $9), 2 × TCA9548A + TCA9555 (≈ $2), 6 SMT standoffs.

**Risks.**
1. DF40 ≈ 30 mating cycles. Log the swaps.
2. VBUS at 83 % of the per-pin rating.
3. FPC impedance not measured by JLC.
4. THT legs on flex (A, HDMI) need selective solder. The leg tips sit inside the ledge window.
5. The sleeve bond is in the pull path.
6. **LCSC stock:** C5342202 has 196; C2979037 has 2, and the alternative is 2.2 mm taller.
7. The WLCSP EEPROM has no LCSC number yet.
8. No port ESD (pre-existing). Add TPD4E05U06-class parts near the JMn.
9. Clamp-plate stiffness with 2 posts per group.
10. Pin 1 through the fold must be checked in 3D.
11. FR4 stiffener chipping. Use SUS 0.2 if it chips.
12. Speaker fold clearance: C 1.66, A 2.72.
13. All land patterns are placeholders. The module flexes are not routed yet.

**Measurements.**
- **M-IOP1:** HYCW417 drawing (height, tabs) and shell plating.
- **M-IOF2:** frame back height.
- Foam thickness, speaker body height and H13 standoff.
- Earlier: M-IOA1, M-IOC1, M-IOS1/2.

**Cross-board overlap.**
- None at the MCIO / IOB-HS1 / DISPLAY-LINK interfaces. Port nets are unchanged and only their connectors change.
- The new parts are internal to the IOB, on I2C_PD (U95 0x70, U96 0x71, U97 0x27 private) and PD_INT_N. The ICD I²C table (`/workspace/macpro62-interface-control.md`, I2C_PD row) should list 0x70 / 0x71, and 0x70 / 0x71 must be added to the TPS65994AD address-avoid list (U-10).

### 4.7.10 Changelog 2026-10-02 ≈ 14:55 ET: module follow-ups (D-IO16) and plate corrections (Aidan 13:37 ET)

**A. Plate corrections (Aidan, priority)**

1. **HDMI ↔ power button back to stock.** In the back view, HDMI is now at **+X (63.86, 107.07)** and the button at **−X (43.02, 108.11)**.
   - Root cause: the 821-2222-A flex trace was digitised from its board-facing side, so it was mirrored. It is now mirrored back about X_M 53.408 (`mechanical/io_plate_v2/mirror_flex_trace.py`; ports move ≤ 0.064).
   - The frame features and the stock-cover openings had been registered to that same grid. They are mirrored too. As a result the **audio holes move** to (42.17, 19.42) / (63.41, 19.10), and the new scan confirms (42.18, 19.38) / (63.41, 19.31).
   - AC = (53.30, 130.15), taken from the scan.
   - **What else had to swap:**
     - (a) **Flex trace:** yes. It was the cause.
     - (b) **Main-board placement:** yes.
       - JM11 HDMI is now **O side, (66.65, 107.07), rot 0**, folding toward +X.
       - SW1 → (43.02, 108.11); D20 → (43.02, 103.38); J30 → (50.32, 104.5).
       - U60 TDP158 → (66.65, 111.57) B and U61 → (61.65, 111.57) B, both next to JM11.
       - U80 → (28.5, 108.5) B, which frees the B side under JM11 for its ESD (D226–D228).
       - Hall sensors U30/U31 → (34.8, 112 / 104).
       - HDMI cradle pegs → (70.82, 111.9) / (55.62, 106.0).
       - J31 flex ZIF → (24.0, 10.0), following the mirrored neck (−X edge). J9 U.FL → (24.0, 16.0).
       - RJ45: ETH1 J25 (63.664, 91.407) and ETH2 J26 (43.145, 91.595). Labels are kept by position (i226 #1 at +X, #2 at −X), and T1/T2 follow.
       - `io_geom.json` openings_outer is mirrored; the originals are kept in `openings_outer_asscanned`.
     - (c) **HDMI module:** no redesign. The same MOD-H is now fitted rotated 180° (like C4–C6). Pin 1 through the fold is verified (item B6). Only the cosmetic orientation of the receptacle trapezoid flips; the plate opening is a rounded rectangle.
   - Main-board DRC 0 / 0 unconnected; ERC 0 / 0.
2. **Glued, no clips.**
   - Removed: clips, the 3.0 × 1.2 rim, the Ø2.4 frame/ear pins, the LED/button-carrier pockets, the frame-screw relief and the 0.2 flex pocket.
   - The flex is PSA-bonded flat. Assembly is aligned with dummy plugs.
   - **Glue land:** a perimeter band 0.4–3.4 mm in from the edge, kept 0.6 clear of the flex, neck and openings. It is one continuous land of 992 mm², 1.9–3.0 mm wide on the sides and 4.5 at the ends, interrupted at Y 28–48 on −X by the neck. It is flat inner face with no added material (DXF layer `GLUE_LANDS`).
3. **1.4 everywhere, edges included.** `SKIN = 1.4`, no rim.
   - The STL ray-cast gives 1.372–1.423 (STL faceting); the exact B-rep probe gives 1.400 normal at the crown, the long edges and the ends.
   - The only exception is the port plug seats: 1.09–1.40 in the default variant, 0.61–1.75 in `_tilt12p5`.
   - All geometry moved 0.2 toward the board because the flex pocket is gone. Module seats: C 8.83 / 8.79, A 5.04 / 5.00, HDMI 8.10. `modules_geom.py`: 101 / 101 checks OK.
4. **Scan check** (`io_plate_v2_A0_scan_overlay.png`):
   - Opening order matches: AC → HDMI slot + button → ETH → 3 C rows → 2 A rows → audio → audio light windows.
   - Outline 163.0 × 52.0 vs design 163.1 × 51.9.
   - The scan shows glue residue along the long edges, which matches perimeter glue lands. It also shows grey rims around the port groups, which look like light-guide gaskets; the inside scan will settle this.

**B. Module follow-ups**

1. **USB-A part:** HC-USB3.0-L137-WJ (C7501870, 13.7 mm, 645 in stock, ≈ $0.12). Kinghelm C2979037 is the alternate (2 in stock, 2.2 mm taller).
   - Loop fold R 1.664 / 1.65 at 0.11 FPC, vs the JLC rule 12t = 1.32 and the 15t loop target = 1.65: OK.
   - Seats 5.04 / 5.00. Plug overmold stand-off 0 with the seats. Flex/plate cut-out margin 0.34.
2. **ESD:** on the **main board, B side, directly under each JMn**.
   - Each lane's F→B via ends on the ESD pad, so there is no stub, the GND return is short, and the 0.4 pF/0.5 pF load sits at the connector-side discontinuity rather than on a 12 µm flex.
   - USB-C module: 2 × TPD4E02B04DQAR (C106794) for SS plus 1 × TPD4E05U06DQAR (C138714) for USB2/CC/SBU.
   - USB-A: 1 + 1.
   - HDMI: 3 × TPD4E05U06.
   - Totals: 16 × 02B04 + 13 × 05U06 (D200–D228).
3. **ID EEPROM:** BL24C02F-NTRC (C2828222, DFN-8 2 × 3, 9,945 in stock, $0.09). Alternates: AT24C02D-MAHM-T C461609 and BL24C02F-RRRC C498263. No stocked WLCSP 24C02 exists.
4. **Routing** (JLC FPC, 12 µm Cu; `tools/zsolve.py`):
   - 50 µm core: 90 Ω = 0.09 / 0.10 solid or 0.12 / 0.10 over the bend hatch 0.10 / 0.25; 100 Ω = 0.08 / 0.15 solid or 0.11 / 0.15 hatched.
   - MOD-A 25 µm core: 0.10 / 0.10 over a 0.10 / 0.30 cross-hatch (≈ 92 Ω, estimate).
   - Bends: hatched GND, no vias, teardrops on every pad/via.
   - **MOD-A:** complete, DRC 0 errors.
   - **MOD-H:** complete, DRC 0 errors. Intra-pair skew ≤ 0.65.
   - **MOD-C:** **open.** The port fan-out of the inner A-row group (CC1, D± A-side, SBU1, SSRX2±) is incomplete: 8 unconnected and 1 clearance (CC2 to shell tab, 0.073). The placeholder HYCW417 shell tabs sit on the tail axis and block the centre channel. Fix with the real land pattern plus a hand fan-out on L2 under the stiffened port.
   - A second via size of 0.40 / 0.20 is allowed (JLC 2-layer FPC charges extra only below a 0.15 hole).
   - USB-A intra-pair skew ≈ 2.6 comes from the 2.0 mm THT pitch. Compensate at the JMn on the main board.
5. **TDR coupons:** `macpro62-io-modules/tdr/tdr_coupon_c50` (90 / 100 Ω solid and hatched, plus a 50 Ω SE reference) and `tdr_coupon_a25` (90 Ω cross-hatch ×2, plus SE). Each line is 50 mm with a GSSG/GSG 1.00 launch. DRC 0. Panel them with the modules.
6. **Pin 1 through the fold** (`tools/check_pin1_3d.py` → `pin1_check_3d.png`): C1, C4, A1, A3 and HDMI (O side) all OK, with the same 1→25 vector and row order header vs JMn. The placeholder pad-row pitches differ (2.6 header vs 3.2 receptacle) and must be checked against the Hirose land patterns.

**Risks added:**
- Other scan-derived main-board X positions may also be mirrored: speaker, PSU connectors, AC window (board cx 50.43), foam rails, CONN_C standoffs. Check them with the inside-face scan / stock board.
- AUD_H jack-nose margin 0.04 (assumed Ø6.0).
- The HDMI flex Y margin 0.165 and plate-opening margin 0.07 are unchanged.
- The frame-screw head must be ≤ ~1.1 above the frame face (M-IOF2).
- Glue choice: VHB/PSA die-cut vs bead; bond strength vs plug pull is carried by the clamp plate.
- §4.7.9 risks 7, 8, 10 and 13 are resolved or updated by this section.

### 4.7.11 Changelog 2026-10-02 ≈ 16:10 / 16:25 ET: plate screwed to the frame — 2× M1.6 centre screws (primary) + 4× M1.6 corner screws (secondary); glue = optional fallback

**Update ≈ 16:25 ET: centre screws are now the PRIMARY plate→frame fixing (Aidan, 16:14 ET: "the couple of holes near the centre definitely have screws"). The 4 corner M1.6 screws below are now secondary.**

*Re-check of the centre features.* Scan 83f0b85e, `io_plate_v2_A0_screw_candidates.png`. The centre features are soft in the scan (out of the focus plane), so all of these are visual reads, ±0.5.

| # | Scan | Flex 821-2222 hole (mirrored trace) | Frame trace (mirrored) | Confidence |
|---|---|---|---|---|
| K9 | soft ring Ø≈2.4, core ≈1.0, at (53.2, 76.1) | HOLE_C1 Ø3.30 at (53.64, 75.53) | HOLE_C1 Ø3.17 at (53.89, 75.41) | **high** that a screw is here (Aidan + 3 sources); position ±0.3 |
| K10 | dark disc Ø≈4.5–5 with bright arcs, at (53.0, 58.6) | HOLE_C2 Ø5.08 at (53.46, 58.16) | HOLE_C2 Ø4.84 at (53.44, 58.38) | **high**; ±0.3 |
| K11 | faint arc + bright blob at (52.6, 19.3) | PIN_C3 Ø5.67 at (53.44, 19.27) | PIN_C3 Ø3 at (52.33, 19.23), "dark ring, bright centre" | **low**: may be a light pipe or pin; built only with `--c3` |
| — | small ring at (47.7, 112.2) | BTN_EAR_1 Ø1.8 | — | flex button-carrier locating ear, not a screw |

The three flex holes are larger than the frame holes. They are the clearance holes the stock posts pass through.

**How the plate reaches the frame.** The frame is not 16.5–18 mm away; that is the plate-to-board-top gap. Plate inner face → PSA 0.05 + flex 0.12 + foam 1.0 = **1.17** → frame front face.
- At the crown: frame front at 18.0 − 1.17 = 16.83 above the board top, frame back at 15.83.
- The module model has `frame_back_height` 15.50–15.56 at the port columns; this is the same concentric frame.

So the stock plate reaches the frame with a **post on the inner face**:
- It runs 1.17 to the frame front, plus 0.8 into the frame hole, which is shorter than the 1.0 frame so the washer clamps the frame.
- Post length 1.97 below the inner face; **local wall 3.37** (the only local exception besides the seats and corner bosses).
- If M-IOF2 shows a different frame height, set `CENTRE_GAP` = D0(x) − frame-front height.

**Design** (`CENTRE_SCREWS` in `build_plate.py`). Positions are the midpoint of the flex-hole and frame-hole centres.

| Screw | Position | Post | Radial margins | csk (default) | pt (`_screwpt`) |
|---|---|---|---|---|---|
| **SCR_C1** | (53.76, 75.47) | Ø2.6 | 0.21 in the flex hole, 0.71 in the foam hole, 0.15 in the frame hole | M1.6 × 6 ISO 7046 countersunk T5 from outside: Ø3.25 csk + Ø1.8 clearance, M1.6 nut + Ø4 washer on the frame back | M1.6 × 4 thread-forming pan T5 + Ø4 washer from the frame side into a blind Ø1.30 pilot, 0.45 skin left |
| **SCR_C2** | (53.45, 58.27) | Ø4.2 | 0.33 flex, 0.83 foam, 0.21 frame | same; washer **Ø6** because the frame hole is Ø4.84 | same; washer Ø6 |

In csk mode the heads are visible on the outer face between the C columns.

**Clearance (default; pt in brackets where it differs).**

| Check | SCR_C1 | SCR_C2 |
|---|---|---|
| Nearest plate opening | C4 3.54 (3.87) | W_TB window 3.54 (3.07) |
| Flex light pad / LED | LED (53.3, 70.9) 2.69 | PAD_TB 1.26 |
| Receptacle shells, in plan | C4 2.67 | C6 2.03 |
| Flex neck | 34.9 | 23.0 |
| Speaker | 20.3 | 19.0 |
| J31 | 64.6 | 47.7 |
| Coin cell | 57.1 | 71.5 |
| CONN_C / J7 (B side) | 64.9 | 46.7 |
| J8 (B side) | 56.5 | 38.8 |

- Module paddles and JMs lie under the posts in plan, but they are ≤ 2.34 above the board. The fastener ends 13.73 (14.23) above the board, so there is no conflict.
- **Needs action 1, module clamp plate C** (PA12 1.6, top 15.26 above the board, 0.57 below the frame back). Both centre fasteners hang into it:
  - It needs a **Ø5.0 clearance hole at SCR_C1** and a **Ø7.0 hole at SCR_C2**.
  - At SCR_C1, the C clamp-post M2 screw at (53.19, 70.80) leaves only ≈ 0.3 of web. Move the post (H21) to Y ≤ 69.8, or merge the hole into a slot.
- **Needs action 2, main board H13.** The frame-centre standoff (53.38, 58.38) sits directly under SCR_C2.
  - Either drop H13 and use the nut,
  - or make H13 an M1.6 standoff reaching the frame back (15.8) and run SCR_C2 (csk, M1.6 × 6–8) plate → frame → H13, without the nut. That is not possible in pt mode.
  - The board is unchanged pending M-IOC4.
- Existing item noticed: the M2 clamp-post screw heads on the clamp-plate top (15.26) have only 0.57 under the frame centre bar. They need countersinking in the clamp plate or frame clearance.
- The corner screws were re-checked against the same list:
  - SCR_B−: the washer/nut footprint overlaps the J31 ZIF in plan by 0.34, but sits 12.7 above the board. J28 is 1.0 away in plan. Check the flex tail route from the neck to J31 clears the SCR_B− nut by ≥ 2.
  - SCR_T−: 0.61 in plan to the BT1 holder, 4.0 to the cell, 12.7 above the board.
  - Speaker ≥ 19.8; flex neck ≥ 11.6.

**Wall:**
- General 1.372–1.423 (exact 1.400).
- Seats unchanged.
- Bosses and posts 0.37 (csk lip) to 3.37.
- All 4 variants are single solids; z extent −4.71..0.

**Centre-screw measurements (M-IOC*)**
- **M-IOC1:** centre hole positions on the plate from the plate edges and the AC opening (calipers), and on the frame. Diameters: frame C1 Ø3.17 and C2 Ø4.84 (trace), flex Ø3.30 / Ø5.08.
- **M-IOC2:** the stock post. Is there a post on the inner face, and what are its OD and length (inner face → frame front)? Foam thickness, free and compressed.
- **M-IOC3:** the stock screw. Which side it is driven from, head type, Ø and height, drive, thread (M1.4 / M1.6 / M2), length. What it threads into: a nut, a clinch nut, a tapped frame, or the plastic post.
- **M-IOC4:** is the frame also screwed to the board at C2 (decides H13)? Frame thickness at the centre bar, and frame-back height above the board (M-IOF2).
- **M-IOC5:** is there a third screw at K11, between the audio jacks? Are the centre screws visible from outside with the case on?


**Rev 2026-10-02 ≈ 16:10 ET: corner screws replace the glue (Aidan's suggestion, 15:55 ET).**

*Evidence (`screw_candidates.py` → `io_plate_v2_A0_screw_candidates.png`).* Positions are back-view mm, read with the outer-face mapping of scan 83f0b85e.

| # | Scan feature | Position (X, Y) | Size | Confidence | Interpretation / what it fastens to |
|---|---|---|---|---|---|
| K1 | sharp ring, image top-left | (74.77, 150.08) | dark core Ø1.0–1.3, ring Ø2.3–2.8 | high that it is a fixing point; X ±0.5, Y ±0.3 | stock plate→metal I/O frame fixing at frame hole CORNER (Ø3.16–3.50) |
| K2 | sharp ring, image top-right | (29.84, 149.82) | same, ring partly in the corner shadow | high / ±0.5 | same |
| K3 | sharp ring, image bottom-left | (74.60, 15.05) | same | high / ±0.5 | same |
| K4 | ring, image bottom-right, half off the scan edge | (29.54, 13.93) | not measurable | medium / ±0.8 | same (inferred by symmetry) |
| K5 | dark round hole at the +X edge, glue residue | (79.52, 140.89) | Ø≈2.4 | low | clip / latch window, not a screw |
| K6–K8 | C-shaped hook marks | (30.61, 140.70), (76.61, 23.24), (28.96, 21.08) | 3–4 mm arcs | medium | stock clip points (CLIPS_L), not screws |
| K9 | soft ring, centre column | (53.4, 75.4) | Ø≈2.5 | medium | frame HOLE_C1 (Ø3.2) locating hole, not a plate screw |
| K10 | soft dark ring, centre column | (53.4, 58.4) | Ø≈5 | medium | frame centre screw HOLE_C2 (Ø4.85), which goes **frame → board standoff H13**. The plate does not reach it, so it is unchanged. |

**What the four rings are.** K1–K4 form a 44.9–45.2 × 135.3–135.9 rectangle. That matches the frame-trace corner holes (44.2 × 135.3, Ø3.16 / 3.39 / 3.30 / 3.50).
- The core (Ø1.0–1.3) fits either an M1.4/M1.6 screw recess (T4/T5 Torx) or a Ø1.1–1.3 threaded or pilot hole.
- The ring (Ø2.3–2.8) fits an M1.4 head (dk 2.6–2.8) or an M1.6 countersunk head (dk 3.0).
- The scan cannot tell a screw head from a brass insert or a hollow heat stake, so the fastener type has **low** confidence.
- **Design choice: M1.6**, the middle of the M1.4–M2 range. It is a 3.0 head in a Ø3.2–3.5 frame hole.

**Design (`FIX = "screws"`, `SCREWS`, `SCREW_MODE` in `build_plate.py`).** There are 4 screws, symmetric about the plate centre line, at a 45.1 × 135.25 pitch:
- SCR_T− (30.64, 149.95)
- SCR_T+ (75.74, 149.95)
- SCR_B− (30.64, 14.70)
- SCR_B+ (75.74, 14.70)

Why symmetric: a symmetric pattern lands in the same place whichever face the scan shows, so the open inner/outer-face question does not move it. The scan rings are symmetric to within about 0.5 mm. The axes are radial, ±11.7°.
- **Default `csk`:**
  - Screw: M1.6 × 5 ISO 7046 / DIN 965 countersunk T5, driven from the outer face.
  - Plate: 90° countersink Ø3.25, so the head sits 0.12 below the face; Ø1.80 clearance hole.
  - Spigot: Ø2.8 × 0.8 on the inner face, locating in the frame corner hole. It is shorter than the 1.0 frame, so the washer bears on the frame.
  - Frame back: DIN 125 washer Ø4 × 0.3 + M1.6 nut, or the stock clinch nut if the frame has one.
  - Local wall 2.2; the lowest fastener point is z −6.71, which leaves 12.7 to the board top.
- **Variant `--screw pt --tag _screwpt`:**
  - Screw: M1.6 × 3 thread-forming-for-plastics pan/wafer T5, driven from the frame side.
  - Plate: blind Ø1.30 pilot with 0.45 skin left, so the outer face is unbroken; same spigot.
  - Engagement is ≈ 1.75, which is short. Use this variant only for light clamping.
- **Glue band kept as a fallback:** DXF layer `GLUE_LANDS_OPTIONAL`, one land of 963 mm², now also 0.6 clear of the screw spigots.
  - New DXF layers: `SCREWS` (countersink, clearance or pilot) and `SCREW_BOSSES` (spigots).
  - New features-JSON entries: `fixing.screws` (per-screw checks) and `kind = "BOSS"`.

**Clearance (all four screws OK):**

| Check | Clearance |
|---|---|
| Outline edge, outer face | ≥ 1.29 (csk) |
| Outline edge, inner face | ≥ 1.52 |
| Flex outline (bottom pair) | 3.63 / 4.17 |
| Flex outline (top pair) | > 30 |
| Flex neck | ≥ 11.6 |
| Nearest opening (AC, AUD_H, W_AUD_O) | ≥ 8.4 |
| Port modules (A2 / A4 at the bottom) | ≥ 9.1 |
| Fastener stack to board top | 12.7 vertical |

Nearest F-side board parts: BT1 coin holder 2.6 in XY (SCR_T−), J31 flex ZIF 1.7 in XY (SCR_B−), L41 4.2 (SCR_T+). All are well below the nut, which sits 12.7 above the board top.

**Wall:**
- Outside the bosses: 1.372–1.423, which is STL faceting; exact 1.400.
- Seats unchanged: 1.09–1.42 default, 0.61–1.75 tilt.
- Bosses (allowed local exception): 0.37 at the countersink lip up to 2.2 at the spigot.

**Variants rebuilt:** `io_plate_v2_A0`, `_tilt12p5`, `_eth2blank`, `_screwpt` (STEP + STL), with thickness PNGs and iso renders for each.

**Disagreement to resolve.** The 100 dpi frame trace, mirrored as used, puts its corner holes 0.6–2.8 mm from the design screws: X 33.4 / 77.6 at the top, 30.3 / 74.5 at the bottom. It is a 1.3° parallelogram, which is probably scan skew.

**Measurements (before printing):**
- **M-IOS1:** frame corner-hole centres from the frame edges, and the pitch (X and Y), by caliper. Also the hole Ø, and whether the holes are plain, tapped, or carry clinch nuts or inserts.
- **M-IOS2:** gap from the plate inner face to the frame front face at the corners (set `CORNER_GAP`), and the frame thickness (M-IOF2).
- **M-IOS3:** the stock fastener: head type (pan / countersunk / wafer), head Ø and height, drive, thread Ø and pitch (M1.4 × 0.3 / M1.6 × 0.35 / M2 × 0.4), length, and which side it is driven from. Or it may be a heat stake or insert.
- **M-IOS4:** the plate corner features measured on the part. Ring and core Ø, centres from the plate edges, and whether the hole is through or blind. Is it visible on the outer face with the case on?
- **M-IOS5:** which face the scan 83f0b85e shows (open). Weak hint: the corner rings are sharp while the centre features are soft, which on a flatbed would favour the concave inner face being on the glass. The translucent light guides blur anyway.

## 5. Interconnects

### 5.1 IOB-HS1: MCIO 124 from CB J3 (CR-CB-IO1)

The pinout is in `kicad/macpro62-io-board/docs/mp62-iob-hs1_mcio124_pinout_v0.1.csv`. It uses the same physical contacts and GND pattern as MP62-FACE.

**Lane pairs (PET = CB TX):**

| Lanes | Use |
|---|---|
| k0–k5 | USB3 for C1–C6 |
| k6–k9 | USB3 for A1–A4 |
| k10 | i226 #1 PCIe x1 (PCH RP3 / HSIO 12) |
| k11 / k12 | DDI-B ML0/1 and ML2/3 |
| k13 | DDI-C ML0/1 (DDI-C is 2-lane since v0.2) |
| **k14** | **i226 #2 PCIe x1 (PCH RP4 / HSIO 13)**; was DDI-C ML2/3 |
| k15 | DDI-B AUX (PET) and DDI-C AUX (PER) |

**Sideband:**

| Contact | Signal |
|---|---|
| A8 / A9 | HPD_B / HPD_C |
| B8 / B9 / A11 | I226 CLKREQ# / WAKE# (shared, OD wired-OR) / PERST# (shared by both i226) |
| B11 / B12 | I226 REFCLK |
| A12 / A30 | PRSNT, tied to GND on the IOB |
| A26 | VBAT_RTC |
| A27 | USB_OC# |
| B29 / B30 | USB2 uplink to hub H1a |
| B26 / B27 | I226B REFCLK± (PCH CLKOUT_PCIE_SRC11 [Proposal]) |
| A29 | I226B CLKREQ# (SRCCLKREQ11#) |
| – | **No spare sideband contacts left on HS1** |

- The CB plan changes:
  - The i226 (U13) moves to the IOB.
  - USB2 on J3 drops from 4 to 1.
  - CB BT1 becomes DNP. The CB keeps the BAT54C diode-OR with 3V3_DSW, 1 µF + 0.1 µF and the RTCRST# RC.
- **Z790 is required** for 10 × 10 G (HSIO 0–9 are dedicated USB 3.2 Gen2). B760 gives 4 × 10 G + 2 × 5 G.
- macOS: 15-port limit per xHCI, so a USBMap is needed.
- Pinout file is now `docs/mp62-iob-hs1_mcio124_pinout_v0.2.csv` (v0.1 superseded).

#### 5.1.1 PCH lane for the second i226-V (D-IO2, 2026-10-02)

Z790 Flex-I/O map [Sourced: Intel 700-series PCH datasheet vol. 1, 743835, "Desktop PCH HSIO Details"]:

| HSIO | Z790 function | MP62 use |
|---|---|---|
| 0–9 | USB 3.2 Gen 2x1 only | 10 × USB3 → IOB (HS1 k0–k9) |
| 10–11 (RP1–2) | PCIe 3.0 | Spare x1 ×2 (Wi-Fi later) |
| **12 (RP3)** | PCIe 3.0 / GbE | **i226 #1** (HS1 k10), CLKOUT_SRC12, same lane as the i225 LAN on MSI ms7d25 |
| **13 (RP4)** | PCIe 3.0 | **i226 #2** (HS1 k14), CLKOUT_SRC11 [Proposal] |
| 14–17 (RP5–8) | PCIe 4.0 | Reserved x4 for the later AQC107 variant |
| 18–25 (RP9–16) | PCIe 4.0 (22–25 also SATA) | M.2 boot x4 (one group); SATA0 → BP |
| 26–37 | PCIe 3.0/SATA, PCIe 4.0 | Spare |

- **No PCH lane conflict.** USB3 sits on HSIO 0–9, which Z790 never shares with PCIe, so the 10 × 10 G ports stay intact. RP1–4 must run as 4 × x1 (soft strap), as on the ms7d25 reference (RP1/RP2/RP3 used as x1). Root ports in use: 4–5 of 16. i226-V links at Gen2 x1 (5 GT/s), which a Gen3 lane covers. B760 has HSIO 10–13 as PCIe 3.0 too.
- **The conflict is on the cable, not the PCH.** All 16 pair slots of the CB J3 / IOB-HS1 MCIO 124 were used, and the 3 spare sideband contacts were the only free pins. Resolution: **DDI-C drops from 4 to 2 lanes** (k14 → i226 #2), REFCLK2 takes B26/B27, CLKREQ2# A29, PERST#/WAKE# are shared.
  - Cost: C6 (iGPU DDI-C, not usable in macOS anyway) is limited to 2-lane HBR2 (≈ 2560 × 1440 @ 60 or 4K @ 30). In return C6 can run DP and USB3 10 G at the same time.
  - Rejected alternative: an ASM1182e PCIe switch on the IOB sharing the k10 lane (+$4–5, a clock buffer, and Gen2 x1 ≈ 4 Gb/s is oversubscribed by 2 × 2.5 G).
- **CB impact (CR-CB-IO1 rev):** J3 k14 = PCH RP4 PCIe (AC caps on the CB TX side), CLKOUT_SRC11 to J3 B26/B27, SRCCLKREQ11# from A29; DDI-C ML2/ML3 not routed.
- **AQC107 later variant:** J3 has no free pairs, so it needs PCIe x4 (RP5–8) on a second cable (IOB-HS2) and replaces i226 #2 at ETH2.

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
- **IOB end is row-swapped (ICD 2026-10-02).** The straight MCIO 74 cable crosses the rows (face spec §9.3), so J2 uses the module-end table with rows A and B exchanged: `kicad/macpro62-io-board/docs/mp62-iob-j2_mcio74_displaylink_iob-end.csv` (written by `build_sch.py`, with the module-end contact alongside). Before this fix J2 used the module-end contacts directly, which put the GPU TX pairs on the wrong row. Net names are unchanged. See `/workspace/macpro62-interface-control.md` §4.

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
| CONN_C, fine pitch + 2 threaded standoffs | (49.7, 5.0), B | **Fan-assembly ribbon** (interposer: fan 12 V/PWM/FG + AirPort Wi-Fi/BT), held by the bracket with 2 captive T8 screws [Sourced: iFixit steps 5–7] | **J7 at (50.49, 5.18) + H14/H15 standoffs (D-IO9, 10:50 ET); bracket keep-out on B (§4.7.7).** M-IOC1. |
| Fan-assembly antenna cable (iFixit 21222 step 8) | ≈ (38.4, 16.0), B, photo candidate (M-IOA1) | AirPort antenna lead to the I/O-cover RF window [Inference] | **J8 U.FL C88373** + DNP J9 pass-through (§4.7.7) |
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

- **BP side (ICD 2026-10-02):** BP J6 is the same GH 15P (BM15B vertical) at BP (11.4, −48.8), 1:1 cable. The BP pulls pin 11 up (10 k to 3V3_SB) to detect the IOB, pulls IOB_INT_N (pin 10) up, and routes CPU-LINK USB2_SPARE (B79/B80) to pins 13/14. The BP stub schematic carries all 15 pins.

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
  - **Since 2026-10-02 SW1 is the no-flex fallback.** With the 821-2222 (or the A1 flex) on the plate, its dome sits right behind the Ø12.4 opening. The cap then presses the dome, and J31 is the button path (§4.7). The dome needs a backstop (M-IOW3).
- **Port lights:** from the flex on J31 (D-IO10). D21–D26 are DNP; U80 keeps D20, the diag LEDs and the A1 flex channels.
- **J30** (DNP, JST SH 2P at (56.5, 104.5) F): optional remote or stock button in parallel.
- **Behaviour (BP MCU firmware):**
  - PWRBTN_IN_N falling edge → pulse PWRBTN# 400 ms (S5→S0, or the OS sleep request in S0). A 4 s hold forces off.
  - Power/sleep LED D20 on TLC59116 OUT8: on in S0, breathing in sleep.
  - **Port lights:** LIS2DH12 (U81, 0x18) runs at 10 Hz low power with an INT1 wake-up threshold of ≈ 63 mg / 1 sample. INT1 → IOB_INT_N.
  - The MCU reads INT1_SRC and commands the stock wall-flex LED MCUs over I²C on J31 (since 2026-10-02 the primary path), or fades in U80 OUT9–14 for the A1 flex (D21–D26 DNP). It holds them for 5 s after the last motion, then fades out over 1 s.
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
| Ethernet | **2 × i226-V**: U50 + NVM U51 + 25 MHz Y4 + SVR L44 → J25 (ETH1); **U52 + NVM U53 + Y6 + L45 → J26 (ETH2)**. Both jacks HanRun HR913790A (P1 common CT → 100 nF, P10 Bob-Smith → GND, green link + yellow activity LEDs via 330 R) | U52 group on B at Xb 20–30, Y 83–100 (left of the J26 THT field). Hub crystal Y2 moved to (53.0, 95.5). |
| HDMI | TDP158 U60 + 1V1 LDO U61; 0.5 A PTC on +5V; DDC 1.8 k pull-ups | |
| Audio | CM108B U70 + Y5. HP_L/R → J28; line-in L+R mixed into the mono ADC; S/PDIF TX to J28; optical RX not supported | CM6646 is the upgrade path. |
| Speaker | PAM8302A U71 (mono sum); SD# from CM108B GPIO3; J29 | |
| Management | TLC59116 U80 (diag D1–D8, power D20; D21–D26 DNP since 2026-10-02); LIS2DH12 U81; ID EEPROM BL24C64A U82 (0x51); Halls U30/U31; SW2 DIAG | |
| RTC | BT1 → R30 1 k → D30 BAT54WS → VBAT_RTC (HS1 A26) | |
| Power | §7 | |

---

## 7. Power tree and budget

- **Chain:** J3 +12V_MAIN → U40 TPS259824 (ILIM ≈ 10 A, UVLO ≈ 10.5 V) → +12V_EFUSE_OUT → **RS90 1 mΩ 2512** → +12V_IOB (ICD rev 2), which feeds:
  - U41 TPS56C215 → **5V_C** (USB-C PP5V).
  - U42 TPS56C215 → **5V_A** (USB-A, hubs, codec, amp, HDMI 5 V).
  - U43 TLV62585 → **3V3** (from 5V_A).
- **Standby:** 3V3_SB comes from the BP over IOB-LINK (U80–U83, LEDs, Halls).
- **Budget:**

  | Load | Power |
  |---|---|
  | USB-C, 6 × 15 W | 90 W |
  | USB-A, 4 × 4.5–7.5 W | 18–30 W |
  | Logic | ≈ 9 W (incl. ≈ 1 W for i226 #2 [Estimate]) |
  | Fan via CONN_C (F90 1.5 A PTC) + AirPort/BT (ICD 2026-10-02) | ≈ 8–13 W [Estimate; stock fan current M-IOC1] |
  | Worst case at 12 V | ≈ 125–140 W (was 117–127 W without the fan) |

- **ICD 2026-10-02:** the unmanaged worst case (≈ 125–140 W ≈ 10.4–11.7 A) exceeds U40's ILIM ≈ 10 A. The D-IO1 pool cap (45–60 W USB-C) keeps it at ≈ 95–110 W. The pool cap is therefore a hard requirement, not just a recommendation, unless ILIM is raised (ampacity of the stock 12P DC pins is unknown, M-CC16).

- **Recommendation (D-IO1):** 5 V / 3 A is advertised at attach, with a 45–60 W USB-C pool. The BP MCU sets the TPS65994 source PDOs over I²C and drops extra ports to 1.5 A.

- **ICD rev 2 (2026-10-02 ≈ 13:15 ET): power monitor + live power target.**
  - **U98 INA228** (VSSOP-10, I2C_SYS **0x41**: A1 = GND, A0 = VS; VS = 3V3_SB, C990 100 nF) measures the whole IOB 12 V across RS90. ALERT (OD) joins **IOB_INT_N** (IOB-LINK pin 10, wired-OR with the existing sources). The BP MCU reads it in the 10 Hz loop (spec §5.5).
  - **System ceiling** is now **445 W** at 12 V (PSU 450 W); the IOB's share in the static allocation is the 45 W pool + USB-A at ILIM + fan + logic (≈ 80–90 W). The pool can grow to 60 W only when the BP grants headroom.
  - **PD-pool actuator:** BP MCU → I2C_SYS → U83 TCA9517 → I2C_PD → TPS65994 (source caps + "SSrC" 4CC, ≈ 0.5–1 s renegotiation [Unverified]). I2C_PD also carries the port-module muxes U95/U96 (0x70/0x71, §4.7.9); the TPS65994 I2C1 targets use 0x20–0x27, so nothing clashes.
  - **Status:** schematic only (ERC 0). **PCB placement of U98 / RS90 is open (ICD U-18)** — RS90 belongs in the 12 V path right after U40, U98 within 10 mm with a Kelvin pair.

---

## 8. PCB

- **Stackup:** 6 layers, JLC06161H-2116.
- **Netclasses:** USB3_90R, DP_100R, PCIE_85R, USB2_90R, MDI_100R, PWR_5V, PWR_12V. Default clearance 0.1.
- **Placement:** see `floorplan_iob_A0.png`, `render_port_side_F.png` and `render_psu_side_B.png`.
- **2026-10-02 ≈ 10:15 ET changes (flex scan + D0):** ports moved to the flex cut-out grid (USB-C X 43.09 / 63.69, Y 75.76 / 65.84 / 55.97; USB-A, ETH, HDMI per §4.1). SW1 / D20 moved to (63.79, 108.11 / 103.38) and set DNP. D21–D26 are DNP and D22 moved to X 53.42. Part numbers and heights are in the values. RJ45 and riser footprints are pending D-IO14/15. DRC 0 / 0 / 0.
- **2026-10-02 changes (D-IO2):** U52/U53/Y6/L45 added on B; J25/J26 on the HR913790A footprint (from the HanRun drawing, verify row offsets); J26 populated; Y2 moved to (53.0, 95.5) to clear the wider jack shield pins.
- **2026-10-01 changes:** J30 and J31 added on F. U83/U84/L44 placed on B. The duplicate PD flash (old U5) was removed. J2 moved to Y 150.6 to clear the AC keep-out. J6 moved to Xb 80. J4 moved to Xb 8.75.
- **DRC:** 0 violations, 0 unconnected, 0 footprint errors (`drc_report.txt`).
- **ERC:** 0 / 0 (`erc_report.txt`).
- The netlist has not been pushed to the PCB yet, so pads are unassigned; routing comes next.

---

- **2026-10-02 ≈ 10:50 ET**:
  - Removed from the main board: USB-C J11–J16, USB-A J21–J24 and HDMI J27 (they move to the risers).
  - Added on F: JR1–JR5 DF40C receptacles, PG1–PG16 VBUS/GND pogo pins, cradle holes H21–H30, and riser outlines on Dwgs.User.
  - J25/J26 are now non-magnetic SMD RJ45; T1/T2 V24P05S sit on B.
  - Added on B: J7 CONN_C (DF12-40) with standoffs H14/H15 at the stock spots, U90 EMC2101 (44.0, 11.0), U91 ASM1182e (24.0, 130.0), U35 CH334R H3 + Y7.
  - DRC 0/0/0 (`--severity-all`), ERC 0. Riser PCBs DRC 0.

- **2026-10-02 ≈ 12:00 ET (tilt 12.5°)**:
  - JR1–JR5, PG1–PG16 and cradle holes H21–H30 moved with the re-computed risers; JR3/JR4 (USB-A, U-turn jumper) at (28.96, 31.59) / (77.93, 31.59).
  - D21–D26 removed (PCB + schematic). DRC 0/0/0, ERC 0; riser_c / riser_a / riser_hdmi DRC 0.

- **2026-10-02 ≈ 11:30 ET**:
  - Added J8 (B, U.FL C88373, fan-assembly antenna cable) and DNP J9 (F, pass-through), net RF_ANT_FAN.
  - T8 bracket keep-out X 38.06–62.92 / Y 0–10.5 on B.Fab + Dwgs.User with a script check; U90 → (65.0, 5.0) rot 90, U70 → (38.0, 24.5).
  - CONN_C signals follow the Apple 12+6 card (LED_WLAN#, 3V3_BT; disables / SMBus dropped).
  - DRC 0/0/0, ERC 0.

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

- **2026-10-02 ≈ 10:50 ET (risers / CONN_C / RJ45):**
  - The DF40 / DF12 / V24P05S / RJ45 / pogo / ASM1182e land patterns are PLACEHOLDERS.
  - The DF40C-50/40 LCSC numbers and the pogo part are TBC.
  - The CONN_C pinout and mating are unconfirmed.
  - The FPC jumper impedance must be TDR-checked.
  - Riser tilt follows R 111.2 (D0-derived); the stock tilt is unconfirmed. **12:00 ET: superseded, tilt = measured 12.5°.** New risks: plug overmold stand-off 0.7–1.4 mm with seats (M-IOT3/M-IOC2); USB-A riser edge gap 0.67; HDMI frame-slot margin 0.19 (photo-based frame); inboard pogo needs a longer (≈ 7.4 working) part.
  - 11:30 ET: J8 antenna receptacle type/position and the T8 bracket outline are unconfirmed (M-IOA1, M-IOB2); the iMac card's U.FL row must be reachable by the stock leads (M-IOA2); R_inner 110 (D0) vs 101.7 (cover scan) is unresolved within ± 0.2 mm at the port edge.
  - The main schematic still lists the port receptacles J11–J24/J27 logically; they physically sit on the riser PCBs, linked by JR1–JR5. The riser schematics and pin maps are still to be drawn.

| Item | Risk | Mitigation |
|---|---|---|
| Land patterns for USB-C, USB-A, RJ45, HDMI, J28, J3, J4 and J31; QFN placeholders for TPS65994AD, TUSB1046A, TUSB1002A, CH334R, i226-V, TDP158 | Wrong pads | Replace them with the datasheet or JLC footprints before routing. |
| Logical pin numbers on the IC symbols | Schematic-to-footprint mismatch | Map every pin from its datasheet. |
| Stock pinouts (PSU, audio, wall flex) | Wrong function | Probe per §9; 0R matrices and DNP links. |
| Plate curvature R and D0 | Ports recessed or proud | M-IOT2 and M-IOF2 before ordering; parametric rebuild. |
| **Measured 12.5° tilt vs R 110 (7° off-normal), 12:00 ET** | Plugs stand 0.7 (USB-C) / 1.1–1.2 (USB-A) / 1.4 (HDMI) mm short of full insertion even with seats; USB 3 SS / HDMI contacts at risk | M-IOT3 (how the stock plugs seat); print a test plate and plug real cables (M-IOC2). Fallbacks: thicker local skin is not possible (flex flat), so either tilt toward the normal (`TILT_OVERRIDE_DEG` 7–9° halves the stand-off) or accept mouths up to ≈ 0.5 proud on the flush edge (`MOUTH_CLR` < 0, only if the case clears). |
| Clip positions | Plate does not latch | VERIFY on the stock plate; print one test plate. |
| i226-V availability (now 2 per board) | Ethernet missing | Check JLC/LCSC stock (KTI226V C26159200) for 2 × qty. |
| **HR913790A not stocked at LCSC** | Assembly delay | JLC global sourcing or consign; fallback Amphenol RJMG2V1SLN12W5R (LCSC C6647577, vertical shielded, 2.5G rating unverified) or a non-magnetic vertical jack + discrete 2.5G transformer. |
| **ETH jack set-back** (both jacks behind the frame plane) | Jack hits the frame, or plug latch/boot hard to reach | M-IOF2 must show D0 ≥ 16.9 + frame-back depth + 0.3. The plug protrudes ≈ 8 mm from the jack face; set-back ≤ ≈ 5 mm keeps the latch reachable [Estimate]. Some snagless boots may touch the plate. |
| **Measured D0 18.0 / 16.5 (§4.7.4)** | No catalogue USB-C/USB-A/HDMI is tall enough (need 17.2–17.9, have 15.0); HR913790A too tall (16.9 vs ≤ 13.6) | Port risers (D-IO14) and a non-magnetic RJ45 + magnetics (D-IO15). Confirm where the 16.5 was read (M-IOD0), the stock wall (M-IOS1) and the board-top reference (M-IOS2). |
| **Plug seating on the curved plate (no lands)** | Plug recess USB-C 0.62–0.67, USB-A 1.7–1.8, HDMI ≈ 2.0: partial mating, USB 3 SS contacts | Print a test plate and try real cables (M-IOC2). Fallback: a 7° wedge riser per column (stock-like). |
| **Plate-side LEDs / button carrier height** | Flex does not lie flat if they are taller than 0.6; pocket wall only 0.35 (light bleed) | M-IOW4; the pockets are parametric (`LED_H`, `BTN_CARRIER_H`). |
| **HDMI shell vs flex cut-out 5.83** | Shell does not pass, so the face drops behind the flex (recess 3–4) | Pick a receptacle whose front shell is ≤ 15.4 × 5.6 (M-IOH2). |
| *(superseded)* D0 ≈ 22–25 mm from the edge photos (§4.7) | Standard vertical USB-C/USB-A/HDMI sit 5–15 mm too deep; USB-C plugs cannot mate | Caliper D0 first (M-IOF2); then tall parts or a raised port carrier (new decision). Board 2.0 vs 1.6 adds 0.4. |
| *(resolved 10:15 ET: no bosses, columns moved; USB-C margin +0.44)* Stock flex vs land bosses (§4.7) | Flex rims must fold 1.2–2.0 into the frame slots; USB-C shell margin −0.11…+0.32 | Gentle fit test only; A1 replacement flex (D-IO12); shift USB-C columns ≈ 0.25 inboard if the caliper confirms. |
| macOS USB / i226 support | Driver issues, now on 2 ports | USBMap; AppleIGC caveat (spec §8.4); the AQC107 variant is the macOS-native fallback. |

---

## 11. BOM and cost [Estimate]

| Group | Per board |
|---|---|
| ICs (3 × TPS65994AD ≈ $15, 6 × TUSB1046A ≈ $18, 4 × TUSB1002A ≈ $7, 2 × i226-V ≈ $12–18, TDP158 ≈ $3.5, 3 × CH334R ≈ $1.5, CM108B ≈ $1.2, power ≈ $5, management ≈ $3, flashes ≈ $1.6) | ≈ $70 |
| Connectors (MCIO 124 ≈ $8–12, MCIO 74 ≈ $6–9, 6 × USB-C ≈ $5, 4 × USB-A ≈ $2, 2 × RJ45 HR913790A ≈ $4–8, HDMI, Micro-Fit, GH15, ZIF ≈ $0.3, FPC 50P, stock headers ≈ $2–6) | ≈ $38 |
| Passives, inductors, crystals, nuts, holder | ≈ $7 |
| **Total parts** | **≈ $115** (was ≈ $105; **+ ≈ $9–14 per board** for i226 #2, its NVM/crystal/inductor/passives and the second jack) |
| 5 × 6-layer PCBs + 2 assembled (JLC turnkey, extended-part fees) | ≈ $720–930 total (+ ≈ $20–30 for 2 assembled boards; no new unique part types, so no new extended-part fees; HR913790A needs global sourcing for both jacks) |
| Plate, MJF PA12 × 2 + clear SLA button cap | ≈ $25–45 plus shipping |
| D21–D26 light-pipe LEDs + PMMA rods | Now DNP / not bought: ≈ −$1 per board |
| Foam or 0.25 Formex insulator (from `io_flex_foam_insulator_A0.dxf`) | ≈ $2–8 one-off (only if the stock foam is unusable) |
| A1 replacement flex (if the stock flex does not fit) | ≈ $40–90 for 5 + LEDs/dome, one-time [Estimate] |

---

## 12. Measurement list

| ID | What |
|---|---|
| **M-IOT1** | Port-face angle per column with a phone inclinometer (zeroed on the PCB), plus caliper inboard/outboard face heights (§4.4). |
| **M-IOT2** | Plate outer-face curvature: steel rule plus feeler gauges at the centre bar and at each column → `CASE_R`. |
| M-IOF1 | Back depth from the board B side to the PSU frame window. |
| **M-IOF2** | *D0 measured 2026-10-02 (18.0 / 16.5).* Still needed: frame thickness and curvature, frame back-plane depth, plate-to-frame gap; originally: **D0 by caliper**: stock board top to the plate crown, installed (photo estimate 22–25, §4.7). Also: stock port-face heights above the board (stack top ≈ 20–23 est.), frame thickness and back-plane depth, plate-to-frame gap at the centre bar, H13 standoff height, centre-screw head height. ETH gate: HR913790A face ≥ 0.3 behind the frame back plane (≈ 1.8–4.8 est.). |
| **M-IOD0 (first)** | Where the 16.5 D0 edge reading was taken (distance from the centre bar; assumed 15.5) and on which side. Ideally D0 at 5 points across (−20, −10, 0, +10, +20). |
| **M-IOS1** | Stock plastic cover wall thickness at the crown and near the ports (assumed 1.2). |
| **M-IOS2** | Stock board thickness and which face sits on the bosses; is D0 referenced to the same top face our board will have? |
| **M-IOW4** | Height of the flex's plate-side LED chips and of the button carrier ring; which flex face carries the LEDs; caliper HOLE_C1 (scan Ø3.3, low confidence) and AUD_O. |
| **M-IOH2** | Stock HDMI receptacle front shell size (must be ≤ 15.4 × 5.6 to pass the flex); the USB-A shell size with its spring fingers. |
| **M-IOC2** | Plug test on a printed plate: USB-C, USB-A (USB 3 link), HDMI and RJ45 cables seated at the computed recesses. |
| **M-IOW1** | 821-2222 flex by caliper: outline, the 15 port cut-outs (especially the TB holes: is the 8.94 USB-C shell clear?), frame-hole holes, LED and pad positions; check against `flex_821-2222_trace.dxf`. |
| **M-IOW2** | Foam thickness, free and compressed, plus flex thickness with PSA (`FOAM_T`, `FLEX_T`, `FLEX_POCKET`). |
| **M-IOW3** | What backs the stock button dome (bracket, frame tab, shroud?), and the dome travel/force. Is the rigid IC tab glued, free or clipped? |
| M-IOF3 | Front height envelope outside the plate for the power stage (U40–U42, L41/L42). |
| M-IOF4 | HS1 (J1) and J2 plug clearance over the psu_frame top bead (Y ≈ 163) and window top (Y ≈ 160). |
| M-IOH1 | Hall sensor positions and magnet polarity (stock: magnet ≈ 1 inch right of the power button overrides the interlock). |
| M-IOP1 | Port grid with calipers (the face centres in §4.1). |
| M-IOC1 | CONN_C full pin map on the stock board (§4.7.7 probing list): GND, 12 V, 3.3 V, PWM, TACH, PCIe pairs, REFCLK, USB2, PERST#/CLKREQ#/WAKE#, disables. |
| M-IOC3 | CONN_C mating: stock cable plug markings, mated height, pin-1 side, bosses; confirm the DF12-40 footprint or find the Apple/Panasonic/JAE part. |
| M-IOT2 | *Measured 2026-10-02 11:47 ET: 12.5° outward, mirrored.* Confirm the reference (board normal, not gravity) and whether USB-C / USB-A / HDMI all share it. |
| **M-IOT3** | Stock mouths vs the cover: recess at the inboard and outboard shell edges of a USB-C, USB-A and the HDMI; with a stock-size cable plugged, the gap between overmold and cover on the high side; are there flat seats / facets round the stock openings? |
| **M-IOA1** | Fan-assembly antenna cable: connector type on the stock IOB (U.FL / MHF / W.FL), exact position (expected ≈ (38.4, 16.0) B), and where its RF goes on the stock board (PCB antenna? a second connector? which card antenna feeds it). |
| **M-IOA2** | iMac card in the fan-assembly adapter: do the 4 stock antenna leads reach its U.FL row; which lead is BT; trimmed-section clearance. |
| **M-IOB2** | T8 fan-cable bracket: outline, thickness, standoff height and thread, ground contact; confirm the B keep-out X 38.06–62.92 / Y 0–10.5. |
| **M-IOK1** | Plate clip positions by caliper from the cover edge (the phone scan cannot resolve them). |
| M-IOR1 | RJ45 ZJLQ-RJ45-SMD-PCB125-8P8C height (≤ 13.0) and latch orientation; V24P05S pin map. |
| M-IOR2 | Riser underside gaps after assembly (DF40 C-fold space 4.4–6.5; pogo working height 5.9–7.1). |
| M-IOB1 | I/O-wall flex J31: count, pitch, contact side, button pair, GND, I²C, LED supply (§9.5). |
| PSU | §9.1 (also confirm the 11/12 contact count). |
| Audio | §9.2. |
| Speaker | §9.3. |
| Board | Stock board thickness by caliper (photo estimate **≈ 2.0**, §4.7), and which face sits on the case bosses. |

---

## 13. Files

- **2026-10-02 ≈ 10:50 ET additions**:
  - `kicad/macpro62-io-risers/`: `risers.json` (geometry), `MP62_RISER.pretty`, and `riser_c/`, `riser_a/`, `riser_hdmi/` (PCB, project, DRC report, top/bottom renders), built by `tools/build_risers.py`.
  - `kicad/macpro62-io-board/tools/risers_geom.py` (riser geometry from the plate stack) and `tools/make_fps_risers.py` (DF40C-80/50/40, DF12-40, RJ45 no-mag, V24P05S, pogo, cradle holes, ASM1182e).
  - `mechanical/io_plate_v2/io_plate_v2_A0_section.png` (tilted risers + cradles).
- **2026-10-02 ≈ 12:00 ET (tilt 12.5°)**: `io_plate_v2_A0_features.json` gains `tilt` (per-port flex / foam / frame margins, stand-offs, seats) and per-port `seat_floor`; `risers.json` gains `checks` (edge gaps, DF40 gaps, pogo classes), `btb_side`, `h13_notch_x_pcb`.
- **2026-10-02 ≈ 11:30 ET additions**:
  - `mechanical/io_cover_scan/`: `scan_overlay.py`, `io_cover_scan_check.json`, `io_cover_scan_overlay.png`, `README.md` (the raw 38 MB PLY and the npy/npz intermediates are kept on the box, not zipped).
  - `kicad/macpro62-io-board/MP62_IO.pretty/MP62_UFL_Hirose_U.FL-R-SMT-1.kicad_mod`.

| Path | Content |
|---|---|
| `kicad/macpro62-io-board/` | KiCad project, `MP62_IO.pretty` (footprints), `MP62_IO.kicad_sym`, `tools/` (make_fps, build_pcb, build_sch, postprocess, floorplan, io_geom.json, placement.json), `docs/` (HS1 pinout CSV, netlist summary), DRC/ERC reports, renders |
| `mechanical/io_plate_v2/` | Plate STEP/STL ×2, DXF ×2, features JSON, previews, sources, README; **flex trace DXF/JSON + check PNG, foam/insulator DXF** |
| `macpro62-io-board.zip` | Everything above plus this plan |
