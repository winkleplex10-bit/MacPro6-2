"""BP v3: apply the CPU-LINK v3 / Face S slot B netlist (bp_model) to the ROUTED rev A1 board without rebuilding it.
usage: python3 tools/v3_apply.py SRC DST
 - J1 / J10 pad nets set from bp_model (only pads whose net changed); LS nets that moved pins (CB_PWRBTN_N A86 -> B99) are ripped
 - J1 A82/A83 (GND -> FS_TX6_P/N): the shared GND via under A82/A83 and the A81 stub to it are removed; A81 gets its own
   GND via south of the pad (same pattern as the other A-row GND pins)
 - new parts appended (R64 1k PLTRST->PERST1, Q12 2N7002 FS_HOLD clamp, R65 10k CLKREQ1 pull-up) placed at PLACE below"""
import re, sys, os, pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bp_model as M
SRC, DST = sys.argv[1], sys.argv[2]
MM = pcbnew.FromMM; mm = pcbnew.ToMM
PLACE = {"R64": (None, 0.0), "Q12": (None, 0.0), "R65": (None, 0.0)}   # (x, y) mm or None (= park off-board for later placement)
import json
if os.environ.get("PLACE"): PLACE.update({k: (tuple(v[0]) if v[0] else None, v[1]) for k, v in json.loads(os.environ["PLACE"]).items()})
b = pcbnew.LoadBoard(SRC)
fp = {f.GetReference(): f for f in b.GetFootprints()}
def net(n):
    ni = b.FindNet(n)
    if ni is None: ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni)
    return ni
P = {p["ref"]: p for p in M.PARTS}
ch = 0; RIPNET = set(); KEEP0 = []
for ref in ("J1", "J10"):
    for pad in fp[ref].Pads():
        want = P[ref]["nets"].get(pad.GetNumber())
        have = pad.GetNetname()
        if want and want != have:
            if have and not have.startswith("unconnected") and have != "GND" and not have.startswith(("FS_", "FP_", "USB2", "SATA")): RIPNET.add(have)
            pad.SetNet(net(want)); ch += 1
        elif not want and have and not have.startswith("unconnected"):
            if re.match(r"FS_(TX|RX)[67]_[PN]$", have):      # v3 x2 build: slot B lanes 6-7 NC on the BP
                pad.SetNet(b.FindNet("") or pcbnew.NETINFO_ITEM(b, "")); pad.SetNetCode(0); ch += 1; print("NC", ref, pad.GetNumber(), have)
            else: print("WARN model NC but board", ref, pad.GetNumber(), have)
print("pad nets changed", ch, "old LS nets ripped (re-route from the new pin with bp_fix):", sorted(RIPNET))
for t in list(b.GetTracks()):
    if t.GetNetname() in RIPNET:
        if t.IsLocked(): print("WARN locked item on ripped net", t.GetNetname())
        b.Remove(t); KEEP0.append(t)
# GND copper under J1 A82/A83
KEEP = []
def near(a, c, t=0.01): return abs(a[0] - c[0]) < t and abs(a[1] - c[1]) < t
def xy(v): return (round(mm(v.x), 3), round(mm(v.y), 3))
for t in list(b.GetTracks()):
    if t.GetNetname() != "GND": continue
    if t.Type() == pcbnew.PCB_VIA_T and near(xy(t.GetPosition()), (132.298, 114.105)): KEEP.append(t); b.Remove(t)
    elif t.Type() == pcbnew.PCB_TRACE_T and near(xy(t.GetStart()), (133.24, 114.025)) and near(xy(t.GetEnd()), (132.298, 114.105)): KEEP.append(t); b.Remove(t)
print("removed GND items", len(KEEP))
gnd = b.FindNet("GND")
A81V = (133.24, 114.97)
HAVE81 = any(t.Type() == pcbnew.PCB_VIA_T and near(xy(t.GetPosition()), A81V) for t in b.GetTracks())
if not HAVE81:
  tr = pcbnew.PCB_TRACK(b); tr.SetStart(pcbnew.VECTOR2I(MM(133.24), MM(114.025))); tr.SetEnd(pcbnew.VECTOR2I(MM(A81V[0]), MM(A81V[1])))
  tr.SetWidth(MM(0.15)); tr.SetLayer(pcbnew.F_Cu); tr.SetNet(gnd); tr.SetLocked(True); b.Add(tr)
  v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(A81V[0]), MM(A81V[1]))); v.SetWidth(MM(0.45)); v.SetDrill(MM(0.25)); v.SetNet(gnd); v.SetLocked(True); b.Add(v)
# new parts: clone footprint of an existing part of the same footprint id
TEMPL = {"MP62_BP:R_0402_1005Metric": "R32", "MP62_BP:SOT-23": "Q11"}
for ref in ("R64", "Q12", "R65"):
    if ref in fp: continue
    pm = P[ref]
    src = fp["R32" if ref.startswith("R") else "Q11"]
    f = pcbnew.FOOTPRINT(src); f.SetReference(ref); f.SetValue(pm["value"])
    for fld in ("LCSC", "MPN"):
        if f.HasField(fld) and pm.get(fld.lower()): f.SetField(fld, pm[fld.lower()])
    for pad in f.Pads(): pad.SetNet(net(pm["nets"][pad.GetNumber()]) if pad.GetNumber() in pm["nets"] else pcbnew.NETINFO_ITEM(b, ""))
    pos, rot = PLACE[ref]
    if pos is None: pos = (250.0 + 3 * len(fp), 20.0)
    f.SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1]))); f.SetOrientationDegrees(rot)
    f.SetPath(pcbnew.KIID_PATH()); b.Add(f); fp[ref] = f
    print("added", ref, pm["value"], pos, rot, [(p.GetNumber(), p.GetNetname()) for p in f.Pads()])
pcbnew.SaveBoard(DST, b); print("saved", DST)
