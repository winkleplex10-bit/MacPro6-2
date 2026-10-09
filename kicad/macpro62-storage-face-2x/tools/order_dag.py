"""Precedence version of order_solve: every conflict rule is 'bad if h[x] < h[y]' -> edge y below x. Topo sort or report a cycle."""
import sys, order_solve as O
def edges(P, VX=1.15, VW=1.0):
    E = set(); n = len(P)
    for a in range(n):
        na, xja, la, xsa = P[a]; lo, hi = min(xja, xsa), max(xja, xsa)
        for b in range(n):
            if a == b: continue
            nb, xjb, lb, xsb = P[b]
            if lb == "L1" and lo - VW < xjb < hi + VW and abs(xjb - xja) > 0.01: E.add((b, a, "L1v %s under hz %s" % (nb, na)))   # h[b] < h[a]
            if abs(xsa - xjb) < VX: E.add((b, a, "Jv %s under Svia %s" % (nb, na)))
            if lb == "B" and abs(xjb - xsa) < VX: E.add((b, a, "Jv/Jvia %s under Sv %s" % (nb, na)))
            if la == "L1" and lb == "B" and abs(xja - xjb) < 0.01: E.add((a, b, "lane"))
    return E
def topo(n, E):
    import collections
    succ = collections.defaultdict(set); indeg = [0] * n
    for a, b, _ in E:
        if b not in succ[a]: succ[a].add(b); indeg[b] += 1
    q = [i for i in range(n) if indeg[i] == 0]; out = []
    while q:
        q.sort(); i = q.pop(0); out.append(i)
        for j in succ[i]:
            indeg[j] -= 1
            if indeg[j] == 0: q.append(j)
    return out if len(out) == n else None
if __name__ == "__main__":
    s = sys.argv[1]
    for Xs in [float(a) for a in sys.argv[2:]]:
        P = O.slot(0 if s == "A" else 4, 11 if s == "A" else 29, Xs); E = edges(P)
        t = topo(len(P), E)
        print(s, Xs, [P[i][0] for i in t] if t else "CYCLE", "" if t else sorted(e[2] for e in E)[:40])
