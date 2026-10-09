"""BP v3 (from rev A1) pin maps; v3 = CPU-LINK v3 slot B x4 on reclaimed pins (docs/cpulink_224_pinout_draft.csv).
BP rev A1 pin maps (J1 CPU-LINK, J9/J10 MCIO BP end, GH15 AUX, IOB-LINK, PSU-IN).
J1: docs/cpulink_224_pinout_draft.csv, with the ICD rev 3.1 PROPOSAL applied: the Face S lanes are reversed on CPU-LINK
(A58/59 = FS_PET3 ... A67/68 = FS_PET0, same for B). Reason: Face S's MCIO is a rotated copy of Face P's, so with the rev 3
order the FS bundle would have to cross itself (planar routing impossible); FP and FS then both have lane number decreasing
with pin number. The CB is not routed yet, so it costs nothing there (needs Aidan's OK)."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "docs", "cpulink_224_pinout_draft.csv")
FS_REVERSED = True

def j1_signals():
    rows = list(csv.DictReader(open(CSV)))
    sig = {r["pin"]: r["signal"].strip() for r in rows}
    if FS_REVERSED and sig.get("A58") == "FS_PET0_P":
        for row in "AB":
            pre = "FS_PET" if row == "A" else "FS_PER"
            for l in range(4):
                p0 = 58 + 3 * l          # rev 3: lane l at 58+3l (P), 59+3l (N)
                q = 58 + 3 * (3 - l)
                sig["%s%d" % (row, q)] = "%s%d_P" % (pre, l)
                sig["%s%d" % (row, q + 1)] = "%s%d_N" % (pre, l)
    return sig

# MCIO 124 BP end (straight cable: the BP sees the module's A row on its B row and vice versa).
# Module end: A = PETp/n (host TX), B = PERp/n; A8 SMCLK, A9 SMDAT, B8 CLKREQ0#, B9 WAKE0#, A11 PERST0#, A12 PRSNT0#, B11/12 REFCLK0+/-.
def mcio_bp_end():
    m = {}
    lanes = [(2, 0), (5, 1), (14, 2), (17, 3), (20, 4), (23, 5), (32, 6), (35, 7), (39, 8), (42, 9), (45, 10), (48, 11),
             (51, 12), (54, 13), (57, 14), (60, 15)]
    gnd = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 38, 41, 44, 47, 50, 53, 56, 59, 62]
    for p, l in lanes:
        m["B%d" % p] = ("PET", l, "P"); m["B%d" % (p + 1)] = ("PET", l, "N")
        m["A%d" % p] = ("PER", l, "P"); m["A%d" % (p + 1)] = ("PER", l, "N")
    for g in gnd:
        m["A%d" % g] = ("GND",); m["B%d" % g] = ("GND",)
    m.update({"B8": ("SMCLK",), "B9": ("SMDAT",), "B11": ("PERST",), "B12": ("PRSNT",),
              "A8": ("CLKREQ",), "A9": ("WAKE",), "A11": ("REFCLK", "P"), "A12": ("REFCLK", "N"),
              "B26": ("RSVD",), "B27": ("RSVD",), "B29": ("PERST1",), "B30": ("PRSNT1",),
              "A26": ("CLKREQ1",), "A27": ("WAKE1",), "A29": ("REFCLK1", "P"), "A30": ("REFCLK1", "N")})   # v3: set B (BP end; module end rows swapped)
    return m, lanes
