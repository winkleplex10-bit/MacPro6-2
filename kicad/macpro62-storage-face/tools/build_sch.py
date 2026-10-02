#!/usr/bin/env python3
"""Generate MP62_Storage.kicad_sym + macpro62-storage-face.kicad_sch (KiCad 9) for the Face S storage module SM-1 rev A0.
Connectivity is by net labels on every pin end (flat single A0 sheet). Real pinouts: M.2 M-key (PCI-SIG M.2 Socket 3),
MCIO 124 module end (from the MP62-FACE CSV), GH15 AUX (CSV), BL24C64A SOIC-8, TMP1075 DSG, 74LVC2G07 DCK, W25Q SOIC-8, LM74700 DBV.
LOGICAL pin numbering (verify vs datasheet before layout): ASM2824 (NDA ball map), TPS259824, TPS56C215, TLV62585."""
import csv, os, uuid
HERE = os.path.dirname(os.path.abspath(__file__)); PRJ = os.path.abspath(os.path.join(HERE, ".."))
NAME = "macpro62-storage-face"; LIBN = "MP62_Storage"
CSVD = "/workspace/macpro62-face/pinouts"
U = lambda: str(uuid.uuid4())
ROOT = U()
SYMS = {}   # name -> dict(pins=[(num,name,side)], w, fp, ref, desc)

def addsym(name, pins, ref, fp, desc, w=None):
    SYMS[name] = dict(pins=pins, ref=ref, fp=fp, desc=desc, w=w)

# ---------- symbol definitions ----------
# MCIO 124 module end
rows = list(csv.DictReader(open(os.path.join(CSVD, "mp62-face-v0.1_mcio124_pcie_module-end.csv"))))
mcio_pins = [(r["contact"], r["signal"], "L" if r["contact"].startswith("A") else "R") for r in rows] + [("MP", "SHIELD/MP", "R")]
addsym("MCIO124_RA_ModuleEnd", mcio_pins, "J", "MP62_Face:MP62_MCIO_124P_RA_SFF-TA-1016", "MCIO 124P RA receptacle, MP62-FACE module-end pinout (host-centric PET/PER names)")
aux = list(csv.DictReader(open(os.path.join(CSVD, "mp62-face-v0.1_aux_gh15.csv"))))
addsym("GH15_AUX", [(r["pin"], r["signal"], "L") for r in aux] + [("MP", "MP", "L")], "J",
       "MP62_Face:JST_GH_SM15B-GHS-TB_1x15-1MP_P1.25mm_Horizontal", "MP62-FACE J_AUX GH 1.25 15P RA (JST SM15B-GHS-TB)")
M2 = {1: "GND", 2: "3V3", 3: "GND", 4: "3V3", 5: "PETn3", 6: "NC6", 7: "PETp3", 8: "NC8", 9: "GND", 10: "DAS/DSS#", 11: "PERn3", 12: "3V3",
      13: "PERp3", 14: "3V3", 15: "GND", 16: "3V3", 17: "PETn2", 18: "3V3", 19: "PETp2", 20: "NC20", 21: "GND", 22: "NC22", 23: "PERn2",
      24: "NC24", 25: "PERp2", 26: "NC26", 27: "GND", 28: "NC28", 29: "PETn1", 30: "NC30", 31: "PETp1", 32: "NC32", 33: "GND", 34: "NC34",
      35: "PERn1", 36: "NC36", 37: "PERp1", 38: "DEVSLP", 39: "GND", 40: "SMB_CLK(1V8)", 41: "PETn0", 42: "SMB_DATA(1V8)", 43: "PETp0",
      44: "ALERT#(1V8)", 45: "GND", 46: "NC46", 47: "PERn0", 48: "NC48", 49: "PERp0", 50: "PERST#", 51: "GND", 52: "CLKREQ#", 53: "REFCLKn",
      54: "PEWAKE#", 55: "REFCLKp", 56: "MFG_DATA", 57: "GND", 58: "MFG_CLK", 67: "NC67", 68: "SUSCLK", 69: "PEDET", 70: "3V3", 71: "GND",
      72: "3V3", 73: "GND", 74: "3V3", 75: "GND"}
