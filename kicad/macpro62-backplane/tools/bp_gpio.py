"""RP2350B GPIO re-assignment by escape direction (rev A1 congestion fix).
Each GPIO net gets the U1 pin that faces where the net goes: cost = mean distance from (pin + 2 mm outward) to the net's
targets (fixed connector/IC pads; targets north of the J1 row are mapped to the W/E corridor ends; non-MCU-cluster parts
-> their cluster centre). Constraints kept from rev A: I2C pairs SDA = even GPIO, SCL = SDA+1, same controller parity
(I2C_SYS + FP_SMB on GPIO%4==0 = I2C0, CB_I2C0 + FS_SMB on GPIO%4==2 = I2C1); CB_UART0 TX on GPIO%4==0 (UART0/1 TX), RX = TX+1.
  python3 tools/bp_gpio.py [board_with_U1_and_fixed_parts]  -> tools/gpio_map.json (read by bp_model.py)"""
import sys, os, json, math, collections
import numpy as np
from scipy.optimize import linear_sum_assignment
import pcbnew
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ["BP_GPIO_DEFAULT"] = "1"
import bp_model as M
from build_bp import MANUAL, FIXED, CLUSTERS, cluster_of
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "work", "bp_routed_r3.kicad_pcb")
b = pcbnew.LoadBoard(src)
CX, CY = 150.0, 100.0
def D(v): return (pcbnew.ToMM(v.x) - CX, CY - pcbnew.ToMM(v.y))
FPs = {f.GetReference(): f for f in b.GetFootprints()}
u1 = FPs["U1"]; uc = D(u1.GetPosition())
gpio_pin = {}   # gpio -> (pin number, pos, outward)
for k, v in M.RP.items():
    if v.startswith("GPIO"):
        g = int(v[4:].split("_")[0]); p = u1.FindPadByNumber(str(k)); pos = D(p.GetPosition())
        dx, dy = pos[0] - uc[0], pos[1] - uc[1]
        out = (1.0, 0.0) if abs(dx) > abs(dy) and dx > 0 else (-1.0, 0.0) if abs(dx) > abs(dy) else (0.0, 1.0) if dy > 0 else (0.0, -1.0)
        gpio_pin[g] = (k, pos, out)
GP0 = dict(M.GP)   # default (rev A) map gpio -> net
nets = list(GP0.values())
parts_by_net = collections.defaultdict(list)
for p in M.PARTS:
    for pin, n in p["nets"].items(): parts_by_net[n].append((p, pin))
def corridor(pt):
    if pt[1] > -12.0: return (-45.0, -14.0) if pt[0] < 0 else (45.0, -14.0)
    return pt
def targets(n):
    T = []
    for p, pin in parts_by_net[n]:
        r = p["ref"]
        if r == "U1": continue
        if r in FIXED or r in MANUAL:
            f = FPs.get(r)
            if f is None: continue
            pd = f.FindPadByNumber(pin)
            if pd: T.append(corridor(D(pd.GetPosition())))
        else:
            c = cluster_of(p)
            if c != "mcu":
                x0, x1, y0, y1 = CLUSTERS[c]; T.append(((x0 + x1) / 2, (y0 + y1) / 2))
    return T
TG = {n: targets(n) for n in nets}
def cost(g, n):
    k, pos, out = gpio_pin[g]; q = (pos[0] + 2 * out[0], pos[1] + 2 * out[1])
    T = TG[n]
    if not T: return 0.0
    return sum(math.hypot(q[0] - t[0], q[1] - t[1]) for t in T) / len(T)
PAIRS = [("I2C_SYS_SDA", "I2C_SYS_SCL", 0), ("FP_SMB_SDA", "FP_SMB_SCL", 0), ("CB_I2C0_SDA", "CB_I2C0_SCL", 2), ("FS_SMB_SDA", "FS_SMB_SCL", 2),
         ("CB_UART0_TX", "CB_UART0_RX", 0)]
free = set(gpio_pin); assign = {}
# pairs: pick by regret (best - second best slot) order
def slots(par):
    return [g for g in sorted(free) if g % 4 == par and g + 1 in free and abs(gpio_pin[g][0] - gpio_pin[g + 1][0]) == 1]
todo = list(PAIRS)
while todo:
    best = None
    for (a, c, par) in todo:
        cs = sorted((cost(g, a) + cost(g + 1, c), g) for g in slots(par))
        reg = (cs[1][0] - cs[0][0]) if len(cs) > 1 else 1e9
        if best is None or reg > best[0]: best = (reg, (a, c, par), cs[0][1])
    _, pr, g = best; assign[g] = pr[0]; assign[g + 1] = pr[1]; free -= {g, g + 1}; todo.remove(pr)
pairnets = {x for a, c, _ in PAIRS for x in (a, c)}
singles = [n for n in nets if n not in pairnets]
gl = sorted(free)
Cm = np.array([[cost(g, n) for g in gl] for n in singles])
ri, ci = linear_sum_assignment(Cm)
for r, c in zip(ri, ci): assign[gl[c]] = singles[r]
assert len(assign) == len(GP0) and set(assign.values()) == set(nets)
tot0 = sum(cost(g, n) for g, n in GP0.items()); tot1 = sum(cost(g, n) for g, n in assign.items())
json.dump({str(g): assign[g] for g in sorted(assign)}, open(os.path.join(HERE, "gpio_map.json"), "w"), indent=1)
side = lambda g: {(1, 0): "E", (-1, 0): "W", (0, 1): "N", (0, -1): "S"}[gpio_pin[g][2]]
print("total escape cost rev A %.0f -> A1 %.0f mm" % (tot0, tot1))
moved = sum(1 for g in assign if assign[g] != GP0[g])
print("re-assigned", moved, "of", len(assign))
for g in sorted(assign): print("GPIO%-2d pin %-2d %s %-18s (was %s)" % (g, gpio_pin[g][0], side(g), assign[g], GP0[g]))
