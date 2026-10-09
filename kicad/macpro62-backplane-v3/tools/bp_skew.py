"""Intra-pair length/skew report for the BP PCIe / REFCLK pairs (copper track length per net incl. breakouts; vias counted as board thickness)."""
import pcbnew, sys, collections, re
pcb = sys.argv[1] if len(sys.argv) > 1 else "backplane.kicad_pcb"
b = pcbnew.LoadBoard(pcb)
L = collections.defaultdict(float); V = collections.Counter()
for t in b.GetTracks():
    n = t.GetNetname()
    if isinstance(t, pcbnew.PCB_VIA): V[n] += 1
    else: L[n] += pcbnew.ToMM(t.GetLength())
rows = []
for n in sorted(L):
    if n.endswith("_P"):
        m = n[:-2] + "_N"
        if m in L and re.match(r"(FP|FS)_(TX|RX)\d+|(FP|FS)_REFCLK|USB2_|SATA0_", n):
            rows.append((n[:-2], L[n], L[m], L[n] - L[m] + 1.6 * (V[n] - V[m]), V[n], V[m]))
if __name__ == "__main__":
    print("%-12s %8s %8s %8s %3s %3s" % ("pair", "P mm", "N mm", "skew", "vP", "vN"))
    for r in rows: print("%-12s %8.2f %8.2f %8.3f %3d %3d" % r)
