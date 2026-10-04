#!/usr/bin/env python3
"""Generate the MacPro6,2 AM5 CPU board (CB, DRAFT) top-level BLOCK schematic (KiCad 9): a root sheet with hierarchical
sheet symbols + net labels, and one stub file per block holding the matching hierarchical labels, a non-BOM #BLK stub
symbol (passive pins, ERC anchor) and a text description. Same generator pattern as kicad/macpro62-backplane/tools/build_sch.py.
Nets are block-level BUNDLES (e.g. PCIE_GFX_L0_7 = 8 TX + 8 RX pairs); circuits TBD. AMD pin names are NDA -> functional names."""
import os, uuid
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
U = lambda: str(uuid.uuid4())
ROOT_UUID = "6a1c2d3e-0000-4000-8000-0000000a0005"
VER = '(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")'
F = '(effects (font (size 1.27 1.27))'
def g(v): return round(v / 1.27) * 1.27
I, O, B, P = "input", "output", "bidirectional", "passive"
SHEETS = [
 ("CPU: Socket AM5 (Ryzen 7 8700G / Ryzen 5 8600G; 7000/9000 later)", "cpu_am5.kicad_sch", [
   "U1 Socket AM5 LGA1718 (Foxconn PE17181/PE17186 or Lotes AZIFS055), MP62 contact frame on the 69.5 x 55 core holes (no stock ILM)",
   "Primary CPU: Ryzen 8000G (Phoenix) - the only AM5 family Dasharo (coreboot + openSIL) boots today; cTDP 45 W (PPT ~61 W)",
   "8000G PCIe 4.0: 20 lanes / 16 usable = GFX x8 (Face P) + GPP x4 (Face S) + GPP x4 (M.2 boot) + x4 PROM21 uplink",
   "GFX lanes 8-15 are routed to J1 but unused by 8000G; live with Ryzen 7000/9000 (x16 Gen5, AC caps fitted)",
   "USB: 2 x USB 10G -> J3 C1/C2, 1 x USB2 -> CPU-LINK SPARE; 2 x USB4 unused in rev A (option: run them at 10G instead of the hub [firmware risk])",
   "Display: DP0 4-lane -> J3 DDIB, DP1 2-lane -> J3 DDIC (AUX AC-coupled, HPD from the IOB); 7000/9000 iGPU = 2 lanes class TBD",
   "FCH (in the CPU): GPP_CLK refclks (closes U-12 on AM5), SPI ROM, SMBus0 (SPD), SLP_S3_L/SLP_S5_L, RSMRST_L, PWR_GOOD, PCIE_RST_L, THERMTRIP_L, PROCHOT_L",
   "Pin names are functional placeholders: the AM5 pin list/land map is AMD NDA"],
  [("VDDCR", I), ("VDDCR_SOC", I), ("VDD_MISC", I), ("VDDIO_MEM_S3", I), ("VDD_18_S5", I), ("VDD_33_S5", I), ("VDD_MISC_S5", I),
   ("SVI3_CLK", B), ("SVI3_DAT", B), ("SVI3_ALERT_L", B), ("PROCHOT_L", B),
   ("DDR5_CHA", B), ("DDR5_CHB", B), ("SMB0_SCL", B), ("SMB0_SDA", B), ("FCH_SPI", B),
   ("PCIE_GFX_L0_7", O), ("PCIE_GFX_L8_15", O), ("PCIE_GPP_FS_X4", O), ("PCIE_GPP_M2_X4", O), ("PCIE_PROM21_X4", B),
   ("GPP_CLK_FP", O), ("GPP_CLK_FS", O), ("GPP_CLK_M2", O), ("GPP_CLK_PROM21", O), ("PCIE_RST_L", O),
   ("USB10G_CPU0", O), ("USB10G_CPU1", O), ("USB2_CPU0", O), ("DP0_ML", O), ("DP0_AUX", B), ("DP1_ML", O), ("DP1_AUX", B),
   ("HPD_B", I), ("HPD_C", I), ("CLK_48M", I), ("RTC_32K", I), ("VBAT_RTC_CB", I),
   ("PWR_BTN_L", I), ("SYS_RESET_L", I), ("RSMRST_L", I), ("PWR_GOOD", I), ("WAKE_L", B),
   ("SLP_S3_L", O), ("SLP_S5_L", O), ("THERMTRIP_L", O), ("FCH_UART0", B)]),
 ("SVI3 VRM: VDDCR + VDDCR_SOC + VDD_MISC", "vrm_svi3.kicad_sch", [
   "U3 AMD SVI3 3-rail digital controller: Renesas RAA229139 (X+Y+Z <= 8) or MPS MP2857 / uPI uP9533P; RAA229621 / XDPE192C3B = 2 rails + separate MISC",
   "Q1-Q5 + L1-L5: VDDCR 5 phases | Q6-Q7 + L6-L7: VDDCR_SOC 2 phases | Q8 + L8: VDD_MISC 1 phase (SVI3 Type II rail)",
   "SiC654 50 A smart power stages (MLP55-31L 5x5) + Eaton FP4 0.15 uH (5.0 mm) - same parts and column as the LGA1700 CB",
   "Load line, IccMax/TDC/EDC and telemetry from the AMD AM5 VR design guide (NDA); 8000G at 45 W cTDP needs ~60-90 A VDDCR peak [Estimate]",
   "VR_HOT_L wired into PROCHOT_L; PMBus to the EC for telemetry (optional)"],
  [("12V_CB", I), ("VR_EN", I), ("VR_PGOOD", O), ("SVI3_CLK", B), ("SVI3_DAT", B), ("SVI3_ALERT_L", B), ("PROCHOT_L", B),
   ("VDDCR", O), ("VDDCR_SOC", O), ("VDD_MISC", O), ("I2C0_SCL", B), ("I2C0_SDA", B)]),
 ("DDR5 2DPC: 4 x UDIMM vertical (back)", "ddr5.kicad_sch", [
   "J6/J7 (CH-A near/far) and J9/J10 (CH-B near/far): UMAX 90414 short-latch DDR5 UDIMM, same positions as the LGA1700 CB",
   "AM5 8600G/8700G: 2DPC 1R/2R = DDR5-3600, 1DPC = DDR5-5200 (AMD spec); daisy chain CPU -> near -> far, populate far first",
   "Module PMIC from 5V_VIN_BULK (U7); SPD hub on SMBus0 (FCH), 3V3_S5 for SPD/HSA",
   "DDR5 40 ohm SE / 80 ohm diff stripline on L3/L8"],
  [("DDR5_CHA", B), ("DDR5_CHB", B), ("5V_VIN_BULK", I), ("3V3_S5", I), ("SMB0_SCL", B), ("SMB0_SDA", B)]),
 ("PROM21 chipset (218-0891025 preferred)", "prom21.kicad_sch", [
   "U2 AMD Promontory 21 (B650/B850-class, single chip), FCBGA 19 x 19, ~7 W; 218-0891025 preferred over 218-0891018 (cost study sec. 10)",
   "Uplink PCIe 4.0 x4 from the CPU; downstream: 10G USB x6 + 20G x1 class, USB2, SATA x4 class, PCIe 4.0/3.0 x1..x4 (B850 table)",
   "Uses: 10G #0-3 -> J3 C3-C6, 10G #4 -> U16 VL822 hub (A1-A4), 10G #5 + 20G spare; USB2 -> J1 MCU/FACEP/FACES + J3 HS1",
   "PCIe x1 -> IOB i226 #1, x1 -> IOB ASM1182e (i226 #2 + AirPort); x4 reserved (AQC107 option); SATA0 -> J1 (BP OpenCore M.2)",
   "Own SPI flash U17 (image from a retail board BIOS [Unverified]); REFCLK/PERST/CLKREQ for its downstream ports [Unverified]",
   "Ballout, rails and strapping are AMD NDA -> open item"],
  [("PCIE_PROM21_X4", B), ("GPP_CLK_PROM21", I), ("PCIE_RST_L", I), ("PROM21_RAILS", I),
   ("USB10G_P21_0_3", O), ("USB10G_P21_4", O), ("USB2_P21_MCU", B), ("USB2_P21_FACEP", B), ("USB2_P21_FACES", B), ("USB2_HS1", B),
   ("PCIE_I226_X1", O), ("PCIE_I226B_X1", O), ("I226_REFCLK", O), ("I226B_REFCLK", O), ("I226_CLKREQ_L", B), ("I226B_CLKREQ_L", B),
   ("I226_PERST_L", O), ("SATA0", B), ("USB_OC_L", I)]),
 ("USB 10G hub (U16 VL822-Q7)", "usb_hub.kicad_sch", [
   "U16 VIA Labs VL822-Q7 USB 3.2 Gen2 1:4 hub, QFN-76 9x9 (LCSC C42419379); alt Genesys GL3590",
   "Upstream = PROM21 10G #4; downstream 1-4 = J3 USB3_A1..A4 (the IOB redriver side unchanged); A1-A4 share 10 Gb/s",
   "Needed because 8000G (2 x 10G) + PROM21 (6 x 10G) = 8 native 10G ports, the IOB needs 10 (C1-C6 + A1-A4)",
   "Own SPI flash + 25 MHz crystal; bypass option with Ryzen 7000/9000 (4 native 10G) TBD"],
  [("USB10G_P21_4", I), ("USB10G_HUB_DS1_4", O), ("3V3_S0", I)]),
 ("Platform power: 12 V entry, eFuse, CPU aux + PROM21 rails", "power.kicad_sch", [
   "LUG1/LUG2 stock 12 V entry -> U11 TPS259851 eFuse -> 12V_CB; U15 INA228 0x45 on I2C0, ALERT + FLT# -> PWR_ALERT_N (as LGA1700)",
   "U4 CPU S5/aux: VDD_18_S5, VDD_33_S5, VDD_MISC_S5 (USB PHY) from 5V_SBY / 3V3_SB [rail list Unverified, AMD NDA]",
   "U8 VDDIO_MEM_S3 1.1 V (DDR5 PHY); U7 5 V VIN_BULK for 4 UDIMM PMICs; U6 PROM21 rails (core ~1.0 V, 1.8 V, 3.3 V) [Estimate]",
   "3V3_S0 load switch (hub, M.2); sequencing by the EC (RAIL_EN_S5 / RAIL_EN_S0, RAILS_PGOOD)"],
  [("5V_SBY", I), ("3V3_SB", I), ("RAIL_EN_S5", I), ("RAIL_EN_S0", I), ("RAILS_PGOOD", O),
   ("12V_CB", O), ("5V_VIN_BULK", O), ("3V3_S5", O), ("3V3_S0", O), ("VDD_18_S5", O), ("VDD_33_S5", O), ("VDD_MISC_S5", O),
   ("VDDIO_MEM_S3", O), ("PROM21_RAILS", O), ("I2C0_SCL", B), ("I2C0_SDA", B), ("PWR_ALERT_N", O)]),
 ("EC, firmware, clocks, RTC, debug", "ec_fw.kicad_sch", [
   "U9 RP2350 EC (as LGA1700): AM5 sequencing RSMRST_L -> PWR_BTN_L -> SLP_S5/S3 -> rails -> PWR_GOOD; VR_EN / VR_PGOOD",
   "Buffers to CPU-LINK (names unchanged): SUS_S3# = SLP_S3_L, SUS_S4_S5# = SLP_S5_L, PLTRST# = PCIE_RST_L, THERMTRIP#, RSMRST_OUT#",
   "LPT actuator on AM5: PPT/TDC/EDC via the SMU (Dasharo/openSIL interface TBD) - fallback fixed cTDP 45 W + PROCHOT_L (CARRIER_HOT#)",
   "U10 FCH SPI ROM 32 MB (Dasharo coreboot + openSIL + PSP blobs), external programming; J4 SPI TPM header (fTPM default)",
   "Y1 48 MHz [Unverified] + 32.768 kHz; VBAT_RTC: IOB coin cell (J3 B26) diode-OR 3V3_S5 -> CPU RTC well; BT1 DNP; J5 debug (FCH UART, SWD, POST)"],
  [("3V3_SB", I), ("PWRBTN_N", I), ("RSTBTN_N", I), ("PWR_BTN_L", O), ("SYS_RESET_L", O), ("RSMRST_L", O), ("PWR_GOOD", O),
   ("SLP_S3_L", I), ("SLP_S5_L", I), ("PCIE_RST_L", I), ("THERMTRIP_L", I), ("VR_EN", O), ("VR_PGOOD", I),
   ("RAIL_EN_S5", O), ("RAIL_EN_S0", O), ("RAILS_PGOOD", I), ("SUS_S3_N", O), ("SUS_S5_N", O), ("RSMRST_OUT_N", O), ("PLTRST_N", O),
   ("THERMTRIP_N", O), ("CARRIER_HOT_N", I), ("PROCHOT_L", B), ("UART0", B), ("I2C0_SCL", B), ("I2C0_SDA", B), ("FAN_PWMOUT", O), ("FAN_TACHIN", I),
   ("FCH_SPI", B), ("FCH_UART0", B), ("CLK_48M", O), ("RTC_32K", O), ("VBAT_RTC_IOB", I), ("VBAT_RTC_CB", O)]),
 ("CPU-LINK J1 (Mini Cool Edge 224 fingers) - AM5 map", "cpu_link.kicad_sch", [
   "J1 card-edge fingers: physical and signal names = ICD rev 3 / LGA1700 CB; AM5 sources in docs/cpulink_224_pinout_am5.csv",
   "FP lanes 0-7 = CPU GFX x8 (8000G); FP lanes 8-15 routed, unused until 7000/9000 x16; FS x4 = CPU GPP; FP/FS REFCLK from the CPU GPP_CLK",
   "USB2 MCU/FACEP/FACES = PROM21 USB2; USB2 SPARE = CPU native USB2; SATA0 = PROM21; SMBus = FCH SMB0 (0R DNP isolation, O-4)",
   "Sideband names unchanged (PWRBTN#, RSTBTN#, SUS_S3#, SUS_S4_S5#, PLTRST#, THERMTRIP#, CARRIER_HOT#, WAKE0#, PWR_ALERT#, UART0, I2C0)",
   "UART0 LPT_SET semantics: PPT/TDC/EDC (AM5) instead of PL1/PL2 -> BP MCU firmware delta only"],
  [("5V_SBY", O), ("3V3_SB", O), ("PCIE_GFX_L0_7", I), ("PCIE_GFX_L8_15", I), ("PCIE_GPP_FS_X4", I), ("GPP_CLK_FP", I), ("GPP_CLK_FS", I),
   ("USB2_P21_MCU", B), ("USB2_P21_FACEP", B), ("USB2_P21_FACES", B), ("USB2_CPU0", I), ("SATA0", B),
   ("PWRBTN_N", O), ("RSTBTN_N", O), ("SUS_S3_N", I), ("SUS_S5_N", I), ("RSMRST_OUT_N", I), ("PLTRST_N", I), ("THERMTRIP_N", I),
   ("CARRIER_HOT_N", O), ("PWR_ALERT_N", I), ("FAN_PWMOUT", I), ("FAN_TACHIN", O), ("UART0", B), ("I2C0_SCL", B), ("I2C0_SDA", B),
   ("SMB0_SCL", B), ("SMB0_SDA", B), ("WAKE_L", B)]),
 ("IOB-HS J3 (MCIO 124 RA, back) - AM5 map", "iob_hs.kicad_sch", [
   "J3 MCIO 124 right-angle, same part/position as the LGA1700 CB; IOB end and signal names unchanged (docs/mp62-cb-j3_mcio124_host-end_am5.csv)",
   "C1/C2 = CPU native 10G (USB4 ports at 10G), C3-C6 = PROM21 10G #0-3, A1-A4 = U16 hub DS1-4, HS1 USB2 = PROM21",
   "i226 #1 x1 + ASM1182e x1 = PROM21 PCIe (REFCLK/CLKREQ/PERST from PROM21 [Unverified]); WAKE -> FCH WAKE_L",
   "DDIB = APU DP0 4-lane, DDIC = DP1 2-lane, AUX AC-coupled; HPD_B/HPD_C level (3.3 V) vs AM5 HPD input TBD",
   "VBAT_RTC in (IOB coin cell); USB_OC# -> PROM21 USB_OC0_L"],
  [("USB10G_CPU0", I), ("USB10G_CPU1", I), ("USB10G_P21_0_3", I), ("USB10G_HUB_DS1_4", I), ("USB2_HS1", B),
   ("PCIE_I226_X1", I), ("PCIE_I226B_X1", I), ("I226_REFCLK", I), ("I226B_REFCLK", I), ("I226_CLKREQ_L", B), ("I226B_CLKREQ_L", B),
   ("I226_PERST_L", I), ("WAKE_L", B), ("DP0_ML", I), ("DP0_AUX", B), ("DP1_ML", I), ("DP1_AUX", B), ("HPD_B", O), ("HPD_C", O),
   ("VBAT_RTC_IOB", O), ("USB_OC_L", O)]),
 ("Boot M.2 J8 (CPU GPP x4)", "m2_boot.kicad_sch", [
   "J8 M.2 2280 M-key (back, same position as the LGA1700 CB); source moves from PCH x4 to CPU GPP PCIe 4.0 x4",
   "REFCLK = CPU GPP_CLK; PERST# = PCIE_RST_L; 3V3_S0 ~2.5 A"],
  [("PCIE_GPP_M2_X4", I), ("GPP_CLK_M2", I), ("PCIE_RST_L", I), ("3V3_S0", I)]),
]
def text(s, x, y, size=1.27):
    s = s.replace('"', "'")
    return f'\t(text "{s}"\n\t\t(exclude_from_sim no)\n\t\t(at {x:.2f} {y:.2f} 0)\n\t\t(effects (font (size {size} {size})) (justify left bottom))\n\t\t(uuid "{U()}")\n\t)\n'

