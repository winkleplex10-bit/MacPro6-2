#!/usr/bin/env python3
"""Generate the MacPro6,2 backplane top-level block-diagram schematic (KiCad 9 format):
a root sheet with hierarchical sheet symbols + labels, and one stub file per block that
holds the matching hierarchical labels and a text description. No components yet."""
import os, uuid
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
U = lambda: str(uuid.uuid4())
ROOT_UUID = "6a1c2d3e-0000-4000-8000-00000000mp62".replace("mp62", "0062")
VER = '(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")'
F = '(effects (font (size 1.27 1.27))'

def g(v):  # snap to 1.27 mm grid
    return round(v / 1.27) * 1.27

# name, file, description lines, pins [(name, type)] ; type in input/output/bidirectional/passive
I, O, B, P = "input", "output", "bidirectional", "passive"
SHEETS = [
 ("Power input, standby rails, safety gate", "power.kicad_sch", [
   "J2 PSU-IN Micro-Fit 3.0 2x4: 12V x2, GND x3, 11V_SB, PS_ON#, PWR_OK (stock PSU pinout TBD, adapter harness)",
   "11V_SB -> 3V3_SB (MCU, EEPROMs, face aux in S5); 11V_SB -> 5V_SBY (COM-HPC suspend well)",
   "12V_MAIN -> 3V3_BP buck (S0); input TVS + fuse; INA228 power monitor 0x40 on I2C_SYS, ALERT -> PWR_ALERT_BP_N (12V_MAIN / 11V_SB stay inside this sheet)",
   "BP 12 V load ~1 A (3V3_BP incl. Gen5 redrivers); fan moved to IOB CONN_C, CB / faces / IOB 12 V by their own PSU leads",
   "HW gate: PS_ON = INTERLOCK_OK AND PS_ON_REQ AND NOT THERM_LATCH (discrete logic, 3V3_SB)",
   "THERM_LATCH set by MOD_THERMTRIP_N / FACE_x_THERM_TRIP_N; cleared by AC cycle (TBD)",
   "INTERLOCK_OK = HALL_A AND HALL_B (or BENCH jumper AND MCU unlock)"],
  [("3V3_SB", O), ("5V_SBY", O), ("3V3_BP", O), ("PSU_PWR_OK", O),
   ("PS_ON_REQ", I), ("IOB_HALL_A_N", I), ("IOB_HALL_B_N", I), ("BENCH_UNLOCK", I), ("INTERLOCK_OK", O),
   ("MOD_THERMTRIP_N", I), ("FACE_P_THERM_TRIP_N", I), ("FACE_S_THERM_TRIP_N", I), ("THERM_LATCH", O),
   ("I2C_SYS_SCL", B), ("I2C_SYS_SDA", B), ("PWR_ALERT_BP_N", O)]),
 ("Management MCU (RP2350A)", "mcu.kicad_sch", [
   "U1 RP2350A (LCSC C42411118) + U2 16 MB QSPI flash + 12 MHz crystal; SWD (J8), BOOTSEL (SW1)",
   "USB FS composite device to the host (HID sensors + vendor HID) via CPU-LINK USB2",
   "Power sequencing (S5/S0 only in rev A), face power policy; LIVE POWER TARGET (arch spec 5.5 / ICD 13.2): 445 W ceiling, 10 Hz loop",
   "LPT telemetry: INA228 BP 0x40 + IOB 0x41 (I2C_SYS), CB 0x45 (MOD_I2C0), faces 0x40 (FACE_x_SMB); alerts: PWR_ALERT_BP_N, MOD_PWR_ALERT_N, IOB_INT_N, FACE_x_SMB_ALERT_N",
   "LPT actuators: EC (UART0: PL1/PL2/PL4, ratio cap) + MOD_CARRIER_HOT_N (PROCHOT#), FACE_x_THERM_ALERT_N (fast cap), face power-target register, PD pool via I2C_PD",
   "Fan: reads the CB demand (MOD_FAN_PWMOUT) and drives the IOB EMC2101 (0x4C on I2C_PD behind TCA9517); reloads LUT + TCRIT at every S0 entry (fail-safe)",
   "Owns FACE_P/FACE_S SMBus segments (ID EEPROM 0x50, temp sensor 0x48)",
   "I2C_SYS: INA 0x40, TMP1075 U3 0x48 / U4 0x49, BP EEPROM 0x50; IOB: LIS2DH12 0x18, EMC2101 0x4C, EEPROM 0x51, TLC59116 0x60",
   "MOD_I2C0 (CPU-LINK B90/B92) = CB ID EEPROM 0x57; MOD_SMB = PCH SMBus (DIMM SPD) -> BP leaves it isolated (DNP) by default",
   "GPIO count is tight on RP2350A: I2C GPIO expander or RP2350B if needed (TBD)"],
  [("3V3_SB", I), ("USB_MCU_DP", B), ("USB_MCU_DN", B), ("PS_ON_REQ", O), ("PSU_PWR_OK", I), ("INTERLOCK_OK", I),
   ("THERM_LATCH", I), ("BENCH_UNLOCK", O), ("PWRBTN_IN_N", I), ("I2C_SYS_SCL", B), ("I2C_SYS_SDA", B),
   ("MOD_PWRBTN_N", O), ("MOD_SUS_S3_N", I), ("MOD_SUS_S5_N", I), ("MOD_RSMRST_N", I), ("MOD_VIN_PWR_OK", O),
   ("MOD_PLTRST_N", I), ("MOD_CARRIER_HOT_N", O), ("MOD_FAN_PWMOUT", I), ("MOD_FAN_TACHIN", O), ("MOD_PWR_ALERT_N", I), ("PWR_ALERT_BP_N", I),
   ("MOD_SMB_SCL", B), ("MOD_SMB_SDA", B), ("MOD_I2C0_SCL", B), ("MOD_I2C0_SDA", B), ("IOB_INT_N", I), ("IOB_PRSNT_N", I),
   ("FACE_P_MOD_LED_N", I), ("FACE_S_MOD_LED_N", I),
   ("FACE_P_PWR_EN", O), ("FACE_P_PWR_GOOD", I), ("FACE_P_RDY", O), ("FACE_P_PRSNT_N", I), ("FACE_P_THERM_ALERT_N", B),
   ("FACE_P_SMB_SCL", B), ("FACE_P_SMB_SDA", B), ("FACE_P_SMB_ALERT_N", I),
   ("FACE_S_PWR_EN", O), ("FACE_S_PWR_GOOD", I), ("FACE_S_RDY", O), ("FACE_S_PRSNT_N", I), ("FACE_S_THERM_ALERT_N", B),
   ("FACE_S_SMB_SCL", B), ("FACE_S_SMB_SDA", B), ("FACE_S_SMB_ALERT_N", I)]),
 ("Face P (primary) AUX link", "face_aux.kicad_sch", None,
  [("FACE_PWR_EN", I), ("FACE_PWR_GOOD", O), ("FACE_PRSNT_N", O), ("FACE_SMB_SCL", B), ("FACE_SMB_SDA", B),
   ("FACE_SMB_ALERT_N", O), ("FACE_THERM_ALERT_N", B), ("FACE_THERM_TRIP_N", O), ("FACE_USB_DP", B), ("FACE_USB_DN", B),
   ("FACE_MOD_LED_N", O), ("3V3_SB", I), ("3V3_BP", I)]),
 ("Face S (secondary) AUX link", "face_aux.kicad_sch", None, None),
 ("CPU board link (J1 CPU-LINK card edge)", "cpu_link.kicad_sch", [
   "J1: Amphenol Mini Cool Edge 224 (ME1022410103011) vertical SMT; MP62 hub pinout (docs/cpulink_224_pinout_draft.csv, CB mapping column)",
   "PCIe HUB: J1 x16 -> J9 MCIO 124 (Face P), J1 x4 -> J10 MCIO 124 (Face S), REFCLK P/S; 85 ohm L1 (TX) / L6 (RX)",
   "Optional Gen5 build: U10-U13 (Face P) + U14 (Face S) TI DS320PR810 linear redrivers + 220 nF output AC caps",
   "Gen4 build: no redrivers, no AC caps on BP (host-TX caps on module/CPU board, device-TX caps on face)",
   "PWR_ALERT# (A-row bay 4, was RSVD_LS1): CB INA228 0x45 ALERT + U11 FLT#, OD, BP 10k pull-up (live power target)",
   "Also carries: power/state sideband (COM-HPC names, CB = Z790 PCH + EC), fan PWMOUT/TACHIN (demand only), SMBus, I2C0, USB2 x4, SATA0, 5V_SBY x6, 3V3_SB x2, GND x80",
   "USB2 x4 = MCU (BP MCU), FACEP / FACES (face AUX pins 13/14), SPARE -> IOB-LINK J6 13/14 (IOB hub H2: USB-A A1-A4 + Bluetooth)",
   "BP makes PERST#_x = PLTRST# AND FACE_x_RDY (MCU asserts after FACE_x_PWR_GOOD); CLKREQ#_x end on BP; WAKE#_x ORed to WAKE0#",
   "12 V main for the CPU board does NOT pass through J1 (CB LUG1/LUG2 single 12 V entry, U11 eFuse)"],
  [("5V_SBY", O), ("3V3_SB", O), ("MOD_PWRBTN_N", I), ("MOD_SUS_S3_N", O), ("MOD_SUS_S5_N", O), ("MOD_RSMRST_N", O),
   ("MOD_VIN_PWR_OK", I), ("MOD_PLTRST_N", O), ("MOD_THERMTRIP_N", O), ("MOD_CARRIER_HOT_N", I), ("MOD_PWR_ALERT_N", O), ("MOD_FAN_PWMOUT", O),
   ("MOD_FAN_TACHIN", I), ("MOD_SMB_SCL", B), ("MOD_SMB_SDA", B), ("FACE_P_RDY", I), ("FACE_S_RDY", I),
   ("USB_MCU_DP", B), ("USB_MCU_DN", B), ("FACE_P_USB_DP", B), ("FACE_P_USB_DN", B), ("FACE_S_USB_DP", B), ("FACE_S_USB_DN", B),
   ("IOB_USB_DP", B), ("IOB_USB_DN", B), ("MOD_I2C0_SCL", B), ("MOD_I2C0_SDA", B),
   ("SATA0_TX_P", O), ("SATA0_TX_N", O), ("SATA0_RX_P", I), ("SATA0_RX_N", I)]),
 ("I/O board low-speed link", "iob_link.kicad_sch", [
   "J6 JST GH 15P (BM15B vertical) <-> IOB J6, 1:1 GH 15P cable (ICD 2026-10-02, pinout = IOB plan 5.3):",
   "1,2 3V3_SB (BP -> IOB) | 3,7,12,15 GND | 4 PWRBTN_IN_N | 5 HALL_A_N | 6 HALL_B_N | 8 I2C_SYS_SCL | 9 I2C_SYS_SDA",
   "10 IOB_INT_N (OD, IOB -> BP, BP pull-up; PD IRQs + LIS2DH12 + IOB INA228 0x41 ALERT) | 11 IOB_PRSNT_N (IOB ties to GND; BP 10k pull-up to 3V3_SB) | 13/14 USB2_LINK D+/D- (CPU-LINK USB2_SPARE)",
   "IOB high-speed (USB3 x10, DDI, 2x i226 PCIe, VBAT) runs CB J3 -> IOB HS1 directly; 12 V via the IOB 12P PSU header, not the BP"],
  [("PWRBTN_IN_N", O), ("IOB_HALL_A_N", O), ("IOB_HALL_B_N", O), ("I2C_SYS_SCL", B), ("I2C_SYS_SDA", B),
   ("IOB_INT_N", O), ("IOB_PRSNT_N", O), ("IOB_USB_DP", B), ("IOB_USB_DN", B), ("3V3_SB", I)]),
 ("OpenCore boot M.2 (SATA)", "m2_boot.kicad_sch", [
   "J7 M.2 M-key socket wired SATA-only (accepts B+M SATA 2242/2230 cards); dedicated OpenCore device",
   "Set as the default UEFI boot entry (LauncherOption=Full); removable-path fallback on the same ESP",
   "SATA0 from the CB Z790 PCH via J1 (SATA-capable HSIO not shared with the M.2 RP9-12 lanes, TBD on the CB)"],
  [("SATA0_TX_P", I), ("SATA0_TX_N", I), ("SATA0_RX_P", O), ("SATA0_RX_N", O), ("3V3_BP", I)]),
]
FACE_DESC = [
  "J3 (Face P) / J4 (Face S): JST GH 15P (BM15B vertical) AUX cable BP -> face J_AUX; pinout = MP62-FACE v0.1 aux_gh15.csv (1:1)",
  "FACE_PWR_EN / FACE_PWR_GOOD, PRSNT#, SMBus (ID EEPROM 0x50, TMP1075 0x48, extra 0x49-0x4F, INA228 12 V monitor 0x40, power-target agent 0x58), THERM_ALERT#, THERM_TRIP#, USB2 (primary), MOD_LED# (pin 15), 3V3_AUX",
  "3V3_AUX: load switch from 3V3_SB (S5, <=50 mW) / 3V3_BP (S0, <=3.3 W); SMBus isolated until FACE_PWR_GOOD",
  "Face main 12 V: bus bar / lug (not on this cable). PCIe + REFCLK + PERST# + CLKREQ# + WAKE#: MCIO from CPU board"]
