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
   "12V_MAIN -> 3V3_BP buck (S0); input TVS + fuse; INA-class monitor on I2C_SYS",
   "HW gate: PS_ON = INTERLOCK_OK AND PS_ON_REQ AND NOT THERM_LATCH (discrete logic, 3V3_SB)",
   "THERM_LATCH set by MOD_THERMTRIP_N / FACE_x_THERM_TRIP_N; cleared by AC cycle (TBD)",
   "INTERLOCK_OK = HALL_A AND HALL_B (or BENCH jumper AND MCU unlock)"],
  [("12V_MAIN", O), ("11V_SB", O), ("3V3_SB", O), ("5V_SBY", O), ("3V3_BP", O), ("PSU_PWR_OK", O),
   ("PS_ON_REQ", I), ("IOB_HALL_A_N", I), ("IOB_HALL_B_N", I), ("BENCH_UNLOCK", I), ("INTERLOCK_OK", O),
   ("MOD_THERMTRIP_N", I), ("FACE_P_THERM_TRIP_N", I), ("FACE_S_THERM_TRIP_N", I), ("THERM_LATCH", O),
   ("I2C_SYS_SCL", B), ("I2C_SYS_SDA", B)]),
 ("Management MCU (RP2350A)", "mcu.kicad_sch", [
   "U1 RP2350A (LCSC C42411118) + U2 16 MB QSPI flash + 12 MHz crystal; SWD (J8), BOOTSEL (SW1)",
   "USB FS composite device to the host (HID sensors + vendor HID) via CPU-LINK USB2",
   "Power sequencing (S5/S0 only in rev A), fan loop (PIO tach capture), face power policy",
   "Owns FACE_P/FACE_S SMBus segments (ID EEPROM 0x50, temp sensor 0x48)",
   "I2C_SYS: INA monitor, TMP1075 x2 core-base sensors (U3, U4), BP EEPROM, IOB LED driver",
   "GPIO count is tight on RP2350A: I2C GPIO expander or RP2350B if needed (TBD)"],
  [("3V3_SB", I), ("USB_MCU_DP", B), ("USB_MCU_DN", B), ("PS_ON_REQ", O), ("PSU_PWR_OK", I), ("INTERLOCK_OK", I),
   ("THERM_LATCH", I), ("BENCH_UNLOCK", O), ("PWRBTN_IN_N", I), ("I2C_SYS_SCL", B), ("I2C_SYS_SDA", B),
   ("MOD_PWRBTN_N", O), ("MOD_SUS_S3_N", I), ("MOD_SUS_S5_N", I), ("MOD_RSMRST_N", I), ("MOD_VIN_PWR_OK", O),
   ("MOD_PLTRST_N", I), ("MOD_CARRIER_HOT_N", O), ("MOD_FAN_PWMOUT", I), ("MOD_FAN_TACHIN", O),
   ("MOD_SMB_SCL", B), ("MOD_SMB_SDA", B), ("FAN_PWM", O), ("FAN_TACH", I),
   ("FACE_P_PWR_EN", O), ("FACE_P_PWR_GOOD", I), ("FACE_P_RDY", O), ("FACE_P_PRSNT_N", I), ("FACE_P_THERM_ALERT_N", B),
   ("FACE_P_SMB_SCL", B), ("FACE_P_SMB_SDA", B), ("FACE_P_SMB_ALERT_N", I),
   ("FACE_S_PWR_EN", O), ("FACE_S_PWR_GOOD", I), ("FACE_S_RDY", O), ("FACE_S_PRSNT_N", I), ("FACE_S_THERM_ALERT_N", B),
   ("FACE_S_SMB_SCL", B), ("FACE_S_SMB_SDA", B), ("FACE_S_SMB_ALERT_N", I)]),
 ("Fan", "fan.kicad_sch", [
   "J5 JST GH 4P: 12V, GND, PWM (open-drain, 25 kHz), FG tach -> harness to the top interposer",
   "Stock fan: Allegro A5940, 100k internal PWM pull-up => full speed if PWM floats (fail-safe)",
   "12V fan feed through eFuse; stock fan connector pinout / supply TBD (donor)"],
  [("12V_MAIN", I), ("FAN_PWM", I), ("FAN_TACH", O)]),
 ("Face P (primary) AUX link", "face_aux.kicad_sch", None,
  [("FACE_PWR_EN", I), ("FACE_PWR_GOOD", O), ("FACE_PRSNT_N", O), ("FACE_SMB_SCL", B), ("FACE_SMB_SDA", B),
   ("FACE_SMB_ALERT_N", O), ("FACE_THERM_ALERT_N", B), ("FACE_THERM_TRIP_N", O), ("FACE_USB_DP", B), ("FACE_USB_DN", B),
   ("3V3_SB", I), ("3V3_BP", I)]),
 ("Face S (secondary) AUX link", "face_aux.kicad_sch", None, None),
 ("CPU board link (J1 CPU-LINK card edge)", "cpu_link.kicad_sch", [
   "J1: Amphenol Mini Cool Edge 224 (ME1022410103011) vertical SMT; MP62 hub pinout (docs/cpulink_224_pinout_draft.csv)",
   "PCIe HUB: J1 x16 -> J9 MCIO 124 (Face P), J1 x4 -> J10 MCIO 124 (Face S), REFCLK P/S; 85 ohm L1 (TX) / L6 (RX)",
   "Optional Gen5 build: U10-U13 (Face P) + U14 (Face S) TI DS320PR810 linear redrivers + 220 nF output AC caps",
   "Gen4 build: no redrivers, no AC caps on BP (host-TX caps on module/CPU board, device-TX caps on face)",
   "Also carries: COM-HPC power/state sideband, fan PWMOUT/TACHIN, SMBus, USB2 x4, SATA0, 5V_SBY x6, 3V3_SB x2, GND x80",
   "BP makes PERST#_x = PLTRST# AND FACE_x_RDY (MCU asserts after FACE_x_PWR_GOOD); CLKREQ#_x end on BP; WAKE#_x ORed to WAKE0#",
   "12 V main for the COM-HPC module does NOT pass through J1 (bus bars or EPS-style input on the CPU board)"],
  [("5V_SBY", O), ("3V3_SB", O), ("MOD_PWRBTN_N", I), ("MOD_SUS_S3_N", O), ("MOD_SUS_S5_N", O), ("MOD_RSMRST_N", O),
   ("MOD_VIN_PWR_OK", I), ("MOD_PLTRST_N", O), ("MOD_THERMTRIP_N", O), ("MOD_CARRIER_HOT_N", I), ("MOD_FAN_PWMOUT", O),
   ("MOD_FAN_TACHIN", I), ("MOD_SMB_SCL", B), ("MOD_SMB_SDA", B), ("FACE_P_RDY", I), ("FACE_S_RDY", I),
   ("USB_MCU_DP", B), ("USB_MCU_DN", B), ("FACE_P_USB_DP", B), ("FACE_P_USB_DN", B), ("FACE_S_USB_DP", B), ("FACE_S_USB_DN", B),
   ("SATA0_TX_P", O), ("SATA0_TX_N", O), ("SATA0_RX_P", I), ("SATA0_RX_N", I)]),
 ("I/O board low-speed link", "iob_link.kicad_sch", [
   "J6 JST GH 15P to the new I/O board (designed later): power button, dual Hall interlock, LED/illumination I2C",
   "3V3_SB supply for the IOB Hall sensors and button; no high-speed signals on this link",
   "IOB high-speed (USB3, DP/HDMI, MDI, audio USB) runs CPU board -> IOB directly (TBD with IOB design)"],
  [("PWRBTN_IN_N", O), ("IOB_HALL_A_N", O), ("IOB_HALL_B_N", O), ("I2C_SYS_SCL", B), ("I2C_SYS_SDA", B), ("3V3_SB", I)]),
 ("OpenCore boot M.2 (SATA)", "m2_boot.kicad_sch", [
   "J7 M.2 M-key socket wired SATA-only (accepts B+M SATA 2242/2230 cards); dedicated OpenCore device",
   "Set as the default UEFI boot entry (LauncherOption=Full); removable-path fallback on the same ESP",
   "SATA0 from the COM-HPC module via J1 (ccAS has 2 x SATA)"],
  [("SATA0_TX_P", I), ("SATA0_TX_N", I), ("SATA0_RX_P", O), ("SATA0_RX_N", O), ("3V3_BP", I)]),
]
FACE_DESC = [
  "J3 (Face P) / J4 (Face S): JST GH 14P low-speed AUX cable BP -> face module",
  "FACE_PWR_EN / FACE_PWR_GOOD, PRSNT#, SMBus (ID EEPROM 0x50, LM75 0x48), THERM_ALERT#, THERM_TRIP#, USB2, 3V3_AUX",
  "3V3_AUX: load switch from 3V3_SB (S5, <=50 mW) / 3V3_BP (S0, <=3.3 W); SMBus isolated until FACE_PWR_GOOD",
  "Face main 12 V: bus bar / lug (not on this cable). PCIe + REFCLK + PERST# + CLKREQ# + WAKE#: MCIO from CPU board"]
