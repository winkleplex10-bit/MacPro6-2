# MacPro6,2: CPU-board and GPU-board options shortlist

Research date and price-check date: **2026-09-30**. All prices are in USD, list price for quantity 1 on the date checked, unless noted.
Companion document: `/workspace/macpro61-stock-hardware-reference.md` (stock geometry, power and thermal data).
Numbered references like **[12]** point to §12, "Sources".

**How to read the tags**
- **[Inference]**: my own engineering reasoning. No source says it directly.
- **[Unverified]**: a source exists but I could not confirm it, or sources conflict.
- **[Price: quote]**: no public price was found.
- **Verdicts**: **Realistic** means buyable by a hobbyist today, with public docs, and assembly at JLCPCB/PCBWay-class shops is plausible. **Stretch** means possible, but one or more hard blockers need luck, vendor goodwill or reverse engineering. **Not feasible** means blocked by NDA, availability, legality or size.

---

## 0. TL;DR: recommended lineup

**Key architecture decision [Inference, from the specs below].** Design **one CPU board: a COM-HPC *Client* carrier that accepts Size C modules**. The Intel LGA1700, Intel Arrow Lake-S and AMD Strix Halo variants then become **module swaps on the same carrier and the same backplane**, not three separate PCB designs.
- COM-HPC Client is a vendor-neutral pinout. All three recommended modules are COM-HPC Client Size C (120 × 160 mm) [26][27][29][31].
- Sizes A and B use the same connector pair, so a Size C carrier may also take smaller modules. **[Unverified]**: check the mounting-hole pattern in the PICMG COM-HPC spec/CDG [38].

| Rank | CPU board variant | Why | Rough module cost (2026-09-30) | Verdict |
|---|---|---|---|---|
| **1 (build first)** | COM-HPC Client Size C carrier + **congatec/JUMPtec COMh-ccAS** (LGA1700, CPU-less) + a retail **35–65 W Raptor Lake** CPU (e.g. i5-14500T) | Cheapest publicly purchasable high-lane module. 16× PCIe Gen5 + 8× Gen4 + 6× Gen3 [26]. Raptor Lake is a proven OpenCore target through Tahoe [10][6]. The CPU is a cheap retail part. | Module $470.59–$570.25 [28] + CPU $232 RCP [33] | **Realistic** (fit risk: Size C is 160 mm long vs ~155 mm estimated face) |
| **2** | Same carrier + **Portwell PCOM-B887** (Arrow Lake-S, Core Ultra 200S) | Newest Intel with public OpenCore support (Arrow Lake detection since OC 1.0.3 [6]). Gen5 x16 + Gen5 x4 + 3× Gen4 x4, **USB4** on module [30]. Tahoe works on Z890 with quirks [8]. | **[Price: quote]** | **Realistic** (price/availability unknown; some Z890 instability reports [9]) |
| **3** | Same carrier + **congatec conga-HPC/cRX1** (AMD Ryzen AI Embedded X100 "Strix Halo") | AMD variant. 45–120 W, up to 24× Gen4, LPDDR5x soldered on module [31]. Best Linux/Windows performance. | **[Price: quote]** | **Realistic** for Linux/Windows. **Stretch** for macOS (Zen 5 hackintosh is new; no iGPU support) [6][13][14] |
| Alt. | COM Express Type 6 Basic **Kontron/JUMPtec COMe-bCL6** (Coffee Lake-H, i7-9850HL) on a *separate* COM Express carrier | The only module found whose **iGPU (UHD 630) is macOS-native through Tahoe**. It matches the MacBookPro16,1 class [2][11]. Enables a true iGPU-only macOS variant. | $941.18 (i3) / $1,513.00 (i7) [34] | **Realistic** but old, costly, and needs a second carrier design |

| Rank | GPU approach | Why | Cost | Verdict |
|---|---|---|---|---|
| **1 (build first)** | **Own MXM 3.1 Type B carrier board per GPU face** + **X-VSION MXM Radeon RX 6600 8 GB** (Navi 23) | Navi 23 is **macOS-native** (12.1 → Tahoe) [15][17]. 100 W TBP per vendor, PCIe 4.0 x8, 82 × 105 mm, in stock [40]. It sits inside the ~100–130 W per-face envelope. The MXM connector is a $11 DigiKey part [45]. | $280 each [40] | **Realistic** (MXM-RX6600-under-macOS not yet confirmed by any report; TBP conflict 75 vs 100 W [41]) |
| **2** | **iGPU-only variant** (no GPU boards; rear video from CPU-board DDI) | Cheapest and lowest power. Works on Linux/Windows with any module. For macOS it requires the Coffee Lake UHD 630 alternate module [11]. | $0 GPU | **Realistic** (Linux/Windows); macOS only with COMe-bCL6 |
| **3** | **Reuse stock FirePro D300/D500/D700 boards** on the new backplane | Zero hardware cost (already owned). Needs the undocumented GPU-flex/MEG-Array pinout reverse-engineered. GCN1 drivers are decaying (macOS only via OCLP; Windows only via community drivers) [47][48][50]. | $0 | **Stretch** |

**Build order [Inference]:**
1. Backplane v0 with the MCU on the bench with the stock PSU: fan PWM/tach, PS_ON, standby, Hall interlock.
2. COM-HPC carrier + COMh-ccAS + i5-14500T with **one** MXM RX 6600 on the GPU-B face, which drives rear video. Bring up Linux first, then OpenCore/macOS Tahoe.
3. Second MXM on the GPU-A face.
4. Module swaps (Arrow Lake, then AMD).

---

## 1. Findings that change the project plan

1. **macOS on this build ends at Tahoe (26).**
   - macOS 27 shipped for Apple silicon only. Apple says Intel Macs get security updates for about 3 more years (to roughly 2028) [1][2][3].
   - Every x86 option below, Intel or AMD, is capped at Tahoe. A macOS-first design has a shelf life of about 2–3 years of security patches.
   - This argues for **Linux/Windows being first-class**, with macOS as a strong "nice to have".
2. **Navi 22 (RX 6700/6700 XT) is *not* natively supported in macOS.** This corrects the brief. Apple never shipped Navi 22. Only Navi 21 and Navi 23 (plus RDNA1 Navi 10/14, Vega, Polaris) are native. Navi 24 is unsupported [15][17][19].
   - Nvidia is dead on modern macOS: all Nvidia, including Kepler, was dropped in Monterey [16].
   - RDNA3/RDNA4 have no driver [17].
   - So the macOS-capable GPU list is **Polaris / Vega / Navi 10/14 / Navi 21 / Navi 23**.
3. **Intel iGPUs after Ice Lake are not macOS-capable.**
   - UHD 770 (Alder/Raptor Lake), Xe (Tiger Lake+), Arrow Lake and Meteor Lake graphics all need a dGPU for macOS [10][11].
   - AMD RDNA iGPUs (Ryzen 7000+/Strix/Strix Halo) are unsupported. NootedRed only covers Vega-based APUs [14].
   - An "iGPU-only macOS variant" therefore means **Coffee/Comet Lake UHD 630 or Ice Lake**. Among modules, only the old Coffee Lake COM Express parts qualify [11][34].
4. **"OpenCore embedded in UEFI" is not realistic on commercial COM modules.**
   - Every module found ships closed **AMI Aptio** firmware. Custom UEFI is available only by contacting the vendor [26][27][31].
   - No public precedent was found for OpenCore embedded in a firmware image. The nearest community advice is to chain-load OpenCore from an ESP after a UEFI payload [21].
   - The realistic plan is a "firmware-like" OpenCore on a dedicated on-board boot device, registered as a firmware boot option via `LauncherOption` [22]. See §9.
   - True embedding is a stretch or research track: coreboot-capable modules (Prodrive Atlas, Kontron COMe-bSL6, LattePanda Mu) or vendor NRE [23].
5. **Kontron's module business is now congatec (JUMPtec).**
   - congatec bought 96% of JUMPtec in July 2025 and now sells the former Kontron COMh-/COMe- lines [36][37].
   - This explains why WDL lists "congatec COMh-ccAS". It also means congatec is the single supplier for the #1 and #3 modules.
6. **Buying modules as a private person is possible but not universal.**
   - module-store.com states that it sells only to OEMs, not private persons [35].
   - WDL Systems shows public web prices with a shop cart [28][34]. Shipping to an individual is **[Unverified]**; check before ordering.
