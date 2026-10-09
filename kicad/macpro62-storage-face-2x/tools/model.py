"""MP62 Face S 2-drive switchless storage module (S2X) rev A0 - single-source netlist + placement model.
Used by build_sch.py (schematic) and build_pcb.py (PCB). Module frame (mm): origin bottom-left, +X right, +Y up, viewed from the CORE side.
All parts are on B (outer side, single-sided assembly). Every part: ref, symbol, value, nets {pin: net}, footprint, LCSC, JLC class, placement."""
import csv
LIBN = "MP62_S2X"
SYMS = {}
def sym(name, pins, ref, fp, desc, w=None):
    SYMS[name] = dict(pins=pins, ref=ref, fp=fp, desc=desc, w=w)
L, R = "L", "R"
CSV = "/workspace/macpro62-face/pinouts/mp62-face-v0.1_mcio124_pcie_module-end.csv"
J1SIG = {r["contact"]: r["signal"] for r in csv.DictReader(open(CSV))}
sym("MCIO124_FACE", [("A%d" % i, J1SIG.get("A%d" % i, "NC"), L) for i in range(1, 63)] + [("B%d" % i, J1SIG.get("B%d" % i, "NC"), R) for i in range(1, 63)] + [("MP", "SHIELD", R)],
    "J", "MP62_MCIO_124P_RA_SFF-TA-1016", "MCIO 124P RA (SFF-TA-1016 Annex A footprint), module-end view: row A = host TX (PET), row B = module TX (PER)", w=24)
sym("GH15_AUX", [("1", "3V3_AUX", L), ("2", "3V3_AUX", L), ("3", "GND", L), ("4", "FACE_PRSNT#", L), ("5", "FACE_PWR_EN", L), ("6", "FACE_PWR_GOOD", L),
    ("7", "GND", L), ("8", "FACE_SMB_CLK", R), ("9", "FACE_SMB_DAT", R), ("10", "FACE_SMB_ALERT#", R), ("11", "THERM_ALERT#", R), ("12", "THERM_TRIP#", R),
    ("13", "USB2_D+", R), ("14", "USB2_D-", R), ("15", "MOD_LED#", R), ("MP", "MP", L)], "J", "JST_GH_SM15B-GHS-TB_1x15-1MP_P1.25mm_Horizontal",
    "Face AUX JST GH 1.25 15P right angle SM15B-GHS-TB")
M2N = {1: "GND", 2: "3V3", 3: "GND", 4: "3V3", 5: "PERn3", 6: "NC", 7: "PERp3", 8: "NC", 9: "GND", 10: "DAS/DSS#", 11: "PETn3", 12: "3V3", 13: "PETp3",
       14: "3V3", 15: "GND", 16: "3V3", 17: "PERn2", 18: "3V3", 19: "PERp2", 20: "NC", 21: "GND", 22: "NC", 23: "PETn2", 24: "NC", 25: "PETp2", 26: "NC",
       27: "GND", 28: "NC", 29: "PERn1", 30: "NC", 31: "PERp1", 32: "NC", 33: "GND", 34: "NC", 35: "PETn1", 36: "NC", 37: "PETp1", 38: "DEVSLP",
       39: "GND", 40: "SMB_CLK", 41: "PERn0", 42: "SMB_DATA", 43: "PERp0", 44: "ALERT#", 45: "GND", 46: "NC", 47: "PETn0", 48: "NC", 49: "PETp0",
       50: "PERST#", 51: "GND", 52: "CLKREQ#", 53: "REFCLKn", 54: "PEWAKE#", 55: "REFCLKp", 56: "MFG_DATA", 57: "GND", 58: "MFG_CLK", 67: "NC",
       68: "SUSCLK", 69: "PEDET", 70: "3V3", 71: "GND", 72: "3V3", 73: "GND", 74: "3V3", 75: "GND", 76: "MH1", 77: "MH2"}
sym("M2_M_KEY", [(str(k), v, L if k % 2 else R) for k, v in sorted(M2N.items())], "J", "M2_M-Key_LOTES_APCI0107-P001A",
    "M.2 Socket 3 key M (PCIe x4), LOTES APCI0107-P001A. Names per PCI-SIG M.2 (PET = host TX / card RX on 47/49 etc., PER = card TX on 41/43 etc.)", w=20)