m2p = [(str(n), M2[n], "L" if n % 2 else "R") for n in sorted(M2)] + [("MP", "MP", "R")]
addsym("M2_Socket3_MKey", m2p, "J", "MP62_Storage:MP62_M2_MKey_SMT_H4.2_PLACEHOLDER",
       "M.2 Socket 3 M-key (PCIe x4 NVMe) 67P; PET = module TX, PER = module RX (M.2 naming, module view)")
sw = []
k = 0
def P(name, side):
    global k
    k += 1; sw.append(("P%d" % k, name, side))
for l in range(8):
    for pol in "PN": P("UP_RX%d%s" % (l, pol), "L")
for l in range(8):
    for pol in "PN": P("UP_TX%d%s" % (l, pol), "L")
for n in ["REFCLK_IN_P", "REFCLK_IN_N", "PERST#", "XTAL_IN", "XTAL_OUT", "SPI_CS#", "SPI_CLK", "SPI_DO", "SPI_DI", "SMB_CLK", "SMB_DAT",
          "VDD33", "VDD_CORE", "VDDA(TBD)", "GND"]:
    P(n, "L")
for d in range(4):
    for l in range(4):
        for pol in "PN": P("DN%d_TX%d%s" % (d, l, pol), "R")
    for l in range(4):
        for pol in "PN": P("DN%d_RX%d%s" % (d, l, pol), "R")
    for pol in "PN": P("DN%d_REFCLK_%s" % (d, pol), "R")
addsym("ASM2824", sw, "U", "MP62_Storage:MP62_BGA-492_21x21mm_Layout25x25_P0.8mm_PLACEHOLDER",
       "ASMedia ASM2824 PCIe Gen3 24-lane packet switch (x8 up, 4 x x4 down). LOGICAL pins P1..; ball map from ASMedia datasheet (NDA)", w=40)
addsym("TPS259824ON", [("1", "IN", "L"), ("2", "EN/UVLO", "L"), ("3", "ILIM", "L"), ("4", "dVdt", "L"), ("5", "GND", "L"),
                       ("6", "OUT", "R"), ("7", "PG", "R"), ("8", "FLT#", "R"), ("9", "IMON", "R"), ("10", "ITIMER", "R")], "U",
       "MP62_Storage:Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm", "TI TPS259824ONRGER 2.7-18 V 15 A eFuse (LCSC C2155766). LOGICAL pins: map IN/OUT pin groups from the datasheet", w=18)
addsym("TPS56C215", [("1", "VIN", "L"), ("2", "EN", "L"), ("3", "MODE", "L"), ("4", "SS", "L"), ("5", "PGND", "L"), ("6", "AGND", "L"),
                     ("7", "SW", "R"), ("8", "BOOT", "R"), ("9", "VREG5", "R"), ("10", "FB", "R"), ("11", "PGOOD", "R")], "U",
       "MP62_Storage:MP62_TI_RNN0018A_VQFN-HR-18_3.5x3.5mm_PLACEHOLDER", "TI TPS56C215RNNR 12 A sync buck (LCSC C473372). LOGICAL pins: map from TI RNN0018A", w=16)
addsym("TLV62585", [("1", "VIN", "L"), ("2", "EN", "L"), ("3", "GND", "L"), ("4", "SW", "R"), ("5", "FB", "R"), ("6", "PG", "R")], "U",
       "MP62_Storage:SOT-563", "TI TLV62585DRL 3 A buck (VDD_CORE). LOGICAL pins: verify DRL pinout", w=14)
addsym("LM74700", [("6", "ANODE", "L"), ("3", "EN", "L"), ("2", "GND", "L"), ("4", "CATHODE", "R"), ("5", "GATE", "R"), ("1", "VCAP", "R")], "U",
       "MP62_Storage:SOT-23-6", "TI LM74700-Q1 ideal-diode controller (reverse-polarity block), SOT-23-6 (KiCad stock pinout)", w=14)
addsym("NMOS_DGS", [("1", "S", "L"), ("4", "G", "L"), ("5", "D", "R")], "Q", "MP62_Storage:TDSON-8-1",
       "N-MOSFET 30 V <= 5 mOhm, 5x6 (pins 1-3 S, 4 G, 5-8 D: tie all in layout)", w=8)