# ---------- sub-sheet stub files ----------
SHEET_UUIDS = [U() for _ in SHEETS]

def stub_lib(sym, pins):
    n = len(pins)
    yb = -(n - 1) * 2.54 - 1.27
    o = f'\t\t(symbol "MP62:{sym}"\n\t\t\t(pin_names (offset 1.016))\n\t\t\t(exclude_from_sim yes)\n\t\t\t(in_bom no)\n\t\t\t(on_board no)\n'
    for k, v, yy, hide in (("Reference", "#BLK", 2.54, ""), ("Value", sym, 3.81, ""), ("Footprint", "", 0, " (hide yes)"), ("Datasheet", "", 0, " (hide yes)"),
                           ("Description", "Non-BOM block stub: one passive pin per hierarchical label (ERC anchor)", 0, " (hide yes)")):
        o += f'\t\t\t(property "{k}" "{v}"\n\t\t\t\t(at 2.54 {yy:.2f} 0)\n\t\t\t\t(effects (font (size 1.27 1.27)) (justify left){hide})\n\t\t\t)\n'
    o += f'\t\t\t(symbol "{sym}_0_1"\n\t\t\t\t(rectangle (start 2.54 1.27) (end 25.4 {yb:.2f})\n\t\t\t\t\t(stroke (width 0.254) (type default))\n\t\t\t\t\t(fill (type background))\n\t\t\t\t)\n\t\t\t)\n'
    o += f'\t\t\t(symbol "{sym}_1_1"\n'
    for i, (pn, pt) in enumerate(pins):
        o += f'\t\t\t\t(pin passive line\n\t\t\t\t\t(at 0 {-i * 2.54:.2f} 0)\n\t\t\t\t\t(length 2.54)\n\t\t\t\t\t(name "{pn}" (effects (font (size 1.0 1.0))))\n\t\t\t\t\t(number "{i + 1}" (effects (font (size 1.0 1.0))))\n\t\t\t\t)\n'
    o += '\t\t\t)\n\t\t)\n'
    return o