sym("STANDOFF", [("1", "MNT", L)], "MH", "M2_Standoff_SMTSO2030CTJ_M2_H3.0", "SMT M2 standoff H3.0 for the 2280 card screw")
sym("MOUNT", [("1", "MNT", L)], "H", "MP62_FACE_MountHole_D5.0_Pad9.0", "Face mounting hole D5.0 (plated, GND)")
sym("LUG", [("1", "LUG", L)], "J", "MP62_FACE_BusBarLug_D3.2_Pad8.8", "Bus-bar lug D3.2 / pad 8.8")
sym("R", [("1", "~", L), ("2", "~", R)], "R", "R_0402_1005Metric", "Resistor")
sym("C", [("1", "~", L), ("2", "~", R)], "C", "C_0402_1005Metric", "Capacitor")
sym("L", [("1", "~", L), ("2", "~", R)], "L", "L_Sunlord_SWPA6045S", "Inductor")
sym("LED", [("1", "K", L), ("2", "A", R)], "D", "LED_0603_1608Metric", "LED")
sym("D", [("1", "K", L), ("2", "A", R)], "D", "D_SMA", "Schottky diode")
sym("NMOS", [("1", "G", L), ("2", "S", L), ("3", "D", R)], "Q", "SOT-23", "N-MOSFET 2N7002")
sym("TPS259470", [("1", "EN/UVLO", L), ("2", "OVLO", L), ("3", "AUXOFF", R), ("4", "FLT#", R), ("5", "IN", L), ("6", "OUT", R), ("7", "DVDT", R),
    ("8", "GND", L), ("9", "ILM", R), ("10", "ITIMER", R)], "U", "TI_RPW_VQFN-10_2x2mm_P0.45mm", "TPS259470ARPWR 2.7-23 V 5.5 A eFuse, true reverse blocking, -15 V input")
sym("INA238", [("1", "A1", L), ("2", "A0", L), ("3", "ALERT", R), ("4", "SDA", R), ("5", "SCL", R), ("6", "VS", L), ("7", "GND", L), ("8", "VBUS", R),
    ("9", "IN-", L), ("10", "IN+", L)], "U", "VSSOP-10_3x3mm_P0.5mm", "INA238AIDGSR 85 V 16-bit I2C power monitor (INA228 register-compatible family)")
sym("TPS54331", [("1", "BOOT", L), ("2", "VIN", L), ("3", "EN", L), ("4", "SS", L), ("5", "VSENSE", R), ("6", "COMP", R), ("7", "GND", R), ("8", "PH", R)],
    "U", "SOIC-8_3.9x4.9mm_P1.27mm", "TPS54331DR 3.5-28 V 3 A 570 kHz buck")
sym("TMP1075", [("1", "SDA", L), ("2", "SCL", L), ("3", "ALERT", L), ("4", "GND", L), ("5", "A2", R), ("6", "A1", R), ("7", "A0", R), ("8", "V+", R)],
    "U", "VSSOP-8_3x3mm_P0.65mm", "TMP1075DGKR I2C temperature sensor (LM75 compatible)")
sym("EEPROM", [("1", "E0", L), ("2", "E1", L), ("3", "E2", L), ("4", "VSS", L), ("5", "SDA", R), ("6", "SCL", R), ("7", "WC#", R), ("8", "VCC", R)],
    "U", "SOIC-8_3.9x4.9mm_P1.27mm", "M24C64-RMN6TP 64 kbit I2C EEPROM")

