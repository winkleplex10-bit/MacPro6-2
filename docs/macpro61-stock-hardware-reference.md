# Mac Pro (Late 2013), MacPro6,1: stock hardware reference for the "MacPro6,2" PCB project

*Compiled 2026-09-29 from public sources. Every specific fact has a citation, keyed to the Sources list at the end ([S1], [S2], …).*

## How to read this document

**Confidence tags** used throughout:

| Tag | Meaning |
|---|---|
| **[Apple]** | Apple primary source: the service guide, the tech-spec pages, or a support article. |
| **[Teardown]** | Third-party physical inspection or measurement, such as iFixit or AnandTech. |
| **[Vendor]** | Parts-reseller listing. Part numbers are usually right, but not authoritative. |
| **[Community]** | Forum or Reddit claim. Unverified. |
| **[Inference]** | My own deduction from the sources. Verify it before relying on it. |
| **UNKNOWN** | Not publicly documented. Needs measurement. |

**Naming.** Apple's names for the boards differ from iFixit's. This document uses Apple's service-guide names.

| Apple service-guide name | iFixit / community name | Where it sits |
|---|---|---|
| **Logic board** | "Interconnect board" | Round board at the bottom, under the core |
| **CPU riser card** | "CPU board" | One face of the triangular core |
| **Graphics board A** / **Graphics board B** | "GPU boards" | The other two core faces. The SSD is on B. |
| **I/O board** (+ I/O wall) | "I/O board" | Rear. The PSU is mounted on it. |
| **Interposer board** | "Top board" | Inside the exhaust assembly, under the fan. Carries the Wi-Fi/BT card. |

The main source is Apple's own *Mac Pro (Late 2013) Service Guide* (344 pages). A copy is publicly attached to a MacRumors thread [S1]. Page numbers ("SG p.N") are PDF page numbers. A local copy is in `macpro61-refs/`.

---

## 0. Most important findings for the PCB design (summary)

1. **The bottom "interconnect" board is not passive. It is Apple's logic board.**
   - It carries the Intel C602J PCH (BD82C602J), the SMC (TI LM4FS1BH), the 64 Mbit EFI boot-ROM SPI flash (MXIC 25L6406E), the system clock generator, a Renesas H8S/2113, and an accelerometer [S2 step 16][S1 p.22].
   - A COM-HPC or COM Express module has no DMI 2.0 link to drive a stock C602J.
   - So "keep the stock bottom board" means one of two things: use it as a copper router with the PCH and SMC idle (unproven), or replace it. **This is the biggest plan-changing finding.** See §9.
2. **Stock PCIe topology** [Apple, S1 p.22]:
   - The CPU (Ivy Bridge-EP, 40 lanes Gen3) sends x16 to GPU A, x16 to GPU B, and x8 Gen3 to a PLX PEX8723 switch on the I/O board.
   - The PEX8723 fans out to three Intel DSL5520 Thunderbolt 2 controllers (each PCIe Gen2 x4) and the USB 3 controller.
   - The PCH supplies the SSD link (Gen2 x4, routed *through GPU B*), 2× Broadcom BCM57762 GbE (x1 each, on the I/O board), and Wi-Fi (x1 Gen1, on the interposer board).
3. **Video to the rear ports comes from GPU B.** GPU B's DP0–5 outputs feed the three TB2 controllers and an HDMI mux/retimer (Parade PS8401A) on the I/O board [S1 p.22][S2].
   - The DP links must therefore cross GPU-B flex → logic board → I/O flex [Inference].
   - A new design that keeps the stock I/O board must feed it up to 6 DP streams plus x8 PCIe on the stock pinout.
4. **Board-to-board connections use three flex cables with mezzanine connectors at both ends**: GPU A, GPU B and the I/O board to the logic board.
   - iFixit identifies these as **FCI (now Amphenol) MEG-Array** [S2 step 11]. MEG-Array is a standard, still-catalogued family on a 1.27 mm BGA grid, including 300-position (10×30) parts [S3]. That makes the connector probably *obtainable*.
   - **The exact Apple part (positions, gender, stack height) is not published.** Community estimates are about 300 pins per connector [S4].
5. **The CPU riser plugs into the logic board with PCB gold fingers in a card-edge slot.** It is not a mezzanine. The community estimates about 324 contacts, but the pitch, card thickness and slot part are UNKNOWN [S4].
   - 12.1 V comes into the riser separately, through two bus-bar screw terminals [S1 pp.298–320, 342].
6. **The PSU is a 450 W, single-rail 12.1 V (37.2 A) unit with an 11 V / 5 W standby output** [S2 step 22][S1 p.22][S5].
   - Main 12 V reaches the CPU riser and both GPU boards via bolted bus bars. 11 V standby and the control signals go to the I/O board over two cables.
   - A dual Hall-effect sensor on the I/O board (the housing interlock) kills 12 V when the outer shell is off [S1 pp.20, 22, 164].
   - **The PSU signal-cable pinout is not public.**
7. **Thermal envelope.**
   - Every Apple-shipped CPU is 130 W TDP [S6 p.4].
   - Apple's rated maximum wall power is 205–270 W depending on configuration [S7].
   - AnandTech measured 437 W average / 463 W peak with CPU and both GPUs loaded, after which the CPU throttled to 2.1 GHz. The GPUs ran at 97 °C [S6 p.14].
   - Apple itself said the core "designed ourselves into a bit of a thermal corner" for single large GPUs [S8].
   - Plan for about 130 W on the CPU face and roughly the same or less per GPU face. A single ≥200 W GPU on one face is high-risk.
8. **The fan has a 3-phase BLDC motor (Nidec) driven by an Allegro A5940 controller on the fan itself.** The fan interface is therefore most likely 12 V, GND, PWM and tach (FG) [S2 step 10][S9]. This is [Inference]; confirm the pinout by measurement.
   - The fan signals run fan flex → interposer board → interposer flex → I/O board → I/O flex → SMC on the logic board [S1 pp.22, 196–233].
9. **The SSD slot is an Apple 12+16-pin blade connector on graphics board B.** It is fed with PCIe Gen2 x4 from the PCH [S1 p.22][S2 step 14].
   - Passive M.2 NVMe adapters exist, e.g. Sintech ST-NGFF2013-C [S4][S10], plus the switch-based Amfeltec AngelShark [S11].
   - No text pinout of the Apple blade has been published. A passive adapter can be continuity-mapped non-destructively.
10. **Mechanical data.**
    - No published board outlines, thickness, CAD, DXF or STEP of the internal boards were found. Community models are exterior-only.
    - The only reliable numbers are the enclosure (251 mm × 167 mm Ø [S5]), Apple's fastener and torque chart [S1 p.342], and the AngelShark size (178 × 65 mm) as a space hint on the GPU-B face [S11].
    - All internal board geometry must be measured.
