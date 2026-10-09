import os, json
"""MP62 backplane rev A1 ("BP-G4" cost-down) - single source netlist + placement model.
Used by build_bp_sch.py (schematic) and build_bp.py (PCB). Disc coordinates (+y = core side), mm.
Every part: ref, symbol, value, nets {pin: net}, footprint, LCSC code, JLC type, DNP flag, placement (x, y, rot)."""
import bp_pins

SYMS = {}
def sym(name, pins, ref, fp, desc, w=None):
    SYMS[name] = dict(pins=pins, ref=ref, fp=fp, desc=desc, w=w)
L, R = "L", "R"
# ---------------- symbols ----------------
j1sig = bp_pins.j1_signals()
sym("CPULINK_224", [("A%d" % i, j1sig["A%d" % i], L) for i in range(1, 113)] + [("B%d" % i, j1sig["B%d" % i], R) for i in range(1, 113)]
    + [("BL", "BOARDLOCK", R)], "J", "MP62_Placeholders:MP62_CPULINK_MiniCoolEdge_224P_Vertical_SMT_PLACEHOLDER",
    "Amphenol Mini Cool Edge 224P vertical ME1022410103011 (CPU-LINK, MP62 pinout ICD rev 3.1 proposal: FS lanes reversed)", w=40)
mc, mlanes = bp_pins.mcio_bp_end()
def mname(k):
    v = mc.get(k, ("NC",))
    return v[0] + ("%d%s" % (v[1], v[2]) if v[0] in ("PET", "PER") else ("+" if v[-1] == "P" else "-") if v[0] == "REFCLK" else "")
sym("MCIO124_BP", [("A%d" % i, mname("A%d" % i), L) for i in range(1, 63)] + [("B%d" % i, mname("B%d" % i), R) for i in range(1, 63)] + [("MP", "SHIELD", R)],
    "J", "MP62_Placeholders:MP62_MCIO_124P_RA_SFF-TA-1016", "MCIO 124P RA (SFF-TA-1016), BP-end view (rows swapped vs module end): B = host TX, A = host RX", w=24)
GH15 = "Connector_JST:JST_GH_BM15B-GHS-TBT_1x15-1MP_P1.25mm_Vertical"
sym("GH15_AUX", [("1", "3V3_AUX", L), ("2", "3V3_AUX", L), ("3", "GND", L), ("4", "FACE_PRSNT#", L), ("5", "FACE_PWR_EN", L), ("6", "FACE_PWR_GOOD", L),
    ("7", "GND", L), ("8", "FACE_SMB_CLK", R), ("9", "FACE_SMB_DAT", R), ("10", "FACE_SMB_ALERT#", R), ("11", "THERM_ALERT#", R), ("12", "THERM_TRIP#", R),
    ("13", "USB2_D+", R), ("14", "USB2_D-", R), ("15", "MOD_LED#", R), ("MP", "MP", L)], "J", GH15, "Face AUX GH 1.25 15P vertical BM15B-GHS-TBT")
sym("GH15_IOB", [("1", "3V3_SB", L), ("2", "3V3_SB", L), ("3", "GND", L), ("4", "PWRBTN_IN_N", L), ("5", "HALL_A_N", L), ("6", "HALL_B_N", L), ("7", "GND", L),
    ("8", "I2C_SYS_SCL", R), ("9", "I2C_SYS_SDA", R), ("10", "IOB_INT_N", R), ("11", "IOB_PRSNT_N", R), ("12", "GND", R), ("13", "USB2_LINK_D+", R),
    ("14", "USB2_LINK_D-", R), ("15", "GND", R), ("MP", "MP", L)], "J", GH15, "IOB-LINK GH 1.25 15P vertical BM15B-GHS-TBT")
sym("MICROFIT8", [("1", "12V_MAIN", L), ("2", "12V_MAIN", L), ("3", "GND", L), ("4", "GND", L), ("5", "GND", R), ("6", "PS_ON#", R), ("7", "11V_SB", R), ("8", "PWR_OK", R)],
    "J", "Connector_Molex:Molex_Micro-Fit_3.0_43045-0812_2x04_P3.00mm_Vertical", "Molex Micro-Fit 3.0 2x4 vertical 43045-0812 (PSU-IN)")
M2P = {1: "GND", 2: "3V3", 3: "GND", 4: "3V3", 9: "GND", 12: "3V3", 14: "3V3", 15: "GND", 16: "3V3", 18: "3V3", 21: "GND", 27: "GND", 33: "GND",
       38: "DEVSLP", 39: "GND", 41: "SATA-B+(HRX+)", 43: "SATA-B-(HRX-)", 45: "GND", 47: "SATA-A-(HTX-)", 49: "SATA-A+(HTX+)", 51: "GND", 57: "GND",
       69: "PEDET", 70: "3V3", 71: "GND", 72: "3V3", 73: "GND", 74: "3V3"}
