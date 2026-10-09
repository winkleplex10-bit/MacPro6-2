# AM5 CB v3: CPU, lanes, power and display (2026-10-08, about 20:45 ET)

Decision (Aidan, 19:50 ET): v3 = **Ryzen 7000/9000 (Raphael / Granite Ridge)** on the same AM5 placeholder socket. The Dasharo
(open firmware) constraint is dropped for v3. Tags as in the spec: [Sourced], [Estimate], [Inference], [Unverified].

## 1. Lane map (v3)

| CPU source | Lanes | Goes to | Notes |
|---|---|---|---|
| GFX | x16 (Gen5 capable, Face P link runs at what the MCIO path supports) | J1 FP lanes 0-15 -> BP J9 -> Face P | all 16 lanes live (the v1 8000G used only 0-7) |
| GPP #1 | x4 Gen4 | J1 FS lanes 0-3 -> BP J10 lanes 0-3 -> Face S slot A | unchanged |
| GPP #2 | x4 Gen4 | J1 FS lanes 4-7 (CPU-LINK v3) -> BP J10 lanes 4-7 -> Face S slot B | **BP v3 (6 layers) routes all four lanes (x4)** |
| Chipset link | x4 Gen4 | PROM21 uplink | unchanged |
| PROM21 free Gen4 x4 | x4 | **J8 M.2 boot** (moved from CPU GPP #2) | REFCLK/PERST from PROM21 [Unverified pin list] |
| GPP_CLK | 1 more refclk | J1 FS_REFCLK1 (B101/B102) -> J10 REFCLK1 | slot B refclk; index TBD (AMD pin list = NDA) |

- Raphael / Granite Ridge: 28 PCIe 5.0 lanes, 24 usable [Sourced: AMD 9600 page, fetched 2026-10-08]; the usable 24 are x16 GFX + 2 x4 GPP;
  the other 4 are the chipset link.
- Phoenix (8600G/8700G) by contrast: 20 PCIe 4.0 lanes, 16 usable (GFX x8 + x4 + x4); x8 to the GPU [Sourced earlier, AM5 plan §10].

## 2. Phoenix vs Raphael on the same socket (public info only)

| Item | Phoenix 8000G (v1 target) | Raphael 7000 / Granite Ridge 9000 (v3) |
|---|---|---|
| Dies | monolithic APU | CCD(s) + 6 nm I/O die |
| PCIe | Gen4, 20/16 usable, GFX x8 | Gen5, 28/24 usable, GFX x16 + 2 x GPP x4 |
| USB | 2 x 10G + 2 x USB4 + USB2 | 4 x 10G + 1 x USB2 [Sourced: AMD 9600 page] -> with PROM21 (6 x 10G) = exactly 10 x 10G, hub bypass possible (open A-7) |
| iGPU | RDNA3 (8600G 8 CU) | RDNA2, 2 CU, DP alt-mode capable [Sourced: AMD 9600 page] |
| Memory | 4 x DDR5-3600 (2DPC) | 4 x 1R/2R DDR5-3600 (2DPC), 2 x 5600 (9000) [Sourced: AMD 9600 page] |
| TDP | 65 W, cTDP 45-65 W | 65 W (non-X); X parts 105-120 W -> not supported in this chassis |
| Open firmware | Dasharo v0.9.0 boots 8000G only | none -> vendor AGESA UEFI (closed); Dasharo constraint dropped for v3 |
| Pinout | AM5 LGA1718 (land map NDA) | same socket; package-level pin use differs (no USB4, more PCIe) -> placeholder unchanged |

**Pins and straps (public info only):** AMD's AM5 land map, strap list and VR guide are NDA, so no per-land comparison is possible.
What is public: the same retail AM5 boards (A620/B650/X670/B850/X870) take Phoenix, Raphael and Granite Ridge with only a BIOS (AGESA) update,
so package-level differences are absorbed by the board's lane wiring and firmware, not by board straps [Inference].
The board-visible differences are:
- PCIe lanes 8-15 of GFX and the second GPP x4: unused on Phoenix, live on Raphael.
- USB4 ports: Phoenix only. They are unused in v1 rev A, so nothing changes.
- Gen5-capable lanes on Raphael: the BP/MCIO path is designed for Gen4, so it trains Gen4.
- Display PHY: Phoenix supports DP 2.1. Raphael's iGPU does DP alt-mode [Sourced: AMD 9600 page]; its exact DP version per port is [Unverified].

The DXIO lane descriptors (which pins are GFX, GPP or chipset, and the bifurcation) live in the firmware's board config, not in straps.

The socket placeholder footprint stays the same (synthetic 1718 lands; real land map is AMD NDA -> do not fab).

## 3. Power / TDP recommendation

**Ryzen 5 9600 (Granite Ridge, Zen 5, 6C/12T) at the default 65 W TDP**; Ryzen 5 7600 is the drop-in alternative (same limits).
Option: 45 W Eco mode when Face P runs its 150 W case (see the budget below).
Not recommended: Ryzen 7 7700 / 9700X at 65 W (8C). They have the same 88 W PPT, so the VRM and budget are the same, but they cost more,
there is more all-core heat at the same PPT, and the 9700X ships with a 105 W BIOS option that must stay disabled. They are acceptable if more cores are wanted.

**VRM changes for 65 W:** none to the stage count. Required work:
- Re-tune the SVI3 controller config for TDC 75 A / EDC 150 A (OCP, load line).
- Check the input caps' ripple at 88 W.
- Re-check the inductor/stage thermals in the core airflow.

| Limit (AM5, 65 W class) | Value |
|---|---|
| PPT | 88 W [Sourced earlier: 7600-class limits] |
| TDC / EDC (VDDCR) | 75 A / 150 A [Sourced earlier] |
| 45 W Eco | PPT about 60-61 W [Inference: PPT = 1.35 x TDP; AMD Eco mode, not a datasheet value] |

**VRM (v1 sized for a fixed 45 W, PPT about 61 W):** 5 x VDDCR + 2 x SOC + 1 x MISC, SiC654 50 A stages + FP4 inductors.
- 65 W: TDC 75 A / 5 = 15 A per phase continuous, EDC 150 A / 5 = 30 A per phase peak; the stages are 50 A parts -> **electrically OK**.
- The VR loop, load line and OCP still come from the AMD VR guide (NDA). Thermals: about 88 W at the socket instead of 61 W (+27 W) into the
  same core plate; the Mac Pro 6,1 core was designed for a higher CPU TDP class [Inference] -> re-check in M-AM5-1.
- **X parts (105-120 W, PPT 142 W+) are out**: the BIOS must lock PPT <= 88 W.

**CB 12 V input:** 88 W / 0.88 + PROM21 ~7 W + DDR5 PMICs/hub/aux ~25 W -> about 130 W, about 11 A at 12 V; U11 TPS259851 ILIM about 25 A -> OK.

**System budget (ICD §13, 445 W ceiling, PSU 450 W):**

| Case | v1 rev 3 table | v3 (9600 at 65 W) | v3 at 45 W Eco |
|---|---|---|---|
| CB worst / sustained | 142 W / 75 W | about 138 W / 128 W | about 111 W / 101 W |
| System worst (Face P 130 W) | about 431 W | about 427 W | about 400 W |
| System worst (Face P 150 W) | about 451 W | about 447 W (over 445 by about 2 W) | about 420 W |
| System sustained | 330-345 W | about 383-398 W | about 356-371 W |

-> 65 W fits the 130 W Face P case; with the 150 W Face P case the LPT must cap PPT (or use 45 W Eco). The LPT_SET payload is PPT/TDC/EDC on AM5 (already in v1).

## 4. Display plan

Keep the v1 path: **iGPU DP0 (4 lanes) + DP1 (2 lanes) -> J3 -> IOB DDI-B / DDI-C (USB-C C5 / C6 DP alt mode)**. The Face P GPU drives
its displays over DISPLAY-LINK (I-3) as before. Reason: display output without the GPU module (bring-up, GPU-less SKU, firmware screens),
and no extra cost. 2-CU RDNA2 output count and lane mapping per port are [Unverified] (AMD datasheet NDA, open A-8).

## 5. Price (context; CPU not in the BOM totals)

| CPU | Price seen 2026-10-08 | Source |
|---|---|---|
| Ryzen 5 9600 | about $120 (multi-store), $244 single tracker | biggo.com compare; h2bench (2026-10-03) |
| Ryzen 5 7600 | about $123 (multi-store), $280-305 single offers | biggo.com; pricehistory.app (Amazon); thecomparator.tech (Newegg) |
| Ryzen 5 8600G (v1 target) | $177-197 box | AM5 plan / cost estimate §10.4 |

CPU delta v3 vs v1: about **-$77 to +$67** (9600 $120-244 vs 8600G $177-197).
