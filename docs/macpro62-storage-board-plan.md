# MacPro6,2 storage face module (Face S), SM-1 rev A0: plan

| Item | Value |
|---|---|
| Date | 2026-10-01 (written ≈ 20:15 ET); **rev 2026-10-02 ≈ 13:15 ET (ICD rev 2): U13 INA228 12 V monitor + R520 shunt, live power target via NVMe power states, face angle 45° (no SM-1 impact)** |
| Owner | Aidan Winkler (MacPro6,2 project) |
| Module | **SM-1 rev A0**: 4 × M.2 2280 NVMe behind an **ASMedia ASM2824** PCIe Gen3 switch, for Face S (BP J10). It also fits Face P. |
| Spec basis | MP62-FACE v0.1 update 2 (`macpro62-face-module-spec-v0.1.md`), architecture spec v0.2, CPU board plan §1.2 |
| KiCad | `kicad/macpro62-storage-face/`, KiCad 9. **Floorplan:** outline, holes, keep-outs, stackup, every IC, connector, socket, standoff, inductor and bulk capacitor placed. DRC **0 / 0**. Schematic: all symbols with labelled connectivity, ERC **0 errors, 0 warnings**. **Routing has not started.** |
| Status | **Plan for review. D1 approved, D4 resolved (2026-10-01, ≈ 20:27 ET). Nothing ordered.** Three land patterns are PLACEHOLDERS (M.2 socket, ASM2824 BGA, TPS56C215). The ASM2824 datasheet is under NDA (§9). |

Tags: **[Sourced]** = from a datasheet, distributor page or our own spec; **[Estimate]**; **[Inference]**; **[Unverified]**; **TBD** / **TO MEASURE**.

---

## 1. Summary and recommendation

1. **The x4 link has to go through a switch.** Face S gets CPU PEG60 Gen4 x4 (CPU-LINK lanes 12–15), and PEG60 **cannot bifurcate**. Without a switch, the module can run only one SSD [Sourced: CPU board plan §1.2, Intel datasheet].
2. **Use the ASMedia ASM2824** (Gen3, 24 lanes: x8 upstream, 4 × x4 downstream).
   - It is the only switch that is cheap, documented by working community boards, and available through JLC's own stock (JLC part C9900092023).
   - Its built-in clock buffer supplies the SSD reference clocks.
   - It can route in 4–6 layers and runs cool enough for passive cooling.
   - The cost of the choice: **Gen3 x4 today ≈ 3.5 GB/s shared by all four SSDs.** If the host later wires x8 (OQ-7), the same board does ≈ 7 GB/s, because the switch's x8 upstream is wired to J_PCIE lanes 0–7 now.
3. **Layout:** all four M.2 cards go on the **outer side** (three 2280 columns plus one 2280 across the top). The switch sits on the **core side**, on the die pad, under a soft gap pad.
   - The core side cannot take standard M.2 sockets: card bottom plus components needs ≈ 4.65 mm, against the 3.5 mm limit.
   - Four 2280 cards on the outer side only fit **without the stock X-bracket** (deviation **D-S1**, conflict C-19). Without the bracket, 4 × 2280 fit. With the bracket, only ≈ 2 × 2280 + 1 × 2260 fit.
4. **Power:** 12 V from the lugs → LM74700 reverse block → TPS259824 eFuse (5 A) → TPS56C215 12 A buck → 3V3_SSD.
   - 4 × 2.5 A for the SSDs plus the switch.
   - Declared **40 W, Class 1**. The theoretical 10 ms peak is ≈ 41.5 W, inside the Class 1 peak of 52 W.
5. **Cost:** 5 PCBs (6 layers) with 2 assembled at JLC ≈ **$330–600** total [Estimate]. That excludes SSDs and the MCIO cable. Parts are ≈ $45–80 per board, of which the ASM2824 is the unknown ($15–40 [Unverified]).
6. **RAID (§8): bootable hardware RAID is not realistic on this board.**
   - The only chip that presents itself as a plain NVMe drive is the Marvell 88NR2241. It is NDA-only, not distributed, and not proven on macOS.
   - Recommended instead: boot from a single SSD, and use **AppleRAID or SoftRAID across the other SSDs as data volumes**.
   - The 88NR2241 stays a possible future variant **SM-1R**. The base board pays nothing for it.

### Decisions Aidan must make

| # | Decision | Recommendation | Consequence of the other option |
|---|---|---|---|
| **D1** | Drop the X-bracket on Face S (low-head screws straight into the bosses, gap pad on the switch) | **APPROVED by Aidan (2026-10-01, ≈ 20:27 ET):** no bracket, 4 × 2280 fitted, module secured with flatter low-head screws | (Rejected: keep the bracket → 2 × 2280 + 1 × 2260) |
| **D2** | Gen3 ASM2824 (≈ 3.5 GB/s total on x4) vs a Gen4 switch (PM40028 / PEX88024, $164–323, NDA, 26+ weeks) | **ASM2824** | Gen4 would give 7.9 GB/s on x4, but costs ≈ 8× more, needs 8+ layers, and has no stock |
| **D3** | Accept J_AUX moved 6 mm down (Y 26.5 → 20.5; the spec says "should") | **Yes** | Otherwise the first SSD column moves and a 2280 no longer fits |
| **D4** | Screw heads under the edges of SSD0/SSD2 | **RESOLVED (2026-10-01): low-head screws, head + washer ≤ 1.6 mm** (wafer / ultra-thin head, §3.3). Any 2280 SSD (single- or double-sided) can go in any slot. Concrete part follows once MF-13 gives the thread | (Rejected: single-sided SSDs only in SSD0/SSD2, or narrower columns) |
| **D5** | 6-layer rev A (template stackup) vs 4 layers | **6 layers** for rev A; try 4 layers as a cost-down once the ball map is known | 4 layers saves ≈ $40–90 per order, but risks a respin |
| **D6** | RAID: no hardware RAID; boot from one SSD; AppleRAID/SoftRAID for data | **Yes** (§8) | Hardware RAID would need the Marvell 88NR2241 (variant SM-1R), which can't be bought |