addsym("BL24C64A", [("1", "A0", "L"), ("2", "A1", "L"), ("3", "A2", "L"), ("4", "GND", "L"), ("8", "VCC", "R"), ("7", "WP", "R"), ("6", "SCL", "R"), ("5", "SDA", "R")],
       "U", "MP62_Storage:SOIC-8_3.9x4.9mm_P1.27mm", "BL24C64A-SFRC 64 kbit I2C EEPROM (LCSC C111004)", w=12)
addsym("TMP1075DSG", [("1", "SDA", "L"), ("2", "SCL", "L"), ("3", "ALERT", "L"), ("4", "GND", "L"), ("8", "V+", "R"), ("7", "A0", "R"), ("6", "A1", "R"), ("5", "A2", "R"), ("9", "EP", "R")],
       "U", "MP62_Storage:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm", "TI TMP1075DSGR I2C temperature sensor (LCSC C2870250)", w=12)
addsym("74LVC2G07", [("1", "1A", "L"), ("3", "2A", "L"), ("2", "GND", "L"), ("5", "VCC", "R"), ("6", "1Y(OD)", "R"), ("4", "2Y(OD)", "R")],
       "U", "MP62_Storage:SOT-363_SC-70-6", "74LVC2G07 dual open-drain buffer (SC-70-6)", w=12)
addsym("SPI_FLASH_SOIC8", [("1", "CS#", "L"), ("2", "DO", "L"), ("3", "WP#", "L"), ("4", "GND", "L"), ("8", "VCC", "R"), ("7", "HOLD#", "R"), ("6", "CLK", "R"), ("5", "DI", "R")],
       "U", "MP62_Storage:SOIC-8_3.9x4.9mm_P1.27mm", "25-series SPI NOR flash, 3.3 V (size per ASMedia firmware)", w=12)
addsym("XTAL4", [("1", "X1", "L"), ("2", "GND", "L"), ("3", "X2", "R"), ("4", "GND", "R")], "Y", "MP62_Storage:Crystal_SMD_3225-4Pin_3.2x2.5mm", "Crystal 3225 4-pin", w=8)
addsym("C", [("1", "~", "L"), ("2", "~", "R")], "C", "MP62_Storage:C_0402_1005Metric", "Capacitor", w=2)
addsym("R", [("1", "~", "L"), ("2", "~", "R")], "R", "MP62_Storage:R_0402_1005Metric", "Resistor", w=2)
addsym("L", [("1", "~", "L"), ("2", "~", "R")], "L", "MP62_Storage:L_Bourns_SRP1038C_10.0x10.0mm", "Inductor", w=2)
addsym("LED", [("1", "K", "L"), ("2", "A", "R")], "D", "MP62_Storage:LED_0603_1608Metric", "LED", w=2)
addsym("D_x2_ACom", [("1", "K1", "L"), ("2", "K2", "L"), ("3", "A", "R")], "D", "MP62_Storage:SOT-23", "Dual Schottky common anode (BAT54A class)", w=6)
addsym("LUG", [("1", "LUG", "R")], "J", "MP62_Face:MP62_FACE_BusBarLug_D3.2_Pad8.8", "Bus-bar lug site (stock PSU bus bar)", w=4)

def pin_geom(s):
    L = [p for p in s["pins"] if p[2] == "L"]; R = [p for p in s["pins"] if p[2] == "R"]
    n = max(len(L), len(R)); h = (n + 1) * 2.54
    w = s["w"] or max(10, 1.27 * max([len(p[1]) for p in s["pins"]] + [4]) * 2 + 2)
    w = round(w / 2.54) * 2.54
    geo = {}
    for side, lst in (("L", L), ("R", R)):
        for i, p in enumerate(lst):
            y = h / 2 - 2.54 * (i + 1)
            x = -w / 2 - 2.54 if side == "L" else w / 2 + 2.54
            geo[p[0]] = (round(x, 2), round(y, 2), 0 if side == "L" else 180, p[1])
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
lib = '(kicad_symbol_lib (version 20241209) (generator "mp62_storage") (generator_version "9.0")\n' + "".join(sym_text(n, s) for n, s in SYMS.items()) + ')\n'
open(os.path.join(PRJ, LIBN + ".kicad_sym"), "w").write(lib)

