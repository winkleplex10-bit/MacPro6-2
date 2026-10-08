"""Impedance check of the as-routed BP A1 / SM-1 pair geometries on JLC04161H-7628 (1.6 mm 4L, 1 oz outer / 0.5 oz inner).
Bottom-up: L4 (gnd for L3 / sig for L4 breakouts), 7628 PP 0.2104 er 4.4, L3 0.0152, core 1.065 er 4.6, L2 GND 0.0152, 7628 PP 0.2104 er 4.4, L1 0.035 + mask."""
import sys, json
sys.path.insert(0, "tools")
from zsolve import solve
PP, CORE = (0.2104, 4.4, "diel"), (1.065, 4.6, "diel")
L1 = [(0.035, 1.0, "gnd"), PP, (0.035, 4.4, "sig")]                      # L1 over L2
L3 = [(0.035, 1.0, "gnd"), PP, (0.0152, 4.4, "sig"), CORE, (0.0152, 1.0, "gnd")]   # L3 between L4 (near) and L2 (far)
L4 = [(0.035, 1.0, "gnd"), PP, (0.035, 4.4, "sig")]                      # L4 breakouts over L3 GND (symmetric to L1)
cases = [("L1 PCIe RX 85R", L1, 0.26, 0.125), ("L3 PCIe TX 85R", L3, 0.21, 0.127), ("L4 RX0/breakout 85R", L4, 0.26, 0.125),
         ("L1 USB2/SATA 90R", L1, 0.24, 0.15)]
res = []
for nm, st, w, s in cases:
    z, e = solve(st, w, s, 0, h_step=0.005, xpad=1.5)
    res.append(dict(case=nm, w=w, gap=s, zdiff=round(float(z), 1), eeff=round(float(e), 2))); print(res[-1], flush=True)
json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else "docs/impedance_A1.json", "w"), indent=1)
