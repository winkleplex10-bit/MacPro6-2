# MacPro6,2: own AM5 CPU board ("CB-AM5"), DRAFT plan and floorplan fp0

| | |
|---|---|
| Date | 2026-10-04, ≈ 12:30 ET (draft requested by Aidan 12:07 ET) |
| Status | **DRAFT** – block schematic bd0 (ERC 0) + part-level floorplan fp0 (DRC 0, no nets, not routed). **Not for fab:** U1 socket and U2 PROM21 pads are synthetic placeholders (AMD NDA). |
| KiCad | `/workspace/kicad/macpro62-am5/` (new, separate sibling of `kicad/macpro62-lga1700`, which is **unchanged**) |
| Basis | cost study `macpro62-cost-estimate.md` §10 (AM5 what-if); LGA1700 CB plan `macpro62-lga1700-board-plan.md`; ICD rev 3 `macpro62-interface-control.md`; arch spec v0.2 change 35 |
| Tags | [Sourced] datasheet/vendor page · [Estimate] · [Inference] · [Unverified] · [Proposal] |

## 0. Summary

- **CPU:** **Ryzen 5 8600G / Ryzen 7 8700G (Phoenix)**. Dasharo v0.9.0 (coreboot + openSIL `phoenix_poc`) boots **only Ryzen 8000G** on AM5 today; Ryzen 7000/9000 "will not boot" [Sourced: cost study §10.3]. 7000/9000 is a later option. The board keeps the routing for it: Face P lanes 8–15 are routed, and the AC caps for all 16 GFX lanes are fitted.
- **Power:** **cTDP 45 W** in the trashcan core (8600G cTDP 45–65 W [Sourced: AMD]). PPT ≈ 61 W at 45 W cTDP (AMD PPT = 1.35 × TDP) [Inference]. That is inside the LGA1700 CB 12 V allocation, which was based on PL2 65 W.
- **Chipset:** one **PROM21** (19 × 19 FCBGA, ~7 W). **218-0891025** is preferred (X870-marked, lower DOA) over 218-0891018. It sits at the old PCH site (110, 133).
- **VRM:** SVI3 controller with 3 rails: **5 × VDDCR + 2 × VDDCR_SOC + 1 × VDD_MISC = 8 SiC654 + 8 FP4**. Candidate: Renesas **RAA229139** (triple-output SVI3). Alternates are MPS **MP2857** and uPI uP9533P. XDPE192C3B and RAA229621 are dual-rail and would need a separate VDD_MISC loop.
- **Memory:** **4 × DDR5 UDIMM vertical, 2DPC**. Same UMAX 90414 sockets and positions as the LGA1700 CB. 8600G: 2DPC 1R/2R = DDR5-3600 [Sourced: AMD].
- **Lanes:**
  - 8000G GFX **x8 → Face P**
  - GPP **x4 → Face S**
  - GPP **x4 → M.2 boot** (moved from the PCH to the CPU)
  - x4 → PROM21
- **USB:** 8000G has 2 × 10G and PROM21 has 6 × 10G, so the platform has **8 native 10G ports**. The IOB needs 10 (C1–C6, A1–A4), so a **VIA VL822-Q7 4-port 10G hub (U16)** on PROM21 10G #4 feeds A1–A4.
- **Connectors:** **same physicals, positions and signal names** (CPU-LINK J1, IOB-HS J3, M.2 J8, lugs). Only the CB-side sources are re-mapped, documented as a delta against ICD rev 3 (§7). **BP, IOB, faces and cables need no hardware change.** The BP MCU firmware sees one semantic change: the UART0 LPT_SET payload becomes PPT/TDC/EDC.
- **Reused from the LGA1700 CB, identical:**
  - outline and tab, mounting, the 4 core holes 69.5 × 55
  - the core-plate / contact-frame approach (71 × 54 frame, H5–H8 seat screws, insulated steel backplate) — the stock AM5 ILM is not fitted
  - all connector positions
  - 10-layer stackup and rules
- **Checks:**
  - DRC: **0 violations, 0 unconnected, 0 footprint errors** (`--severity-all`).
  - ERC: **0**.
  - Outline mirror check: 0.000 mm².
  - All 57 footprints are in-board.
  - Placeholders are flagged per footprint (`MP62_STATUS` field + `placeholders_flagged.txt`).

## 1. CPU choice and firmware