FP, FS = [i for i, sh in enumerate(SHEETS) if sh[1] == "face_aux.kicad_sch"]
SHEETS[FP] = (SHEETS[FP][0], SHEETS[FP][1], FACE_DESC, SHEETS[FP][3])
SHEETS[FS] = (SHEETS[FS][0], SHEETS[FS][1], FACE_DESC, SHEETS[FP][3])
PREFIX = {FP: "FACE_P_", FS: "FACE_S_"}

def top_net(idx, pin):
    if idx in PREFIX and pin.startswith("FACE_"):
        return PREFIX[idx] + pin[len("FACE_"):]
    return pin

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
    s += f'\t(title_block\n\t\t(title "MP62 backplane: {name if fname != "face_aux.kicad_sch" else "Face AUX link (instanced for Face P and Face S)"}")\n\t\t(date "2026-10-02")\n\t\t(rev "A-bd2")\n\t\t(comment 1 "Block stub: hierarchical labels + one non-BOM stub symbol (#BLKn, passive pins) so ERC sees the nets; circuit TBD")\n\t)\n\t(lib_symbols\n' + stub_lib(sym, pins) + '\t)\n'
    y = 30.48
    for (pn, pt) in pins:
        s += f'\t(hierarchical_label "{pn}"\n\t\t(shape {pt})\n\t\t(at 38.1 {y:.2f} 180)\n\t\t{F} (justify right))\n\t\t(uuid "{U()}")\n\t)\n'
        y += 2.54
    s += f'\t(symbol\n\t\t(lib_id "MP62:{sym}")\n\t\t(at 38.1 30.48 0)\n\t\t(unit 1)\n\t\t(exclude_from_sim yes)\n\t\t(in_bom no)\n\t\t(on_board no)\n\t\t(dnp no)\n\t\t(uuid "{U()}")\n'
    s += f'\t\t(property "Reference" "#BLK{insts[0][1] + 1}"\n\t\t\t(at 40.64 27.94 0)\n\t\t\t(effects (font (size 1.27 1.27)) (justify left) (hide yes))\n\t\t)\n'
    s += f'\t\t(property "Value" "{sym}"\n\t\t\t(at 40.64 26.67 0)\n\t\t\t(effects (font (size 1.27 1.27)) (justify left) (hide yes))\n\t\t)\n'
    for i in range(len(pins)):
        s += f'\t\t(pin "{i + 1}"\n\t\t\t(uuid "{U()}")\n\t\t)\n'
    s += '\t\t(instances\n\t\t\t(project "backplane"\n'
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
open(os.path.join(PRJ, "MP62_BP_Stubs.kicad_sym"), "w").write(_lib)
open(os.path.join(PRJ, "sym-lib-table"), "w").write('(sym_lib_table\n  (version 7)\n  (lib (name "MP62")(type "KiCad")(uri "${KIPRJMOD}/MP62_BP_Stubs.kicad_sym")(options "")(descr "MP62 backplane block-stub symbols (non-BOM)"))\n)\n')

