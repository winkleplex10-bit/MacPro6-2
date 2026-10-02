#!/usr/bin/env python3
"""Inject the JLC06161H-2116 6-layer stackup into the template board and set MP62-FACE netclasses in the .kicad_pro."""
import json, os
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pcb = os.path.join(PRJ, "macpro62-storage-face.kicad_pcb"); pro = pcb.replace(".kicad_pcb", ".kicad_pro")
D = lambda n, t, th, mat, er, lt=0.02: f'\t\t\t(layer "dielectric {n}" (type "{t}") (thickness {th}) (material "{mat}") (epsilon_r {er}) (loss_tangent {lt}))\n'
C = lambda name, th: f'\t\t\t(layer "{name}" (type "copper") (thickness {th}))\n'
HEAD = '\t\t(stackup\n\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))\n\t\t\t(layer "F.Paste" (type "Top Solder Paste"))\n\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))\n'
TAIL = '\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))\n\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))\n\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))\n\t\t\t(copper_finish "ENIG")\n\t\t\t(dielectric_constraints no)\n\t\t)\n'
body = (C("F.Cu", 0.035) + D(1, "prepreg", 0.2234, "2116 0.127 + 2313 0.0964 (NP-155F)", 4.14) +
        C("In1.Cu", 0.0152) + D(2, "core", 0.30, "FR4 core 0.30 (NP-155F)", 4.6) +
        C("In2.Cu", 0.0152) + D(3, "prepreg", 0.4168, "7628 x2 0.2084 each (NP-155F)", 4.4) +
        C("In3.Cu", 0.0152) + D(4, "core", 0.30, "FR4 core 0.30 (NP-155F)", 4.6) +
        C("In4.Cu", 0.0152) + D(5, "prepreg", 0.2234, "2313 0.0964 + 2116 0.127 (NP-155F)", 4.14) + C("B.Cu", 0.035))
s = open(pcb).read()
if "(stackup" not in s:
    s = s.replace("\t(setup\n", "\t(setup\n" + HEAD + body + TAIL, 1); open(pcb, "w").write(s)
d = json.load(open(pro))
d["meta"]["filename"] = "macpro62-storage-face.kicad_pro"
d["sheets"] = []; d["boards"] = []
base = [c for c in d["net_settings"]["classes"] if c["name"] == "Default"][0]
base.update(clearance=0.127, track_width=0.2, via_diameter=0.6, via_drill=0.3)
def nc(name, **kw):
    c = dict(base); c.update(name=name, **kw); return c
d["net_settings"]["classes"] = [base,
    nc("PCIE_85R", clearance=0.2, track_width=0.35, diff_pair_width=0.35, diff_pair_gap=0.2, diff_pair_via_gap=0.25,
       description="PCIe Gen4 85 ohm diff (L1/L6 microstrip on JLC06161H-2116). START VALUE; confirm with the JLC impedance calculator"),
    nc("DISP_100R", clearance=0.2, track_width=0.25, diff_pair_width=0.25, diff_pair_gap=0.2, diff_pair_via_gap=0.25,
       description="DP 1.4 / HDMI 2.1 / USB-C alt-mode 100 ohm diff. START VALUE; confirm with the JLC impedance calculator"),
    nc("REFCLK_85R", clearance=0.2, track_width=0.35, diff_pair_width=0.35, diff_pair_gap=0.2, description="PCIe REFCLK HCSL 85-100 ohm"),
    nc("USB2_90R", clearance=0.2, track_width=0.3, diff_pair_width=0.3, diff_pair_gap=0.2, description="USB2 fallback on AUX"),
    nc("PWR_3V3", clearance=0.2, track_width=1.0, via_diameter=0.8, via_drill=0.4, description="3V3_SSD: up to 10-12 A peak, use L4 plane + pours"),
    nc("PWR_12V", clearance=0.3, track_width=2.0, via_diameter=0.8, via_drill=0.4, description="12 V input: >=15 A, use pours on 2 oz outer copper"),
]
d["net_settings"]["netclass_patterns"] = [
    {"netclass": "PCIE_85R", "pattern": "*PE?[TR]?[pn]*"}, {"netclass": "PCIE_85R", "pattern": "*PCIE_*"},
    {"netclass": "REFCLK_85R", "pattern": "*REFCLK*"}, {"netclass": "DISP_100R", "pattern": "*DP?_L*"},
    {"netclass": "DISP_100R", "pattern": "*HDMI_*"}, {"netclass": "USB2_90R", "pattern": "*USB2_D*"},
    {"netclass": "PWR_12V", "pattern": "+12V*"}, {"netclass": "PWR_3V3", "pattern": "3V3_SSD"}, {"netclass": "PWR_3V3", "pattern": "VDD_CORE"}]
d["net_settings"]["netclass_assignments"] = None
d["board"]["design_settings"]["rules"]["min_hole_clearance"] = 0.25
d.setdefault("text_variables", {})["STACKUP"] = "JLC06161H-2116 6L 1.6mm"
d["text_variables"]["SPEC"] = "MP62-FACE v0.1 + Face S SM-1 plan"
json.dump(d, open(pro, "w"), indent=2)
print("postprocess ok")
