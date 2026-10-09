"""BP v3: generate bp_pair2 JSON specs for the slot B pairs from the board's pad positions.
usage: python3 tools/v3_specs.py BOARD OUTDIR
J1 P/N per contact pair is free (CPU-LINK v3 is a new pinout): "P" = the pad on the right-hand side of the initial travel
direction; the chosen J1 polarity is written to OUTDIR/j1_polarity.json (feeds the CSV / ICD v3). J10 polarity is fixed
(S2X module end)."""
import sys, json, math, pcbnew, os
b = pcbnew.LoadBoard(sys.argv[1]); OUT = sys.argv[2]
mm = pcbnew.ToMM
fp = {f.GetReference(): f for f in b.GetFootprints()}
def pad(ref, n):
    p = [q for q in fp[ref].Pads() if q.GetNumber() == n][0]; return (round(mm(p.GetPosition().x), 4), round(mm(p.GetPosition().y), 4))
r = (0.7071068, -0.7071068); u = (0.7071068, 0.7071068)   # J10 row direction (A1 -> A62), outer -> inner (SE)
def R(v): return [round(v[0], 4), round(v[1], 4)]
SFT = {"L1": 0.1925, "L3": 0.1685, "L4": 0.1925}; W = {"L1": 0.26, "L3": 0.21, "L4": 0.26}
if os.environ.get("BP6") == "1":   # 6L JLC06161H-2116: inner pairs 0.24/0.127
    SFT.update(L3=0.1835, LX=0.1835); W.update(L3=0.24, LX=0.24)
# ---------------- J10 ends ----------------
def j10_outer_L1(pP, pN, Lb=1.2):
    M = ((pP[0] + pN[0]) / 2, (pP[1] + pN[1]) / 2); s = SFT["L1"]; t = 0.3 - s
    def pt(a, c): return R((M[0] + u[0] * a + r[0] * c, M[1] + u[1] * a + r[1] * c))
    return {"c": pt(-Lb, 0), "L": ["L1"], "dir": [1, 1], "tail": 0.6,
            "post": {"P": [["t", "L1", [pt(-Lb, -s), pt(-Lb + t, -0.3), list(pP)], 0.26]], "N": [["t", "L1", [pt(-Lb, s), pt(-Lb + t, 0.3), list(pN)], 0.26]]}}
def j10_between(n, row, layer="L4", back=0.9):
    """pins n (P) / n+1 (N): L4 pair heading SE under the A row -> between-row vias -> L1 stub to the row's pads."""
    A0, A1_ = pad("J10", "A%d" % n), pad("J10", "A%d" % (n + 1)); B0, B1_ = pad("J10", "B%d" % n), pad("J10", "B%d" % (n + 1))
    vP = R(((A0[0] + B0[0]) / 2, (A0[1] + B0[1]) / 2)); vN = R(((A1_[0] + B1_[0]) / 2, (A1_[1] + B1_[1]) / 2))
    M = ((vP[0] + vN[0]) / 2, (vP[1] + vN[1]) / 2); s = SFT[layer]
    def pt(a, c): return R((M[0] + u[0] * a + r[0] * c, M[1] + u[1] * a + r[1] * c))
    tP, tN = (B0, B1_) if row == "B" else (A0, A1_)
    return {"c": pt(-back, 0), "L": [layer], "dir": [1, 1], "tail": 0.5, "rel": 0.5,
            "post": {"P": [["t", layer, [pt(-back, -s), pt(-back + 0.25, -s), vP], W[layer]], ["v", vP], ["t", "L1", [vP, list(tP)], 0.2]],
                     "N": [["t", layer, [pt(-back, s), pt(-back + 0.25, s), vN], W[layer]], ["v", vN], ["t", "L1", [vN, list(tN)], 0.2]]}}
# ---------------- J1 starts (returns start dict + polarity: right-hand pad = P) ----------------
def j1_north(pe, pw):          # B-row pair escaping north on L1 (right of north = east)
    xm = (pe[0] + pw[0]) / 2; y = pe[1]; s = SFT["L1"]; ys = y - 0.775; t = 0.3 - s
    return {"c": [xm, round(ys - t, 4)], "L": "L1", "dir": [0, -1], "lead": 0.3,
            "pre": {"P": [["t", "L1", [list(pe), [pe[0], ys], [round(xm + s, 4), round(ys - t, 4)]], 0.26]],
                    "N": [["t", "L1", [list(pw), [pw[0], ys], [round(xm - s, 4), round(ys - t, 4)]], 0.26]]}}, (pe, pw)