---

## 2. Switch choice

| Part | Gen | Lanes (up / down) | Package | Price / availability | Power | Notes |
|---|---|---|---|---|---|---|
| **ASMedia ASM2824** | 3 | 24: x8 up; 16 down, up to 12 ports (4 × x4 here) | LFBGA-492, 21 × 21 | JLC **C9900092023** ("JLCPCB Assembly", new arrival; X-ray; price not shown). LCSC C20612120 shows 0 stock (MOQ 444, and the $0.04 price is not real). Broker stock exists (Allelco ≈ 4,860). **≈ $15–40 [Unverified]** | ≈ 3–5 W [Estimate; not published] | SRIS support; **built-in downstream clock buffer**; open 4-layer reference card (OSHWHub "wesd" ASM2824 M.2 card: "4 layers is enough", "not very hot, passive is enough", "chip prices skyrocketed") [Sourced] |
| ASMedia ASM2812 | 3 | 12: x4 up, 8 down | same ball-out (pin-compatible) | as above | lower | Upstream lanes 4–7 and downstream 8–15 unavailable. A **2-SSD cost-down** option on the same PCB |
| ASMedia ASM2806 | 3 | 6: x2 up, 4 × x1 down | QFN88 | — | ≈ 1–2 W | Too narrow (x2 upstream) |
| Microchip PM40028 (Switchtec PFX) | 4 | 28 | FCBGA | $164–280, 0 stock, 26–28 weeks | ≈ 8–12 W [Estimate] | NDA config; ≥ 8 layers |
| Broadcom PEX88024 | 4 | 24 | FCBGA | ≈ $323, brokers | ≈ 8–10 W [Estimate] | NDA |

**Bandwidth trade-off**

| Host link | Raw | Real (≈ 88 %) | Per SSD with all four busy |
|---|---|---|---|
| Gen3 x4 (today, ASM2824 on BP J10 lanes 0–3) | 3.94 GB/s | ≈ 3.5 GB/s | ≈ 0.9 GB/s |
| Gen3 x8 (later, if the host wires x8: OQ-7) | 7.88 GB/s | ≈ 6.9 GB/s | ≈ 1.7 GB/s |
| Gen4 x4 with a Gen4 switch (not chosen) | 7.88 GB/s | ≈ 6.9 GB/s | ≈ 1.7 GB/s |
| Gen4 x4 to one SSD, no switch (CPU-board M.2 style) | 7.88 GB/s | ≈ 6.9 GB/s | one SSD only |

- **One SSD at a time:** a single Gen3 x4 SSD runs at full speed (≈ 3.5 GB/s) behind the switch. A Gen4 SSD gets Gen3 speed.
- **Latency:** the switch adds ≈ 150 ns of cut-through latency [Estimate]. That is invisible on NVMe.
- **Gen4 at 8× the cost** only pays off once the host gives Face S Gen4 x8 and the user needs > 3.5 GB/s of aggregate throughput.

---

## 3. Mechanical

### 3.1 Why the outer side

- **Core side (F) does not work.** The limit is ≤ 3.5 mm (G = 4.5 ± 0.5). A standard M.2 socket puts the card bottom at ≈ 2.5 mm (H3.2), plus a 0.8 mm card, plus 1.35 mm of top-side parts ≈ **4.65 mm**.
  - Mid-mount (sunken) sockets would need 4 cutouts of ≈ 22 × 84 mm through the die pad and boss area. Not possible.
- **The die pad must carry the switch.** It is the only > 2 W part, it is the hot spot at (52, 69.5), and it has nowhere else to go.
- **Outer side (B), envelope:** h(x) is ≥ 13.6 mm across X 15.5–88.5. A card top at ≈ 5.8 mm (H4.2 socket) leaves room for ≈ 7 mm heatsinks on SSD0/SSD2 and ≈ 13 mm on SSD1.

### 3.2 Placement (module frame, viewed from the core side; see `floorplan_storage_SM1.png`)