# ---------------- parts catalogue: value, footprint, LCSC, JLC class ----------------
CAT = {"10k": ("10k", "R_0402_1005Metric", "C25744", "basic"), "100k": ("100k", "R_0402_1005Metric", "C25741", "basic"),
       "1k": ("1k", "R_0402_1005Metric", "C11702", "basic"), "4k7": ("4.7k 1%", "R_0402_1005Metric", "C25900", "basic"),
       "1k5": ("1.5k 1%", "R_0402_1005Metric", "C25867", "basic"), "27k": ("27k", "R_0402_1005Metric", "C25771", "pref"),
       "120k": ("120k 1%", "R_0603_1608Metric", "C25808", "basic"), "10k1": ("10k 1%", "R_0402_1005Metric", "C25744", "basic"),
       "2m": ("2mR 1% 2W", "R_2512_6332Metric", "C160926", "ext"),
       "100n": ("100nF 16V", "C_0402_1005Metric", "C1525", "basic"), "100n50": ("100nF 50V", "C_0402_1005Metric", "C307331", "basic"),
       "2n2": ("2.2nF 50V", "C_0402_1005Metric", "C1531", "pref"), "3n3": ("3.3nF 50V", "C_0402_1005Metric", "C26404", "pref"),
       "1n": ("1nF 50V", "C_0402_1005Metric", "C1523", "basic"), "47p": ("47pF 50V", "C_0402_1005Metric", "C1567", "basic"),
       "10n": ("10nF 50V", "C_0402_1005Metric", "C15195", "basic"), "47u": ("47uF 10V X5R", "C_1206_3216Metric", "C96123", "basic"),
       "10u50": ("10uF 50V X5R", "C_1206_3216Metric", "C13585", "basic"), "22u25": ("22uF 25V X5R", "C_1206_3216Metric", "C12891", "basic"),
       "22u0805": ("22uF 25V X5R", "C_0805_2012Metric", "C45783", "basic"),
       "2N7002": ("2N7002", "SOT-23", "C8545", "basic"), "SS34": ("SS34", "D_SMA", "C8678", "basic"), "LEDR": ("red 0603", "LED_0603_1608Metric", "C2286", "basic"),
       "RB751": ("RB751V-40", "D_SOD-323", "C7502691", "pref"), "6u8": ("6.8uH 4.3A SWPA6045S6R8MT", "L_Sunlord_SWPA6045S", "C57254", "ext")}
PARTS = []
def add(ref, s, value, nets, x, y, rot=0.0, fp=None, lcsc="", jlc="", dnp=False, cat=None, side="B"):
    if cat:
        v, f, lc, jt = CAT[cat]; value = value or v; fp = fp or f; lcsc = lcsc or lc; jlc = jlc or jt
    PARTS.append(dict(ref=ref, sym=s, value=value, nets=nets, fp=fp or SYMS[s]["fp"], lcsc=lcsc, jlc=jlc, dnp=dnp, x=x, y=y, rot=rot, side=side))
_n = {"R": 1, "C": 1, "Q": 1, "D": 1}
def nxt(k):
    r = "%s%d" % (k, _n[k]); _n[k] += 1; return r
def R(cat_, a, b, x, y, rot=0.0):
    ref = nxt("R"); add(ref, "R", None, {"1": a, "2": b}, x, y, rot, cat=cat_); return ref
def C(cat_, a, b, x, y, rot=0.0):
    ref = nxt("C"); add(ref, "C", None, {"1": a, "2": b}, x, y, rot, cat=cat_); return ref
def Q(g, s, d, x, y, rot=0.0):
    ref = nxt("Q"); add(ref, "NMOS", None, {"1": g, "2": s, "3": d}, x, y, rot, cat="2N7002"); return ref
def D(cat_, k, a, x, y, rot=0.0, s="D"):
    ref = nxt("D"); add(ref, s, None, {"1": k, "2": a}, x, y, rot, cat=cat_); return ref

# ---------------- geometry ----------------
XS = {"A": 46.0, "B": 70.0}; YS = 55.0        # M.2 socket origins (rot 180, B side): odd row at YS-3.77 faces J1, card toward +Y
Y_STANDOFF = YS + 78.75
J1_X, J1_Y = 47.0, 14.5 + 6.025

# ---------------- J1 MCIO ----------------
def j1net(pin):
    s = J1SIG.get(pin, "NC")
    if s == "GND" or s.startswith("MCIO_PRSNT"): return "GND"
    import re
    m = re.match(r"(PET|PER)([pn])(\d+)$", s)
    if m:
        lane = int(m.group(3))
        if lane >= 8: return None
        sl = "A" if lane < 4 else "B"
        return "PCIE_%s_%s%d_%s" % (sl, "HTX" if m.group(1) == "PET" else "MTX", lane % 4, "P" if m.group(2) == "p" else "N")
    mp = {"REFCLK0+": "REFCLK_A_P", "REFCLK0-": "REFCLK_A_N", "REFCLK1+": "REFCLK_B_P", "REFCLK1-": "REFCLK_B_N",
          "CLKREQ0#": "CLKREQ_A_N", "CLKREQ1#": "CLKREQ_B_N", "WAKE0#": "WAKE_A_N", "WAKE1#": "WAKE_B_N",
          "PERST0#": "PERST_A_HOST_N", "PERST1#": "PERST_B_HOST_N"}
    return mp.get(s)
