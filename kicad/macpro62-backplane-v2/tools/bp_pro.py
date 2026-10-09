"""Write net classes / patterns into backplane.kicad_pro (rev A1, 4L)."""
import json, os, copy
PRJ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
p = os.path.join(PRJ, "backplane.kicad_pro"); pro = json.load(open(p))
ns = pro["net_settings"]; base = copy.deepcopy([c for c in ns["classes"] if c["name"] == "Default"][0])
def cls(name, clr, tw, dpw=None, dpg=None, prio=0):
    c = copy.deepcopy(base); c.update({"name": name, "clearance": clr, "track_width": tw, "via_diameter": 0.45, "via_drill": 0.25})
    if dpw: c.update({"diff_pair_width": dpw, "diff_pair_gap": dpg, "diff_pair_via_gap": 0.25})
    c["priority"] = prio
    return c
ns["classes"] = [cls("Default", 0.1, 0.15, prio=2147483647), cls("PCIE_85R", 0.1, 0.26, 0.26, 0.125, 0), cls("USB2_SATA_90R", 0.1, 0.24, 0.24, 0.15, 1),
                 cls("PWR", 0.15, 0.3, prio=2), cls("PWR_FINE", 0.1, 0.2, prio=3)]
ns["netclass_patterns"] = [{"netclass": "PCIE_85R", "pattern": pat} for pat in ("FP_TX*", "FP_RX*", "FS_TX*", "FS_RX*", "*REFCLK*")] + \
    [{"netclass": "USB2_SATA_90R", "pattern": pat} for pat in ("USB2_*", "SATA0_*", "*USB*_D?")] + \
    [{"netclass": "PWR_FINE", "pattern": pat} for pat in ("3V3_SB", "DVDD")] + \
    [{"netclass": "PWR", "pattern": pat} for pat in ("VIN*", "5V_SBY", "12V_*", "11V_*", "3V3_AUX_*", "3V3_M2", "SW_*", "VBUS*")]
ns["netclass_assignments"] = None
r = pro["board"]["design_settings"]["rules"]
r.update({"min_clearance": 0.1, "min_track_width": 0.09, "min_via_diameter": 0.45, "min_through_hole_diameter": 0.25, "min_hole_clearance": 0.2,
          "min_hole_to_hole": 0.2, "min_copper_edge_clearance": 0.4, "min_via_annular_width": 0.1})
json.dump(pro, open(p, "w"), indent=2)
print("pro updated")