| Item | Position | Side | Notes |
|---|---|---|---|
| **SSD0 / SSD1 / SSD2** | Columns centred at X **26.5 / 52.0 / 77.5** (cards X 15.5–37.5, 41–63, 66.5–88.5) | B | Card-edge datum at **Y 108.5**, socket body to Y ≈ 115. Cards run **toward −Y**, to Y 28.5, which is the 2280 standoff, just above the connector band. Long axis along the airflow. 2 mm air gaps between cards. |
| **SSD3** | Across the top: datum X 12, card X 12–92, Y 115–137 | B | Socket at X ≈ 5.5–12, where h(5.5) = 7.5 mm. Stays clear of the lug keep-outs (Y ≥ 139). |
| **Standoffs** | 2280 at each card end (fitted). 2230/2242/2260 footprints **DNP** (SSD1 has only 2260/2280; the 2230/2242 positions sit behind U1) | B | Shorter cards are possible at no cost. Not fitted by default, because a metal standoff under a double-sided 2280 can touch the card's bottom-side parts |
| **J1 J_PCIE** | X 43.5, mating face Y 14.5 (per spec) | B | All 8 lanes wired |
| **J3 J_AUX** | **(16.5, 20.5)**, opening −X | B | Moved −6 mm (D3). Body Y 9.5–31.5, clear of SSD0 |
| **U1 ASM2824** | Centred on the die pad (52, 69.5) | F | 21 × 21 BGA ≈ 1.5–1.7 mm tall. **3.0 mm soft gap pad**, no Cu block (§3.3) |
| Switch support (U5/L2 core buck, Y1, U8 flash, U7 TMP1075, U9/U10/U12 PERST# buffers, bulk caps) | Around TZ1 | F | All ≤ 2 mm tall, so ≤ 3.0 mm over the strip pads and ≤ 3.5 mm elsewhere |
| **Power band** (Q1 + U3 reverse block, U2 eFuse, U4 + L1 buck, output caps, U6 EEPROM, LEDs D1–D7) | Y 139–166, X 16–88 | B | h ≥ 13 mm. The lug keep-outs X 0–16 and 88–104 stay empty on both sides (spec) |
| **U11 TMP1075 (THERM_TRIP#)** | (52, 100) under SSD1 | B | WSON 0.8 mm, fine under a card |

**Height rules used on B:**
- Under an M.2 card, host parts **≤ 1.6 mm**. The card bottom is ≈ 3.5 mm (H4.2), and double-sided cards have bottom parts down to ≈ 1.35 mm. Only 0402/0603/0805 passives, the WSON sensor and decoupling go there.
- The 1.6 mm figure is [Estimate] until the LOTES drawing is checked.

### 3.3 Retention and cooling

- **No X-bracket (D-S1, D1 approved).** 4 **low-head screws** go straight through the Ø5.0 holes into the core bosses. No spacer under the head.
  - The board sits on the 4.5 mm bosses as on any module.
  - **Rule (D4 resolved):** screw head + washer **≤ 1.6 mm** above the outer surface. The outer edges of SSD0/SSD2 pass over the KO-B2 circles at X 15/89, about 2.15 mm above the board (the lowest point under a double-sided card: card bottom ≈ 3.5 mm minus 1.35 mm of bottom parts), which leaves ≥ 0.5 mm margin. Any 2280 SSD can go in any slot.
  - **Screw type (part number after MF-13):**
    - **Wafer / ultra-thin-head machine screw:** head ≈ 0.8–1.0 mm tall, Ø ≈ 6–7 mm (bears on the Ø9 pad, inside KO-B2 Ø12), Torx or cross recess, steel 8.8+ or A2 stainless.
    - Either no washer, or one DIN 433 / ISO 7092 small thin washer (≈ 0.5 mm for M3). That totals ≈ 1.3–1.5 mm.
    - Too tall: ISO 7380 button head (M3 k = 1.65 mm) and ISO 14583 / DIN 7985 pan heads (≈ 2+ mm). Head heights are typical catalogue values [verify on the vendor drawing].
  - **Length:** stock screw length minus the bracket eyelet thickness, to keep the same thread engagement in the boss (MF-13).
  - **Torque:** wafer heads have shallow drives. Tighten snug (≈ 0.5–0.8 N·m [Estimate]) with removable thread-locker, not the stock 1.2 N·m.
  - SSDs come out before the module is removed.
- **Switch heat path:** U1 → 3.0 mm soft gap pad (≥ 6 W/m·K, ≤ Shore 00-40) → die pad.
  - Gap 4.5 − ≈ 1.6 = 2.9 mm, so a 3.0 mm pad is ≈ 3–20 % compressed across the tolerance. With ±0.5 tolerance, use a 3.5 mm pad if G measures high.
  - R ≈ 3 mm / (6 W/m·K × 441 mm²) ≈ **1.1 K/W**, so 4 W gives a ≈ 5 K rise. No preload needed, so the bracket isn't needed for the switch either.
- **SSD cooling** (conflict C-20): the SSDs (2–8 W each) sit in the gap between board and shell, outside any core pad.
  - The cards run along Y (bottom intake → top fan), and the gaps between cards are open.
  - Stick-on M.2 heatsinks fit within the envelope (≤ 7 mm on SSD0/SSD2, ≤ 13 mm on SSD1/SSD3 centre).
  - NVMe drives throttle themselves at their composite-temperature limits, and the host reads their SMART temperatures.
  - **Outer-gap airflow TO MEASURE MF-14** (one thermocouple on an SSD during a 10 min write).

### 3.4 Sockets and standoffs (JLC/LCSC)

| Part | LCSC | Notes |
|---|---|---|
| **LOTES APCI0107-P001A**, M.2 M-key, H4.2 | **C841661** (≈ 1,592 stock) | Chosen: more air and more under-card room than H3.2 |
| LOTES APCI0079-P002A, M.2 M-key, H3.2 (double-sided module) | C841651 (≈ 1,119) | Fallback. Card bottom ≈ 2.5 mm, so the under-card limit drops to ≈ 0.6 mm and the screw-head limit to ≈ 0.6 mm |
| YIYUAN SMTSO M2 SMT standoff | C5301773 (SMTSOM225BTR, 2.5 mm tall, for H3.2) | For H4.2 use the ≈ 3.5 mm height of the same family (**part number TBD**, check the LOTES drawing for the card-bottom height) |
| M2 × 3 screws (or Q-latch) | — | Shipped with the SSD or bought separately |

---

## 4. Electrical

### 4.1 Block diagram

```
Lugs J20/J22 (+12V_IN) ─ Q1 + U3 LM74700 (reverse block) ─ +12V_PROT ─ R520 2 mΩ (U13 INA228) ─ +12V_PROT_S ─ U2 TPS259824 eFuse 5 A ─ +12V_SW ─ U4 TPS56C215 12 A ─ L1 ─ 3V3_SSD (≈ 10 A peak)
                                                                     │ PG                                   │ PGOOD
                                                                     └──────────────── EN ──────────────────┘     └─ U5 TLV62585 EN ─ VDD_CORE ─ PG_ALL ─ FACE_PWR_GOOD
J1 MCIO lanes 0-7 RX (A row) ───────────────────────► U1 ASM2824 UP RX0-7
J1 lanes 0-7 TX (B row) ◄── 220 nF ◄──────────────── U1 UP TX0-7
U1 DN port d TX0-3 ── 220 nF ──► M.2 SSDd PER0-3   |   M.2 SSDd PET0-3 ──► U1 DN port d RX0-3     (d = 0..3)
J1 REFCLK0± ──► U1 REFCLK_IN (common clock) ; U1 DNd_REFCLK± ──► M.2 SSDd REFCLK±
J1 PERST0# ──► U12 (AND PG_ALL) ──► U1 PERST# ; ──► U9/U10 74LVC2G07 ──► SSD0-3 PERST# (10k to 3V3_SSD)
J3 AUX: 3V3_AUX ─ U6 EEPROM 0x50, U7 TMP1075 0x48 (THERM_ALERT#), U11 TMP1075 0x49 (THERM_TRIP#, POR default 80 °C)
```

### 4.2 Signals

| Function | Implementation | Status |
|---|---|---|
| Upstream | ASM2824 x8 to J_PCIE lanes 0–7. 220 nF caps on the module TX (row B), per spec §4. Host caps on module RX. Rev A BP wires lanes 0–3, so the link trains x4 | [Proposal] |
| Downstream | 4 × x4. 220 nF on the switch TX next to the switch. M.2 naming: **PET = module TX → switch RX**; **PER = module RX ← switch TX** | [Sourced: M.2 spec pinout] |
| Lane/polarity | Polarity inversion is mandatory in PCIe. Lane reversal is supported on most switches [Unverified for the ASM2824]. Route without reversal in rev A | |
| REFCLK | Host REFCLK0 (100 MHz HCSL, common clock, free-running) → switch. The switch's internal buffer drives the 4 M.2 REFCLKs. SRIS is supported if the host clock ever proves bad. A 25 MHz crystal footprint (Y1) is fitted **only if the datasheet needs it** | [Sourced: OSHWHub; SRIS from the ASMedia product page] |
| PERST# | Host PERST0# → U12 (open drain, gated by PG_ALL) → switch PERST#. Host PERST0# → U9/U10 (74LVC2G07, open drain) → SSD0–3 PERST#, with 10k pull-ups to 3V3_SSD. The SSDs never see PERST# released before 3V3_SSD is good | [Proposal] |
| CLKREQ# | SSD CLKREQ# pulled up (10k), clocks always running. Host CLKREQ0#: not driven (DNP 0R to GND, per spec clk_flags.bit2) | [Proposal] |
| PCIe SMBus (A8/A9) | Not connected in rev A. The M.2 SMBus is **1.8 V**, and all 4 NVMe-MI endpoints share 0x6A, so it would need a level shifter plus a PCA9546-class mux. That can be a later option | [Sourced: M.2 1.8 V SMBus] |
| WAKE0#, PEWAKE#, SUSCLK, DEVSLP, PEDET, ALERT# | NC | |
| Activity | Each SSD's DAS/DSS# → its own LED (D1–D4, 1k to 3V3_SSD). Wired-OR through BAT54A (D6/D7) → MOD_LED# (OD, ≤ 5 mA). D5 = 3V3_SSD power LED | [Proposal] |
| Management | AUX SMBus (3V3_AUX): EEPROM 0x50 (WP strapped high, DNP 0R to program), TMP1075 0x48 → THERM_ALERT#, TMP1075 0x49 → THERM_TRIP#. FACE_PRSNT# tied to GND. FACE_PWR_EN has a 100k pull-down. eFuse FLT# → FACE_SMB_ALERT#. **ICD rev 2:** U13 **INA228** at **0x40** (mandatory > 3 W, face spec §6.8) across R520 2 mΩ 2512 (+12V_PROT → +12V_PROT_S, ahead of U2); ALERT (OD) also → FACE_SMB_ALERT#; C520 100 nF | [Sourced: spec §5, §8] |
| Switch config | SPI NOR (U8). Size and image come from ASMedia (TBD, NDA). Footprint SOIC-8 | TBD |

### 4.3 Rails

| Rail | Source | Load | Notes |
|---|---|---|---|
| +12V_IN | Both lug sites in parallel (spec) | ≤ 3.5 A | Reverse polarity: **LM74700-Q1 + 30 V N-FET** (≤ 5 mΩ; ≈ 60 mW at 3.5 A). ≤ 47 µF ahead of the eFuse (10 µF fitted) |
| +12V_SW | **TPS259824ONRGER** eFuse (C2155766) | I_LIM ≈ 5 A (60 W) | Inrush ≤ 1 A via dVdt. EN = FACE_PWR_EN. PG → enables U4 |
| **3V3_SSD** | **TPS56C215RNNR** (C473372), 12 A, D-CAP3, 1.0 µH 10 × 10 inductor (I_sat ≥ 15 A) | 4 × 2.5 A (M.2 max) + switch 3.3 V I/O (≈ 0.3 A [Estimate]) ≈ **10.3 A peak**, ≈ 6–8 A sustained | ≈ 92 % at 8 A [Estimate]. 6 × 47 µF at the buck, 2 × 22 µF at each socket. Distribution on the L4 plane plus B-side pours. The M.2 tolerance is ±5 % |
| VDD_CORE | **TLV62585** 3 A buck from 3V3_SSD (placeholder) | ≈ 2–3 A [Estimate] | **Voltage and any extra analog rails (e.g. 1.8 V / PHY) come from the ASM2824 datasheet (TBD).** Rename the symbol pin VDDA(TBD) accordingly |
| 3V3_AUX | From the BP (AUX pins 1–2) | EEPROM + 2 sensors ≈ 1 mA | S5-safe |

**Sequencing:** FACE_PWR_EN → eFuse → EFUSE_PG → 3V3 buck → PG_3V3 → core buck → PG_ALL → FACE_PWR_GOOD (open drain, < 150 ms total) → host releases PERST0# → switch and SSDs out of reset.

### 4.3.1 Live power target (ICD rev 2) [Proposal]

SM-1 has no MCU, so it is **telemetry-only** for the system 445 W loop (spec §5.5): the BP MCU reads U13 (V, I, P, energy) over FACE_S_SMB every 100 ms and sets the INA228 power-over-limit alert to the Face S allocation + 10 %. To reduce storage power, the BP asks the macOS helper (vendor HID) to lower each SSD's **NVMe power state** (Set Features FID 02h). THERM_ALERT# stays the fast hardware path. No power-target agent at 0x58 is fitted.

### 4.4 Power budget (12 V input, Face S slot max 40 W, Class 1)

| Load | Peak (≤ 10 ms) | Worst sustained (1 s avg) | Typical (uplink-bound) |
|---|---|---|---|
| 4 × M.2 NVMe (3.3 V × 2.5 A max each) | 33.0 W | 4 × 7 W = 28 W (Gen3 drives at max write) | 4 × 3–4 W = 12–16 W |
| ASM2824 (incl. VDD_CORE conversion) | 5 W | 4.5 W | 3–4 W |
| Sensors, EEPROM, LEDs, buffers | 0.2 W | 0.2 W | 0.1 W |
| 3V3 buck loss (≈ 92 %) | 3.2 W | 2.8 W | 1.4 W |
| eFuse + reverse FET | 0.2 W | 0.1 W | 0.05 W |
| **Total at 12 V** | **≈ 41.5 W** | **≈ 35.6 W** | **≈ 17–22 W** |
| Limit | 1.3 × 40 = **52 W** ✓ | **40 W** ✓ | |

- **Declare** `p_sustained_w = 40` and Class 1.
- The Gen3 x4 uplink (≈ 3.5 GB/s) makes the worst sustained case hard to reach. Four drives writing at full power for > 1 s while sharing 3.5 GB/s is possible only with internal garbage collection.
- Gen4 SSDs at their 8–10 W peaks would exceed the M.2 3.3 V × 2.5 A limit only if the drive violates the M.2 spec. Prefer Gen3 or efficient Gen4 drives (≤ 7 W).

### 4.5 Stackup and routing rules

- **6 layers, JLC06161H-2116** (template):
  - L1 (F) switch fan-out
  - L2 GND
  - L3 inner signals (stripline PCIe where needed)
  - L4 3V3_SSD / 12 V planes
  - L5 GND
  - L6 (B) MCIO and M.2 pads plus microstrip
- PCIe is Gen3 8 GT/s. Netclass PCIE_85R (start values; check with the JLC impedance calculator).
- Budget ≤ 2 vias per lane. ASM2824 → socket runs are ≈ 40–65 mm, well inside the Gen3 loss budget.
- **4-layer option** (D5): the OSHWHub card proves 4 layers can work. It needs both outer layers referenced to solid planes, which makes the 10 A 3V3 distribution harder. Evaluate it once the ball map is known.
- **BGA:** the 0.8 mm pitch is **assumed** (the placeholder is a 25 × 25 grid minus 133 balls). If it is real, it fans out with 0.3/0.15 vias without via-in-pad; JLC's 0.3 mm via is a standard process. X-ray inspection is required (JLC does it for BGA).

---

## 5. KiCad project (`kicad/macpro62-storage-face/`)

| File | What |
|---|---|
| `macpro62-storage-face.kicad_pro/.kicad_pcb/.kicad_sch` | Project. **The PCB is a floorplan:** outline, holes, stackup, rule areas, every major part placed, lug reference tracks. DRC: **0 violations, 0 unconnected**. The schematic covers every part with label connectivity. ERC: **0 / 0** |
| `MP62_Storage.kicad_sym` | Custom symbols. **Real pinouts:** M.2 Socket 3 M-key (67 contacts), MCIO 124 module end (from the spec CSV), GH15 AUX, BL24C64A, TMP1075 DSG, 74LVC2G07, SPI NOR, LM74700 DBV. **Logical pin numbering** (verify against the datasheet): ASM2824, TPS259824, TPS56C215, TLV62585 |
| `MP62_Storage.pretty` | Footprints. **PLACEHOLDERS:** M.2 socket (generic 0.5 mm pitch rows), ASM2824 BGA-492, TPS56C215 RNN. The rest are KiCad stock copies |
| `MP62_Face.pretty` | Template footprints (MCIO, GH15, lug, mount hole) |
| `tools/make_storage_fps.py`, `tools/make_footprints.py`, `tools/build_storage.py`, `tools/postprocess.py`, `tools/build_sch.py`, `tools/floorplan.py` | Generators. Rebuild order in README |
| `render_outer_side_B.png`, `render_core_side_F.png`, `floorplan_storage_SM1.png`, `schematic_overview.png` | Views |
| `drc_report.txt`, `erc_report.txt` | Reports |

**Not done yet:**
- PCB nets (the PCB carries only the lug nets, so the schematic and PCB are not linked)
- placement of ≈ 120 small passives (48 AC caps, decoupling, pull-ups)
- routing, copper pours, thermal vias, fab outputs

These follow once the ASM2824 ball map and the LOTES drawing are in hand.

---

## 6. BOM (per board) [prices LCSC 2026-10-01 where an LCSC number is given; otherwise Estimate]

| Ref | Part | LCSC / source | Qty | Unit | Ext |
|---|---|---|---|---|---|
| U1 | ASMedia ASM2824 LFBGA-492 | JLC C9900092023 (price TBD) | 1 | **$15–40 [Unverified]** | $15–40 |
| J1 | Amphenol G97R24332HR MCIO 124 RA | C4867471 (**0 stock**: consign or global-source) | 1 | $9.59 | $9.59 |
| J5–J8 | LOTES APCI0107-P001A M.2 M-key H4.2 | C841661 | 4 | ≈ $0.6 [Estimate] | $2.40 |
| MH×80 | SMT M2 standoff (H4.2 height TBD) | YIYUAN family (C5301773 = 2.5 mm) | 4 (+10 DNP pads) | ≈ $0.15 | $0.60 |
| J3 | JST SM15B-GHS-TB | C265027 | 1 | $0.87 | $0.87 |
| U2 | TI TPS259824ONRGER | C2155766 | 1 | $5.90 | $5.90 |
| U3 + Q1 | TI LM74700-Q1 + 30 V N-FET 5 × 6 | TBD at order | 1 + 1 | ≈ $0.8 + $0.4 | $1.20 |
| U4 | TI TPS56C215RNNR | **C473372** | 1 | $1.06 | $1.06 |
| L1 | 1.0 µH, I_sat ≥ 15 A, 10 × 10 | TBD | 1 | ≈ $0.6 | $0.60 |
| U5 + L2 | TLV62585DRL + 0.47 µH 2520 (rail TBD) | TBD | 1 + 1 | ≈ $0.4 + $0.05 | $0.45 |
| U6 | BL24C64A-SFRC | C111004 | 1 | $0.19 | $0.19 |
| U7, U11 | TI TMP1075DSGR | C2870250 | 2 | $0.50 | $1.00 |
| U13 + R520 | TI INA228AIDGSR (VSSOP-10) + 2 mΩ 2512 shunt (ICD rev 2) | LCSC TBD [Unverified] | 1 + 1 | ≈ $3.5 + $0.2 [Estimate] | $3.70 |
| U9, U10, U12 | 74LVC2G07 (SC-70-6) | TBD (basic/extended) | 3 | ≈ $0.10 | $0.30 |
| U8 | SPI NOR 25Q (size TBD) | TBD | 1 | ≈ $0.25 | $0.25 |
| Y1 | 25 MHz 3225 (only if required) | TBD | 0–1 | ≈ $0.10 | $0.10 |
| D1–D5, D6–D7 | LED 0603 × 5, BAT54A × 2 | basic parts | 7 | ≈ $0.02 | $0.14 |
| C/R | ≈ 150 passives: 48 × 220 nF, 6 × 47 µF, 8 × 22 µF 0805, 4 × 22 µF 1206 25 V, decoupling, pull-ups | basic parts | ≈ 150 | — | ≈ $2–4 |
| — | 3.0 mm soft gap pad ≈ 25 × 25 (not JLC; buy separately) | — | 1 | $3–8 | $3–8 |
| **Total per board** | | | | | **≈ $49–84** (≈ $46–76 assembled by JLC + gap pad; +$3.7 for U13/R520, ICD rev 2) |

**Interface kit** (connectors, eFuse, EEPROM, sensor) ≈ $17, matching spec §15.

## 7. Cost: 5 PCBs, 2 assembled at JLC [Estimate; instant quote needed]

| Item | Cost | Basis |
|---|---|---|
| PCB, 6 layers, 104 × 166 mm, 1.6 mm, ENIG, impedance control, 5 pcs | $70–140 | JLC 6-layer pricing scaled by area (≈ 1.7 × 100 × 100) [Estimate] |
| PCBA, 2 boards, **double-sided** (BGA on F; sockets and power on B): setup + stencil × 2 sides, BGA X-ray, ≈ 20 extended parts × $3 loading fee | $110–200 | JLC fee schedule [Estimate] |
| Parts for 2 boards (§6, without the gap pad), plus JLC attrition | $90–160 | §6 |
| MCIO 124 RA sourcing (0 at LCSC: global sourcing or consigned) | $0–30 extra | |
| Shipping, duties | $40–70 | [Estimate] |
| **Total, 5 PCBs / 2 assembled** | **≈ $330–600** | Excludes SSDs, the MCIO 16i cable (≈ $60–80, custom length, spec C-9) and gap pads |
| Assemble the other 3 later | ≈ $45–80 parts + ≈ $60 fees per batch | |

---

## 8. RAID

### 8.1 What "bootable RAID on macOS" requires

- macOS boots only from a volume that its **built-in drivers** can see and that the firmware boot path (Apple EFI, or OpenCore/UEFI NVMe on MP62) can read.
- A hardware RAID would therefore have to present itself as **one plain NVMe controller (class 01-08-02) or one AHCI disk**, with no vendor kext.
- **Apple software RAID cannot boot on current macOS.** Booting from AppleRAID or SoftRAID volumes ended with APFS/Big Sur. Workarounds existed up to Mojave. RAID still works fine for **data** volumes [Sourced: SoftRAID/OWC notes, earlier research].

### 8.2 Candidate RAID-on-chip parts

| Candidate | How it presents itself | macOS without a driver? | Bootable on macOS? | Availability / price | Power | Fit on SM-1 | Verdict |
|---|---|---|---|---|---|---|---|
| **Marvell 88NR2241(-B)** NVMe RAID accelerator (Gen3 x8 up, up to 4 NVMe SSDs; RAID 0/1/10/JBOD) | **One standard NVMe virtual drive, inbox drivers** [Sourced: Marvell PR; used in HPE NS204i-p, Dell BOSS-N1, HighPoint SSD6202A/SSD6204A "driverless, bootable"] | **In principle** (standard NVMe class). **Not verified**: HighPoint, HPE and Dell list Windows/Linux/VMware/FreeBSD only, never macOS. macOS's NVMe driver has quirks with non-Apple controllers | Unverified. Array creation and repair need Marvell's CLI/UEFI HII, with no macOS tool. A degraded array would be invisible in macOS | **NDA-only** (Marvell extranet), not at LCSC or distributors, licensed firmware. **Not orderable for JLC turnkey** | Not published (≈ 5–8 W [Estimate]) | Would replace U1 on the die pad (x8 up / 4 × x4 down, the same topology). Different ball map, so a different PCB | **Only real candidate, but not available.** At most a future variant **SM-1R** |
| Broadcom SAS3916 / SAS4016 tri-mode (MegaRAID 9560/9600) | MegaRAID RAID controller | **No**: needs the megaraid driver; no macOS driver | No | Brokers, $100–300+, NDA | 10–20 W | No | Not viable |
| HighPoint SSD7101A / SSD7505 class (PLX/Broadcom switch + HighPoint RAID driver) | Switch + vendor driver | **No**: HighPoint kext on Intel macOS 10.13–13 | **RAID not bootable.** Booting from a single non-RAID SSD up to 10.15 | Cards only, not a chip | — | — | Not viable |
| JMicron JMB394 (SATA 3G, 1 to 5 ports, hardware RAID 0/1/3/5/10) | One SATA disk behind AHCI | Yes (AHCI is native) | **Plausible**, because it sits behind a plain AHCI port | Brokers only; old part; needs an AHCI controller plus SATA SSDs | ≈ 1 W | Would need a separate SATA path. ≈ 300 MB/s (3G) | Technically bootable, but **slow and obsolete**. Not recommended |
| Marvell 88SE9230 (PCIe Gen2 x2 → 4 SATA, HyperDuo/RAID) | AHCI in JBOD mode; RAID mode changes the class and needs a driver | AHCI/JBOD only (forum reports) | **RAID: no** | LCSC/brokers | ≈ 1 W | SATA | Not viable for RAID boot |
| ASM2824 (this board) | A plain switch: 4 separate native NVMe drives | Yes | **Each SSD is bootable individually** (the Sonnet M.2 4x4, a PLX-switch card, is officially bootable from a single SSD on Mac Pro 7,1/5,1; on MP62 the OpenCore/Dasharo NVMe driver sees each drive behind the bridge) | ✓ | 3–5 W | ✓ | **Chosen** |

### 8.3 What is bootable on the plain switch board

| Setup | Bootable? | Notes |
|---|---|---|
| Single APFS SSD behind the ASM2824 | **Yes** [Inference; Sonnet 4x4 precedent, standard NVMe behind a PCIe bridge] | Needs the MP62 firmware (OpenCore/EDK2) NVMe driver to enumerate behind the bridge, which EDK2 does. Confirm on the first board (test T-S3) |
| AppleRAID (Disk Utility, RAID 0/1/JBOD) across SSD1–SSD3 | **No** (data only) | Built-in, free. Survives OS reinstalls |
| SoftRAID (OWC, RAID 0/1/4/5/10, monitoring) | **No** (data only on Big Sur and later) | ≈ $80–180 licence [Estimate]. Better health monitoring than AppleRAID |
| APFS container spanning drives | Not supported (APFS has no spanning; Fusion is HDD + SSD only) | — |
| Boot redundancy | Clone the boot SSD (Carbon Copy Cloner / SuperDuper) to a second SSD; select it in the boot picker if the first fails | The practical stand-in for RAID 1 boot |

**Recommended configuration:** SSD0 = boot (APFS). SSD1–SSD3 = one SoftRAID or AppleRAID set (RAID 0 for speed, or RAID 5/10 with SoftRAID for redundancy). Optionally keep a nightly clone of SSD0. The CPU board's own M.2 can be the boot drive instead, which frees all four Face S slots for the array.

### 8.4 Design decision

- **No hardware RAID in rev A.** The base board carries no RAID-related part or cost.
- **SM-1R variant (future, only if Marvell or HighPoint will supply parts and firmware):**
  - same outline, sockets, power band and AUX/EEPROM
  - U1 replaced by the 88NR2241 (Gen3 x8 up / 4 × x4 down, so the same lane topology and the same J1 x8 wiring)
  - new BGA land pattern, firmware SPI flash and power rails per Marvell
  - the EEPROM `module_type` stays storage, with a RAID flag
- **SM-1R needs a cheap feasibility test first:** a used **HPE NS204i-p** (88NR2241 RAID 1, two M.2 22110) in a Thunderbolt PCIe enclosure on an Intel Mac. If macOS mounts and boots its virtual NVMe drive, SM-1R is worth pursuing [Proposal; untested].
- The base board cannot hold a populate-option footprint for both chips, because the two BGAs differ and share the die pad.

---

## 9. Risks

| ID | Risk | Level | Mitigation |
|---|---|---|---|
| R-S1 | **ASM2824 datasheet, ball map, firmware and SPI image are NDA/unpublished** | **High** | Ask ASMedia (or the JLC/LCSC FAE) for the datasheet and reference design. The OSHWHub card's EasyEDA project (CC BY-NC-SA) shows a working ball-out to cross-check. Don't route until we have it |
| R-S2 | ASM2824 price and stock (the JLC part shows no price; "prices skyrocketed") | Medium | Check C9900092023 at order time. The ASM2812 is pin-compatible as a fallback (2 × x4 or 4 × x2) |
| R-S3 | MCIO 124 RA at 0 stock | Medium | Spec C-8: global sourcing or consign; allow equivalents |
| R-S4 | Outer-gap airflow too weak for 4 SSDs | Medium | Heatsinks; MF-14 test; SSDs self-throttle; prefer efficient drives |
| R-S5 | Screw heads collide with SSD0/SSD2 | Low (D4 resolved) | Low-head screws, head + washer ≤ 1.6 mm (§3.3); part number after MF-13 |
| R-S6 | Placeholder land patterns (M.2, BGA, RNN) | Medium | Replace from the LOTES / ASMedia / TI drawings before routing (DRC is meaningless until then) |
| R-S7 | macOS / firmware booting behind the switch | Low–Medium | Sonnet precedent; test T-S3 |
| R-S8 | THERM_ALERT# throttle rule cannot be met by a module without an MCU (C-21) | Low | The host applies NVMe power states. Spec change proposed |
| R-S9 | Gap tolerance (G 4.5 ± 0.5) vs the switch gap pad | Low | Soft 3.0/3.5 mm pads; choose after G is measured |

## 10. Open questions and measurements for Aidan

| ID | Item | Why |
|---|---|---|
| ~~MF-4~~ | ~~Bracket height~~ | **Not needed for SM-1** (D1 approved: no bracket) |
| **MF-13 (new)** | Stock screw thread (M3? pitch), length, and bracket eyelet thickness | Picks the low-head screw part number and length (D4, §3.3) |
| **MF-14 (new)** | Air temperature/flow in the board-to-shell gap: thermocouple on a dummy SSD during a 10 min load | SSD cooling (C-20) |
| **M1c** | Base-board standoff spacing (C-16) | No SM-1 impact. The J1 position follows the spec. Nothing locked here depends on C-16 |
| **M2c** | Face angle (C-18) | **Answered ≈ 45° (Aidan 2026-10-02).** No SM-1 impact: the module frame is face-relative. The BP J10 moved (fp5) and the Face S cable jogs 10.5 mm (face spec §3.6; ICD O-6) |
| **M5 / M5b** | Lug polarity / site per face | Both sites are fitted |
| G | Core gap per unit (±0.05) | Gap-pad thickness |
| **ICD O-1 (2026-10-02)** | BP J10 cannot move to s = +8.5 (G1 hole keep-out); it sits at s = −5.0, so the SM-1 J1 (X 43.5) cable needs a **13.5 mm lateral jog** | Cable choice/length (M4, C-9). No SM-1 change unless the spec moves J_PCIE (`macpro62-interface-control.md`) |
| OQ-7 | Will a future host give Face S x8? | Already wired on the module |
| OQ-S1 | ASM2824 datasheet access (ASMedia FAE / JLC) | R-S1 |
| OQ-S2 | Which SSDs? Single-sided Gen3/Gen4 ≤ 7 W preferred | Thermal and power |
| OQ-S3 | Boot drive on Face S or on the CPU-board M.2? | RAID layout (§8.3) |

## 11. Test plan (first 2 boards)

- **T-S1 power:** reverse-polarity test at the lugs (current-limited supply), eFuse inrush ≤ 1 A, rails, PG timing ≤ 150 ms.
- **T-S2 link:** on the bench host (Z790 desktop + MCIO adapter, or the real BP): x4 Gen3 training, 4 SSDs enumerated, `lspci -vv` link status, fio on each and on all four.
- **T-S3 macOS:** each SSD visible; boot from SSD0; SoftRAID/AppleRAID set on SSD1–SSD3; 10 min write while logging SSD temperatures (MF-14) and the 12 V input power (≤ 40 W).
- **T-S4 thermal:** switch temperature through TMP1075 0x48; THERM_TRIP# behaviour at 80 °C (heat gun on U11).

## 12. Sources (checked 2026-10-01)

- ASMedia ASM2824 product page (24 lanes / 12 ports, SRIS); PCI-SIG integrators list.
- OSHWHub "ASM2824 PCIE转M.2扩展卡" (wesd, CC BY-NC-SA 4.0): built-in clock buffer, 4 layers enough, passive cooling, ASM2812/1824/1812 compatible (ASM2812 lanes up 4–7 / down 8–15 unavailable).
- JLCPCB part C9900092023 (ASM2824/ASmedia); LCSC C20612120.
- LCSC C473372 TPS56C215RNNR ($1.06; 360–2,406 stock); TI TPS56C215 datasheet (3.8–17 V, 12 A).
- LCSC C841661 / C841651 LOTES M.2 sockets; C5301773 YIYUAN standoff.
- Marvell 88NR2241 press release and HPE NS204i-p blog ("native NVMe RAID", inbox drivers); Dell BOSS-N1 user guide (inbox NVMe drivers); HighPoint SSD6202A/SSD6204A pages.
- HighPoint SSD7000-series macOS driver notes; Sonnet M.2 4x4 bootability notes; SoftRAID/OWC on RAID boot (Big Sur and later).
- Microchip PM40028 and Broadcom PEX88024 distributor listings.
- MP62-FACE v0.1 spec (§3–§6, §10, §11.3, §13–§15) and pinout CSVs; CPU board plan §1.2.
