#!/usr/bin/env python3
"""AM5 CB (draft) pinout DELTA against the ICD (macpro62-interface-control.md rev 3).
The CONNECTOR PHYSICALS and the SIGNAL NAMES at the contacts are unchanged (BP and IOB need no change);
only the CB-side source of each signal is re-mapped from LGA1700/Z790 to AM5 (Ryzen 8000G Phoenix + one PROM21).
Inputs (read-only): ../macpro62-lga1700/docs/cpulink_224_pinout_draft.csv, ../macpro62-lga1700/docs/mp62-cb-j3_mcio124_host-end.csv
Outputs: docs/cpulink_224_pinout_am5.csv, docs/mp62-cb-j3_mcio124_host-end_am5.csv, docs/pinout_delta_summary.txt"""
import csv, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.abspath(os.path.join(HERE, ".."))
LGA = os.path.abspath(os.path.join(PRJ, "..", "macpro62-lga1700", "docs"))

def cpulink(sig):
    m = re.match(r"FP_PE([TR])(\d+)_([PN])", sig)
    if m:
        n = int(m.group(2)); t = "TX (AC caps on the CB)" if m.group(1) == "T" else "RX"
        if n <= 7:
            return "CPU PCIe GFX lane %d %s; Ryzen 8000G = x8 Gen4 -> Face P" % (n, t), "REMAP"
        return "CPU PCIe GFX lane %d %s; ROUTED but not driven by Ryzen 8000G (x8); live with Ryzen 7000/9000 (x16, Gen5)" % (n, t), "REMAP (8000G: unused)"
    m = re.match(r"FS_PE([TR])(\d+)_([PN])", sig)
    if m:
        return "CPU PCIe GPP x4 (Gen4) lane %s %s -> Face S" % (m.group(2), "TX (AC caps on the CB)" if m.group(1) == "T" else "RX"), "REMAP"
    if sig.startswith("FP_REFCLK"): return "CPU (FCH) GPP_CLK output for the GFX x8/x16 link (index TBD) - CPU makes the 100 MHz refclks; no PCH CLKOUT", "REMAP (closes U-12 on AM5)"
    if sig.startswith("FS_REFCLK"): return "CPU (FCH) GPP_CLK output for the GPP x4 Face S link (index TBD)", "REMAP (closes U-12 on AM5)"
    if sig.startswith("SATA0"): return "PROM21 SATA port on a Gen3/SATA flex lane (lane TBD from the PROM21 ballout)", "REMAP"
    if sig.startswith("USB2_MCU"): return "PROM21 USB2 port (number TBD)", "REMAP"
    if sig.startswith("USB2_FACEP"): return "PROM21 USB2 port -> Face P AUX 13/14", "REMAP"
    if sig.startswith("USB2_FACES"): return "PROM21 USB2 port -> Face S AUX 13/14", "REMAP"
    if sig.startswith("USB2_SPARE"): return "CPU native USB2 port (8000G: 1) -> BP J6 13/14 -> IOB hub H2", "REMAP"
    T = {
     "PWRBTN#": ("EC GPIO in -> EC drives FCH PWR_BTN_L", "REMAP (name)"),
     "RSTBTN#": ("EC GPIO in -> FCH SYS_RESET_L", "REMAP (name)"),
     "SUS_S3#": ("FCH SLP_S3_L (buffered, 3V3_SB)", "REMAP (name)"),
     "SUS_S4_S5#": ("FCH SLP_S5_L (buffered; AM5 has no separate SLP_S4)", "REMAP (name)"),
     "SMB_CLK": ("FCH SMBus 0 (DDR5 SPD hub / PMIC bus): 0R DNP isolation on the CB by default (as LGA1700, O-4)", "REMAP (source)"),
     "SMB_DAT": ("FCH SMBus 0, as SMB_CLK", "REMAP (source)"),
     "SMB_ALERT#": ("FCH SMBus 0 ALERT (DNP with SMB_*)", "REMAP (source)"),
     "RSMRST_OUT#": ("copy of EC-driven FCH RSMRST_L", "REMAP (name)"),
     "PLTRST#": ("FCH PCIE_RST_L (buffered); BP makes PERST#_FP/FS = PLTRST# AND FACE_x_RDY", "REMAP (name)"),
     "THERMTRIP#": ("CPU THERMTRIP_L (OD) wired-OR with the PROM21 thermal trip (if any)", "REMAP (name)"),
     "CARRIER_HOT#": ("EC GPIO in -> CPU PROCHOT_L (OD) - LPT fast cap path unchanged", "REMAP (name)"),
     "WAKE0#": ("FCH WAKE_L (faces' WAKE# ORed on the BP)", "REMAP (name)"),
     "UART0_TX": ("EC UART TX (EC <-> BP MCU); LPT_SET semantics change: PPT/TDC/EDC instead of PL1/PL2 (plan sec. 9)", "SAME pin, NEW semantics"),
     "UART0_RX": ("EC UART RX", "SAME"),
    }
    if sig in T: return T[sig]
    return None, "SAME"

