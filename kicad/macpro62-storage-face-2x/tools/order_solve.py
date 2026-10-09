"""Manhattan 2-via pair plan: J1 verticals (B for module-TX/REFCLK from row B, L1 for host-TX from the row-A gap vias),
L1 horizontals at height h(k), B verticals into the socket. Brute-force the height order with symbolic conflict checks."""
import itertools, sys
def j1x(c): return 28.1 + 0.6 * (c - 1)
def slot(lane0, clkc, Xs):
    P = []
    for k in range(4):
        c = {0: 2, 1: 5, 2: 14, 3: 17, 4: 20, 5: 23, 6: 32, 7: 35}[lane0 + k]
        xj = (j1x(c) + j1x(c + 1)) / 2
        # socket: host TX n/p 47/49 (lane0) .. 11/13; module TX 41/43 .. 5/7
        hp = {0: 48, 1: 36, 2: 24, 3: 12}[k]; mp = {0: 42, 1: 30, 2: 18, 3: 6}[k]
        fx = lambda n: Xs - 9.25 + 0.25 * (n - 1)
        P.append(("H%d" % k, xj, "L1", fx(hp)))
        P.append(("M%d" % k, xj, "B", fx(mp)))
    P.append(("CLK", (j1x(clkc) + j1x(clkc + 1)) / 2, "B", Xs - 9.25 + 0.25 * 53))
    return P
def conflicts(P, h, VX=1.15, VW=1.0):
    bad = []
    n = len(P)
    for a in range(n):
        na, xja, la, xsa = P[a]
        for b in range(n):
            if a == b: continue
            nb, xjb, lb, xsb = P[b]
            lo, hi = min(xja, xsa), max(xja, xsa)
            # L1 horizontal a vs L1 vertical b (H)
            if lb == "L1" and lo - VW < xjb < hi + VW and h[b] > h[a] - 0.5 and not (abs(xjb - xja) < 0.01): bad.append((na, nb, "hz/L1v"))
            # J-side vertical b vs S-side via of a
            if abs(xsa - xjb) < VX and h[a] < h[b]: bad.append((na, nb, "Svia/Jv"))
            # B J-vertical b vs B S-vertical a
            if lb == "B" and abs(xjb - xsa) < VX and h[a] < h[b]: bad.append((na, nb, "Sv/Jv"))
            # S-side vertical a vs J-side via b (B or L1->? J via exists only for B-start)
            if lb == "B" and abs(xjb - xsa) < VX and h[b] > h[a]: bad.append((na, nb, "Sv/Jvia"))
        # same lane: H below M
    for a in range(n):
        for b in range(n):
            if P[a][2] == "L1" and P[b][2] == "B" and abs(P[a][1] - P[b][1]) < 0.01 and h[a] > h[b]: bad.append((P[a][0], P[b][0], "lane"))
    return bad
def solve(P, want=1):
    n = len(P); best = None
    for perm in itertools.permutations(range(n)):
        h = [0] * n
        for lvl, i in enumerate(perm): h[i] = lvl
        c = conflicts(P, h)
        if best is None or len(c) < len(best[1]): best = (perm, c)
        if not c: return perm, c
    return best
if __name__ == "__main__":
    for Xs in [float(a) for a in sys.argv[2:]]:
        P = slot(0 if sys.argv[1] == "A" else 4, 11 if sys.argv[1] == "A" else 29, Xs)
        perm, c = solve(P)
        print(sys.argv[1], Xs, "order bottom->top", [P[i][0] for i in perm], "conflicts", len(c), c[:4])