11. **Closest precedent.** Nobody has publicly put non-Apple compute boards on the stock thermal core. The nearest are:
    - CodeJingle's partial delayering/pin-mapping, later abandoned [S4].
    - Apple-internal development cards that replace a GPU board on the stock flex and break out its x16 into M.2 slots (surfaced on Reddit, April 2026) [S4 p.47–48][S12].
    - The Amfeltec AngelShark.

---

## 1. Overall architecture

### 1.1 Board and module inventory

| Assembly (Apple name) | Apple service part no. | PCB / other number | Key contents | Source |
|---|---|---|---|---|
| **CPU riser card** | 661-7543 / 661-7544 / 661-7545 / 661-7546 (one per CPU SKU) | 820-5494-A [Vendor] | LGA2011 (Socket R) CPU; 4× DDR3 ECC RDIMM slots; VRM (Intersil ISL6367 controller + IR3575 power stages); SMSC EMC1428 temperature sensor; diagnostic LEDs CPU_PROCHOT, MEM_EVENT, CPU_CATERR, CPU_ERROR | [S1 pp.17–18, 300–320][S2 steps 18–20][S13] |
| **Logic board** (iFixit: "interconnect board") | 661-7527 | 820-3637-A [Vendor] | Intel BD82C602J PCH; TI LM4FS1BH (SMC); Renesas H8S/2113 MCU (role unknown); ICS 932SQL435 clock generator; LM393 comparator; MXIC 25L6406E 64 Mbit SPI flash (boot ROM); accelerometer; "GCON" GPU power-enable controller; CPU riser card-edge slot; 3× mezzanine connectors (GPU A flex, GPU B flex, I/O flex) | [S1 pp.22, 189–194][S2 step 16][S14][S15] |
| **Graphics board A** ("Compute") | 661-7531 (3 GB D500), 661-7532 (6 GB D700), 661-7533 (2 GB D300) | 820-3533-A (D500 3 GB), 820-3627-A (D300 2 GB) [Vendor, low confidence] | AMD FirePro D300/D500/D700 GPU + GDDR5; GPU VRM; temperature sensors; mezzanine connector to GPU flex; 2 bus-bar terminals | [S1 pp.22, 282–297][S14] |
| **Graphics board B** ("Render") | 661-7547 (6 GB), 661-7548 (3 GB), 661-7549 (2 GB) | not found | As board A, **plus the PCIe flash-storage (SSD) slot**. Its DP0–5 outputs drive the rear ports. **Required for minimum boot.** | [S1 pp.11, 22, 282–297][S2 step 14] |
| **I/O board** (with I/O wall) | 661-7553 | 820-3552-A [Vendor] | PLX PEX8723 PCIe switch; 3× Intel DSL5520 Thunderbolt 2 controllers; Fresco Logic FL1100 USB 3 controller; 2× Broadcom BCM57762 GbE; Cirrus Logic CS4208 audio codec; Parade PS8401A HDMI retimer + DP mux; dual Hall-effect interlock sensor; 8 diagnostic LEDs + DIAG button; PSU mounting | [S1 pp.19–22, 234–262][S2 steps 23–25][S16] |
| **I/O wall illumination / LED flex** | part of the I/O wall | – | Illuminates the port icons (21 LEDs per SG). LED-flex microcontrollers on I2C. Power button. | [S1 p.22][S2] |
| **Interposer board** | (part of the exhaust assembly) | not found | Carries the Broadcom BCM4360 Wi-Fi/BT card and the fan flex connector. Links to the I/O board through the interposer flex. | [S1 pp.22, 196–233][S2 steps 8–9] |
| **Power supply** | 661-7542 | 614-0521, Delta ADP-450AF [Vendor] | 450 W; 12.1 V main (37.2 A); 11 V / 5 W standby | [S1 p.22][S2 step 22][S17] |
| **Fan** | 923-0491 [Vendor]; 610-0181 [Vendor] | Nidec AG720K01 motor; Allegro A5940 driver on the fan | Single impeller at the top, exhausting upward | [S2 step 10][S15] |
| **Flex cables** | Graphics flex 923-0500 (×2, also listed as 821-1880 [Vendor]); I/O flex 923-0501; interposer flex 923-0496 | – | Mezzanine connectors at both ends (graphics and I/O flexes). Locking-lever connectors on the interposer flex. | [S15][S1 pp.169–170, 195] |
| **Bus bars** | 923-0684 [Vendor] (CPU bus bars + bus bars A/B) | – | 12.1 V distribution from the PSU to the CPU riser and GPU boards | [S1 pp.298–299, 342][S15] |
| **Thermal core** | part of the "core" assembly | – | Triangular extruded aluminum heat sink. The CPU and the two GPU boards mount to its three faces. | [S1 pp.23–28][S2] |

Vendor-listed 820-numbers (820-5494-A, 820-3637-A, 820-3552-A, 820-3533-A, 820-3627-A) come from reseller listings, not from Apple. Confirm them by reading the silkscreen on your own boards; a photo is fine and no disassembly beyond what you already do is needed.

### 1.2 Physical topology

Summary of the connections, from SG pp.22–28 and the take-apart sections [S1]:

```
                 [Fan] --fan flex (vertical blind-mate)--> [Interposer board + Wi-Fi/BT]
                                                                 |
                                               interposer flex 923-0496 (locking-lever conns)
                                                                 |
 [GPU A] ==GPU flex 923-0500 (mezz↔mezz)==\                     [I/O board + I/O wall]
                                           [LOGIC BOARD]==I/O flex 923-0501 (mezz↔mezz)==/   |  \
 [GPU B + SSD] ==GPU flex 923-0500========/  (PCH, SMC,                          PSU DC cable   PSU signal cable
                                              ROM, clock)                                  \   /
 [CPU riser] ==gold-finger card edge into logic-board slot                               [PSU 450 W]
                                                                                     |  4 bus-bar screws
 12.1 V bus bars:  PSU ──> CPU riser (2 screws);  PSU ──> bus bar A ──> GPU A (2 screws);  PSU ──> bus bar B ──> GPU B (2 screws)
```

Mounting and bring-up notes:
- The **PSU is mounted on the I/O board** and sits between the CPU riser and the I/O board. Bus bars A/B pass through slots in the core to reach the GPU boards [S1 pp.250–262, 298–299].
- **Minimum configuration for booting** [S1 p.11]: PSU, 1 DIMM, **graphics board B**, I/O board, AC inlet, CPU riser, logic board, I/O wall. Graphics board A is not required.
- Community report: booting with one GPU runs the CPU at about 1.2 GHz, with the fan at full speed and a warning LED lit [Community, S4 p.28].

