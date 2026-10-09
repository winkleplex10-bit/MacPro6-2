# CB (LGA1700) v2 copy work log: REFCLK1 for Face S slot B + PEG 2x8 bifurcation strap
Copy of kicad/macpro62-lga1700 (original untouched). Floorplan only (no nets, not routed).

## 19:41 ET: v2 copy made
- Sources: Intel 743844 rev 015 (13th/14th Gen Core datasheet vol 1, local mp62-spec-refs/lga1700/cpu_rpls_ds1.pdf) Table 51 + CFG[17:0] (p.175);
  Intel 655258 (12th Gen datasheet vol 1, edc.intel.com) same table; LGA1700 ballout 743844-001: CFG[5] = land H11, CFG[6] J13, CFG[2] J11,
  VCC_CFG_PU_OUT N12. Z790 PCH ballout 743835-001: CLKOUT_PCIE_P13 = P3, CLKOUT_PCIE_N13 = P4, GPP_H7/SRCCLKREQ13# = N50.
  ARK: Z790 "PCIe 5.0: 1x16 or 2x8, PCIe 4.0: 1x4"; B760 "PCIe 5.0: 1x16, PCIe 4.0: 1x4" (no 2x8).

## 19:48 ET: v2 PARKED (Aidan chose the HYBRID v3 storage layout)
State at park: copy of the v1 floorplan only; no file edited. Strap findings kept above for reference (CFG[6:5]/CFG[2], Table 51,
743844 rev 015; Z790 1x16 or 2x8, B760 1x16 only). Superseded by kicad/macpro62-lga1700-v3.