SHEETS[3] = (SHEETS[3][0], SHEETS[3][1], FACE_DESC, SHEETS[3][3])
SHEETS[4] = (SHEETS[4][0], SHEETS[4][1], FACE_DESC, SHEETS[3][3])
PREFIX = {3: "FACE_P_", 4: "FACE_S_"}

def top_net(idx, pin):
    if idx in PREFIX and pin.startswith("FACE_"):
        return PREFIX[idx] + pin[len("FACE_"):]
    return pin

def text(s, x, y, size=1.27):
    s = s.replace('"', "'")
    return f'\t(text "{s}"\n\t\t(exclude_from_sim no)\n\t\t(at {x:.2f} {y:.2f} 0)\n\t\t(effects (font (size {size} {size})) (justify left bottom))\n\t\t(uuid "{U()}")\n\t)\n'

# ---------- sub-sheet stub files ----------
written = set()
for idx, (name, fname, desc, pins) in enumerate(SHEETS):
    if fname in written:
        continue
    written.add(fname)
    s = f'(kicad_sch\n\t{VER}\n\t(uuid "{U()}")\n\t(paper "A4")\n'
    s += f'\t(title_block\n\t\t(title "MP62 backplane: {name if fname != "face_aux.kicad_sch" else "Face AUX link (instanced for Face P and Face S)"}")\n\t\t(date "2026-10-01")\n\t\t(rev "A-bd1")\n\t\t(comment 1 "Block stub: hierarchical labels only, circuit TBD")\n\t)\n\t(lib_symbols)\n'
    y = 30.48
    for (pn, pt) in pins:
        s += f'\t(hierarchical_label "{pn}"\n\t\t(shape {pt})\n\t\t(at 38.1 {y:.2f} 180)\n\t\t{F} (justify right))\n\t\t(uuid "{U()}")\n\t)\n'
        y += 2.54
    s += text("BLOCK STUB (rev A block diagram). Contents planned:", 76.2, 30.48, 1.5)
    for i, d in enumerate(desc):
        s += text("- " + d, 76.2, 35.56 + i * 3.81)
    s += ')\n'
    open(os.path.join(PRJ, fname), "w").write(s)