### 1.3 Official block diagram

Apple's system block diagram (SG p.22) is saved at `macpro61-refs/apple_service_block_diagram_MacPro_Late2013.png`, with zoomed crops alongside it. §2.3 summarizes it.

---

## 2. Interconnect

### 2.1 Connector inventory

| Link | Connector type | Known details | Confidence / source |
|---|---|---|---|
| GPU A ↔ logic board | Flex 923-0500 with mezzanine connectors at both ends | iFixit: "FCI Meg-Array connector… the same type used for G4 & G5 daughtercards". Community: about 300 pins per GPU flex; one poster counted "about 206" visible contacts. Apple: "not all pins on board connectors are live". | [Teardown S2 step 11][Community S4 p.6][Apple S1 p.170] |
| GPU B ↔ logic board | Same flex 923-0500 | Same as GPU A. It also carries the SSD PCIe x4 and the DP outputs to the logic board [Inference from S1 p.22]. | as above |
| I/O board ↔ logic board | Flex 923-0501 with mezzanine connectors at both ends | Apple's tool uses a *large* hook for the I/O-flex stiffener and a small hook for the GPU flexes [S1 p.170], so the I/O connector or stiffener is physically different. It looks similar in size and aspect ratio in service photos, but that is not confirmed. | [Apple S1 p.170][Community S4] |
| CPU riser ↔ logic board | Gold-finger card edge on the riser PCB, into a slot on the logic board | About 324 contacts, "pretty sure all used" (CodeJingle). The riser↔logic board mapping was never done. Pitch, thickness, key and slot part are **UNKNOWN**. | [Community S4 pp.14–16] |
| Interposer board ↔ I/O board | Interposer flex 923-0496, locking-lever connectors, cable bracket 923-0692 at the I/O end | Pin count and pinout **UNKNOWN** | [Apple S1 pp.196–233, 343][Vendor S15] |
| Fan ↔ interposer board | Fan flex cable, "vertical blind-mate connector" | Pinout **UNKNOWN** (probably 12 V / GND / PWM / FG, see §4) | [Apple S1 pp.197, 230] |
| PSU ↔ I/O board | "Large" PSU DC-out cable and "small" PSU signal cable | Connector type and pinout **UNKNOWN**. CodeJingle mentions "7 unknown pins of the power supply". | [Apple S1 p.250][Community S4] |
| PSU ↔ CPU riser, GPU A, GPU B | Bolted copper bus bars | 4 T8 screws (923-0712, 0.85 N·m) at the PSU; 2 T8 screws (923-0712, 0.85 N·m) at the CPU riser; 2 T8 screws (923-0716, 1.2 N·m) at each GPU board | [Apple S1 p.342] |
| I/O wall LED flex / power button ↔ I/O board | Flex connector | Community: "Pin 3 and pin 6 on the IO Wall connector act as the power button" | [Community S4 p.19, unverified] |
| SSD ↔ GPU B | Apple proprietary 12+16 blade slot | See §6 | [S2 step 14][S4] |
| Wi-Fi/BT card ↔ interposer board | Apple proprietary Wi-Fi card slot (BCM4360) | Secured by 2 T5 screws 923-0725 | [S1 p.343][S2] |

### 2.2 The mezzanine connectors: what is known about MEG-Array

**Identification.** iFixit's teardown calls the GPU-flex connectors FCI MEG-Array [S2 step 11]. FCI's connector business is now part of Amphenol ICC. The MEG-Array datasheet [S3] (saved as `macpro61-refs/Amphenol_MEG-Array_datasheet.pdf`) gives:
- 1.27 mm × 1.27 mm grid; BGA solder-ball attach to the PCB on both plug and receptacle.
- Sizes from 81 to 528 positions. A **300-position (10 × 30 array)** size is standard. Example PNs: plug 84500 (0 mm stack contribution), plug 84578 (6 mm); receptacles 84501 (4 mm), 84502 (5.5 mm), 84553 (8 mm). Mated heights run 4–14 mm.
- 2.0 A per contact; rated durability 50/100/200 mating cycles (plating-dependent).

**What is NOT confirmed** for Apple's parts:
- Positions (300? 400?); which end is plug vs receptacle; mated height; whether Apple used a custom or stiffened variant (the SG mentions a "stiffener" on each cable connector, S1 p.170).
- The pinout.
- Whether the I/O connector is the same size as the GPU connectors.

Evidence for about 300 positions:
- My visual estimate from the service photos is about 10 × 30 [Inference].
- CodeJingle: "~920 pins" across the three logic-board flex connectors [Community S4].

**Obtainability.** If the parts turn out to be catalogue MEG-Array, they can be bought (Amphenol ICC and distributors). That keeps "reuse the stock flex cables" viable. The alternative is fabricating custom flex cables. Zebax sells MEG-Array breakout/test adapters, but only in a 400-position format (ZX181) [S18], so a 300-position probe board would have to be designed yourself.

**Handling (non-destructive):**
- Apple requires mezzanine removal tool **076-1458**. Hook it under the connector stiffener and rock it like a bottle opener, one end then the other [S1 pp.169–170].
- Inspect for bent pins with an LED flashlight at 45°. Replace the cable if its pins are damaged [S1 p.170].
- Mating-cycle ratings are low (50–200) [S3]. Budget connect/disconnect cycles on the working machine. Buy spare 923-0500 / 923-0501 cables for experiments.

### 2.3 Signal allocation (from the Apple block diagram, SG p.22)

