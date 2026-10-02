#!/usr/bin/env python3
"""Inject the JLC06161H-2116 6-layer stackup and set IOB netclasses in the .kicad_pro."""
import json, os
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pcb = os.path.join(PRJ, "macpro62-io-board.kicad_pcb"); pro = pcb.replace(".kicad_pcb", ".kicad_pro")
D = lambda n, t, th, mat, er, lt=0.02: f'\t\t\t(layer "dielectric {n}" (type "{t}") (thickness {th}) (material "{mat}") (epsilon_r {er}) (loss_tangent {lt}))\n'
C = lambda name, th: f'\t\t\t(layer "{name}" (type "copper") (thickness {th}))\n'
HEAD = '\t\t(stackup\n\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))\n\t\t\t(layer "F.Paste" (type "Top Solder Paste"))\n\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))\n'
TAIL = '\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))\n\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))\n\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))\n\t\t\t(copper_finish "ENIG")\n\t\t\t(dielectric_constraints no)\n\t\t)\n'
body = (C("F.Cu", 0.035) + D(1, "prepreg", 0.2234, "2116 0.127 + 2313 0.0964 (NP-155F)", 4.14) + C("In1.Cu", 0.0152) + D(2, "core", 0.30, "FR4 core 0.30", 4.6) +
        C("In2.Cu", 0.0152) + D(3, "prepreg", 0.4168, "7628 x2", 4.4) + C("In3.Cu", 0.0152) + D(4, "core", 0.30, "FR4 core 0.30", 4.6) +
        C("In4.Cu", 0.0152) + D(5, "prepreg", 0.2234, "2313 0.0964 + 2116 0.127", 4.14) + C("B.Cu", 0.035))
s = open(pcb).read()
if "(stackup" not in s:
    s = s.replace("\t(setup\n", "\t(setup\n" + HEAD + body + TAIL, 1); open(pcb, "w").write(s)
d = json.load(open(pro)); d["meta"]["filename"] = "macpro62-io-board.kicad_pro"
base = [c for c in d["net_settings"]["classes"] if c["name"] == "Default"][0]
base.update(clearance=0.1, track_width=0.15, via_diameter=0.45, via_drill=0.3)
def nc(name, **kw):
    c = dict(base); c.update(name=name, **kw); return c
d["net_settings"]["classes"] = [base,
    nc("USB3_90R", clearance=0.2, track_width=0.2, diff_pair_width=0.2, diff_pair_gap=0.18, diff_pair_via_gap=0.25, description="USB 3.2 Gen2 / USB-C SS 85-90 ohm diff. START VALUE (JLC calculator)"),
    nc("DP_100R", clearance=0.2, track_width=0.18, diff_pair_width=0.18, diff_pair_gap=0.2, description="DP HBR3 / HDMI TMDS 100 ohm diff. START VALUE"),
    nc("PCIE_85R", clearance=0.2, track_width=0.22, diff_pair_width=0.22, diff_pair_gap=0.18, description="i226 PCIe x1 + REFCLK 85 ohm"),
    nc("USB2_90R", clearance=0.15, track_width=0.2, diff_pair_width=0.2, diff_pair_gap=0.18, description="USB2 90 ohm"),
    nc("MDI_100R", clearance=0.2, track_width=0.18, diff_pair_width=0.18, diff_pair_gap=0.2, description="i226 MDI 100 ohm to the magjack"),
    nc("PWR_5V", clearance=0.2, track_width=1.0, via_diameter=0.8, via_drill=0.4, description="5V_C / 5V_A / VBUS: up to 12 A per rail, use L4 + pours"),
    nc("PWR_12V", clearance=0.3, track_width=1.5, via_diameter=0.8, via_drill=0.4, description="12 V from the PSU DC header, <= 12 A")]
d["net_settings"]["netclass_patterns"] = [{"netclass": "USB3_90R", "pattern": "*SS*"}, {"netclass": "USB3_90R", "pattern": "*USB3*"},
    {"netclass": "DP_100R", "pattern": "*ML*"}, {"netclass": "DP_100R", "pattern": "*TMDS*"}, {"netclass": "PCIE_85R", "pattern": "*PCIE*"},
    {"netclass": "PCIE_85R", "pattern": "*REFCLK*"}, {"netclass": "USB2_90R", "pattern": "*USB2*"}, {"netclass": "USB2_90R", "pattern": "*_D[PN]"},
    {"netclass": "MDI_100R", "pattern": "*MDI*"}, {"netclass": "PWR_5V", "pattern": "5V_*"}, {"netclass": "PWR_5V", "pattern": "VBUS*"}, {"netclass": "PWR_12V", "pattern": "+12V*"}]
d["net_settings"]["netclass_assignments"] = None
d["board"]["design_settings"]["rules"]["min_clearance"] = 0.1
d.setdefault("text_variables", {})["STACKUP"] = "JLC06161H-2116 6L 1.6mm"
json.dump(d, open(pro, "w"), indent=2); print("postprocess ok")