# ---------- root sheet ----------
s = f'(kicad_sch\n\t{VER}\n\t(uuid "{ROOT_UUID}")\n\t(paper "A2")\n'
s += '\t(title_block\n\t\t(title "MacPro6,2 Backplane (BP) - top-level block diagram")\n\t\t(date "2026-10-02")\n\t\t(rev "A-bd2")\n\t\t(company "MacPro6,2 / Aidan Winkler")\n'
s += '\t\t(comment 1 "HUB topology: CPU board card edge J1 (Mini Cool Edge 224) -> BP -> J9/J10 MCIO 124 -> Face P x16 / Face S x4")\n\t\t(comment 2 "See macpro62-architecture-spec-v0.2.md sections 3-5")\n\t)\n\t(lib_symbols)\n'
s += text("MP62 BACKPLANE rev A - BLOCK DIAGRAM. Sheets are stubs (labels only). Nets with the same label name are connected.", 25.4, 20.32, 2.0)
s += text("Off-board links: J1 CPU-LINK (card edge from CPU board) | J2 PSU-IN | J3/J4 Face P/S AUX (GH15) | J6 IOB-LINK (fan via IOB CONN_C, no J5) | J7 M.2 OpenCore | J8 SWD | J9/J10 MCIO 124 to Face P/S (PCIe hub)", 25.4, 25.4, 1.6)
W = 60.96
cols = [(38.1, 38.1), (165.1, 38.1), (292.1, 38.1), (38.1, 200.66), (165.1, 200.66), (292.1, 200.66), (419.1, 38.1), (419.1, 200.66)]
page = 2
for idx, (name, fname, desc, pins) in enumerate(SHEETS):
    x, y = cols[idx]
    h = g(5.08 + 2.54 * len(pins))
    s += f'\t(sheet\n\t\t(at {x:.2f} {y:.2f})\n\t\t(size {W:.2f} {h:.2f})\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n'
    s += '\t\t(stroke (width 0.1524) (type solid))\n\t\t(fill (color 0 0 0 0.0000))\n'
    s += f'\t\t(uuid "{SHEET_UUIDS[idx]}")\n'
    s += f'\t\t(property "Sheetname" "{name}"\n\t\t\t(at {x:.2f} {y - 0.71:.2f} 0)\n\t\t\t{F} (justify left bottom))\n\t\t)\n'
    s += f'\t\t(property "Sheetfile" "{fname}"\n\t\t\t(at {x:.2f} {y + h + 0.59:.2f} 0)\n\t\t\t{F} (justify left top))\n\t\t)\n'
    py = y + 2.54
    labels = ""
    for (pn, pt) in pins:
        # inputs on the left edge, everything else on the right edge
        left = (pt == "input")
        px = x if left else x + W
        ang = 180 if left else 0
        just = "left" if left else "right"
        s += f'\t\t(pin "{pn}" {pt}\n\t\t\t(at {px:.2f} {py:.2f} {ang})\n\t\t\t(uuid "{U()}")\n\t\t\t{F} (justify {just}))\n\t\t)\n'
        lx = px - 10.16 if left else px + 10.16
        labels += f'\t(wire\n\t\t(pts (xy {px:.2f} {py:.2f}) (xy {lx:.2f} {py:.2f}))\n\t\t(stroke (width 0) (type default))\n\t\t(uuid "{U()}")\n\t)\n'
        net = top_net(idx, pn)
        lang = 0 if not left else 180
        ljust = "left" if not left else "right"
        labels += f'\t(label "{net}"\n\t\t(at {lx:.2f} {py:.2f} {lang})\n\t\t(fields_autoplaced yes)\n\t\t{F} (justify {ljust} bottom))\n\t\t(uuid "{U()}")\n\t)\n'
        py += 2.54
    s += f'\t\t(instances\n\t\t\t(project "backplane"\n\t\t\t\t(path "/{ROOT_UUID}"\n\t\t\t\t\t(page "{page}")\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
    s += labels
    page += 1
s += '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n)\n'
open(os.path.join(PRJ, "backplane.kicad_sch"), "w").write(s)
print("schematic written")