| Source | Link | Destination | Physical path [Inference where marked] |
|---|---|---|---|
| CPU (E5 v2, 40 lanes) | PCIe Gen3 x16 (16 GB/s) | GPU A ("Compute") | CPU riser edge → logic board → GPU-A flex. CodeJingle says the logic board routes the CPU PCIe lanes straight through to the GPUs [S4]. |
| CPU | PCIe Gen3 x16 | GPU B ("Render") | same, via the GPU-B flex |
| CPU | PCIe Gen3 x8 (8 GB/s) | PEX8723 switch port 0 (I/O board) | riser → logic board → I/O flex [Inference] |
| CPU | DMI Gen2 x4 | C602J PCH (logic board) | riser edge → logic board |
| CPU | PECI; temperature sensors on I2C | SMC | riser edge → logic board |
| PEX8723 ports 2/3/4 | PCIe Gen2 x4 each (2 GB/s) | Thunderbolt 2 controllers A/B/C (Intel DSL5520) | on the I/O board |
| PEX8723 port 1 | x4 port, used as **x1 Gen2** | USB 3 controller (Fresco FL1100, 4 ports) | on the I/O board. **Conflict:** AnandTech says the USB controller hangs off the PCH instead [S6 p.8]. Apple's diagram shows the switch. Verify with `lspci -t` / System Information on the working unit (non-destructive). |
| PCH | PCIe Gen2 x4 (2 GB/s) | PCIe flash storage | logic board → GPU-B flex → GPU B → SSD slot |
| PCH | PCIe x1 ×2 | 2× BCM57762 GbE | logic board → I/O flex → I/O board [Inference] |
| PCH | PCIe Gen1 x1 (0.25 GB/s) | Wireless card | logic board → I/O flex → I/O board → interposer flex → interposer board [Inference] |
| PCH | HDA | Audio codec (CS4208), I/O board | I/O flex |
| PCH | USB 1.1/2.0 | Bluetooth / internal | not fully legible in the diagram |
| PCH | SATA | – | unused |
| GPU B | DP0–DP5 | TB2 controllers A/B/C (two DP inputs each) and a 5.4 Gbps mux → HDMI retimer (PS8401A) | GPU-B flex → logic board → I/O flex → I/O board [Inference: this is the only path that connects them] |
| GPU A | DP0–5 | not connected to the ports in the diagram | GPU A's DP outputs appear unused, which fits it being "Compute" |
| GPU A ↔ GPU B | "DVO connection" | – | Via the flexes and logic board [Inference]. AnandTech believes the CrossFire bridge runs over this link [S6]. |
| SMC | I2C, ADC, PWM/tach, PwrBtn, PECI | sensors, fan, LED MCUs, PSU control | logic board, plus flexes to the I/O board and interposer board |
| SSD | "OOBv3 to SMC" | SMC | GPU-B flex [Inference] |

**Rough I/O-flex budget** [Inference]: x8 Gen3 + 3 × x1 + HDA + up to 6 DP main links (4 lanes each + AUX + HPD) + SMC sideband + power. That easily fits about 300 positions. If the stock I/O board is to be driven from a new design, however, all of these must be reproduced on the stock pinout.

**Thunderbolt port ↔ bus mapping.** Apple's rear-port numbering and bus grouping are documented by Apple [S19]. Real-world bandwidth notes are in TekRevue [S20] and AnandTech [S6 p.8]. AnandTech notes the PEX8723 is similar to the PEX8724 and that upstream bandwidth is about 15 GB/s [S6 p.8].

### 2.4 Published pinouts

**None are complete.**
- CodeJingle delayered boards and posted partial pinout spreadsheets (LogicBoard1/2/3.numbers via Dropbox, MacRumors thread p.15). He described them as incomplete. The links may be dead [S4].
- He stated the riser ↔ logic board (324-pin) mapping was never done [S4].
- A Rossmann Group forum thread (2020) asking for an A1481 schematic got no schematic [S21]. No leaked Apple schematic (820-3637 / 820-5494) was found publicly.

---

## 3. PSU

| Item | Value | Source |
|---|---|---|
| Apple service part | 661-7542. Vendors list 614-0521 and Delta ADP-450AF. | [S17][Vendor] |
| Rating | 450 W max continuous. 100–120 V / 200–240 V AC input. | [Apple S5] |
| Main output | **12.1 V at 37.2 A** (label) | [Teardown S2 step 22] |
| Standby output | **11 V, 5 W** ("450W 12V, 5W 11V") | [Apple S1 p.22] |
| Cooling | No dedicated fan; relies on the system fan airflow | [S2 step 22] |
| Main 12 V distribution | Bus bars to the CPU riser (2× T8 923-0712 at 0.85 N·m) and via bus bars A/B to each GPU board (2× T8 923-0716 at 1.2 N·m each). Bus bars attach to the PSU with 4× T8 923-0712 at 0.85 N·m. | [Apple S1 pp.298–299, 342] |
| To the I/O board | "11 V + power supply control cables to I/O board" (a large DC cable and a small signal cable). PSU is mounted to the I/O board with 4× T10 ball screws 923-0717. | [Apple S1 pp.22, 250, 343] |
| Sensors | Tp0t (PSU temperature), VD2R (11 V rail), II0R (I/O board 12 V current), among others | [Apple S1 pp.13–14] |

**Power-on sequence** (inferred from the diagnostic LEDs on the I/O board) [Apple S1 pp.19–20]:

| LED | Meaning |
|---|---|
| #1 | Flex check (the flexes are seated) |
| #2 | 11 V standby present (always on with AC) |
| #3 | 12 V main on (after the power button) |
| #4 | Platform reset released |
| #5 | S5 |
| #6 | S0 |
| #7 | S4 |
| #8 | PCIe switch link (fast blink = Gen2, slow = Gen1) |

A DIAG button on the back of the I/O board lights the LEDs when the housing is off.

**Housing interlock** [Apple S1 pp.20, 22, 164]:
- A **dual Hall-effect sensor on the I/O board** senses the outer housing. With the housing removed, the PSU 12 V main output is disabled.
- For LED diagnostics only, Apple describes holding a magnet about 1 inch to the right of the power button to override the interlock.
- **Hazardous energy (>240 VA) is present on the bus bars** when the machine is powered [S1 pp.164, 298]. The I/O flex must not touch the PSU.

**Pinout: UNKNOWN.**
- The PSU signal-cable and DC-cable pinouts are not public.
- PinoutGuide's "Mac Pro PSU J3" pinout is for the 2006–2012 tower (980 W unit) and does **not** apply.
- CodeJingle reported "7 unknown pins of the power supply" [Community S4].
- SMC reset on this machine is "unplug AC for 15 s" [S1 p.9].

A MacRumors thread on testing the PSU bus bars contains only anecdotal readings; the voltages people quote are not trustworthy [S22].

---

## 4. Fan and thermal

### 4.1 Fan

| Item | Detail | Source |
|---|---|---|
| Fan | Single fan at the top of the core. Motor by Nidec (AG720K01). | [Teardown S2 step 10] |
| Driver | **Allegro A5940**, a sensorless sinusoidal 3-phase BLDC driver, on the fan PCB | [Teardown S2 step 10] |
| A5940 interface | PWM speed input: logic-level, up to 6 V, internal 100 kΩ pull-up, about 9% duty minimum threshold. Open-drain FG tach output. VBB typically 12 V. | [Datasheet S9] |
| Probable fan pinout | 12 V (or 11 V) / GND / PWM / FG | **[Inference]**. Measure with the fan connected and in-circuit. |
| Signal path | Fan flex → interposer board → interposer flex → I/O board → I/O flex → SMC on the logic board | [Apple S1 pp.22, 196–233] |
| Fastening | 3× T10 923-0724 at 1.2 N·m (fan to exhaust) | [Apple S1 p.343] |
| **Removal warning** | Removing the fan requires removing the exhaust **roof**, which is attached with VHB adhesive. Apple requires installing a **new roof**. | [Apple S1 p.202] |
| Sensors | Fan speed is monitored by the SMC and readable in software (e.g. Apple Hardware Test / third-party SMC tools) | [S1 pp.8, 13–14] |