def j1_gap_south(pe, pw):      # B-row pair dropping south into the J1 row gap on L1 (right of south = west)
    xm = (pe[0] + pw[0]) / 2; y = pe[1]; s = SFT["L1"]; ys = y + 0.62; t = 0.3 - s
    return {"c": [xm, round(ys + t, 4)], "L": "L1", "dir": [0, 1], "lead": 0.1, "rel": 0.5,
            "pre": {"P": [["t", "L1", [list(pw), [pw[0], ys], [round(xm - s, 4), round(ys + t, 4)]], 0.26]],
                    "N": [["t", "L1", [list(pe), [pe[0], ys], [round(xm + s, 4), round(ys + t, 4)]], 0.26]]}}, (pw, pe)
def j1_north_via(pe, pw, vy=109.9):   # B-row pair: L1 stub north to vias, L3 heading SOUTH from the vias (right = west)
    xm = (pe[0] + pw[0]) / 2; s = SFT["L3"]
    return {"c": [xm, round(vy + 0.15, 4)], "L": "L3", "dir": [0, 1], "lead": 0.35, "rel": 0.45,
            "pre": {"P": [["t", "L1", [list(pw), [pw[0], vy]], 0.2], ["v", [pw[0], vy]], ["t", "L3", [[pw[0], vy], [round(xm - s, 4), round(vy + 0.15, 4)]], W["L3"]]],
                    "N": [["t", "L1", [list(pe), [pe[0], vy]], 0.2], ["v", [pe[0], vy]], ["t", "L3", [[pe[0], vy], [round(xm + s, 4), round(vy + 0.15, 4)]], W["L3"]]]}}, (pw, pe)
def j1_north_via_n(pe, pw, vy=109.9):   # B-row pair: L1 stub north to vias, L3 heading NORTH from the vias (right = east)
    xm = (pe[0] + pw[0]) / 2; s = SFT["L3"]
    return {"c": [xm, round(vy - 0.15, 4)], "L": "L3", "dir": [0, -1], "lead": 0.35, "rel": 0.45,
            "pre": {"P": [["t", "L1", [list(pe), [pe[0], vy]], 0.2], ["v", [pe[0], vy]], ["t", "L3", [[pe[0], vy], [round(xm + s, 4), round(vy - 0.15, 4)]], W["L3"]]],
                    "N": [["t", "L1", [list(pw), [pw[0], vy]], 0.2], ["v", [pw[0], vy]], ["t", "L3", [[pw[0], vy], [round(xm - s, 4), round(vy - 0.15, 4)]], W["L3"]]]}}, (pe, pw)
def j1_south_via(pe, pw, vy=115.4):   # A-row pair: L1 stub south to vias, L3 heading NORTH from the vias (right = east)
    xm = (pe[0] + pw[0]) / 2; s = SFT["L3"]
    return {"c": [xm, round(vy - 0.15, 4)], "L": "L3", "dir": [0, -1], "lead": 0.35, "rel": 0.45,
            "pre": {"P": [["t", "L1", [list(pe), [pe[0], vy]], 0.15], ["v", [pe[0], vy]], ["t", "L3", [[pe[0], vy], [round(xm + s, 4), round(vy - 0.15, 4)]], W["L3"]]],
                    "N": [["t", "L1", [list(pw), [pw[0], vy]], 0.15], ["v", [pw[0], vy]], ["t", "L3", [[pw[0], vy], [round(xm - s, 4), round(vy - 0.15, 4)]], W["L3"]]]}}, (pe, pw)
def j1_gap_via(pe, pw, vy=112.95, dx=-0.65, layer="L4"):   # A-row pair: L1 stub NW into the J1 row gap, vias, inner layer heading NORTH (right = east)
    """lane 7 TX: the A-row south via sites are taken by USB2_FACEP_N (B.Cu, x 152.9), so drop in the row gap instead."""
    xm = (pe[0] + pw[0]) / 2 + dx; s = SFT[layer]; vP = [round(pe[0] + dx, 4), vy]; vN = [round(pw[0] + dx, 4), vy]
    return {"c": [round(xm, 4), round(vy - 0.15, 4)], "L": layer, "dir": [0, -1], "lead": 0.2, "rel": 0.45,
            "pre": {"P": [["t", "L1", [list(pe), [pe[0], round(pe[1] - 0.6, 4)], vP], 0.15], ["v", vP], ["t", layer, [vP, [round(xm + s, 4), round(vy - 0.15, 4)]], W[layer]]],
                    "N": [["t", "L1", [list(pw), [pw[0], round(pw[1] - 0.6, 4)], vN], 0.15], ["v", vN], ["t", layer, [vN, [round(xm - s, 4), round(vy - 0.15, 4)]], W[layer]]]}}, (pe, pw)
