# MacPro6,2 — own LGA1700 CPU board ("CB"): feasibility study and plan

Version fl1, 2026-10-01 (~18:00 ET). Status: **[Proposal]**. Tags are the same as in the spec: [Sourced] with a link, [Estimate], [Inference], [Unverified], TBD.

**Decision (Aidan, 2026-10-01 ~17:30 ET):** skip the COM-HPC module. The first CPU board is our own LGA1700 socket board (the former stretch goal P6, spec §6.8). The COM-HPC carrier (`/workspace/kicad/macpro62-cpu-carrier/`) stays as an **archived fallback**. It is not deleted.

Deliverables:
- this plan;
- the KiCad floorplan `/workspace/kicad/macpro62-lga1700/` (DRC 0, `floorplan.png`);
- spec v0.2 changelog item 17 and §6 / §10 / §11 updates;
- the zip `/workspace/macpro62-lga1700.zip`.

---

## 0. Summary

| Topic | Recommendation | Confidence |
|---|---|---|
| Chipset | **Z790** (FH82Z790, SRM8P). It matches the Dasharo MSI PRO Z790-P reference exactly: same PCH SKU, FSP, ME image and soft-strap layout. B760 is a pin-compatible cost-down (same 700-series ballout). W680 only if ECC is a must. | medium |
| Lane budget | CPU PEG x16 → Face P; CPU x4 Gen4 → Face S; PCH Gen4 x4 → M.2 boot; PCH x1 → i226-V; PCH x4 reserved → AQC107; PCH USB3 ×4 + USB2 ×4 → IOB; SATA0 + 4 × USB2 → CPU-LINK. Fits Z790 and B760. | high |
| Firmware | **coreboot + Dasharo** (upstream `msi/ms7d25` port as the template). Public RPL-S FSP. ME = CSME 16.1 Consumer region built with MFIT, HAP bit set. EDK2 (Dasharo UefiPayloadPkg) payload. OpenCore is first loaded from the BP SATA SSD (rev A); embedding it in the payload FV is the stretch goal. | medium (ME/FIT legal grey area) |
| EC | **RP2350 on the CB** as a GPIO "EC": power sequencing, PWRBTN#, RSMRST#, PWROKs, fan/thermal, SMBus. No SuperIO, no eSPI device. Console on the PCH UART. | medium |
| VRM | **RT3628AE** (LCSC C3249940) with **6 + 1 phases**: 7 × Vishay SiC654 50 A plus 2 for VCCIN_AUX, and Eaton FP4 0.15 µH 5.0 mm inductors. All on the front, ≤ 6.0 mm, and thermally padded to the core plate. | medium (controller config tools are NDA) |
| Memory | **2 × DDR5 SO-DIMM** (UMAX 90415-4015SR, 4.0 mm), one per channel, **on the back in the stock DIMM strips**. That zone has proven Z room toward the PSU. | medium-high |
| PCB | **JLC 10-layer, 1.6 mm, ENIG + hard-gold bevelled fingers, POFV via-in-pad, impedance control** | high (capability); PCH 0.5 mm fan-out is the tight spot |
| Socket | **Foxconn PE17007-11NK0-1H**, LCSC C38520273, $5.79 @ 1, 32 in stock (2026-10-01) | high |
| iGPU | **Enabled** (UHD 770): DDI-1 native DP + DDI-2 into the IOB USB-C DP-alt mux. Bring-up and fallback for Windows/Linux only. **macOS cannot use it at all** (§7). | high |
| Rev-A cost | **≈ $1.5k–2.6k** for 5 PCBs and 2 assembled; **≈ $2.6k–4.4k** for 5 assembled. CPU, RAM and SSD extra; plan on a rev B. [Estimate] | low-medium |
| Go/no-go | **GO for a de-risking phase P6-0** (≈ 3–6 weeks, ≈ $400–900). **CONDITIONAL GO** for the rev-A order at gate G-A. | — |

---

## 1. Chipset (PCH)

### 1.1 SKU comparison [Sourced: Intel 700-series PCH datasheet vol. 1, 743835-004, SKU table]

| | B760 | H770 | Z790 | W680 (600-series) |
|---|---|---|---|---|
| DMI 4.0 | x4 | x8 | x8 | x8 |
| PCIe Gen4 / Gen3 | 10 / 4 | 16 / 8 | 20 / 8 | TBD (600-series datasheet not checked) |
| SATA 6 Gb/s | 4 | 8 | 8 | 8 |
| USB2 / 5G / 10G / 20G | 12 / 6 / 4 / 2 | 14 / 8 / 4 / 2 | 14 / 10 / 10 / 5 | TBD |
| CPU PEG bifurcation (x8/x8) | no | yes | yes | yes |
| CSME | 16 Consumer | 16 Consumer | 16 Consumer | 16 **Corporate** |
| ECC (with 12th–14th gen Core) | no | no | no | **yes** |
| Intel RCP | **$31** [N86] | TBD | **$57** [N87] | **$56** [N88] |
| Package | FCBGA 28 × 25 (all 700-series share one ballout, 1045 balls) | ← | ← | 600-series ballout (TBD, likely the same body) |

### 1.2 Our needs vs the budget

| Need | Source | Lanes | B760 | Z790 |
|---|---|---|---|---|
| Face P GPU x16 | CPU PEG Gen5 (lanes 16–31 on CPU-LINK, Gen4 by policy) | 16 (CPU) | ✓ | ✓ |
| Face S x4 | **CPU Gen4 x4** (CPU-LINK lanes 12–15) | 4 (CPU) | ✓ | ✓ |
| M.2 boot NVMe | PCH Gen4 x4 | 4 | ✓ | ✓ |
| i226-V 2.5GbE | PCH Gen3 x1 | 1 | ✓ | ✓ |
| AQC107 10GbE (later) | PCH Gen3/4 x4 | 4 | ✓ (9 of 14) | ✓ (9 of 28) |
| SATA0 to the BP (OpenCore SSD) | PCH SATA | 1 | ✓ | ✓ |
| USB to the IOB | PCH USB3 ×4 + USB2 ×4 | — | ✓ | ✓ |
| USB2 on CPU-LINK (BP MCU, Face P, Face S, spare) | PCH USB2 ×4 | — | ✓ (8 + EC = 9 of 12) | ✓ |
| Audio | **USB audio on the IOB** (rev-A default, CM6646). An HDA codec (Realtek ALC897-VA2-CG, LCSC C5884442) is a DNP option. | HDA link | ✓ | ✓ |
| Display | CPU DDI (§7) | — | ✓ | ✓ |

- **Both B760 and Z790 meet the requirement.** B760 has two penalties:
  - DMI x4 (≈ 7.9 GB/s) is shared by NVMe, 10GbE and USB. That is acceptable for this machine.
  - No CPU x8/x8 split. We don't need one, because the BP would split lanes if a future face needs x8/x8 (spec §2.4).