**Non-destructive tip.** The fan interface can be sniffed at the interposer board's fan-flex connector *without removing the roof*. The interposer board is reachable by removing the exhaust assembly [S1 pp.196–233].

### 4.2 Thermal core limits

Apple has not published a thermal-design rating for the core. Available data:

| Data point | Value | Source |
|---|---|---|
| Apple max wall power | D300 / 4-core config: 43 W idle / 205 W max. D500 / 6-core: 43 / 238 W. D700 / 12-core: 44 / 270 W. | [Apple S7] |
| PSU rating | 450 W continuous | [Apple S5] |
| AnandTech worst case (CPU + both GPUs loaded) | 437 W average, 463 W peak at the wall. The CPU then throttled to 2.1 GHz and the GPUs reached 97 °C. CPU-only or GPU-only load ran about 300–320 W. | [Teardown S6 p.14] |
| Apple's own view (2017) | "We designed ourselves into a bit of a thermal corner… larger single GPUs required… more thermal capacity" (Federighi) | [S8] |

**CPU options** (all LGA2011 Ivy Bridge-EP, 130 W TDP) [S6 p.4][S5]:

| Cores | CPU | Base / Turbo |
|---|---|---|
| 4 | E5-1620 v2 | 3.7 / 3.9 GHz |
| 6 | E5-1650 v2 | 3.5 / 3.9 GHz |
| 8 | E5-1680 v2 | 3.0 / 3.9 GHz |
| 12 | E5-2697 v2 | 2.7 / 3.5 GHz |

Community upgrade guides report the 150 W E5-2687W v2 working, but with thermal caveats [Community S23].

**GPU options** (AMD FirePro, Apple-specific) [S6 p.9][S5]:

| GPU | Die | Stream processors | Clock (base / boost) | Memory bus | VRAM | TDP |
|---|---|---|---|---|---|---|
| D300 | Pitcairn | 1280 | 800 / 850 MHz | 256-bit | 2 GB GDDR5 | **Not published** |
| D500 | Tahiti LE | 1536 | 650 / 725 MHz | 384-bit | 3 GB GDDR5 | **Not published** |
| D700 | Tahiti XT | 2048 | 650 / 850 MHz | 384-bit | 6 GB GDDR5 | **Not published** |

Values such as "274 W" found in search-engine summaries are unsourced and should be ignored. A rough envelope from the wall-power data above is about 100–130 W per GPU face [Inference].

### 4.3 Thermal interface and mounting

| Board | Fastening to the core | Thermal interface |
|---|---|---|
| CPU riser | Leaf spring + 4× T10 923-0707 at 1.2 N·m into core standoffs 923-0689 | CPU IHS sits directly on the core face. Apple specifies thermal grease (3 syringes) applied through a stencil. |
| GPU boards | Leaf spring + 4× T10 923-0708 at 1.2 N·m on standoff 923-0690 | Thermal grease on the GPU die, plus VRAM thermal pads. **The pad kit differs:** 923-00323 (D300) vs 923-00324 (D500/D700). So the component-to-core gap differs by SKU. |
| Logic board | 2× T8 923-0711 at 0.35 N·m on standoffs 923-0693 (standoffs torqued at 0.35 N·m) | – |

Sources: [Apple S1 pp.282–320, 342–343].

After service, Apple runs a Cooling System Diagnostic [S1].

Thermal sensors listed in the SG (p.13–14) include:
- TC0p (CPU proximity), TG0d / TG1d (GPU die), Te0t (PCIe switch), TM0p (memory), Tp0t (PSU), plus voltage and current sensors per rail.

A new board that wants the stock SMC to stay happy would need to emulate these. That is not an issue if you replace the SMC.

---

## 5. Board dimensions and mechanical information

| Item | Value | Source |
|---|---|---|
| Enclosure | 9.9 in (251 mm) tall × 6.6 in (167 mm) diameter; 11 lb (5 kg) | [Apple S5] |
| Internal board outlines, thickness, hole positions | **Not published. No CAD, DXF or STEP found.** | – |
| Community 3D models | Exterior shells only (Printables/Thingiverse lookalike cases, e.g. "MacPi Pro"). No internals. | [search, see §8] |
| AngelShark carrier (fits on the GPU-B face region) | 178 × 65 mm | [S11 manual] |
| Fastener and torque chart | Full chart on SG pp.342–343 (excerpted in §§3–4) | [Apple S1] |
| Captive screws | Some captive screws are two-piece and can separate during removal | [S24] |
| Standoffs | Core standoffs can loosen or pull out when screws are removed. Torque to spec. | [S1 pp.308–320] |

**Stock board shapes, from the service photos** in `macpro61-refs/`:
- **CPU riser**: roughly rectangular, with the gold-finger edge at the bottom and the bus-bar terminals at the top corner.
- **GPU boards**: long and narrow, running the height of the core face, with the flex mezzanine near the bottom.
- **Logic board**: a disc with a card-edge slot and three mezzanines.
- **I/O board**: a vertical rectangle behind the I/O wall.
- **Interposer**: small, at the top.

My rough photo-scaled estimate (using DIMM length as scale) puts the CPU riser at about 130 × 155 mm. **This is an estimate only (±15%). Measure it.**

**COM module fit, for comparison** [S25]:

| Standard | Module size | Z-height (top of carrier board, with heatspreader) | Max power |
|---|---|---|---|
| COM-HPC Client | Size A 120 × 95 mm; Size B 120 × 120 mm; Size C 120 × 160 mm | 20 mm | up to 251 W |
| COM Express Type 6 | Basic 125 × 95 mm; Compact 95 × 95 mm | 18 mm | 137 W |

Whether Size A/B or COM Express Basic fits the CPU face, with the module's heatspreader against the core, depends on the measured face width and the PSU clearance behind the riser. Both are UNKNOWN. Note that the stock CPU riser has the socket side facing the core and the back side facing the PSU [S1].

---

## 6. SSD