def j1_gap_via2(pe, pw, layer="L4"):   # lane 7 TX v2: P via NW of the P pad, N via over the A56 side; L1 stubs clear USB2_FACEP_N's via (152.91,112.6) by >= 0.3
    s = SFT[layer]; vP = [round(pw[0] - 0.20, 4), 112.4]; vN = [round(pw[0] - 0.80, 4), 113.0]; c = [round(vP[0] - s, 4), 112.0]
    return {"c": c, "L": layer, "dir": [0, -1], "lead": 0.2, "rel": 0.4,
            "pre": {"P": [["t", "L1", [list(pe), [pe[0], round(pe[1] - 0.6, 4)], [round(pe[0] - 0.25, 4), round(pe[1] - 0.85, 4)], [vP[0], round(vP[1] + 0.225, 4)], vP], 0.15],
                          ["v", vP], ["t", layer, [vP, [vP[0], c[1]]], W[layer]]],
                    "N": [["t", "L1", [list(pw), [pw[0], round(pw[1] - 0.6, 4)], vN], 0.15], ["v", vN],
                          ["t", layer, [vN, [vN[0], round(c[1] + 0.2, 4)], [round(c[0] - s, 4), c[1]]], W[layer]]]}}, (pe, pw)
def J1(a, c):   # east, west pad of a J1 contact pair
    pa, pc = pad("J1", a), pad("J1", c); return (pa, pc) if pa[0] > pc[0] else (pc, pa)
num = {}
for p in fp["J1"].Pads(): num[(round(mm(p.GetPosition().x), 4), round(mm(p.GetPosition().y), 4))] = p.GetNumber()
PAIRS = {   # name: (J1 contacts, start kind, J10 end)
 "rx4": (("B82", "B83"), j1_north, ("outer", "A20")),
 "rx6": (("B104", "B105"), j1_gap_south, ("outer", "A32")),
 "clk": (("B101", "B102"), j1_north_via_n if os.environ.get("BP6") == "1" else j1_north_via, ("between", 29, "A")),
 "rx5": (("B86", "B87"), j1_north_via, ("outer", "A23")),
 "tx4": (("A82", "A83"), j1_south_via, ("between", 20, "B")),
 "tx5": (("A86", "A87"), j1_south_via, ("between", 23, "B")),
 "tx6": (("A101", "A102"), j1_south_via, ("between", 32, "B")),
 "rx7": (("B54", "B55"), j1_north_via_n if os.environ.get("BP6") == "1" else j1_north_via, ("outer", "A35")),
 "tx7": (("A54", "A55"), (lambda pe, pw: j1_gap_via2(pe, pw, layer=os.environ.get("TX7L", "L4"))) if os.environ.get("BP6") == "1" else j1_south_via, ("between", 35, "B")),
}
NET = {"rx7": "FS_RX7", "tx7": "FS_TX7", "rx4": "FS_RX4", "rx5": "FS_RX5", "rx6": "FS_RX6", "clk": "FS_REFCLK1", "tx4": "FS_TX4", "tx5": "FS_TX5", "tx6": "FS_TX6"}
POL = {}
ENDL = json.loads(os.environ.get("ENDL", "{}"))   # BP6: per-pair J10 between-row landing layer, e.g. {"clk":"LX"}
only = sys.argv[3:] or list(PAIRS)
for nm, (cts, kind, end) in PAIRS.items():
    if nm not in only: continue
    pe, pw = J1(*cts); st, (pP, pN) = kind(pe, pw)
    POL[NET[nm]] = {"P": num[pP], "N": num[pN]}
    if end[0] == "outer":
        n0 = int(end[1][1:]); en = j10_outer_L1(pad("J10", end[1]), pad("J10", "A%d" % (n0 + 1)))
    else: en = j10_between(end[1], end[2], ENDL.get(nm, "L4"))
    spec = {"P": NET[nm] + "_P", "N": NET[nm] + "_N", "reg": [100, 157 if nm in ("rx7", "tx7") else 141, 82, 121], "start": st, "end": en,
            "lays": ["L1"] if nm == "rx4" else (["L1", "L3", "LX", "L4"] if os.environ.get("BP6") == "1" else ["L1", "L3", "L4"])}
    fn = os.path.join(OUT, nm + ".json")
    if os.path.exists(fn):
        old = json.load(open(fn)); spec["block"] = old.get("block", [])
        if os.environ.get("BP6") == "1": spec["block"] = []   # 4L-era blocks dropped for the 6L reroute
        for k in ("lays", "reg", "hsx", "viac"):
            if k in old and k != "lays": spec[k] = old[k]
    json.dump(spec, open(fn, "w"), indent=1); print(nm, POL[NET[nm]], "->", fn)
pf = os.path.join(OUT, "j1_polarity.json"); old = json.load(open(pf)) if os.path.exists(pf) else {}
old.update(POL); json.dump(old, open(pf, "w"), indent=1)