# ---------- root sheet ----------
s = f'(kicad_sch\n\t{VER}\n\t(uuid "{ROOT_UUID}")\n\t(paper "A2")\n'
s += '\t(title_block\n\t\t(title "MacPro6,2 Backplane (BP) - top-level block diagram")\n\t\t(date "2026-10-01")\n\t\t(rev "A-bd1")\n\t\t(company "MacPro6,2 / Aidan Winkler")\n'
s += '\t\t(comment 1 "HUB topology: CPU board card edge J1 (Mini Cool Edge 224) -> BP -> J9/J10 MCIO 124 -> Face P x16 / Face S x4")\n\t\t(comment 2 "See macpro62-architecture-spec-v0.2.md sections 3-5")\n\t)\n\t(lib_symbols)\n'
s += text("MP62 BACKPLANE rev A - BLOCK DIAGRAM. Sheets are stubs (labels only). Nets with the same label name are connected.", 25.4, 20.32, 2.0)
s += text("Off-board links: J1 CPU-LINK (card edge from CPU board) | J2 PSU-IN | J3/J4 Face P/S AUX | J5 FAN | J6 IOB-LINK | J7 M.2 OpenCore | J8 SWD | J9/J10 MCIO 124 to Face P/S (PCIe hub)", 25.4, 25.4, 1.6)
W = 60.96
cols = [(38.1, 38.1), (165.1, 38.1), (292.1, 38.1), (38.1, 200.66), (165.1, 200.66), (292.1, 200.66), (419.1, 38.1), (419.1, 200.66)]
page = 2
for idx, (name, fname, desc, pins) in enumerate(SHEETS):
    x, y = cols[idx]
    h = g(5.08 + 2.54 * len(pins))
    s += f'\t(sheet\n\t\t(at {x:.2f} {y:.2f})\n\t\t(size {W:.2f} {h:.2f})\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n'
    s += '\t\t(stroke (width 0.1524) (type solid))\n\t\t(fill (color 0 0 0 0.0000))\n'
    s += f'\t\t(uuid "{U()}")\n'
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