# ---------- instances ----------
inst = []   # (ref, symname, x, y, value, netmap, footprint override, dnp)
def add(ref, sym, x, y, value, nets, fp=None, dnp=False):
    x = round(x / 2.54) * 2.54; y = round(y / 2.54) * 2.54
    inst.append((ref, sym, x, y, value, nets, fp, dnp))
# J1 MCIO
j1 = {}
for r in rows:
    c, sgl = r["contact"], r["signal"]
    if sgl == "GND": j1[c] = "GND"
    elif sgl[:3] == "PET" and sgl[4:].isdigit() and int(sgl[4:]) < 8:          # host TX -> module RX
        l = int(sgl[4:]); j1[c] = "PCIE_UP_RX%d_%s" % (l, "P" if sgl[3] == "p" else "N")
    elif sgl[:3] == "PER" and sgl[3] in "pn" and sgl[4:].isdigit() and int(sgl[4:]) < 8:          # module TX (via cap) -> host RX
        l = int(sgl[4:]); j1[c] = "PCIE_UP_TXC%d_%s" % (l, "P" if sgl[3] == "p" else "N")
    elif sgl == "PERST0#": j1[c] = "HOST_PERST#"
    elif sgl == "MCIO_PRSNT0#": j1[c] = "GND"
    elif sgl == "REFCLK0+": j1[c] = "HOST_REFCLK_P"
    elif sgl == "REFCLK0-": j1[c] = "HOST_REFCLK_N"
    elif sgl == "CLKREQ0#": j1[c] = "HOST_CLKREQ0#"
j1["MP"] = "GND"
add("J1", "MCIO124_RA_ModuleEnd", 60, 140, "MCIO124 RA G97R24332HR", j1)
# U1 switch
u1 = {}
for num, nm, side in sw:
    if nm.startswith("UP_RX"): u1[num] = "PCIE_UP_RX%s_%s" % (nm[5], nm[6])
    elif nm.startswith("UP_TX"): u1[num] = "PCIE_UP_TX%s_%s" % (nm[5], nm[6])
    elif nm.startswith("DN") and "_TX" in nm: u1[num] = "PCIE_SSD%s_TX%s_%s" % (nm[2], nm[6], nm[7])
    elif nm.startswith("DN") and "_RX" in nm: u1[num] = "PCIE_SSD%s_RX%s_%s" % (nm[2], nm[6], nm[7])
    elif "REFCLK_" in nm and nm.startswith("DN"): u1[num] = "SSD%s_REFCLK_%s" % (nm[2], nm[-1])
u1.update({n: v for n, nm, _ in sw for k_, v in [("REFCLK_IN_P", "HOST_REFCLK_P"), ("REFCLK_IN_N", "HOST_REFCLK_N"), ("PERST#", "SW_PERST#"),
           ("XTAL_IN", "XTAL_IN"), ("XTAL_OUT", "XTAL_OUT"), ("SPI_CS#", "SPI_CS#"), ("SPI_CLK", "SPI_CLK"), ("SPI_DO", "SPI_MOSI"),
           ("SPI_DI", "SPI_MISO"), ("VDD33", "3V3_SSD"), ("VDD_CORE", "VDD_CORE"), ("VDDA(TBD)", "VDD_CORE"), ("GND", "GND")] if nm == k_})
add("U1", "ASM2824", 330, 200, "ASM2824 (JLC C9900092023)", u1)
# AC caps: upstream TX (module side, 220 nF) and downstream TX (host side for the SSD, 220 nF)
cx, cy = 180, 60
cn = 100
for l in range(8):
    for pol in "PN":
        add("C%d" % cn, "C", cx, cy, "220nF 0201/0402 X7R", {"1": "PCIE_UP_TX%d_%s" % (l, pol), "2": "PCIE_UP_TXC%d_%s" % (l, pol)}); cn += 1; cy += 10.16
