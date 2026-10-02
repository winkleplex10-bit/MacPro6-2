#!/usr/bin/env python3
"""Generate MP62_IO.kicad_sym + macpro62-io-board.kicad_sch (KiCad 9) for the MacPro6,2 I/O board IOB rev A0.
Flat sheet, label connectivity (a net label or a no-connect flag on every pin end), all instances on the 2.54 grid.
REAL pinouts: MCIO 124 (MP62 IOB-HS v0.1 CSV, docs/), MCIO 74 display link (MP62-FACE CSV), USB Type-C receptacle,
USB 3.x Std-A, HDMI type A, BL24C64A / 25-series flash SOIC-8, Micro-Fit J5 (= BP J2), GH15 IOB-LINK (CR-BP-IOB).
LOGICAL pin numbers (map from datasheets before layout): TPS65994AD, TUSB1046A, TUSB1002A, CH334R, i226-V, TDP158,
CM108B, PAM8302A, TLC59116, LIS2DH12, TPS259824, TPS56C215, TLV62585, VBUS switches, RJ45 magjack, stock audio/PSU headers
(stock headers: UNCONFIRMED pin functions - see plan section 9 for the probing procedure)."""
import csv, os, uuid
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.abspath(os.path.join(HERE, ".."))
NAME = "macpro62-io-board"; LIBN = "MP62_IO"; FPL = "MP62_IO"
U = lambda: str(uuid.uuid4())
ROOT = U()
SYMS = {}

def addsym(name, pins, ref, fp, desc, w=None):
    SYMS[name] = dict(pins=pins, ref=ref, fp=FPL + ":" + fp, desc=desc, w=w)
def ic(name, left, right, ref, fp, desc, w=None, start=1):
    """auto-numbered logical pins; pin names must be unique"""
    pins = []; n = start
    for side, lst in (("L", left), ("R", right)):
        for nm in lst:
            pins.append((str(n), nm, side)); n += 1
    addsym(name, pins, ref, fp, desc, w)

# ---------------- symbols ----------------
hs = list(csv.DictReader(open(os.path.join(PRJ, "docs", "mp62-iob-hs1_mcio124_pinout_v0.2.csv"))))
addsym("MCIO124_IOB_HS1", [(r["contact"], r["signal"], "L" if r["contact"][0] == "A" else "R") for r in hs] + [("MP", "SHIELD/MP", "R")],
       "J", "MP62_MCIO_124P_RA_SFF-TA-1016", "MCIO 124P RA (Amphenol G97R24332HR class), MP62 IOB-HS v0.1 pinout, CB J3 -> IOB")
dl = list(csv.DictReader(open("/workspace/macpro62-face/pinouts/mp62-face-v0.1_mcio74_displaylink_module-end.csv")))
addsym("MCIO74_DisplayLink", [(r["contact"], r["signal"], "L" if r["contact"][0] == "A" else "R") for r in dl] + [("MP", "SHIELD/MP", "R")],
       "J", "MP62_MCIO_74P_RA_SFF-TA-1016", "MCIO 74P RA, MP62-FACE display-link pinout (module end), Face P -> IOB")
usbc = [("A1", "GND_A1", "L"), ("A4", "VBUS_A4", "L"), ("A9", "VBUS_A9", "L"), ("B4", "VBUS_B4", "L"), ("B9", "VBUS_B9", "L"), ("A5", "CC1", "L"),
        ("B5", "CC2", "L"), ("A6", "D+_A6", "L"), ("A7", "D-_A7", "L"), ("B6", "D+_B6", "L"), ("B7", "D-_B7", "L"), ("A8", "SBU1", "L"), ("B8", "SBU2", "L"),
        ("A12", "GND_A12", "L"), ("A2", "TX1+", "R"), ("A3", "TX1-", "R"), ("B11", "RX1+", "R"), ("B10", "RX1-", "R"), ("B2", "TX2+", "R"), ("B3", "TX2-", "R"),
        ("A11", "RX2+", "R"), ("A10", "RX2-", "R"), ("B1", "GND_B1", "R"), ("B12", "GND_B12", "R"), ("S", "SHIELD", "R")]
addsym("USB_C_24P", usbc, "J", "MP62_USB_C_24P_Vertical_PLACEHOLDER", "USB Type-C 24P receptacle, vertical (USB-C spec pinout)")
addsym("USB_A3", [("1", "VBUS", "L"), ("2", "D-", "L"), ("3", "D+", "L"), ("4", "GND", "L"), ("7", "GND_DRAIN", "L"), ("5", "SSRX-", "R"), ("6", "SSRX+", "R"),
                  ("8", "SSTX-", "R"), ("9", "SSTX+", "R"), ("S", "SHIELD", "R")], "J", "MP62_USB_A3_9P_Vertical_PLACEHOLDER", "USB 3.x Std-A receptacle, vertical (USB 3.2 pinout)")
addsym("HDMI_A", [(str(i), n, "L" if i <= 10 else "R") for i, n in enumerate(
    ["D2+", "D2_S", "D2-", "D1+", "D1_S", "D1-", "D0+", "D0_S", "D0-", "CK+", "CK_S", "CK-", "CEC", "UTIL", "SCL", "SDA", "DDC_GND", "+5V", "HPD"], 1)] + [("S", "SHIELD", "R")],
    "J", "MP62_HDMI_A_Vertical_PLACEHOLDER", "HDMI type A receptacle, vertical (HDMI 1.4/2.0 pinout)")
addsym("RJ45_NOMAG", [(str(k), "P%d" % k, "L") for k in range(1, 9)] + [("S", "SHIELD", "R")], "J", "MP62_RJ45_Vertical_SMD_NoMag_PLACEHOLDER",
       "Vertical SMD RJ45 8P8C, no magnetics, no LED (Lingqiang ZJLQ-RJ45-SMD-PCB125-8P8C C55547809, height <= 13.0 VERIFY) - D-IO15")
ic("V24P05S", sum([["C%d+" % i, "C%d-" % i, "CCT%d" % i] for i in range(1, 5)], []), sum([["L%d+" % i, "L%d-" % i, "LCT%d" % i] for i in range(1, 5)], []), "T",
   "MP62_JASN_V24P05S_SMD-24P_15.1x7.1_PLACEHOLDER", "JASN V24P05S 2.5GBASE-T magnetics 1CT:1CT (LCSC C2827281), LOGICAL pins (map from the JASN drawing)", w=12.7)
ic("EMC2101", ["VDD", "SCL", "SDA", "GND"], ["FAN_PWM", "ALERT#/TACH", "DP", "DN"], "U", "MSOP-8_3x3mm_P0.65mm", "Microchip EMC2101 fan controller + temp sensor, SMBus 0x4C (LOGICAL pins)", w=12.7)
ic("ASM1182E", ["UP_RXP", "UP_RXN", "UP_TXP", "UP_TXN", "UP_REFCLKP", "UP_REFCLKN", "PERST#", "XI", "XO", "VCC3P3", "VCC1P0", "GND"],
   ["DN0_TXP", "DN0_TXN", "DN0_RXP", "DN0_RXN", "DN0_REFCLKP", "DN0_REFCLKN", "DN0_CLKREQ#", "DN1_TXP", "DN1_TXN", "DN1_RXP", "DN1_RXN", "DN1_REFCLKP", "DN1_REFCLKN", "DN1_CLKREQ#", "EP_GND"],
   "U", "MP62_ASMedia_ASM1182e_QFN-64_9x9_P0.5_PLACEHOLDER", "ASMedia ASM1182e PCIe Gen2 1:2 packet switch (downstream REFCLK outputs per datasheet: VERIFY), LOGICAL pins", w=15.24)
CONNC = [("1", "GND"), ("2", "GND"), ("3", "WL_PCIE_TX+"), ("4", "FAN_12V"), ("5", "WL_PCIE_TX-"), ("6", "FAN_12V"), ("7", "GND"), ("8", "FAN_12V"), ("9", "WL_PCIE_RX+"), ("10", "GND"),
         ("11", "WL_PCIE_RX-"), ("12", "FAN_PWM"), ("13", "GND"), ("14", "FAN_TACH"), ("15", "WL_REFCLK+"), ("16", "GND"), ("17", "WL_REFCLK-"), ("18", "BT_USB2_DP"), ("19", "GND"),
         ("20", "BT_USB2_DN"), ("21", "WL_PERST#"), ("22", "GND"), ("23", "WL_CLKREQ#"), ("24", "3V3_WL"), ("25", "WL_WAKE#"), ("26", "3V3_WL"), ("27", "LED_WLAN#"), ("28", "3V3_WL"),
         ("29", "NC29"), ("30", "3V3_WL"), ("31", "NC31"), ("32", "GND"), ("33", "NC33"), ("34", "3V3_BT"), ("35", "FAN_SENSE"), ("36", "GND"), ("37", "NC37"), ("38", "NC38"),
         ("39", "GND"), ("40", "GND")]
addsym("UFL", [("1", "SIG", "L"), ("2", "GND", "R")], "J", "MP62_UFL_Hirose_U.FL-R-SMT-1", "Hirose U.FL-R-SMT-1 50 ohm receptacle (C88373)")
addsym("CONNC_40", [(k, n + ("" if n not in ("GND", "FAN_12V", "3V3_WL") else "_" + k), "L" if int(k) % 2 else "R") for k, n in CONNC], "J", "MP62_Hirose_DF12-40DS-0.5V_PLACEHOLDER",
       "CONN_C fan + AirPort 2x20 @ 0.5 (stock press B2B, DF12-40DS-0.5V(86) candidate). PROPOSED pinout - every pin UNCONFIRMED until M-IOC1 probing.")
