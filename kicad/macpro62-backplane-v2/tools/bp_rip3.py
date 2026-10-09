import sys, re; sys.path.insert(0, "../tools")
import bp_fix as F, pcbnew
src, dst, nets, protect = sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4]
F.HS = re.compile(F.HS.pattern + "|" + protect)
b = pcbnew.LoadBoard(src); g = F.Grid(b)
for t in [t for t in b.GetTracks() if t.GetNetname() in nets and not t.IsLocked()]: g.remove_item(t)
vict = {}
for n in nets:
    F.RIP = True; F.RIPPED.clear()
    a, ok = F.route_net(g, n); print(n, ok, len(a), "ripped", dict(F.RIPPED))
    for m in F.RIPPED: vict[m] = 1
F.RIP = False; fails = []
for n in vict:
    if n in nets: continue
    a, ok2 = F.route_net(g, n); print(" reroute", n, ok2, len(a))
    if not ok2: fails.append(n)
for n in nets:
    a, ok2 = F.route_net(g, n)
    if not ok2: fails.append(n)
print("fails", fails)
pcbnew.SaveBoard(dst, b); print("saved", dst)
