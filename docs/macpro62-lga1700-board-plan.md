# MacPro6,2 — own LGA1700 CPU board ("CB"): feasibility study and plan

Version fl2.1, 2026-10-01 (~21:15 ET, right-notch note ~21:21 ET; fl2.1 = single 12 V entry at the left lug pair, from Aidan's stock-board photos ~21:03 ET, right notch = GPU bus-bar pass-through ~21:19 ET, §6; fl2 = 4 × DDR5 UDIMM vertical in the stock DIMM strips, §4, after Aidan's question and correction ~18:10 ET; fl1 = 2 × SO-DIMM, kept as the fallback variant). Status: **[Proposal]**. Tags are the same as in the spec: [Sourced] with a link, [Estimate], [Inference], [Unverified], TBD.

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
| Memory | **fl2: 4 × DDR5 UDIMM, vertical, like the stock Mac Pro** (UMAX 90414 short-latch SMT sockets at the stock card centrelines x 6.5 / 15.8 and 140.55 / 149.85, back side), **2DPC daisy chain**, DDR5-4000 (4 × 1R) / 3600 (4 × 2R) / 4400 (2 DIMMs), up to 4 × 48 GB. Same topology as the Dasharo reference MSI PRO Z690-A (2DPC). **Gate: M-CC15** (DIMM top ≤ 33.25 mm off the back vs stock DDR3 ≈ 30 + seat). Fallbacks: VLP 18.75 mm UDIMMs in the same sockets, or fl1 2 × SO-DIMM. | medium |
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
| i226-V 2.5GbE ×2 (on the IOB since CR-CB-IO1; 2nd port added 2026-10-02, spec item 24) | PCH Gen3 x1 ×2: RP3 / HSIO 12 (CLKOUT_SRC12) and RP4 / HSIO 13 (CLKOUT_SRC11) via J3 k10 / k14 | 2 | ✓ | ✓ |
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
  - Costs: CSME **Corporate** (a different ME image and a different Dasharo baseline; no W680 Dasharo reference found), **no loose-chip source found**, and ECC UDIMMs.
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
  3. Keep the ms7d25 memory config as is: `BOARD_TYPE_DESKTOP_2DPC`, `MEM_TOPO_DIMM_MODULE`, SPD 0x50/0x51 (CH-A) and 0x52/0x53 (CH-B), `dq_pins_interleaved = true` [N121]. (The fl1 SO-DIMM fallback would need a 1DPC board type and a new SPD map.)
  4. Write a new VBT (§7.3) and a new ME/descriptor (§2.3).
- **First run on the real MSI board:** start with a used **MSI PRO Z690-A DDR5** (or Z790-P). Build Dasharo from source, add OpenCore, boot Tahoe, and only then change things for our board. That de-risks ~80 % of the firmware without our hardware (phase P6-0, §10).

### 2.2 FSP

- Public binary plus headers: intel/FSP `RaptorLakeFspBinPkg/Client/RaptorLakeS`. The AlderLake-S paths are symlinks to it [N97].
- License: redistribution of the binary is allowed (per the FSP license in the repo).
- Memory init: FSP-M with SPD from the modules; the 4-DIMM 2DPC desktop topology is exactly what the ms7d25 port already sets up (DDR5 and DDR4 variants) [N121].

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
  - Back-side VRM rejected: the back strips hold the DIMM sockets and the centre holds the backplate.
  - fl2: the power stages moved from x 12.0 to **x 11.15** so their through vias land in the 4.2 mm corridor between the back pad rows of J7 (outer) and J6 (inner) (x 9.05–13.25).
- **Cooling (bonus):** the plate sits 6.3–7.5 mm above the board, so the 5.0 mm inductor tops are 1.3–2.5 mm below it. A **soft thermal pad (≤ 30 Shore 00) from the inductors / power stages / PCH to the black plate** makes the core the VRM heatsink [Inference].
  - The pad force adds to the CPU clamp load; size the pads so they add < 50 N [Estimate].

### 3.3 Other rails [Proposal]