- **Recommendation: Z790.**
  - The firmware reference (Dasharo MSI PRO Z790-P, MS-7E06) and the upstream coreboot port (MSI PRO Z690-A, MS-7D25) both use Z-class PCH SKUs.
  - With the same SKU we can reuse the vendor ME region and descriptor layout and the FSP/HSIO configuration with the fewest changes (§2.3).
  - B760 is pin-compatible (same ballout), so it is a later BOM swap, not a redesign.
- **W680 / ECC:**
  - Only W680 enables ECC with Core i5/i7/i9 12th–14th gen. The ASRock Rack W680 WS lists the i5-14500T [N89].
  - Costs: CSME **Corporate** (a different ME image and a different Dasharo baseline; no W680 Dasharo reference found), **no loose-chip source found**, and ECC SO-DIMMs.
  - Recommendation: **no ECC in rev A** (decision D2).
- **HSIO / Flex-I/O lane muxing** (which PCH HSIO lanes are PCIe vs USB3 vs SATA) is set by the PCH soft straps. The rule: **use the PCH lanes the same way the MSI PRO Z790-P does** (its M.2_x slot for the boot SSD, its LAN lane for the i226-V, an x4 slot group for the AQC107). Then the Z790-P descriptor straps can be reused ([Inference]; map the lanes from the coreboot `ms7d25` devicetree and the board manual before layout).

### 1.3 Sourcing loose PCHs (honest status)

| Part | Listing | Price | Remark |
|---|---|---|---|
| Z790 FH82Z790 SRM8P | afromanshop.lt, milpood.ee [N90] | **€45–48** | Generic "new original" re-seller pages, most likely mirror listings of Chinese brokers. **Authenticity unverified.** |
| Z790 | Taobao listing via taouq [N90] | ¥140 (≈ $20) | Suspiciously cheap: likely pulled/reballed. |
| B760 FH82B760 SRM8V | oknabytok.sk / Israeli mirror shops [N91], itdevices.ca [N91] | €41.75–44.41, CAD 40.64 | Same caveat |
| W680 FH82W680 | — | — | Not found loose |
| LCSC / Mouser / Digi-Key | — | — | **Not stocked** (Intel sells chipsets only to OEMs/ODMs). |

- **Risk: pulled or fused parts.** A PCH pulled from a production board may have had its **Field Programmable Fuses (Boot Guard, ME manufacturing state) burned** by the OEM. Such a part may refuse our unsigned firmware.
  - Buy only **new, sealed tray/tape** parts.
  - Buy **5 + 3 spares** from **two** sellers. Check the markings and the X-ray, and keep a known-good test path (§10, G2).
  - Never "close manufacturing" (EOM) during bring-up [Inference from CSME FPF behaviour].
- **Fallback if sourcing fails:** sacrifice a used MSI PRO Z790-P/Z690-A as a PCH donor and have it professionally reballed. That inherits the same fuse risk, but MSI does not fuse Boot Guard on the Dasharo-supported boards (Dasharo flashes them) [Inference].

### 1.4 JLC assembly of a customer-supplied BGA PCH

- **Ball pitch:** min **0.5005 mm**, typical neighbour **0.565 mm** (staggered). 1045 balls, 359 GND, field ±13.34 × ±11.84 mm [Sourced: ballout xlsx, N84].
- **JLC standard PCBA** supports BGA down to **0.35 mm** pitch [N92]. **Customer parts:** JLC accepts consigned parts shipped to its warehouse [N93][N94].
  - The PCH ships as a moisture-sensitive tray part, so ask JLC for baking.
  - Expect JLC not to guarantee the yield of consigned parts [Unverified].
- **Socket:** JLC stocks LCSC parts, so the Foxconn socket can be a normal "extended" part (LCSC C38520273).
- **Rework:** JLC does not offer BGA rework of returned boards [Inference: not on their service list]. Plan on a local BGA rework service (≈ $50–150 per chip [Estimate]) and **spare PCHs**. The socket has 1700 solder balls, and JLC's X-ray inspection covers both BGAs (ask for the X-ray report).

### 1.5 Public reference material (Intel PDG/CRB need a CNDA)

| What | Status | Use |
|---|---|---|
| **PCH 700 datasheet vol 1** (743835) + ballout / GPIO / electrical xlsx attachments | **Public** [N84] | Footprint (done), rails and Icc (e.g. VCCPRIM_CORE 0.82 V 11.2 A S0), power-sequencing signal list, GPIO tables |
| **CPU 13/14th gen datasheet vol 1** (743844) + S-LGA ballout xlsx | **Public** [N85] | Land pattern (done), rails, IccMax, DDI/PCIe/DDR features |
| **Intel PDG** (platform design guide), **CRB schematics**, IMVP 9.1 VR spec, TMSDG, EDS vol 2 | **CNDA only** | Not available to us; we design from datasheets plus reverse references |
| **coreboot `msi/ms7d25`** (MSI PRO Z690-A, DDR4 and DDR5 variants), upstream | **Public** [N95] | devicetree (PCIe root-port → slot map, CLKSRC), **gpio.c (full board GPIO/pad config)**, memory SPD/topology settings, SuperIO usage (NCT6687D). This is the best public "schematic substitute". |
| **Dasharo docs** for MSI Z690-A / Z790-P [N96] | Public | Feature status, ME handling (HAP), build components (coreboot 25.12, edk2-stable202602, FSP RPL-S C.0.C8.50, ME 16.1.30.2307) |
| **Intel FSP** RaptorLakeFspBinPkg (Client / RaptorLakeS) + integration guide | **Public, redistributable binary** [N97] | Memory init (FSP-M), silicon init (FSP-S), UPD list |
| **MSI MS-7D25 / MS-7E06 boardviews / schematics** | Circulate on repair forums (badcaps etc.) [N98] | **Unauthorised, copyright MSI.** Use only privately as a reading aid (VR topology, strap resistors, sequencing). Do not copy, publish or redistribute; do not put them in the repo. |
| Open LGA1700 boards | None found (no open-hardware LGA1700 board with public schematics) | — |

---

## 2. Firmware

### 2.1 Chain

`RP2350 EC sequencing` → `PCH CSME 16.1 (HAP)` → `coreboot (Dasharo fork, new mainboard "mp62/cb")` → `FSP-M/FSP-S (RPL-S public binary)` → `EDK2 payload (Dasharo UefiPayloadPkg)` → boot entry **"MP62 OpenCore"** → macOS Tahoe 26 / Windows / Linux.

- **Platform support:**
  - Alder Lake-S and Raptor Lake-S (12th–14th gen) run on Dasharo MSI PRO Z690-A **v1.1.7** and MSI PRO Z790-P **v0.9.5** (released 2026-08-13) [N96].
  - The Z690-A port is upstream in coreboot (CB:63463, DDR5 variant CB:68448) [N95].
  - Z790-P pre-built binaries are a Dasharo Pro Package item, but **the source is open**. We build from source.