addsym("RJ45_HR913790A", [("1", "CT", "L")] + [(str(k), "TRD%d%s" % ((k - 2) // 2 + 1, "+-"[(k - 2) % 2]), "L") for k in range(2, 10)] +
       [("10", "BS_CAP", "R"), ("11", "LEDGO_11", "R"), ("12", "LEDGO_12", "R"), ("13", "LEDY_K", "R"), ("14", "LEDY_A", "R"), ("S", "SHIELD", "R")],
       "J", "MP62_RJ45_HanRun_HR913790A_Vertical_2G5", "HanRun HR913790A vertical RJ45, integrated 2.5G/5G magnetics (P1 = common CT, P10 = 1000 pF Bob-Smith to chassis); green/orange bicolour 11/12, yellow 14(A)/13(K)")
addsym("AUDIO_STOCK_50P", [(str(i), "P%d" % i, "L" if i <= 25 else "R") for i in range(1, 51)] + [("MP", "MP", "R")], "J",
       "MP62_StockAudio_EdgeCard_50P_P0.5_PLACEHOLDER", "Stock audio module connector placeholder 50P 0.5 mm (count, pitch and pinout UNCONFIRMED)")
addsym("PSU_DC_12P", [(str(i), "P%d" % i, "L" if i <= 6 else "R") for i in range(1, 13)], "J", "MP62_StockPSU_DC_12P_P1.5_Shrouded_PLACEHOLDER",
       "Stock PSU DC-out header 12P (pinout UNCONFIRMED)")
addsym("PSU_SIG_6P", [(str(i), "P%d" % i, "L") for i in range(1, 7)] + [("MP", "MP", "R")], "J", "MP62_StockPSU_SIG_6P_P1.25_Vertical_PLACEHOLDER",
       "Stock PSU signal header 6P (pinout UNCONFIRMED)")
addsym("MicroFit_2x4", [(str(i), "P%d" % i, "L" if i <= 4 else "R") for i in range(1, 9)], "J", "Molex_Micro-Fit_3.0_43045-0812_2x04_P3.00mm_Vertical", "Molex Micro-Fit 3.0 2x4 vertical")
addsym("GH15", [(str(i), "P%d" % i, "L") for i in range(1, 16)] + [("MP", "MP", "R")], "J", "JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical", "JST GH 15P vertical")
addsym("FPC14", [(str(i), "P%d" % i, "L" if i <= 7 else "R") for i in range(1, 15)] + [("MP", "MP", "R")], "J", "Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal", "FPC/ZIF 14P 0.5 mm (HX FPC 0.5-14P HYH2.0 C7502869, dual-side contacts); land pattern placeholder")
addsym("SH2", [("1", "1", "L"), ("2", "2", "L"), ("MP", "MP", "R")], "J", "JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical", "JST SH 2P vertical (speaker)")
ic("TPS65994AD", ["PP5V", "VIN_3V3", "LDO_3V3", "LDO_1V5", "ADCIN1", "ADCIN2", "HRESET", "I2C1_SCL", "I2C1_SDA", "I2C1_IRQ#", "I2C2_SCL", "I2C2_SDA", "I2C2_IRQ#",
                   "SPI_MISO", "SPI_MOSI", "SPI_CLK", "SPI_CS#", "GND", "EP_GND"],
   ["PA_VBUS", "PA_CC1", "PA_CC2", "PB_VBUS", "PB_CC1", "PB_CC2", "PA_PPHV", "PB_PPHV", "GPIO0", "GPIO1", "GPIO2", "GPIO3", "GPIO4", "GPIO5",
    "I2C3_SCL", "I2C3_SDA", "I2C3_IRQ#"], "U", "MP62_TI_TPS65994AD_QFN-48_6x6_P0.4_PLACEHOLDER",
   "TI TPS65994AD dual-port USB PD controller, integrated 5 V / 3 A source paths (LOGICAL pins - map from the RSL datasheet)", w=25.4)
ic("TUSB1046A", ["SSTXP", "SSTXN", "SSRXP", "SSRXN", "DP0P", "DP0N", "DP1P", "DP1N", "DP2P", "DP2N", "DP3P", "DP3N", "AUXP", "AUXN", "HPDIN",
                 "SCL/CTL1", "SDA/CTL0", "I2C_EN", "A0", "A1", "VCC", "GND"],
   ["TX1P", "TX1N", "RX1P", "RX1N", "TX2P", "TX2N", "RX2P", "RX2N", "SBU1", "SBU2", "FLIP", "EP_GND"], "U", "MP62_TI_TUSB1046A_WQFN-40_4x6_P0.5_PLACEHOLDER",
   "TI TUSB1046A-DCI USB-C DP alt-mode linear redriver crosspoint, I2C mode (EQ via registers; LOGICAL pins)", w=20.32)
ic("TUSB1002A", ["RX1P", "RX1N", "TX2P", "TX2N", "EN", "VCC", "GND"], ["TX1P", "TX1N", "RX2P", "RX2N", "EQ1", "EQ2", "EP_GND"], "U",
   "MP62_TI_TUSB1002A_WQFN-24_4x4_P0.5_PLACEHOLDER", "TI TUSB1002A USB 3.2 Gen2 dual-channel redriver (ch1 host->port, ch2 port->host; LOGICAL pins)", w=15.24)
ic("VBUS_SW", ["IN", "EN", "GND"], ["OUT", "FLT#"], "U", "SOT-23-5", "1.5 A USB power switch SY6280/TPS2553 class (LOGICAL pins)", w=10.16)
ic("CH334R", ["UDP", "UDM", "XI", "XO", "V5", "V33", "RESET#", "GND"], ["DP1", "DM1", "DP2", "DM2", "DP3", "DM3", "DP4", "DM4", "EP_GND"], "U",
   "MP62_WCH_CH334R_QFN-24_4x4_P0.5_PLACEHOLDER", "WCH CH334R 4-port USB2 MTT hub (LOGICAL pins)", w=12.7)
ic("I226V", ["PETP", "PETN", "PERP", "PERN", "REFCLKP", "REFCLKN", "PERST#", "CLKREQ#", "WAKE#", "XTAL1", "XTAL2", "SPI_CS#", "SPI_CLK", "SPI_MOSI", "SPI_MISO",
             "VCC3P3", "SVR_SW", "VCC0P9", "GND"],
   ["MDI0P", "MDI0N", "MDI1P", "MDI1N", "MDI2P", "MDI2N", "MDI3P", "MDI3N", "LED0#", "LED1#", "LED2#", "RSET", "EP_GND"], "U",
   "MP62_Intel_i226V_QFN-56_7x7_P0.4_PLACEHOLDER", "Intel i226-V 2.5GbE controller+PHY (PCIe x1; LOGICAL pins - map from the Intel datasheet)", w=17.78)
ic("TDP158", ["IN_D0P", "IN_D0N", "IN_D1P", "IN_D1N", "IN_D2P", "IN_D2N", "IN_CKP", "IN_CKN", "SCL_SRC", "SDA_SRC", "HPD_SRC", "OE", "I2C_EN", "VCC", "VDD", "GND"],
   ["OUT_D0P", "OUT_D0N", "OUT_D1P", "OUT_D1N", "OUT_D2P", "OUT_D2N", "OUT_CKP", "OUT_CKN", "SCL_SNK", "SDA_SNK", "HPD_SNK", "EP_GND"], "U",
   "MP62_TI_TDP158_WQFN-40_5x5_P0.4_PLACEHOLDER", "TI TDP158RSB 6 Gbps AC-to-HDMI retimer (DP++ in, HDMI out; LOGICAL pins)", w=17.78)
ic("LDO5", ["IN", "EN", "GND"], ["OUT", "NC/BP"], "U", "SOT-23-5", "LDO SOT-23-5 (1-IN 2-GND 3-EN 4-NC/BP 5-OUT)", w=10.16)
ic("CM108B", ["USB_DP", "USB_DM", "XI", "XO", "VDD5", "VREG3V3", "AVDD", "GND", "AGND"],
   ["HP_L", "HP_R", "MIC_IN", "MIC_BIAS", "SPDIF_OUT", "GPIO1", "GPIO2", "GPIO3", "VOL_UP", "VOL_DN", "MUTE"], "U", "LQFP-48_7x7mm_P0.5mm",
   "C-Media CM108B USB audio codec, UAC1 (stereo DAC, mono mic ADC, S/PDIF out; LOGICAL pins)", w=17.78)
addsym("PAM8302A", [("1", "SD#", "L"), ("3", "IN+", "L"), ("4", "IN-", "L"), ("6", "VDD", "L"), ("7", "GND", "L"), ("5", "VO+", "R"), ("8", "VO-", "R"), ("2", "NC", "R")],
       "U", "MSOP-8_3x3mm_P0.65mm", "Diodes PAM8302A 2.5 W mono class-D (MSOP-8 pinout - verify)", w=12.7)
ic("TLC59116", ["REXT", "A0", "A1", "A2", "A3", "RESET#", "SCL", "SDA", "VCC", "GND"], ["OUT%d" % i for i in range(16)], "U", "TSSOP-28_4.4x9.7mm_P0.65mm",
   "TI TLC59116 16-ch constant-current I2C LED sink driver (LOGICAL pins)", w=12.7)
ic("LIS2DH12", ["SCL", "SDA", "SA0", "CS", "VDD", "VDD_IO", "GND"], ["INT1", "INT2"], "U", "LGA-12_2x2mm_P0.5mm", "ST LIS2DH12 3-axis accelerometer (LOGICAL pins)", w=12.7)
addsym("BL24C64A", [("1", "A0", "L"), ("2", "A1", "L"), ("3", "A2", "L"), ("4", "GND", "L"), ("8", "VCC", "R"), ("7", "WP", "R"), ("6", "SCL", "R"), ("5", "SDA", "R")],
       "U", "SOIC-8_3.9x4.9mm_P1.27mm", "BL24C64A-SFRC 64 kbit I2C EEPROM", w=12.7)
addsym("SPI_FLASH", [("1", "CS#", "L"), ("2", "DO", "L"), ("3", "WP#", "L"), ("4", "GND", "L"), ("8", "VCC", "R"), ("7", "HOLD#", "R"), ("6", "CLK", "R"), ("5", "DI", "R")],
       "U", "SOIC-8_3.9x4.9mm_P1.27mm", "25-series SPI NOR flash 3.3 V", w=12.7)
ic("TCA9517", ["SCLA", "SDAA", "VCCA", "GND"], ["SCLB", "SDAB", "VCCB", "EN"], "U", "MSOP-8_3x3mm_P0.65mm", "TI TCA9517DGKR level-shifting I2C buffer (LOGICAL pins)", w=12.7)
ic("74LVC1G07", ["A", "GND"], ["Y(OD)", "VCC"], "U", "SOT-23-5", "74LVC1G07 open-drain buffer, Ioff (LOGICAL pins)", w=10.16)
addsym("HALL_SOT23", [("1", "VDD", "L"), ("3", "GND", "L"), ("2", "OUT", "R")], "U", "SOT-23", "DRV5032 class omnipolar Hall switch, OD/PP out (DBZ pinout - verify)", w=10.16)
addsym("TPS259824ON", [("1", "IN", "L"), ("2", "EN/UVLO", "L"), ("3", "ILIM", "L"), ("4", "dVdt", "L"), ("5", "GND", "L"),
                       ("6", "OUT", "R"), ("7", "PG", "R"), ("8", "FLT#", "R"), ("9", "IMON", "R"), ("10", "ITIMER", "R")], "U",
       "Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm", "TI TPS259824ONRGER 2.7-18 V 15 A eFuse (LOGICAL pins)", w=17.78)
addsym("TPS56C215", [("1", "VIN", "L"), ("2", "EN", "L"), ("3", "MODE", "L"), ("4", "SS", "L"), ("5", "PGND", "L"), ("6", "AGND", "L"),
                     ("7", "SW", "R"), ("8", "BOOT", "R"), ("9", "VREG5", "R"), ("10", "FB", "R"), ("11", "PGOOD", "R")], "U",
       "MP62_TI_RNN0018A_VQFN-HR-18_3.5x3.5mm_PLACEHOLDER", "TI TPS56C215RNNR 12 A sync buck (LOGICAL pins)", w=15.24)
addsym("TLV62585", [("1", "VIN", "L"), ("2", "EN", "L"), ("3", "GND", "L"), ("4", "SW", "R"), ("5", "FB", "R"), ("6", "PG", "R")], "U", "SOT-563",
       "TI TLV62585DRL 3 A buck (LOGICAL pins)", w=12.7)
addsym("XTAL4", [("1", "X1", "L"), ("2", "GND", "L"), ("3", "X2", "R"), ("4", "GND2", "R")], "Y", "Crystal_SMD_3225-4Pin_3.2x2.5mm", "Crystal 3225 4-pin", w=7.62)
addsym("C", [("1", "~", "L"), ("2", "~", "R")], "C", "C_0402_1005Metric", "Capacitor", w=2.54)
addsym("R", [("1", "~", "L"), ("2", "~", "R")], "R", "R_0402_1005Metric", "Resistor", w=2.54)
addsym("L", [("1", "~", "L"), ("2", "~", "R")], "L", "L_Bourns_SRP1038C_10.0x10.0mm", "Inductor", w=2.54)
addsym("LED", [("1", "K", "L"), ("2", "A", "R")], "D", "LED_0603_1608Metric", "LED", w=2.54)
addsym("D", [("1", "K", "L"), ("2", "A", "R")], "D", "D_SOD-323", "Diode (pin 1 = cathode)", w=2.54)
addsym("SW2P", [("1", "1", "L"), ("2", "2", "R")], "SW", "SW_SPST_PTS810", "Push button SPST", w=5.08)
addsym("BATT", [("1", "+", "L"), ("2", "-", "R")], "BT", "BatteryHolder_Keystone_3034_1x20mm", "CR2032 / BR2032 holder (pad 1 = +)", w=5.08)
addsym("MECH1", [("1", "1", "L")], "H", "MP62_IO_MountHole_D3.8_Pad7.5", "Mechanical pad (plated)", w=5.08)

def pin_geom(s):
    L = [p for p in s["pins"] if p[2] == "L"]; R = [p for p in s["pins"] if p[2] == "R"]
    n = max(len(L), len(R)); h = (n + 1) * 2.54
    w = s["w"] or max(10, 1.27 * max([len(p[1]) for p in s["pins"]] + [4]) * 2 + 2)
    w = round(w / 2.54) * 2.54
    geo = {}
    for side, lst in (("L", L), ("R", R)):
        for i, p in enumerate(lst):
            y = h / 2 - 2.54 * (i + 1)
            y = round(round(y / 1.27) * 1.27, 2)
            x = -w / 2 - 2.54 if side == "L" else w / 2 + 2.54
            geo[p[0]] = (round(x, 2), y, 0 if side == "L" else 180, p[1])
    return w, h, geo
def sym_text(name, s):
    w, h, geo = pin_geom(s)
    pins = "".join(f'      (pin passive line (at {x} {y} {a}) (length 2.54) (name "{nm}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))\n'
                   for num, (x, y, a, nm) in geo.items())
    hide = ' (hide yes)'
    return (f'  (symbol "{name}" (pin_names (offset 0.508)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "{s["ref"]}" (at 0 {h / 2 + 1.5:.2f} 0) (effects (font (size 1.27 1.27))))\n'
            f'    (property "Value" "{name}" (at 0 {-h / 2 - 1.5:.2f} 0) (effects (font (size 1.27 1.27))))\n'
            f'    (property "Footprint" "{s["fp"]}" (at 0 0 0) (effects (font (size 1.27 1.27)){hide}))\n'
            f'    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)){hide}))\n'
            f'    (property "Description" "{s["desc"]}" (at 0 0 0) (effects (font (size 1.27 1.27)){hide}))\n'
            f'    (symbol "{name}_0_1" (rectangle (start {-w / 2:.2f} {h / 2:.2f}) (end {w / 2:.2f} {-h / 2:.2f}) (stroke (width 0.254) (type default)) (fill (type background))))\n'
            f'    (symbol "{name}_1_1"\n{pins}    )\n  )\n')
open(os.path.join(PRJ, LIBN + ".kicad_sym"), "w").write(
    '(kicad_symbol_lib (version 20241209) (generator "mp62_io") (generator_version "9.0")\n' + "".join(sym_text(n, s) for n, s in SYMS.items()) + ')\n')

# ---------------- instances ----------------
inst = []   # dict(ref, sym, value, nets(by pin number), fp, dnp, sec)
SEC = ["(none)"]
def section(t): SEC[0] = t
def add(ref, sym, value, nets, fp=None, dnp=False):
    s = SYMS[sym]; byname = {p[1]: p[0] for p in s["pins"]}
    nn = {}
    for k, v in nets.items():
        num = k if k in {p[0] for p in s["pins"]} else byname[k]
        nn[num] = v
    inst.append(dict(ref=ref, sym=sym, value=value, nets=nn, fp=fp, dnp=dnp, sec=SEC[0]))
CN = [100]; RN = [100]
def cap(n1, n2, val, dnp=False):
    add("C%d" % CN[0], "C", val, {"1": n1, "2": n2}, dnp=dnp); CN[0] += 1
def res(n1, n2, val, dnp=False):
    add("R%d" % RN[0], "R", val, {"1": n1, "2": n2}, dnp=dnp); RN[0] += 1
def dec(net, vals):
    for v in vals: cap(net, "GND", v)

# --- J1 IOB-HS1 ---
section("IOB-HS1 MCIO 124 <- CB J3 (CR-CB-IO1)")
j1 = {}
for r in hs:
    s = r["signal"]
    if s.startswith("IOB_HS_PRSNT"): j1[r["contact"]] = "GND"
    elif s.startswith("RSVD"): pass
    elif s.endswith("_SSRX_P") or s.endswith("_SSRX_N") or (s.startswith("PCIE_I226_RX")) or (s.startswith("PCIE_I226B_RX")):
        j1[r["contact"]] = s.replace("_SSRX_", "_SSRXC_").replace("_RX_", "_RXC_")     # after the IOB AC caps
    else: j1[r["contact"]] = s
j1["MP"] = "GND"
add("J1", "MCIO124_IOB_HS1", "IOB-HS1 MCIO 124 RA <- CB J3", j1)
# --- J2 display link ---
section("Display link MCIO 74 <- Face P (GPU links 0-4)")
j2 = {}
for r in dl:
    s = r["signal"]
    if s == "GND": j2[r["contact"]] = "GND"; continue
    s = s.replace("AUX2+/DDC_SCL", "HDMI_DDC_SCL_SRC").replace("AUX2-/DDC_SDA", "HDMI_DDC_SDA_SRC")
    if s.startswith("ML"):  # MLkp_l
        k, pol, l = s[2], s[3].upper(), s[5]; s = "DL%s_ML%s_%s" % (k, l, pol)
    elif s.startswith("AUX"): s = "DL%s_AUX_%s" % (s[3], "P" if s[4] == "+" else "N")
    elif s.startswith("HPD"): s = "DL_HPD%s" % s[3]
    j2[r["contact"]] = s
j2["MP"] = "GND"
add("J2", "MCIO74_DisplayLink", "DISPLAY-LINK MCIO 74 RA <- Face P", j2)

# --- USB-C ports ---
# port -> (video source prefix, lanes, aux, hpd net, PD ref, PD port)
CP = {1: ("DL0", 4, "DL0_AUX", "DL_HPD0", "U1", "A"), 2: ("DL1", 4, "DL1_AUX", "DL_HPD1", "U1", "B"), 3: ("DL3", 2, "DL3_AUX", "DL_HPD3", "U2", "A"),
      4: ("DL4", 2, "DL4_AUX", "DL_HPD4", "U2", "B"), 5: ("DDIB", 4, "DDIB_AUX", "HPD_B", "U3", "A"), 6: ("DDIC", 2, "DDIC_AUX", "HPD_C", "U3", "B")}   # C6 2-lane since v0.2 (HS1 k14 -> i226 #2)
for p in range(1, 7):
    section("USB-C C%d (DP alt mode) + TUSB1046A U%d" % (p, 10 + p))
    src, nl, aux, hpd, pd, pp = CP[p]
    c = "C%d" % p
    add("J1%d" % p, "USB_C_24P", "USB-C %s receptacle vertical (%s)" % (c, src),
        {"A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "S": "GND", "A4": "VBUS_" + c, "A9": "VBUS_" + c, "B4": "VBUS_" + c, "B9": "VBUS_" + c,
         "A5": c + "_CC1", "B5": c + "_CC2", "A6": c + "_USB2_DP", "B6": c + "_USB2_DP", "A7": c + "_USB2_DN", "B7": c + "_USB2_DN", "A8": c + "_SBU1", "B8": c + "_SBU2",
         "A2": c + "_SS_TX1_P", "A3": c + "_SS_TX1_N", "B11": c + "_SS_RX1_P", "B10": c + "_SS_RX1_N", "B2": c + "_SS_TX2_P", "B3": c + "_SS_TX2_N",
         "A11": c + "_SS_RX2_P", "A10": c + "_SS_RX2_N"})
    m = {"SSTXP": "USB3_%s_SSTX_P" % c, "SSTXN": "USB3_%s_SSTX_N" % c, "SSRXP": "USB3_%s_SSRX_P" % c, "SSRXN": "USB3_%s_SSRX_N" % c,
         "AUXP": aux + "_P", "AUXN": aux + "_N", "HPDIN": hpd, "SCL/CTL1": "PD%s_I2C3_SCL" % pd[1], "SDA/CTL0": "PD%s_I2C3_SDA" % pd[1],
         "I2C_EN": "3V3", "A0": "GND" if pp == "A" else "3V3", "A1": "GND", "VCC": "3V3", "GND": "GND", "EP_GND": "GND",
         "TX1P": c + "_SSC_TX1_P", "TX1N": c + "_SSC_TX1_N", "RX1P": c + "_SS_RX1_P", "RX1N": c + "_SS_RX1_N",
         "TX2P": c + "_SSC_TX2_P", "TX2N": c + "_SSC_TX2_N", "RX2P": c + "_SS_RX2_P", "RX2N": c + "_SS_RX2_N", "SBU1": c + "_SBU1", "SBU2": c + "_SBU2"}
    for l in range(nl):
        m["DP%dP" % l] = "%s_ML%d_P" % (src, l); m["DP%dN" % l] = "%s_ML%d_N" % (src, l)
    add("U%d" % (10 + p), "TUSB1046A", "TUSB1046A-DCI %s mux/redriver (I2C 0x%02X on PD%s I2C3)" % (c, 0x12 if pp == "A" else 0x13, pd[1]), m)
    for t in ("TX1", "TX2"):
        for pol in "PN": cap(c + "_SSC_%s_%s" % (t, pol), c + "_SS_%s_%s" % (t, pol), "220nF 0201 X7R (connector-side AC cap)")
    for pol in "PN": cap("USB3_%s_SSRX_%s" % (c, pol), "USB3_%s_SSRXC_%s" % (c, pol), "220nF 0201 X7R (host RX AC cap)")
    dec("3V3", ["100nF", "100nF", "10uF 0402"])
    for cc in ("CC1", "CC2"): cap(c + "_" + cc, "GND", "220pF 0402 50V (CC, per TPS65994 guide)")
    cap("VBUS_" + c, "GND", "10uF 0603 25V (VBUS)")
    for sb in ("SBU1", "SBU2"): pass
# --- PD controllers ---
for i, ref in enumerate(("U1", "U2", "U3")):
    section("PD controller %s (TPS65994AD) + config flash" % ref)
    a, b = 2 * i + 1, 2 * i + 2
    n = ref[1]
    add(ref, "TPS65994AD", "TPS65994AD PD #%s (C%d, C%d)" % (n, a, b),
        {"PP5V": "5V_C", "VIN_3V3": "3V3", "LDO_3V3": "PD%s_LDO3V3" % n, "LDO_1V5": "PD%s_LDO1V5" % n, "ADCIN1": "PD%s_ADCIN1" % n, "ADCIN2": "PD%s_ADCIN2" % n,
         "HRESET": "GND", "I2C1_SCL": "I2C_PD_SCL", "I2C1_SDA": "I2C_PD_SDA", "I2C1_IRQ#": "PD_INT_N", "SPI_MISO": "PD%s_SPI_MISO" % n, "SPI_MOSI": "PD%s_SPI_MOSI" % n,
         "SPI_CLK": "PD%s_SPI_CLK" % n, "SPI_CS#": "PD%s_SPI_CS#" % n, "GND": "GND", "EP_GND": "GND",
         "PA_VBUS": "VBUS_C%d" % a, "PA_CC1": "C%d_CC1" % a, "PA_CC2": "C%d_CC2" % a, "PB_VBUS": "VBUS_C%d" % b, "PB_CC1": "C%d_CC1" % b, "PB_CC2": "C%d_CC2" % b,
         "GPIO0": CP[a][3], "GPIO1": CP[b][3], "I2C3_SCL": "PD%s_I2C3_SCL" % n, "I2C3_SDA": "PD%s_I2C3_SDA" % n,
         **({"GPIO2": "DIAG_BTN_N"} if n == "1" else {"GPIO2": "DLINK_PRSNT#"} if n == "2" else {})})
    fl = {"1": "U4", "2": "U6", "3": "U7"}[n]
    add(fl, "SPI_FLASH", "W25Q80DV class 8 Mbit (PD #%s app config)" % n, {"1": "PD%s_SPI_CS#" % n, "2": "PD%s_SPI_MISO" % n, "3": "3V3", "4": "GND", "8": "3V3",
        "7": "3V3", "6": "PD%s_SPI_CLK" % n, "5": "PD%s_SPI_MOSI" % n})
    res("PD%s_SPI_CS#" % n, "3V3", "10k")
    res("PD%s_ADCIN1" % n, "PD%s_LDO1V5" % n, "ADCIN1 divider top (dead-battery/boot config per TPS65994 table)")
    res("PD%s_ADCIN1" % n, "GND", "ADCIN1 divider bottom")
    res("PD%s_ADCIN2" % n, "PD%s_LDO1V5" % n, "ADCIN2 divider top (I2C address index %s)" % n)
    res("PD%s_ADCIN2" % n, "GND", "ADCIN2 divider bottom")
    res("PD%s_I2C3_SCL" % n, "3V3", "4.7k"); res("PD%s_I2C3_SDA" % n, "3V3", "4.7k")
    dec("5V_C", ["10uF 0805 10V", "10uF 0805 10V", "100nF"]); dec("3V3", ["10uF 0402", "100nF"])
    dec("PD%s_LDO3V3" % n, ["10uF 0402"]); dec("PD%s_LDO1V5" % n, ["4.7uF 0402"])
for h in ("HPD_B", "HPD_C"): res(h, "GND", "100k HPD pull-down")
for k in (0, 1, 3, 4): res("DL_HPD%d" % k, "GND", "100k HPD pull-down")
res("PD_INT_N", "3V3", "10k")
res("DLINK_PRSNT#", "3V3", "10k (display-link cable present, read via PD #2 GPIO2)")

# --- USB-A ports ---
for p in range(1, 5):
    section("USB-A A%d (10G) + TUSB1002A U%d + VBUS switch U%d" % (p, 20 + p, 24 + p))
    a = "A%d" % p
    add("J2%d" % p, "USB_A3", "USB 3.2 Gen2 Std-A vertical %s" % a, {"1": "VBUS_" + a, "2": a + "_USB2_DN", "3": a + "_USB2_DP", "4": "GND", "7": "GND",
        "5": a + "_SS_RX_N", "6": a + "_SS_RX_P", "8": a + "_SS_TX_N", "9": a + "_SS_TX_P", "S": "GND"})
    add("U2%d" % p, "TUSB1002A", "TUSB1002A %s redriver" % a, {"RX1P": "USB3_%s_SSTX_P" % a, "RX1N": "USB3_%s_SSTX_N" % a, "TX1P": a + "_SSC_TX_P", "TX1N": a + "_SSC_TX_N",
        "RX2P": a + "_SS_RX_P", "RX2N": a + "_SS_RX_N", "TX2P": "USB3_%s_SSRX_P" % a, "TX2N": "USB3_%s_SSRX_N" % a, "EN": "3V3", "VCC": "3V3", "GND": "GND",
        "EQ1": "REDRV_EQ", "EQ2": "REDRV_EQ", "EP_GND": "GND"})
    for pol in "PN":
        cap(a + "_SSC_TX_" + pol, a + "_SS_TX_" + pol, "220nF 0201 X7R (port TX AC cap)")
        cap("USB3_%s_SSRX_%s" % (a, pol), "USB3_%s_SSRXC_%s" % (a, pol), "220nF 0201 X7R (host RX AC cap)")
    add("U2%d" % (4 + p), "VBUS_SW", "SY6280AAC / TPS2553 1.5 A switch %s" % a, {"IN": "5V_A", "EN": "5V_A", "GND": "GND", "OUT": "VBUS_" + a, "FLT#": "USB_OC#"})
    cap("VBUS_" + a, "GND", "100uF 1206 6.3V (port bulk, USB 2.0 120 uF rule with 2 ports)")
    dec("3V3", ["100nF", "100nF"])
res("REDRV_EQ", "GND", "EQ strap (value per TUSB1002A EQ table, trace length ~40 mm)")
res("USB_OC#", "3V3", "10k (PCH OC0# pull-up is on the CB; DNP)", dnp=True)

# --- USB2 hubs ---
section("USB2 hubs CH334R (H1a U34, H1b U32, H2 U33, H3 U35)")
hubs = [("U34", "Y1", "USB2_HS1", ["C1", "C2", "C3", "H1B"], "H1a <- HS1 USB2 (CB PCH port)"),
        ("U32", "Y2", "H1B_USB2", ["C4", "C5", "C6", "AUD"], "H1b <- H1a port 4"),
        ("U33", "Y3", "USB2_LINK", ["A1", "A2", "A3", "H3"], "H2 <- IOB-LINK USB2 (BP spare)"),
        ("U35", "Y7", "H3_USB2", ["A4", "BT", "SPARE1", "SPARE2"], "H3 <- H2 port 4 (A4 + AirPort Bluetooth + 2 spare), 2026-10-02")]
for ref, y, up, dn, val in hubs:
    m = {"UDP": up + "_DP", "UDM": up + "_DN", "XI": ref + "_XI", "XO": ref + "_XO", "V5": "5V_A", "V33": ref + "_V33", "RESET#": ref + "_V33", "GND": "GND", "EP_GND": "GND"}
    for i, d in enumerate(dn):
        if not d.startswith("SPARE"): m["DP%d" % (i + 1)] = d + "_USB2_DP"; m["DM%d" % (i + 1)] = d + "_USB2_DN"
    add(ref, "CH334R", "CH334R " + val, m)
    add(y, "XTAL4", "12MHz 3225 +/-20ppm", {"1": ref + "_XI", "3": ref + "_XO", "2": "GND", "4": "GND"})
    cap(ref + "_XI", "GND", "22pF"); cap(ref + "_XO", "GND", "22pF")
    dec(ref + "_V33", ["1uF"]); dec("5V_A", ["1uF"])

# --- Ethernet ---
section("Ethernet: 2 x i226-V (U50 -> J25 ETH1, U52 -> J26 ETH2), D-IO2 resolved 2026-10-02")
def eth_port(n, u, nvm, xt, l, j, pfx, note):
    P = "PCIE_%s" % pfx                     # PCIE_I226 / PCIE_I226B
    S = pfx                                  # I226 / I226B
    E = "ETH%d" % n
    add(u, "I226V", "Intel i226-V 2.5GbE #%d (%s)" % (n, note), {"PETP": P + "_RX_P", "PETN": P + "_RX_N", "PERP": P + "_TX_P", "PERN": P + "_TX_N",
        "REFCLKP": S + "_REFCLK+", "REFCLKN": S + "_REFCLK-", "PERST#": "I226_PERST#", "CLKREQ#": S + "_CLKREQ#", "WAKE#": "I226_WAKE#", "XTAL1": S + "_XI", "XTAL2": S + "_XO",
        "SPI_CS#": S + "_SPI_CS#", "SPI_CLK": S + "_SPI_CLK", "SPI_MOSI": S + "_SPI_MOSI", "SPI_MISO": S + "_SPI_MISO", "VCC3P3": "3V3", "SVR_SW": S + "_SVR", "VCC0P9": S + "_0V9",
        "GND": "GND", "EP_GND": "GND", **{"MDI%d%s" % (i, q): "%s_MDI%d_%s" % (E, i, q) for i in range(4) for q in "PN"},
         "RSET": S + "_RSET"})
    for pol in "PN": cap(P + "_RX_" + pol, P + "_RXC_" + pol, "220nF 0201 X7R (i226 TX -> PCH RX AC cap)")
    add(xt, "XTAL4", "25MHz 3225 +/-30ppm (i226 #%d)" % n, {"1": S + "_XI", "3": S + "_XO", "2": "GND", "4": "GND"})
    cap(S + "_XI", "GND", "18pF"); cap(S + "_XO", "GND", "18pF")
    add(nvm, "SPI_FLASH", "i226 #%d NVM 2 Mbit+ SPI flash (Intel image)" % n, {"1": S + "_SPI_CS#", "2": S + "_SPI_MISO", "3": "3V3", "4": "GND", "8": "3V3", "7": "3V3",
        "6": S + "_SPI_CLK", "5": S + "_SPI_MOSI"})
    add(l, "L", "i226 #%d SVR inductor (value per Intel design guide)" % n, {"1": S + "_SVR", "2": S + "_0V9"}, fp=FPL + ":L_1008_2520Metric")
    dec(S + "_0V9", ["22uF 0603", "1uF", "100nF"]); dec("3V3", ["22uF 0603", "1uF", "100nF", "100nF"])
    res(S + "_RSET", "GND", "RSET (value per Intel)")
    tn = "T1" if n == 1 else "T2"
    add(tn, "V24P05S", "JASN V24P05S 2.5G magnetics (%s), C2827281" % E, {**{"C%d%s" % (i + 1, "+-"[k]): "%s_MDI%d_%s" % (E, i, "PN"[k]) for i in range(4) for k in range(2)},
        **{"L%d%s" % (i + 1, "+-"[k]): "%s_TRD%d_%s" % (E, i, "PN"[k]) for i in range(4) for k in range(2)},
        **{"CCT%d" % (i + 1): E + "_CT" for i in range(4)}, **{"LCT%d" % (i + 1): "%s_LCT%d" % (E, i) for i in range(4)}})
    add(j, "RJ45_NOMAG", "Non-magnetic vertical RJ45 (%s) C55547809" % E, {**{"%d" % (1 + 2 * i + k): "%s_TRD%d_%s" % (E, i, "PN"[k]) for i in range(4) for k in range(2)}, "S": "GND"})
    cap(E + "_CT", "GND", "100nF 0402 (chip-side centre taps, i226 MDI)")
    for i in range(4): res("%s_LCT%d" % (E, i), E + "_BOB", "75R 0402 (Bob-Smith)")
    cap(E + "_BOB", "GND", "1nF 2 kV 1206 (Bob-Smith to chassis)")
    res(S + "_CLKREQ#", "3V3", "10k (DNP if CB pulls up)", dnp=True)
eth_port(1, "U50", "U51", "Y4", "L44", "J25", "I226", "HS1 k10, PCH RP3 / HSIO 12, CLKOUT_SRC12")
eth_port(2, "U52", "U53", "Y6", "L45", "J26", "I226S", "HS1 k14, PCH RP4 / HSIO 13, CLKOUT_SRC11; REFCLK on HS1 B26/B27, CLKREQ# A29")

# --- CONN_C fan + AirPort (2026-10-02) ---
section("CONN_C fan + AirPort (J7), EMC2101 U90, ASM1182e U91 (PCIe x1 shared with i226 #2)")
add("U91", "ASM1182E", "ASM1182e PCIe Gen2 switch: up = HS1 k14 (PCH RP4), dn0 = i226 #2, dn1 = AirPort", {"UP_RXP": "PCIE_I226B_TX_P", "UP_RXN": "PCIE_I226B_TX_N",
    "UP_TXP": "PCIE_I226B_RXS_P", "UP_TXN": "PCIE_I226B_RXS_N", "UP_REFCLKP": "I226B_REFCLK+", "UP_REFCLKN": "I226B_REFCLK-", "PERST#": "I226_PERST#", "XI": "U91_XI", "XO": "U91_XO",
    "VCC3P3": "3V3", "VCC1P0": "U91_1V0", "GND": "GND", "EP_GND": "GND",
    "DN0_TXP": "PCIE_I226S_TX_P", "DN0_TXN": "PCIE_I226S_TX_N", "DN0_RXP": "PCIE_I226S_RXC_P", "DN0_RXN": "PCIE_I226S_RXC_N", "DN0_REFCLKP": "I226S_REFCLK+", "DN0_REFCLKN": "I226S_REFCLK-", "DN0_CLKREQ#": "I226S_CLKREQ#",
    "DN1_TXP": "WL_PCIE_TXC+", "DN1_TXN": "WL_PCIE_TXC-", "DN1_RXP": "WL_PCIE_RX+", "DN1_RXN": "WL_PCIE_RX-", "DN1_REFCLKP": "WL_REFCLK+", "DN1_REFCLKN": "WL_REFCLK-", "DN1_CLKREQ#": "WL_CLKREQ#"})
res("I226B_CLKREQ#", "GND", "0R: HS1 CLKREQ# for RP4 held low (switch upstream needs REFCLK always)")
for pol in "PN": cap("PCIE_I226B_RXS_" + pol, "PCIE_I226B_RXC_" + pol, "220nF 0201 (switch TX -> PCH RX AC cap)")
for pol in "+-": cap("WL_PCIE_TXC" + pol, "WL_PCIE_TX" + pol, "100nF 0201 (switch TX -> AirPort RX AC cap)")
add("Y8", "XTAL4", "25MHz 3225 (ASM1182e, per datasheet)", {"1": "U91_XI", "3": "U91_XO", "2": "GND", "4": "GND"})
dec("U91_1V0", ["10uF", "1uF", "100nF"]); dec("3V3", ["10uF", "100nF", "100nF"])
add("J7", "CONNC_40", "CONN_C fan + AirPort (stock press B2B, 2x20 @0.5; pinout UNCONFIRMED, M-IOC1)", {**{k: n for k, n in CONNC if n not in ("NC29", "NC31", "NC33", "NC37", "NC38", "FAN_SENSE")},
    "21": "I226_PERST#", "25": "I226_WAKE#", "18": "BT_USB2_DP", "20": "BT_USB2_DN"})
add("J8", "UFL", "Fan-assembly antenna coax (stock type/position UNCONFIRMED, M-IOA1)", {"1": "RF_ANT_FAN", "2": "GND"})
add("J9", "UFL", "Optional antenna pass-through (DNP) - 50 ohm CPW from J8", {"1": "RF_ANT_FAN", "2": "GND"}, dnp=True)
add("U90", "EMC2101", "EMC2101 fan controller (SMBus 0x4C, PWM 25 kHz, TACH)", {"VDD": "3V3", "SCL": "I2C_SYS_SCL", "SDA": "I2C_SYS_SDA", "GND": "GND",
    "FAN_PWM": "FAN_PWM", "ALERT#/TACH": "FAN_TACH", "DP": "EMC_DP", "DN": "EMC_DN"})
res("FAN_TACH", "3V3", "10k TACH pull-up"); res("FAN_PWM", "3V3", "4k7 PWM pull-up (open-drain)")
add("Q90", "C", "MMBT3904 remote diode (or omit: EMC2101 internal sensor)", {"1": "EMC_DP", "2": "EMC_DN"})
add("F90", "R", "1.5 A PTC / 0R fuse link (+12V_IOB -> FAN_12V)", {"1": "+12V_IOB", "2": "FAN_12V"})
add("U92", "C", "3V3 WLAN load switch (TPS22918 class, 2 A) 3V3 -> 3V3_WL (LOGICAL 2-pin stand-in)", {"1": "3V3", "2": "3V3_WL"})
dec("3V3_WL", ["22uF 0805", "1uF", "100nF"]); dec("FAN_12V", ["10uF 25V 0805"])
# card side = Apple 12+6 AirPort edge (BCM94360CD / iMac 2017 BCM943602-class, P1..P18): 3V3 WiFi, LED_WLAN#, PET/PER/REFCLK, WAKE#, PERST#, CLKREQ#, USB D-/D+, 3V3 BT
# -> no W_DISABLE# / BT_DISABLE# / SMBus on the card (pins 29/31/33 left NC; the adapter board may still add parts: M-IOC1)
res("LED_WLAN#", "3V3_WL", "10k DNP (card LED_WLAN# open-drain, unused)", dnp=True)
res("WL_CLKREQ#", "3V3", "10k"); res("3V3_BT", "3V3_SB", "0R: Bluetooth 3V3 (card P18) from standby so BT can wake in S3; confirm on M-IOC1"); res("3V3_BT", "3V3", "0R DNP alt: BT from S0 3V3", dnp=True)


# --- HDMI ---
section("HDMI: GPU link 2 (DP++) -> TDP158 U60 -> J27")
# DP++ lane mapping: ML0 -> TMDS D2, ML1 -> D1, ML2 -> D0, ML3 -> clock
add("U60", "TDP158", "TDP158RSBR HDMI retimer", {"IN_D2P": "DL2_ML0_P", "IN_D2N": "DL2_ML0_N", "IN_D1P": "DL2_ML1_P", "IN_D1N": "DL2_ML1_N",
    "IN_D0P": "DL2_ML2_P", "IN_D0N": "DL2_ML2_N", "IN_CKP": "DL2_ML3_P", "IN_CKN": "DL2_ML3_N", "SCL_SRC": "HDMI_DDC_SCL_SRC", "SDA_SRC": "HDMI_DDC_SDA_SRC",
    "HPD_SRC": "DL_HPD2", "OE": "3V3", "I2C_EN": "GND", "VCC": "3V3", "VDD": "1V1_HDMI", "GND": "GND", "EP_GND": "GND",
    "OUT_D0P": "TMDS_D0_P", "OUT_D0N": "TMDS_D0_N", "OUT_D1P": "TMDS_D1_P", "OUT_D1N": "TMDS_D1_N", "OUT_D2P": "TMDS_D2_P", "OUT_D2N": "TMDS_D2_N",
    "OUT_CKP": "TMDS_CK_P", "OUT_CKN": "TMDS_CK_N", "SCL_SNK": "HDMI_SCL", "SDA_SNK": "HDMI_SDA", "HPD_SNK": "HDMI_HPD"})
add("J27", "HDMI_A", "HDMI type A vertical", {"1": "TMDS_D2_P", "2": "GND", "3": "TMDS_D2_N", "4": "TMDS_D1_P", "5": "GND", "6": "TMDS_D1_N", "7": "TMDS_D0_P",
    "8": "GND", "9": "TMDS_D0_N", "10": "TMDS_CK_P", "11": "GND", "12": "TMDS_CK_N", "15": "HDMI_SCL", "16": "HDMI_SDA", "17": "GND", "18": "HDMI_5V_OUT",
    "19": "HDMI_HPD", "S": "GND"})
add("U61", "LDO5", "TLV75511PDBV 1.1 V LDO (TDP158 VDD)", {"IN": "3V3", "EN": "3V3", "GND": "GND", "OUT": "1V1_HDMI"})
add("F1", "R", "0.5 A PTC 0805 (HDMI +5V, 55 mA min per spec)", {"1": "5V_A", "2": "HDMI_5V_OUT"}, fp=FPL + ":R_0805_2012Metric")
res("HDMI_SCL", "HDMI_5V_OUT", "1.8k DDC pull-up (sink side)"); res("HDMI_SDA", "HDMI_5V_OUT", "1.8k DDC pull-up (sink side)")
res("HDMI_HPD", "GND", "100k HPD pull-down"); res("DL_HPD2", "GND", "100k")
dec("1V1_HDMI", ["10uF 0402", "100nF", "100nF"]); dec("3V3", ["10uF 0402", "100nF"])

# --- Audio ---
section("Audio: CM108B U70 -> stock audio module J28; PAM8302A U71 -> speaker J29")
add("U70", "CM108B", "CM108B USB audio codec (UAC1)", {"USB_DP": "AUD_USB2_DP", "USB_DM": "AUD_USB2_DN", "XI": "AUD_XI", "XO": "AUD_XO", "VDD5": "5V_A",
    "VREG3V3": "AUD_3V3", "AVDD": "AUD_AVDD", "GND": "GND", "AGND": "AGND", "HP_L": "HP_L", "HP_R": "HP_R", "MIC_IN": "LINE_IN_MONO", "MIC_BIAS": "MIC_BIAS",
    "SPDIF_OUT": "SPDIF_TX", "GPIO1": "JD_HP", "GPIO2": "JD_LINE", "GPIO3": "AMP_SD#"})
add("Y5", "XTAL4", "12MHz 3225 (CM108B)", {"1": "AUD_XI", "3": "AUD_XO", "2": "GND", "4": "GND"})
cap("AUD_XI", "GND", "22pF"); cap("AUD_XO", "GND", "22pF")
dec("AUD_3V3", ["4.7uF", "100nF"]); dec("AUD_AVDD", ["10uF 0402", "100nF"]); dec("5V_A", ["10uF 0402"])
add("FB1", "R", "ferrite 600R@100MHz 0402 (AVDD)", {"1": "AUD_3V3", "2": "AUD_AVDD"})
add("NT1", "R", "0R net-tie AGND-GND (single point at codec)", {"1": "AGND", "2": "GND"})
res("LINE_L", "LINE_IN_MONO", "10k (L+R mix into the mono ADC; CM6646 upgrade = stereo line in)")
res("LINE_R", "LINE_IN_MONO", "10k")
res("MIC_BIAS", "LINE_IN_MONO", "DNP 2.2k (only if the stock line-in jack is a mic/combo)", dnp=True)
res("JD_HP", "AUD_3V3", "100k jack-detect pull-up"); res("JD_LINE", "AUD_3V3", "100k jack-detect pull-up")
# stock audio connector: PROVISIONAL mapping (UNCONFIRMED; probe per plan section 9.3)
aud = {1: "AGND", 2: "HP_L", 3: "HP_R", 4: "AGND", 5: "JD_HP", 6: "LINE_L", 7: "LINE_R", 8: "AGND", 9: "JD_LINE", 10: "SPDIF_TX", 11: "SPDIF_RX",
       12: "AUD_OPT_3V3", 13: "GND", 14: "GND"}
add("J28", "AUDIO_STOCK_50P", "Stock audio module connector PLACEHOLDER (pins 1-14 PROVISIONAL, 15-50 NC until probed)",
    {**{str(k): v for k, v in aud.items()}, "MP": "GND"})
res("3V3", "AUD_OPT_3V3", "0R (optical TX/RX module supply; 10R if the module wants filtering)")
cap("AUD_OPT_3V3", "GND", "10uF 0402")
res("SPDIF_RX", "GND", "DNP: optical input not supported by CM108B (CM6646 upgrade)", dnp=True)
add("U71", "PAM8302A", "PAM8302AAS 2.5 W mono class-D", {"1": "AMP_SD#", "3": "AMP_INP", "4": "AMP_INN", "6": "5V_A", "7": "GND", "5": "SPK_P", "8": "SPK_N"})
cap("HP_L", "AMP_INP", "100nF (L into IN+)"); cap("HP_R", "AMP_INP", "100nF (R into IN+, mono sum)")
cap("AMP_INN", "AGND", "220nF (IN- to AGND)")
dec("5V_A", ["10uF 0603", "1uF"])
res("AMP_SD#", "GND", "100k (amp off until codec GPIO3 enables; firmware mutes on JD_HP)")
add("J29", "SH2", "Speaker 2P JST SH vertical (stock speaker, pitch verify)", {"1": "SPK_P", "2": "SPK_N", "MP": "GND"})
add("H11", "MECH1", "M1.6 SMT nut SMTSO1615MTJ (speaker screw 1)", {"1": "GND"}, fp=FPL + ":MP62_SMT_Nut_M1.6_H1.5_SMTSO1615")
add("H12", "MECH1", "M1.6 SMT nut SMTSO1615MTJ (speaker screw 2)", {"1": "GND"}, fp=FPL + ":MP62_SMT_Nut_M1.6_H1.5_SMTSO1615")

# --- Stock PSU headers and pass-through ---
section("Stock PSU headers J3 (DC 12P) / J4 (signal 6P) -> J5 Micro-Fit -> BP J2  (PINOUTS UNCONFIRMED)")
add("J3", "PSU_DC_12P", "Stock PSU DC-out 12P (PROVISIONAL: 1-6 +12V, 7-12 GND - PROBE FIRST)",
    {**{str(i): "+12V_MAIN" for i in range(1, 7)}, **{str(i): "GND" for i in range(7, 13)}})
add("J4", "PSU_SIG_6P", "Stock PSU signal 6P (PROVISIONAL: 1 11V_SB, 2 GND, 3 PS_ON#, 4 PWR_OK, 5/6 PSU SMBus? - PROBE FIRST)",
    {"1": "11V_SB", "2": "GND", "3": "PS_ON#", "4": "PWR_OK", "5": "PSU_SMB_CLK", "6": "PSU_SMB_DAT", "MP": "GND"})
add("J5", "MicroFit_2x4", "Micro-Fit 2x4 -> BP J2 (1-2 12V_MAIN, 3-5 GND, 6 PS_ON#, 7 11V_SB, 8 PWR_OK)",
    {"1": "+12V_MAIN", "2": "+12V_MAIN", "3": "GND", "4": "GND", "5": "GND", "6": "PS_ON#", "7": "11V_SB", "8": "PWR_OK"})
res("PSU_SMB_CLK", "I2C_SYS_SCL", "DNP 0R (only if J4 5/6 prove to be 3.3 V SMBus)", dnp=True)
res("PSU_SMB_DAT", "I2C_SYS_SDA", "DNP 0R", dnp=True)
cap("+12V_MAIN", "GND", "10uF 1206 25V (header)")

# --- IOB-LINK and management ---
section("IOB-LINK GH15 J6 <- BP J6 (CR-BP-IOB), button, Halls, LEDs, EEPROM, accelerometer")
add("J6", "GH15", "IOB-LINK GH15 vertical <- BP J6", {"1": "3V3_SB", "2": "3V3_SB", "3": "GND", "4": "PWRBTN_IN_N", "5": "HALL_A_N", "6": "HALL_B_N", "7": "GND",
    "8": "I2C_SYS_SCL", "9": "I2C_SYS_SDA", "10": "IOB_INT_N", "11": "GND", "12": "GND", "13": "USB2_LINK_DP", "14": "USB2_LINK_DN", "15": "GND", "MP": "GND"})
add("SW1", "SW2P", "Power button PTS810 on the IOB behind the plate opening (printed cap); stock button is on the I/O-wall flex, not the stock IOB", {"1": "PWRBTN_IN_N", "2": "GND"})
cap("PWRBTN_IN_N", "GND", "100nF (debounce; pull-up on BP)")
add("J30", "SH2", "OPTIONAL 2P: stock I/O-wall button (or remote button) in parallel with SW1 - DNP until M-IOB1", {"1": "PWRBTN_IN_N", "2": "GND", "MP": "GND"}, dnp=True)
add("D31", "D", "ESD TVS 5V SOD-323 (PESD5V0S1BA class) on PWRBTN_IN_N", {"1": "PWRBTN_IN_N", "2": "GND"})
# I/O-wall flex (Apple 821-2222 I/O wall: power button + port illumination). 14 contacts counted from Aidan's photos; pin functions UNCONFIRMED.
add("J31", "FPC14", "I/O-wall flex ZIF 14P 0.5 (stock position, bottom-right F side) - pin map PROVISIONAL, see plan 9.5",
    {**{str(i): "WALL_P%d" % i for i in range(1, 15)}, "MP": "GND"})
WALL = {3: ("PWRBTN_IN_N", False, "0R: community claim pins 3+6 = power button"), 6: ("GND", False, "0R: button return (pins 3+6)"),
        1: ("GND", True, "DNP 0R: GND? (probe)"), 2: ("GND", True, "DNP 0R: GND? (probe)"), 4: ("3V3_SB", True, "DNP 0R: LED-MCU logic 3V3? (probe)"),
        5: ("3V3_SB", True, "DNP 0R: 3V3? (probe)"), 7: ("I2C_SYS_SCL", True, "DNP 0R: LED-MCU I2C SCL? (probe; must be 3.3 V)"),
        8: ("I2C_SYS_SDA", True, "DNP 0R: LED-MCU I2C SDA? (probe)"), 9: ("IOB_INT_N", True, "DNP 0R: flex IRQ/motion? (probe)"),
        10: ("5V_A", True, "DNP 0R: LED supply 5 V? (probe; S0 only)"), 11: ("GND", True, "DNP 0R: GND? (probe)"), 12: ("3V3", True, "DNP 0R: 3V3? (probe)"),
        13: ("GND", True, "DNP 0R: GND? (probe)"), 14: ("GND", True, "DNP 0R: GND? (probe)")}
for k in sorted(WALL):
    n, d, v = WALL[k]; res("WALL_P%d" % k, n, v, dnp=d)
add("SW2", "SW2P", "DIAG button TL3342 (back side)", {"1": "DIAG_BTN_N", "2": "GND"}, fp=FPL + ":SW_SPST_TL3342")
res("DIAG_BTN_N", "3V3", "10k (read via PD #1 GPIO2; S0 only)")
for ref, net in (("U30", "HALL_A_N"), ("U31", "HALL_B_N")):
    add(ref, "HALL_SOT23", "DRV5032FB (OD, 5 Hz low power) - position M-IOH1", {"1": "3V3_SB", "3": "GND", "2": net})
    cap("3V3_SB", "GND", "100nF")
add("U80", "TLC59116", "TLC59116IPWR @0x60 (A3..A0 = 0)", {"REXT": "LED_REXT", "A0": "GND", "A1": "GND", "A2": "GND", "A3": "GND", "RESET#": "3V3_SB",
    "SCL": "I2C_SYS_SCL", "SDA": "I2C_SYS_SDA", "VCC": "3V3_SB", "GND": "GND",
    **{"OUT%d" % i: "LED%d_K" % (i + 1) for i in range(8)}, "OUT8": "LED_PWR_K", **{"OUT%d" % (9 + i): "LEDP%d_K" % (i + 1) for i in range(6)}})
res("LED_REXT", "GND", "REXT ~ 2.7k (Iout ~ 7 mA max; PWM per channel)")
dec("3V3_SB", ["1uF", "100nF"])
for i in range(8): add("D%d" % (i + 1), "LED", "Diag LED %d (stock #1-#8 set) 0603" % (i + 1), {"1": "LED%d_K" % (i + 1), "2": "3V3_SB"})
add("D20", "LED", "Power/sleep LED white 0603 (under button cap)", {"1": "LED_PWR_K", "2": "3V3_SB"})
for i, t in enumerate(["HDMI label", "ETH icon", "USB-C icon upper", "USB-C icon lower", "USB icon", "audio icons"]):
    add("D%d" % (21 + i), "LED", "DNP (2026-10-02: port lighting via the 821-2222 flex on J31; the metal frame centre bar blocks board-side light pipes) light-pipe LED 0603: " + t,
        {"1": "LEDP%d_K" % (i + 1), "2": "3V3_SB"}, dnp=True)
add("U81", "LIS2DH12", "LIS2DH12TR @0x18 (optional rotate-to-light)", {"SCL": "I2C_SYS_SCL", "SDA": "I2C_SYS_SDA", "SA0": "GND", "CS": "3V3_SB", "VDD": "3V3_SB",
    "VDD_IO": "3V3_SB", "GND": "GND", "INT1": "IOB_INT_N"})
dec("3V3_SB", ["100nF"])
add("U82", "BL24C64A", "BL24C64A-SFRC IOB ID EEPROM @0x51", {"1": "3V3_SB", "2": "GND", "3": "GND", "4": "GND", "8": "3V3_SB", "7": "IOB_EE_WP", "6": "I2C_SYS_SCL", "5": "I2C_SYS_SDA"})
res("IOB_EE_WP", "3V3_SB", "10k (write-protect by default)"); res("IOB_EE_WP", "GND", "DNP 0R (program)", dnp=True)
dec("3V3_SB", ["100nF"])
add("U83", "TCA9517", "TCA9517DGKR I2C buffer: I2C_SYS (3V3_SB) <-> PD controllers (3V3, S0 only)", {"SCLA": "I2C_SYS_SCL", "SDAA": "I2C_SYS_SDA", "VCCA": "3V3_SB",
    "GND": "GND", "SCLB": "I2C_PD_SCL", "SDAB": "I2C_PD_SDA", "VCCB": "3V3", "EN": "PG_3V3"})
res("I2C_PD_SCL", "3V3", "4.7k"); res("I2C_PD_SDA", "3V3", "4.7k"); dec("3V3_SB", ["100nF"]); dec("3V3", ["100nF"])
add("U84", "74LVC1G07", "74LVC1G07 PD_INT_N -> IOB_INT_N (Ioff, safe when 3V3 is off)", {"A": "PD_INT_N", "GND": "GND", "Y(OD)": "IOB_INT_N", "VCC": "3V3"})
res("IOB_INT_N", "3V3_SB", "10k (DNP if the BP pulls up)", dnp=True)
# --- RTC coin cell ---
section("RTC coin cell BT1 -> R30 -> D30 -> VBAT_RTC (HS1 A26)")
add("BT1", "BATT", "CR2032/BR2032 holder Keystone 3034 (stock spot)", {"1": "BT1_POS", "2": "GND"})
add("R30", "R", "1k VBAT series (UL limit)", {"1": "BT1_POS", "2": "VBAT_D"})
add("D30", "D", "BAT54WS (no charge into the cell)", {"2": "VBAT_D", "1": "VBAT_RTC"})
cap("VBAT_RTC", "GND", "100nF (CB keeps 1uF + 0.1uF + diode-OR with 3V3_DSW)")
add("H13", "MECH1", "I/O-frame centre standoff M2 (stock TB-bar point), height M-IOF2", {"1": "GND"}, fp=FPL + ":MP62_Frame_Standoff_M2_SMT_PLACEHOLDER")
for h in ("HTL", "HTR", "HML", "HMR", "HBL", "HBR"):
    add(h, "MECH1", "Stock mount hole " + h[1:] + " (6 stock bosses)", {"1": "GND"})

# --- Power tree ---
section("Power: +12V_MAIN -> TPS259824 eFuse -> 5V_C / 5V_A bucks -> 3V3")
add("U40", "TPS259824ON", "TPS259824ONRGER eFuse 12 V (ILIM ~10 A)", {"1": "+12V_MAIN", "2": "EFUSE_EN", "3": "EFUSE_ILIM", "4": "EFUSE_DVDT", "5": "GND",
    "6": "+12V_IOB", "7": "EFUSE_PG", "8": "EFUSE_FLT#", "9": "EFUSE_IMON", "10": "GND"})
res("+12V_MAIN", "EFUSE_EN", "UVLO top (~10.5 V on)"); res("EFUSE_EN", "GND", "UVLO bottom")
res("EFUSE_ILIM", "GND", "ILIM ~10 A (value per datasheet)"); cap("EFUSE_DVDT", "GND", "dVdt (inrush <= 2 A, value per datasheet)")
res("EFUSE_IMON", "GND", "IMON (value per datasheet)"); res("EFUSE_PG", "3V3_SB", "10k"); res("EFUSE_FLT#", "3V3_SB", "10k")
res("EFUSE_FLT#", "IOB_INT_N", "0R (fault -> IOB_INT_N, OD)")
for ref, out, L, en, pg in (("U41", "5V_C", "L41", "EFUSE_PG", "PG_5VC"), ("U42", "5V_A", "L42", "EFUSE_PG", "PG_5VA")):
    t = out[-1]
    add(ref, "TPS56C215", "TPS56C215RNNR %s buck 12 A" % out, {"1": "+12V_IOB", "2": en, "3": "BK%s_MODE" % t, "4": "BK%s_SS" % t, "5": "GND", "6": "GND",
        "7": "BK%s_SW" % t, "8": "BK%s_BOOT" % t, "9": "BK%s_VREG5" % t, "10": "BK%s_FB" % t, "11": pg})
    add(L, "L", "1.5uH >=15 A Isat 10x10 (%s)" % out, {"1": "BK%s_SW" % t, "2": out})
    cap("BK%s_BOOT" % t, "BK%s_SW" % t, "100nF BOOT"); cap("BK%s_VREG5" % t, "GND", "4.7uF VREG5"); cap("BK%s_SS" % t, "GND", "SS (value per datasheet)")
    res("BK%s_MODE" % t, "GND", "MODE strap (FCCM, 800 kHz)"); res(out, "BK%s_FB" % t, "FB top (5.10 V)"); res("BK%s_FB" % t, "GND", "FB bottom")
    res(pg, "3V3_SB", "10k PG pull-up")
for i in range(4): add("C%d" % (50 + i), "C", "22uF 25V 1206 buck input", {"1": "+12V_IOB", "2": "GND"}, fp=FPL + ":C_1206_3216Metric")
for i in range(8):
    add("C%d" % (40 + i), "C", "47uF 10V 1206 output bulk (%s)" % ("5V_C" if i < 4 else "5V_A"), {"1": "5V_C" if i < 4 else "5V_A", "2": "GND"}, fp=FPL + ":C_1206_3216Metric")
add("U43", "TLV62585", "TLV62585DRL 3V3 3 A from 5V_A", {"1": "5V_A", "2": "PG_5VA", "3": "GND", "4": "BK3_SW", "5": "BK3_FB", "6": "PG_3V3"})
add("L43", "L", "0.47uH 2520 (3V3)", {"1": "BK3_SW", "2": "3V3"}, fp=FPL + ":L_1008_2520Metric")
res("3V3", "BK3_FB", "FB top (3.3 V)"); res("BK3_FB", "GND", "FB bottom"); res("PG_3V3", "3V3_SB", "10k")
dec("3V3", ["22uF 0805", "22uF 0805"]); dec("5V_A", ["10uF 0805"])
dec("3V3_SB", ["10uF 0402"])

# ---------------- layout + emit ----------------
COLW_MIN = 60.0; MAXH = 1050.0
x0, y0 = 30.0, 40.0
cx, cy, colw = x0, y0, 0.0
pos = {}; titles = []
last_sec = None
for it in inst:
    s = SYMS[it["sym"]]; w, h, geo = pin_geom(s)
    need = h + 12 + (10 if it["sec"] != last_sec else 0)
    if cy + need > MAXH or (it["sec"] != last_sec and it["sym"] in ("MCIO124_IOB_HS1",)):
        if cy > y0: cx += colw; cy = y0; colw = 0.0
    if it["sec"] != last_sec:
        titles.append((it["sec"], cx, cy)); cy += 10; last_sec = it["sec"]
    W = w + 2 * 2.54 + 2 * 34
    colw = max(colw, W, COLW_MIN)
    X = cx + W / 2; Y = cy + h / 2 + 4
    pos[it["ref"]] = (round(X / 2.54) * 2.54, round(Y / 2.54) * 2.54)
    cy += h + 12
PW = int(cx + colw + 30); PH = int(MAXH + 60)
def esc(s): return s.replace('"', "'")
out = [f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{ROOT}") (paper "User" {PW} {PH})',
       '  (title_block (title "MP62 I/O board IOB rev A0 (6 x USB-C DP alt, 4 x USB-A 10G, HDMI, 2.5GbE, stock audio/PSU/speaker)") (date "2026-10-01") (rev "A0")'
       ' (company "MacPro6,2 / Aidan Winkler") (comment 1 "Flat sheet, label connectivity. LOGICAL pins on IC placeholders - map from datasheets before routing")'
       ' (comment 2 "Stock PSU / audio header pin functions are PROVISIONAL - probe per plan section 9") (comment 3 "Small passives are not yet placed on the PCB floorplan"))',
       '  (lib_symbols']
for n, s in SYMS.items():
    out.append(sym_text(f"{LIBN}:{n}", s).replace(f'(symbol "{LIBN}:{n}_0_1"', f'(symbol "{n}_0_1"').replace(f'(symbol "{LIBN}:{n}_1_1"', f'(symbol "{n}_1_1"'))
out.append('  )')
for t, x, y in titles:
    out.append(f'  (text "{esc(t)}" (exclude_from_sim no) (at {x + 2:.2f} {y + 4:.2f} 0) (effects (font (size 2.5 2.5) (bold yes)) (justify left bottom)) (uuid "{U()}"))')
nl = nnc = 0
refs = set()
for it in inst:
    ref = it["ref"]; assert ref not in refs, ref; refs.add(ref)
    s = SYMS[it["sym"]]; w, h, geo = pin_geom(s); X, Y = pos[ref]; dnp = it["dnp"]
    fpv = it["fp"] or s["fp"]
    out.append(f'  (symbol (lib_id "{LIBN}:{it["sym"]}") (at {X:.3f} {Y:.3f} 0) (unit 1) (exclude_from_sim no) (in_bom {"no" if dnp else "yes"}) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{U()}")')
    out.append(f'    (property "Reference" "{ref}" (at {X} {Y - h / 2 - 1.5:.2f} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Value" "{esc(it["value"])}" (at {X} {Y + h / 2 + 1.5:.2f} 0) (effects (font (size 1.0 1.0))))')
    out.append(f'    (property "Footprint" "{fpv}" (at {X} {Y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    out.append(f'    (property "Datasheet" "" (at {X} {Y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    for num in geo: out.append(f'    (pin "{num}" (uuid "{U()}"))')
    out.append(f'    (instances (project "{NAME}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
    for num, (px, py, a, nm) in geo.items():
        x, y = round(X + px, 3), round(Y - py, 3)
        if num in it["nets"]:
            ang, just = (180, "right bottom") if a == 0 else (0, "left bottom")
            out.append(f'  (label "{esc(it["nets"][num])}" (at {x} {y} {ang}) (effects (font (size 1.0 1.0)) (justify {just})) (uuid "{U()}"))'); nl += 1
        else:
            out.append(f'  (no_connect (at {x} {y}) (uuid "{U()}"))'); nnc += 1
out.append('  (sheet_instances (path "/" (page "1")))\n)')
open(os.path.join(PRJ, NAME + ".kicad_sch"), "w").write("\n".join(out) + "\n")
open(os.path.join(PRJ, "sym-lib-table"), "w").write('(sym_lib_table\n  (version 7)\n  (lib (name "MP62_IO")(type "KiCad")(uri "${KIPRJMOD}/MP62_IO.kicad_sym")(options "")(descr "MP62 I/O board symbols"))\n)\n')
# net summary for the plan
nets = {}
for it in inst:
    for num, n in it["nets"].items(): nets.setdefault(n, []).append(it["ref"] + "." + num)
single = sorted(n for n, v in nets.items() if len(v) == 1)
open(os.path.join(PRJ, "docs", "sch_netlist_summary.txt"), "w").write(
    "\n".join("%s: %s" % (n, " ".join(v)) for n, v in sorted(nets.items())) + "\n\nSINGLE-PIN NETS (intentional stubs / to other boards):\n" + "\n".join(single) + "\n")
print("symbols", len(SYMS), "instances", len(inst), "labels", nl, "no_connect", nnc, "nets", len(nets), "single-pin", len(single), "paper", PW, PH)
print("single:", single)
