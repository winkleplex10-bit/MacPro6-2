"""v3: docs/cpulink_224_pinout_am5_v3.csv = AM5 CPU-LINK map re-pinned to CPU-LINK v3 (Ryzen 7000/9000).
Reads docs/cpulink_224_pinout_am5.csv (v1 AM5 map, unchanged) + ../macpro62-backplane-v3/docs/cpulink_224_pinout_draft.csv (CPU-LINK v3 signals)."""
import csv, os, re
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
v1 = list(csv.DictReader(open(os.path.join(PRJ, "docs/cpulink_224_pinout_am5.csv"))))
bp = {r["pin"]: r["signal"] for r in csv.DictReader(open(os.path.join(PRJ, "../macpro62-backplane-v3/docs/cpulink_224_pinout_draft.csv")))}
K = "cb_net_am5 (Ryzen 8000G + PROM21 CB, DRAFT)"
out = []
def src(sig, old):
    m = re.match(r"FS_PE([TR])([4-7])_([PN])$", sig)
    if m:
        ln = int(m.group(2))
        return ("CPU PCIe GPP#2 x4 (Gen4) lane %d %s -> Face S slot B (J10 lane %d)%s" % (ln - 4, "TX (AC caps on the CB)" if m.group(1) == "T" else "RX", ln,
                ""), "NEW v3 (slot B)")
    if sig.startswith("FS_REFCLK1"): return "CPU (FCH) GPP_CLK output for GPP#2 (slot B), index TBD; CLKREQ1#/PERST1#/WAKE1# handled on the BP", "NEW v3 (slot B)"
    m = re.match(r"FP_PE([TR])(\d+)_", sig)
    if m: return "CPU PCIe GFX x16 (Gen5 on 7000/9000) lane %s %s -> Face P" % (m.group(2), "TX (AC caps on the CB)" if m.group(1) == "T" else "RX"), "REMAP (live x16)"
    if sig == "PWRBTN#": return "EC GPIO in -> EC drives FCH PWR_BTN_L (moved pin in v3)", "MOVED v3"
    if sig == "RSTBTN#": return "EC GPIO in -> FCH SYS_RESET_L (moved pin in v3)", "MOVED v3"
    if sig == "BIOS_SEL": return "EC GPIO in (optional dual-image select) (moved pin in v3)", "MOVED v3"
    return None
for r in v1:
    pin = r["pin"]; sig = bp[pin]; n = dict(r)
    if sig != r["signal"] or sig.startswith("FP_PE") or sig.startswith(("FS_REFCLK1",)):
        s = src(sig, r)
        if s: n[K], n["delta_vs_ICD"] = s
        if sig != r["signal"]:
            n["delta_vs_ICD"] = n["delta_vs_ICD"] + " (was %s)" % r["signal"]
            n["dir_cb_view"] = "out" if re.match(r"FS_PET|FS_REFCLK1", sig) else "in" if sig.startswith("FS_PER") else r["dir_cb_view"]
        n["signal"] = sig
    out.append(n)
K3 = "cb_net_am5_v3 (Ryzen 7000/9000 + PROM21 CB, DRAFT)"
with open(os.path.join(PRJ, "docs/cpulink_224_pinout_am5_v3.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["pin", "bay", "signal", "cb_net_lga1700", K3, "dir_cb_view", "delta_vs_ICD_v1"])
    for n in out: w.writerow([n["pin"], n["bay"], n["signal"], n["cb_net_lga1700"], n[K], n["dir_cb_view"], n["delta_vs_ICD"]])
ch = [n for n, r in zip(out, v1) if n["signal"] != r["signal"]]
print("v3 pins changed vs v1:", len(ch)); [print(" ", n["pin"], n["signal"], "<-", r["signal"]) for n, r in zip(out, v1) if n["signal"] != r["signal"]]