7. **Framework Intel mainboards are BootGuard-locked.** coreboot's own docs state flashing "will not result in a bootable system" on retail Marigold/Sakura/Sunflower boards [23c]. The FW16 board is also far too large for a core face (§3.3).
8. **The COM-HPC Size C length is the #1 mechanical risk.**
   - The module is 160 mm long [26]. My photo-scaled estimate of the stock CPU riser is about 130 × 155 mm ±15% (stock reference §5). **Measure before committing.**
   - Size A (95 × 120) and Size B (120 × 120) mobile-class modules are the fallback. They trade x16 for x8 + x4 lanes (§3.1).
9. **MXM RX 6600 exists cheaply ($280), is Navi 23 (macOS-native), and fits the per-face thermal budget.** This makes "own GPU carrier boards" realistic, where designing a GPU from chips is not.

---

## 2. Ground truth used to judge macOS viability (checked 2026-09-30)

| Topic | Current state | Sources |
|---|---|---|
| Last Intel macOS | **macOS 26 Tahoe**. macOS 27 is Apple-silicon only (released Sept 2026). Intel security updates continue for about 3 years. | [1][2][3] |
| Tahoe-supported Intel Macs (SMBIOS targets) | MacPro7,1; iMac 2020 (iMac20,1/20,2); MacBook Pro 16" 2019; MacBook Pro 13" 2020 (4-port) | [1][2] |
| SMBIOS caveat | On Tahoe, MacPro7,1 SMBIOS reportedly needs a board-id check skip. iMac20,x does not. SMBIOSes that assume an iGPU (iMac) must not be used on iGPU-less setups; use MacPro/iMacPro instead. | [5][18] |
| OpenCore | 1.0.8 released 27 Sep 2026. 1.0.7 improved Tahoe XhciPortLimit. 1.0.3 added Arrow Lake detection and fixed Raptor Lake detection. 1.0.2/1.0.3 added AMD family 1Ah (Zen 5). | [6] |
| Alder/Raptor Lake | Works via CPUID spoof to Comet Lake. UHD 770 unsupported, so a dGPU is required. | [10] |
| Arrow Lake | Z890 builds run Sequoia and Tahoe 26.0.1 (ProvideCurrentCpuInfo + AppleMCEReporterDisabler). Some instability reports. | [7][8][9] |
| AMD CPUs | AMD Vanilla patches support 15h/16h/17h/19h through Tahoe. Zen 5 (1Ah) handling is in OpenCore 1.0.2+. **[Unverified]**: how mature Zen 5 hackintoshes are in practice. | [6][13] |
| Intel iGPU | UHD 630 (Coffee/Comet Lake) and Ice Lake Iris Plus supported. Tiger Lake and newer unsupported. | [11][12] |
| AMD iGPU | NootedRed: Vega-based APUs only (Raven/Picasso/Renoir/Cezanne family), 10.15–26. RDNA iGPUs unsupported. | [14] |
| AMD dGPU | Native: Polaris, Vega, Navi 10/14, Navi 21, Navi 23 (RX 6600/6600 XT id 73FF, W6600). Navi 23 usually needs `agdpmod=pikera`. Navi 22 needs the WIP NootRX. Navi 24, RDNA3 and RDNA4 are unsupported. Binned "RX 580 2048SP" and Lexa-based RX 550s do not work natively. | [15][17][19][20] |
| Nvidia | Unsupported since Monterey (all generations). | [16] |

---

## 3. CPU options

### 3.0 CPU comparison table

Stock CPU face for reference: ~130 × 155 mm (estimate, ±15%). Stock CPU was 130 W TDP. Measured on Aidan's unit: 130 W 10-core at 65–70 °C with the fan at 1900 RPM.

