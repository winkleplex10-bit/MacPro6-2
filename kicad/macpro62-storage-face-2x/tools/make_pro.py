"""Project file (from the backplane A1 template): net classes, patterns and JLC 4L rules for S2X. Writes NAME.kicad_pro / .kicad_dru / fp-lib-table."""
import json, os, copy, sys
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NAME = sys.argv[1] if len(sys.argv) > 1 else "macpro62-storage-face-2x"
pro = json.load(open("/workspace/kicad/macpro62-backplane/backplane.kicad_pro"))
pro["meta"]["filename"] = NAME + ".kicad_pro"
pro["sheets"] = [[pro["sheets"][0][0], ""]] if pro.get("sheets") else []
pro["boards"] = []
ns = pro["net_settings"]; base = copy.deepcopy([c for c in ns["classes"] if c["name"] == "Default"][0])
def cls(name, clr, tw, dpw=None, dpg=None, prio=0, vd=0.45, vh=0.25, desc=""):
    c = copy.deepcopy(base); c.update({"name": name, "clearance": clr, "track_width": tw, "via_diameter": vd, "via_drill": vh, "description": desc})
    if dpw: c.update({"diff_pair_width": dpw, "diff_pair_gap": dpg, "diff_pair_via_gap": 0.25})
    c["priority"] = prio; return c
ns["classes"] = [cls("Default", 0.1, 0.15, prio=2147483647),
                 cls("PCIE_85R", 0.1, 0.26, 0.26, 0.13, 0, desc="PCIe Gen4 + REFCLK 85 ohm diff, L1 (ref L2) / L4 (ref L3), JLC04161H-7628"),
                 cls("PWR_12V", 0.1, 0.8, prio=1, vd=0.6, vh=0.3, desc="+12V after the lugs (<= 2 A load; lug-to-lug trunk is a pour)"),
                 cls("PWR_3V3", 0.15, 0.8, prio=2, vd=0.6, vh=0.3, desc="3V3 slot rails 3 A + buck switch nodes"),
                 cls("PWR_AUX", 0.1, 0.3, prio=3, desc="3V3_AUX")]
ns["netclass_patterns"] = [{"netclass": "PCIE_85R", "pattern": p} for p in ("PCIE_*", "REFCLK_*")] + \
    [{"netclass": "PWR_12V", "pattern": p} for p in ("+12V*",)] + [{"netclass": "PWR_3V3", "pattern": p} for p in ("3V3_A", "3V3_B", "PH_*")] + \
    [{"netclass": "PWR_AUX", "pattern": "3V3_AUX"}]
ns["netclass_assignments"] = None
r = pro["board"]["design_settings"]["rules"]
r.update({"min_clearance": 0.1, "min_track_width": 0.09, "min_via_diameter": 0.45, "min_through_hole_diameter": 0.25, "min_hole_clearance": 0.2,
          "min_hole_to_hole": 0.25, "min_copper_edge_clearance": 0.4, "min_via_annular_width": 0.1})
pro.setdefault("text_variables", {})["STACKUP"] = "JLC04161H-7628 4L 1.6mm"
json.dump(pro, open(os.path.join(PRJ, NAME + ".kicad_pro"), "w"), indent=2)
open(os.path.join(PRJ, NAME + ".kicad_dru"), "w").write('''(version 1)
# S2X: keep pours >= ~3w away from the 85R pairs (impedance solved as edge-coupled microstrip, no coplanar ground)
(rule "hs_pour_clearance"
  (constraint clearance (min 0.4))
  (condition "A.hasNetclass('PCIE_85R') && B.Type == 'Zone'"))
# exposed thermal copper: mask openings intentionally over GND pours
''')
open(os.path.join(PRJ, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "MP62_S2X")(type "KiCad")(uri "${KIPRJMOD}/MP62_S2X.pretty")(options "")(descr "MP62 S2X footprints"))\n)\n')
print("pro written", NAME)
