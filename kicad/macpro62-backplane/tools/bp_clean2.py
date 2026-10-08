"""In-process dangling-track removal (pcbnew connectivity), loops until stable; then zone refill.
   python3 tools/bp_clean2.py BOARD   (in place). Locked non-GND copper is kept."""
import pcbnew, sys
import json, subprocess, re
pcb = sys.argv[1]; tot = 0; KEEP = []
HS = re.compile(r"(FP|FS)_(TX|RX)\d+_[PN]$|(FP|FS)_REFCLK_[PN]$|SATA0_|USB2_SPARE")
_b = pcbnew.LoadBoard(pcb); pcbnew.ZONE_FILLER(_b).Fill(_b.Zones()); pcbnew.SaveBoard(pcb, _b); del _b   # stale pours make DRC crawl
subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", "/tmp/bpclean2.json", pcb], capture_output=True)
dv = {i["uuid"] for v in json.load(open("/tmp/bpclean2.json"))["violations"] if v["type"] == "via_dangling" for i in v["items"]}
b = pcbnew.LoadBoard(pcb); MM = pcbnew.FromMM
tr = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]; nv = nj = 0
for v in list(b.GetTracks()):
    if v.Type() != pcbnew.PCB_VIA_T or v.m_Uuid.AsString() not in dv or HS.match(v.GetNetname()) or v.GetNetname() == "GND": continue
    c = v.GetPosition(); r = v.GetWidth(pcbnew.F_Cu) / 2; ends = []
    for t in tr:
        if t.GetNetCode() != v.GetNetCode(): continue
        for e in (t.GetStart(), t.GetEnd()):
            if (e - c).EuclideanNorm() <= r: ends.append((t, e))
    for t, e in ends:   # keep same-layer joins: bridge each end to the via centre
        if e != c:
            n = pcbnew.PCB_TRACK(b); n.SetStart(e); n.SetEnd(c); n.SetWidth(t.GetWidth()); n.SetLayer(t.GetLayer()); n.SetNet(v.GetNet()); b.Add(n); nj += 1
    if len(ends) <= 1:   # single stub (e.g. unused locked escape): unlock the stub so the dangling pass removes it
        for t, e in ends: t.SetLocked(False)
    KEEP.append(v); b.Remove(v); nv += 1
print("dangling vias removed", nv, "bridges", nj)
for it in range(400):
    b.BuildConnectivity(); conn = b.GetConnectivity(); rm = []
    for t in b.GetTracks():
        if t.Type() != pcbnew.PCB_TRACE_T or (t.IsLocked() and t.GetNetname() != "GND"): continue
        if conn.TestTrackEndpointDangling(t, False): rm.append(t)
    if not rm: break
    for t in rm: KEEP.append(t); b.Remove(t)
    tot += len(rm)
print("removed dangling tracks", tot, "in", it, "passes")
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(pcb, b)