j1n = {p: j1net(p) for p, _, _ in SYMS["MCIO124_FACE"]["pins"] if p != "MP"}
j1n = {k: v for k, v in j1n.items() if v}; j1n["MP"] = "GND"
add("J1", "MCIO124_FACE", "MCIO 124P RA G97R24332HR (J_PCIE, lanes 0-7: x4 slot A + x4 slot B)", j1n, J1_X, J1_Y, 180, lcsc="C4867471", jlc="ext (consign: 0 stock)")
add("J3", "GH15_AUX", "SM15B-GHS-TB GH15 RA (J_AUX)", {"1": "3V3_AUX", "2": "3V3_AUX", "3": "GND", "4": "GND", "5": "FACE_PWR_EN", "6": "FACE_PWR_GOOD",
    "7": "GND", "8": "FACE_SMB_CLK", "9": "FACE_SMB_DAT", "10": "FACE_SMB_ALERT_N", "11": "THERM_ALERT_N", "12": "THERM_TRIP_N", "15": "MOD_LED_N", "MP": "GND"},
    16.5, 26.5, 90, lcsc="C265027", jlc="ext")
for i, (x, y) in enumerate([(15.0, 44.5), (89.0, 44.5), (15.0, 94.5), (89.0, 94.5)]):
    add("H%d" % (i + 1), "MOUNT", "MOUNT D5.0", {"1": "GND"}, x, y, 0, side="F")
for ref, (x, y), n, site in (("J20", (97.26, 147.44), "+12V_IN", "A"), ("J21", (97.06, 159.13), "GND", "A"), ("J22", (6.74, 147.44), "+12V_IN", "B"), ("J23", (6.94, 159.13), "GND", "B")):
    add(ref, "LUG", "BUSBAR LUG site %s %s" % (site, n), {"1": n}, x, y, 0, side="F")

# ---------------- M.2 slots ----------------
def m2nets(sl):
    n = {}
    for k, v in M2N.items():
        if v == "GND" or v.startswith("MH"): n[str(k)] = "GND"
        elif v == "3V3": n[str(k)] = "3V3_" + sl
    for lane, (tn, tp, rn, rp) in enumerate([(47, 49, 41, 43), (35, 37, 29, 31), (23, 25, 17, 19), (11, 13, 5, 7)]):
        # Lane polarity inversion (PCIe receivers must support it): the MCIO and M.2 pinouts face each other mirrored, so every data pair is
        # wired P->n / N->p. REFCLK keeps its polarity (crossed via pair in the router).
        n[str(tn)] = "PCIE_%s_HTX%d_P" % (sl, lane); n[str(tp)] = "PCIE_%s_HTX%d_N" % (sl, lane)
        n[str(rn)] = "PCIE_%s_MTX%d_P" % (sl, lane); n[str(rp)] = "PCIE_%s_MTX%d_N" % (sl, lane)
    n.update({"53": "REFCLK_%s_N" % sl, "55": "REFCLK_%s_P" % sl, "50": "PERST_%s_N" % sl, "52": "CLKREQ_%s_N" % sl, "54": "WAKE_%s_N" % sl, "10": "DAS_%s_N" % sl})
    return n
for i, sl in enumerate("AB"):
    add("J%d" % (5 + i), "M2_M_KEY", "M.2 M-key slot %s (LOTES APCI0107-P001A)" % sl, m2nets(sl), XS[sl], YS, 180, lcsc="C841661", jlc="ext")
    add("MH%d" % (1 + i), "STANDOFF", "SMTSO2030CTJ M2 standoff (2280)", {"1": "GND"}, XS[sl], Y_STANDOFF, 0, lcsc="C2915627", jlc="ext")