- **Port path:**
  1. Copy `src/mainboard/msi/ms7d25`.
  2. Rewrite gpio.c from our schematic, rewrite the devicetree (root ports, CLKSRC, USB port map, DDI config, HDA off), drop the NCT6687D SuperIO, and add the RP2350 EC interface (GPIO/SMBus only).
  3. Set the memory topology to 2 × SO-DIMM 1DPC.
  4. Write a new VBT (§7.3) and a new ME/descriptor (§2.3).
- **First run on the real MSI board:** start with a used **MSI PRO Z690-A DDR5** (or Z790-P). Build Dasharo from source, add OpenCore, boot Tahoe, and only then change things for our board. That de-risks ~80 % of the firmware without our hardware (phase P6-0, §10).

### 2.2 FSP

- Public binary plus headers: intel/FSP `RaptorLakeFspBinPkg/Client/RaptorLakeS`. The AlderLake-S paths are symlinks to it [N97].
- License: redistribution of the binary is allowed (per the FSP license in the repo).
- Memory-init UPDs for SO-DIMM DDR5 1DPC exist on the client platforms; we use SPD from the modules.

### 2.3 Intel ME / CSME and the descriptor

- **Needed:**
  - a CSME **16.1 Consumer** firmware binary for the 700-series PCH;
  - the **Flash Image Tool (MFIT 16.1)**, to build the descriptor with our **soft straps** (HSIO lane muxing, SPI/eSPI config, GPIO strap defaults) and the ME region.
