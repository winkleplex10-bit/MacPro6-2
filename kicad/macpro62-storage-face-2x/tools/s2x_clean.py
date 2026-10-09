"""Cleanup after the Freerouting import (no rip-up, no re-route, no single-net passes): remove dangling vias / track stubs reported by
KiCad DRC (via_dangling, track_dangling), never HS (PCIe/REFCLK) copper; a via is kept only if it joins >= 2 copper layers (tracks/pads/zones); a dangling track that is
touched part-way (e.g. a locked pre-route tail past the router's junction) is trimmed back to the last junction instead of deleted. Refill zones.
One pass per process (pcbnew reload in-process is unstable); loop:  for i in 1..6: python3 tools/s2x_clean.py BOARD
Needs BOARD's .kicad_pro/.kicad_dru beside it (tools/drc.sh copies them)."""
import pcbnew, sys, json, subprocess, re
pcb = sys.argv[1]
HS = re.compile(r"^(PCIE_[AB]_[HM]TX\d_[PN]|REFCLK_[AB]_[PN])$")
b0 = pcbnew.LoadBoard(pcb); pcbnew.ZONE_FILLER(b0).Fill(b0.Zones()); pcbnew.SaveBoard(pcb, b0); del b0
subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", "/tmp/s2xclean.json", pcb], capture_output=True)
d = json.load(open("/tmp/s2xclean.json"))
ids = {i["uuid"] for v in d["violations"] if v["type"] in ("via_dangling", "track_dangling") for i in v["items"]}
print("dangling items", len(ids), "unconnected", len(d["unconnected_items"]))
b = pcbnew.LoadBoard(pcb); n = 0; nt = 0
tr = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
pads = list(b.GetPads()); zones = list(b.Zones())
def V(p): return pcbnew.VECTOR2I(int(p.x), int(p.y))
def segd(p, a, c):
    ax, ay, cx, cy = a.x, a.y, c.x, c.y; dx, dy = cx - ax, cy - ay; L2 = dx * dx + dy * dy
    u = 0 if L2 == 0 else max(0, min(1, ((p.x - ax) * dx + (p.y - ay) * dy) / L2))
    return ((p.x - ax - u * dx) ** 2 + (p.y - ay - u * dy) ** 2) ** 0.5, u
def touch_pts(t):
    """parameter u (0 = start, 1 = end) of every same-net connection along track t"""
    a, c, w, net, ly = t.GetStart(), t.GetEnd(), t.GetWidth(), t.GetNetCode(), t.GetLayer(); us = []
    for o in tr:
        if o.m_Uuid.AsString() == t.m_Uuid.AsString() or o.GetNetCode() != net or o.GetLayer() != ly: continue
        for e in (o.GetStart(), o.GetEnd()):
            d, u = segd(e, a, c)
            if d <= (w + o.GetWidth()) / 2 * 0.5: us.append(u)
        for e in (a, c):   # our end on the other track's body
            d, u2 = segd(e, o.GetStart(), o.GetEnd())
            if d <= (w + o.GetWidth()) / 2 * 0.5: us.append(0.0 if e == a else 1.0)
    for v in vias:
        if v.GetNetCode() != net: continue
        d, u = segd(v.GetPosition(), a, c)
        if d <= v.GetWidth(pcbnew.F_Cu) / 2: us.append(u)
    for p in pads:
        if p.GetNetCode() != net or not p.IsOnLayer(ly): continue
        for uu in (0.0, 1.0):
            e = a if uu == 0 else c
            if p.HitTest(e): us.append(uu)
        d, u = segd(p.GetPosition(), a, c)
        if d <= w / 2: us.append(u)
    for z in zones:
        if z.GetNetCode() != net or not z.IsOnLayer(ly): continue
        for uu, e in ((0.0, a), (1.0, c)):
            if z.HitTestFilledArea(ly, e): us.append(uu)
    return us
def joins(v):
    c = v.GetPosition(); r = v.GetWidth(pcbnew.F_Cu) / 2; ls = set()
    for t in tr:
        if t.GetNetCode() != v.GetNetCode(): continue
        if segd(c, t.GetStart(), t.GetEnd())[0] <= r: ls.add(t.GetLayer())
    for p in pads:
        if p.GetNetCode() == v.GetNetCode() and p.HitTest(c): ls.add(-1)
    for z in zones:
        if z.GetNetCode() == v.GetNetCode():
            for l in z.GetLayerSet().Seq():
                if z.HitTestFilledArea(l, c): ls.add(l)
    return len(ls) >= 2
for t in list(b.GetTracks()):
    if t.m_Uuid.AsString() not in ids or HS.match(t.GetNetname()): continue
    if t.Type() == pcbnew.PCB_VIA_T:
        if t.GetNetname() == "GND" or joins(t): continue
        b.Remove(t); vias[:] = [o for o in vias if o.m_Uuid.AsString() != t.m_Uuid.AsString()]; n += 1; continue
    us = touch_pts(t); s0 = any(u < 1e-3 for u in us); s1 = any(u > 1 - 1e-3 for u in us)
    if s0 and s1: continue
    if not s0 and not s1: b.Remove(t); tr[:] = [o for o in tr if o.m_Uuid.AsString() != t.m_Uuid.AsString()]; n += 1; continue
    a, c = t.GetStart(), t.GetEnd()
    if s0:   # end 1 dangles: trim to the touch point nearest the end
        u = max(us)
        if u < 1e-3: b.Remove(t); tr[:] = [o for o in tr if o.m_Uuid.AsString() != t.m_Uuid.AsString()]; n += 1; continue
        t.SetEnd(V(pcbnew.VECTOR2I(int(a.x + u * (c.x - a.x)), int(a.y + u * (c.y - a.y)))))
    else:
        u = min(us)
        if u > 1 - 1e-3: b.Remove(t); tr[:] = [o for o in tr if o.m_Uuid.AsString() != t.m_Uuid.AsString()]; n += 1; continue
        t.SetStart(V(pcbnew.VECTOR2I(int(a.x + u * (c.x - a.x)), int(a.y + u * (c.y - a.y)))))
    nt += 1
print("trimmed", nt)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(pcb, b)
print("removed", n)