# ---------------- 12 V entry: eFuse + monitor (top band) ----------------
add("U1", "TPS259470", "TPS259470ARPWR", {"1": "FACE_PWR_EN", "2": "EF_OVLO", "4": "FACE_SMB_ALERT_N", "5": "+12V_IN", "6": "+12V_SW", "7": "EF_DVDT",
    "8": "GND", "9": "EF_ILM", "10": "EF_ITIMER"}, 46.0, 150.0, 0, lcsc="C3662799", jlc="ext")
R("100k", "FACE_PWR_EN", "GND", 42.5, 152.5, 90)        # EN pull-down (face off unless the BP enables it)
R("120k", "+12V_IN", "EF_OVLO", 42.5, 148.0, 90)        # OVLO 120k/10k: 1.20 V * 13 = 15.6 V
R("10k1", "EF_OVLO", "GND", 41.0, 148.0, 90)
R("1k", "EF_ILM", "GND", 49.5, 152.0, 90)               # ILIM ~ 3.3 A
C("3n3", "EF_DVDT", "GND", 49.5, 148.0, 90)
C("2n2", "EF_ITIMER", "GND", 51.0, 152.0, 90)
C("22u25", "+12V_IN", "GND", 38.0, 150.0, 90)
C("100n50", "+12V_IN", "GND", 44.0, 145.5, 0)
add("R%d" % _n["R"], "R", None, {"1": "+12V_SW", "2": "+12V_S"}, 56.0, 150.0, 180, cat="2m"); _n["R"] += 1
C("100n50", "+12V_SW", "GND", 51.5, 145.5, 0)
add("U2", "INA238", "INA238AIDGSR @0x40", {"1": "GND", "2": "GND", "3": "FACE_SMB_ALERT_N", "4": "FACE_SMB_DAT", "5": "FACE_SMB_CLK", "6": "3V3_AUX",
    "7": "GND", "8": "+12V_S", "9": "+12V_S", "10": "+12V_SW"}, 56.0, 143.0, 0, lcsc="C2868250", jlc="ext")
C("100n", "3V3_AUX", "GND", 60.0, 143.0, 90)
C("22u25", "+12V_S", "GND", 63.0, 150.0, 90)
C("22u25", "+12V_S", "GND", 66.5, 150.0, 90)

# ---------------- 3V3 bucks (one per slot) ----------------
def buck(sl, x, y, mir):
    """TPS54331 3.3 V / 3 A. x,y = U centre; mir = +1 puts L / D / Cout toward +X (slot A, left strip), -1 toward -X (slot B, right strip)."""
    s = "_" + sl; u = "U%d" % (3 if sl == "A" else 4)
    add(u, "TPS54331", "TPS54331DR", {"1": "BOOT" + s, "2": "+12V_S", "4": "SS" + s, "5": "FB" + s, "6": "COMP" + s, "7": "GND", "8": "PH" + s},
        x, y, 180 if mir > 0 else 0, lcsc="C9865", jlc="pref")
    C("10u50", "+12V_S", "GND", x - mir * 5.6, y, 90)
    C("100n50", "+12V_S", "GND", x - mir * 5.6, y + 3.4, 0)
    C("100n50", "BOOT" + s, "PH" + s, x + mir * 1.0, y + 4.0, 0)
    C("10n", "SS" + s, "GND", x - mir * 1.5, y + 4.0, 0)
    R("4k7", "3V3_" + sl, "FB" + s, x - mir * 1.5, y - 4.0, 0)
    R("1k5", "FB" + s, "GND", x - mir * 1.5, y - 5.3, 0)
    R("27k", "COMP" + s, "CRC" + s, x - mir * 4.0, y - 4.0, 0)
    C("1n", "CRC" + s, "GND", x - mir * 4.0, y - 5.3, 0)
    C("47p", "COMP" + s, "GND", x - mir * 6.5, y - 4.0, 90)
    lx = x + mir * 8.0
    add("L%d" % (1 if sl == "A" else 2), "L", None, {"1": "PH" + s, "2": "3V3_" + sl}, lx, y, 0, cat="6u8")
    D("SS34", "PH" + s, "GND", x + mir * 5.0, y - 5.6, 0)
    C("47u", "3V3_" + sl, "GND", lx - 2.0, y + 6.0, 90)
    C("47u", "3V3_" + sl, "GND", lx + 2.0, y + 6.0, 90)