- **Availability:**
  - Intel distributes CSME kits only to OEMs under NDA.
  - CSME 16 firmware and MFIT 16.1.25.2091 are mirrored on the Win-Raid forum [N99]. **Not official; legal grey area** (for personal use only; we don't redistribute them).
  - The ME region and descriptor can also be extracted from the **public MSI BIOS update file** for the Z790-P/Z690-A (`ifdtool`/`me_cleaner` read them). The MSI image is licensed for MSI boards, so personal use only.
- **Strategy:**
  1. Lay out the PCH lanes like the Z790-P (§1.2), so its descriptor straps are close to right.
  2. Open it in MFIT, change only what differs, and set **HAP** (High Assurance Platform) like Dasharo does [N96].
  3. Optionally soft-disable/trim with `me_cleaner`. It reportedly still works on newer platforms [N100]; test it on the MSI board first.
- **Fuses / Boot Guard:** with new unfused PCHs, Boot Guard is off. **Never run FPF commit / End-of-Manufacturing.** Keep the PCH in manufacturing mode during development [Inference].
- **Flash:** 32 MB SPI NOR (W25Q256JV class) on SPI0, with a SOIC clip / Tag-Connect header for external programming. A **second SPI flash socket or dual-image** is a later option.

### 2.4 EC / SuperIO: the RP2350 as a GPIO EC [Proposal]

- **Desktop boards** use a SuperIO (NCT6687D on MS-7D25) for HWM/fan, sequencing helpers and the legacy UART. **No SuperIO is functionally required:**
  - The **RP2350** (QFN-60, LCSC C42411118, $1.299 per the spec BOM) on the CB, powered from 3V3_SB, drives and monitors:
    - DSW_PWROK, RSMRST#, PWRBTN#, SLP_S3# / SLP_S4# / SLP_S5# / SLP_SUS# (inputs);
    - PCH_PWROK, SYS_PWROK, VR enables, and the VR / eFuse PGOODs.
  - Timing per the public PCH datasheet power-sequencing section. The exact delays and margins are in the PDG, so add margin and measure on the MSI board ([Estimate]/TBD).
  - It also runs fans/thermal via SMBus or I²C, presents the CB ID EEPROM (0x57, mandatory per spec §6.7), and talks to the BP MCU (CPU-LINK sideband).
- **eSPI:** the RP2350 has **no eSPI target hardware**; a PIO eSPI is possible but unproven. We **don't use an eSPI device**: no eSPI EC, and the TPM is on SPI0 CS2#. Configure eSPI as unused in the soft straps / FSP [Inference; on the MSI reference board the SuperIO cannot be removed, so this is first tested on our rev-A board, with a footprint for an eSPI header kept as a fallback].
- **Console:** PCH LPSS UART (coreboot supports it on ADL/RPL) on the debug header. The POST code goes to the EC via a GPIO port or SMBus (optional).

### 2.5 OpenCore

- **Rev A (proven):** EDK2 payload → boot entry → OpenCore on the **BP M.2 SATA** SSD (spec §9 unchanged). SMBIOS MacPro7,1.
- **Stretch (Aidan's goal): OpenCore embedded in the payload firmware volume.**
  - Add `OpenCore.efi` plus an `OcBinaryData`/config FFS as a built-in boot option, the way Dasharo embeds iPXE and the UEFI Shell [Inference].
  - Config/kexts in a small read-only FV filesystem, or still from an ESP.
  - There is no ready-made "OpenCore in coreboot" project (checked). This is our own work.
- **macOS facts:**
  - macOS **Tahoe 26 is the last macOS for Intel** [N101]. Raptor Lake runs it only through OpenCore (hybrid P/E cores: `ProvideCurrentCpuInfo`, CPU topology quirks).
  - An AMD dGPU on Face P is required (§7).
  - After Tahoe, the machine stays a Windows/Linux workstation.

---

## 3. CPU VRM and the other rails

### 3.1 Rail requirements [Sourced: 743844 vol 1 tables 81–84 and the rail land counts in the ballout]

| Rail | Lands | i5-14500T (35 W 6P+8E) | Headroom target | Notes |
|---|---|---|---|---|
| VCCCORE | 280 | **IccMax ≈ 120 A**, PL1 35 W, PL2 92 W, Tau 28 s | **160 A** (65 W 6P+8E IccMax) | SVID, IMVP 9.1 load line (CNDA) |
| VCCGT | 51 | IccMax_GT **30 A** (S 35/65 W), TDC 22 A (65 W) | 30 A | SVID rail 2 |
| VCCIN_AUX | 28 | IccMax **33 A** (35 W); 32–36 A across S SKUs | 36 A | Feeds the FIVRs (SA, PCIe, display IO). Voltage = a few discrete levels selected by **PCH VID** pins |
| VDD2 (DDR5 MC) | 17–20 | **4 A** non-ECC / 4.5 A ECC | 5 A | 1.1 V fixed |
| VCC1P05_PROC | 8–9 | small (fixed 1.05 V) | 2 A [Estimate] | |
| VCC1P8_PROC | 2 | small | 0.5 A | |
| PCH VCCPRIM_CORE 0.82 V | — | **11.2 A** S0 + HSIO adders (0.11 A per Gen4 lane / DMI lane) | 15 A | 743835 "Power Rail Icc" |
| PCH 1.8 V (PRIM, HSIO PLL, XTAL) | — | ≈ 2.3 A | 3 A | |
| PCH 3.3 V primary, DSW 3.3, SPI, RTC | — | < 0.5 A total, RTC 6 µA in G3 | | DSW and the primary well also in S5 (≈ 1.7 A on 0.82 V in Sx) |

The CPU has **no separate VCCSA land**: SA is supplied internally from VCCIN_AUX via FIVR [Sourced: ballout rail list].

### 3.2 VCCCORE + VCCGT [Proposal]

- **Controller: Richtek RT3628AEGQW**
  - IMVP 9.1, dual rail, up to 8 + 1 phases [N102]. **LCSC C3249940: $2.18 @ 1, 170 in stock** (2026-10-01).
  - Same family as the MSI Z790-P (RT3628AE, 14 + 1 + 1 "Duet Rail") [N103].
  - **Risk:** its full datasheet and configuration GUI are NDA (Richtek FAE). Alternatives: MPS MP2965 (IMVP9, 7 + 3) and Infineon XDPE152C4D (no LCSC stock seen); same NDA situation.
- **Phases:**
  - **6 core + 1 GT**, each a **Vishay SiC654CD 50 A** smart power stage (PowerPAK MLP55-31L 5 × 5). **LCSC C1852094: $1.02 @ 1, 3,001 in stock.** The AOS AOZ5311NQI-03 55 A (C5943980) is out of stock.
  - 6 × 50 A = 300 A of stage rating for a 120–160 A IccMax: ≈ 25 A per phase at 35 W PL2, thermally easy.
  - A 65 W 8P+16E part (IccMax ~ 240–307 A) would need 8 phases plus a better thermal path → out of scope for rev A; that is decision D4. [Estimate from the IccMax table]
- **Inductors (front, under the plate, ≤ 6.0 mm):**
  - **Eaton FLAT-PAC FP4-150-R**: 0.15 µH, 42 A, **10.2 × 6.8 × 5.0 mm max** [N104].
  - Lower option: Coilmaster SEP0603ER15MLF (0.15 µH, 45 A, 3.0 mm) or SEP0603EBR22MLF (0.22 µH, 40 A) [N105]; no LCSC price found.
- **Output caps:** polymer ≤ 2.8 mm (7343 tantalum-polymer class) plus MLCC; **no tall polymer cans on the front.** 12 V bulk polymers go on the back (CB1/CB2).
- **Side:** **front**, left of the socket, because the VCCCORE and VCCGT lands sit at the left and bottom of the land field (`fitcheck_floorplan.txt`). Shortest path; no vias carrying 120 A.
  - Back-side VRM rejected: the back strips hold the SO-DIMMs and the centre holds the backplate.
- **Cooling (bonus):** the plate sits 6.3–7.5 mm above the board, so the 5.0 mm inductor tops are 1.3–2.5 mm below it. A **soft thermal pad (≤ 30 Shore 00) from the inductors / power stages / PCH to the black plate** makes the core the VRM heatsink [Inference].
  - The pad force adds to the CPU clamp load; size the pads so they add < 50 N [Estimate].

### 3.3 Other rails [Proposal]

- **VCCIN_AUX:** 2-phase (2 × SiC654 + 2 × FP4), with a controller that takes the PCH VID pins. Candidate TBD: MSI uses a separate small multiphase controller. Placed front-right, below the PCH-rail block.
- **VCC1P05/1P8_PROC, VDD2, PCH 0.82 V (15 A), 1.8 V, 3.3 V, DSW, 5 V VIN_BULK** (the DDR5 SO-DIMM PMICs need 5 V): JLC-stocked bucks. Part selection is a schematic task (TPS546/TPS56xxx/MPS class).
- **Standby:** 5V_SBY (6 pins) and 3V3_SB (2 pins) come from the BP over CPU-LINK (spec §3.8). They power the PCH primary/DSW wells, the RP2350 and the RTC in S5 (≈ 1–3 W [Estimate]); check against the BP 5V_SBY budget.
- **12 V input:** LUG1–4 → 2 × TPS259851 eFuse (as on the carrier) → VCCCORE VR (left pair) and the rest (right pair). Sustained ≈ 92 W PL2 + 25 W other ≈ 10 A at 12 V [Estimate].

---

## 4. Memory

| Option | Fits? | Pros | Cons | Verdict |
|---|---|---|---|---|
| **DDR5 SO-DIMM × 2, back, stock DIMM strips** | **Yes**: x 2.5–34.5 and 121.5–153.5, y 36.5–114.5 (back), clear of the backplate (x 37.25–118.75) | Stock DIMMs lived in these strips, so the Z room toward the PSU is proven. Socket 4.0 mm (UMAX 90415-4015SR, **LCSC C19267513, $2.74, 96 in stock**). Up to 2 × 48 GB. PMIC is on the module (we only supply 5 V). | DDR channels leave the package's **+Y (top) edge** and must turn left/right (byte swizzle allowed, ~50–80 mm). Max ~DDR5-4800/5600 1DPC [Estimate] | **Recommended** |
| DDR5 SO-DIMM on the front | Height 4.0 + module ≈ 5–6 mm under a 6.0 limit | — | No margin; it blocks the VRM/PCH area | Reject |
| Full DDR5 UDIMM (stock-like vertical) | Possibly in the strips (DDR3 DIMMs did) | Cheapest RAM | 133 mm slot length + latches in a 133 mm strip; tall | Not for rev A |
| Soldered DDR5 (memory-down) | Yes | Lowest profile | 8–16 BGA DRAMs + PMIC/SPD on our board, FSP memory-down config, no upgrade, much harder SI | Fallback only |
| DDR4 SO-DIMM | Yes | Cheaper RAM; the Z690-A DDR4 Dasharo variant exists | The 14th-gen platform is moving to DDR5; DDR4 needs 1.2 V VDDQ and VPP rails on our board | No |

- **Channel naming:** CH-A = J6 (left strip), CH-B = J7 (right strip). The connector row sits on the inner edge, toward the CPU; the module extends outward.
- **Height on the back:** confirm M-CC3 / M-CC15 (gap to the PSU at the strips with the board in the stock plane). The stock DIMMs stood here, so this is low risk.
- **Back-strip vias vs front VRM:** VCCCORE thermal vias under the power stages (x 9–15) land under the SO-DIMM module body (allowed; tented). They must stay clear of the connector pad rows (x ≈ 30–35).

---

## 5. PCB technology, stackup, socket

- **Layer count: 10.**
  - LGA1700 escape: 1700 lands at 0.8 mm, with ≈ 270 DDR5 signals, 80 PCIe, 32 DMI and 50 DDI lands.
  - PCH: 1045 balls at 0.50–0.565 mm, 28 × 25.
  - Two 120 A + 33 A power planes.
  - Mainstream ATX B760 boards are 6-layer and Z790 boards are 6–8-layer [Inference/industry practice], but our board is ~40 % of an ATX area, with the DIMMs and VRM squeezed into the strips. **10 layers buys clean references and a dedicated power pair.** 8 layers is a cost-down for rev B once rev A is routed.
- **Stackup (placeholder in KiCad; take the real dielectrics from the JLC 10-layer selector):** L1 S (front / finger side B) · L2 GND · L3 S (DDR5, PCIe stripline) · L4 GND · L5 PWR · L6 PWR · L7 GND · L8 S (DDR5, DMI) · L9 GND · L10 S (back / finger side A).
  - Impedance: 85 Ω PCIe/DMI, 90 Ω USB, DDR5 40 Ω SE / 80 Ω diff; ±10 % at JLC [N106].
- **JLC capability** [N106]:
  - 10 layers at 1.6 mm, impedance control, ENIG, hard gold with bevel.
  - **Via-in-pad (POFV) default on 6+ layers**; min via 0.15 drill / 0.25 pad; 0.09/0.09 mm track/space.
- **PCH fan-out:**
  - At 0.5005 mm min pitch with 0.25 pads, nothing fits between balls (0.25 gap). Every ball needs a POFV via, and inner-row escape uses the 0.565 neighbour gaps (0.315 mm: one 0.09 track with 0.11 clearance).
  - JLC standard has **no blind/buried microvias** [Unverified], so this is **through-via POFV only**. That is tight but similar to mainstream boards. **Make a test coupon / ask JLC engineering** (risk R-L5).
- **Price:**
  - No current public 10-layer list price was found. A 2022 JLC China promotion priced 5 pcs 10-layer ≤ 10 × 10 cm at ¥1,000 (≈ $137) [N107].
  - Our 156 × 170 mm board is ≈ 2.65× that area, so ≈ **$450–1,000 for 5 boards** with POFV, impedance and hard-gold bevelled fingers [Estimate; **get the instant quote**].
- **Socket:** **Foxconn PE17007-11NK0-1H** (LGA1700, SMT, gold): **LCSC C38520273**, $5.79 @ 1 / $4.95 @ 10, **32 in stock** (2026-10-01) [N108].
  - Lotes/Deren LGA1700 sockets are alternates. Deren lists a 0.8 mm pitch, a 37.5 × 45 package and a 0.13 mm stencil [N109].
  - **Get the Foxconn footprint drawing.** The KiCad pads are Intel land positions with 0.45 [Estimate] pads, and the housing outline 49 × 43 is an estimate.

---

## 6. Mechanics

- **Outline:** `/workspace/bracket/cpu_board/cpu_board_outline_corrected.dxf`.
  - The DXF is a back-view scan, but the outline is **mirror-symmetric about x = 78 above the shoulder.** The build checks this: the symmetric-difference area is 0.000 mm². So it is used unmirrored, with the stock tab replaced. Lower chamfers, lug notches (x 24–48 / 108–132 at y 163.5) and corner radii are unchanged.
- **CPU-LINK tab:** identical to the carrier (Mini Cool Edge 224 card, 79.89 wide at x = 78, key F x = 57.70, slots 78.36 / 98.57, tip y 1.722, shoulder 12.982). Fingers: front = side B, back = side A. No vias or pour at y < 6.
  - **Host TX AC caps** (CAC1, 0201) sit just above the shoulder. Unlike the module case, the host board owns the TX caps.
- **4 outer heatsink holes (fixed):** (43.25 / 112.75, 46 / 101), Ø5 plated, Ø12 no-track/no-via keep-outs. All other holes are free.
- **MP62 contact frame (spec §6.8):**
  - 71 × 54 body, long side along board x (package X), ≤ 6.0 mm tall, 7075 hard-anodised.
  - Its ear bosses sit on the 4 core holes. 4 own seat screws (H5–H8 at socket centre ± 28 / ± 21, M3 or #6-32) go into PEM nuts in our steel backplate.
  - The backplate is 81.5 × 67 on the back, with a window for the socket-cavity MLCCs.
  - Core clamping: 4 spring-loaded shoulder screws, ≈ 450–600 N, with the safety sleeve at ≥ 6.3 mm (unchanged).
- **Socket position:** centred on the measured pedestal (78.41, 73.25). The pedestal (40.6 × 41.1) covers the IHS.
- **Bus-bar lugs:** LUG1–4 at x 30.5 / 42.2 / 115.7 / 128.2, y 159.8 (front view). Polarity TBD (M-CC7).
- **Height rule:**
  - Front ≤ **6.0 mm** (5.5 recommended) everywhere under the plate (x 16.2–140.4, y 22.5–164.4). That excludes polymer cans, the MCIO receptacle and SO-DIMMs from the front.
  - The back holds J3 (MCIO RA), the SO-DIMMs, the M.2, BT1 and the bulk caps. **M-CC3 (back clearance to the PSU) is now a gating measurement** for J3 and the M.2 (the SO-DIMMs are in the proven strips).

---

## 7. iGPU (UHD 770) and display paths [Proposal; parent steering 2026-10-01 17:49 ET]

### 7.1 What the CPU offers [Sourced: 743844 vol 1 Table 60, ballout]

- **5 DDI ports (A–E)**, each 4 main-link pairs plus an AUX pair. DP up to **HBR3** (HBR3 needs an on-board retimer, Note 1); HDMI TMDS up to 5.94 Gbps. Up to 4 displays.
- **Where the lands are:** the DDI lands are in the bottom-left corner of the land field (board x 68–76, y 56–62).
- **HPD and DDC are on the PCH:** DDSP_HPD1–4 / HPDA (GPP_I1–I4, GPP_R9) and DDPx_CTRLCLK/DATA.

### 7.2 Proposal

| Port | Use | Path | Rate |
|---|---|---|---|
| **DDI-B → IOB native DP** (DP++ receptacle on the IOB) | Bring-up without any face module; service/fallback monitor | CB → J3 MCIO → IOB | **HBR2** (5.4 Gb/s; 4K60 8 bpc with 4 lanes); no retimer |
| **DDI-C → IOB USB-C DP-alt** | Second source into the IOB USB-C DP-alt path, **next to the Face P GPU's DP** | CB → J3 → IOB 2:1 DP mux (e.g. TI HD3SS215 class [Unverified]) → USB-C alt-mode mux/redriver (TUSB1046-class [Unverified]) | HBR2 |
| DDI-A/D/E | not connected (AUX/main pins left per datasheet rules) | — | — |

- The DDI main links run ≈ 110–130 mm from the bottom-left of the socket to J3 at the back top, plus the cable. That suits HBR2 [Estimate]. HBR3 would need retimers; not in rev A.
- **IOB link (J3, MCIO 124 RA) pair count** (the MCIO 124 carries 32 differential pairs plus sideband [spec §3; verify the pin map]):

| Group | Pairs |
|---|---|
| USB 3.2 × 4 (TX + RX) | 8 |
| USB2 × 4 | 4 |
| i226-V MDI (2.5GBASE-T, 4 pairs) | 4 |
| **DDI-B (4 main + AUX)** | **5** |
| **DDI-C (4 main + AUX)** | **5** |
| **Total** | **26 of 32 (6 spare)** |
| Single-ended (sideband pins) | 2 × HPD, DP-mux SEL (or I²C to the IOB mux), DDC only if an HDMI is fitted, IOB 3V3/5V sense, PWRBTN/LED via the BP link (unchanged) |

### 7.3 Primary display selection in firmware

- **FSP / coreboot:**
  - `InternalGfx` is set when IGD is enabled in the devicetree and SOC_INTEL_DISABLE_IGD is not selected.
  - DDI ports are configured with `ddi_portX_config` / `ddi_ports_config` (DDC/HPD enables) in the devicetree [N110].
  - IGD needs a **VBT** describing our ports (coreboot `util/intelvbttool`; start from the MSI VBT and edit the DDI types).
- **Priority:** `ONBOARD_VGA_IS_PRIMARY` sets **priority only**. If the preferred device is missing, firmware falls back to the other [N111].
- **Proposal:**
  - Ship **"Primary display = Auto (PEG first)"**: the Face P GPU's GOP drives the pre-boot UI when present; without a GPU the iGPU on DDI-B is used.
  - Expose a Dasharo setup option {Auto/PEG, iGPU, iGPU off}, backed by a CMOS/EFI option like `igd_dvmt_prealloc` [N110].
  - "iGPU off" is the clean choice for macOS-only users.

### 7.4 macOS caveat (stronger than "patchy")

- **macOS has no driver for any Xe-based Intel iGPU, including Alder Lake / Raptor Lake UHD 770, in any version** (Dortania GPU Buyers Guide; the Dortania Z690 notes; EliteMacx86) [N112].
  - Display out: **no**. QuickSync/headless: also **no** (headless IGPU only works on supported iGPUs up to UHD 630 / Comet Lake).
- **In macOS the iGPU must be hidden:** OpenCore DeviceProperties `class-code` = 0xFFFFFFFF (Dortania's recommendation; `disable-gpu` is unreliable) or `-wegnoigpu`, or "iGPU off" in our setup.
  - With the iGPU enabled and a monitor on DDI-B/C, macOS shows nothing on those ports. Users plug into the Face P GPU (an AMD GPU is required for Tahoe).
- **The realistic role of the iGPU:** firmware bring-up, BIOS/OpenCore picker without a GPU face, **Windows/Linux display and QuickSync/VA-API**, and a service fallback.

---

## 8. Floorplan (KiCad `/workspace/kicad/macpro62-lga1700/`)

`macpro62_lga1700.kicad_pcb`:
- 10 copper layers, 1.6 mm, JLC rules (0.09/0.09, via 0.25/0.15, edge 0.5).
- **DRC: 0 violations, 0 unconnected** (`drc_report.txt`).
- Renders: `floorplan.png` (board) and `floorplan_notes.png`. Numbers in `fitcheck_floorplan.txt`. Rebuild steps in the `README.md`.

| Ref | Part (placeholder, real size) | Side | Position (x, y), courtyard |
|---|---|---|---|
| U1 | LGA1700 Foxconn PE17007, **1700 lands from the Intel ballout** | F | centre (78.41, 73.25), 49.5 × 43.5 |
| — | MP62 contact frame 71 × 54 + 4 ears (Eco1) | F | on U1 |
| H1–H4 | core holes Ø5 (fixed) | F/B | (43.25/112.75, 46/101) |
| H5–H8 | frame seat screws Ø3.4 | F/B | U1 ± 28 / ± 21 |
| Q1–Q7, L1–L7 | SiC654 + FP4: 6 core + 1 GT phases | F | x 9–30, y 39–100 |
| CIN1 / COUT1 | 12 V in / VCCCORE out caps | F | x 3–8 / 31–36 |
| U3 | RT3628AE | F | (14, 108) |
| U4 / U5 / U6 / U7 | VCCIN_AUX 2-phase / 1P05+1P8 / PCH rails / 5 V VIN_BULK | F | x 120–148, y 34–108 |
| U8 | VDD2 1.1 V | F | (62, 110) |
| **U2** | **PCH Z790 FCBGA 28 × 25, 1045 balls from the Intel ballout** | F | (110, 133) |
| Y1, U9, U10, J4, J5 | crystals, **RP2350 EC**, 32 MB SPI, TPM header, debug | F | top band x 59–94 |
| U11, U12 | eFuses | F | (36, 146), (134, 146) |
| LUG1–4 | bus-bar lugs | F | y 159.8 |
| J1, CAC1 | CPU-LINK fingers, host TX AC caps | F/B | tab, y 15–23 |
| **J6, J7** | **DDR5 SO-DIMM CH-A / CH-B** (UMAX 90415-4015SR) | **B** | x 2.5–34.5 / 121.5–153.5, y 36.5–114.5 |
| J8 | M.2 2280 boot (PCH x4) | B | y 13–36 |
| J3 | IOB-HS MCIO 124 RA (USB3/USB2/MDI/**2 × DDI**) | B | (78, 160), exits toward the top edge |
| U13, U14, BT1, CB1/CB2 | i226-V, ALC897 (DNP), CR2032, 12 V bulk | B | top |
| — | backplate keep-out | B | x 37.25–118.75, y 40–107 |

**Land-group check** (from the public ballout, drawn on Dwgs.User):
- DDR0/DDR1 exit the top edge (y 78–91) and fan out to J6/J7.
- PCIe x16 + x4 are bottom-right (x 77–99, y 56–71) and run straight down to J1.
- DMI x8 is on the right edge, running toward U2.
- The DDI lands are bottom-left.
- VCCGT is on the left edge, beside the VRM. VCCCORE fills the left and bottom of the land ring around the central cavity.
- **Caveat:** this assumes the Intel X/Y coordinates are a top view. If they are a bottom view, the left/right sides swap (the DDR edge stays on top). **Verify before routing** (R-L11).

---

## 9. Cost estimate, rev A (2–5 boards at JLC) [Estimate unless a source is given]

| Item | 2 assembled (5 fabbed) | 5 assembled | Basis |
|---|---|---|---|
| PCB 10L 156 × 170, 1.6 mm, ENIG, POFV, impedance, hard-gold bevel, 5 pcs | $450–1,000 | $450–1,000 | 2022 JLC 10L promo ¥1,000 / 5 pcs / 10 × 10 [N107] × 2.65 area + extras; **instant quote needed** |
| PCBA setup, stencil, double-sided, BGA X-ray, consignment handling, extended-part fees (~40 unique × $3) | $250–450 | $350–600 | JLC price page [N113]; per-joint cost is small (~5k joints/board) |
| **PCH** Z790 loose (+3 spares) | 5 × $50–55 = $250–275 | 8 × $50–55 = $400–440 | €45–48 listings [N90]; authenticity risk |
| Socket ($5.79), RT3628AE ($2.18), 9 × SiC654 ($1.02), 2 × SO-DIMM socket ($2.74), RP2350 ($1.30) | 2 × ≈ $27 | 5 × ≈ $27 | LCSC 2026-10-01 [N102][N108][N114][N115] |
| 9 × FP4 inductors, eFuses, bucks, SPI flash, i226-V, crystals, M.2 socket, ~1,500–2,500 passives | 2 × $100–180 | 5 × $100–180 | [Estimate]; no prices sourced for FP4/i226-V |
| Contact frame (CNC 7075) + steel backplate + springs/screws (2–5 sets) | $100–250 | $200–400 | JLC CNC/sheet-metal [Estimate] |
| Shipping, customs/duties | $100–200 | $150–250 | [Estimate] |
| **Subtotal (boards)** | **≈ $1.5k–2.6k** | **≈ $2.6k–4.4k** | |
| CPU i5-14500T tray | $254–300 each | | Aztek $253.91, SHI $283, Neutron $300.23 (2026-10-01) [N116] |
| DDR5 SO-DIMM 2 × 16–32 GB, NVMe | per user | | not sourced |
| **De-risk kit (P6-0):** used MSI PRO Z690-A DDR5 / Z790-P, CH341A/SOIC clip, spare 14th-gen CPU (if needed) | $150–350 + tools | | [Estimate] |
| **Respin (rev B)** | budget a further ≈ 70–100 % of the rev-A subtotal | | first-spin success for a hobby LGA board is unlikely |

---

## 10. Risks, mitigations and go/no-go

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-L1 | **No Intel PDG/CRB** (CNDA): power sequencing margins, strap values, DDR5/PCIe routing rules, VR load-line (IMVP 9.1) | **High** | Public datasheets (rails, Icc, sequencing signal list, GPIO); coreboot ms7d25 gpio/devicetree; private reading of the MS-7D25/7E06 boardview (no copying); conservative SI (DDR5-4800, Gen4 policy); measure on the MSI board |
| R-L2 | **PCH sourcing / authenticity / fuses**: no franchised source; pulled parts may be fused | **High** | New sealed only; two sellers; X-ray + marking check; test one PCH early (G2: buy, inspect); spares; never close manufacturing |
| R-L3 | **ME/FIT availability & legality** (CSME 16.1 Consumer + MFIT via Win-Raid / vendor image) | **High** (legal grey) | Personal use, no redistribution; mirror the Z790-P lane map to reuse its descriptor; HAP; me_cleaner trial on the MSI board |
| R-L4 | **VR controller configuration** (RT3628AE datasheet/GUI under NDA; IMVP 9.1 load line) | **High** | Ask the Richtek FAE (hobby projects are often refused); read MSI's RT3628 configuration from its board (PMBus/I²C dump) [Inference]; alternative controller with public docs (TBD); 35 W CPU = big margin |
| R-L5 | **PCH 0.5 mm fan-out on JLC through-via POFV**; 10L SI | Med-High | JLC DFM review before the order; test coupon; 0.565 neighbour gaps; 8 → 10 layers already |
| R-L6 | **BGA/LGA assembly yield and rework** (two large BGAs, consigned PCH) | Medium | JLC X-ray; local BGA rework shop; spare PCHs; order 5 PCBs, assemble 2 first |
| R-L7 | **DDR5 routing to two side strips** (channels exit one edge) | Medium | Byte/bit swizzle per DDR5 rules; DDR5-4800 1DPC; FSP memory training; memory-down as plan B |
| R-L8 | **Front height ≤ 6.0** under the plate (inductors 5.0, caps ≤ 2.8) + thermal pads loading the board | Medium | FP4 / SEP0603 parts; height check per BOM line; soft pads with a force budget |
| R-L9 | **Firmware effort** (new coreboot mainboard, EC sequencing, VBT, OpenCore embedding) | High (time) | P6-0 on the real MSI board first; reuse ms7d25; OpenCore from the SATA SSD in rev A |
| R-L10 | **Back clearance to the PSU** for J3 (MCIO RA) and the M.2 (M-CC3) | Medium | Measure; SO-DIMMs already in the proven strips; J3 → low-profile alternative if needed |
| R-L11 | **Ballout orientation / socket footprint** (Intel X/Y view, Foxconn pad sizes) | Medium | Foxconn drawing; check the pin-1 corner against the package drawing (743844 vol 1 mechanical section) before routing |
| R-L12 | **Gen5 x16 over the CPU-LINK + BP + MCIO** | Low (policy Gen4) | Spec §3.6 unchanged: Gen4 default, optional BP redrivers |
| R-L13 | macOS lifetime (Tahoe is the last Intel macOS) | Accepted | Windows/Linux long-term; OpenCore until then |

**Go/no-go:**
- **GO now for P6-0 "de-risk"** (≈ 3–6 weeks, ≈ $400–900):
  - **G1 Firmware on the reference:** a used MSI PRO Z690-A DDR5 (or Z790-P). Build Dasharo from source; build the ME/descriptor with MFIT (HAP); boot OpenCore → Tahoe from SATA; test embedding OpenCore in the payload; test the iGPU/PEG primary-display options. Dump the RT3628 configuration and measure the sequencing.
  - **G2 Sourcing:** buy 3–5 Z790s from two sellers; inspect; confirm JLC consignment and BGA handling in writing; get an instant 10L quote and a DFM opinion on the PCH fan-out.
  - **G3 Schematic + routing study:** the PCH escape on 10L at JLC rules, plus DDR5 to J6/J7 (use the existing floorplan).
  - **G4 Measurements:** M-CC3 (back clearance), M-CC7 (lug polarity), M-CC8 (boss thread).
- **Gate G-A (rev-A order): CONDITIONAL GO** if G1 boots Tahoe with our own build, G2 yields authentic unfused PCHs and a JLC yes, and G3 shows the PCH and DDR5 routable.
  - **No-go triggers:** no ME/descriptor path; PCHs fused or fake; VR controller not configurable. In that case, fall back to the archived COM-HPC carrier (Size A) or memory-down variants.
- **Honest summary:**
  - The electrical design is feasible with public data plus a reference board, but it is **the hardest board in the project by far**.
  - The closed parts (PDG, IMVP, ME/FIT) are worked around, not solved.
  - Expect a rev B, and expect firmware bring-up to take months of evenings.

---

## 11. Decisions for Aidan

1. **D1 Chipset:** Z790 (recommended; reference parity) or B760 (RCP $26 lower, loose listings only ≈ €3–6 lower; DMI x4)?
2. **D2 ECC:** no (recommended) or W680 + ECC SO-DIMMs (CSME Corporate, no loose source found)?
3. **D3 Memory:** 2 × DDR5 SO-DIMM on the back strips (recommended) or memory-down?
4. **D4 CPU class:** design the VR for the 35 W T-series 6P+8E (120–160 A, 6 + 1 phases; recommended) or reserve 8 phases for 65 W 8P+16E?
5. **D5 ME approach:** MFIT build from the CSME kit (Win-Raid) vs the vendor-image ME region (both grey) with HAP; OK to proceed for personal use?
6. **D6 P6-0:** OK to buy a used MSI PRO Z690-A DDR5 / Z790-P as the firmware reference and 3–5 loose Z790s now?
7. **D7 iGPU ports:** DDI-B native DP + DDI-C into the USB-C DP-alt mux (proposed), HBR2 only, default "Primary display = Auto (PEG first)"?
8. **D8 OpenCore location for rev A:** keep it on the BP SATA M.2 (recommended), with embedding as the stretch?
9. **D9 Budget:** accept ≈ $1.5k–2.6k (2 boards) / $2.6k–4.4k (5 boards) plus a probable rev B?

---

## 12. Sources (also added to the spec as N84–N116)

- [N84] Intel 700 Series Chipset Family PCH Datasheet vol 1, 743835-004 (+ attachments 743835_001_Ballout / GPIO / Electr_Therm_Spec xlsx): https://cdrdv2-public.intel.com/743835/743835-004.pdf
- [N85] Intel 13th/14th Gen Core desktop datasheet vol 1, 743844-015 (+ 743844-001_S_LGA_Ballout.xlsx): https://cdrdv2-public.intel.com/743844/743844-015.pdf
- [N86] Intel B760 ordering/spec (RCP $31): https://www.intel.com/content/www/us/en/products/sku/229719/intel-b760-chipset/ordering.html
- [N87] Intel Z790 ordering (FH82Z790, SRM8P, RCP $57): https://www.intel.com/content/www/us/en/products/sku/229721/intel-z790-chipset/ordering.html
- [N88] Intel W680 ordering (FH82W680, RCP $56): https://www.intel.com/content/www/us/en/products/sku/218834/intel-w680-chipset/ordering.html
- [N89] ASRock Rack W680 WS (lists the i5-14500T, ECC): https://www.newegg.com/asrock-rack-w680-ws/p/N82E16813140147
- [N90] Loose Z790 listings: https://www.afromanshop.lt/Value-Extra-182549.html ; https://milpood.ee/Premium_32253-Store ; https://www.taouq.com/id-ANX6YkPjHzt4jGRmWNmSmmYsvtn-VeR99wckn8BGqeJIJ/ [Unverified sellers]
- [N91] Loose B760 SRM8V listings: https://www.oknabytok.sk/Global-unique-529893.htm ; https://www.itdevices.ca/product-details/654217 [Unverified sellers]
- [N92] JLCPCB PCB assembly capabilities (BGA ≥ 0.35 mm pitch): https://jlcpcb.com/capabilities/pcb-assembly-capabilities
- [N93] JLCPCB: how to use my own parts: https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order
- [N94] JLCPCB: how to consign parts: https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb
- [N95] coreboot MSI PRO Z690-A (ms7d25) port: https://review.coreboot.org/c/coreboot/+/63463 ; DDR5 variant: https://review.coreboot.org/c/coreboot/+/68448
- [N96] Dasharo MSI Z690-A / Z790-P releases v1.1.7 / v0.9.5 (2026-08-13): https://docs.dasharo.com/variants/msi_z790/releases/ ; https://blog.3mdeb.com/2026/2026-08-13-msi_z690-a_z790-p_v1.1.7_v0.9.5_release/
- [N97] Intel FSP (RaptorLakeFspBinPkg/Client/RaptorLakeS): https://github.com/intel/fsp ; ADL-S → RPL-S FSP in coreboot: https://review.coreboot.org/c/coreboot/+/78190
- [N98] MSI MS-7D25 boardview thread (unauthorised; reference only): https://www.badcaps.net/ (thread 100259 "boardview schematics for msi z690-a pro ms-7d25")
- [N99] Win-Raid: Intel CSME 16 firmware and tools (MFIT 16.1.25.2091): https://winraid.level1techs.com/t/intel-csme-drivers-firmware-and-tools-for-me-16/89959
- [N100] me_cleaner on newer platforms (issue 340): https://github.com/corna/me_cleaner/issues/340
- [N101] macOS Tahoe is the last Intel macOS: https://appleinsider.com/articles/25/06/17/opencore-and-hackintosh-are-sadly-dead-after-apple-ends-intel-mac-support
- [N102] Richtek RT3628AE: https://www.richtek.com/Products/Vcore/intel-vcore/RT3628AE ; LCSC C3249940: https://www.lcsc.com/product-detail/C3249940.html
- [N103] MSI PRO Z790-P VRM (RT3628AE, 14 + 1 + 1, 55 A): https://tech4gamers.com/msi-z790-pz-motherboard-review-value-features-and-looks/
- [N104] Eaton FP4-150-R datasheet (10.2 × 6.8 × 5.0, 0.15 µH, 42 A): https://xonstorage.z8.web.core.windows.net/pdf/eaton_fp4150r_apr22_xonlink.pdf
- [N105] Coilmaster SEP0603ER15MLF: https://www.coilmaster.com.tw/en/product/SEP0603ER15MLF.html
- [N106] JLCPCB PCB capabilities (10 layers, impedance, via-in-pad): https://jlcpcb.com/capabilities/
- [N107] JLC (China) 10-layer promotion 2022: https://www.jlc.com/portal/q7i37597.html
- [N108] Foxconn PE17007-11NK0-1H, LCSC C38520273: https://www.lcsc.com/product-detail/C38520273.html
- [N109] Deren LGA1700 socket brochure: https://static.deren.com/ (file 6380741085151012745523273.pdf)
- [N110] coreboot ADL romstage display UPDs (DdiPortXConfig, DDC/HPD, IGD prealloc option): https://review.coreboot.org/c/coreboot/+/87620/3/src/soc/intel/alderlake/romstage/fsp_params.c ; https://review.coreboot.org/c/coreboot/+/55273 ; SOC_INTEL_DISABLE_IGD: https://review.coreboot.org/c/coreboot/+/49291
- [N111] ONBOARD_VGA_IS_PRIMARY = priority only: https://review.coreboot.org/c/coreboot/+/39374
- [N112] macOS has no Xe iGPU support (ADL/RPL): https://dortania.github.io/GPU-Buyers-Guide/modern-gpus/intel-gpu.html ; https://dortania.github.io/hackintosh/updates/2022/01/09/alder-lake.html ; https://elitemacx86.com/threads/how-to-disable-unsupported-igpu-intel-graphics-on-desktops-and-laptops.1013/
- [N113] JLCPCB PCB assembly price: https://jlcpcb.com/help/article/pcb-assembly-price
- [N114] Vishay SiC654CD-T1-GE3, LCSC C1852094: https://www.lcsc.com/product-detail/gate-drivers_vishay-intertech-sic654cd-t1-ge3_C1852094.html
- [N115] UMAX 90415-4015SR DDR5 SO-DIMM socket, LCSC C19267513: https://www.lcsc.com/product-detail/C19267513.html
- [N116] i5-14500T tray prices: https://www.aztekcomputers.com/cm8071505092904-core-i5-14500t-up-to-4-80ghz-tray-intel/p ; https://www.shi.com/product/47566241/Intel-Core-i5-i5-14500T ; https://www.neutronusa.com/prod.cfm/5149012
- Realtek ALC897-VA2-CG, LCSC C5884442: https://www.lcsc.com/product-detail/C5884442.html
