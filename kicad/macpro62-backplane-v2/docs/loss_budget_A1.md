# BP rev A1 (BP-G4) PCIe loss budget: why the Gen5 redrivers are removed

Generated 2026-10-04 (ET) from the as-routed board (`tools/bp_skew.py`, `tools/bp_zreport.py`).
Method and per-segment assumptions follow architecture spec v0.2 §3.6 [Estimate]. The only changes are the as-routed BP length and the measured impedance.

## As-routed BP channel
- Lane copper length, J1 pad to MCIO pad: **29.2 mm (FS_RX0) to 68.5 mm (FP_RX0)**. Both vias are included as 1.6 mm each. Most FP lanes are 30–57 mm.
- Intra-pair skew after tuning: **0.000 mm** on all 40 lanes and both REFCLKs. The ≤ 5 mil (0.127 mm) target is met.
- Impedance from the 2-D field solver, JLC04161H-7628:
  - L1 RX 0.26/0.125: **83.1 Ω**
  - L3 TX 0.21/0.127: **86.4 Ω**
  - L4 breakout: 83.1 Ω
  - USB2/SATA 0.24/0.15: 90.0 Ω
  - All are within ±10 % of the 85 Ω and 90 Ω targets.
- The GND pour is held ≥ 0.5 mm from the 85 Ω pairs (`backplane.kicad_dru`), so the solved microstrip/stripline geometry stays valid.

## Gen4 budget, 28 dB @ 8 GHz

| Segment | dB @ 8 GHz |
|---|---|
| Root package + module/CPU-board traces + COM-HPC | 5–8.4 |
| CPU-LINK Mini Cool Edge | ~0.5 |
| **BP A1, 29–69 mm at 0.5–0.6 dB/in** | **0.6–1.6** |
| MCIO receptacle × 2 | 0.3 |
| MCIO cable 0.2–0.4 m | 0.6–1.2 |
| Face board (module budget ≤ 1.8 dB, face spec §4) | 0.5–1.8 |
| Endpoint package | 2–3 |
| **Total** | **≈ 9.5–16.8 dB** |

That leaves **≈ 11–18 dB of margin** before reflection and crosstalk penalties from the 4 separable interfaces. Gen4 needs no redriver.

## Decision
- The 5 × DS320PR810 sites (BP-G5) are **removed from the A1 layout**, not just DNP.
  - The redrivers only pay off at Gen5 (36 dB @ 16 GHz, ≈ 18–35 dB estimated).
  - Keeping the footprints would need the 6-layer stackup, plus the AC-cap and redriver breakout area in the lane field.
- The host firmware must force Gen4 on BP-G4: `pcie_gen_max = 4` reported by the BP.
- A Gen5 BP stays a separate future variant (BP-G5, 6L). See `variants/fp6_floorplan_6L/`.
- Saving: about $95–115 per BP in redrivers (LCSC C6539580, $18.75–22.99 each) plus the 6L → 4L fab delta. See the cost file.
- Vendor S-parameters for the Mini Cool Edge and the MCIO cable are still TBD. A simulation before any Gen5 attempt is still required.