buck("A", 15.5, 72.0, 1)
buck("B", 95.5, 72.0, -1)

# ---------------- per slot: socket bulk, PERST# translator, LED, temperature sensors ----------------
for sl in "AB":
    xs = XS[sl]
    C("22u0805", "3V3_" + sl, "GND", xs - 7.0, YS + 8.0, 0)
    C("22u0805", "3V3_" + sl, "GND", xs + 7.0, YS + 8.0, 0)
    C("100n", "3V3_" + sl, "GND", xs + 9.8, YS + 8.0, 90)
px = {"A": 24.0, "B": 79.0}
for sl in "AB":
    x = px[sl]; s = "_" + sl
    Q("PERST_%s_HOST_N" % sl, "GND", "PERST_%s_INV" % sl, x - 2.0, 37.0, 0)
    R("100k", "PERST_%s_HOST_N" % sl, "GND", x - 2.0, 33.5, 0)
    R("10k", "3V3_AUX", "PERST_%s_INV" % sl, x + 2.0, 33.5, 0)
    Q("PERST_%s_INV" % sl, "GND", "PERST_%s_N" % sl, x + 2.0, 37.0, 0)
    R("10k", "3V3_" + sl, "PERST_%s_N" % sl, x + 2.0, 40.0, 0)
for sl, (x, y) in (("A", (8.0, 62.0)), ("B", (98.0, 62.0))):
    D("LEDR", "DAS_%s_N" % sl, "LED_%s_A" % sl, x, y, 90, s="LED")
    R("1k", "3V3_" + sl, "LED_%s_A" % sl, x, y + 3.0, 90)
D("RB751", "DAS_A_N", "MOD_LED_N", 24.5, 50.0, 0, s="D")
D("RB751", "DAS_B_N", "MOD_LED_N", 79.0, 49.0, 0, s="D")
add("U6", "TMP1075", "TMP1075DGKR @0x48 (THERM_ALERT#)", {"1": "FACE_SMB_DAT", "2": "FACE_SMB_CLK", "3": "THERM_ALERT_N", "4": "GND", "5": "GND", "6": "GND",
    "7": "GND", "8": "3V3_AUX"}, XS["A"], YS + 10.5, 90, lcsc="C2864807", jlc="ext")
add("U7", "TMP1075", "TMP1075DGKR @0x49 (THERM_TRIP#, 80 C POR default)", {"1": "FACE_SMB_DAT", "2": "FACE_SMB_CLK", "3": "THERM_TRIP_N", "4": "GND",
    "5": "GND", "6": "GND", "7": "3V3_AUX", "8": "3V3_AUX"}, XS["B"], YS + 10.5, 90, lcsc="C2864807", jlc="ext")
C("100n", "3V3_AUX", "GND", XS["A"] + 3.5, YS + 10.5, 90)
C("100n", "3V3_AUX", "GND", XS["B"] + 3.5, YS + 10.5, 90)
add("U8", "EEPROM", "M24C64-RMN6TP @0x50 (FRU / ID)", {"1": "GND", "2": "GND", "3": "GND", "4": "GND", "5": "FACE_SMB_DAT", "6": "FACE_SMB_CLK", "7": "GND",
    "8": "3V3_AUX"}, 28.0, 150.0, 0, lcsc="C79988", jlc="pref")
C("100n", "3V3_AUX", "GND", 28.0, 145.5, 0)
# ---------------- FACE_PWR_GOOD = 3V3_A good AND 3V3_B good (open drain) ----------------
Q("PG_G", "GND", "FACE_PWR_GOOD", 15.0, 57.0, 0)
Q("3V3_A", "PG_M", "PG_G", 19.0, 57.0, 0)
Q("3V3_B", "GND", "PG_M", 85.0, 58.5, 0)
R("100k", "3V3_AUX", "PG_G", 17.0, 60.0, 0)

def nets():
    s = set()
    for p in PARTS: s.update(v for v in p["nets"].values() if v)
    return sorted(s)
if __name__ == "__main__":
    import collections
    print(len(PARTS), "parts", len(nets()), "nets")
    cnt = collections.Counter(v for p in PARTS for v in p["nets"].values())
    print([n for n, c in cnt.items() if c < 2])
