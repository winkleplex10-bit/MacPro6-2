"""Update /workspace/macpro62-cost-estimate.md for one board group (BP A1 or SM-1 A1): replaces that group's line items in the
markdown table + CSV, its §2 summary row, its §1 board-table row, recomputes subtotal / duty (35 % on pcb-class deltas) / grand total
(rounded to $100 like the original), and inserts/replaces a '### <title>' change log in §6.   python3 cost_update.py spec.json"""
import json, sys, csv, io, re
spec = json.load(open(sys.argv[1]))
F = "/workspace/macpro62-cost-estimate.md"
s = open(F).read()
old_group = spec["old_group"]; new_group = spec["group"]
lines = s.split("\n")
# --- old values of the group (from CSV) for deltas
a = s.index("```csv\n") + 7; e = s.index("```", a)
rows = list(csv.reader(io.StringIO(s[a:e])))
hdr = rows[0]; body = rows[1:]
oldv = [0, 0, 0, 0]; oldpcb = [0, 0, 0, 0]
for r in body:
    if r and r[0] in (old_group, new_group):
        for i in range(4):
            oldv[i] += int(r[2 + i]); oldpcb[i] += int(r[2 + i]) if r[6] == "pcb" else 0
newv = [sum(it[2 + i] for it in spec["items"]) for i in range(4)]
newpcb = [sum(it[2 + i] for it in spec["items"] if it[6] == "pcb") for i in range(4)]
d = [newv[i] - oldv[i] for i in range(4)]; dd = [round(0.35 * (newpcb[i] - oldpcb[i])) for i in range(4)]
# --- CSV block
out = []; ins = False
for r in body:
    if r and r[0] in (old_group, new_group):
        if not ins:
            for it in spec["items"]: out.append([new_group, it[1]] + [str(x) for x in it[2:6]] + [it[6], it[7]])
            ins = True
        continue
    if r and r[0] == "TOTAL before duty": tb = [int(x) for x in r[2:6]]; r = r[:2] + [str(int(round((tb[i] + d[i]) / 100.0) * 100)) for i in range(4)] + r[6:]
    if r and r[0] == "US DDP duty": du = [int(x) for x in r[2:6]]; r = r[:2] + [str(int(round((du[i] + dd[i]) / 10.0) * 10)) for i in range(4)] + r[6:]
    out.append(r)
tot = {r[0]: r for r in out if r and r[0] in ("TOTAL before duty", "US DDP duty", "GRAND TOTAL")}
T = [int(x) for x in tot["TOTAL before duty"][2:6]]; Du = [int(x) for x in tot["US DDP duty"][2:6]]
G = [int(round((T[i] + Du[i]) / 100.0) * 100) for i in range(4)]
for r in out:
    if r and r[0] == "GRAND TOTAL": r[2:6] = [str(x) for x in G]
buf = io.StringIO(); w = csv.writer(buf, lineterminator="\n"); w.writerow(hdr); w.writerows(out)
s = s[:a] + buf.getvalue() + s[e:]
# --- markdown line-item table
mdrows = ["| %s | %s | %d | %d | %d | %d | %s | %s |" % ((new_group, it[1]) + tuple(it[2:6]) + (it[6], it[7])) for it in spec["items"]]
L = s.split("\n"); out = []; ins = False
for ln in L:
    if ln.startswith("| %s | " % old_group) or ln.startswith("| %s | " % new_group):
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) == 8 and re.match(r"^\d+$", cells[2]):
            if not ins: out.extend(mdrows); ins = True
            continue
        if len(cells) == 4 and cells[1].startswith("$"):   # §2 summary row
            fm = lambda x: "${:,}".format(x)
            pm = [int(round(newv[2] / 5.0 / 10)) * 10, int(round(newv[3] / 5.0 / 10)) * 10]
            out.append("| %s | %s – %s | %s – %s | %s – %s |" % (new_group, fm(newv[0]), fm(newv[1]), fm(newv[2]), fm(newv[3]), fm(pm[0]), fm(pm[1]))); continue
        if len(cells) > 8 and "kicad_pcb" in ln and spec.get("board_row"):
            out.append(spec["board_row"]); continue
    out.append(ln)
s = "\n".join(out)
fm = lambda x: "${:,}".format(x)
s = re.sub(r"\| \*\*Subtotal before import duty\*\* \|[^\n]*", "| **Subtotal before import duty** | **%s – %s** | **%s – %s** | **%s – %s** |" % (fm(T[0]), fm(T[1]), fm(T[2]), fm(T[3]), fm(int(round(T[2] / 500.0)) * 100), fm(int(round(T[3] / 500.0)) * 100)), s)
s = re.sub(r"\| US DDP import duty pre-collected by JLC([^|]*)\|[^\n]*", lambda m: "| US DDP import duty pre-collected by JLC%s| %s – %s | %s – %s | %s – %s |" % (m.group(1), fm(Du[0]), fm(Du[1]), fm(Du[2]), fm(Du[3]), fm(int(round(Du[2] / 50.0)) * 10), fm(int(round(Du[3] / 50.0)) * 10)), s)
s = re.sub(r"\| \*\*Grand total, delivered to the US\*\* \|[^\n]*", "| **Grand total, delivered to the US** | **%s – %s** | **%s – %s** | **%s – %s** |" % (fm(G[0]), fm(G[1]), fm(G[2]), fm(G[3]), fm(int(round(G[2] / 500.0)) * 100), fm(int(round(G[3] / 500.0)) * 100)), s)
# --- change log section
title = spec["log_title"]; block = "### " + title + "\n\n" + spec["log_md"].rstrip() + "\n"
if ("### " + title) in s:
    i = s.index("### " + title); j = s.find("\n## ", i); j2 = s.find("\n### ", i + 4)
    j = min([x for x in (j, j2) if x > 0] or [len(s)])
    s = s[:i] + block + s[j:]
else:
    k = s.index("## 6. Ways to cut cost"); k = s.find("\n## ", k + 5)
    s = s[:k] + "\n" + block + s[k:]
open(F, "w").write(s)
print("group", new_group, "old", oldv, "new", newv, "delta", d, "duty delta", dd, "totals", T, Du, G)