written = set()
for idx, (name, fname, desc, pins) in enumerate(SHEETS):
    if fname in written:
        continue
    written.add(fname)
    s = f'(kicad_sch\n\t{VER}\n\t(uuid "{U()}")\n\t(paper "A4")\n'
    sym = "STUB_" + fname.replace(".kicad_sch", "").upper()
    insts = [(SHEET_UUIDS[k], k) for k, sh in enumerate(SHEETS) if sh[1] == fname]
    s += f'\t(title_block\n\t\t(title "MP62 AM5 CPU board: {name}")\n\t\t(date "2026-10-04")\n\t\t(rev "A-am5-bd0")\n\t\t(comment 1 "Block stub: hierarchical labels + one non-BOM stub symbol (#BLKn, passive pins) so ERC sees the nets; circuit TBD")\n\t)\n\t(lib_symbols\n' + stub_lib(sym, pins) + '\t)\n'
    y = 30.48
    for (pn, pt) in pins:
        s += f'\t(hierarchical_label "{pn}"\n\t\t(shape {pt})\n\t\t(at 38.1 {y:.2f} 180)\n\t\t{F} (justify right))\n\t\t(uuid "{U()}")\n\t)\n'
        y += 2.54
    s += f'\t(symbol\n\t\t(lib_id "MP62:{sym}")\n\t\t(at 38.1 30.48 0)\n\t\t(unit 1)\n\t\t(exclude_from_sim yes)\n\t\t(in_bom no)\n\t\t(on_board no)\n\t\t(dnp no)\n\t\t(uuid "{U()}")\n'
    s += f'\t\t(property "Reference" "#BLK{insts[0][1] + 1}"\n\t\t\t(at 40.64 27.94 0)\n\t\t\t(effects (font (size 1.27 1.27)) (justify left) (hide yes))\n\t\t)\n'
    s += f'\t\t(property "Value" "{sym}"\n\t\t\t(at 40.64 26.67 0)\n\t\t\t(effects (font (size 1.27 1.27)) (justify left) (hide yes))\n\t\t)\n'
    for i in range(len(pins)):
        s += f'\t\t(pin "{i + 1}"\n\t\t\t(uuid "{U()}")\n\t\t)\n'
    s += '\t\t(instances\n\t\t\t(project "macpro62_am5"\n'
    for su, k in insts:
        s += f'\t\t\t\t(path "/{ROOT_UUID}/{su}"\n\t\t\t\t\t(reference "#BLK{k + 1}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n'
    s += '\t\t\t)\n\t\t)\n\t)\n'
    s += text("BLOCK STUB (rev A block diagram). Contents planned:", 76.2, 30.48, 1.5)
    for i, d in enumerate(desc):
        s += text("- " + d, 76.2, 35.56 + i * 3.81)
    s += ')\n'
    open(os.path.join(PRJ, fname), "w").write(s)

