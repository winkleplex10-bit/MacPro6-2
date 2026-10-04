#!/usr/bin/env python3
"""Inject a JLC 10-layer 1.6 mm stackup (PLACEHOLDER dielectrics summing to 1.6 mm - take the real table from JLC's
order-page stackup selector / impedance calculator) and net classes into macpro62_am5.kicad_pcb/.kicad_pro.
L1 S (front, fingers side B) / L2 GND / L3 S (stripline: DDR5, PCIe) / L4 GND / L5 PWR / L6 PWR / L7 GND /
L8 S (stripline: DDR5, PROM21 uplink) / L9 GND / L10 S (back, fingers side A)."""
import json, os
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pcb = os.path.join(PRJ, "macpro62_am5.kicad_pcb")
D = lambda n, t, th, mat, er, lt=0.02: f'\t\t\t(layer "dielectric {n}" (type "{t}") (thickness {th}) (material "{mat}") (epsilon_r {er}) (loss_tangent {lt}))\n'
C = lambda name, th: f'\t\t\t(layer "{name}" (type "copper") (thickness {th}))\n'
HEAD = '\t\t(stackup\n\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))\n\t\t\t(layer "F.Paste" (type "Top Solder Paste"))\n\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))\n'
TAIL = '\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))\n\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))\n\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))\n\t\t\t(copper_finish "ENIG")\n\t\t\t(dielectric_constraints no)\n\t\t\t(edge_connector bevelled)\n\t\t)\n'
th = [0.09, 0.20, 0.13, 0.20, 0.1684, 0.20, 0.13, 0.20, 0.09]
kind = ["prepreg", "core"] * 4 + ["prepreg"]
names = ["F.Cu"] + ["In%d.Cu" % i for i in range(1, 9)] + ["B.Cu"]
body = ""
for i, n in enumerate(names):
    body += C(n, 0.035 if n in ("F.Cu", "B.Cu") else 0.0152)
    if i < 9:
        body += D(i + 1, kind[i], th[i], ("FR4 core" if kind[i] == "core" else "7628/2116 prepreg") + " PLACEHOLDER", 4.6 if kind[i] == "core" else 4.4)
tag = "JLC 10L 1.6mm (placeholder dielectrics; use the JLC 10-layer stackup selector)"
s = open(pcb).read()
if "(stackup" not in s:
    s = s.replace("\t(setup\n", "\t(setup\n" + HEAD + body + TAIL, 1)
    open(pcb, "w").write(s)
pro = pcb.replace(".kicad_pcb", ".kicad_pro")
d = json.load(open(pro))
classes = d["net_settings"]["classes"]
for c in classes:
    if c["name"] == "Default":
        c.update(clearance=0.1, track_width=0.1, via_diameter=0.25, via_drill=0.15)
if not any(c["name"] == "PCIE_85R" for c in classes):
    base = dict([c for c in classes if c["name"] == "Default"][0])
    def add(**kw):
        b = dict(base); b.update(**kw); classes.append(b)
    add(name="PCIE_85R", clearance=0.15, track_width=0.12, diff_pair_width=0.12, diff_pair_gap=0.15, description="PCIe Gen4 (8000G) / Gen5 (7000/9000 option) 85 ohm diff. START VALUES - compute with the JLC impedance calculator")
    add(name="DDR5_40R_SE", clearance=0.1, track_width=0.1, description="DDR5 DQ/CA 40 ohm single-ended, DQS/CK 80 ohm diff. START VALUES")
    add(name="USB_DDI_90R", clearance=0.12, track_width=0.12, diff_pair_width=0.12, diff_pair_gap=0.15, description="USB2/USB 10G/USB4/SATA 90 ohm (USB4 85 ohm per AMD guide TBD), DP 85-100 ohm diff. START VALUES")
    add(name="PWR_12V", clearance=0.3, track_width=2.0, description="12 V: pours on L5/L6 + L1/L10")
d["board"]["design_settings"]["rules"]["min_hole_clearance"] = 0.2
d.setdefault("text_variables", {})["STACKUP"] = tag
json.dump(d, open(pro, "w"), indent=2)
print("postprocess ok", tag)