| Option | Lanes (usable) | USB native | Open firmware | Verdict |
|---|---|---|---|---|
| **Ryzen 5 8600G / 7 8700G** (Phoenix, Zen 4) | PCIe 4.0, 20 / 16: GFX x8 + 2 × GPP x4 + x4 chipset | 2 × USB4, 2 × USB 10G, 1 × USB2 [Sourced: AMD 8600G page] | **Dasharo v0.9.0 boots it** (validated on an 8600G on the MSI PRO B850-P) | **Primary** |
| Ryzen 5 7600 / 9600 (Raphael / Granite Ridge) | PCIe 5.0, 28 / 24 | 4 × 10G + USB2 | none ("will not boot") | Later option: same board; Face P becomes x16 Gen5 |
| Ryzen PRO 8x00GE (35 W) | as 8000G | as 8000G | as 8000G | OEM-only [Unverified availability] |

- **Chain:** PSP boot ROM → PSP blobs (closed) → coreboot + openSIL (`phoenix_poc`) → UEFI payload → OpenCore → macOS. FCH SPI ROM U10 is 32 MB.
- **Port work:**
  - The Dasharo MSI PRO B850-P port is the reference board ("mule").
  - The MP62 CB needs a new coreboot mainboard: GPIO/straps, DXIO lane descriptors for the GFX x8 / GPP x4 / x4 map, the USB port map, the APCB memory config for 2DPC, and SVI3/VRM data.
- **PROM21** carries its own SPI image (U17), extracted from a retail BIOS [Unverified].
- **EC:** the RP2350 EC (U9) stays. It handles AM5 sequencing (RSMRST_L, PWR_BTN_L, SLP_S5_L/SLP_S3_L, PWR_GOOD, VR enable) and the same CPU-LINK sideband.

## 2. Power (45 W core)

| Item | LGA1700 CB (i5-14500T) | AM5 CB (8600G/8700G @ cTDP 45 W) | Note |
|---|---|---|---|
| CPU sustained / short | PL1 35 / PL2 65 W | PPT ≈ 61 W sustained (no PL2 boost window on AM5) [Inference] | without cTDP: PPT 88 W → **must** apply cTDP in firmware |
| Chipset | Z790 ~6 W [Unverified] | PROM21 ~7 W | +1 W |
| VDDCR current | 120–160 A IccMax | TDC/EDC for 45 W ≈ 55 / 100 A [Estimate]; 65 W parts 75 / 150 A [Sourced: cost study, 7600-class] | 5 × 50 A stages = 250 A capability |
| CB 12 V input | ≈ 10–13 A peak | ≈ 9–11 A peak [Estimate] (VRM 70 W + PROM21 + DDR5 PMICs + hub + aux) | U11 TPS259851 ILIM ~25 A unchanged |