# ---------- project symbol library for the stub symbols (keeps ERC free of lib_symbol_issues) ----------
_lib = '(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "mp62_build_sch")\n\t(generator_version "9.0")\n'
_done = set()
for (name, fname, desc, pins) in SHEETS:
    if fname in _done:
        continue
    _done.add(fname)
    _lib += stub_lib("STUB_" + fname.replace(".kicad_sch", "").upper(), pins).replace('(symbol "MP62:', '(symbol "')
_lib += ')\n'
open(os.path.join(PRJ, "MP62_AM5_Stubs.kicad_sym"), "w").write(_lib)
open(os.path.join(PRJ, "sym-lib-table"), "w").write('(sym_lib_table\n  (version 7)\n  (lib (name "MP62")(type "KiCad")(uri "${KIPRJMOD}/MP62_AM5_Stubs.kicad_sym")(options "")(descr "MP62 AM5 CB block-stub symbols (non-BOM)"))\n)\n')


# ---------- root sheet ----------
s = f'(kicad_sch\n\t{VER}\n\t(uuid "{ROOT_UUID}")\n\t(paper "A2")\n'
s += '\t(title_block\n\t\t(title "MacPro6,2 AM5 CPU board (CB) DRAFT - top-level block diagram")\n\t\t(date "2026-10-04")\n\t\t(rev "A-am5-bd0")\n\t\t(company "MacPro6,2 / Aidan Winkler")\n'
s += '\t\t(comment 1 "Ryzen 8000G (Dasharo) + PROM21 + SVI3 3-rail VRM + DDR5 2DPC; connector physicals = LGA1700 CB / ICD rev 3")\n\t\t(comment 2 "See macpro62-am5-board-plan.md; nets are block-level bundles")\n\t)\n\t(lib_symbols)\n'
s += text("MP62 AM5 CPU BOARD rev A-am5 DRAFT - BLOCK DIAGRAM. Sheets are stubs (labels only). Same label name = same net (bundle).", 25.4, 20.32, 2.0)
s += text("Off-board: J1 CPU-LINK (card edge -> BP) | J3 IOB-HS MCIO 124 | J8 M.2 boot | LUG1/LUG2 12 V | J5 debug | J4 TPM. AMD pin names (NDA) replaced by functional names.", 25.4, 25.4, 1.6)
W = 60.96
XS = [38.1, 165.1, 292.1, 419.1]
hs = [g(5.08 + 2.54 * len(sh[3])) for sh in SHEETS]
RY = [38.1]
for r in range(1, 3):
    RY.append(g(RY[-1] + max(hs[(r - 1) * 4:r * 4]) + 22.86))
