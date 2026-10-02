# MacPro6,2: Interface Control Document (ICD), rev 2

| Item | Value |
|---|---|
| Date | 2026-10-02, rev 1 ≈ 12:30 ET; **rev 2 ≈ 13:15 ET** (Aidan's decisions: 445 W ceiling + live power target, face normals ≈ 45°, CR-2 by jog cable, O-3/O-4/O-5 approved; port modules PMI-50) |
| Owner | Aidan Winkler (MacPro6,2 project) |
| Scope | Every inter-board interface: CB (LGA1700/Z790 CPU board), BP (base board / backplane, Ø122), IOB (I/O board rev A0 + risers), face modules (MP62-FACE v0.1, template, SM-1 storage face) |
| Masters | Architecture spec `macpro62-architecture-spec-v0.2.md` (changes 30–32; §5.5 LPT), face spec `macpro62-face-module-spec-v0.1.md` update 4 (supersedes arch §7), CB plan fl2.3, IOB plan (incl. §4.7.9 port modules), SM-1 plan, `kicad/macpro62-io-modules/README.md` |
| Tags | [Sourced], [Estimate], [Inference], [Unverified], [Proposal], TBD — as in the spec |

**Conventions**

- **"Host end" / "module end" / "IOB end":** all MCIO cables are straight-plug ↔ straight-plug SFF-TA-1016 cables that **cross the rows** (P1 B-n ↔ P2 A-n, SFF-9402). The two ends of one link therefore use the same contact numbers with **rows A and B exchanged**. Every pinout file says which end it describes.
- **Direction** is given as source → sink. "OD" = open drain; the pull-up side is named.
- **Coordinates:** BP = disc frame, origin = midpoint of the gold holes, +y = core/GPU side (BP KiCad). CB = board frame, x right, y up from the bottom edge, front = CPU side. IOB = board frame (Xb, Y). Module = face frame (X 0–104, Y up from the bottom edge, core view).
- Status column: **OK** = both ends agree (checked net by net or line by line); **FIXED** = mismatch found in this audit and corrected; **OPEN** = needs a decision or a measurement (§16).

---

## 1. Interface map

| # | Interface | End A (part, gender) | End B (part, gender) | Medium | Pinout of record |
|---|---|---|---|---|---|
| I-1 | CPU-LINK | CB J1: card-edge fingers 224 (male tab, 79.89 × 1.57) | BP J1: Amphenol Mini Cool Edge 224 ME1022410103011, vertical SMT (female) | direct mate | `kicad/macpro62-backplane/docs/cpulink_224_pinout_draft.csv` (+ `cb_net` column) — identical copy in `kicad/macpro62-lga1700/docs/` |
| I-2 | IOB-HS1 | CB J3: MCIO 124 RA receptacle (back side) | IOB J1: MCIO 124 RA receptacle (`MP62_MCIO_124P_RA_SFF-TA-1016`) | MCIO 124 cable, plug–plug, crossed | IOB end `kicad/macpro62-io-board/docs/mp62-iob-hs1_mcio124_pinout_v0.2.csv`; CB end `kicad/macpro62-lga1700/docs/mp62-cb-j3_mcio124_host-end.csv` |
| I-3 | DISPLAY-LINK | Face P J_DISP (template J2): MCIO 74 RA receptacle, module X 82 | IOB J2: MCIO 74 RA receptacle | MCIO 74 cable, plug–plug, crossed | module end `macpro62-face/pinouts/mp62-face-v0.1_mcio74_displaylink_module-end.csv`; IOB end `kicad/macpro62-io-board/docs/mp62-iob-j2_mcio74_displaylink_iob-end.csv` |
| I-4 | BP → Face P / Face S PCIe | BP J9 / J10: MCIO 124 RA receptacles (`MP62_MCIO_124P_RA_SFF-TA-1016`) | Module J_PCIE (template J1): MCIO 124 RA receptacle, module X 43.5 | MCIO 124 cable, plug–plug, crossed | module end `macpro62-face/pinouts/mp62-face-v0.1_mcio124_pcie_module-end.csv`; BP end = same, rows swapped |
| I-5 | Face AUX ×2 | BP J3 / J4: JST GH 15P **BM15B-GHS-TBT** vertical | Module J_AUX (template J3): JST GH 15P **SM15B-GHS-TB** RA, module X 16.5 | GH 15P cable, GHR-15V-S both ends, 1:1 | `macpro62-face/pinouts/mp62-face-v0.1_aux_gh15.csv` |
| I-6 | IOB-LINK | BP J6: JST GH 15P BM15B-GHS-TBT vertical | IOB J6: JST GH 15P BM15B-GHS-TBT vertical | GH 15P cable, 1:1 | IOB plan §5.5 (table §7 here) |
| I-7 | PSU → IOB | PSU DC-out 12P + PSU data 6P (stock cables, female) | IOB J3 12P (stock CONN_B) + J4 6P (stock CONN_A) headers | stock cables | provisional (§8) |
| I-8 | IOB → BP PSU pass-through | IOB J5: Micro-Fit 3.0 43045-0812 2×4 vertical | BP J2: Micro-Fit 3.0 43045-0812 2×4 vertical | Micro-Fit 2×4 harness (43025-0800 housings), 1:1 | §8 |
| I-9 | 12 V bus bars / lugs | PSU terminal pairs (stock bus bars, T8 923-0716) | CB LUG1/LUG2; Face J20/J21 (site A) or J22/J23 (site B) | bus bar / lug | §9 |
| I-10 | Fan + AirPort | stock fan-assembly ribbon / interposer | IOB J7 CONN_C 2×20 0.5 (DF12-40DS-0.5V(86) candidate) + J8 U.FL | stock ribbon | IOB plan §4.7.7, M-IOC1 |
| I-11 | I/O wall flex | stock 821-2222 flex, 14 fingers 0.5 | IOB J31 HX FPC 0.5-14P (C7502869), double-sided contacts | stock flex | IOB plan §5.6, jumper matrix |
| I-12 | **PMI-50 port modules** (internal to the IOB) | IOB JM1–JM11: Hirose **DF40C-50DS** receptacle, F side | module paddle: **DF40C-50DP** header (faces down), on the FPC of MOD-C / MOD-A / MOD-H | direct mate (board-to-board) | `kicad/macpro62-io-modules/README.md` (PMI-50 table), IOB plan §4.7.9; §10.1 here |

---

## 2. I-1 CPU-LINK (CB ↔ BP)

**Mechanical:** CB tab 79.89 ± 0.10 × 1.57, hard-gold bevelled fingers, footprint `MP62_CPULINK_MiniCoolEdge224_CardEdge_Fingers` (same as the archived CC carrier; front F.Cu = side B, back B.Cu = side A). BP J1 at (0, −12.6) rot 180° (fp3a): A row (host TX) faces the PSU side, B row faces the core. Measured stock riser slot −12.5 ± 0.3 from the hole axis (base-board scan) → no move. **Status OK** (fp3a cross-check; CB uses the same tab geometry at x 78).

| Group | Pins (CSV) | CB net (cb_net) | Dir | BP net | Status |
|---|---|---|---|---|---|
| Face P PCIe x16 | A/B 2–56 (FP_PET/PER15…0) | CPU PEG lanes, TX AC caps on the CB | CB ↔ BP | → J9 (redriver sites U10–U13 in G5) | OK |
| Face S PCIe x4 | A/B 57–… (FS_PET/PER0…3) | CPU PCIe x4, TX AC caps on the CB | CB ↔ BP | → J10 (U14 in G5) | OK |
| FP_REFCLK± / FS_REFCLK± | bay 2 / bay 3 A row | PCH CLKOUT for CPU PEG / CPU x4 (SRCn **TBD**; SRC11/SRC12 are used by the IOB) | CB → BP | → J9/J10 REFCLK0 | OPEN (U-12) |
| SATA0 TX/RX | A73/A74, B70/B71 | PCH SATA0 (HSIO TBD, not shared with M.2 RP9–12) | CB ↔ BP | → J7 M.2 SATA | OPEN (U-13) |
| USB2_MCU | B73/B74 | PCH USB2 port | bi | BP MCU USB FS | OK |
| USB2_FACEP / USB2_FACES | B51/B52, B76/B77 | PCH USB2 ports | bi | → J3 / J4 pins 13/14 | OK (C-3) |
| USB2_SPARE | B79/B80 | PCH USB2 port | bi | → **J6 pins 13/14 → IOB USB2_LINK → hub H2** (USB-A A1–A4 + Bluetooth) | **FIXED** (BP stub had no route) |
| PWRBTN# | A86 | EC GPIO in → PCH PWRBTN# | BP → CB, OD, pull-up BP 3V3_SB | MCU relays IOB PWRBTN_IN_N | OK |
| SUS_S3# / SUS_S4_S5# | A89 / A90 | PCH SLP_S3# / SLP_S4# (buffered) | CB → BP | MCU sequencing | OK (name mapping added) |
| RSMRST_OUT#, PLTRST#, THERMTRIP# | bay 4 A row | EC RSMRST# copy, PCH PLTRST#, CPU/PCH THERMTRIP# (OD) | CB → BP | MCU; PERST#_x = PLTRST# ∧ FACE_x_RDY; THERM_LATCH | OK |
| VIN_PWR_OK, CARRIER_HOT#, WAKE0#, RSTBTN#, BIOS_SEL | bay 4 A row | EC GPIO in; PROCHOT#; PCH WAKE# | BP → CB | MCU; **CARRIER_HOT# = LPT fast cap (≤ 1 ms, §13.2)** | OK |
| **PWR_ALERT#** | **A105** (was RSVD_LS1) | **CB U15 INA228 ALERT ∨ U11 FLT#** (OD) | CB → BP, OD, **10 k pull-up BP 3V3_SB** | MCU IRQ (`MOD_PWR_ALERT_N`) → LPT fast path | **NEW (rev 2)** |
| SMB_CLK/DAT/ALERT# | B-row bay 4 | **PCH SMBus = DIMM SPD/PMIC/TS bus → DNP 0R on the CB** | bi | MOD_SMB (left unconnected by default) | **FIXED**; **approved (Aidan, O-4)** |
| I2C0_CLK/DAT | B90 / B92 | **CB ID EEPROM 0x57** + **CB INA228 U15 0x45** (rev 2) + EC target, 3V3_SB | bi, OD | MCU (MOD_I2C0) | **FIXED**; approved O-4 |
| UART0_TX/RX | bay 4 B row | EC UART; **LPT link** (`LPT_SET` / `LPT_REPORT`, CRC, 10 Hz heartbeat, §13.2) | bi | MCU | OK |
| FAN_PWMOUT / FAN_TACHIN | bay 4 B row | EC fan demand out / regenerated tach in | CB → BP / BP → CB | MCU (PIO); fan itself via IOB EMC2101 | **FIXED** (semantics) |
| 5V_SBY ×6, 3V3_SB ×2 | bay 4 | CB standby inputs | BP → CB | PS1 | OK (budget §13) |
| CC_PRSNT1#/2# | A1 / A112 | GND on short fingers | CB → BP | MCU presence | OK |
| GND ×80, RSVD ×14 | | | | | OK |

---

## 3. I-2 IOB-HS1 (CB J3 ↔ IOB J1)

Connector: MCIO 124 RA receptacle at both ends (Amphenol G97R24332HR / Molex 2173463021 class). CB J3 at CB (78, 160), back side, exits toward the top edge (area placeholder 44 × 12; swap to the SFF footprint at schematic stage). IOB J1 on IOB B side, Xb 13.2–59.8, Y 153–177. Cable length/route: **M9 / U-6**.

| Lane slot (k) | Function | CB source | IOB sink | Status |
|---|---|---|---|---|
| k0–k5 | USB 3.2 Gen2 C1–C6 | PCH HSIO 0–5 (USB3 ports 1–6), TX AC caps on the CB | TUSB1046A U11–U16 | OK |
| k6–k9 | USB 3.2 Gen2 A1–A4 | PCH HSIO 6–9 | TUSB1002A U21–U24 | OK (**needs Z790**) |
| k10 | i226 #1 PCIe x1 | PCH RP3 / HSIO 12 | U50 | OK |
| k11, k12 | DDI-B ML0–3 (AC caps on the CB, 75–200 nF) | CPU DDI-B | C5 TUSB1046A | OK |
| k13 | DDI-C ML0–1 | CPU DDI-C | C6 TUSB1046A | OK |
| k14 | PCIe x1 → ASM1182e U91 (i226 #2 U52 + AirPort J7) | PCH RP4 / HSIO 13 | U91 upstream | OK (ASM1182e internals U-8) |
| k15 | DDI-B AUX (PET) / DDI-C AUX (PER) | CPU DDI AUX | TUSB1046A AUX | OK |

| Sideband (IOB-end contact → CB-end contact) | Signal | Dir | Notes | Status |
|---|---|---|---|---|
| A8 → B8 / A9 → B9 | HPD_B / HPD_C | IOB → CB | 3.3 V from PD #3 GPIO → PCH DDSP_HPD | OK |
| B8 → A8 | I226_CLKREQ# | IOB → CB, OD | → SRCCLKREQ12# | OK |
| B9 → A9 | I226_WAKE# | IOB → CB, OD | wired-OR of both i226; no WoL in rev A (i226 on S0-only 3V3) | OK / note |
| A11 → B11 | I226_PERST# | CB → IOB | PLTRST-derived, shared U50 / U52 / U91 / J7 | OK (U-8: downstream PERST via ASM1182e) |
| B11/B12 → A11/A12 | I226 REFCLK± | CB → IOB | CLKOUT_SRC12 | OK |
| A12, A30 → B12, B30 | IOB_HS_PRSNT0#/1# | IOB → CB | tied to GND on the IOB | OK |
| A26 → B26 | VBAT_RTC | IOB → CB | IOB BT1 → 1 k → BAT54WS; CB diode-OR with 3V3_DSW; **CB BT1 DNP** | **FIXED** (CB BT1 now DNP) |
| A27 → B27 | USB_OC# | IOB → CB, OD | FLT# wire-OR of U25–U28 → PCH OC0#, **pull-up on the CB** | OK |
| B26/B27 → A26/A27 | I226B REFCLK± | CB → IOB | CLKOUT_SRC11 [Proposal] → ASM1182e upstream | OK |
| A29 → B29 | I226B_CLKREQ# | IOB → CB, OD | → SRCCLKREQ11#; held low on the IOB (R143 0R) | OK |
| B29/B30 → A29/A30 | USB2_HS1 D± | bi | PCH USB2 → IOB hub H1a | OK |

**Fixed:** the CB had no host-end table; the generator `kicad/macpro62-lga1700/tools/make_j3_pinout.py` now writes it (rows swapped). CB U13 i226-V removed (both i226 on the IOB); CB plan §0/§1.2/§7.2/§8 updated (no MDI on the cable, no 2:1 DP mux, 10 × USB3, 1 USB2).

---

## 4. I-3 DISPLAY-LINK (Face P J_DISP ↔ IOB J2)

| Link | GPU source (module) | IOB sink | Status |
|---|---|---|---|
| DL0 (4-lane) | GPU DP link 0 | C1 TUSB1046A | OK |
| DL1 (4-lane) | link 1 | C2 | OK |
| DL2 (DP++, AUX = DDC) | link 2 | HDMI via TDP158 U60 | OK |
| DL3 (2-lane) | link 3 | C3 | OK |
| DL4 (2-lane) | link 4 | C4 | OK |
| HPD0–4 | module input (3.3 V) | PD #1 GPIO0/1, TDP158, PD #2 | OK |
| DLINK_PRSNT# | module ties low | PD #2 GPIO2 | OK |

- **FIXED:** IOB J2 used the **module-end** contact numbers directly. With the crossing cable the GPU TX pairs (module row A per §9.3) arrive on IOB row B. `build_sch.py` now builds J2 from the module-end table with rows A/B exchanged and writes `docs/mp62-iob-j2_mcio74_displaylink_iob-end.csv`; ERC 0. Net names unchanged.
- AC coupling on the module (DP source); no DP_PWR / 5 V on the cable (IOB makes them). OK.
- Cable path and length from module X 82 to IOB J2: **M9 / U-6**.

---

## 5. I-4 BP J9 / J10 → Face P / Face S PCIe (MCIO 124)

| Signal (module end, face spec §4) | BP source | Dir | Rev A | Status |
|---|---|---|---|---|
| PET0–15 (Face P) / PET0–3 (Face S) | CPU via CPU-LINK (AC caps on the CB; G5: at redriver outputs) | BP → module | x16 / x4 wired | OK |
| PER… | module TX (caps on the module) | module → BP | | OK (SM-1: caps on module TX row B) |
| REFCLK0± | FP_REFCLK / FS_REFCLK pass-through | BP → module | 100 MHz HCSL, free-running | OK |
| PERST0# | BP: PLTRST# ∧ FACE_x_RDY | BP → module | | OK |
| CLKREQ0# | terminates on the BP (clock always on) | module → BP | SM-1 leaves it undriven (DNP 0R) | OK |
| WAKE0# | ORed on the BP into CPU-LINK WAKE0# | module → BP, OD | | OK |
| MCIO_PRSNT# (set A) | module ties low | module → BP | | OK |
| Set B (REFCLK1, PERST1#, …) | not driven by BP rev A | – | | OK |
| USB2 | **not on the MCIO** (C-3) — on AUX | – | | **FIXED** (arch §7.5 marked superseded) |

**Mechanical (fp5, rev 2; face normals ≈ 45° / 135°, Aidan 2026-10-02):** both BP receptacles use the SFF-TA-1016 RA footprint (pad rows 0.575 / 3.525). Face J_PCIE stays at module X 43.5 → s = +8.5 on both faces (C-2, rotational symmetry; module frame unchanged).

| | s requested (CR-2) | s placed | r_c | rot | Fit (rmax ≤ 58 / G-hole ≥ 6 / S-hole ≥ 3) | Cable jog |
|---|---|---|---|---|---|---|
| J9 Face P | +8.5 | **−5.2** | 31.2 | −45° | 51.8 / 6.2 / 3.8 → OK | **13.7 mm** (by the cable) |
| J10 Face S | +8.5 | **−2.0** | 31.5 | +45° | 50.4 / 13.4 / 5.0 → OK | **10.5 mm** (by the cable) |

- **Why not s = +8.5:** with 90° between the faces, both receptacles at s = +8.5 collide at the apex (J9/J10 apex gap is 1.3 mm at the placed values), J10 is bounded by the G1 hole keep-out, and J4 only fits beyond J10's lower-left end if J10 s ≤ −2. Scan scripts `scratch/icd2/` (scan2, joint, sepmod, ovl). At 45° the GPU board ends sit at (±75.7, 2.1), 14.7 mm in front of the CB plane → **no CB change**.
- **CR-2 CLOSED by the cable (Aidan):** MCIO 124 straight-plug ↔ straight-plug, rows crossed (SFF-9402), **85 Ω flat-ribbon twinax, 34 AWG** (Amphenol AssembleTech MCIO family or equal, custom length), vendor-formed lateral jog 13.7 / 10.5 mm ± 1 mm, inside bend radius **≥ 3 mm per ribbon layer** (vendor: ≥ 2.5 × 0.55–0.60 mm), ≤ 2 static bends, no creases (face spec §3.6).
- **Routing:** BP plug exits radially (along the face normal) → passes under the module bottom edge → 90° up on the outer side → module J_PCIE plug travelling +Y. Plug body 8.2 mm high → **6.8 mm clearance under the 15 mm edge** (M1; 15.3 mm if 23.5, C-16).
- **Space check [Estimate]:** BP mating faces at n ≈ 43.3 / 43.6 mm; with an assumed 15 mm plug the BP plug rear is at n ≈ 58.3–58.6 and the module plug's cable exit at n ≈ 60.7, Y ≈ −0.5. Free cable between plug rears ≈ **12 mm (M1 = 15) to ≈ 20 mm (23.5)**, one 90° bend R ≈ 2.1–2.4 mm. That is **below the 3 mm bend rule and short for a 10–14 mm jog** → **OPEN O-6** (plug length U-19, M1c, vendor sample).
- Lane estimates (BP, CPU-LINK → J9/J10): Face P 39–65 mm, Face S 40–43 mm (`lane_length_estimate.txt`).

---

## 6. I-5 Face AUX (BP J3/J4 ↔ module J_AUX), GH15

| Pin | Signal | Dir | BP side | Module side (SM-1) | Status |
|---|---|---|---|---|---|
| 1, 2 | 3V3_AUX | BP → module | load switch: 3V3_SB (S5 ≤ 15 mA) / 3V3_BP (S0 ≤ 1 A) | EEPROM, sensors | OK |
| 3, 7 | GND | | | | OK |
| 4 | FACE_PRSNT# | module → BP | MCU input, pull-up | tied to GND | OK |
| 5 | FACE_PWR_EN | BP → module, push-pull | MCU | 100 k pull-down, eFuse EN | OK |
| 6 | FACE_PWR_GOOD | module → BP, OD | pull-up to 3V3_AUX on BP | eFuse PG / PG_ALL | OK |
| 8 / 9 | FACE_SMB_CLK / DAT | bi, OD | MCU, 2.2 k pull-ups, isolated until PWR_GOOD | EEPROM 0x50, TMP1075 0x48 / 0x49, **INA228 0x40 (rev 2, SM-1 U13)**; power-target agent 0x58 on modules with an MCU | OK |
| 10 | FACE_SMB_ALERT# | module → BP, OD | MCU (LPT fast path) | eFuse FLT# ∨ **INA228 ALERT** (rev 2) | OK |
| 11 | THERM_ALERT# | bi, OD | MCU; **host drives it low = "cut ≥ 25 % within 100 ms"** (LPT fast cap) | TMP1075 0x48 | OK |
| 12 | THERM_TRIP# | module → BP, OD | THERM_LATCH (PSU off) | TMP1075 0x49 comparator | OK |
| 13 / 14 | USB2 D+ / D− | bi | CPU-LINK USB2_FACEP / USB2_FACES | optional | OK (C-3) |
| 15 | MOD_LED# | module → BP, OD ≤ 5 mA | MCU mirrors it to the face LED | SSD activity wired-OR | **FIXED** (BP had GH14, no pin 15) |

- **FIXED:** BP J3/J4 GH14 (BM14B) → **GH15 BM15B-GHS-TBT**; `face_aux` stub gained FACE_MOD_LED_N. Gender: both ends are GH headers (BP vertical, module RA); the cable carries GHR-15V-S housings. Positions **fp5 (rev 2):** **J3 (0, 51.4) rot 0** in the apex wedge (Face P's J_AUX end); **J4 (−38.0, 2.5) rot 135°** beyond J10's lower-left end, 6.3 mm from G1 (Face S frame n 28.6, s 25.1).
- Cable length: TBD (U-6).

---

## 7. I-6 IOB-LINK (BP J6 ↔ IOB J6), GH15 1:1

| Pin | Signal | Dir | BP side | IOB side | Status |
|---|---|---|---|---|---|
| 1, 2 | 3V3_SB | BP → IOB | PS1 | U80 TLC59116, U81 LIS2DH12, U82 EEPROM, Halls, U83 A side, **U98 INA228** (3V3_BT now on S0: R149 fitted, R148 DNP) | OK (budget §13) |
| 3, 7, 12, 15 | GND | | | | OK |
| 4 | PWRBTN_IN_N | IOB → BP, OD | **pull-up on the BP**, MCU GPIO | J31 P3 ∨ SW1, 100 nF, TVS | OK |
| 5 / 6 | HALL_A_N / HALL_B_N | IOB → BP | HW gate + MCU (pull-ups BP) | U30 / U31 | OK |
| 8 / 9 | I2C_SYS SCL / SDA | bi, OD | MCU master, pull-ups on 3V3_SB | IOB devices (§11) | OK |
| 10 | IOB_INT_N | IOB → BP, OD | **pull-up on the BP** | U84 (PD IRQs), LIS2DH12 INT1, **U98 INA228 ALERT (rev 2)** | **FIXED** (missing in BP stub) |
| 11 | IOB_PRSNT_N | IOB → BP | **BP 10 k pull-up to 3V3_SB**, MCU input | tied to GND | **FIXED** (arch §4.8 / BP treated as GND/not present) |
| 13 / 14 | USB2_LINK D+ / D− | bi | CPU-LINK USB2_SPARE | hub H2 (USB-A A1–A4, Bluetooth via 4th CH334R) | **FIXED** (no BP route before) |

Positions: BP J6 (11.4, −48.8) rot 180 (moved 1.6 mm for S3); IOB J6 B side, Xb 68.4–91.7, Y 8.7–15.3. Cable length TBD (U-6).

---

## 8. I-7 / I-8 PSU chain (PSU → IOB J3/J4 → IOB J5 → BP J2)

| PSU cable pin (provisional) | IOB header | IOB J5 (Micro-Fit) | BP J2 | BP net | Status |
|---|---|---|---|---|---|
| DC 1–6 +12 V | J3 1–6 | 1, 2 (12V_MAIN, ahead of U40) | 1, 2 | 12V_MAIN → PS2 (≈ 1 A) | OK (pinout U-1) |
| DC 7–12 GND | J3 7–12 | 3, 4, 5 | 3, 4, 5 | GND | OK |
| Data 1 11V_SB | J4 1 | 7 | 7 | 11V_SB → PS1 | OK (U-1) |
| Data 2 GND | J4 2 | (GND) | – | | OK |
| Data 3 PS_ON# | J4 3 | 6 | 6 | HW gate output | OK (polarity U-2) |
| Data 4 PWR_OK | J4 4 | 8 | 8 | MCU / VIN_PWR_OK logic | OK (U-2) |
| Data 5 / 6 PSU SMBus? | J4 5 / 6 | – | – | IOB I2C_SYS via **DNP 0R** | OK (U-1) |

- 12 V current through the stock 12P header: IOB ≈ 8–11.7 A + BP ≈ 1 A over 6 pins (≈ 1.5–2 A/pin); pin rating unknown (U-1 / M-CC16).
- Harness IOB J5 → BP J2: Micro-Fit 3.0 2×4, 18 AWG, 1:1. Length TBD (U-6).

---

## 9. I-9 12 V entries and current budgets

| Board | Entry | Protection | Sustained / peak | Rating / note | Status |
|---|---|---|---|---|---|
| CB | LUG1 (27.95, 159.8) / LUG2 (40.75, 159.8), single entry, 2 × 2 PTH per lug | U11 TPS259851, ILIM ≈ 25 A → **RS1 0.5 mΩ / U15 INA228 (rev 2)** | ≈ 12 A / 20 A | plane L5+L6 ≥ 20 mm; which PSU pair feeds the CB: **M-CC16 (U-3)** | OK / OPEN |
| CB right notch | GPU bus-bar pass-through, rule area x 105–135, y 160.5–169.5 | – | – | ≥ 3 mm clearance [Proposal] | OK |
| Face P | J20/J21 (site A) or J22/J23 (site B), Ø3.2 / Ø8.8 | module eFuse (gated by FACE_PWR_EN) | 10.8 A (130 W) / 12.5 A (150 W) | ≥ 15 A per lug; polarity/site per face **M5 (U-4)** | OPEN |
| Face S (SM-1) | same sites, both fitted | **R520 2 mΩ / U13 INA228 (rev 2)** → eFuse ILIM 5 A | ≤ 3.3 A (40 W) | | OK |
| IOB | J3 12P | U40 TPS259824, ILIM ≈ 10 A → **RS90 1 mΩ / U98 INA228 (rev 2)** | ≈ 8–9 A capped / ≈ 11.7 A unmanaged | **unmanaged worst case > ILIM** → D-IO1 pool cap is mandatory; LPT holds it (§13.2) | OK (closed O-2) |
| BP | J2 pins 1–2 | input fuse + TVS | ≈ 1 A (G4) / ≈ 1.5 A (G5) | fan removed from the BP | **FIXED** |
| Fan | IOB +12V_IOB → F90 1.5 A PTC → J7 | PTC | ≤ 0.8 A [Estimate] | stock fan current M-IOC1 | OPEN (U-5) |
| PSU | stock 450 W, 12.1 V 37.2 A; 11 V SB 5 W | | **ceiling 445 W** (rev 2) | | §13 |

---

## 10. I-10 / I-11 IOB to stock flexes (informative)

| Interface | IOB part | Signals | Status |
|---|---|---|---|
| CONN_C (fan + AirPort) | J7 DF12-40 placeholder at the stock spot (50.49, 5.18) B, H14/H15 standoffs, T8 bracket keep-out | fan 12 V / PWM / TACH (U90 EMC2101), AirPort PCIe x1 (U91 downstream 1) + USB2 BT (CH334R U35), PERST#, REFCLK (U-8), antenna J8 U.FL | pinout **M-IOC1 / M-IOC3 (U-5)** |
| I/O wall flex | J31 14P 0.5 at (82.8, 10.0) F | P3 → PWRBTN_IN_N, P6 → GND fitted; others DNP 0R matrix (I2C_SYS, 3V3_SB, IOB_INT_N, 5V_A, 3V3) | pins provisional (§9.5 probing) |

### 10.1 I-12 PMI-50 port-module interface (internal to the IOB) [Proposal, D-IO16]

Each USB-C (C1–C6), USB-A (A1–A4) and HDMI port is a flex-only module (MOD-C / MOD-A / MOD-H, `kicad/macpro62-io-modules/`). The module paddle carries a **Hirose DF40C-50DP** header (facing down) that mates with a **DF40C-50DS** receptacle (JM1–JM11) on the IOB F side. Plug loads go through the bonded sleeve → collar → clamp plate → standoffs, never through the DF40. DF40 is rated for about 30 mating cycles. Swaps are done with the system off.

**Pinout (one standard for all modules; row A = odd pins 2k−1, row B = even pins 2k):**

| k | A | B | k | A | B |
|---|---|---|---|---|---|
| 1–6 | VBUS | VBUS | 18 | CC1 | HPD |
| 7–8 | GND | GND | 19 | CC2 | UTIL |
| 9 | HS0_P | HS2_P | 20 | GND | GND |
| 10 | HS0_N | HS2_N | 21 | ID_SCL | ID_SDA |
| 11 | GND | GND | 22 | 3V3_MOD | PRSNT# |
| 12 | HS1_P | HS3_P | 23 | LED# | GND |
| 13 | HS1_N | HS3_N | 24–25 | GND | GND |
| 14 | GND | GND | | | |
| 15 | USB2_DP | SBU1 | | | |
| 16 | USB2_DN | SBU2 | | | |
| 17 | GND | GND | | | |

| Item | MOD-C (USB-C) | MOD-A (USB-A 3.0) | MOD-H (HDMI) |
|---|---|---|---|
| HS0 / HS1 / HS2 / HS3 | TX1 / RX1 / TX2 / RX2 | SSTX / SSRX / NC / NC | D2 / D1 / D0 / CLK |
| CC1/CC2, SBU1/2 | CC, SBU | NC | SBU1/2 = DDC SCL/SDA |
| HPD, UTIL | – | NC | HPD; UTIL = CEC (NC) |
| VBUS (12 pins × 0.3 A = 3.6 A) | 5V_C per port (3 A = 83 %) | 5V_A | +5V |

- **PRSNT#:** grounded on the module → U97 TCA9555 input (on U96 ch 3; internal 100 k pull-ups); U97 INT# → PD_INT_N (→ U84 74LVC1G07 → IOB_INT_N).
- **ID EEPROM:** 24C02 at **0x50** on every module, on ID_SCL/ID_SDA, behind the I2C_PD muxes **U95 TCA9548A (0x70)** and **U96 TCA9548A (0x71)**: C1–C6 = U95 ch 0–5, A1–A2 = U95 ch 6–7, A3–A4 = U96 ch 0–1, HDMI = U96 ch 2. U96 ch 3 is U97's private segment; ch 4–7 are spare. Only one channel is enabled at a time, so the eleven 0x50 EEPROMs never clash (§11). All of this is on 3V3 (S0), so module IDs are readable in S0 only.
- **Impedance:** 90 Ω differential (USB), 100 Ω (TMDS), 2-layer PI FPC with L2 solid GND; JLC does not test FPC impedance → coupon + TDR.
- **Status:** module outlines/footprints DRC 0/0, no nets or routing yet; DF40/receptacle/EEPROM land patterns are placeholders (port-module worker). Not checked net by net in this ICD.

---

## 11. I²C / SMBus address map

| Bus (master) | Domain | Device | Address | Board | Status |
|---|---|---|---|---|---|
| I2C_SYS (BP MCU) | 3V3_SB | **INA228** BP 12V_MAIN (rev 2) | 0x40 | BP | Proposal |
| | | **INA228 U98** IOB 12 V (rev 2; A1 GND, A0 VS) | **0x41** | IOB | **NEW** |
| | | TMP1075 U3 / U4 | 0x48 / 0x49 | BP | Proposal |
| | | BP ID EEPROM | 0x50 | BP | Proposal |
| | | LIS2DH12 U81 | 0x18 | IOB | OK |
| | | ID EEPROM U82 BL24C64A | 0x51 | IOB | OK |
| | | TLC59116 U80 (+ all-call 0x68, SWRST 0x6B reserved) | 0x60 | IOB | OK |
| | | I/O-wall LED MCUs (via J31 DNP links) | **unknown** | stock flex | OPEN (U-9) |
| | | PSU SMBus (DNP 0R) | **unknown** | PSU | OPEN (U-1) |
| I2C_PD (behind IOB TCA9517 U83, EN = PG_3V3) | 3V3 (S0) | TPS65994AD U1–U3 (I2C1 target; IOB `build_sch.py` uses the 0x20–0x27 range) | **TBD (ADCIN2 straps)** — must avoid 0x18/**0x40/0x41**/0x48–0x51/0x4C/0x60/0x68/0x6B/**0x70/0x71** | IOB | OPEN (U-10) |
| | | **TCA9548A U95 / U96** (port-module muxes, rev 2) | **0x70 / 0x71** | IOB | **NEW** (port-module worker) |
| | | behind U95/U96 private channels: **24C02 ID EEPROM** per module slot (11 ×) | 0x50 (one channel at a time) | port modules | **NEW**; no clash (private) |
| | | behind **U96 ch 3** (private `MODMGT` segment): **TCA9555 U97** (module PRSNT# inputs, INT# → PD_INT_N) | 0x27 | IOB | **NEW**; private channel, so no clash with the TPS65994 0x20–0x27 range |
| | | **EMC2101 U90** | 0x4C | IOB | **FIXED** (was on I2C_SYS with an S0-only VDD → bus clamp risk in S5) |
| FACE_P_SMB / FACE_S_SMB (BP MCU, one segment each) | 3V3_AUX | ID EEPROM / TMP1075 (+ 0x49–0x4F extra sensors, 0x51–0x57 other) | 0x50 / 0x48 | module | **FIXED** (arch §7.9 now allows 0x49–0x4F; SM-1 uses 0x49) |
| | | **INA228 12 V monitor** (mandatory > 3 W; SM-1 U13) / **power-target agent** (modules with an MCU) | **0x40 / 0x58** | module | **NEW** (face spec §6.8, §8) |
| CPU-LINK I2C0 (BP MCU) | 3V3_SB | CB ID EEPROM (+ EC target TBD) | 0x57 | CB | **FIXED** (was on the PCH SMBus); approved O-4 |
| | | **INA228 U15** CB 12 V (rev 2; A1 = A0 = VS) | **0x45** | CB | **NEW** |
| PCH SMBus (PCH) | CB | DDR5 SPD / PMIC / TS | 0x50–0x53 / 0x48–0x4B / 0x10–0x13, 0x30–0x33 | CB | isolated from CPU-LINK SMB_* by DNP 0R (**approved, O-4**) |
| TUSB1046A I2C (per PD I2C3) | local | TUSB1046A | 0x12 / 0x13 | IOB | local, not on I2C_SYS |

---

## 12. PCIe lane, clock and reset map (no double-booking)

| Source | Lanes | Consumer | Board / connector | REFCLK | PERST# | CLKREQ# |
|---|---|---|---|---|---|---|
| CPU PEG | x16 | Face P | CPU-LINK → BP J9 | FP_REFCLK (PCH SRCn TBD) | BP: PLTRST# ∧ FACE_P_RDY | ends on BP |
| CPU PCIe | x4 | Face S | CPU-LINK → BP J10 | FS_REFCLK (SRCn TBD) | BP: PLTRST# ∧ FACE_S_RDY | ends on BP |
| PCH HSIO 0–9 | 10 × USB3 10 G | IOB C1–C6, A1–A4 | J3/HS1 k0–k9 | – | – | – |
| PCH RP1–2 (HSIO 10–11) | 2 × x1 | spare | – | – | – | – |
| PCH RP3 (HSIO 12) | x1 | i226 #1 | HS1 k10 | SRC12 | CB PLTRST-derived (shared) | SRCCLKREQ12# |
| PCH RP4 (HSIO 13) | x1 | ASM1182e → i226 #2 + AirPort | HS1 k14 | SRC11 [Proposal] | shared | SRCCLKREQ11# (held low) |
| PCH RP5–8 (HSIO 14–17) | x4 | reserved AQC107 (needs a 2nd cable) | – | – | – | – |
| PCH RP9–12 (HSIO 18–21) | x4 | CB J8 M.2 boot | CB | SRCn TBD | CB | CB |
| PCH SATA (HSIO 22–25 SATA-capable) | 1 | BP J7 OpenCore SSD | CPU-LINK SATA0 | – | – | – |
| CPU DDI-B / DDI-C | 4 + 2 lanes + AUX | IOB C5 / C6 | HS1 k11–k13, k15 | – | – | – |
| GPU DP links 0–4 | | IOB C1–C4, HDMI | DISPLAY-LINK | – | – | – |

Check: every CPU and PCH lane appears once. SRC11 / SRC12 are taken by the IOB; the CB must assign the Face P / Face S / M.2 CLKOUTs from the remaining SRCs (U-12). SATA0 lane choice U-13.

---

## 13. Power budget (system, 12 V side)

| Load | Worst case | Sustained | Source |
|---|---|---|---|
| CB | ≈ 142 W (PL2 92 W) | ≈ 75 W (PL1 35 W) | CB plan §3.3 |
| Face P | 130 W (cap) / 150 W after P3 | 130 W | face spec §6.2 |
| Face S (SM-1) | 40 W | ≈ 35 W | SM-1 plan §4.4 |
| BP | ≈ 10 W (G4) / 17 W (G5) | ≈ 10 W | arch §4.4 |
| Fan (IOB CONN_C) | ≤ 10 W | ≈ 3–5 W | M-IOC1 |
| IOB | ≈ 99 W | ≈ 75 W (pool 45 W) | IOB plan §7 |
| **Total** | **≈ 431 W (≈ 451 W at Face P 150 W)** | **≈ 330–345 W** | PSU 450 W; **ceiling 445 W** (rev 2; was ≤ 405 W) |

Standby (11 V SB, 5 W): BP MCU/sensors ≤ 0.3 W, faces ≤ 0.1 W, CB 5V_SBY 1–3 W (estimate; measure), IOB 3V3_SB ≤ 0.05 W with LEDs off (**port lights in S5 add ≈ 0.1–0.3 W; Bluetooth adds its idle draw if 3V3_BT stays on 3V3_SB**), loss ≈ 15 % → ≈ 2.3–4.2 W. Rev 2: Bluetooth moved to S0 (O-3 closed), so it no longer adds to S5.

### 13.1 Margins against the 445 W ceiling (rev 2)

| Case | 12 V total | Margin to 445 W |
|---|---|---|
| Sustained | 330–345 W | 100–115 W |
| Static safe allocation (CB PL1 35 / PL2 65 ≈ 112 W, faces at declared class, pool 45 W, BP, fan, IOB logic) | 408 W (428 W with Face P 150 W) | 37 W (17 W) |
| Transients (PL2 + pool + Face P 130 W) | 417 W | 28 W |
| Unmanaged worst case | 431 W (438 W with BP-G5) | 14 W (7 W) |
| Unmanaged worst case, Face P 150 W | 451 W (458 W with BP-G5) | **−6 W (−13 W) → held by the LPT** |

### 13.2 Live power target (LPT) — signals, telemetry, firmware (arch spec §5.5) [Proposal]

**Loop:** BP MCU, 10 Hz. Ceiling 445 W, loop target 430 W. Prediction per consumer = max(EWMA 1 s + 2σ, demand hint), clipped to [floor, cap]. Headroom goes CPU turbo → GPU → USB-C pool → storage; claw-back in reverse. Floors = static safe allocation (§13.1); on telemetry or heartbeat loss > 1 s each consumer falls back to its floor by itself.

| Kind | Signal / register | Path | Notes |
|---|---|---|---|
| Telemetry | INA228 BP 12V_MAIN | I2C_SYS 0x40 | 16× avg (≈ 17 ms), energy every 100 ms |
| Telemetry | INA228 IOB 12 V (U98, RS90 1 mΩ) | I2C_SYS 0x41 (IOB-LINK 8/9) | ALERT → IOB_INT_N |
| Telemetry | INA228 CB 12 V (U15, RS1 0.5 mΩ) | CPU-LINK I2C0 0x45 | ALERT ∨ U11 FLT# → A105 PWR_ALERT# |
| Telemetry | INA228 module 12 V | FACE_x_SMB 0x40 (AUX 8/9) | ALERT ∨ eFuse FLT# → FACE_x_SMB_ALERT# (AUX 10) |
| Telemetry | CPU RAPL package power, PL state, PROCHOT, Tj | EC → MCU over CPU-LINK UART0 (`LPT_REPORT`) | backup: EC eFuse IMON |
| Telemetry | PSU output (if the 6P data header has SMBus) | I2C_SYS via IOB DNP 0R | cross-check only (U-1) |
| Telemetry | TPS65994 per-port contracts | I2C_PD (U83) | PD addresses U-10 |
| Alert in | PWR_ALERT_BP_N (BP INA228), MOD_PWR_ALERT_N (A105), IOB_INT_N, FACE_P/S_SMB_ALERT_N | MCU GPIO IRQ | alert limit = allocation + 10 % (CB, faces) / board cap (BP, IOB) |
| Actuator | CPU PL1/PL2/Tau/PL4/ratio cap | MCU → EC UART0 `LPT_SET` → SMI → SMM writes MSR 0x610 (+ MCHBAR RAPL mirror), 0x601, 0x1AD | ≤ 10 ms; PECI limit writes only if supported (O-7) |
| Actuator (fast) | CARRIER_HOT# → PROCHOT# | CPU-LINK, hardware path | < 1 ms |
| Actuator | GPU `p_target_w` (reg 0x00); reads `p_now_w` 0x01, `p_request_w` 0x02, flags | FACE_P_SMB agent 0x58 | settle ≤ 100 ms, 1 s heartbeat |
| Actuator (fast) | THERM_ALERT# driven low by the host | AUX 11 | module cuts ≥ 25 % within 100 ms |
| Actuator | USB-C source PDOs (3 A / 1.5 A), pool 30–60 W | I2C_SYS → U83 → I2C_PD → TPS65994 (source caps + "SSrC" 4CC) | ≈ 0.5–1 s (O-8) |
| Actuator | NVMe power state (FID 02h) | MCU → vendor HID → macOS helper | SM-1 has no MCU; THERM_ALERT# backstop |
| Fan | EMC2101 LUT / TCRIT / PWM / fan-fail | MCU → I2C_PD 0x4C, **reloaded at every S0 entry** + read-back | O-5 approved |

**Fast path:** any alert → MCU IRQ (< 100 µs) → read the sensors (≤ 2 ms) → if Σ > 445 W: assert CARRIER_HOT# + FACE_P_THERM_ALERT#, drop the pool to 45 W; release after 200 ms once Σ < 430 W and the new limits are set.

| Agent | Firmware requirement |
|---|---|
| BP MCU (RP2350) | LPT loop; INA228 setup at every 3V3_SB power-up; I2C masters I2C_SYS, I2C0, FACE_P/S_SMB; UART0 EC link with 10 Hz heartbeat; fast path in the IRQ handler; TPS65994 PDO management; EMC2101 reload at every S0 entry; telemetry/event log over vendor HID |
| CB EC (RP2350) | `LPT_SET` / `LPT_REPORT`; apply limits via SMI/SMM; RAPL reads (PECI or SMM); fall back to PL1 35 / PL2 65 W on heartbeat loss > 1 s; CARRIER_HOT# → PROCHOT# in hardware |
| CB BIOS / SMM | MSR 0x610 lock bit (63) **clear**; SMI handler for the EC mailbox; boot at PL2 65 W |
| Face module MCU | face spec §6.8: INA228 0x40 (> 3 W, mandatory), agent 0x58 (`p_target_w` etc.), floor on heartbeat loss |
| macOS helper | NVMe Set Features FID 02h per SSD; optional GPU limits; reports over vendor HID |

---

## 14. Mechanical mating and keep-outs

| Item | Value | Status |
|---|---|---|
| CR-BP-1 | Ø6 rule-area keep-outs (all copper layers, no footprints/tracks/vias/pour) at S1 (−52.64, 13.81), S2 (−26.57, −46.65), S3 (26.49, −46.64), S4 (−18.12, 50.70), S5 (18.49, 50.72), S6 (52.80, 13.88); fit check courtyard ≥ 3.0 from each centre | **APPLIED** |
| U4 | (−27, −46.5) → **(−30, −38)** (S2 was inside its courtyard) | **FIXED** |
| J6 / J3 / J4 / J8 / U3 / Y1 | moved for S3 / S4 / S5 and the new J9 (§6, §7); fp5: J3 (0, 51.4), J4 (−38.0, 2.5), J8 (−40, −34), SW1 (30.5, −34), U3 (0, 41.6), Y1 (−2.6, 6) | **FIXED** |
| J5 (fan) | removed | **FIXED** |
| Fit check | fp5: all 27 BP parts rmax ≤ 58 (max 57.8), gold-hole ≥ 6, S ≥ 3: **ALL OK**; DRC 0 / 0, ERC 0 | OK |
| Face normals | **≈ 45° / 135° (Aidan 2026-10-02, M2c answered; C-18 closed)**. BP fp5 re-placed J9/J10/J3/J4, redrivers, MCU, SW1/J8; CB unaffected (GPU board ends 14.7 mm in front of the CB plane); module frame unchanged. Residual: caliper check of each GPU face | **RESOLVED** (U-7 residual) |
| GPU-board bottom edge above the BP | 15 mm (M1) vs ≈ 23.5 implied by the standoffs (**M1c / C-16**) | OPEN |
| CB tab ↔ BP J1 | slot y −12.5 ± 0.3 (scan) vs J1 −12.6 | OK |
| MCIO clearance under the cards | plug body 8.2 mm → 6.8 mm under the 15 mm edge (15.3 at 23.5); jog cable feasibility **O-6** | OPEN (O-6) |
| Cable lengths | MCIO BP→faces: only ≈ 12–20 mm free between plug rears (rev 2 space check; was 30–60 mm) (M4, C-9); HS1 CB→IOB and DISPLAY-LINK (M9); GH15 AUX ×2, IOB-LINK, Micro-Fit harness — none measured | OPEN (U-6) |
| IOB riser / plate geometry | being re-tilted by another worker (change 29); not touched here | – |

---

## 15. Ground

| Path | Carries | Note |
|---|---|---|
| PSU bus bars → CB GND lug / face GND lugs | 12 V return of the CB and faces | intended return path |
| PSU DC 12P pins 7–12 → IOB | IOB 12 V return (≈ 10 A) | |
| IOB J5 3–5 → BP J2 3–5 | BP return (≈ 1 A) | |
| CPU-LINK 80 GND | CB ↔ BP reference, PCIe return | parallel to the lug path → 12 V return current can share it |
| MCIO shells/GND (4 cables), GH GND pins | signal reference | must not carry 12 V return |
| BP H1/H2 plated holes | chassis | GND/chassis bond [Inference] |

**OPEN (U-11):** single-point chassis bond and how much 12 V return current flows through CPU-LINK / MCIO grounds instead of the bus bars. Measure DC drop CB GND lug ↔ BP GND under load during bring-up.

---

## 16. Decisions for Aidan

| ID | Decision | Outcome (rev 2) | Status |
|---|---|---|---|
| ~~O-1~~ | BP J10 cannot meet CR-2 | **Aidan: flat-ribbon twinax MCIO cables that bend and jog.** At 45° both J9 and J10 need the jog (13.7 / 10.5 mm); J_PCIE stays at X 43.5 | CLOSED → feasibility O-6 |
| ~~O-2~~ | 12 V budget > 405 W | **Aidan: 445 W ceiling (PSU 450 W) + live power target** (§13.1, §13.2); D-IO1 pool cap stays mandatory | CLOSED |
| ~~O-3~~ | IOB 3V3_BT rail | **S0: R149 fitted, R148 DNP** (IOB `build_sch.py`, ERC 0) | CLOSED |
| ~~O-4~~ | CB ID EEPROM on I2C0 + PCH SMBus isolated | **approved** (CB plan fl2.3) | CLOSED |
| ~~O-5~~ | EMC2101 fail-safe | **approved:** BP MCU reloads LUT/TCRIT/PWM/fan-fail at every S0 entry + read-back (check the power-on default duty, U-14) | CLOSED |
| **O-6** | **Jog-cable feasibility:** only ≈ 12–20 mm free cable between plug rears (M1 15 → 23.5) vs 10.5–13.7 mm jogs and a ≥ 3 mm bend rule | Get the MCIO plug drawing (length to cable exit, U-19), measure M1c, ask Amphenol/vendor for a jog sample (M4). Fallbacks: (a) shorter or side-exit BP plug; (b) move the BP receptacles inward (fp6, smaller r_c; fit/J1 limits); (c) raise Y_mate on the module (≤ 28.5, MECH rev); (d) J_PCIE at module X 52 on all modules (template + SM-1 J1 move, ≈ 4–5 mm jogs) | **OPEN** |
| **O-7** | Do PECI power-limit writes (WrPkgConfig) work on Raptor Lake client parts? | If not: SMM mailbox only (already the primary path) | OPEN [Unverified] |
| **O-8** | TPS65994 PDO renegotiation timing (source caps + SSrC) and sink behaviour (Apple/USB-PD devices) | Measure at bring-up; LPT assumes ≈ 1 s | OPEN [Unverified] |
| **O-9** | INA228 (VSSOP-10) LCSC part number, stock and pin numbering of the symbol | Verify against the TI datasheet before schematic freeze (CB U15, IOB U98, SM-1 U13, template U5) | OPEN [Unverified] |

---

## 17. Unverified items (need a measurement or a datasheet)

| ID | Item | Affects | Ref |
|---|---|---|---|
| U-1 | Stock PSU 12P DC and 6P data pinouts, pin ampacity, SMBus presence | I-7/I-8, IOB 12 V | M6, M-CC16, IOB §9.1 |
| U-2 | PS_ON# polarity/level, PWR_OK timing, 11 V SB behaviour | BP gate | M6 |
| U-3 | Which PSU terminal pair feeds the CB and lug polarity | CB LUG1/2 | M-CC16, M-CC7 |
| U-4 | Face lug positions, polarity per face, bus-bar ampacity | Face J20–J23 | M5 |
| U-5 | CONN_C pinout, fan current, FG pole count, antenna receptacle | IOB J7/J8, fan | M-IOC1, M-IOC3, M-IOA1, M7 |
| U-6 | Cable lengths and routes: MCIO BP→faces (30–60 mm, custom), HS1 CB J3→IOB J1, DISPLAY-LINK, GH15 ×3, Micro-Fit harness | ordering | M4, M9, C-9 |
| U-7 | ~~Face-normal angle~~ **answered ≈ 45° / 135° (rev 2)**; residual caliper check of each GPU face; GPU-board edge height 15 vs 23.5 mm | J9/J10 jog, O-6 | M2c (residual), M1c, C-16 |
| U-8 | ASM1182e: downstream REFCLK outputs and per-port PERST# (IOB wires the host I226_PERST# straight to U50/U52/U91/J7) | i226 #2, AirPort | ASM1182e datasheet |
| U-9 | I/O-wall flex LED MCU addresses and supply | I2C_SYS map | IOB §9.5 |
| U-10 | TPS65994AD I2C addresses from the ADCIN2 straps | I2C_PD | TI datasheet |
| U-11 | Ground return sharing (§15) | all | bring-up |
| U-12 | PCH CLKOUT_SRC assignment for Face P, Face S, M.2 (SRC11/12 used by the IOB) | CB | Z790 PDG / MSI ref |
| U-13 | SATA0 HSIO lane (SATA-capable, not RP9–12; e.g. HSIO 22–25 group) [Inference] | CB, BP J7 | Z790 Flex-I/O |
| U-14 | EMC2101 power-on default duty; SMBus pin back-power tolerance | fan fail-safe | EMC2101 datasheet |
| U-15 | USB2 over the unshielded GH15 IOB-LINK (CPU-LINK → BP → IOB) signal integrity | Bluetooth, USB-A USB2 | bring-up |
| U-16 | CB 5V_SBY S5 draw | standby budget | measure |
| U-17 | IOB PCB value text for U90 still says "I2C_SYS" (placement.json; next IOB PCB rebuild by the riser worker) | docs only | – |
| U-18 | IOB PCB placement of **U98 INA228 + RS90 1 mΩ** (schematic only in rev 2; RS90 in the 12 V path right after U40, Kelvin pair, U98 ≤ 10 mm) | IOB PCB | IOB PCB owner |
| U-19 | MCIO 124 cable plug length (mating face → cable exit) and exit style (straight / side) | O-6, cable order | plug drawing, M4 |
| U-20 | Stock PSU behaviour at 445 W for > 1 s (OCP/OPP point) | 445 W ceiling | M6 |

---

## 18. Files changed

### 18.1 Rev 2 (2026-10-02 ≈ 12:40–13:15 ET)

- **BP** `kicad/macpro62-backplane/`: `tools/hub_floorplan.py` (fp5, 45° / 135°), `tools/build_pcb.py`, `tools/build_sch.py` (PWR_ALERT stubs, LPT/EMC2101 text), `tools/cpulink_pinout.py` (A105 PWR_ALERT#), `README.md`; regenerated `backplane.kicad_pcb`, `drc_report.txt` (0/0), `fitcheck_floorplan.txt` (ALL OK), `floorplan.png/.svg`, `lane_length_estimate.txt`, `.kicad_sch`, `erc_report.txt` (0), `schematic_blockdiagram.pdf`, `docs/cpulink_224_pinout_draft.csv`.
- **CB** `kicad/macpro62-lga1700/`: `tools/make_placeholders.py` (`MP62_AREA_PwrMon_INA228_10x6`), `tools/build_pcb.py` (U15, rev A-fl2.3), regenerated PCB, `drc_report.txt` (0/0), `floorplan.png`, `docs/cpulink_224_pinout_draft.csv`; plan `macpro62-lga1700-board-plan.md` (fl2.3).
- **IOB** `kicad/macpro62-io-board/` (schematic only): `tools/build_sch.py` (R148 DNP / R149 fitted, U98 INA228, RS90, C990, +12V_EFUSE_OUT), `tools/make_fps.py`, new `MP62_IO.pretty/VSSOP-10_3x3mm_P0.5mm.kicad_mod`, `MP62_IO.pretty/R_2512_6332Metric.kicad_mod`; regenerated `macpro62-io-board.kicad_sch`, `erc_report.txt` (0), `docs/sch_netlist_summary.txt`; plan `macpro62-io-board-plan.md` + `docs/` copy (§4.7.7, §7). `placement.json`, risers and plate untouched.
- **SM-1** `kicad/macpro62-storage-face/`: `tools/build_sch.py` (U13, R520, C520), `tools/build_storage.py`, `tools/make_storage_fps.py`, new VSSOP-10 / R_2512 footprints, regenerated PCB/schematic, `drc_report.txt` (0/0), `erc_report.txt` (0), `README.md`; plan `macpro62-storage-board-plan.md`.
- **Face template** `kicad/macpro62-face-template/`: `tools/make_footprints.py`, `tools/build_template.py` (reference RS1/U5), new VSSOP-10 / R_2512 footprints, regenerated PCB, `drc_report.txt` (0/0), `README.md`.
- **Face spec** `macpro62-face/src/spec_part1..5.md` → `macpro62-face-module-spec-v0.1.md` (update 4: §3.5, §3.6 cable, §6.3, new §6.8 LPT, §7, §8, §13).
- **Master spec** `macpro62-architecture-spec-v0.2.md` (change 32; §3.1, §3.4, §3.13, §4.8, §4.9, §5.4, new §5.5, §7.9, M2c).
- This ICD; zips rebuilt.

### 18.2 Rev 1 (2026-10-02 ≈ 12:30 ET)

- **BP** `kicad/macpro62-backplane/`: `tools/hub_floorplan.py`, `tools/build_pcb.py`, `tools/build_sch.py`, `tools/make_placeholders.py`, `tools/cpulink_pinout.py`, `README.md`; regenerated `backplane.kicad_pcb/.kicad_pro`, `drc_report.txt` (0/0), `fitcheck_floorplan.txt` (ALL OK), `floorplan.png/.svg`, `lane_length_estimate.txt`, all `.kicad_sch` (fan sheet deleted), `erc_report.txt` (0), `schematic_blockdiagram.pdf`, `docs/cpulink_224_pinout_draft.csv`; new `MP62_BP_Stubs.kicad_sym`, `sym-lib-table`, `MP62_Placeholders.pretty/MP62_MCIO_124P_RA_SFF-TA-1016.kicad_mod`.
- **CB** `kicad/macpro62-lga1700/`: `tools/build_pcb.py`, `tools/make_placeholders.py`, new `tools/make_j3_pinout.py`, new `docs/mp62-cb-j3_mcio124_host-end.csv`, `docs/cpulink_224_pinout_draft.csv`; regenerated PCB, `drc_report.txt` (0/0), `floorplan.png`; plan `macpro62-lga1700-board-plan.md` (fl2.2).
- **IOB** `kicad/macpro62-io-board/`: `tools/build_sch.py` (J2 row swap, U90 bus), regenerated `macpro62-io-board.kicad_sch`, `erc_report.txt` (0), `docs/sch_netlist_summary.txt`, new `docs/mp62-iob-j2_mcio74_displaylink_iob-end.csv`; plan `macpro62-io-board-plan.md` + `docs/` copy (§4.7.7 fan control, §5.2, §5.5, §7 budget).
- **Face spec** `macpro62-face/src/spec_part1.md`, `spec_part4.md`, `spec_part5.md` → rebuilt `macpro62-face-module-spec-v0.1.md` (host = CB, §9.6 IOB-end table, §13 CR status).
- **SM-1** `macpro62-storage-board-plan.md` (§10 O-1 row).
- **Master spec** `macpro62-architecture-spec-v0.2.md` (change 30; §1.2, §3.8, §3.9, §4.1, §4.3, §4.4, §4.6, §4.7, §4.8, §4.9, §5.1, §5.3, §5.4, §7 banner/§7.5/§7.6/§7.8/§7.9, M7).
- This ICD.
