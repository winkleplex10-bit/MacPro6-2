#!/usr/bin/env python3
"""CB J3 (IOB-HS) host-end pinout = IOB HS1 v0.2 table (IOB end) with rows A/B exchanged.
The straight MCIO 124 cable crosses the rows (SFF-9402: host TX on row B at the host end). ICD 2026-10-02."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "macpro62-io-board", "docs", "mp62-iob-hs1_mcio124_pinout_v0.2.csv")
OUT = os.path.join(HERE, "..", "docs", "mp62-cb-j3_mcio124_host-end.csv")
xr = lambda c: ("B" if c[0] == "A" else "A") + c[1:]
rows = list(csv.DictReader(open(SRC)))
with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cb_contact", "iob_hs1_contact", "signal", "dir", "notes"])
    for r in sorted(rows, key=lambda r: (int(xr(r["contact"])[1:]), xr(r["contact"])[0])):
        w.writerow([xr(r["contact"]), r["contact"], r["signal"], r["dir"], r["notes"]])
print("wrote", OUT, len(rows), "contacts")