cols = [(XS[i % 4], RY[i // 4]) for i in range(len(SHEETS))]
page = 2
for idx, (name, fname, desc, pins) in enumerate(SHEETS):
    x, y = cols[idx]
    h = hs[idx]
    s += f'\t(sheet\n\t\t(at {x:.2f} {y:.2f})\n\t\t(size {W:.2f} {h:.2f})\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n'
    s += '\t\t(stroke (width 0.1524) (type solid))\n\t\t(fill (color 0 0 0 0.0000))\n'
    s += f'\t\t(uuid "{SHEET_UUIDS[idx]}")\n'
    s += f'\t\t(property "Sheetname" "{name}"\n\t\t\t(at {x:.2f} {y - 0.71:.2f} 0)\n\t\t\t{F} (justify left bottom))\n\t\t)\n'
    s += f'\t\t(property "Sheetfile" "{fname}"\n\t\t\t(at {x:.2f} {y + h + 0.59:.2f} 0)\n\t\t\t{F} (justify left top))\n\t\t)\n'
    py = y + 2.54
    labels = ""
    for (pn, pt) in pins:
        left = (pt == "input")
        px = x if left else x + W
        ang = 180 if left else 0
        just = "left" if left else "right"
        s += f'\t\t(pin "{pn}" {pt}\n\t\t\t(at {px:.2f} {py:.2f} {ang})\n\t\t\t(uuid "{U()}")\n\t\t\t{F} (justify {just}))\n\t\t)\n'
        lx = px - 10.16 if left else px + 10.16
        labels += f'\t(wire\n\t\t(pts (xy {px:.2f} {py:.2f}) (xy {lx:.2f} {py:.2f}))\n\t\t(stroke (width 0) (type default))\n\t\t(uuid "{U()}")\n\t)\n'
        lang = 0 if not left else 180
        ljust = "left" if not left else "right"
        labels += f'\t(label "{pn}"\n\t\t(at {lx:.2f} {py:.2f} {lang})\n\t\t(fields_autoplaced yes)\n\t\t{F} (justify {ljust} bottom))\n\t\t(uuid "{U()}")\n\t)\n'
        py += 2.54
    s += f'\t\t(instances\n\t\t\t(project "macpro62_am5"\n\t\t\t\t(path "/{ROOT_UUID}"\n\t\t\t\t\t(page "{page}")\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
    s += labels
    page += 1
s += '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n)\n'
open(os.path.join(PRJ, "macpro62_am5.kicad_sch"), "w").write(s)
# net sanity: every bundle on >= 2 sheets
from collections import Counter
c = Counter(pn for sh in SHEETS for pn, pt in set(sh[3]))
single = [k for k, v in c.items() if v < 2]
print("schematic written: %d sheets, %d nets, single-sheet nets: %s" % (len(SHEETS), len(c), single or "none"))