- **VCCIN_AUX:** 2-phase (2 × SiC654 + 2 × FP4), with a controller that takes the PCH VID pins. Candidate TBD: MSI uses a separate small multiphase controller. Placed front-right, below the PCH-rail block.
- **VCC1P05/1P8_PROC, VDD2, PCH 0.82 V (15 A), 1.8 V, 3.3 V, DSW, 5 V VIN_BULK** (the DDR5 module PMICs need 5 V; 4 UDIMMs ≈ 6 A budget [Estimate]): JLC-stocked bucks. Part selection is a schematic task (TPS546/TPS56xxx/MPS class).
- **Standby:** 5V_SBY (6 pins) and 3V3_SB (2 pins) come from the BP over CPU-LINK (spec §3.8). They power the PCH primary/DSW wells, the RP2350 and the RTC in S5 (≈ 1–3 W [Estimate]); check against the BP 5V_SBY budget.
- **12 V input (fl2.1, single entry):** the stock board takes 12 V **only at the left lug pair** (LUG1/LUG2, top-left next to the VRM; Aidan's photos, §6.1). LUG1/LUG2 → **one** TPS259851 eFuse U11 (36, 146) (ILIM ≈ 25 A, TVS, IMON → EC ADC) → 12 V plane → VCCCORE/GT VR input caps (CIN1) and every other rail. U12 and the right-hand pair are gone.
  - Load [Estimate]: 92 W PL2 + 6 W PCH + ≈ 20 W for 4 DDR5 DIMMs (PMIC from 5 V) + i226/EC/misc ≈ 125 W → ≈ 142 W in at ≈ 88 % → **≈ 12 A sustained at 12 V; design for 20 A peak** (PL2/turbo transients, DIMM inrush). The stock board fed a 130 W Xeon E5 plus 4 DIMMs through the same pair, so one pair is enough.
  - Lug pins: each lug lands on 2 × 2 PTH (back photo), so ≈ 3 A per pin at 12 A, ≈ 5 A per pin at 20 A. Use ≥ 1.6 mm drilled, ≥ 2.6 mm annular pads, all 10 layers tied to the 12 V / GND planes [Estimate].
  - **Copper [Estimate, IPC-2221 internal]:** 13 A at 10 °C rise needs ≈ 1,460 mil² ≈ 27 mm of 1 oz on one layer. **12 V on L5 + L6 (1 oz), ≥ 20 mm wide** from U11 down the left edge to CIN1 / the VRM column (≈ 60 mm, ≈ 0.75 mΩ, ≈ 10 mV and 0.13 W at 13 A), plus **≥ 8 mm across the top band** to the right-side rails (VCCIN_AUX, 5 V / 3.3 V bucks, ≈ 4–5 A). If JLC's 10L inner layers are 0.5 oz, double the widths or add a third 12 V layer. GND return: L2/L4/L7/L9 solid, stitched at the GND lug.
  - Short path: the entry, U11 and the VCCCORE input caps are all at the top-left, so the high-current path is short and stays on the left; only ≈ 4–5 A travels to the right.

---

## 4. Memory (fl2: 4 × full-size DIMM, stock-like) [Proposal; Aidan question + correction 2026-10-01 ~18:10 ET]

**Stock reference.** The Mac Pro 6,1 has 4 full-length 240-pin DDR3 ECC DIMMs (UDIMM or RDIMM, 1866), 2 per side, and "DIMMs with heatsinks are not supported" [N122]. Per Aidan's correction they **stand vertically** off the back of the riser in normal-style sockets; Apple's socket assembly only tilts to release them. Scan geometry (`/workspace/bracket/cpu_board/`): card centrelines **x 6.5 / 15.8 and 140.55 / 149.85** (9.3 mm pitch), pair bodies x 2.5–18.5 / 137.0–153.0, **y 22.5–168.2 (145.7 long)**. A DDR3 RDIMM is **30.0 mm** tall (29.85–30.50, Micron) [N122], so the proven envelope toward the PSU is ≈ 30 mm + the stock seating plane (≈ 31–32.5 mm in total, matching Aidan's "about 31 mm").

### 4.1 Sockets: vertical 288-pin, buyable

| Part | Type | Key dims | Availability / price (2026-10-01) | Use |
|---|---|---|---|---|
| **UMAX 90414-xx011-x1 series** (drawing C-90414 rev 3) | DDR5 UDIMM, vertical SMT, 0.85 mm, tab or boardlock | body 141.7 × 6.30, height 21.3, **seat ≤ 2.0**; latch: **short 142.0 closed / 151.5 open / 152 keep-out**, middle 145.5/156/156, long 147.5/158.5/162 | **LCSC C2922443 = 90414-15011-21 (long latch, tab): $4.44, 72 in stock**; short-latch code = "…-11" per the ordering table, not seen at LCSC [Unverified] | **Recommended family; order the short latch** (the long latch does not fit the outer slots, below) [N117] |
| UMAX 90413-15011-21 | DDR5 DIMM, vertical SMT | (drawing not read) | LCSC C2922442, $4.10, 3 in stock | alternative [N117] |
| **Amphenol DDR504xxx (standard latch) / DDR506xxx (narrow latch)** | DDR5, vertical SMT | **length ≤ 142, width ≤ 6.5, height ≤ 21.3, seat ≤ 2.0**; also a **single-fixed-latch** option (one end fixed, left or right) | distributors / sample (not checked) | second source; the single-latch version saves ≈ 5 mm of latch swing [N118] |
| TE 1-/2-/8-2355626-1, 8-2355632-1 | DDR5 DIMM, vertical SMT | profile 21.3, row-to-row 3.0 | Digi-Key 2-2355626-1 ≈ $7.38 (stock not read) | second source [N119] |
| **UMAX 90411-151231 / -151131** | **DDR4** UDIMM, vertical SMT, 0.85 mm | DDR4 family envelope (drawing not read) | **LCSC C5889263 $2.47, 205 in stock; C5889264 $2.44, 24 in stock** | only if the DDR4 board variant is chosen [N124] |
| Molex 151080-0101 (25°) | DDR4, angled THT | — | Digi-Key 470 @ $49.36 | **not needed** any more (the stock DIMMs were vertical); no angled DDR5 UDIMM socket was found |

- **Tilt/latch release:** no catalogue socket copies Apple's tilting socket cradle; it is Apple's own mechanism, and a hinged cradle on a rigid 10-layer board would need flexible interconnect (not reasonable). **Standard short ejector latches** are the answer.
  - Open-latch envelope (152, centred at y 95.6) = y 19.6–171.6. The latch tips swing above the board and pass the outline by **≤ 2.1 mm at the top edge** and **≤ 4.4 mm at the bottom chamfer of the outer slots**. That only matters if the enclosure is in the way when DIMMs are changed. Check it with M-CC15.
  - If it collides, use a **single-fixed-latch** socket (Amphenol option) with the fixed end at the bottom chamfer. Or add the simple **MP62 DIMM retainer**: a 1 mm stainless or 3D-printed bar across the two module tops per strip, two M2.5 screws into standoffs at the strip ends (y ≈ 20 / 170, inside the old stock end-cap zone). That bar also holds the modules against shock in the vertical-board orientation. It is optional and needs no board change except two holes.
- **Long latch (the LCSC stock part) does not fit the outer slots:** closed 147.5 must span y ≈ 21.7–169.2, and at x 3.35 the bottom chamfer is at y ≈ 24.0. It does fit the inner slots. Use the short latch for all four (one BOM line).

### 4.2 Mechanical fit (vertical, toward the PSU)

| Item | Value | Source |
|---|---|---|
| DDR5 UDIMM (JEDEC MO-329) | **133.35 × 31.25**, thickness **≤ 4.05** (incl. PMIC/DRAM, no heat spreader) | C-90414 sheet 2 [N117] |
| Socket seat | ≤ 2.0 above the board | [N117][N118] |
| **DIMM top above the CB back** | **≤ 33.25 mm** | 2.0 + 31.25 |
| Stock DDR3 top | 30.0 (29.85–30.50) + stock seat (≈ 1–2.5, not measured) ≈ 31–32.5 | [N122], scan |
| **Difference** | **≈ +0.75 … +2.25 mm** (nominal ≈ +1.25: the DDR4/DDR5 module is 1.25 mm taller than DDR3) | [Inference] |
| CB float on the springs | IHS Z range 6.53–7.53 → the board plane moves ≤ 1.0 mm | §6 |
| **Requirement M-CC15** | back-to-PSU gap at the strips **≥ 34.5 mm** (33.25 + 1.0 float, + margin), plus the latch-swing check | [Proposal] |
| Fallback if the gap is 21–34.5 mm | **DDR5 VLP UDIMM 18.75 mm** in the same sockets (top ≤ 20.75): Apacer, Cervoz, Innodisk, 16/32 GB, 4800/5600, industrial pricing | [N123] |
| Lengthwise | short latch closed 142.0 at y 24.6–166.6 (centre 95.6) inside the stock 22.5–168.2 | fl2 fit check |
| Pitch | stock 9.3 → **3.0 mm** between the socket bodies (6.3) and **5.25 mm** between bare modules (4.05) | — |
| Heat spreaders | modules ≤ 7 mm thick still clear each other; tall "gaming" spreaders do not fit the height. Use JEDEC-height bare modules, as Apple requires | [N122] |

**Result: 4 vertical DDR5 UDIMMs fit the stock strips in x and y like stock.** The only open item is the ≈ 1–2 mm of extra height and the latch swing (M-CC15).

### 4.3 Electrical

- **Topology:** 2 DPC per channel, **daisy chain** (CPU → near slot → far slot). Intel requires the **far slot to be populated first** when a channel has one DIMM [N120], which is the daisy-chain convention; Intel client DDR5 boards do not use T-topology [Inference]. fl2: **J6 = CH-A DIMM1 (inner, near, x 15.8), J7 = CH-A DIMM2 (outer, far, x 6.5); J9 = CH-B DIMM1 (x 140.55), J10 = CH-B DIMM2 (x 149.85)**. Populate J7 + J10 first.
- **Speed (Intel 743844 vol 1, Processor SKU Support Matrix, S Refresh UDIMM) [N120]:**

| Config | DDR5 | DDR4 |
|---|---|---|
| 1DPC board (SO-DIMM fl1, or 2 slots) | 5600 (1R and 2R) | 3200 |
| 2DPC board, 1 DIMM per channel | **4400** | 3200 |
| 2DPC board, 2 × 1R per channel | **4000** | 3200 |
| 2DPC board, 2 × 2R per channel | **3600** | 3200 |

  - Bandwidth (2 channels): DDR5-5600 89.6 GB/s · 4400 70.4 · 4000 64.0 · 3600 57.6 · DDR4-3200 51.2.
  - Capacity: RPL supports 16 and 24 Gb DDR5 dies → 48 GB UDIMMs → **4 × 48 = 192 GB** (= the i5-14500T maximum) vs 2 × 48 = 96 GB on SO-DIMMs; DDR4 4 × 32 = 128 GB.
- **Routing:**
  - The DDR lands leave the **+Y package edge** (y 78–91). Each channel runs ≈ 45–60 mm sideways to its strip and then spreads along the 128 mm pin field (pins span ± 63.3 from the socket centre): **≈ 60–125 mm CPU → near slot, + 9.3 mm to the far slot** [Estimate]. That is longer than an ATX board (DIMMs parallel to the DDR edge), but a 2DPC channel only runs at 3600–4400, which is more forgiving than the SO-DIMM fl1 at 5600. Byte-lane skew between bytes is trained (write leveling / read training); match within a byte only.
  - The socket's 0.85 mm double row is easier to escape than the SO-DIMM's 0.5 mm. Each signal now visits two sockets (≈ 2 × 130 nets [Estimate], short stubs between the rows).
  - **Layer count stays at 10.** DDR5 on L3/L8 striplines. Under the front VCCCORE switch nodes (left strip), use L8 (shielded by L7/L9 GND) and keep L3 out of the SW-node footprints.
  - **VRM via corridor:** the left strip lies under the front VRM. The power stages moved to x 11.15 so their vias land between the J7 and J6 pad rows (x 9.05–13.25, drawn on Eco2 in fl2).
- **Power:** DDR5 modules carry their own PMIC: the CB supplies only **5 V VIN_BULK** (U7, ≈ 6 A budget for 4 modules [Estimate]) and 3.3 V for the SPD hub. CPU VDD2 1.1 V unchanged. Each slot straps its SPD-hub address with the HSA pin resistor → 0x50/0x51/0x52/0x53 [Inference, JEDEC DDR5 SPD hub].
  - DDR4 would instead need VDDQ 1.2 V (≈ 6–10 A for 4 DIMMs [Estimate]), VPP 2.5 V, a VTT 0.6 V sink/source regulator and VREFCA on our board, and VDD2 becomes 1.2 V.
- **coreboot / FSP:** the reference MSI PRO Z690-A (ms7d25) is itself a 4-DIMM 2DPC board. Its upstream `romstage_fsp_params.c` sets `UserBd = BOARD_TYPE_DESKTOP_2DPC`, `MEM_TOPO_DIMM_MODULE`, SPD 0x50/0x51/0x52/0x53, `dq_pins_interleaved = true` and `ect = true`, for **both DDR4 and DDR5** variants [N121]. **fl2 matches it 1:1**, so no memory-config change is needed. The fl1 SO-DIMM board would have to change it.

### 4.4 Options and recommendation

| Option | Speed (all slots full) | Max capacity | Height / mech | Board effort | Firmware | Verdict |
|---|---|---|---|---|---|---|
| **A. 4 × DDR5 UDIMM vertical (fl2)** | 4000 (1R) / 3600 (2R); 4400 with 2 DIMMs | **192 GB** | ≤ 33.25 mm, ≈ +1.25 mm over stock → **M-CC15**; latch swing check | 4 sockets $4.4 each; only 5 V for the PMICs | **= ms7d25 (2DPC)** | **Recommended** (stock-like, max capacity, reference parity) |
| B. 4 × DDR4 UDIMM vertical | 3200 (no 2DPC derating) | 128 GB | same envelope (31.25) | + VDDQ/VPP/VTT/VREF rails; sockets $2.47 (C5889263) | = ms7d25 DDR4 (the first Dasharo variant) | Only for cheap used DDR4; 20–30 % less bandwidth than A, more rails |
| C. 2 × DDR5 SO-DIMM (fl1) | **5600** | 96 GB | 4 mm sockets + modules lying flat, ≤ ≈ 8 mm → no PSU question | 2 sockets $2.74 | new 1DPC config | **Fallback** if M-CC15 fails and VLP is unwanted |
| A-VLP. Option A with 18.75 mm VLP UDIMMs | as A | 4 × 32 GB = 128 GB (VLP sizes seen) | ≤ 20.75 mm | as A | as A | fallback for A without a board change |

**Decision D3 (new):** take A as the rev-A baseline (fl2 is drawn that way) and keep C as the documented fallback (`docs/fl1_sodimm_variant/`). The board is DDR5 **or** DDR4, never both. The DDR4 variant would be a separate board revision.

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
- **Bus-bar lugs (fl2.1): only LUG1 / LUG2, left notch.** Centres **x 27.95 / 40.75** (legs 24.05–31.85 / 36.85–44.65), feet at y ≈ 157, footprint centre y 159.8, front (CPU-side) view, ±0.8 mm (photo, §6.1). Footprint: 8 × 6 pad + 2 × 2 PTH each [Estimate]. Pair spacing 12.8. Polarity TBD (M-CC7): placeholder LUG1 = GND?, LUG2 = 12 V?. The right notch (x 108–132) stays in the outline but has **no CB lugs**.
  - **Right notch = GPU bus-bar pass-through (Aidan, ~21:19 ET):** the notch at x 108–132 (y 163.5–169.5) carries the GPU power bus bars/lugs past the CPU board; the CB has no lugs there. KiCad rule area `GPU_BUSBAR_PASSTHROUGH` = notch + 3 mm (x 105–135, y 160.5–169.5), all copper layers, both sides: no footprints, pads, tracks, vias or pour. **Required clearance [Proposal]:** ≥ 3 mm from the notch walls to any CB copper or part (electrically 12 V needs only ≈ 0.1–0.6 mm, IPC-2221; the 3 mm covers the bar's position tolerance, lug screw heads, insulation sleeve and assembly by hand). Confirm the bar width, thickness and offset in the notch with M5 (bus-bar positions and cross-sections). The earlier LUG1–4 at 30.5 / 42.2 / 115.7 / 128.2 (two pairs, 85.6 apart, with a 5 mm bus-bar jog to the PSU's 74.7) are void.
- **Stock photo check (fl2.1, Aidan's photos 2026-10-01 ~21:03 ET, `/workspace/mp62-spec-refs/photos/`).** Method: a homography from the 4 core holes (photo → board frame); outline edges land within ≈ 1 mm (left edge 0.9, top 171 vs 169.5, notch walls 23.2 / 47.3 vs 24 / 48 → +0.75 mm x correction).
  - **12 V entry:** 2 copper lugs at the top-left, in the left notch, next to the VRM. The back photo shows each lug soldered with 2 × 2 pins and **nothing at the right notch**. → single entry, above.
  - **Sides:** the back photo shows the **4 DIMM slots and the socket backplate on the back**. fl2 already has J6/J7/J9/J10 on B (all 288 SMD pads on B.Cu) and U1, the VRM (Q/L) and the lugs on F. **No side change was needed.**
  - **Stock VRM along the top:** 7 inductors at y ≈ 119–131 across x ≈ 46–120, controller near (46, 152), a row of polymer input caps (OS-CON-type, 16 V) at y ≈ 157–168, x ≈ 49–108. **Ours differs on purpose:** a left column at x 11.15 (LGA1700 VCCCORE/VCCGT lands sit on the left / bottom edges of the package, R-L11) with the lugs and U11 right above it, so the single left entry still gives a short path. The top band carries the eFuse, bucks, EC and debug.
  - **Frame and holes:** the large stock frame on 4 outer holes agrees with our 4 core holes (43.25 / 112.75, 46 / 101); the 4 stock ILM holes are dropped as before.
  - **Conflicts found:** (1) ~~the old outline scan shows 4 eyelet tabs (both notches), the photo only 2~~ **closed (Aidan, ~21:19 ET):** the scan's right-hand tab pair belongs to the GPU power path passing through the right notch, not to the CPU board. (2) The photo lug centres match the scan's LUG1/LUG2 taken **unmirrored** (23.8–31.8 / 36.2–44.4) better than the mirrored LUG4/LUG3 we had used (30.5 / 42.2, 1.5–2.5 mm off). That fits a CPU-side scan, but the spec says the scan shows the back (§6.1 "View (fp2)"). The outline, holes and notches are symmetric and the stock tab is replaced, so only the lug x positions depend on it. Caliper check: M-CC16. The tab is out of frame in the photo, so the stock key could not be checked. (3) The stock polymer caps at y ≈ 157–168 are cans (height not measured; ≈ 6–8 mm is typical for this class [Estimate]) inside our assumed flat black-plate zone (y ≤ 164.4), so the plate must have a relief or a larger gap there → M-CC11 / M-CC2. Our board puts no tall part there, so this only changes the plate model, not the layout.
- **Height rule:**
  - Front ≤ **6.0 mm** (5.5 recommended) everywhere under the plate (x 16.2–140.4, y 22.5–164.4). That excludes polymer cans, the MCIO receptacle and memory sockets from the front.
  - The back holds J3 (MCIO RA), the 4 DIMM sockets, the M.2, BT1 and the bulk caps. **M-CC3 / M-CC15 (back clearance to the PSU) is a gating measurement** for J3, the M.2 and the DIMMs (≤ 33.25 mm, ≈ 1–2 mm above the stock DDR3 envelope, §4.2).

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
| U11 | eFuse, whole CB (U12 removed in fl2.1) | F | (36, 146) |
| LUG1, LUG2 | bus-bar lugs, single 12 V entry (no right pair) | F | (27.95, 159.8), (40.75, 159.8) |
| J1, CAC1 | CPU-LINK fingers, host TX AC caps | F/B | tab, y 15–23 |
| **J6, J7 / J9, J10** | **DDR5 UDIMM vertical sockets** (UMAX 90414 short latch): CH-A near/far, CH-B near/far | **B** | centrelines x 15.8 / 6.5 / 140.55 / 149.85, y 24.3–166.9 (courtyard 142.5 × 7.0); latch-open keep-out 152 on Dwgs |
| CB1, CB2 | 12 V bulk polymer (moved out of the strips in fl2) | B | x 19.7–36.3 / 120.2–136.8, y 39.7–70.3 |
| J8 | M.2 2280 boot (PCH x4) | B | y 13–36 |
| J3 | IOB-HS MCIO 124 RA (USB3/USB2/MDI/**2 × DDI**) | B | (78, 160), exits toward the top edge |
| U13, U14, BT1, CB1/CB2 | i226-V, ALC897 (DNP), CR2032, 12 V bulk | B | top |
| — | backplate keep-out | B | x 37.25–118.75, y 40–107 |

**Land-group check** (from the public ballout, drawn on Dwgs.User):
- DDR0/DDR1 exit the top edge (y 78–91): CH-A to J6 → J7 (left), CH-B to J9 → J10 (right), daisy chain.
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
| Socket ($5.79), RT3628AE ($2.18), 9 × SiC654 ($1.02), 4 × DDR5 DIMM socket (≈ $4.44, long-latch LCSC price as a proxy for the short latch), RP2350 ($1.30) | 2 × ≈ $27 | 5 × ≈ $27 | LCSC 2026-10-01 [N102][N108][N114][N115] |
| 9 × FP4 inductors, eFuses, bucks, SPI flash, i226-V, crystals, M.2 socket, ~1,500–2,500 passives | 2 × $100–180 | 5 × $100–180 | [Estimate]; no prices sourced for FP4/i226-V |
| Contact frame (CNC 7075) + steel backplate + springs/screws (2–5 sets) | $100–250 | $200–400 | JLC CNC/sheet-metal [Estimate] |
| Shipping, customs/duties | $100–200 | $150–250 | [Estimate] |
| **Subtotal (boards)** | **≈ $1.5k–2.6k** | **≈ $2.6k–4.4k** | |
| CPU i5-14500T tray | $254–300 each | | Aztek $253.91, SHI $283, Neutron $300.23 (2026-10-01) [N116] |
| DDR5 UDIMM 2–4 × 16–48 GB (JEDEC height, no heat spreader), NVMe | per user | | not sourced |
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
| R-L7 | **DDR5 2DPC routing to two side strips** (channels exit one edge; ≈ 60–125 mm + 9.3 mm daisy chain, under the VRM on the left) | Medium | Intel 2DPC speeds are low (3600–4400); intra-byte matching only; L8 under the VRM; FSP training; fallback fl1 SO-DIMM 1DPC or memory-down |
| R-L8 | **Front height ≤ 6.0** under the plate (inductors 5.0, caps ≤ 2.8) + thermal pads loading the board | Medium | FP4 / SEP0603 parts; height check per BOM line; soft pads with a force budget |
| R-L9 | **Firmware effort** (new coreboot mainboard, EC sequencing, VBT, OpenCore embedding) | High (time) | P6-0 on the real MSI board first; reuse ms7d25; OpenCore from the SATA SSD in rev A |
| R-L10 | **Back clearance to the PSU** for J3 (MCIO RA), the M.2 and the **4 vertical DIMMs (≤ 33.25 mm, ≈ +1–2 mm over stock DDR3)** (M-CC3 / M-CC15) | Medium | Measure; DIMMs → VLP 18.75 mm UDIMMs or fl1 SO-DIMMs; J3 → low-profile alternative |
| R-L14 | **DIMM socket variant**: the LCSC stock part is the long latch (does not fit the outer slots); short-latch availability unverified; open latches swing ≤ 2.1 / 4.4 mm past the outline | Low-Med | Order the UMAX short latch (or Amphenol DDR504/506 ≤ 142, TE 2355626); single-fixed-latch option; optional MP62 DIMM retainer bar |
| R-L15 | **Single 12 V entry** (fl2.1): ≈ 12 A sustained / 20 A peak through one lug pair (4 pins per lug) and one eFuse; lug x from a photo (±0.8 mm); which PSU pair feeds the CB unknown | Low-Med | Stock board did the same with a 130 W Xeon; L5+L6 12 V ≥ 20 mm; ILIM ≈ 25 A; M-CC16 caliper + continuity check before the footprint is frozen; right notch kept clear for the GPU bus bars (§6) |
| R-L11 | **Ballout orientation / socket footprint** (Intel X/Y view, Foxconn pad sizes) | Medium | Foxconn drawing; check the pin-1 corner against the package drawing (743844 vol 1 mechanical section) before routing |
| R-L12 | **Gen5 x16 over the CPU-LINK + BP + MCIO** | Low (policy Gen4) | Spec §3.6 unchanged: Gen4 default, optional BP redrivers |
| R-L13 | macOS lifetime (Tahoe is the last Intel macOS) | Accepted | Windows/Linux long-term; OpenCore until then |

**Go/no-go:**
- **GO now for P6-0 "de-risk"** (≈ 3–6 weeks, ≈ $400–900):
  - **G1 Firmware on the reference:** a used MSI PRO Z690-A DDR5 (or Z790-P). Build Dasharo from source; build the ME/descriptor with MFIT (HAP); boot OpenCore → Tahoe from SATA; test embedding OpenCore in the payload; test the iGPU/PEG primary-display options. Dump the RT3628 configuration and measure the sequencing.
  - **G2 Sourcing:** buy 3–5 Z790s from two sellers; inspect; confirm JLC consignment and BGA handling in writing; get an instant 10L quote and a DFM opinion on the PCH fan-out.
  - **G3 Schematic + routing study:** the PCH escape on 10L at JLC rules, plus DDR5 2DPC to J6/J7 and J9/J10 (use the fl2 floorplan).
  - **G4 Measurements:** M-CC3 / **M-CC15 (back clearance, now incl. the DIMM top ≤ 33.25 + float and the latch swing)**, M-CC7 (lug polarity), M-CC8 (boss thread), **M-CC16 (lug x by caliper, scan view, which PSU pair feeds the CB; right-tab part closed)**.
- **Gate G-A (rev-A order): CONDITIONAL GO** if G1 boots Tahoe with our own build, G2 yields authentic unfused PCHs and a JLC yes, and G3 shows the PCH and DDR5 routable.
  - **No-go triggers:** no ME/descriptor path; PCHs fused or fake; VR controller not configurable. In that case, fall back to the archived COM-HPC carrier (Size A) or memory-down variants.
- **Honest summary:**
  - The electrical design is feasible with public data plus a reference board, but it is **the hardest board in the project by far**.
  - The closed parts (PDG, IMVP, ME/FIT) are worked around, not solved.
  - Expect a rev B, and expect firmware bring-up to take months of evenings.

---

## 11. Decisions for Aidan

1. **D1 Chipset:** Z790 (recommended; reference parity) or B760 (RCP $26 lower, loose listings only ≈ €3–6 lower; DMI x4)?
2. **D2 ECC:** no (recommended) or W680 + ECC UDIMMs (CSME Corporate, no loose source found)?
3. **D3 Memory:** **4 × DDR5 UDIMM vertical, stock-like (fl2, recommended, gated on M-CC15)**, 4 × DDR4 UDIMM (separate board variant), or 2 × DDR5 SO-DIMM (fl1 fallback)?
4. **D4 CPU class:** design the VR for the 35 W T-series 6P+8E (120–160 A, 6 + 1 phases; recommended) or reserve 8 phases for 65 W 8P+16E?
5. **D5 ME approach:** MFIT build from the CSME kit (Win-Raid) vs the vendor-image ME region (both grey) with HAP; OK to proceed for personal use?
6. **D6 P6-0:** OK to buy a used MSI PRO Z690-A DDR5 / Z790-P as the firmware reference and 3–5 loose Z790s now?
7. **D7 iGPU ports:** DDI-B native DP + DDI-C into the USB-C DP-alt mux (proposed), HBR2 only, default "Primary display = Auto (PEG first)"?
8. **D8 OpenCore location for rev A:** keep it on the BP SATA M.2 (recommended), with embedding as the stretch?
9. **D9 Budget:** accept ≈ $1.5k–2.6k (2 boards) / $2.6k–4.4k (5 boards) plus a probable rev B?

---

## 12. Sources (also added to the spec as N84–N125)

- Aidan's stock CPU-board photos (2026-10-01 ~21:03 ET), CPU side and back with the 4 DIMM slots: `/workspace/mp62-spec-refs/photos/stock_cb_cpu_side.jpg`, `stock_cb_back_dimms.jpg` (homography `H_cpu.npy`, crops alongside) [spec N125].
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
- [N117] UMAX 90414 DDR5 UDIMM vertical SMT socket, drawing C-90414 rev 3 (LCSC datasheet): https://datasheet.lcsc.com/datasheet/pdf/28cf2deacb4c13dfe1244a30de7ae951.pdf?productCode=C2922443 ; LCSC C2922443 (90414-15011-21): https://www.lcsc.com/product-detail/C2922443.html ; C2922442 (90413-15011-21): https://www.lcsc.com/product-detail/C2922442.html
- [N118] Amphenol DDR5 product presentation (vertical DDR5 DIMM: length ≤ 142, width ≤ 6.5, height ≤ 21.3, seat ≤ 2.0; DDR504/DDR506; single fixed latch): https://cdn.amphenol-cs.com/media/wysiwyg/files/documentation/customerpresentation/ddr5_productpresentation.pdf
- [N119] TE DDR5 DIMM vertical SMT 1-2355626-1 / 8-2355632-1 datasheets: https://atta.szlcsc.com/upload/public/pdf/source/20241028/3906346FCF571F42CD4305C9D13F8559.pdf ; https://pdf.htelec.com/pdf/te/product-8-2355632-1.datasheet.pdf ; Digi-Key 2-2355626-1: https://www.digikey.com/en/products/result?keywords=2-2355626-1
- [N120] Intel 743844 vol 1, Processor SKU Support Matrix (DDR5 S Refresh UDIMM 1DPC 5600; 2DPC: 1 DIMM 4400 / 2 × 1R 4000 / 2 × 2R 3600; DDR4 3200; "far memory slot to be populated" for 1 DIMM on 2DPC): https://edc.intel.com/content/www/us/en/design/products/platforms/details/raptor-lake-s/13th-generation-core-processors-datasheet-volume-1-of-2/014/processor-sku-support-matrix/
- [N121] coreboot msi/ms7d25 `romstage_fsp_params.c` (BOARD_TYPE_DESKTOP_2DPC, SPD 0x50–0x53, DDR4 + DDR5): https://github.com/coreboot/coreboot/blob/main/src/mainboard/msi/ms7d25/romstage_fsp_params.c
- [N122] Apple HT6064 Mac Pro (Late 2013) memory specifications (4 slots, full-length DDR3 ECC, no heat sinks): https://web.archive.org/web/20140228151020/http:/support.apple.com/kb/HT6064 ; Micron 8 GB DDR3 RDIMM, module height 30 mm (29.85–30.50): https://file.icallin.com/r/datasheets/microntechnologyinc-mt18jsf1g72pdz1g6d1-datasheets-0683.pdf
- [N123] DDR5 VLP UDIMM 18.75 mm: Apacer https://www.apacer.com/en/product/industrial-product/detail/industrial_dram/ddr5_vlp_udimm ; Cervoz https://www.cervoz.com/products/ddr5-vlp-dimm/lists/unbuffered/standard-temp ; Innodisk https://www.innodisk.com/en/products/dram-modules/ddr5/ddr5-ecc-udimm-vlp
- [N124] UMAX 90411 DDR4 vertical SMT socket: LCSC C5889263 https://www.lcsc.com/product-detail/C5889263.html ; C5889264 https://www.lcsc.com/product-detail/C5889264.html