rows = list(csv.DictReader(open(os.path.join(LGA, "cpulink_224_pinout_draft.csv"))))
LCOL = "cb_net (LGA1700/Z790 CB)"
out = os.path.join(PRJ, "docs", "cpulink_224_pinout_am5.csv")
cnt = {}
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["pin", "bay", "signal", "cb_net_lga1700", "cb_net_am5 (Ryzen 8000G + PROM21 CB, DRAFT)", "dir_cb_view", "delta_vs_ICD"])
    for r in rows:
        a, d = cpulink(r["signal"])
        if a is None: a = r[LCOL]
        cnt[d] = cnt.get(d, 0) + 1
        w.writerow([r["pin"], r["bay"], r["signal"], r[LCOL], a, r["dir_cb_view"], d])
rep = ["CPU-LINK (I-1) AM5 delta: %d contacts, physical + signal names unchanged" % len(rows)] + ["  %-32s %d" % kv for kv in sorted(cnt.items())]

def j3(sig, notes):
    m = re.match(r"USB3_C(\d)_SS(TX|RX)_([PN])", sig)
    if m:
        c = int(m.group(1))
        src = "CPU native USB 3.2 Gen2 port %d" % (c - 1) if c <= 2 else "PROM21 USB 3.2 Gen2 port %d" % (c - 3)
        return "%s %s (USB-C C%d)" % (src, m.group(2), c), "REMAP"
    m = re.match(r"USB3_A(\d)_SS(TX|RX)_([PN])", sig)
    if m:
        a = int(m.group(1))
        return "U16 VL822-Q7 hub downstream port %d %s (USB-A A%d); hub upstream = PROM21 USB 10G port 4; A1-A4 share 10 Gb/s" % (a, m.group(2), a), "REMAP (NEW hub)"
    m = re.match(r"PCIE_I226(B?)_(TX|RX)_([PN])", sig)
    if m:
        return ("PROM21 PCIe Gen4 x1 (downstream lane TBD) %s -> %s" % (m.group(2), "IOB ASM1182e (i226 #2 + AirPort)" if m.group(1) else "IOB i226 #1")), "REMAP"
    m = re.match(r"DDI([BC])_(ML\d|AUX)_([PN])", sig)
    if m:
        dp = "DP0 (4-lane)" if m.group(1) == "B" else "DP1 (2 of 4 lanes)"
        return "APU display %s %s (AC caps on the CB); AM5 display pin names under NDA [Unverified]" % (dp, m.group(2)), "REMAP"
    T = {
     "HPD_B": ("APU DP0 HPD input (3.3 V from IOB PD #3; level/5V-tolerance TBD)", "REMAP"),
     "HPD_C": ("APU DP1 HPD input", "REMAP"),
     "I226_CLKREQ#": ("PROM21 downstream CLKREQ# for the i226 #1 port", "REMAP"),
     "I226B_CLKREQ#": ("PROM21 downstream CLKREQ# for the ASM1182e port", "REMAP"),
     "I226_WAKE#": ("FCH WAKE_L (wired-OR; no WoL in rev A)", "REMAP"),
     "I226_PERST#": ("PROM21 downstream PERST# (or FCH PCIE_RST_L buffer)", "REMAP"),
     "I226_REFCLK+": ("PROM21 downstream REFCLK out [Unverified: PROM21 refclk outputs]", "REMAP"),
     "I226_REFCLK-": ("PROM21 downstream REFCLK out", "REMAP"),
     "I226B_REFCLK+": ("PROM21 downstream REFCLK out #2", "REMAP"),
     "I226B_REFCLK-": ("PROM21 downstream REFCLK out #2", "REMAP"),
     "VBAT_RTC": ("IOB coin cell -> CB diode-OR with 3V3_S5 -> CPU (FCH) VBAT/RTC well; CB BT1 DNP", "REMAP (sink)"),
     "USB_OC#": ("PROM21 USB_OC0_L (pull-up on the CB)", "REMAP"),
     "USB2_HS1_DP": ("PROM21 USB2 port -> IOB hub H1a", "REMAP"),
     "USB2_HS1_DN": ("PROM21 USB2 port -> IOB hub H1a", "REMAP"),
    }
    if sig in T: return T[sig]
    return notes, "SAME"

rows = list(csv.DictReader(open(os.path.join(LGA, "mp62-cb-j3_mcio124_host-end.csv"))))
out2 = os.path.join(PRJ, "docs", "mp62-cb-j3_mcio124_host-end_am5.csv")
cnt = {}
with open(out2, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cb_contact", "iob_hs1_contact", "signal", "dir", "notes_lga1700", "cb_source_am5 (DRAFT)", "delta_vs_ICD"])
    for r in rows:
        a, d = j3(r["signal"], r["notes"])
        cnt[d] = cnt.get(d, 0) + 1
        w.writerow([r["cb_contact"], r["iob_hs1_contact"], r["signal"], r["dir"], r["notes"], a, d])
rep += ["", "IOB-HS1 J3 (I-2) AM5 delta: %d contacts, physical + signal names + IOB end unchanged" % len(rows)] + ["  %-32s %d" % kv for kv in sorted(cnt.items())]
open(os.path.join(PRJ, "docs", "pinout_delta_summary.txt"), "w").write("\n".join(rep) + "\n")
print("\n".join(rep))
