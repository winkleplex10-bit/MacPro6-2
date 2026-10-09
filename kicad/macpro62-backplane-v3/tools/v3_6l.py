"""BP v3 -> 6 layers, JLC06161H-2116 (1.6 mm). Existing copper keeps its KiCad layer:
F.Cu L1 (RX microstrip, ref In1) | In1 L2 GND | In2 L3 (TX stripline, ref In1 / In3 pour) | In3 L4 NEW signal (slot B, ref In4 / In2 pour)
| In4 L5 GND (new solid plane) | B.Cu L6 (ex-L4 GND + breakout, now ref In4).   usage: v3_6l.py SRC DST"""
import sys, re, pcbnew
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
if '"In3.Cu"' not in s:
    s = s.replace('(6 "In2.Cu" signal "L3_SIG_TX_PWR")', '(6 "In2.Cu" signal "L3_SIG_TX_PWR")\n\t\t(8 "In3.Cu" signal "L4_SIG_SLOTB")\n\t\t(10 "In4.Cu" signal "L5_GND")', 1)
    s = s.replace('(2 "B.Cu" signal "L4_GND_BRK")', '(2 "B.Cu" signal "L6_GND_BRK")', 1)
D = lambda n, t, th, mat, er, lt=0.02: f'\t\t\t(layer "dielectric {n}" (type "{t}") (thickness {th}) (material "{mat}") (epsilon_r {er}) (loss_tangent {lt}))\n'
C = lambda name, th: f'\t\t\t(layer "{name}" (type "copper") (thickness {th}))\n'
if "(stackup" not in s:
    st = ('\t\t(stackup\n\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))\n\t\t\t(layer "F.Paste" (type "Top Solder Paste"))\n\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))\n'
          + C("F.Cu", 0.035) + D(1, "prepreg", 0.2234, "2116 0.127 + 2313 0.0964", 4.137) + C("In1.Cu", 0.0152) + D(2, "core", 0.30, "FR4 core 0.30", 4.6)
          + C("In2.Cu", 0.0152) + D(3, "prepreg", 0.4168, "7628 x2 0.2084", 4.4) + C("In3.Cu", 0.0152) + D(4, "core", 0.30, "FR4 core 0.30", 4.6)
          + C("In4.Cu", 0.0152) + D(5, "prepreg", 0.2234, "2313 0.0964 + 2116 0.127", 4.137) + C("B.Cu", 0.035)
          + '\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))\n\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))\n\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))\n\t\t\t(copper_finish "ENIG")\n\t\t\t(dielectric_constraints no)\n\t\t)\n')
    s = s.replace("\t(setup\n", "\t(setup\n" + st, 1)
open(dst, "w").write(s)
b = pcbnew.LoadBoard(dst)
b.SetCopperLayerCount(6)
ls = b.GetEnabledLayers(); ls.AddLayer(pcbnew.In3_Cu); ls.AddLayer(pcbnew.In4_Cu); b.SetEnabledLayers(ls)
gnd = b.FindNet("GND")
ref = [z for z in b.Zones() if z.GetZoneName() == "L2_GND"][0]
for z in b.Zones():
    if z.GetZoneName() == "L4_GND" and z.GetLayer() == pcbnew.B_Cu: z.SetZoneName("L6_GND")
have = {z.GetZoneName() for z in b.Zones()}
for L, nm, pr in ((pcbnew.In3_Cu, "L4_GND", 0), (pcbnew.In4_Cu, "L5_GND", 0)):
    if nm in have: continue
    z = ref.Duplicate(); z.SetLayer(L); z.SetZoneName(nm); z.SetNet(gnd); z.SetAssignedPriority(pr); b.Add(z)
# keep-out rule areas that cover all inner layers get In3/In4 too
for z in b.Zones():
    if z.GetIsRuleArea():
        lset = z.GetLayerSet()
        if lset.Contains(pcbnew.In2_Cu) and lset.Contains(pcbnew.In1_Cu): lset.AddLayer(pcbnew.In3_Cu); lset.AddLayer(pcbnew.In4_Cu); z.SetLayerSet(lset)
b.Save(dst)
print("6L ok", dst, b.GetCopperLayerCount(), sorted(z.GetZoneName() for z in b.Zones() if not z.GetIsRuleArea()))