- **Thermals:** 45 W is the same class as the T-series PL2 window. The core plate and fan curve are unchanged. Re-check with M-AM5-1 (Z stack) and the IHS area (40 × 40 vs LGA1700 37.5 × 45).
- **LPT (live power target, arch spec §5.5):**
  - On Intel, the actuator was PL1/PL2/PL4 via the EC.
  - On AM5 it becomes **PPT/TDC/EDC through the SMU**. This needs an openSIL/coreboot SMM or EC-mailbox path [Unverified]. It is **open item A-9**.
  - **Fallback:** fixed cTDP 45 W in firmware, plus the fast hardware cap via **PROCHOT_L** (CPU-LINK CARRIER_HOT#, unchanged).

## 3. Chipset: PROM21

- **Part:**
  - **218-0891025** (preferred) or 218-0891018 [Sourced: cost study §10.2].
  - No franchised channel; AMD MOQ is 1,000 units. Broker or recycled parts at $15–50 [Estimate]. X-ray and spares mandatory.
- **Capability:**
  - B850-class single chip: **6 × USB 10G, 1 × USB 20G, 1 × USB 5G, SATA up to 4** [Sourced: AMD AM5 chipset table].
  - PCIe 4.0 downstream: 8 lanes as 2 × x4, plus 4 × Gen3/SATA flex lanes [Sourced: cost study].
  - Uplink PCIe 4.0 x4.
- **Allocation:**

| PROM21 resource | Use | Connector |
|---|---|---|
| uplink x4 Gen4 | CPU GPP x4 | – |
| USB 10G #0–3 | IOB USB-C C3–C6 | J3 |
| USB 10G #4 | U16 VL822 hub upstream → IOB USB-A A1–A4 | J3 |
| USB 10G #5, USB 20G, USB 5G | spare | – |
| USB2 ports | CPU-LINK USB2_MCU / FACEP / FACES; J3 HS1 (IOB hub H1a) | J1, J3 |
| PCIe x1 | IOB i226 #1 | J3 k10 |
| PCIe x1 | IOB ASM1182e (i226 #2 + AirPort) | J3 k14 |
| PCIe x4 | reserved AQC107 (needs a second cable, as LGA1700) | – |
| SATA (flex lane) | SATA0 → BP J7 OpenCore SSD | J1 |
| REFCLK / CLKREQ / PERST for its downstream ports | i226 #1, ASM1182e | J3 [Unverified that PROM21 sources them; fallback = CPU GPP_CLK + buffer] |

- **Not public (AMD NDA):** ballout, pitch, rails, strapping and thermal pad. U2 is a 19 × 19 outline with **484 synthetic balls at 0.8**, flagged PLACEHOLDER-NDA. Its back decoupling field is 100–120 × 123–143.

## 4. CPU VRM and other rails

### 4.1 SVI3 VRM [Proposal]

| Rail | Phases | Parts | Placement |
|---|---|---|---|
| VDDCR (cores) | 5 | Q1–Q5 SiC654 + L1–L5 FP4-150-R | left column x 11.15 / 24.5, y 42–78 |
| VDDCR_SOC | 2 | Q6–Q7 + L6–L7 | y 87–96 |
| VDD_MISC | 1 | Q8 + L8 | y 105 |
| Controller | – | U3 **RAA229139** (X+Y+Z ≤ 8, Rail1 ≤ 3, Rail2 ≤ 2, SVI3 Type II on Rail 2) / MP2857 / uP9533P | (14, 117) |

- **Layout:**
  - CIN1/COUT1 are extended to 5 × 75 (y 36–111).
  - The back via corridor between the J7/J6 pad rows is extended to 8 stages.
- **Same parts as LGA1700:** the SiC654 / FP4 parts and the column are unchanged; the 8th stage replaces VCCGT + VCCIN_AUX.
- **NDA dependencies:** load line, phase counts per SKU, telemetry gain and the SVI3 address map come from the AMD AM5 VR design guide (NDA). The controller config tools are NDA too, as with the RT3628AE.

### 4.2 Other rails (right column) [Proposal; rail list Unverified]

| Ref | Area | Content |
|---|---|---|
| U4 | 28 × 22 | CPU always-on / S5 rails: VDD_18_S5, VDD_33_S5, VDD_MISC_S5 (USB PHY), VDD_18 / VDD_33 S0 switches |
| U5 | 28 × 14 | SVI3 pull-ups, PWROK/RSMRST logic, FCH straps, clock area |
| U6 | 28 × 18 | PROM21 rails (core ≈ 0.9–1.0 V ≈ 6 A, 1.8 V, 3.3 V, PHY) [Estimate] |
| U7 | 14 × 8 | 12 → 5 V VIN_BULK for the 4 UDIMM PMICs (unchanged) |
| U8 | 14 × 8 | VDDIO_MEM_S3 1.1 V (DDR5 PHY) 4–6 A [Estimate] |

## 5. Memory

- **Sockets:** 4 × UMAX 90414 short-latch vertical DDR5 UDIMM on the back at the stock centrelines x 6.5 / 15.8 / 140.55 / 149.85, y centre 95.6. These are the LGA1700 fl2 positions. Daisy chain CPU → near (J6 / J9) → far (J7 / J10); populate far first.
- **Speeds and capacity:**
  - AM5 (8600G): **2DPC 1R/2R = DDR5-3600**, 1DPC = DDR5-5200 [Sourced: AMD 8600G page, Kingston population rules].
  - Up to 4 × 48 GB = 192 GB [Inference].
- **Routing and height:**
  - The DDR5 layout guide is AMD NDA. Routing intent: CH-A to the left pair, CH-B to the right pair, striplines on L3/L8.
  - The socket orientation that puts the DDR land field toward +y is **assumed** (A-2).
  - DIMM height gate is unchanged: M-CC15 (top ≤ 33.25 mm off the back).

## 6. Lane, USB and display plan

| Source | Lanes | Consumer | Connector | REFCLK | PERST# |
|---|---|---|---|---|---|
| CPU GFX (8000G) | **x8 Gen4** (lanes 0–7) | Face P | J1 FP lanes 0–7 → BP J9 | CPU GPP_CLK (FCH) | BP: PLTRST# ∧ FACE_P_RDY |
| CPU GFX lanes 8–15 | x8 (unused on 8000G) | Face P (7000/9000: x16 Gen5) | J1 FP lanes 8–15 | same | same |
| CPU GPP | x4 Gen4 | Face S | J1 FS lanes → BP J10 | CPU GPP_CLK | BP |
| CPU GPP | x4 Gen4 | M.2 boot J8 | CB | CPU GPP_CLK | CB PCIE_RST_L |
| CPU | x4 Gen4 | PROM21 uplink | CB | CPU GPP_CLK | CB |
| CPU USB 10G #0/#1 | 2 | IOB USB-C C1/C2 | J3 k0/k1 | – | – |
| CPU USB4 #0/#1 | 2 | **unused in rev A** (option: run at 10G instead of the hub; firmware risk) | – | – | – |
| CPU USB2 | 1 | CPU-LINK USB2_SPARE → BP → IOB hub H2 | J1 | – | – |
| PROM21 USB 10G #0–3 | 4 | IOB USB-C C3–C6 | J3 k2–k5 | – | – |
| U16 VL822 DS1–4 (up = PROM21 10G #4) | 4 (share 10 Gb/s) | IOB USB-A A1–A4 | J3 k6–k9 | – | – |
| PROM21 PCIe x1 / x1 | 2 | i226 #1 / ASM1182e | J3 k10 / k14 | PROM21 [Unverified] | PROM21 or buffered PCIE_RST_L |
| APU DP0 (4 lanes) + AUX | 4 + AUX | IOB DDI-B path (C5) | J3 k11/k12 + AUX | – | – |
| APU DP1 (2 lanes) + AUX | 2 + AUX | IOB DDI-C path (C6) | J3 k13 + AUX | – | – |

- **No double-booking:** every CPU and PROM21 lane appears once.
- **U-12 on AM5:** the CPU (FCH) generates the GPP refclks, so the "PCH SRC assignment" question is **closed on AM5**. The exact GPP_CLK indices are TBD with the AMD pin list.
- **The hub is the cheapest way to reach 10 ports.** It costs one QFN-76 plus a 25 MHz crystal and SPI flash; the alternative is a second PROM21 (X670-style, +$30–100 [Estimate], +7 W).
  - **Trade-off:** A1–A4 share one 10 Gb/s uplink. With 7000/9000 (4 native 10G), C1/C2 could move to the CPU and the hub could be bypassed (resistor-option study, open A-7).
- **Display:** the 8000G supports up to 4 displays, DP 2.1 [Sourced: AMD]. Two APU outputs replace Intel DDI-B/C on the same J3 pins. HPD level/5 V tolerance and AUX AC coupling are TBD with the AMD datasheet (A-8). With 7000/9000 (2-CU iGPU) the display count is [Unverified].

## 7. Connector pinout delta vs the ICD (rev 3)

- **Physicals, positions and signal names are unchanged** for I-1 CPU-LINK (224) and I-2 IOB-HS1 (MCIO 124). The BP, the IOB and their CSVs stay valid. Only the CB-side source of each net changes.
- **Full per-contact tables:**
  - `kicad/macpro62-am5/docs/cpulink_224_pinout_am5.csv` (columns cb_net_lga1700 / cb_net_am5 / delta_vs_ICD)
  - `kicad/macpro62-am5/docs/mp62-cb-j3_mcio124_host-end_am5.csv`
  - counts in `pinout_delta_summary.txt`

### 7.1 I-1 CPU-LINK (224 contacts): 115 SAME, 60 REMAP, 32 REMAP (8000G unused), 4 REMAP (closes U-12), 9 REMAP (name), 3 REMAP (source), 1 new semantics

| Signals (ICD name) | Contacts | LGA1700 source | AM5 source |
|---|---|---|---|
| FP_PET/PER lanes 0–7 | 32 | CPU PEG x16 | CPU GFX x8 Gen4 (8000G) → Face P |
| FP_PET/PER lanes 8–15 | 32 | CPU PEG x16 | routed, **not driven by 8000G**; live with 7000/9000 x16 Gen5 |
| FS_PET/PER lanes 0–3 | 16 | CPU PCIe x4 | CPU GPP x4 Gen4 |
| FP_REFCLK, FS_REFCLK | 4 | PCH CLKOUT SRCn (U-12) | CPU (FCH) GPP_CLK → **U-12 closed on AM5** |
| SATA0 TX/RX | 4 | PCH SATA | PROM21 SATA (flex lane TBD) |
| USB2_MCU, USB2_FACEP, USB2_FACES | 6 | PCH USB2 | PROM21 USB2 |
| USB2_SPARE | 2 | PCH USB2 | CPU native USB2 |
| PWRBTN#, RSTBTN#, SUS_S3#, SUS_S4_S5#, RSMRST_OUT#, PLTRST#, THERMTRIP#, CARRIER_HOT#, WAKE0# | 9 | Intel PCH names | FCH PWR_BTN_L / SYS_RESET_L / SLP_S3_L / SLP_S5_L (no SLP_S4) / RSMRST_L / PCIE_RST_L / THERMTRIP_L / PROCHOT_L / WAKE_L (via the EC or buffers) |
| SMB_CLK, SMB_DAT, SMB_ALERT# | 3 | PCH SMBus | FCH SMBus0 (0R DNP isolation kept, O-4) |
| UART0_TX/RX | (same pin) | EC ↔ BP MCU, LPT_SET = PL1/PL2/PL4 | same pins; **LPT_SET payload = PPT/TDC/EDC** (BP MCU firmware delta) |

### 7.2 I-2 IOB-HS1 J3 (124 contacts): 46 SAME, 61 REMAP, 16 REMAP (new hub), 1 REMAP (sink)

| Signals (ICD name) | Contacts | LGA1700 source | AM5 source |
|---|---|---|---|
| USB3_C1, USB3_C2 SSTX/SSRX | 8 | PCH USB3 ports 1/2 | CPU native USB 10G #0/#1 |
| USB3_C3…C6 SSTX/SSRX | 16 | PCH USB3 ports 3–6 | PROM21 USB 10G #0–3 |
| USB3_A1…A4 SSTX/SSRX | 16 | PCH USB3 ports 7–10 | **U16 VL822-Q7 DS1–4** (upstream PROM21 10G #4; shared 10 Gb/s) |
| PCIE_I226 TX/RX, I226_REFCLK±, I226_CLKREQ#, I226_PERST# | 8 | PCH RP3 / SRC12 | PROM21 PCIe x1 + its downstream clock/reset [Unverified] |
| PCIE_I226B TX/RX, I226B_REFCLK±, I226B_CLKREQ# | 7 | PCH RP4 / SRC11 | PROM21 PCIe x1 (→ ASM1182e) |
| I226_WAKE# | 1 | PCH WAKE# | FCH WAKE_L |
| DDIB ML0–3 + AUX, HPD_B | 11 | CPU DDI-B | APU DP0 (4-lane) + AUX + HPD |
| DDIC ML0–1 + AUX, HPD_C | 7 | CPU DDI-C | APU DP1 (2 lanes) + AUX + HPD |
| USB2_HS1 D± | 2 | PCH USB2 | PROM21 USB2 |
| USB_OC# | 1 | PCH OC0# | PROM21 USB_OC0_L |
| VBAT_RTC | 1 | PCH RTC well | CPU (FCH) RTC well, diode-OR with 3V3_S5 (sink) |

- **ICD action:** none for rev A. A pointer note was added (ICD §19). If Aidan adopts AM5, these tables become the ICD CB-side source columns.

## 8. Mechanics: socket, retention, Z stack

- **Socket:**
  - Socket AM5 = **LGA1718**, contacts at **0.81 (X) × 0.94 (Y)** in a hexagonal field, 1.4 A/contact, SMT solder balls [Sourced: Lotes socket brochure E1 230131]. Package 40 × 40 [Sourced].
  - Candidates: Foxconn PE17181-11AJ0-1H / PE17186-11ZZ0-1H, Lotes AZIFS055. Not on LCSC; consign them and buy spares.
- **Footprint U1 (PLACEHOLDER-NDA):**
  - 1718 synthetic lands on the sourced pitch: ±17.8 × ±18.8 field, central void, corners trimmed. Positions are in `docs/u1_am5_lands_PLACEHOLDER.csv`.
  - Pad Ø0.50 and housing 46 × 46 are [Estimate].
  - The stock AM5 cooler pattern 54 × 90 is drawn on Dwgs only and is **not drilled**.
  - **Replace with the vendor/AMD footprint before any routing.**
- **Position:** the measured pedestal (78.41, 73.25), as LGA1700.
- **Orientation (A-2):** DDR edge toward +y (DIMMs left/right), PCIe toward −y (J1), USB/DP left, SVI3/FCH right. This is [Inference]; the AMD land map decides.
- **Retention (approach reused):**
  - The **MP62 contact frame 71 × 54 × ≤ 6.0 (7075)** keeps its 4 ears on the fixed 69.5 × 55 core holes and the **H5–H8 seat screws** into PEM nuts in the insulated steel backplate (81.5 × 67, same zone).
  - The frame window changes to **~36 × 36** to bear on the AM5 IHS flange, as AMD's ILM does [Estimate].
  - The stock Lotes AZIF0002 ILM (6-32 screws at 10.3 kgf·cm) and AHSK0001 backplate are not used; they are unlikely to fit the core-plate Z stack.
  - **Open:** the AM5 socket static load and the IHS flange geometry (AMD mechanical guide, NDA) (A-3).
  - The H5 hole edge is ≈ 3.3 mm from the estimated housing; re-check with the drawing.
- **Z stack (M-AM5-1):** seated AM5 IHS top above the PCB vs the pedestal gap. LGA1700 was planned at IHS Z 6.53–7.53. The board floats on springs, so ±1 mm can be absorbed; the frame thickness/shim is set from M-AM5-1.
- **Unchanged:**
  - front height limit 6.0 mm (5.5 rec.) under the plate
  - lugs, the GPU bus-bar pass-through and DIMM heights (M-CC15)

## 9. Stackup proposal

Same as the LGA1700 CB (JLC 10L 1.6 mm, ENIG + hard-gold fingers, POFV via-in-pad):

| Layer | Use |
|---|---|
| L1 | signal (front: socket, VRM, PROM21, hub) |
| L2 | GND |
| L3 | stripline: DDR5 CH-A/CH-B, PCIe |
| L4 | GND |
| L5 / L6 | power: 12 V (≥ 20 mm down the left edge), VDDCR/SOC/MISC pours |
| L7 | GND |
| L8 | stripline: DDR5, PROM21 uplink, USB 10G |
| L9 | GND |
| L10 | signal (back: DIMMs, J3, M.2) |

- **Net classes (start values):** PCIE_85R, DDR5_40R_SE (80 Ω diff DQS/CK), USB_DDI_90R (USB 10G/SATA 90 Ω, DP 85–100 Ω), PWR_12V. Dielectrics are placeholders summing to 1.6 mm; take the JLC 10L table.
- **Why still 10L:** retail B650/B850 boards are 6–8L. PROM21 is coarser than the 0.5 mm Z790 PCH, but the socket field plus 2DPC escape is unchanged. **10L for rev A, 8L is a rev-B study** (cost study §10.2: −$300).

## 10. Floorplan fp0 (KiCad `/workspace/kicad/macpro62-am5/`)

Frame: x 0–156, y up from the board bottom; FRONT = socket/core side. Full coordinates are in `fitcheck_floorplan.txt`; flags are in `placeholders_flagged.txt`.

| Ref | Side | Position / extent | Status |
|---|---|---|---|
| U1 Socket AM5 | F | (78.41, 73.25), courtyard 46.5² | PLACEHOLDER-NDA |
| H1–H4 core holes | F | 43.25 / 112.75 × 46 / 101 | FIXED (measured) |
| H5–H8 seat screws | F | CX ± 28, CY ± 21 | reused |
| Q1–Q8 / L1–L8 | F | x 11.15 / 24.5, y 42 + 9k | sourced dims |
| CIN1 / COUT1 | F | x 5.5 / 33.5, y 36–111 | area |
| U3 SVI3 ctrl | F | (14, 117) | area |
| U4 / U5 / U6 / U7 | F | (134, 45) / (134, 66) / (134, 86) / (127, 104) | area |
| U8 VDDIO_MEM | F | (62, 110) | area |
| U2 PROM21 | F | (110, 133), 19 × 19 | PLACEHOLDER-NDA |
| U16 VL822 hub | F | (90, 154) | area (new) |
| U17 PROM21 SPI | F | (126, 150) | area (new) |
| Y1, U9, U10, J4, J5, U11, U15 | F | as LGA1700 | area |
| LUG1 / LUG2 | F | (27.95 / 40.75, 159.8) | placeholder |
| J1 fingers, CAC1 | F | tab x 38.06–117.95; (80, 19) | sourced / area |
| J6 / J7 / J9 / J10 DIMMs | B | x 15.8 / 6.5 / 140.55 / 149.85, y 95.6 | sourced dims |
| J8 M.2, J3 MCIO, BT1, CB1, CB2, U14 | B | as LGA1700 | placeholder / area |

- **Keep-outs (as LGA1700):** core-boss D12 (no tracks/vias), backplate zone (B, no footprints), GPU bus-bar pass-through (all layers), tab y < 6 (no vias/pour).
- **Previews:**
  - `floorplan.png` (board)
  - `floorplan_notes.png` (with the User.1 legend)
  - `socket_detail.png` (crop)
  - `schematic_root.png` and `schematic_blockdiagram.pdf` (11 pages)

### 10.1 Block schematic bd0

Root sheet + 10 stub sheets (hierarchical labels + non-BOM #BLK stub symbol, same generator pattern as the BP). Nets are block-level bundles: 90 nets, each on ≥ 2 sheets. ERC 0.

The sheets:
1. CPU AM5
2. SVI3 VRM
3. DDR5 2DPC
4. PROM21
5. USB 10G hub
6. Platform power
7. EC / firmware / clocks / RTC
8. CPU-LINK J1
9. IOB-HS J3
10. Boot M.2 J8

AMD pin names are NDA, so functional names are used.

### 10.2 DRC

`kicad-cli pcb drc --severity-all`: **0 violations, 0 unconnected pads, 0 footprint errors** (2026-10-04 ≈ 12:26 ET). DRC is clean because there are no nets. It proves placement and courtyards only.

**Placeholders flagged:**

| Count | Flag | Parts |
|---|---|---|
| 2 | PLACEHOLDER-NDA | U1, U2 (synthetic pads) |
| 3 | PLACEHOLDER | LUG1/2, J8 |
| 23 | AREA | – |
| 20 | sourced outer dims, pads approximate | SiC654, FP4, DIMM |
| 4 | fixed | core holes |
| 4 | reused | seat screws |
| 1 | sourced | J1 fingers |

## 11. Cost

See `macpro62-cost-estimate.md` §10:
- CB delta vs LGA1700, 10L: **−$170 to +$170 (qty 1)**.
- Delivered: **≈ −$220 to +$240**, within ±5 % of the grand total.

This draft adds two lines to the VRM estimate (8 instead of 7 stages, ≈ +$3–5) and the **VL822-Q7 hub** (LCSC C42419379, ≈ $2–4 + crystal/flash [Estimate]). Both are still inside the §10 band.

## 12. Risks

| # | Risk | Mitigation |
|---|---|---|
| R-A1 | **AMD NDA**: no land map, socket footprint, PROM21 ballout, VR or DDR guide → cannot route | Get AMD/ODM docs under NDA, or derive from a retail board + vendor socket drawing (Foxconn/Lotes); do not fab fp0 |
| R-A2 | Firmware: Dasharo supports only 8000G and one reference board; porting to MP62 is real coreboot work | Use the MSI PRO B850-P Dasharo mule first; keep the LGA1700 CB as the parallel primary |
| R-A3 | PROM21 recycled parts / DOA | 218-0891025, X-ray, spares (cost study) |
| R-A4 | USB: A1–A4 share 10 Gb/s through the hub | Acceptable for USB-A; USB4-at-10G option or 7000/9000 later |
| R-A5 | LPT actuator via SMU not available in open firmware | Fixed cTDP 45 W + PROCHOT fallback |
| R-A6 | Z stack / IHS flange differ from LGA1700 → frame redesign | M-AM5-1 before CNC; frame window and thickness are parameters |
| R-A7 | 8000G caps Face P at x8 Gen4 | Navi 23 is natively x8 → no loss today; 7000/9000 restore x16 |

## 13. Open items

| ID | Item | Needed for |
|---|---|---|
| A-1 | **AMD AM5 land map / socket footprint (NDA)** + vendor socket drawing (PE17181 / AZIFS055): replace U1 | any routing |
| A-2 | Socket orientation on the board (DDR edge +y assumed) | DDR/PCIe escape |
| A-3 | AM5 socket load spec + IHS flange geometry → contact-frame window and load; seat-screw clearance | frame CNC |
| A-4 | **M-AM5-1**: seated IHS Z vs pedestal (stock retail AM5 board + 8600G) | frame / springs |
| A-5 | **PROM21**: ballout, pitch, rails, strapping, SPI image, refclk/PERST for downstream ports, thermal pad | U2, U6, U17 |
| A-6 | SVI3 controller choice (RAA229139 vs MP2857 vs uP9533P), availability, config tools (NDA), phase map 5/2/1 | VRM |
| A-7 | USB: hub (VL822 vs GL3590) vs USB4-at-10G vs bypass for 7000/9000; PROM21 USB port numbering | J3 map |
| A-8 | Display: APU DP pin mapping, HPD input level (IOB drives 3.3 V), AUX coupling, DP1 lane count | J3 k11–k15 |
| A-9 | LPT on AM5: PPT/TDC/EDC runtime path (openSIL/SMU mailbox) vs fixed cTDP; BP MCU UART0 payload | arch spec §5.5 |
| A-10 | Dasharo port to the MP62 CB (mainboard dir, DXIO map, APCB 2DPC, GPIO) | bring-up |
| A-11 | AM5 aux rail list and currents (VDD_18_S5, VDD_33_S5, VDD_MISC_S5, VDDIO_MEM_S3, …) | U4, U8 |
| A-12 | GPP_CLK indices for FP / FS / M.2 / PROM21; 48 MHz crystal vs clock input [Unverified] | clocks |
| A-13 | 2DPC DDR5 topology rules (AMD DDR guide, NDA); SPD/SMBus0 isolation (O-4) still valid | DDR routing |
| A-14 | M-CC15 DIMM height (unchanged from LGA1700) | back side |
| A-15 | 8L feasibility (rev B) | cost |
| A-16 | THERMTRIP / PROCHOT wiring with PROM21 (PROM21 thermal trip output?) | sideband |

## 14. Decisions for Aidan

| # | Decision | Recommendation |
|---|---|---|
| D-A1 | Keep AM5 as a parallel draft, or switch the primary CB from LGA1700 to AM5 | **Parallel draft** until A-1/A-5 docs (NDA) and a Dasharo mule boot are in hand |
| D-A2 | USB 10G #9/#10: VL822 hub (fp0) vs USB4 ports at 10G vs a second PROM21 | Hub (cheapest, lowest firmware risk) |
| D-A3 | Fixed cTDP 45 W vs runtime PPT control for LPT | Fixed 45 W + PROCHOT for rev A |
| D-A4 | 10L (fp0) vs 8L | 10L for rev A |

## 15. Sources

- AMD Ryzen 5 8600G product page (65 W, cTDP 45–65 W, PCIe 4.0 20/16 lanes, 2 × USB4 + 2 × USB 10G + USB2, 4 × DDR5-3600 / 2 × 5200, DP 2.1, 4 displays): https://www.amd.com/en/products/processors/desktops/ryzen/8000-series/amd-ryzen-5-8600g.html (fetched 2026-10-04)
- AMD AM5 chipset table (B850 single PROM21: 6 × 10G, 1 × 20G, 1 × 5G, SATA 4): https://www.amd.com/en/products/processors/chipsets/am5.html
- Lotes socket brochure E1 230131 (Socket AM5 LGA1718, pitch 0.81 × 0.94, 1718 contacts, AZIF0002 ILM 6-32 10.3 kgf·cm, AHSK0001 BP): https://kaztech.jp/wp-content/uploads/2024/05/Lotes-socket-introduction_E1_230131-1.pdf
- Renesas RAA229139 (triple-output SVI3 controller, short-form datasheet); MPS MP2857; uPI uP9533P; Infineon XDPE192C3B (dual-rail): see cost study §10.6 and Renesas/MPS/Infineon product pages
- VIA Labs VL822-Q7 (USB 3.2 Gen2 4-port hub, QFN-76 9 × 9): LCSC C42419379; Genesys GL3590: LCSC C22375753
- Dasharo v0.9.0 MSI PRO B850-P WIFI (8000G only), PROM21 sourcing/part numbers, socket part numbers: `macpro62-cost-estimate.md` §10.3/§10.6
- Kingston DDR5 population rules (AMD 2DPC speeds): https://www.kingston.com/en/memory/memory-population-rules
- LGA1700 CB geometry, outline and placements: `kicad/macpro62-lga1700/tools/build_pcb.py` (read only)
