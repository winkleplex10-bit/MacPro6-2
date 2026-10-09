#!/usr/bin/env python3
"""Inject the JLC stackup and JLC-friendly rules.
  hub (default):  backplane.kicad_pcb        -> JLC06161H-2116, 6 layers, 1.6 mm (per jlcpcb.com/impedance)
  direct:         backplane_direct.kicad_pcb -> JLC04161H-7628, 4 layers, 1.6 mm
Usage: VARIANT=hub|direct python3 postprocess.py"""
import json, os
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VARIANT = os.environ.get("VARIANT", "hub")
pcb = os.path.join(PRJ, "backplane.kicad_pcb" if VARIANT == "hub" else "backplane_direct.kicad_pcb")
D = lambda n, t, th, mat, er, lt=0.02: f'\t\t\t(layer "dielectric {n}" (type "{t}") (thickness {th}) (material "{mat}") (epsilon_r {er}) (loss_tangent {lt}))\n'
C = lambda name, th: f'\t\t\t(layer "{name}" (type "copper") (thickness {th}))\n'
HEAD = '''		(stackup
			(layer "F.SilkS" (type "Top Silk Screen"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
'''
TAIL = '''			(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen"))
			(copper_finish "ENIG")
			(dielectric_constraints no)
		)
'''
if VARIANT == "hub":
    body = (C("F.Cu", 0.035) + D(1, "prepreg", 0.2234, "2116 0.127 + 2313 0.0964 (NP-155F)", 4.14) +
            C("In1.Cu", 0.0152) + D(2, "core", 0.30, "FR4 core 0.30 (NP-155F)", 4.6) +
            C("In2.Cu", 0.0152) + D(3, "prepreg", 0.4168, "7628 x2 0.2084 each (NP-155F)", 4.4) +
            C("In3.Cu", 0.0152) + D(4, "core", 0.30, "FR4 core 0.30 (NP-155F)", 4.6) +
            C("In4.Cu", 0.0152) + D(5, "prepreg", 0.2234, "2313 0.0964 + 2116 0.127 (NP-155F)", 4.14) +
            C("B.Cu", 0.035))
    tag = "JLC06161H-2116 6L 1.6mm"
else:
    body = (C("F.Cu", 0.035) + D(1, "prepreg", 0.2104, "7628 x1 (NP-155F)", 4.4) +
            C("In1.Cu", 0.0152) + D(2, "core", 1.065, "FR4 core (NP-155F)", 4.43) +
            C("In2.Cu", 0.0152) + D(3, "prepreg", 0.2104, "7628 x1 (NP-155F)", 4.4) + C("B.Cu", 0.035))
    tag = "JLC04161H-7628 4L 1.6mm"
s = open(pcb).read()
if "(stackup" not in s:
    s = s.replace("\t(setup\n", "\t(setup\n" + HEAD + body + TAIL, 1)
    open(pcb, "w").write(s)
pro = pcb.replace(".kicad_pcb", ".kicad_pro")
if os.path.exists(pro):
    d = json.load(open(pro))
    classes = d["net_settings"]["classes"]
    for c in classes:
        if c["name"] == "Default":
            c.update(clearance=0.127, track_width=0.2, via_diameter=0.6, via_drill=0.3)
    if VARIANT == "hub" and not any(c["name"] == "PCIE_85R" for c in classes):
        base = dict([c for c in classes if c["name"] == "Default"][0])
        base.update(name="PCIE_85R", clearance=0.2, track_width=0.35, diff_pair_width=0.35, diff_pair_gap=0.2,
                    diff_pair_via_gap=0.25, via_diameter=0.6, via_drill=0.3,
                    description="PCIe Gen4/5 85 ohm diff, L1/L6 microstrip over In1/In4 GND (0.2234 mm). START VALUE from IPC-2141 estimate; confirm with JLC impedance calculator before routing")
        classes.append(base)
        usb = dict(base); usb.update(name="USB2_SATA_90R", track_width=0.3, diff_pair_width=0.3, diff_pair_gap=0.2,
                    description="USB2 90 ohm / SATA 85-100 ohm diff, L1/L6 microstrip. START VALUE; confirm with JLC calculator")
        classes.append(usb)
    d["board"]["design_settings"]["rules"]["min_hole_clearance"] = 0.25
    d.setdefault("text_variables", {})["STACKUP"] = tag
    json.dump(d, open(pro, "w"), indent=2)
print("postprocess ok", VARIANT, tag)
