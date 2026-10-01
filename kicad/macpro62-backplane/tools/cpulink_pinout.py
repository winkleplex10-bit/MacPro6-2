#!/usr/bin/env python3
"""MP62 CPU-LINK (hub) pinout draft for Amphenol Mini Cool Edge 224 (ME1022410103011).
Positions A1..A112 / B1..B112; 4 bays x 28 per side; A1 at the +x end of the BP footprint.
Side A row (toward disc +y) = host TX (CPU board -> BP) routed on BP L1; side B = host RX, BP L6.
Bays 1-3: GND-S-S repeating (G at k = 1,4,...,28 within each bay) => 9 diff pairs per bay side."""
import csv, collections, os
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "cpulink_224_pinout_draft.csv")
def bay_pairs(names):
    assert len(names) == 9
    pins = []
    for k in range(28):
        if k % 3 == 0: pins.append("GND")
        else:
            p = names[k // 3]
            pins.append(p + ("_P" if k % 3 == 1 else "_N") if p != "GND" else "GND")
    return pins
# Face P: lane 15 at the outer (+x) end, lane 0 innermost (order-preserving toward J9).
A = (bay_pairs(["FP_PET%d" % l for l in range(15, 6, -1)]) +
     bay_pairs(["FP_PET%d" % l for l in range(6, -1, -1)] + ["FP_REFCLK", "RSVD_REFCLK2"]) +
     bay_pairs(["FS_PET%d" % l for l in range(0, 4)] + ["FS_REFCLK", "SATA0_TX", "RSVD_HS_A1", "RSVD_HS_A2", "GND"]))
B = (bay_pairs(["FP_PER%d" % l for l in range(15, 6, -1)]) +
     bay_pairs(["FP_PER%d" % l for l in range(6, -1, -1)] + ["USB2_FACEP", "RSVD_HS_B1"]) +
     bay_pairs(["FS_PER%d" % l for l in range(0, 4)] + ["SATA0_RX", "USB2_MCU", "USB2_FACES", "USB2_SPARE", "RSVD_HS_B2"]))
lsA = ["PWRBTN#", "RSTBTN#", "SUS_S3#", "SUS_S4_S5#", "RSMRST_OUT#", "VIN_PWR_OK", "PLTRST#", "THERMTRIP#",
       "CARRIER_HOT#", "WAKE0#", "BIOS_SEL", "GPIO0", "GPIO1", "RSVD_LS1", "5V_SBY", "5V_SBY", "5V_SBY", "5V_SBY"]
lsB = ["SMB_CLK", "SMB_DAT", "SMB_ALERT#", "I2C0_CLK", "I2C0_DAT", "UART0_TX", "UART0_RX", "FAN_PWMOUT", "FAN_TACHIN",
       "GPIO2", "GPIO3", "RSVD_LS2", "RSVD_LS3", "RSVD_LS4", "3V3_SB", "3V3_SB", "5V_SBY", "5V_SBY"]
def ls_bay(lst):
    it = iter(lst); return ["GND" if k % 3 == 0 else next(it) for k in range(28)]
A += ls_bay(lsA); B += ls_bay(lsB)
A[0] = "CC_PRSNT1#"; A[111] = "CC_PRSNT2#"      # end positions: short (last-mate) fingers on the card, tied to GND there
assert len(A) == 112 and len(B) == 112
rows = []
for i in range(112):
    bay = i // 28 + 1
    rows.append(("A%d" % (i + 1), bay, A[i])); rows.append(("B%d" % (i + 1), bay, B[i]))
with open(OUT, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["pin", "bay", "signal"]); w.writerows(rows)
cnt = collections.Counter()
for _, _, s in rows:
    if s == "GND": cnt["GND"] += 1
    elif s.startswith(("FP_PE", "FS_PE")): cnt["PCIe lane pins"] += 1
    elif "REFCLK" in s and not s.startswith("RSVD"): cnt["REFCLK pins"] += 1
    elif s.startswith("SATA"): cnt["SATA pins"] += 1
    elif s.startswith("USB2"): cnt["USB2 pins"] += 1
    elif s.startswith("RSVD"): cnt["reserved pins"] += 1
    elif s in ("5V_SBY", "3V3_SB"): cnt[s] += 1
    else: cnt["low-speed/sideband"] += 1
print(dict(cnt), sum(cnt.values()))
