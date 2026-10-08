"""Remove dangling vias / track stubs (DRC via_dangling, track_dangling) iteratively, refill zones.
   python3 tools/bp_clean.py BOARD [maxiter]   (in place; needs BOARD's .kicad_pro/.kicad_dru beside it)"""
import pcbnew, sys, json, subprocess, os
pcb = sys.argv[1]; maxit = 1   # one pass per process (pcbnew segfaults on a reload in the same process); loop in the shell
for it in range(maxit):
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", "/tmp/bpclean.json", pcb], capture_output=True)
    d = json.load(open("/tmp/bpclean.json"))
    ids = {i["uuid"] for v in d["violations"] if v["type"] in ("via_dangling", "track_dangling") for i in v["items"]}
    print("iter", it, "dangling items", len(ids), "unconnected", len(d["unconnected_items"]))
    if not ids: break
    b = pcbnew.LoadBoard(pcb); n = 0
    tr = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
    def joins(v):   # a via whose annulus joins >=2 own-net track ends is a connector, keep it
        c = v.GetPosition(); r = v.GetWidth(pcbnew.F_Cu) / 2; k = 0
        for t in tr:
            if t.GetNetCode() != v.GetNetCode(): continue
            for e in (t.GetStart(), t.GetEnd()):
                if (e - c).EuclideanNorm() <= r: k += 1
        return k >= 2
    for t in list(b.GetTracks()):
        if t.Type() == pcbnew.PCB_VIA_T and t.m_Uuid.AsString() in ids and joins(t): continue
        if t.m_Uuid.AsString() in ids and not (t.IsLocked() and t.GetNetname() != "GND"):
            b.Remove(t); n += 1
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(pcb, b)
    print("  removed", n)
    if n == 0: break