m2pads = [str(i) for i in list(range(1, 59)) + list(range(67, 76))]
sym("M2_M_SATA", [(p, M2P.get(int(p), "NC%s" % p), L if int(p) % 2 else R) for p in m2pads] + [("MP", "MP", R)], "J",
    "MP62_BP:MP62_M2_MKey_SMT_H4.2_PLACEHOLDER", "M.2 Socket 3 M-key (SATA use only, host view: 47/49 = host TX, 41/43 = host RX)", w=20)
QFN80 = "Package_DFN_QFN:QFN-80-1EP_10x10mm_P0.4mm_EP3.4x3.4mm"
RP = {1: "GPIO4", 2: "GPIO5", 3: "GPIO6", 4: "GPIO7", 5: "IOVDD", 6: "GPIO8", 7: "GPIO9", 8: "GPIO10", 9: "GPIO11", 10: "DVDD", 11: "GPIO12",
      12: "GPIO13", 13: "GPIO14", 14: "GPIO15", 15: "IOVDD", 16: "GPIO16", 17: "GPIO17", 18: "GPIO18", 19: "GPIO19", 20: "GPIO20", 21: "GPIO21",
      22: "GPIO22", 23: "GPIO23", 24: "IOVDD", 25: "GPIO24", 26: "GPIO25", 27: "GPIO26", 28: "GPIO27", 29: "IOVDD", 30: "XIN", 31: "XOUT",
      32: "DVDD", 33: "SWCLK", 34: "SWDIO", 35: "RUN", 36: "GPIO28", 37: "GPIO29", 38: "GPIO30", 39: "GPIO31", 40: "GPIO32", 41: "IOVDD",
      42: "GPIO33", 43: "GPIO34", 44: "GPIO35", 45: "GPIO36", 46: "GPIO37", 47: "GPIO38", 48: "GPIO39", 49: "GPIO40_ADC0", 50: "IOVDD",
      51: "DVDD", 52: "GPIO41", 53: "GPIO42", 54: "GPIO43", 55: "GPIO44", 56: "GPIO45", 57: "GPIO46", 58: "GPIO47", 59: "ADC_AVDD",
      60: "IOVDD", 61: "VREG_AVDD", 62: "VREG_PGND", 63: "VREG_LX", 64: "VREG_VIN", 65: "VREG_FB", 66: "USB_DM", 67: "USB_DP",
      68: "USB_OTP_VDD", 69: "QSPI_IOVDD", 70: "QSPI_SD3", 71: "QSPI_SCLK", 72: "QSPI_SD0", 73: "QSPI_SD2", 74: "QSPI_SD1", 75: "QSPI_SS",
      76: "IOVDD", 77: "GPIO0", 78: "GPIO1", 79: "GPIO2", 80: "GPIO3", 81: "GND_EP"}
sym("RP2350B", [(str(k), v, L if k <= 40 or k == 81 else R) for k, v in RP.items()], "U", QFN80,
    "Raspberry Pi RP2350B QFN-80 (LCSC C42415655), pinout from the RP2350 datasheet", w=22)
sym("W25Q_SOIC8", [("1", "CS#", L), ("2", "DO(IO1)", L), ("3", "WP#(IO2)", L), ("4", "GND", L), ("8", "VCC", R), ("7", "HOLD#(IO3)", R), ("6", "CLK", R), ("5", "DI(IO0)", R)],
    "U", "Package_SO:SOIC-8_5.3x5.3mm_P1.27mm", "Winbond W25Q128JVSIQ 128 Mbit QSPI flash, SOIC-8 208 mil (LCSC C97521, JLC basic)", w=12)
sym("TPS563201", [("3", "VIN", L), ("5", "EN", L), ("1", "GND", L), ("2", "SW", R), ("6", "VBST", R), ("4", "VFB", R)], "U", "Package_TO_SOT_SMD:SOT-23-6",
    "TI TPS563201DDCR 3 A sync buck 4.5-17 V, SOT-23-6 (LCSC C116592)", w=10)
sym("INA226", [("10", "IN+", L), ("9", "IN-", L), ("8", "VBUS", L), ("6", "VS", L), ("7", "GND", L), ("5", "SCL", R), ("4", "SDA", R), ("3", "ALERT", R), ("2", "A0", R), ("1", "A1", R)],
    "U", "Package_SO:VSSOP-10_3x3mm_P0.5mm", "TI INA226AIDGSR power monitor (LCSC C49851; pin-compatible with INA228 DGS)", w=12)
sym("TMP1075_DGK", [("1", "SDA", L), ("2", "SCL", L), ("3", "ALERT", L), ("4", "GND", L), ("8", "V+", R), ("7", "A0", R), ("6", "A1", R), ("5", "A2", R)],
    "U", "Package_SO:VSSOP-8_3x3mm_P0.65mm", "TI TMP1075DGKR temperature sensor, VSSOP-8 (LCSC C2864807)", w=12)