cx, cy = 450, 60
for d in range(4):
    for l in range(4):
        for pol in "PN":
            add("C%d" % cn, "C", cx + 45 * (d // 2), cy + 10.16 * (16 * (d % 2) + 2 * l + (pol == "N")), "220nF 0402 X7R",
                {"1": "PCIE_SSD%d_TX%d_%s" % (d, l, pol), "2": "PCIE_SSD%d_TXC%d_%s" % (d, l, pol)}); cn += 1
# M.2 sockets
for d in range(4):
    m = {}
    for n, nm in M2.items():
        s_ = str(n)
        if nm == "GND": m[s_] = "GND"
        elif nm == "3V3": m[s_] = "3V3_SSD"
        elif nm[:3] == "PET" and nm[3] in "pn": m[s_] = "PCIE_SSD%d_RX%s_%s" % (d, nm[4], "P" if nm[3] == "p" else "N")    # module TX -> switch RX
        elif nm[:3] == "PER" and nm[3] in "pn": m[s_] = "PCIE_SSD%d_TXC%s_%s" % (d, nm[4], "P" if nm[3] == "p" else "N")   # switch TX (after cap) -> module RX
        elif nm == "REFCLKp": m[s_] = "SSD%d_REFCLK_P" % d
        elif nm == "REFCLKn": m[s_] = "SSD%d_REFCLK_N" % d
        elif nm == "PERST#": m[s_] = "SSD%d_PERST#" % d
        elif nm == "CLKREQ#": m[s_] = "SSD%d_CLKREQ#" % d
        elif nm == "DAS/DSS#": m[s_] = "SSD%d_DAS#" % d
    m["MP"] = "GND"
    add("J%d" % (5 + d), "M2_Socket3_MKey", 640 + 170 * (d % 2), 150 + 230 * (d // 2), "M.2 M-key H4.2 LOTES APCI0107-P001A (SSD%d)" % d, m)
# PERST fan-out, CLKREQ / PERST pull-ups, LEDs
add("U9", "74LVC2G07", 330, 470, "74LVC2G07", {"1": "HOST_PERST#", "3": "HOST_PERST#", "2": "GND", "5": "3V3_SSD", "6": "SSD0_PERST#", "4": "SSD1_PERST#"})
add("U10", "74LVC2G07", 330, 500, "74LVC2G07", {"1": "HOST_PERST#", "3": "HOST_PERST#", "2": "GND", "5": "3V3_SSD", "6": "SSD2_PERST#", "4": "SSD3_PERST#"})
add("U12", "74LVC2G07", 330, 530, "74LVC2G07", {"1": "HOST_PERST#", "3": "PG_ALL", "2": "GND", "5": "3V3_SSD", "6": "SW_PERST#", "4": "SW_PERST#"})
rn = 200
for d in range(4):
    for sig in ("PERST#", "CLKREQ#"):
        add("R%d" % rn, "R", 700, 450 + 12 * (rn - 200), "10k", {"1": "SSD%d_%s" % (d, sig), "2": "3V3_SSD"}); rn += 1
    add("R%d" % rn, "R", 700, 450 + 12 * (rn - 200), "1k", {"1": "SSD%d_LEDK" % d, "2": "3V3_SSD"}, dnp=False); rn += 1
    add("D%d" % (1 + d), "LED", 760, 450 + 14 * d, "green 0603 (SSD%d activity)" % d, {"1": "SSD%d_DAS#" % d, "2": "SSD%d_LEDK" % d})
add("R%d" % rn, "R", 700, 450 + 12 * (rn - 200), "10k", {"1": "SW_PERST#", "2": "3V3_SSD"}); rn += 1
add("D6", "D_x2_ACom", 480, 470, "BAT54A", {"1": "SSD0_DAS#", "2": "SSD1_DAS#", "3": "MOD_LED#"})
add("D7", "D_x2_ACom", 480, 490, "BAT54A", {"1": "SSD2_DAS#", "2": "SSD3_DAS#", "3": "MOD_LED#"})
add("R%d" % rn, "R", 700, 450 + 12 * (rn - 200), "DNP 0R (CLKREQ0# to GND only if clk_flags.bit2)", {"1": "HOST_CLKREQ0#", "2": "GND"}, dnp=True); rn += 1
# switch support: crystal, flash, decoupling
add("Y1", "XTAL4", 200, 330, "25MHz 3225 (populate only if ASM2824 requires; TBD)", {"1": "XTAL_IN", "3": "XTAL_OUT", "2": "GND", "4": "GND"})
add("C300", "C", 180, 350, "12pF", {"1": "XTAL_IN", "2": "GND"}); add("C301", "C", 220, 350, "12pF", {"1": "XTAL_OUT", "2": "GND"})
add("U8", "SPI_FLASH_SOIC8", 200, 380, "W25Q16JVSSIQ class (size TBD)", {"1": "SPI_CS#", "2": "SPI_MISO", "3": "3V3_SSD", "4": "GND", "8": "3V3_SSD", "7": "3V3_SSD", "6": "SPI_CLK", "5": "SPI_MOSI"})
for i in range(12):
    add("C%d" % (310 + i), "C", 180 + 25 * (i % 4), 410 + 12 * (i // 4), "1uF/100nF 0402", {"1": "VDD_CORE" if i < 8 else "3V3_SSD", "2": "GND"})
# management
add("J3", "GH15_AUX", 60, 400, "J_AUX SM15B-GHS-TB", {"1": "3V3_AUX", "2": "3V3_AUX", "3": "GND", "4": "GND", "5": "FACE_PWR_EN", "6": "FACE_PWR_GOOD",
    "7": "GND", "8": "FACE_SMB_CLK", "9": "FACE_SMB_DAT", "10": "FACE_SMB_ALERT#", "11": "THERM_ALERT#", "12": "THERM_TRIP#", "15": "MOD_LED#", "MP": "GND"})
add("R300", "R", 120, 450, "100k", {"1": "FACE_PWR_EN", "2": "GND"})
add("U6", "BL24C64A", 60, 470, "BL24C64A-SFRC @0x50", {"1": "GND", "2": "GND", "3": "GND", "4": "GND", "8": "3V3_AUX", "7": "EEPROM_WP", "6": "FACE_SMB_CLK", "5": "FACE_SMB_DAT"})
add("R301", "R", 120, 464, "10k (WP strapped high)", {"1": "EEPROM_WP", "2": "3V3_AUX"})
add("R302", "R", 120, 476, "DNP 0R (WP low to program)", {"1": "EEPROM_WP", "2": "GND"}, dnp=True)
add("U7", "TMP1075DSG", 60, 500, "TMP1075DSGR @0x48 (THERM_ALERT#)", {"1": "FACE_SMB_DAT", "2": "FACE_SMB_CLK", "3": "THERM_ALERT#", "4": "GND", "8": "3V3_AUX", "7": "GND", "6": "GND", "5": "GND", "9": "GND"})
add("U11", "TMP1075DSG", 60, 530, "TMP1075DSGR @0x49 (THERM_TRIP#, POR default 80 C comparator)", {"1": "FACE_SMB_DAT", "2": "FACE_SMB_CLK", "3": "THERM_TRIP#", "4": "GND", "8": "3V3_AUX", "7": "3V3_AUX", "6": "GND", "5": "GND", "9": "GND"})
add("C400", "C", 120, 500, "100nF", {"1": "3V3_AUX", "2": "GND"}); add("C401", "C", 120, 530, "100nF", {"1": "3V3_AUX", "2": "GND"})
add("C402", "C", 120, 488, "100nF", {"1": "3V3_AUX", "2": "GND"})
# power
for ref, n, x, y in (("J20", "+12V_IN", 60, 600), ("J22", "+12V_IN", 60, 610), ("J21", "GND", 60, 620), ("J23", "GND", 60, 630)):
    add(ref, "LUG", x, y, "bus-bar lug %s" % n, {"1": n})
add("Q1", "NMOS_DGS", 140, 600, "N-MOSFET 30V <=5mOhm 5x6", {"1": "+12V_IN", "4": "RB_GATE", "5": "+12V_PROT"})
add("U3", "LM74700", 140, 640, "LM74700-Q1 (DBV)", {"6": "+12V_IN", "3": "+12V_IN", "2": "GND", "4": "+12V_PROT", "5": "RB_GATE", "1": "RB_VCAP"})
add("C500", "C", 200, 650, "100nF 25V (VCAP)", {"1": "RB_VCAP", "2": "+12V_IN"})
add("C501", "C", 200, 600, "10uF 25V 1206 (<=47 uF total ahead of eFuse)", {"1": "+12V_PROT", "2": "GND"})
add("U2", "TPS259824ON", 260, 610, "TPS259824ONRGER (C2155766)", {"1": "+12V_PROT", "2": "EFUSE_EN", "3": "EFUSE_ILIM", "4": "EFUSE_DVDT", "5": "GND",
    "6": "+12V_SW", "7": "EFUSE_PG", "8": "FACE_SMB_ALERT#", "9": "EFUSE_IMON", "10": "GND"})
add("R500", "R", 320, 640, "1k (EN series; FACE_PWR_EN 3.3 V > EN threshold)", {"1": "FACE_PWR_EN", "2": "EFUSE_EN"})
add("R501", "R", 320, 652, "ILIM set ~5 A (value per datasheet)", {"1": "EFUSE_ILIM", "2": "GND"})
add("C502", "C", 320, 664, "dVdt: inrush <= 1 A into ~400 uF (value per datasheet)", {"1": "EFUSE_DVDT", "2": "GND"})
add("R502", "R", 320, 676, "IMON (value per datasheet)", {"1": "EFUSE_IMON", "2": "GND"})
add("R503", "R", 320, 688, "10k PG pull-up", {"1": "EFUSE_PG", "2": "3V3_AUX"})
add("U4", "TPS56C215", 420, 610, "TPS56C215RNNR (C473372)", {"1": "+12V_SW", "2": "EFUSE_PG", "3": "BUCK_MODE", "4": "BUCK_SS", "5": "GND", "6": "GND",
    "7": "BUCK_SW", "8": "BUCK_BOOT", "9": "BUCK_VREG5", "10": "BUCK_FB", "11": "PG_3V3"})
add("L1", "L", 500, 600, "1.0uH >=15A Isat 10x10 (SRP1038C class)", {"1": "BUCK_SW", "2": "3V3_SSD"})
add("C503", "C", 500, 612, "100nF BOOT", {"1": "BUCK_BOOT", "2": "BUCK_SW"})
add("C504", "C", 500, 624, "4.7uF VREG5", {"1": "BUCK_VREG5", "2": "GND"})
add("C505", "C", 500, 636, "SS cap (value per datasheet)", {"1": "BUCK_SS", "2": "GND"})
add("R504", "R", 500, 648, "MODE strap (DCAP3, FCCM/skip per datasheet)", {"1": "BUCK_MODE", "2": "GND"})
add("R505", "R", 500, 660, "FB top (3.3 V)", {"1": "3V3_SSD", "2": "BUCK_FB"}); add("R506", "R", 500, 672, "FB bottom", {"1": "BUCK_FB", "2": "GND"})
add("R507", "R", 500, 684, "10k PG pull-up", {"1": "PG_3V3", "2": "3V3_AUX"})
for i in range(4):
    add("C%d" % (510 + i), "C", 560, 600 + 12 * i, "22uF 25V 1206 (VIN)", {"1": "+12V_SW", "2": "GND"})
for i in range(6):
    add("C%d" % (520 + i), "C", 600, 600 + 12 * i, "47uF 6.3V 1206 (3V3_SSD)", {"1": "3V3_SSD", "2": "GND"})
for i in range(8):
    add("C%d" % (530 + i), "C", 640, 600 + 12 * i, "22uF 0805 (at slot %d)" % (i // 2), {"1": "3V3_SSD", "2": "GND"})
add("U5", "TLV62585", 420, 700, "TLV62585DRL VDD_CORE (voltage per ASM2824 datasheet)", {"1": "3V3_SSD", "2": "PG_3V3", "3": "GND", "4": "CORE_SW", "5": "CORE_FB", "6": "PG_ALL"})
add("L2", "L", 500, 704, "0.47uH 2520", {"1": "CORE_SW", "2": "VDD_CORE"}, fp="MP62_Storage:L_1008_2520Metric")
add("R508", "R", 500, 716, "FB top (VDD_CORE)", {"1": "VDD_CORE", "2": "CORE_FB"}); add("R509", "R", 500, 728, "FB bottom", {"1": "CORE_FB", "2": "GND"})
add("R510", "R", 500, 740, "10k PG pull-up", {"1": "PG_ALL", "2": "3V3_SSD"})
add("R511", "R", 500, 752, "0R: PG_ALL -> FACE_PWR_GOOD (OD, host pull-up)", {"1": "PG_ALL", "2": "FACE_PWR_GOOD"})
add("C540", "C", 580, 700, "22uF 0805 (VDD_CORE)", {"1": "VDD_CORE", "2": "GND"}); add("C541", "C", 580, 712, "10uF 0805 (CORE VIN)", {"1": "3V3_SSD", "2": "GND"})
add("D5", "LED", 580, 740, "green 0603 (3V3_SSD on)", {"1": "PWR_LEDK", "2": "3V3_SSD"})
add("R512", "R", 620, 740, "1k", {"1": "PWR_LEDK", "2": "GND"})

# ---------- emit schematic ----------
def esc(s): return s.replace('"', "'")
out = [f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{ROOT}") (paper "A0")',
       '  (title_block (title "MP62 Face S storage module SM-1 rev A0 (4 x M.2 NVMe behind ASM2824)") (date "2026-10-01") (rev "A0")'
       ' (company "MacPro6,2 / Aidan Winkler") (comment 1 "Flat sheet, label connectivity. LOGICAL pins: ASM2824, TPS259824, TPS56C215, TLV62585 - verify vs datasheets")'
       ' (comment 2 "Values marked per datasheet are TBD. Small passives not yet placed on the PCB floorplan"))',
       '  (lib_symbols']
for n, s in SYMS.items():
    out.append(sym_text(f"{LIBN}:{n}", s).replace(f'(symbol "{LIBN}:{n}_0_1"', f'(symbol "{n}_0_1"').replace(f'(symbol "{LIBN}:{n}_1_1"', f'(symbol "{n}_1_1"'))
out.append('  )')
nlabels = 0; nnc = 0
for ref, sname, X, Y, val, nets, fp, dnp in inst:
    s = SYMS[sname]; w, h, geo = pin_geom(s)
    fpv = fp or s["fp"]
    out.append(f'  (symbol (lib_id "{LIBN}:{sname}") (at {X:.3f} {Y:.3f} 0) (unit 1) (exclude_from_sim no) (in_bom {"no" if dnp else "yes"}) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{U()}")')
    out.append(f'    (property "Reference" "{ref}" (at {X} {Y - h / 2 - 1.5:.2f} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Value" "{esc(val)}" (at {X} {Y + h / 2 + 1.5:.2f} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Footprint" "{fpv}" (at {X} {Y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    out.append(f'    (property "Datasheet" "" (at {X} {Y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    for num in geo: out.append(f'    (pin "{num}" (uuid "{U()}"))')
    out.append(f'    (instances (project "{NAME}" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )')
    for num, (px, py, a, nm) in geo.items():
        x, y = round(X + px, 3), round(Y - py, 3)
        if num in nets:
            ang, just = (180, "right bottom") if a == 0 else (0, "left bottom")
            out.append(f'  (label "{nets[num]}" (at {x} {y} {ang}) (effects (font (size 1.0 1.0)) (justify {just})) (uuid "{U()}"))'); nlabels += 1
        else:
            out.append(f'  (no_connect (at {x} {y}) (uuid "{U()}"))'); nnc += 1
out.append(f'  (sheet_instances (path "/" (page "1")))\n)')
open(os.path.join(PRJ, NAME + ".kicad_sch"), "w").write("\n".join(out) + "\n")
open(os.path.join(PRJ, "sym-lib-table"), "w").write('(sym_lib_table\n  (version 7)\n  (lib (name "MP62_Storage")(type "KiCad")(uri "${KIPRJMOD}/MP62_Storage.kicad_sym")(options "")(descr "MP62 storage module symbols"))\n)\n')
print("symbols", len(SYMS), "instances", len(inst), "labels", nlabels, "no_connect", nnc)
