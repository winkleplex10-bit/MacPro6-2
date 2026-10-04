#!/usr/bin/env python3
"""Rev 2026-10-02 ~14:15 ET: the 821-2222-A trace was taken from the flex face that lay on the scanner glass and placed in the
back-view frame WITHOUT a mirror, on the assumption that this was the plate-facing side. Aidan's flatbed scan of the stock plate OUTER face
(83f0b85e, parent msg 13:37 ET) shows HDMI on the LEFT and the power button on the RIGHT seen from outside -> in the back view HDMI is on the +X
column and the button on the -X column, the opposite of the trace. The flex cut-outs must sit behind the plate openings, so the whole trace is
mirrored (the scanned face was the BOARD-facing side). This script mirrors every X about the LSQ centre of the port cut-outs (C x6, A x4, ETH x2:
X_M = 53.408, port grid moves <= 0.07) and swaps the IDs of the symmetric pairs back so that IDs stay position-based (C1-C3 / A1-A2 / ETH2 /
AUD_H on the -X column as before). Input: flex_821-2222_trace_asscanned.json (the original, kept). Output: flex_821-2222_trace.json."""
import json, os, copy
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "flex_821-2222_trace_asscanned.json"); DST = os.path.join(HERE, "flex_821-2222_trace.json")
if not os.path.exists(SRC): os.rename(DST, SRC)
F = json.load(open(SRC))
ports = [c for c in F["cutouts"] if c["id"][0] in "CA" and c["id"][1:].isdigit() or c["id"].startswith("ETH")]
X_M = round(sum(c["cx"] for c in ports) / len(ports), 3)
mx = lambda x: round(2 * X_M - x, 3)
G = copy.deepcopy(F)
G["outline"] = [[mx(x), y] for x, y in F["outline"]][::-1]
G["tail"] = [[mx(x), y] for x, y in F["tail"]][::-1]
for key in ("cutouts", "holes", "light_pads", "silver_frames", "leds"):
    for it in G[key]: it["cx"] = mx(it["cx"])
G["button"]["cx"] = mx(F["button"]["cx"])
for key in ("neck", "ignored_tab"): G[key]["x"] = sorted(mx(x) for x in F[key]["x"])
G["contact_end"]["x"] = sorted(mx(x) for x in F["contact_end"]["x"]); G["contact_end"]["contacts"]["x"] = sorted(mx(x) for x in F["contact_end"]["contacts"]["x"])
G["overall"]["frame_x"] = sorted(mx(x) for x in F["overall"]["frame_x"])
SWAP = {"C1": "C4", "C2": "C5", "C3": "C6", "A1": "A3", "A2": "A4", "ETH1": "ETH2", "AUD_H": "AUD_O", "PAD_AUD_H": "PAD_AUD_O"}
SWAP.update({v: k for k, v in list(SWAP.items())})
for key in ("cutouts", "light_pads"):
    for it in G[key]:
        if it["id"] in SWAP: it["id"] = SWAP[it["id"]]
G["frame"] = ("stock back-view frame (X right seen from behind, Y up toward MEG end), mm. MIRRORED rev 2026-10-02 ~14:15 ET about X %.3f: the scanned face "
              "was the BOARD-facing side (HDMI must be on +X / button on -X in the back view, plate outer-face scan 83f0b85e). IDs of the symmetric "
              "pairs kept position-based (C1-3, A1-2, ETH2, AUD_H = -X column; 'H' no longer means the HDMI side). LEDs / button carrier seen on the "
              "scanned face are therefore on the BOARD side of the flex (VERIFY with the inside-face scan)." % X_M)
G["mirror"] = dict(x_m=X_M, source=os.path.basename(SRC), port_shift_max=round(max(abs(mx(c["cx"]) - [d for d in F["cutouts"] if d["id"] == SWAP.get(c["id"], c["id"])][0]["cx"]) for c in ports), 3))
json.dump(G, open(DST, "w"), indent=1)
print("X_M", X_M, "port shift max", G["mirror"]["port_shift_max"])
for c in G["cutouts"]: print(c["id"], c["cx"], c["cy"])
print("button", G["button"]["cx"], G["button"]["cy"], "neck", G["neck"], "contact_end", G["contact_end"]["x"])