| # | Option | CPU gen / TDP | Board size vs face | PCIe for GPUs + storage/IO | Memory | Hobbyist availability & price (2026-09-30) | Firmware openness | macOS viability | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| A1-a | **congatec/JUMPtec COMh-ccAS** (COM-HPC Client C) | LGA1700 Alder/Raptor/Raptor Refresh, **35–65 W**, up to 16 cores [26] | 160 × 120 mm: **longer than ~155 mm estimate** | 16× Gen5 (PEG) + 8× Gen4 + 6× Gen3; 4× USB 3.2 [26]. CPU supports 1×16 or 2×8 (+4) [33]; module BIOS bifurcation not stated **[Unverified]** | 2× DDR5 SO-DIMM on module (4 on request) [26] | WDL, CPU-less: H610 $470.59; H610E $485.81; Q670 $555.01; Q670E $564.71; W680 $564.71; R680E $570.25 [28]. Plus retail CPU (i5-14500T RCP $232 [33]; i5-13500T $242.79 Newegg [33b]) | AMI UEFI; "contact tech support for custom UEFI" [26]. No coreboot port. | Good: Raptor Lake via OC (Comet Lake spoof), dGPU required, Tahoe OK [10][6] | **Realistic** (fit risk) |
| A1-b | congatec conga-HPC/cRLS (Client C) | Raptor Lake-S E-series, 65 W (i3-13100E … i9-13900E) [27][27b] | 160 × 120 | PEG 1×16 Gen5, **BIOS-configurable 2×8**; 3× Gen4 x4; 3× Gen3 x4; 4× USB 3.2 Gen2x2 [27] | 4× DDR5 SO-DIMM, up to 192 GB [27] | **[Price: quote]**; module-store refuses private buyers [35] | AMI Aptio [27] | Same as A1-a | **Realistic** if a seller is found |
| A1-c | ADLINK COM-HPC-cRLS (Client C) | Raptor Lake-S E, 65 W [32] | 160 × 120 | Similar class [32] | SO-DIMM | WDL: i7-13700E $1,509.21; i9-13900E $1,908.65 [28] | Vendor AMI-class BIOS **[Unverified]** | Same as A1-a | **Realistic** but about 2.5× the cost of A1-a + CPU |
| A1-d | **Portwell PCOM-B887** (Client C) | Arrow Lake-S Core Ultra 200S, socketed LGA1851 [30] | 160 × 120 | Gen5 x16 + Gen5 x4 + 3× Gen4 x4 + Gen4 x2 + 8× Gen4 x1; **USB4** [30] | 4× DDR5 SO-DIMM up to 192 GB [30] | **[Price: quote]** | Vendor BIOS **[Unverified type]** | Arrow Lake: OC 1.0.3+, Tahoe with quirks [6][8]; instability reports [9] | **Realistic** (price TBD) |
| A1-e | congatec conga-HPC/cBLS (Client C) | Bartlett Lake-S (Core 7 251E, 5 211E, 3 201E), 60–65 W [27c] | 160 × 120 | Up to 42 lanes (16 Gen5 + up to 12 Gen4) [27c] | DDR5 (ECC capable) [27c] | **[Price: quote]** | AMI **[Unverified]** | **[Unverified]**: no OpenCore report found for Bartlett Lake | **Stretch** (macOS unknown) |
| A1-f | Size A/B mobile modules: **COMh-caAP** (ADL-P/H, A), COMh-caRP (RPL-P, A), conga-HPC/cRLP (RPL-P, A), TRIA HCA-RLP (A), **Portwell PCOM-B886** (Arrow Lake-H/U, B) | 15–45 W class H/P/U | **95 × 120 (A) / 120 × 120 (B): best fit** | Size A H-SKU: x8 PEG (Gen4/Gen5) + 2× Gen4 x4 + up to 8× Gen3 + 2× Thunderbolt [39][39b][39c]. B886: Gen5 x8 + 2× Gen4 x4 + 2× USB4 [30b] | 2× DDR5 SO-DIMM (cRLP up to 64 GB) [39b] | WDL: COMh-caAP i3-12300HE **$820.76**; i7-12800HE **$1,548.79** [28b]. Others **[Price: quote]** | AMI-class **[Unverified]** | ADL/RPL mobile via spoof, dGPU needed [10]; Arrow Lake-H **[Unverified]** | **Realistic** (fallback if Size C doesn't fit; GPU B gets x4) |
| A1-g | **congatec conga-HPC/cRX1** (Client C) | AMD Ryzen AI Embedded X199/X188/X168 (Zen 5, 16/12/8 cores), **45–120 W** [31] | 160 × 120 | Up to 24× Gen4 (assembly option), optional onboard PCIe switch [31] | 32/64/128 GB **LPDDR5x-8533 soldered** [31] | **[Price: quote]** (PNs 053700–053712) [31] | AMI Aptio [31]. coreboot has an AMD Strix Halo *reference board* ("maple") upstream [23e], but no module port | Zen 5 via OC 1Ah + AMD Vanilla; RDNA3.5 iGPU unsupported, dGPU required [6][13][14] | **Realistic** (Linux/Win); **Stretch** (macOS) |
| A2-a | **Kontron/JUMPtec COMe-bCL6** (COM Express Type 6 Basic) and equivalents (ADLINK Express-CFR, SECO OBERON) | Coffee Lake-H (i3-9100HL … i7-9850HL), CM246/QM370 [34b] | 125 × 95: fits | Type 6 PEG port (x16 Gen3 class) + PCH lanes **[Unverified lane map; check manual]** | SO-DIMM DDR4 **[Unverified]** | WDL: i3-9100HL $941.18; i7-9850HL $1,513.00; ADLINK Express-CFR i7-9850HL $1,352.43; SECO OBERON i7-9850HL $1,471 [34] | AMI-class. (Older sibling COMe-bSL6 Skylake has an upstream coreboot port [23b].) | **Best native macOS**: Coffee Lake-H + **UHD 630 native** (MacBookPro16,1 class, Tahoe-supported) [2][11] | **Realistic** (old/costly; separate carrier) |
| A2-b | Newer COM Express Type 6 (ADLINK Express-TL, Express-RLP, COMe-bRP6) | Tiger/Raptor Lake-P/H | 125 × 95 | Type 6 PEG + PCH lanes | SO-DIMM | WDL: Express-TL i3-11100HE $865.72; Express-RLP i3-1315UE $797.55, i7-13800HE $1,481.94; COMe-bRP6 i7-1370PE $1,471.28 [34] | AMI-class | dGPU required (Xe unsupported) [11] | **Stretch**: no advantage over COM-HPC; fewer lanes |
| A2-c | congatec **conga-TCV2** (COM Express Type 6 Compact) | AMD Ryzen Embedded V2000 (Zen 2), 10–54 W; Vega iGPU up to 7 CU [42] | 95 × 95: fits easily | PEG x8 Gen3 (default 2×x4, BIOS 1×x8) + 8× Gen3 lanes [42b] | 2× DDR4 SO-DIMM ≤64 GB [42c] | **[Price: quote]** | AMI | Zen 2 via AMD Vanilla [13]; Vega iGPU *maybe* via NootedRed (Renoir-family) **[Unverified for V2000]** [14] | **Stretch** (lane-starved; only AMD "iGPU macOS" candidate) |
| A2-d | coreboot-supported COM Express: **Prodrive Atlas** (Compact T6/T10, ADL-P/RPL-P), Kontron COMe-bSL6 (Skylake) | ADL-P/RPL-P; Skylake | 95 × 95 / 125 × 95 | Atlas: 1× Gen5 x8, 2× Gen4 x4 [43] | SO-DIMM **[Unverified]** | **[Price: quote]**; availability to individuals unknown | **Open**: upstream coreboot [23a][23b] | ADL/RPL: dGPU needed; Skylake: supported CPU, HD 530 iGPU only to older macOS **[Unverified]** | **Stretch** (the "true OpenCore-in-firmware" research path) |
| A3-a | **Framework Laptop 16 mainboard** (Ryzen AI 300) | Zen 5 mobile | **About 336 × 170 mm (my reading of the published 2D drawing) [44b]: does not fit** | Expansion bay **PCIe Gen4 x8** (open CC-BY spec) + 2× M.2 [44][44c] | SO-DIMM DDR5 | AI 5 340 $499 (pre-order), AI 7 350 $749, AI 9 HX 370 $1,049 [44a] | Vendor firmware; no coreboot port for FW16 in the coreboot tree [23] | One MXM on x8 max; AMD caveats | **Not feasible** (size); OK as a bench dev mule |
| A3-b | Framework 13 mainboards (Intel/AMD) | Mobile | Too large, laptop outline [44d] | No x8 PCIe slot; USB4/M.2 only **[Inference]** | SO-DIMM/LPDDR | From $449 (AI 300) [44e] | **Intel boards BootGuard-locked** [23c]; AMD Azalea coreboot is a proof of concept, "not production quality" [23d] | — | **Not feasible** |
| A3-c | **LattePanda Mu** (SoM) | Intel N100/N305, 9–35 W [46] | Small SoM | 9× PCIe 3.0 [46] | LPDDR5 soldered [46] | About $140 (Hackaday comment) [46b] | **Open**: upstream coreboot port, docs say to copy a variant for custom carriers (FSP/ME/IFD blobs needed) [23f]; open KiCad carriers [46] | Too weak for the goal; N-series iGPU unsupported | **Not feasible** as the main CPU; **great firmware/OpenCore-embedding dev mule** |
| A4 | **Raw socket board** (LGA1700/LGA1851 + PCH, or AM5 + Promontory) | Desktop 35–125 W+ | Needs own full board | Everything | DIMMs on own board | CPUs are buyable (retail). **PCH/Promontory not sold to hobbyists through distributors; Intel PDG/CRB schematics require an Intel RDC account with restricted collections** [24]. AMD AGESA/PSP is NDA; openSIL client support is Phoenix only [25] | FSP binaries public (incl. RPL-S) [24b]; ME/IFD, PDG, CRB not public. Open precedents exist **only as ports to retail boards** (Dasharo MSI Z690/Z790/B760; 3mdeb MSI B850-P on openSIL) [23g][25] | Would be ideal if it existed | **Not feasible** (legal/doc access + DDR5/PCIe5 layout + 10+ layer board) |
| A5 | **Soldered BGA mobile CPU on own board** | e.g. Intel i7-13800HE FCBGA1744 50 × 25 mm, RCP $460 [24c]; AMD Ryzen Embedded V3000 BGA 25 × 35 mm, 10–54 W, 20× Gen4 [24d]; Ryzen Embedded 8845HS FP7r2 [24e] | Own board | SoC lanes | Own DDR5 routing | Intel embedded BGA parts are listed at Mouser (e.g. i3-13300HE $511.39 per search snippet **[Unverified]**) | Needs NDA PDG/reference schematics, FSP/ME or AGESA/PSP. The only hobby precedent (DIY Ryzen board) used **"leaked" documentation**, chips from likely unauthorized sellers, and BIOS copied from a laptop [24f] | Would work like a laptop hackintosh | **Not feasible** legally/practically (**Stretch** only with a vendor NDA) |

### 3.1 Notes per option

**A1: COM-HPC Client (primary recommendation).**
- *Why COM-HPC over COM Express:*
  - Gen5 x16 PEG plus many Gen4 lanes on desktop-socket modules [26][27][30].
  - A single 12 V input rated up to 251 W on Size C (stock reference §5, [38]).
  - Public carrier design guide: the PICMG COM-HPC Carrier Design Guide R2.2 is a free download [38].
  - Carrier connectors are stocked at DigiKey: Samtec **ASP-214802-01** (5 mm stack) $42.65, 33 in stock; **ASP-209948-01** (10 mm stack) $48.01, 6 in stock. Two per carrier [45b].
  - The full COM-HPC base spec is a separate PICMG document; only an abridged spec is linked publicly [38b]. **[Unverified]**: price and access to the full spec.
- *Lane budget for the stock-like topology (COMh-ccAS):*
  - x16 Gen5 PEG split 2×8 feeds GPU A and GPU B (MXM RX 6600 is x8 Gen4 [40], so x8 loses nothing).
  - 8× Gen4 feeds NVMe x4 and an x4 uplink toward an I/O switch/USB4 controller.
  - 6× Gen3 feeds Ethernet, Wi-Fi and so on.
  - **Verify PEG 2×8 bifurcation support in the ccAS BIOS.** The CPU supports it [33]. congatec's cRLS documents it explicitly [27]. The ccAS datasheet is silent [26].
- *CPU choice for A1-a:*
  - The ccAS datasheet limits it to **35–65 W and ≤16 cores** [26]. An i5-14500T (14 cores, 35 W base / 92 W max turbo, RCP $232) [33] or an i5-14500 (65 W) fits. An i7-14700 (20 cores) may be out of module spec **[Inference; check the module's validated CPU list]**.
  - Given the measured headroom (130 W CPU at 65–70 °C at max fan), a 65 W part with PL2 capped at about 100–125 W should be thermally comfortable. **[Inference]**: the module heatspreader adds a thermal interface versus the stock direct-IHS contact.
- *Chipset SKU:*
  - H610 is cheapest ($470.59) but has fewer PCH lanes/USB.
  - Q670E/R680E ($564.71/$570.25) are embedded-grade [28].
  - For a hackintosh there is no macOS-specific chipset preference. Pick by I/O count **[Inference]**.

**A1-g: AMD Strix Halo (cRX1).** This is a strong Linux/Windows board: up to 16 Zen 5 cores, 40-CU RDNA 3.5, 45–120 W [31]. For macOS:
- the iGPU is unusable [14], so a Navi 23 MXM is needed;
- AMD hackintoshes carry the usual AMD Vanilla limitations [13];
- Zen 5 support is recent [6].
Memory is soldered, so there is no SO-DIMM on the module. At 120 W it takes the whole stock CPU-face budget.

**A2: COM Express.** Type 6 has fewer, older lanes than COM-HPC.
- Its unique value is the **Coffee Lake-H COMe-bCL6** [34b]. It is basically the silicon of the Tahoe-supported MacBook Pro 16" 2019, with UHD 630, which is the only **iGPU-only** macOS path [2][11].
- Carrier connectors: TE **3-1827253-6** (220-pos, 5 mm), DigiKey $27.23 qty 1 [45c]. A Type 6 carrier needs two **[Inference from the 440-pin COM Express pinout]**.
- There is an open-source KiCad **COM Express Type 7** baseboard by Antmicro [53]. Type 7 is a server pinout without video, so it is reusable only for the layout approach.

**A3: SoMs/mini boards.**
- Framework boards are the most open consumer x86 boards, with published drawings, interface schematics and an open expansion-bay spec [44][44c].
- But the FW16 board is far too large for a core face [44b]. Intel FW13-class boards are BootGuard-locked [23c].
- LattePanda Mu is the best **open-firmware sandbox**: an upstream coreboot port, and the docs explicitly support custom carriers [23f][46]. It is not a CPU-board candidate.
- Intel NUC compute elements were not evaluated further (not researched).

**A4/A5: own CPU silicon.** Honest verdict: **not feasible** for a hobby build.
- Intel's platform design guides and reference schematics sit behind RDC accounts with restricted collections [24].
- AMD's AGESA/PSP is NDA. openSIL covers only Phoenix on client, with Zen 6 targeted for 2026–27 [25].
- Chipsets are not sold through Mouser/DigiKey.
- The one hobby Ryzen board relied on leaked docs and gray-market chips [24f].
- CPUs themselves *are* buyable (Intel embedded BGA RCP $460 for i7-13800HE [24c]). Documents, chipset and firmware are the blockers, not silicon.

---

## 4. GPU options

### 4.0 GPU comparison table

Per-face budget: about 100–130 W (stock reference §4.2). Rear video in the stock design comes from **GPU B** DP0–5 through the I/O board.

| # | Option | TDP | PCIe | Display outputs | Size | Availability & price (2026-09-30) | macOS | Windows / Linux | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| B1-a | **X-VSION MXM Radeon RX 6600 8 GB** (Navi 23) | **100 W TBP (vendor)** [40]; the HIS-made MXM RX 6600 teardown says **VBIOS fixed at 75 W**, pushable past 130 W, 10 phases, no fan header [41] **[Conflict]** | PCIe 4.0 x8 [40] | DP (count per listing, **verify**) [40] | MXM 3.0/3.1 Type B, 82 × 105 mm [40] | **$280, in stock** [40] | **Native** (Navi 23, 12.1 → Tahoe, `agdpmod=pikera` typical) [15][17]. MXM variant not yet reported under macOS **[Unverified]**; UEFI GOP presence unknown | Current AMD RDNA2 drivers / amdgpu | **Realistic (recommended)** |
| B1-b | X-VSION MXM RX 6600 XT 8 GB | 100 W [40b] | 4.0 x8 | DP | Type B | **Out of stock** [40b]; eBay listing, MXM 3.1 Type B, $299 [40c] | Native (73FF) [15] | Same | **Realistic** (supply-limited) |
| B1-c | X-VSION MXM RX 5500 XT 8 GB (Navi 14) | 100 W [40d] | 4.0 x8 [40d] | DP | Type B | $200, in stock [40d] | **Native** since 10.15.1; pikera often needed [15][17] | Current drivers | **Realistic** (budget fallback) |
| B1-d | X-VSION MXM RX 580 8 GB (Polaris) | 120 W [40e] | 3.0 x16 [40e] | **6× DP** [40e] | MXM 3.1 Type B | $220 [40e] | Native through Tahoe (avoid 2048SP bins) [17][20] | **Windows: Polaris moved to AMD's legacy maintenance branch with Adrenalin 26.5.2** [49] | **Realistic w/ caveats** (hot for a face; aging) |
| B1-e | X-VSION E9174 4 GB / RX 550 / R5 230 | — | — | — | Type A/B | $200 / $130 / $50 [40f] | E9174 die **[Unverified]** (likely Polaris 12, unsupported); RX 550 Lexa not native [20] | OK | **Not recommended** |
| B1-f | Nvidia MXM (e.g. Advantech SKY-MXM-A1000 Type A 60 W; SKY-MXM-A4500 Type B+ 115 W, Gen3 x16) | 60 / 115 W [52] | Gen3 x8 / x16 [52] | DP 1.4a [52] | 82 × 70 / 82 × 105 [52] | Not priced | **None** [16] | Good | **Realistic** only for a Linux/Windows-only variant |
| B1-conn | MXM connector | — | — | — | — | **JAE MM70-314B1-2-R300** (replaces EOL MM70-314-310B1-1-R300, same footprint, 6.7 mm): DigiKey **$11.16**, 3,305 in stock; alt. ATTEND 125B-78C00 $16.69 [45]. Rated 30 mating cycles [45a] | — | — | Realistic |
| B2 | Embedded AMD GPU as discrete BGA | — | — | — | — | Not found at Mouser/DigiKey-class distributors in this search; the only embedded RDNA2 option found is the MXM module form above | — | — | **Not feasible** (as BGA) |
| B3 | **CPU iGPU only** | 0 W extra | — | Module DDI ×3 (+eDP) [26][27] | — | $0 | Only UHD 630/Ice Lake native [11]. UHD 770, Xe and RDNA3.5 are not [10][14] | Fine on all modules | **Realistic** (Linux/Win); macOS only with A2-a |
| B4 | **Discrete GPU die on our own board** | 100 W+ | — | — | — | AMD/Nvidia GPU dies are not sold through hobby distributors (none found). A 100 W Navi 23 board needs a 10-phase VRM (per the MXM teardown [41]), GDDR6 routing and a VBIOS | — | — | **Not feasible** |
| B5 | **Stock FirePro D300/D500/D700 boards** (GCN1 Pitcairn/Tahiti) | ≈100–130 W/face (estimate) | x16 Gen3 over stock flex | DP0–5 (GPU B) | Stock | Owned | OCLP supports MacPro6,1 as "Legacy Metal (macOS 13+)" [47]. Sequoia works with glitches; D300 most problematic [48]. Tahoe only via OCLP 3.0 beta [50][50b]. **On a hackintosh backplane: untested [Inference]** | **Windows: AMD's current Adrenalin is not for Boot Camp; community drivers (bootcampdrivers.com Adrenalin 24.10.1 mod, updated 2025-03-23; R.ID GCN1) [51][51b]. Linux: amdgpu default for GCN1 since 6.19, some early hang reports [51c]** | **Stretch** |

### 4.1 Notes

- **MXM is the only realistic "replaceable GPU" path.**
  - PWR_SRC accepts **7–20 V** (6.5–22 V absolute) plus 5 V and 3.3 V rails [52]. The bus-bar 12.1 V can feed PWR_SRC directly. The carrier only needs small 5 V and 3.3 V bucks. A Clevo schematic budgets PWR_SRC 10 A, 5 V 2.5 A and 3.3 V 1 A [52b].
  - Rule from the Advantech MXM manual: *no voltage on MXM signal pins until PWR_GOOD is asserted* [52]. The MCU/backplane must sequence this.
- **Orientation [Inference]:** on MXM cards the GPU die and VRAM sit on the side away from the host connector (laptop heatsink side). A carrier mounted "behind" the card presents the die to the core face, like the stock boards. VRAM pad thickness must be worked out per card; Apple itself used different pad kits for D300 and D500/D700 (stock reference §4.3).
- **Display count:**
  - The stock I/O board expects up to 6 DP streams from GPU B (3× TB2 controllers + HDMI) (stock reference §0.3).
  - The RX 580 MXM offers 6× DP [40e]. The RX 6600 MXM output count must be checked [40]. Desktop Navi 23 drives 4 displays **[Unverified for MXM]**.
  - With four outputs, map 3 to the TB2 controllers and 1 to HDMI **[Inference]**.
- **macOS unknowns specific to MXM Navi 23:**
  1. Whether the VBIOS includes a UEFI GOP. Without it there is no pre-boot picker on that GPU. The iMac MXM community had to build EFI VBIOSes for older MXM cards [19b].
  2. Whether macOS accepts the MXM board's device-id/VBIOS as-is.
  Neither is confirmed.

---

## 5. Recommended lineup (ranked by feasibility and cost)

### CPU board variants
1. **"MP6,2-RPL": COM-HPC Size C carrier + COMh-ccAS + i5-14500T (build first).**
   - Module $470.59–$570.25 [28] + CPU $232 [33]. The cheapest high-lane option you can actually buy.
   - Raptor Lake OpenCore is well trodden [10].
   - The same carrier later takes variants 2 and 3.
2. **"MP6,2-ARL": same carrier + Portwell PCOM-B887 (Arrow Lake-S).**
   - Newer CPU, on-module USB4 [30]. Arrow Lake runs Tahoe with quirks [8].
   - Price TBD. Some stability reports to watch [9].
3. **"MP6,2-AMD": same carrier + congatec conga-HPC/cRX1.**
   - Best Linux/Windows performance and efficiency [31]. macOS is experimental.
   - Price TBD, probably the most expensive module **[Inference]**.
- *Optional side variant:* **"MP6,2-CFL" (COM Express COMe-bCL6, UHD 630)**. Build it only if an iGPU-only, most-native-macOS box is wanted. It needs its own COM Express carrier. $941.18–$1,513.00 [34].
- *If Size C doesn't fit the CPU face:* use a Size A/B carrier with **COMh-caAP** ($820.76/$1,548.79) [28b], conga-HPC/cRLP, or **Portwell PCOM-B886** (Arrow Lake-H) [30b]. GPU B then drops to x4 (see §6).

### GPU approaches
1. **MXM Type B carrier boards + RX 6600 MXM** ($280 each; RX 5500 XT $200 fallback) [40][40d]. Both faces: 2× ~100 W.
2. **iGPU-only** (no GPU boards). Linux/Windows on any module, or macOS on the CFL variant. Rear video must then come from CPU-board DDI through the backplane.
3. **Stock D-series reuse.** Keep as a stretch/"museum" option. Only attempt it after the MEG-Array/flex pinout is mapped.

### Indicative first-build BOM (prices checked 2026-09-30; PCB fab/assembly and RAM not included)

| Item | Price | Source |
|---|---|---|
| COMh-ccAS Q670E (CPU-less) | $564.71 | [28] |
| Intel i5-14500T | $232 (RCP) | [33] |
| 2× MXM RX 6600 | 2 × $280 | [40] |
| 2× Samtec ASP-214802-01 COM-HPC plug (5 mm) | 2 × $42.65 | [45b] |
| 2× JAE MM70-314B1-2-R300 MXM connector | 2 × $11.16 | [45] |
| **Subtotal** | **≈ $1,464** + DDR5 SO-DIMMs + PCBs | — |

---

## 6. What each choice implies for the backplane spec

All of this is **[Inference]** from the module, MXM and PSU specs cited.

**Signals on the CPU-board card edge (to the backplane)**

| Group | Variant 1/2/3 (COM-HPC C + 2× MXM) | Size A/B fallback | iGPU-only / CFL variant |
|---|---|---|---|
| GPU A link | PCIe x8 (Gen4 is enough for RX 6600; Gen5-capable source) | x8 | — |
| GPU B link | PCIe x8 | **x4** Gen4 | — |
| I/O-board uplink (stock PEX8723 wants x8 Gen3) | x4–x8 from Gen4/Gen3 pool | x4 | x4 |
| NVMe | Prefer M.2 **on the CPU carrier** (saves edge pins); or x4 to backplane | same | same |
| USB | USB 3.2 ×4 + USB 2.0 ×8 (module-dependent) [26][27]; USB4 ×2 on B887/B886 [30][30b] | TB/USB4 on H-series | USB 3.x |
| Video | From GPU B (MXM DP) to the I/O board, *not* through the CPU edge | same | **DDI ×3 from the CPU edge** → backplane → I/O board |
| Ethernet | 2× 2.5GbE (i226 on module) as MDI to the I/O board, or keep on the carrier [39b] | same | same |
| Mgmt | SMBus/I²C (module board controller + MXM thermal SMBus), PWR_BTN#, RESET#, SUS_S3#/S5#, PWR_OK, THERMTRIP#, fan tach/PWM | same | same |

- **Edge connector:** we choose it, since the stock ~324-contact slot is unknown (stock reference §0.5). Use a PCIe-Gen4-rated card-edge part. **Keep PCIe at Gen4 or lower across all edges and flexes.** Plan a "force Gen3" BIOS fallback in case MEG-Array + flex signal integrity is marginal. MEG-Array SI at 16 GT/s is unverified.
- **GPU faces:**
  - Each face gets an MXM carrier: MXM connector [45] + PWR_SRC from the 12.1 V bus bar + local 5 V/3.3 V bucks [52][52b] + an MEG-Array flex to the backplane.
  - GPU B's carrier must route its DP outputs back through the flex to the I/O board, as in the stock design.
- **Power budget (12.1 V rail = 37.2 A ≈ 450 W):**

| Load | Variant 1 | Variant 3 (AMD) | Note |
|---|---|---|---|
| CPU module | 65 W PBP / cap PL2 ≈ 100–125 W | up to 120 W [31] | COM-HPC C allows up to 251 W [38] |
| 2× MXM RX 6600 | 2 × 100 W [40] | 2 × 100 W | 75 W if the VBIOS limit holds [41] |
| Backplane + I/O + SSD + fan | ~30–40 W (estimate) | same | [Inference] |
| **Peak** | **≈ 330–365 W** | **≈ 350–360 W** | Under 450 W with ≥ 20% margin. Stock measured 437–463 W at the wall (stock reference §4.2) |

- **Standby is only 11 V / 5 W** (stock reference §0.6). The MCU, the module standby rail (COM-HPC 5 V standby, if used), Wake-on-LAN and S3 DDR5 self-refresh must fit in 5 W.
  - Consider designing S5-only (no S3) at first **[Inference]**.
  - The ccAS allows "12 V ATX and/or single supply" operation [26]. Single-supply mode avoids a module standby rail but removes S3/WoL.
- **MCU duties:**
  - PSU enable and Hall interlock (stock reference §0.6).
  - The COM-HPC power-button/sleep-state handshake.
  - Per-MXM PWR_EN → PWR_GOOD sequencing (no signals before PWR_GOOD [52]).
  - Fan PWM/tach: A5940 PWM input, FG tach (stock reference §4.1).
  - Read temperatures from the module (board controller over I²C) and from the MXMs (SMBus, TH_ALERT#/TH_OVER#). Close the fan loop.
  - Thermal failsafe.
- **Connectors on the backplane:** card-edge socket (CPU), 2–3 MEG-Array (GPU A, GPU B, I/O), bus-bar lugs, PSU signal cable, fan flex.

---

## 7. What each choice implies for the firmware plan

| Path | How | Applies to | Verdict |
|---|---|---|---|
| **F1: vendor UEFI + "firmware-like" OpenCore** | Keep the module's AMI UEFI. Put OpenCore on a **dedicated small boot device on the carrier/backplane** (e.g. a soldered eMMC/USB-flash/M.2 2230; **[Inference]** design choice). Register it as a firmware boot entry with `Misc → Boot → LauncherOption = Full` [22]. Handle CFG-Lock etc. with OC quirks. | All variants | **Realistic (do this first)** |
| **F2: vendor custom UEFI with OpenCore embedded** | Ask congatec/Portwell for a custom UEFI build: OC as an embedded FFS application + default boot option. The ccAS datasheet invites custom-UEFI requests [26]. | Variants 1–3 | **Stretch** (NRE/volume terms unknown; hobby buyer unlikely to qualify) |
| **F3: self-modded AMI image** | Insert OC into the vendor image with UEFITool-style tools. | Variants 1–3 | **Stretch → not feasible if Boot Guard/signed capsules are enabled** on the module (**[Unverified]** per module) |
| **F4: coreboot + EDK2 payload with OpenCore embedded** | coreboot → EDK2 UefiPayloadPkg [23h]. Include OpenCore.efi plus an embedded FAT image (config.plist/kexts) as a RAM disk/boot option **[Inference; no precedent found]**. Community reports say OC is chain-loaded from an ESP, not run as a payload [21]. | Only coreboot-capable hardware: **Prodrive Atlas** (COM Express), Kontron COMe-bSL6, **LattePanda Mu** (dev mule) [23a][23b][23f]. Intel FSP binaries are public, incl. RPL-S [24b]. | **Stretch / research** |
| **F5: AMD open firmware** | openSIL (Phoenix client only today) [25]; coreboot "maple" is an AMD Strix Halo *reference* board [23e]. PSP firmware signing applies. | Variant 3 | **Not feasible near-term** |

- **macOS SMBIOS:**
  - Variants 1/2/3 use a dGPU. Use **MacPro7,1** (dGPU does everything) with the Tahoe board-id skip [5][18].
  - The CFL variant can use the natively supported **MacBookPro16,1**-class identity with UHD 630 [2][11] (**[Inference]** on the exact SMBIOS choice).
- **Linux/Windows** boot straight from the vendor UEFI (no OC dependency). This is another reason to treat macOS as a boot option rather than the firmware identity.

---

## 8. Top risks

1. **Mechanical fit.**
   - COM-HPC Size C is 160 mm long versus the ~155 mm (±15%) face estimate.
   - The MXM Type B is 82 mm wide versus the unknown GPU-face width.
   - Module stack height: about 20 mm over the carrier with heatspreader.
   - PSU clearance behind the CPU board.
   - Measure all four first (stock reference §5, §10).
2. **Module procurement.** Portwell and cRX1 prices are quote-only. Some distributors refuse private buyers [35]. The WDL public prices [28] should be confirmed with an actual order or quote.
3. **PCIe Gen4 through MEG-Array + flex.** The signal integrity is unknown. Plan Gen3 fallback and test coupons.
4. **"OpenCore in firmware".** Not achievable on closed AMI modules without vendor cooperation. F1 is the practical target [26][21][22].
5. **MXM RX 6600 unknowns:**
   - TBP conflict (100 W vendor vs 75 W teardown) [40][41].
   - No fan header [41].
   - GOP/UEFI VBIOS and macOS acceptance unconfirmed.
   - Single small vendor (X-VSION) + eBay supply [40][40c].
6. **macOS runway.** Tahoe is the end of the road for x86 (security updates to ~2028) [1][2]. Arrow Lake and Zen 5 hackintosh support is new and has reported quirks [8][9].
7. **Standby budget.** 5 W at 11 V limits S3/WoL design.
8. **Thermal path.** The module heatspreader and MXM VRAM pads contact the stock core faces. Pad thickness and flatness must be engineered. Measured headroom (65–70 °C at 130 W) is encouraging for a 65 W-class CPU.
9. **Stock I/O board reuse.** It expects PEX8723 x8 Gen3 upstream and up to 6 DP streams, and has TB2 (DSL5520) controllers. Hackintosh support for TB2 on this topology is unknown **[Unverified]**. Designing a new I/O board may be simpler.

---

## 9. Precedents to learn from or reuse (research item C)

| Project | What it is | Reuse value | Source |
|---|---|---|---|
| **LattePanda Mu carriers** (official, open KiCad) + community **MuBook NAS carrier** assembled at JLCPCB | x86 SoM carriers designed and fabbed by hobbyists | Closest hobby precedent for "x86 module + custom carrier + JLC assembly"; coreboot-supported | [46][46b][23f] |
| **Antmicro COM Express Type 7 baseboard** (open KiCad, Apache-2.0) | Full open COM Express carrier with PCIe redrivers, M.2, OCuLink, power | Reference for COM connector breakout, PCIe routing, power tree | [53][53b] |
| **PICMG COM-HPC Carrier Design Guide R2.2** | Free official carrier design guide (interface schematics, layout rules) | Primary reference for the CPU carrier | [38] |
| **Framework ExpansionBay** (CC-BY spec + CAD) and FW16/FW13 mainboard docs | Open PCIe x8 module interface; mainboard reuse docs; community x16-slot bay board | Reference for a PCIe x8 GPU module interface and power | [44][44c][44f] |
| **Dasharo (coreboot + EDK2) on MSI PRO Z690-A/Z790-P/B760-P**; **3mdeb MSI PRO B850-P openSIL** | Open firmware ported to retail LGA1700/AM5 boards | Proves FSP/openSIL-based open firmware on desktop platforms; not a hardware template | [23g][25] |
| **Prodrive Atlas** (upstream coreboot COM Express) | Open-firmware COM module | Candidate for firmware path F4 | [23a][43] |
| **DIY Ryzen mobile board** (Hackaday, 6-layer KiCad, 100 × 100 mm) | Hobby x86 BGA board | Shows the BGA-CPU path depends on leaked docs; a cautionary precedent | [24f] |
| **iMac MXM GPU upgrade community** (EFI VBIOS work for MXM cards) | Running MXM AMD GPUs under macOS with EFI boot screens | Directly relevant to GOP/VBIOS on MXM Radeons | [19b] |
| Apple internal GPU-face dev cards / CodeJingle / AngelShark | Mac Pro 6,1 flex/mezzanine reverse-engineering | See stock reference §8 | stock ref. |

---

## 10. Open questions to resolve next

1. Measure the CPU-face and GPU-face usable areas, PSU clearance and the stock riser outline (decides Size C vs A/B, and MXM Type B vs A).
2. Get quotes: Portwell PCOM-B887/B886, congatec cRX1, and cRLS. Confirm that WDL will sell and ship to an individual.
3. Confirm COMh-ccAS PEG 2×8 bifurcation and the validated CPU list (T/non-E desktop parts).
4. Get the RX 6600 MXM facts: DP output count, UEFI GOP present?, actual power limit, and a macOS test report (or buy one and test on an MXM-to-PCIe adapter).
5. Decide whether to keep the stock I/O board (TB2) or design a new I/O board (USB4 from Arrow Lake modules).

---

## 11. Price-check log (all 2026-09-30)

- WDL Systems, COM-HPC Client C [28]:
  - COMh-ccAS H610 $470.59; H610E $485.81; Q670 $555.01; Q670E $564.71; W680 $564.71; R680E $570.25.
  - ADLINK COM-HPC-cRLS i7-13700E $1,509.21; i9-13900E $1,908.65.
- WDL, COM-HPC Client A: COMh-caAP i3-12300HE $820.76; i7-12800HE $1,548.79 [28b].
- WDL, COMe Type 6 Basic [34]:
  - COMe-bCL6 i3-9100HL $941.18; i7-9850HL $1,513.00.
  - ADLINK Express-CFR $1,352.43; SECO OBERON $1,471.
  - Express-TL i3-11100HE $865.72.
  - Express-RLP i3-1315UE $797.55; i7-13800HE $1,481.94.
  - COMe-bRP6 i7-1370PE $1,471.28.
  - congatec COM Express Eval Carrier2 $665.
- Intel i5-14500T RCP $232 [33]; i5-13500T Newegg $242.79 [33b]; eBay used i5-14500T $278 [33c].
- X-VSION MXM [40]: RX 6600 $280 (in stock); RX 6600 XT out of stock; RX 5500 XT $200; RX 580 $220; E9174 $200; RX 550 $130; R5 230 $50. eBay RX 6600 XT MXM $299 [40c].
- DigiKey [45][45b][45c]:
  - JAE MM70-314B1-2-R300 $11.16 (3,305 in stock); ATTEND 125B-78C00 $16.69.
  - Samtec ASP-214802-01 $42.65; ASP-209948-01 $48.01.
  - TE 3-1827253-6 $27.23.
- Framework [44a][44e]: FW16 AI 300 mainboard $499 / $749 / $1,049; FW13 AI 300 from $449; Framework Desktop mainboard from $969 [44g].
- Intel i7-13800HE RCP $460 [24c].

---

## 12. Sources

**macOS / OpenCore / GPU support**
- [1] Apple, macOS versions / compatibility: https://support.apple.com/en-us/100100
- [2] Apple, Intel-Mac support statement / Tahoe compatible Macs: https://support.apple.com/en-us/149035
- [3] MacRumors, "macOS 27 won't run on these Macs" (2026-06-03): https://www.macrumors.com/2026/06/03/macos-27-wont-run-on-these-macs/
- [5] hackintosh-forum.de thread 60288 (Tahoe SMBIOS board-id notes): https://www.hackintosh-forum.de/forum/thread/60288-eignung-von-intel-arrow-lake-cpus-mit-z890-boards-f%C3%BCr-hackintosh/ (Arrow Lake/Z890 suitability thread)
- [6] OpenCorePkg releases (1.0.2/1.0.3/1.0.7/1.0.8 notes): https://github.com/acidanthera/OpenCorePkg/releases
- [7] r/hackintosh, Arrow Lake 265K + RX 6900 XT on Sequoia: https://www.reddit.com/r/hackintosh/comments/1gzkw4n/
- [8] InsanelyMac, "Unable to boot into macOS Tahoe with Core Ultra Arrow Lake" (solved: AppleMCEReporterDisabler + ProvideCurrentCpuInfo): https://www.insanelymac.com/forum/topic/362692-unable-to-boot-into-macos-tahoe-with-core-ultra-arrow-lake/ ; also Olarila Z890 AORUS PRO ICE + 265K build: https://olarila.com/topic/41552-perfect-hackintosh-on-gigabyte-z890-aorus-pro-ice-with-intel-core-ultra-7-265k/
- [9] Olarila, "Random system freezes on macOS after BIOS update (ASUS Z890 / Arrow Lake)": https://olarila.com/topic/46465-random-system-freezes-on-macos-after-bios-update-asus-z890-arrow-lake-hackintosh-issue/
- [10] OpenCore Visual Beginners Guide, "Using Alder Lake": https://chriswayg.gitbook.io/opencore-visual-beginners-guide/advanced-topics/using-alder-lake
- [11] Dortania GPU Buyers Guide, Intel iGPUs: https://dortania.github.io/GPU-Buyers-Guide/modern-gpus/intel-gpu.html
- [12] Dortania, macOS hardware limits: https://dortania.github.io/OpenCore-Install-Guide/macos-limits.html
- [13] AMD Vanilla patches: https://github.com/AMD-OSX/AMD_Vanilla (also mikigal/ryzen-hackintosh, updated June 2026 for Tahoe: https://github.com/mikigal/ryzen-hackintosh)
- [14] NootedRed (ChefKiss): https://chefkiss.dev/applehax/nootedred/
- [15] Dortania GPU Buyers Guide, AMD: https://dortania.github.io/GPU-Buyers-Guide/modern-gpus/amd-gpu.html
- [16] Dortania GPU Buyers Guide (Nvidia status): https://dortania.github.io/GPU-Buyers-Guide/
- [17] HackintoshBuilder GPU list 2026 (Tahoe/Sequoia): https://www.hackintoshbuilder.com/hackintosh-gpu-compatibility-list/
- [18] Dortania, choosing the SMBIOS: https://dortania.github.io/OpenCore-Install-Guide/extras/smbios-support.html
- [19] tonymacx86, RX 6000 family status (Navi 22/24 not working): https://www.tonymacx86.com/threads/success-xfx-rx-6600-xt-graphics-card-in-monterey-12-2-1.319128/
- [19b] MacRumors, iMac MXM GPU upgrade thread (EFI VBIOS for MXM): https://forums.macrumors.com/threads/2011-imac-graphics-card-upgrade.1596614/page-871
- [20] MacRumors, RX6600XT Sequoia thread (2048SP/Lexa caveats, AVX2): https://forums.macrumors.com/threads/rx6600xt-sequoia.2452637/
- [21] r/hackintosh, "Run OpenCore as a coreboot payload" (answer: chain-load from ESP): https://www.reddit.com/r/hackintosh/comments/1d0v7ff/run_opencore_as_a_coreboot_payload_on_actual_mac/
- [22] Dortania, LauncherOption: https://dortania.github.io/OpenCore-Post-Install/multiboot/bootstrap.html

**Firmware openness**
- [23] coreboot source tree, cloned 2026-09-30 (HEAD a8d37966): https://github.com/coreboot/coreboot
  - [23a] Prodrive Atlas: https://github.com/coreboot/coreboot/tree/main/src/mainboard/prodrive/atlas
  - [23b] Kontron COMe-bSL6: https://github.com/coreboot/coreboot/tree/main/src/mainboard/kontron/bsl6
  - [23c] Framework Marigold/Sakura/Sunflower docs ("All mainboards sold to customers ship with BootGuard enabled…"): https://github.com/coreboot/coreboot/blob/main/Documentation/mainboard/framework/marigold.md
  - [23d] Framework Azalea (FW13 AMD 7040) PoC: https://github.com/coreboot/coreboot/blob/main/Documentation/mainboard/framework/azalea/azalea.md
  - [23e] AMD reference boards (birman, maple): https://github.com/coreboot/coreboot/tree/main/src/mainboard/amd
  - [23f] LattePanda Mu: https://github.com/coreboot/coreboot/blob/main/Documentation/mainboard/lattepanda/mu.md
  - [23g] MSI ms7d25 (PRO Z690-A) etc.: https://github.com/coreboot/coreboot/tree/main/src/mainboard/msi ; Dasharo MSI Z690 release notes (v1.1.7, 2026-08-13): https://docs.dasharo.com/variants/msi_z690/releases/
  - [23h] EDK2 UefiPayloadPkg build instructions: https://github.com/tianocore/edk2/blob/master/UefiPayloadPkg/BuildAndIntegrationInstructions.txt
- [24] Intel Resource & Documentation Center (RDC account, restricted collections): https://www.intel.com/content/www/us/en/resources-documentation/developer.html
- [24b] Intel FSP binaries (RaptorLakeFspBinPkg etc.): https://github.com/intel/FSP
- [24c] Intel i7-13800HE (FCBGA1744, RCP $460): https://www.intel.com/content/www/us/en/products/sku/232150/intel-core-i713800he-processor-24m-cache-up-to-5-00-ghz/specifications.html (SKU 232150; Intel blocks scripted fetches, so open it in a browser)
- [24d] AMD Ryzen Embedded V3000: https://www.amd.com/en/products/embedded/ryzen/ryzen-v3000-series.html
- [24e] Ryzen Embedded 8845HS OPN 100-000001316E, FP7r2 package: from a cpu-world listing. **[Unverified: exact page URL not kept; search cpu-world for the OPN]** https://www.cpu-world.com/
- [24f] Hackaday, "Building a DIY Ryzen-based PC" (2025-11-02): https://hackaday.com/2025/11/02/building-a-diy-ryzen-based-pc/
- [25] 3mdeb, MSI PRO B850-P openSIL port part 3: https://blog.3mdeb.com/2026/2026-04-03-msi_pro_b850p_part3/ ; Wccftech on openSIL for AM5/Zen 6: https://wccftech.com/amd-opensil-open-source-firmware-lands-on-am5-motherboards-prepped-for-zen-6/ ; Phoronix openSIL: https://www.phoronix.com/news/AMD-openSIL-September-2024

**CPU modules / boards**
- [26] COMh-ccAS datasheet (Kontron/JUMPtec): https://www.kontron.com/download/download?filename=%2Fdownloads%2Fdatasheets%2Fc%2Fcomh-client%2Fcomh-ccas_datasheet.pdf&product=172993
- [27] congatec conga-HPC/cRLS: https://www.congatec.com/en/products/com-hpc/conga-hpccrls/ ; user guide: https://www.congatec.com/fileadmin/user_upload/Documents/Manual/GALS.pdf
- [27b] CNX Software on cRLS SKUs: https://www.cnx-software.com/2023/01/27/conga-hpc-crls-raptor-lake-com-hpc-client-module-128gb-ddr5-ram/
- [27c] congatec conga-HPC/cBLS press release: https://www.congatec.com/us/congatec/press-releases/article/congatec-launches-new-high-performance-com-hpc-module-for-demanding-real-time-applications/
- [28] WDL Systems, COM-HPC Client C listing: https://www.wdlsystems.com/custitem_ff_form_factor/COM~HPC-Client-C
- [28b] WDL Systems, COM-HPC Client A listing: https://www.wdlsystems.com/custitem_ff_form_factor/COM~HPC-Client-A
- [29] congatec COM-HPC/COM Express with Core Ultra Series 3 (Panther Lake): https://www.congatec.com/en/technologies/com-hpc-and-com-express-modules-with-intel-core-ultra-series-3-processors/
- [30] Portwell PCOM-B887: https://portwell.com/products/detail.php?CUSTCHAR1=PCOM-B887
- [30b] Portwell PCOM-B886: https://portwell.com/products/detail.php?CUSTCHAR1=PCOM-B886 ; Portwell COM-HPC overview: https://portwell.com/products/com-hpc.php
- [31] congatec conga-HPC/cRX1: https://www.congatec.com/en/products/com-hpc/conga-hpccrx1/
- [32] ADLINK COM-HPC-cRLS: https://www.adlinktech.com/products/Computer_on_Modules/COM-HPC-Client-Module/COM-HPC-cRLS?lang=en
- [33] Intel i5-14500T ARK (RCP $232, 35/92 W, 1×16+4 / 2×8+4): https://www.intel.com/content/www/us/en/products/sku/236780/intel-core-i5-processor-14500t-24m-cache-up-to-4-80-ghz/specifications.html
- [33b] Newegg i5-13500T OEM: https://www.newegg.com/p/274-000A-01NR4
- [33c] eBay used i5-14500T: https://www.ebay.com/itm/406019437108
- [34] WDL Systems, COMe Type 6 Basic listing: https://www.wdlsystems.com/custitem_ff_form_factor/COMe-Type-6-Basic
- [34b] Kontron COMe-bCL6 announcement: https://www.kontron.com/en/news/kontron-announces-new-com-express-r-type-6-module-with-high-performance-8th-gen-intel-r-core-tm-xeon-r-e-processors/n153165
- [35] module-store.com (OEM-only sales note): https://www.module-store.com/en/congatec/conga-hpc-crls-i9-13900e/conga-hpc-crls-049800
- [36] congatec, portfolio expansion after acquiring Kontron's module business (July 2025): https://www.congatec.com/us/congatec/press-releases/article/congatec-expands-its-computer-on-module-portfolio-with-18-new-product-families/
- [37] Kontron COM portfolio page (distribution now via JUMPtec): https://www.kontron.com/en/landing-pages/computer-on-modules-portfolio
- [38] PICMG design guides (COM-HPC CDG R2.2, free): https://www.picmg.org/resources/design-guides/ ; https://www.picmg.org/product/com-hpc-carrier-design-guide-rev-2-2/
- [38b] PICMG COM-HPC overview (abridged spec, related docs): https://www.picmg.org/openstandards/com-hpc/
- [39] TRIA HCA-RLP (Size A, x8 PEG Gen5 option, 8 Gen4, 8 Gen3): https://www.tria-technologies.com/2024/01/08/high-performance-com-hpc-client-module-family-based-on-13th-gen-intel-core-processors/
- [39b] congatec conga-HPC/cRLP datasheet: https://pub-mediabox-storage.rxweb-prd.com/exhibitor/document/exh-732e7e33-a9fc-47d7-a48e-efbb8d6b384f/d8424ed1-ae55-4e53-942a-7c22793775eb.pdf
- [39c] Kontron COMh-caRP user guide (PEG x8 on H-SKUs only): https://www.kontron.com/downloads/manuals/com-hpc-client/comh-carp_userguide_0-3.pdf?product=176930
- [42] congatec conga-TCV2: https://www.congatec.com/us/products/com-express-type-6/conga-tcv2/
- [42b] conga-TCV2 user guide (PEG x8 default 2×x4): https://www.congatec.com/fileadmin/user_upload/Documents/Manual/TCV2.pdf
- [42c] conga-TCV2 datasheet: https://www.fortec-integrated.de/fileadmin/pdf/produkte/Embedded/COM/Express_Compact/conga-TCV2_Datasheet.pdf
- [43] Prodrive Atlas product page: https://prodrive-technologies.com/en/products/embedded-computing-cabinets/embedded-computing/computers-on-module-atlas/
- [44] Framework Laptop 16 docs (mainboard reuse, interface schematics): https://github.com/FrameworkComputer/Framework-Laptop-16
  - [44a] FW16 Ryzen AI 300 mainboard store page: https://frame.work/products/laptop16-mainboard-amd-ai300
  - [44b] FW16 mainboard 2D drawing PDF (my reading of the dimension text: ~336.5 mm and ~169.5 mm overall; approximate): https://github.com/FrameworkComputer/Framework-Laptop-16/blob/main/Mainboard/Framework_Laptop_16_Mainboard_drawings.pdf
  - [44c] Framework ExpansionBay (open spec, PCIe x8): https://github.com/FrameworkComputer/ExpansionBay ; Dual M.2 blog: https://frame.work/blog/our-first-new-framework-laptop-16-expansion-bay-module
  - [44d] Framework Laptop 13 mainboard docs: https://github.com/FrameworkComputer/Framework-Laptop-13
  - [44e] FW13 Ryzen AI 300 announcement (mainboard from $449): https://community.frame.work/t/introducing-the-framework-laptop-13-powered-by-amd-ryzen-ai-300-series/65007
  - [44f] Community FW16 x16-slot (x8-lane) bay board: https://community.frame.work/t/framework-16-pcie-x-16-slot-for-expansion-bay/77257
  - [44g] Framework Desktop mainboard: https://frame.work/products/framework-desktop-mainboard-amd-ryzen-ai-max-300-series
- [46] LattePanda Mu (open carrier files): https://github.com/LattePandaTeam/LattePanda-Mu ; https://www.lattepanda.com/lattepanda-mu
- [46b] Hackaday design review, LattePanda Mu NAS carrier: https://hackaday.com/2025/08/12/design-review-lattepanda-mu-nas-carrier/

**GPU**
- [40] X-VSION MXM RX 6600 8 GB: https://www.x-vsion.com/product/mxm-radeon-rx-6600-8gb/ ; category: https://www.x-vsion.com/product-category/mxms/mxmamd/
  - [40b] RX 6600 XT MXM: https://www.x-vsion.com/product/mxm-radeon-rx-6600-xt-8gb/
  - [40c] eBay MXM RX 6600 XT: https://www.ebay.com/itm/397616163301
  - [40d]/[40e]/[40f] RX 5500 XT, RX 580, E9174/RX 550/R5 230: X-VSION AMD MXM category page above
- [41] Reddit teardown of the MXM RX 6600: https://www.reddit.com/r/Amd/comments/xatzqz/ ; Tom's Hardware: https://www.tomshardware.com/news/amds-radeon-rx-6600-emerges-in-mxm-form-factor
- [45] DigiKey JAE MXM connector (EOL notice → MM70-314B1-2-R300): https://www.digikey.com/en/products/detail/jae-electronics/MM70-314-310B1-1-R300/2183603 ; EOL bulletin: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7041/MB-419.pdf
  - [45a] 30 mating-cycle rating for JAE MM70: from a TraceParts listing. **[Unverified: exact URL not kept; confirm in the JAE MM70 datasheet]**
  - [45b] DigiKey Samtec COM-HPC connectors: https://www.digikey.com/en/product-highlight/s/samtec/com-hpc-standard-connectors ; Samtec COM-HPC page: https://www.samtec.com/standards/picmg/comhpc/
  - [45c] DigiKey TE 3-1827253-6: https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/3-1827253-6/2188003
- [47] OCLP supported models (MacPro6,1 Legacy Metal): https://dortania.github.io/OpenCore-Legacy-Patcher/MODELS.html
- [48] MacRumors, MacPro6,1 Ventura/Sonoma/Sequoia + OCLP issues: https://forums.macrumors.com/threads/macpro6-1-ventura-sonoma-sequoia-and-oclp-drm-chrome-electron-issues.2367706/page-6
- [49] Guru3D, AMD Adrenalin (Polaris/Vega to legacy support from 26.5.2): https://www.guru3d.com/files/category/videocards-ati-catalyst-windows-7-8-10/
- [50] OCLP legacy GCN/Tahoe tracking issue: https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1167
- [50b] The Register forums, OCLP 3.0 beta on Tahoe: https://forums.theregister.com/forum/all/2026/07/16/20265/
- [51] bootcampdrivers.com (modded Adrenalin for D300/D500/D700): https://www.bootcampdrivers.com/ ; AMD Adrenalin 26.8.1 notes (not for Boot Camp): https://www.amd.com/en/resources/support-articles/release-notes/RN-RAD-WIN-26-8-1.html
- [51b] R.ID community drivers (GCN1 list incl. FirePro D300/D500/D700): https://rdn-id.com/ ; r/macpro Boot Camp driver options: https://www.reddit.com/r/macpro/comments/1h2ypcf/
- [51c] Phoronix, Linux 6.19 amdgpu default for GCN1: https://www.phoronix.com/review/linux-619-amdgpu-radeon ; Gentoo wiki AMDGPU: https://wiki.gentoo.org/wiki/AMDGPU
- [52] Advantech SKY-MXM-A1000 startup manual (PWR_SRC 7–20 V; signal rule; A1000 specs): https://advdownload.advantech.com/productfile/Downloadfile5/1-2DSVTPU/SKY-MXM-A1000_Startup_Manual_Ed.1_FINAL.pdf ; SKY-MXM-A4500 manual: https://www.rosch-computer.com.au/file.jsp?aid=53792&sku=SKY-MXM-A4500
- [52b] Clevo P775TM schematic excerpt (MXM PWR_SRC 10 A, 5 V 2.5 A, 3.3 V 1 A): https://www.e-weekly.co.uk/download/RnD/DRIVERS/CLEVO/P775TM1/ESM.pdf

**Precedents**
- [53] Antmicro COM Express Type 7 baseboard: https://github.com/antmicro/com-express-7-baseboard
- [53b] Antmicro blog: https://antmicro.com/blog/2024/11/com-express-baseboard-type-7