| Item | Detail | Source |
|---|---|---|
| Location | On graphics board B, facing outward; 1× T8 923-0715 at 0.40 N·m | [Apple S1 p.343][S2 step 14] |
| Connector | Apple proprietary "12+16" blade connector (the same family as the 2013–2015 MacBook Air/Pro). Contact count 55, of which about 28 are unique signals; two solid pads are ground (CodeJingle). | [Community S4][Beetstech S26] |
| Link | PCIe **Gen2 x4** from the C602J PCH (2 GB/s in Apple's diagram). Routed PCH → logic board → GPU-B flex → GPU B → slot. Real-world ceiling about 1.5 GB/s. | [Apple S1 p.22][S4][S26] |
| Sideband | "OOBv3 to SMC" | [Apple S1 p.22] |
| Power sensors | SSD voltage and current sensors are listed in the SG sensor table | [S1 p.14] |
| Stock drives | Samsung (controller S4LN053X01), AHCI | [S2 step 6] |
| Link width conflict | Beetstech says Gen3-generation Apple SSUAX blades are x2 except 1 TB (x4) [S26]. AnandTech describes the Mac Pro drives as x4 [S6]. **Check your own drive in System Information (non-destructive).** | – |
| NVMe boot | Requires boot ROM MP61.0120.B00 or later (installed by macOS High Sierra) | [Community S4][S26] |

**Commercial adapters:**
- **Sintech ST-NGFF2013-C** (passive M.2 M-key → Apple 12+16). The "-C" revision is the one recommended for the Mac Pro 6,1. Users recommend Kapton-taping the adapter's back [S4][S10].
- **PC Parts 239** adapters (similar; availability varies).
- **Chenyang** adapters (reported problems in the thread).
- **Amfeltec AngelShark** (SKU-088-01). A PCIe-switch carrier: x4 upstream from the Apple slot, fanning out to 2× M.2 plus the original Apple SSD. It takes 12 V by replacing GPU B's two bus-bar screws with threaded standoffs; board size 178 × 65 mm [S11]. Manual saved in `macpro61-refs/`.

**Pinout: not publicly documented as text.** Buy a passive Sintech adapter and continuity-map it: M.2 M-key pinout (public PCI-SIG/M.2 spec) ↔ blade pads. This is fully non-destructive.

**Design note** [Inference]:
- On a new GPU-B replacement board, either pass the PCH-origin x4 through to an Apple slot or M.2, or drop the stock SSD path.
- If the stock logic board is not used, the SSD lanes have no source unless the module provides them. A native M.2 socket on the new carrier is simpler.

---

## 7. SMC and system control

**What Apple says the SMC does** [Apple S1 p.8]: controls power on/off, sleep/wake/idle, resets and fans.

**From the block diagram** [Apple S1 p.22]:
- SMC interfaces: PECI to the CPU; LPC/I2C to the PCH; I2C to the accelerometer and ambient temperature sensors; ADC for voltage/current sense; fan PWM/tach; power button.
- **GCON** drives GPU power-enable. It is separate from the SMC on the logic board.
- System clock generator; boot ROM.

**Other system-control items:**

| Function | Implementation | Source |
|---|---|---|
| Main controller | TI LM4FS1BH (an LM4F-series TI ARM Cortex-M part; exact datasheet not public) | [Teardown S2 step 16] |
| Additional MCU | Renesas H8S/2113. **Role unknown** (possibly legacy/LPC or GCON). | [Teardown S2 step 16] |
| EFI boot ROM | MXIC MX25L6406E 64 Mbit SPI flash. Contains the Mac firmware, including GPU EFI support (a community claim says the GPU's boot graphics live in the boot ROM via UGA; unverified). | [S2 step 16][Community S4] |
| I/O panel illumination | LED-flex microcontrollers on I2C drive 21 icon LEDs. iFixit found about 3 probable TI MSP430 MCUs. The accelerometer detects when the machine is rotated; the illumination turns on when motion is detected. | [Apple S1 pp.17, 22][S2] |
| Power button | On the I/O wall, via the LED flex → I/O board → I/O flex → SMC. Community: pins 3 & 6 of the I/O-wall connector. | [Apple S1 p.22][Community S4 p.19] |
| PSU enable | SMC → (I/O flex) → I/O board → PSU signal cable, gated by the Hall-effect interlock | [Apple S1 pp.20, 22][Inference for path] |
| Diagnostic LEDs | CPU riser: CPU_PROCHOT, MEM_EVENT, CPU_CATERR, CPU_ERROR. I/O board: 8 LEDs (§3). | [Apple S1 pp.17–20] |
| Sensors | Dozens of thermal and voltage/current sensors (listed in SG pp.13–14) | [Apple S1] |
| Serialization | The logic board carries the serial number. Replacement boards need Apple's Blank Board Serializer (BBS). | [Apple S1, logic-board replacement section] |

**What a replacement bottom board or controller must replicate** [Inference, based on the above]:
1. Standby power from the 11 V rail. Power-button input. PS_ON-style enable to the PSU and power-good monitoring. Interlock handling. Sequencing: 12 V main → CPU/GPU VRM enables (GCON-like) → platform reset.
2. Fan PWM out and tach in (fan-curve control from CPU/GPU temperatures).
3. I2C master to the I/O-wall LED MCUs (protocol unknown; sniff it on the working unit) and optionally an accelerometer for the "light up on rotate" behavior.
4. Reset or enable lines for the I/O-board devices (PEX8723, TB2 controllers, GbE, USB), which today come from the logic board over the I/O flex. **Pinout UNKNOWN.**
5. If macOS matters: Apple SMC keys cannot be emulated in hardware without an Apple SMC. Hackintosh-style VirtualSMC would be needed.

---

## 8. Existing projects and prior art

| Project | What they did | What they learned | Source |
|---|---|---|---|
| **CodeJingle** (MacRumors, 2017–2018) | Delayered and probed boards to put a non-Apple GPU (Vega) on the GPU flex. Posted partial logic-board pinouts. | The logic board routes CPU PCIe straight to the GPUs. The CPU riser edge has about 324 pins, all apparently used. PSU standby is 11 V (non-standard). The project was abandoned: fried parts, time. | [S4 pp.1–20] |
| **Apple-internal development cards** (Reddit u/dogtooth97, April 2026; reposted in the MacRumors thread) | Boards that replace a GPU board on the stock mezzanine flex and break out x16 to about 6 M.2/x4 slots. Used in Apple imaging stations. | **Proves the GPU-flex x16 can drive arbitrary PCIe devices with the stock logic board and firmware.** The Reddit original could not be fetched from here. | [S4 pp.47–48][S12] |
| **Amfeltec AngelShark** | Commercial switch-based carrier in the GPU-B SSD slot, fitting between GPU B and the housing | Space exists over GPU B for a 178 × 65 mm board. 12 V can be taken from the GPU bus-bar screws. | [S11] |
| **Sintech / PC Parts M.2 adapters** | Passive NVMe adapters | NVMe works with the updated boot ROM. Physical fit is tight; use Kapton. | [S4][S10] |
| **eGPU / AVX2 limits** | – | Newer AMD GPUs need macOS versions that require AVX2, which Ivy Bridge lacks (tsialex) | [S4] |
| **Mini-ITX "trashcan" builds** | Replica or gutted enclosures with standard ITX boards (InsanelyMac "realistic MacPro 2013 build"; tonymacx86 "Mac Pro (2013) Mod"; smallformfactor.net "Mac Pro Late 2013 mini-ITX case mod") | **They discard the thermal core.** Not directly applicable. The tonymacx86 and SFF.net pages could not be fetched (403), so treat them as unverified leads. | [S27][S28][S29] |

**No public project** was found that reuses the stock thermal core and PSU with non-Apple compute boards. MacPro6,2 would be the first known attempt.

---

## 9. Risks that change the plan

1. **The bottom board is the real logic board** (PCH, SMC, boot ROM) [S2 step 16][S1 p.22]. A COM module cannot drive the C602J (DMI). Options:
   - **(a)** Keep the stock logic board as a passive router only, leaving the PCH and SMC powered but idle. Unknown whether the SMC will even enable the PSU 12 V without a valid CPU, PCH and flex handshake ("Flex check" LED #1). It also leaves the SSD, Ethernet, Wi-Fi and HDA without a host.
   - **(b)** Design a new bottom board: COM-module-to-flex router plus your own SMC-replacement MCU. More work, but everything is under your control.
   - **(c)** Keep the stock logic board, CPU riser and GPU B and just add devices on the GPU-A flex, as Apple's dev cards do. This is the lowest-risk first milestone.
2. **Driving the stock I/O board needs its full undocumented pinout**: x8 PCIe to the PEX8723, DP streams for TB2/HDMI, x1 for GbE and Wi-Fi, HDA, resets and SMC sideband. Probing it requires a MEG-Array breakout (self-designed; Zebax only offers 400-position).
3. **Connector procurement.** Probably catalogue Amphenol MEG-Array (buyable), but the exact PN, stack height and gender are unconfirmed. The card-edge slot on the logic board is a completely unknown part. If you replace the logic board, you need a matching slot for a stock-shaped riser, or you drop the edge interface altogether.
4. **Thermal.** The core is sized for three roughly balanced loads totaling about 450 W at the wall, with throttling at the extreme [S6 p.14][S8]. A single large GPU on one face is unlikely to be cooled well.
5. **Power.** 12.1 V only (no 3.3 V/5 V; the carrier must generate them) plus 11 V standby. Hall interlock. Hazardous energy on the bus bars. Undocumented PSU signaling.
6. **macOS.** With a modern module, macOS means Hackintosh-style (OpenCore). No Apple SMC or boot ROM. Treat it as optional, as planned.
7. **Keeping the working unit working:**
   - Don't remove the roof or fan (VHB, needs a new roof).
   - Keep mezzanine mating cycles low; use tool 076-1458.
   - Replace thermal grease and pads after any GPU or CPU removal (SKU-specific pad kits).
   - Standoffs can pull out.
   - Do not power up with the housing overridden except for LED diagnostics.
   - Do all destructive probing on donor or spare boards (dead logic boards and GPUs are cheap on eBay).

---

## 10. Open questions to measure during teardown

All of these can be measured without damage on the working unit (calipers, photos, continuity), or on donor parts.

**Connectors and flexes**
- [ ] MEG-Array identity for each of the 3 logic-board flexes (GPU A, GPU B, I/O): position count (10×30?), plug vs receptacle at each end, mated stack height, stiffener design, housing markings and PN. Check whether all 6 ends are identical.
- [ ] Flex lengths, widths and bend geometry (to design a breakout or pass-through board).
- [ ] Which positions are ground, power or signal (continuity against ground and the 12 V bus on a *spare* flex or dead board).
- [ ] CPU riser gold fingers: contact count per side, pitch, finger length, PCB thickness at the edge, key location. Slot part markings on the logic board.
- [ ] Interposer flex (923-0496) connector type, pin count and pinout. Fan-flex connector type and pinout.
- [ ] I/O-wall LED/power-button flex connector: pin count; verify the claim that pins 3 and 6 are the power button.

**Power**
- [ ] PSU DC-out cable and signal cable: connector types, pin count, pinout (11 V, GND, PS_ON-equivalent, PWR_OK, interlock, I2C/PMBus?). Measure on the working unit with the housing on, by back-probing carefully, or on a spare PSU.
- [ ] Whether the PSU outputs 12 V if enabled with no logic board present (spare PSU only).
- [ ] Bus-bar terminal positions and hole sizes on the CPU riser and GPU boards. Bus-bar cross-sections.
- [ ] Hall-sensor location and magnet polarity (for a new interlock or bypass on the bench).

**Mechanical**
- [ ] Outline, thickness and mounting-hole coordinates of the CPU riser, both GPU boards, the logic board, the I/O board and the interposer board. Scan them flat on a flatbed scanner with a ruler for a DXF trace.
- [ ] Core face flatness and exact face width. Standoff positions and thread. Leaf-spring geometry and force.
- [ ] Z-heights: CPU IHS to core, GPU die and VRAM to core (compare the D300 vs D500/D700 pad kits), component keep-out on each board's back side.
- [ ] Clearance between each board's outer side and the housing. Clearance between the CPU riser back and the PSU.

**Electrical and firmware (non-destructive, from the running OS)**
- [ ] `lspci -tv` (Linux live USB) or System Information → PCI topology. Resolve the USB-behind-switch vs behind-PCH conflict. Confirm the TB/GbE/Wi-Fi attachment.
- [ ] Stock SSD link width (x2 vs x4).
- [ ] SMC keys and fan speed (e.g. `smcFanControl` / `istats` / Linux `applesmc`). Fan PWM frequency and duty at the fan-flex connector.
- [ ] I2C protocol to the LED-flex MCUs (logic-analyzer sniffing at the I/O-wall flex while rotating the machine).
- [ ] SSD 12+16 pinout, by continuity-mapping a Sintech ST-NGFF2013-C adapter.
- [ ] Roles of the H8S/2113 and GCON. Whether the SMC powers the rails with no CPU riser (donor board only).
- [ ] Board 820-numbers from the silkscreen, to confirm the vendor listings.

---

## 11. Files in `/workspace/macpro61-refs/`

| File | What it is |
|---|---|
| `Apple_MacPro_Late2013_service_manual_macrumors.pdf` | Apple Service Guide (344 pp.) [S1] |
| `apple_service_block_diagram_MacPro_Late2013.png` + `block_diagram_crop_*.png` | Official system block diagram (SG p.22) and zoomed crops |
| `svc_IO_board_overview.jpg`, `svc_logic_board_interconnect_overview.jpg`, `svc_CPU_riser_card_overview.jpg`, `svc_graphics_board_overview.jpg`, `svc_interposer_board_overview.jpg` | Board overview photos from the SG |
| `svc_exploded_*.jpg`, `svc_PSU_on_IO_board.jpg`, `svc_bus_bars_*.jpg`, `svc_mezzanine_tool_logic_board_removal.jpg` | Exploded views, PSU, bus bars and the mezzanine tool (SG) |
| `Amfeltec_AngelShark_MacPro2013_hwmanual_v1.1.pdf` | AngelShark hardware manual [S11] |
| `Amphenol_MEG-Array_datasheet.pdf` | MEG-Array connector family datasheet [S3] |

---

## 12. Sources

- **[S1]** Apple, *Mac Pro (Late 2013) Service Guide*, public copy attached to MacRumors: https://forums.macrumors.com/attachments/mp-2013-late-pdf.1962952/. Referenced pages: 8–14 (overview, sensors), 11 (minimum config), 17–22 (LEDs, block diagram), 164–170 (safety, tools, mezzanine), 189–195 (logic board, flexes), 196–233 (exhaust, interposer, fan, roof), 234–262 (I/O, PSU), 282–299 (graphics, bus bars), 300–320 (CPU riser), 342–343 (screw chart).
- **[S2]** iFixit, *Mac Pro Late 2013 Teardown*: https://www.ifixit.com/Teardown/Mac+Pro+Late+2013+Teardown/20778. Related guides: https://www.ifixit.com/Guide/Mac+Pro+Late+2013+Interconnect+Board+Replacement/21209, https://www.ifixit.com/Guide/Mac+Pro+Late+2013+Power+Supply+Replacement/21212, https://www.ifixit.com/Guide/Mac+Pro+Late+2013+I-O+Board+Replacement/21213
- **[S3]** Amphenol ICC, MEG-Array mezzanine datasheet: https://www.amphenol-cs.com/media/wysiwyg/files/documentation/datasheet/mezzanine/mezz_megarray.pdf
- **[S4]** MacRumors, "NVMe with ST-NGFF2013-C / Vega internal GPU Mac Pro 2013 6,1" (48 pages, 2017–2026): https://forums.macrumors.com/threads/nvme-with-st-ngff2013-c-vega-internal-gpu-mac-pro-2013-6-1.2085886/
- **[S5]** Apple, Mac Pro (Late 2013) Technical Specifications: https://support.apple.com/en-us/112025
- **[S6]** AnandTech, *The Mac Pro Review (Late 2013)* (archived): http://web.archive.org/web/2020/https://www.anandtech.com/show/7603/mac-pro-review-late-2013 (p.4 CPUs, p.8 PCIe/TB, p.9 GPUs, p.14 power/thermal; append `/N` for page N)
- **[S7]** Apple, Mac Pro power consumption and thermal output: https://support.apple.com/en-us/102839
- **[S8]** TechCrunch, 2017 transcript, Schiller/Federighi/Ternus: https://techcrunch.com/2017/04/06/transcript-phil-schiller-craig-federighi-and-john-ternus-on-the-state-of-apples-pro-macs/
- **[S9]** Allegro A5940 datasheet: https://www.allegromicro.com/-/media/files/datasheets/a5940-datasheet.pdf
- **[S10]** Sintech ST-NGFF2013-C adapter (as discussed in [S4]; vendor listings vary)
- **[S11]** Amfeltec AngelShark: https://www.amfeltec.com/mac-pro-late-2013-cylinder-ssd-upgrade/. Manual: https://amfeltec.com/wp-content/uploads/2019/06/AngelShark_SKU-088-01_hwmanual_v1.1.pdf
- **[S12]** Reddit r/macpro, "Mac Pro with PCIe slot is real…" (April 2026): https://www.reddit.com/r/macpro/comments/1si6l5f/mac_pro_with_pcie_slot_is_real_and_it_wont_hurt (not fetchable here; content known via [S4] pp.47–48)
- **[S13]** Beetstech, CPU riser board 820-5494-A: https://beetstech.com/product/mac-pro-a1481-2013-cpu-riser-board-820-5494-a
- **[S14]** UsedMac, Mac Pro 2013 parts (820-numbers): https://usedmac.com/product-category/mac-pro-parts-2/mac-pro-2013/
- **[S15]** MacRecycling, exploded view and part numbers, Mac Pro Late 2013: https://www.macrecycling.com/Exploded-30-Mac_Pro_Late_2013.html
- **[S16]** SPW Industrial, Mac Pro Late 2013 I/O board and logic board listings (661-7553 / 820-3552-A; 661-7527 / 820-3637-A): https://www.spwindustrial.com
- **[S17]** Beetstech, Mac Pro A1481 power supply 450 W 661-7542: https://beetstech.com/product/mac-pro-a1481-power-supply-450w-661-7542
- **[S18]** Zebax ZX181 MEG-Array adapter: http://www.zebax.com/doc/ZX1/ZX181-Meg-Array.pdf
- **[S19]** Apple, Mac Pro (Late 2013) Thunderbolt ports and displays: https://support.apple.com/en-us/HT5918
- **[S20]** TekRevue, Mac Pro Thunderbolt performance: https://www.tekrevue.com/tip/mac-pro-thunderbolt-performance/
- **[S21]** Rossmann Group forum, "Mac Pro 2013 A1481 D300 graphics card and schematic" (2020, no schematic provided): https://boards.rossmanngroup.com/threads/mac-pro-2013-a1481-d300-graphics-card-and-schematic.59313/
- **[S22]** MacRumors, "Mac Pro 2013 A1481 power supply test": https://forums.macrumors.com/threads/mac-pro-2013-a1481-power-supply-test.2246813/
- **[S23]** Greg Gant, *The definitive Mac Pro 2013 trashcan guide*: https://blog.greggant.com/posts/2019/05/07/the-definitive-mac-pro-2013-trashcan-guide.html
- **[S24]** Hackjob blog, Mac Pro 6,1 teardown/repaste (2025): https://hackjobblog.blogspot.com/2025/03/apple-mac-pro-61-teardown-repaste-and.html
- **[S25]** congatec, COM-HPC Client vs COM Express Type 6 comparison: https://www.congatec.com/en/technologies/com-hpc-client/
- **[S26]** Beetstech, Apple proprietary SSD guide: https://beetstech.com/blog/apple-proprietary-ssd-ultimate-guide-to-specs-and-upgrades
- **[S27]** InsanelyMac, "Realistic MacPro 2013 build": https://www.insanelymac.com/forum/topic/343022-realistic-macpro-2013-build/
- **[S28]** tonymacx86, "Mac Pro (2013) Mod" (not fetched, 403): https://www.tonymacx86.com/threads/mac-pro-2013-mod.270218/
- **[S29]** smallformfactor.net, "MacPro Late 2013 mini-ITX case mod" (not fetched, 403): https://smallformfactor.net/forum/threads/macpro-late-2013-mini-itx-case-mod.427/