sym("LVC1G74", [("1", "CLK", L), ("2", "D", L), ("7", "PRE#", L), ("6", "CLR#", L), ("4", "GND", L), ("8", "VCC", R), ("5", "Q", R), ("3", "Q#", R)],
    "U", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", "SN74LVC1G74DCUR D flip-flop (thermal-trip latch), VSSOP-8 DCU (LCSC C70285)", w=10)
sym("XTAL4", [("1", "X1", L), ("2", "GND", L), ("3", "X2", R), ("4", "GND", R)], "Y", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "Crystal 3225 4-pin", w=8)
sym("PMOS", [("1", "G", L), ("2", "S", R), ("3", "D", R)], "Q", "Package_TO_SOT_SMD:SOT-23", "P-MOSFET SOT-23 (AO3401A, LCSC C15127 basic)", w=6)
sym("NMOS", [("1", "G", L), ("2", "S", R), ("3", "D", R)], "Q", "Package_TO_SOT_SMD:SOT-23", "N-MOSFET SOT-23 (2N7002, LCSC C8545 basic)", w=6)
sym("D_x2_ACom", [("1", "K1", L), ("2", "K2", L), ("3", "A", R)], "D", "Package_TO_SOT_SMD:SOT-23", "Dual Schottky common anode BAT54A", w=6)
sym("D", [("1", "K", L), ("2", "A", R)], "D", "Diode_SMD:D_SMA", "Diode", w=2)
sym("LED", [("1", "K", L), ("2", "A", R)], "D", "LED_SMD:LED_0603_1608Metric", "LED 0603", w=2)
sym("C", [("1", "~", L), ("2", "~", R)], "C", "Capacitor_SMD:C_0402_1005Metric", "Capacitor", w=2)
sym("R", [("1", "~", L), ("2", "~", R)], "R", "Resistor_SMD:R_0402_1005Metric", "Resistor", w=2)
sym("L", [("1", "~", L), ("2", "~", R)], "L", "Inductor_SMD:L_Changjiang_FNR4030S", "Inductor", w=2)
sym("F", [("1", "~", L), ("2", "~", R)], "F", "Fuse:Fuse_1206_3216Metric", "Fuse", w=2)
sym("SW", [("1", "1", L), ("2", "2", R)], "SW", "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", "Tact switch TS-1187A (LCSC C318884 basic)", w=4)
sym("JUMPER", [("1", "1", L), ("2", "2", R)], "JP", "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "Solder jumper, open", w=4)
sym("SH3_SWD", [("1", "SWCLK", L), ("2", "GND", L), ("3", "SWDIO", L), ("MP", "MP", R)], "J", "Connector_JST:JST_SH_BM03B-SRSS-TB_1x03-1MP_P1.00mm_Vertical",
    "Raspberry Pi debug connector JST SH 3P", w=8)
sym("HOLE", [("1", "1", L)], "H", "MountingHole:MountingHole_4mm_Pad", "Mounting hole D4 plated", w=4)

# ---------------- BOM catalogue (merged values) ----------------
# key -> (value, footprint, LCSC, JLC type)
CAT = {
    "C100n": ("100nF 16V X7R 0402", "Capacitor_SMD:C_0402_1005Metric", "C1525", "basic"),
    "C1u": ("1uF 25V X5R 0402", "Capacitor_SMD:C_0402_1005Metric", "C52923", "basic"),
    "C4u7": ("4.7uF 10V X5R 0402", "Capacitor_SMD:C_0402_1005Metric", "C23733", "basic"),
    "C22u": ("22uF 25V X5R 0805", "Capacitor_SMD:C_0805_2012Metric", "C45783", "basic"),
    "C15p": ("15pF 50V C0G 0402", "Capacitor_SMD:C_0402_1005Metric", "C1548", "basic"),
    "R10k": ("10k 1% 0402", "Resistor_SMD:R_0402_1005Metric", "C25744", "basic"),
    "R2k2": ("2.2k 1% 0402", "Resistor_SMD:R_0402_1005Metric", "C25879", "basic"),
    "R1k": ("1k 1% 0402", "Resistor_SMD:R_0402_1005Metric", "C11702", "basic"),
    "R100k": ("100k 1% 0402", "Resistor_SMD:R_0402_1005Metric", "C25741", "basic"),
    "R33k": ("33k 1% 0402", "Resistor_SMD:R_0402_1005Metric", "C25779", "basic"),
    "R56k": ("56k 1% 0402", "Resistor_SMD:R_0402_1005Metric", "C25796", "pref"),
    "R33": ("33R 1% 0402", "Resistor_SMD:R_0402_1005Metric", "C25105", "basic"),
    "R27": ("27R 1% 0402", "Resistor_SMD:R_0402_1005Metric", "C25100", "ext"),
    "R10m": ("10mR 1% 1W 1206 shunt", "Resistor_SMD:R_1206_3216Metric", "C105362", "ext"),
    "L4u7": ("4.7uH 2A 4x4 (SWPA4030S4R7MT)", "Inductor_SMD:L_Changjiang_FNR4030S", "C57269", "ext"),
    "L3u3": ("3.3uH 0806 (FNR201610S3R3MT, RP2350 VREG)", "Inductor_SMD:L_0805_2012Metric", "C167673", "ext"),
    "F3A": ("3A 1206 fast fuse (0466003.NRHF class)", "Fuse:Fuse_1206_3216Metric", "C14165", "ext"),
    "SS34": ("SS34 3A 40V Schottky SMA", "Diode_SMD:D_SMA", "C8678", "basic"),
    "TVS15": ("SMAJ15A TVS SMA", "Diode_SMD:D_SMA", "C113958", "ext"),
    "BAT54A": ("BAT54A (LBAT54ALT1G)", "Package_TO_SOT_SMD:SOT-23", "C12743", "ext"),
    "LEDR": ("LED red 0603", "LED_SMD:LED_0603_1608Metric", "C2286", "basic"),
    "AO3401A": ("AO3401A P-MOS", "Package_TO_SOT_SMD:SOT-23", "C15127", "basic"),
    "2N7002": ("2N7002 N-MOS", "Package_TO_SOT_SMD:SOT-23", "C8545", "basic"),
    "TS1187": ("TS-1187A-B-A-B tact", "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", "C318884", "basic"),
    "XTAL12": ("12MHz 3225 crystal 20pF", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "C9002", "basic"),
}
PARTS = []
def add(ref, s, value, nets, x=None, y=None, rot=0.0, fp=None, lcsc="", jlc="", dnp=False, cat=None, side="F"):
    if cat:
        v, f, lc, jt = CAT[cat]; value = value or v; fp = fp or f; lcsc = lcsc or lc; jlc = jlc or jt
    PARTS.append(dict(ref=ref, sym=s, value=value, nets=nets, fp=fp or SYMS[s]["fp"], lcsc=lcsc, jlc=jlc, dnp=dnp, x=x, y=y, rot=rot, side=side))
_n = {"R": 1, "C": 1}
def R(cat_, a, b, x=None, y=None, rot=0.0, dnp=False, note=""):
    ref = "R%d" % _n["R"]; _n["R"] += 1
    add(ref, "R", (CAT[cat_][0] + (" " + note if note else "")), {"1": a, "2": b}, x, y, rot, cat=cat_, dnp=dnp); return ref
def C(cat_, a, b="GND", x=None, y=None, rot=0.0, dnp=False):
    ref = "C%d" % _n["C"]; _n["C"] += 1
    add(ref, "C", CAT[cat_][0], {"1": a, "2": b}, x, y, rot, cat=cat_, dnp=dnp); return ref

# ---------------- J1 CPU-LINK ----------------
def j1net(pin):
    s = j1sig[pin]
    if s in ("GND",): return "GND"
    if s.startswith("RSVD") or s in ("SMB_CLK", "SMB_DAT", "SMB_ALERT#", "GPIO0", "GPIO1", "GPIO2", "GPIO3", "BIOS_SEL", "RSTBTN#", "WAKE0#"):
        return None
    for pre, nm in (("FP_PET", "FP_TX"), ("FP_PER", "FP_RX"), ("FS_PET", "FS_TX"), ("FS_PER", "FS_RX")):
        if s.startswith(pre): return nm + s[len(pre):]           # FP_TX15_P ...
    m = {"CC_PRSNT1#": "CC_PRSNT1_N", "CC_PRSNT2#": "CC_PRSNT2_N", "PWRBTN#": "CB_PWRBTN_N", "SUS_S3#": "CB_SUS_S3_N", "SUS_S4_S5#": "CB_SUS_S45_N",
         "RSMRST_OUT#": "CB_RSMRST_N", "VIN_PWR_OK": "CB_VIN_PWR_OK", "PLTRST#": "CB_PLTRST_N", "THERMTRIP#": "CB_THERMTRIP_N",
         "CARRIER_HOT#": "CB_CARRIER_HOT_N", "PWR_ALERT#": "CB_PWR_ALERT_N", "I2C0_CLK": "CB_I2C0_SCL", "I2C0_DAT": "CB_I2C0_SDA",
         "UART0_TX": "CB_UART0_TX", "UART0_RX": "CB_UART0_RX", "FAN_PWMOUT": "CB_FAN_PWM", "FAN_TACHIN": "CB_FAN_TACH", "5V_SBY": "5V_SBY", "3V3_SB": "3V3_SB"}
    if s in m: return m[s]
    return s.replace("#", "_N")   # FP_REFCLK_P, SATA0_TX_P, USB2_*_P ...
add("J1", "CPULINK_224", "ME1022410103011 Mini Cool Edge 224 (C4941560, 0 stock: pre-order)", {p: j1net(p) for p in j1sig if j1net(p)} | {"BL": "GND"},
    0.0, -12.6, 180.0, lcsc="C4941560", jlc="ext/pre-order")
# ---------------- J9 / J10 MCIO ----------------
def mcio_nets(face, nl):
    d = {}
    for k, v in mc.items():
        if v[0] in ("PET", "PER"):
            if v[1] < nl: d[k] = "%s_%s%d_%s" % (face, "TX" if v[0] == "PET" else "RX", v[1], v[2])
        elif v[0] == "GND": d[k] = "GND"
        elif v[0] == "REFCLK": d[k] = "%s_REFCLK_%s" % (face, v[1])
        elif v[0] == "PERST": d[k] = "%s_PERST_N" % face
        elif v[0] == "PRSNT": d[k] = "%s_MCIO_PRSNT_N" % face
    d["MP"] = "GND"
    return d
add("J9", "MCIO124_BP", "MCIO 124P RA G97R24332HR class (C4867471, 0 stock: pre-order) -> Face P x16", mcio_nets("FP", 16), lcsc="C4867471", jlc="ext/pre-order")
add("J10", "MCIO124_BP", "MCIO 124P RA (C4867471) -> Face S x4", mcio_nets("FS", 4), lcsc="C4867471", jlc="ext/pre-order")
# ---------------- face AUX ----------------
for J, F in (("J3", "FP"), ("J4", "FS")):
    usb = "USB2_FACEP" if F == "FP" else "USB2_FACES"
    add(J, "GH15_AUX", "BM15B-GHS-TBT (C5305069) Face %s AUX" % F[1], {"1": "3V3_AUX_" + F[1], "2": "3V3_AUX_" + F[1], "3": "GND", "4": F + "_PRSNT_N", "5": F + "_PWR_EN",
        "6": F + "_PWR_GOOD", "7": "GND", "8": F + "_SMB_SCL", "9": F + "_SMB_SDA", "10": F + "_SMB_ALERT_N", "11": F + "_THERM_ALERT_N", "12": F + "_THERM_TRIP_N",
        "13": usb + "_P", "14": usb + "_N", "15": F + "_MOD_LED_N", "MP": "GND"}, lcsc="C5305069", jlc="ext")
add("J6", "GH15_IOB", "BM15B-GHS-TBT (C5305069) IOB-LINK", {"1": "3V3_SB", "2": "3V3_SB", "3": "GND", "4": "PWRBTN_IN_N", "5": "HALL_A_N", "6": "HALL_B_N", "7": "GND",
    "8": "I2C_SYS_SCL", "9": "I2C_SYS_SDA", "10": "SYS_INT_N", "11": "IOB_PRSNT_N", "12": "GND", "13": "USB2_SPARE_P", "14": "USB2_SPARE_N", "15": "GND", "MP": "GND"},
    lcsc="C5305069", jlc="ext")
add("J2", "MICROFIT8", "Molex 43045-0812 Micro-Fit 2x4 (C277661)", {"1": "12V_MAIN_IN", "2": "12V_MAIN_IN", "3": "GND", "4": "GND", "5": "GND", "6": "PSU_PS_ON_N",
    "7": "11V_SB_IN", "8": "PSU_PWR_OK"}, lcsc="C277661", jlc="ext (THT)")
add("H1", "HOLE", "MountingHole D4 plated (GND)", {"1": "GND"}, fp="MountingHole:MountingHole_4mm_Pad")
add("H2", "HOLE", "MountingHole D4 plated (GND)", {"1": "GND"}, fp="MountingHole:MountingHole_4mm_Pad")
# ---------------- power ----------------
add("D1", "D", "", {"1": "VIN_OR", "2": "12V_MAIN_IN"}, cat="SS34")
add("D2", "D", "", {"1": "VIN_OR", "2": "11V_SB_IN"}, cat="SS34")
add("F1", "F", "", {"1": "VIN_OR", "2": "VIN_F"}, cat="F3A")
add("D3", "D", "", {"1": "VIN_F", "2": "GND"}, cat="TVS15")
add("R100", "R", "", {"1": "VIN_F", "2": "VIN"}, cat="R10m")
add("U5", "INA226", "INA226AIDGSR @0x40 (C49851)", {"10": "VIN_F", "9": "VIN", "8": "VIN", "6": "3V3_SB", "7": "GND", "5": "I2C_SYS_SCL", "4": "I2C_SYS_SDA",
    "3": "SYS_INT_N", "2": "GND", "1": "GND"}, lcsc="C49851", jlc="ext")
C("C100n", "3V3_SB")
for i in range(3): C("C22u", "VIN")
for U, out, rtop, en in (("U6", "3V3_SB", "R33k", "EN_3V3"), ("U7", "5V_SBY", "R56k", "EN_5V")):
    sw, bst, fb = "SW_" + out, "BST_" + out, "FB_" + out
    add(U, "TPS563201", "TPS563201DDCR (C116592) -> " + out, {"3": "VIN", "5": en, "1": "GND", "2": sw, "6": bst, "4": fb}, lcsc="C116592", jlc="ext")
    add("L%d" % (1 if U == "U6" else 2), "L", "", {"1": sw, "2": out}, cat="L4u7")
    C("C100n", bst, sw)
    R(rtop, out, fb); R("R10k", fb, "GND")
    for i in range(2): C("C22u", out)
    C("C100n", "VIN")
R("R100k", "EN_3V3", "VIN", note="(U6 EN, always on)")
R("R100k", "EN_5V", "GND", note="(U7 off until the MCU enables 5V_SBY)")
# face AUX + M.2 load switches
for q, F in (("Q1", "P"), ("Q2", "S")):
    add(q, "PMOS", "", {"1": "AUX%s_EN_N" % F, "2": "3V3_SB", "3": "3V3_AUX_" + F}, cat="AO3401A")
    R("R10k", "AUX%s_EN_N" % F, "3V3_SB")
    C("C22u", "3V3_AUX_" + F); C("C100n", "3V3_AUX_" + F)
add("Q3", "PMOS", "", {"1": "M2_EN_N", "2": "3V3_SB", "3": "3V3_M2"}, cat="AO3401A", dnp=True)
add("Q4", "NMOS", "", {"1": "CB_SUS_S3_N", "2": "GND", "3": "M2_EN_N"}, cat="2N7002", dnp=True)
R("R10k", "M2_EN_N", "3V3_SB", dnp=True)
C("C22u", "3V3_M2", dnp=True); C("C100n", "3V3_M2", dnp=True)
R("R10k", "M2_DEVSLP", "GND", dnp=True)
add("J7", "M2_M_SATA", "M.2 M-key socket LOTES APCI0107 class (C841661) - DNP option (OpenCore boot SSD, SATA0)",
    {str(k): ("3V3_M2" if v == "3V3" else "GND" if v == "GND" else None) for k, v in M2P.items()} | {"41": "SATA0_RX_P", "43": "SATA0_RX_N", "47": "SATA0_TX_N",
    "49": "SATA0_TX_P", "38": "M2_DEVSLP", "MP": "GND"}, lcsc="C841661", jlc="ext", dnp=True)
PARTS[-1]["nets"] = {k: v for k, v in PARTS[-1]["nets"].items() if v}
add("H3", "HOLE", "M.2 2242 standoff pad (DNP option)", {"1": "GND"}, fp="MP62_BP:MP62_M2_Standoff_SMT_M2_Pad5.0", dnp=True)
# ---------------- HW safety gate (PS_ON = Hall interlock AND PS_ON_REQ AND NOT THERM_LATCH) ----------------
add("Q5", "PMOS", "", {"1": "HALL_A_N", "2": "3V3_SB", "3": "ILK_A"}, cat="AO3401A")
add("Q6", "PMOS", "", {"1": "HALL_B_N", "2": "3V3_SB", "3": "ILK_A"}, cat="AO3401A")
add("Q7", "PMOS", "", {"1": "PS_ON_REQ_N", "2": "ILK_A", "3": "ILK_B"}, cat="AO3401A")
add("Q8", "PMOS", "", {"1": "THERM_LATCH", "2": "ILK_B", "3": "PSON_DRV"}, cat="AO3401A")
add("Q9", "NMOS", "", {"1": "PSON_DRV", "2": "GND", "3": "PSU_PS_ON_N"}, cat="2N7002")
add("JP1", "JUMPER", "BENCH: bridges the Hall interlock (open = normal)", {"1": "3V3_SB", "2": "ILK_A"})
R("R100k", "ILK_A", "GND"); R("R100k", "PSON_DRV", "GND")
for n in ("HALL_A_N", "HALL_B_N", "PS_ON_REQ_N"): R("R10k", n, "3V3_SB")
add("U8", "LVC1G74", "SN74LVC1G74DCUR thermal latch (C70285)", {"1": "GND", "2": "GND", "7": "TRIP_N", "6": "LATCH_CLR_N", "4": "GND", "8": "3V3_SB", "5": "THERM_LATCH"},
    lcsc="C70285", jlc="ext")
C("C100n", "3V3_SB")
R("R10k", "LATCH_CLR_N", "3V3_SB"); C("C1u", "LATCH_CLR_N")
R("R10k", "TRIP_N", "3V3_SB")
add("D4", "D_x2_ACom", "", {"1": "CB_THERMTRIP_N", "2": "FP_THERM_TRIP_N", "3": "TRIP_N"}, cat="BAT54A")
add("D5", "D_x2_ACom", "", {"1": "FS_THERM_TRIP_N", "2": "BP_OTEMP_N", "3": "TRIP_N"}, cat="BAT54A")
for n in ("CB_THERMTRIP_N", "FP_THERM_TRIP_N", "FS_THERM_TRIP_N", "BP_OTEMP_N"): R("R10k", n, "3V3_SB")
add("U3", "TMP1075_DGK", "TMP1075DGKR @0x48 core side (C2864807)", {"1": "I2C_SYS_SDA", "2": "I2C_SYS_SCL", "3": "BP_OTEMP_N", "4": "GND", "8": "3V3_SB",
    "7": "GND", "6": "GND", "5": "GND"}, lcsc="C2864807", jlc="ext")
C("C100n", "3V3_SB")
add("U4", "TMP1075_DGK", "TMP1075DGKR @0x49 PSU side (C2864807)", {"1": "I2C_SYS_SDA", "2": "I2C_SYS_SCL", "3": "BP_OTEMP_N", "4": "GND", "8": "3V3_SB",
    "7": "3V3_SB", "6": "GND", "5": "GND"}, lcsc="C2864807", jlc="ext")
C("C100n", "3V3_SB")
# PERST#_x = PLTRST# AND NOT FACE_x_HOLD (2N7002 clamps the face's PERST# low until the MCU releases HOLD)
for q, F in (("Q10", "FP"), ("Q11", "FS")):
    R("R1k", "CB_PLTRST_N", F + "_PERST_N")
    add(q, "NMOS", "", {"1": F + "_HOLD", "2": "GND", "3": F + "_PERST_N"}, cat="2N7002")
    R("R10k", F + "_HOLD", "3V3_SB")
    R("R10k", F + "_MCIO_PRSNT_N", "3V3_SB")
    aux = "3V3_AUX_" + F[1]
    R("R10k", F + "_PRSNT_N", "3V3_SB"); R("R10k", F + "_PWR_GOOD", aux)
    R("R2k2", F + "_SMB_SCL", aux); R("R2k2", F + "_SMB_SDA", aux)
    R("R10k", F + "_SMB_ALERT_N", aux); R("R10k", F + "_THERM_ALERT_N", aux)
    add("D%d" % (6 if F == "FP" else 7), "LED", "", {"1": F + "_MOD_LED_N", "2": F + "_LEDA"}, cat="LEDR")
    R("R1k", F + "_LEDA", aux)
# CPU-LINK low-speed terminations
for n in ("CB_PWRBTN_N", "CB_PWR_ALERT_N", "CB_CARRIER_HOT_N", "CC_PRSNT1_N", "CC_PRSNT2_N", "SYS_INT_N", "IOB_PRSNT_N", "PWRBTN_IN_N"): R("R10k", n, "3V3_SB")
for n in ("CB_I2C0_SCL", "CB_I2C0_SDA", "I2C_SYS_SCL", "I2C_SYS_SDA"): R("R2k2", n, "3V3_SB")
R("R1k", "PSU_PWR_OK", "PSU_PWR_OK_M"); R("R100k", "PSU_PWR_OK_M", "GND")
add("SW2", "SW", "BENCH power button (TS-1187A)", {"1": "PWRBTN_IN_N", "2": "GND"}, cat="TS1187")
# LEDs
add("D8", "LED", "", {"1": "LED12_K", "2": "12V_MAIN_IN"}, cat="LEDR"); R("R10k", "LED12_K", "GND", note="(12V LED)")
add("D9", "LED", "", {"1": "LED11_K", "2": "11V_SB_IN"}, cat="LEDR"); R("R10k", "LED11_K", "GND", note="(11V_SB LED)")
add("D10", "LED", "", {"1": "LED_ST_K", "2": "3V3_SB"}, cat="LEDR"); R("R1k", "LED_ST_K", "MCU_LED_N")
# ---------------- MCU ----------------
GP = {0: "CB_UART0_RX", 1: "CB_UART0_TX", 2: "CB_FAN_TACH", 3: "CB_FAN_PWM", 4: "I2C_SYS_SDA", 5: "I2C_SYS_SCL", 6: "CB_I2C0_SDA", 7: "CB_I2C0_SCL",
      8: "CB_PWRBTN_N", 9: "CB_SUS_S3_N", 10: "CB_SUS_S45_N", 11: "CB_RSMRST_N", 12: "CB_VIN_PWR_OK", 13: "CB_PLTRST_N", 14: "CB_CARRIER_HOT_N",
      15: "CB_PWR_ALERT_N", 16: "CC_PRSNT2_N", 37: "PS_ON_REQ_N", 38: "PSU_PWR_OK_M", 39: "PWRBTN_IN_N", 40: "ILK_A", 41: "SYS_INT_N",
      42: "THERM_LATCH", 43: "LATCH_CLR_N", 44: "EN_5V", 45: "MCU_LED_N", 46: "IOB_PRSNT_N", 47: "CC_PRSNT1_N"}
for i, s in enumerate(("PRSNT_N", "PWR_EN", "PWR_GOOD", "SMB_SDA", "SMB_SCL", "SMB_ALERT_N", "THERM_ALERT_N", None, "HOLD", "MCIO_PRSNT_N")):
    GP[17 + i] = "FP_" + s if s else "AUXP_EN_N"
    GP[27 + i] = "FS_" + s if s else "AUXS_EN_N"
# rev A1: GPIOs re-assigned by escape direction (tools/bp_gpio.py -> tools/gpio_map.json)
_GPJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gpio_map.json")
if os.path.exists(_GPJ) and not os.environ.get("BP_GPIO_DEFAULT"):
    _m = {int(k): v for k, v in json.load(open(_GPJ)).items()}
    assert sorted(_m.values()) == sorted(GP.values()), "gpio_map.json net set mismatch"
    GP = _m
u1 = {}
for k, v in RP.items():
    if v.startswith("GPIO"):
        g = int(v[4:].split("_")[0]); u1[str(k)] = GP[g]
    elif v in ("IOVDD", "ADC_AVDD", "USB_OTP_VDD", "QSPI_IOVDD", "VREG_VIN"): u1[str(k)] = "3V3_SB"
    elif v in ("DVDD", "VREG_FB"): u1[str(k)] = "DVDD"
    elif v in ("VREG_PGND", "GND_EP"): u1[str(k)] = "GND"
    elif v == "VREG_AVDD": u1[str(k)] = "VREG_AVDD"
    elif v == "VREG_LX": u1[str(k)] = "VREG_LX"
    elif v in ("XIN", "XOUT"): u1[str(k)] = v
    elif v.startswith("QSPI_"): u1[str(k)] = v
    elif v == "USB_DP": u1[str(k)] = "USB_DP_M"
    elif v == "USB_DM": u1[str(k)] = "USB_DM_M"
    elif v in ("SWCLK", "SWDIO", "RUN"): u1[str(k)] = "MCU_" + v
add("U1", "RP2350B", "RP2350B QFN-80 (C42415655)", u1, lcsc="C42415655", jlc="ext")
for i in range(6): C("C100n", "3V3_SB")
C("C4u7", "3V3_SB")                              # VREG_VIN
add("L3", "L", "", {"1": "VREG_LX", "2": "DVDD"}, cat="L3u3")
C("C4u7", "DVDD"); C("C4u7", "DVDD")
for i in range(3): C("C100n", "DVDD")
R("R33", "3V3_SB", "VREG_AVDD"); C("C100n", "VREG_AVDD")
add("Y1", "XTAL4", "", {"1": "XIN", "3": "XOUT_C", "2": "GND", "4": "GND"}, cat="XTAL12")
R("R1k", "XOUT", "XOUT_C"); C("C15p", "XIN"); C("C15p", "XOUT_C")
add("U2", "W25Q_SOIC8", "W25Q128JVSIQ (C97521, basic)", {"1": "QSPI_SS", "2": "QSPI_SD1", "3": "QSPI_SD2", "4": "GND", "8": "3V3_SB", "7": "QSPI_SD3",
    "6": "QSPI_SCLK", "5": "QSPI_SD0"}, lcsc="C97521", jlc="basic")
C("C100n", "3V3_SB")
R("R1k", "QSPI_SS", "BOOTSEL_N")
add("SW1", "SW", "BOOTSEL (TS-1187A)", {"1": "BOOTSEL_N", "2": "GND"}, cat="TS1187")
R("R33", "USB_DP_M", "USB2_MCU_P"); R("R33", "USB_DM_M", "USB2_MCU_N")   # 27R (ext) -> 33R basic: USB FS series R, merged line
add("J8", "SH3_SWD", "BM03B-SRSS-TB SWD (DNP)", {"1": "MCU_SWCLK", "2": "GND", "3": "MCU_SWDIO", "MP": "GND"}, dnp=True, lcsc="C160389", jlc="ext")
C("C100n", "MCU_RUN")

def nets():
    s = set()
    for p in PARTS: s |= set(p["nets"].values())
    return sorted(s)
if __name__ == "__main__":
    print(len(PARTS), "parts,", len(nets()), "nets")
    from collections import Counter
    c = Counter(p["lcsc"] for p in PARTS if not p["dnp"]); print(c.most_common(40))
