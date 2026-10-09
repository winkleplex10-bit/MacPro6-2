# BP rev A2 (v2 copy) work log: CPU PEG x8/x8 + slot B (Face S lanes 4-7) + REFCLK1 / PERST1# / CLKREQ1# / WAKE1#
Copy of kicad/macpro62-backplane rev A1 (original untouched; baseline checksums /workspace/scratch/v2_baseline/originals.sha256).
Decision (Aidan, 2026-10-08 ~19:35 ET): PEG 2x8, Face P x8, slot B = PEG lanes 8-11 via a BP re-route to J10 lanes 4-7; REFCLK1 from a spare
PCH CLKOUT over CPU-LINK reserved pins (no BP buffer); PERST1# = PLTRST# AND FACE_S_RDY on the BP, CLKREQ1# terminated, WAKE1# ORed into WAKE0#.
Rules: 4 layers; existing HS pairs keep 0 skew / 2-2 vias; no rip-up; protect HS/SATA/USB2; don't push.

## 19:41 ET: v2 copy made (work/ not copied)
- Routing study on A1 (read-only): J1 FP lanes 8-11 sit at J1 X 172-178 (right of lanes 0-7, X 155-171); J10 lanes 4-7 pads at (126-135, 87-96).
  The lanes 0-7 bundle (L1 RX + L3 TX interleaved) and the FP_REFCLK/TX0 (L3) + RX0 (L4) loops round the J9 tip lie between them.
  A direct path must cross 16+ pairs with no free signal layer (L2 = L1 reference, L4 = L3 reference), so the new pairs go AROUND J9
  (freed J9 lanes 8-15 corridor -> J9 outer side -> north of the J9 tip -> J10 outer side).

## 19:48 ET: v2 PARKED (Aidan chose the HYBRID v3 storage layout)
State at park: copy of A1 only. No board/schematic/tool edits made. Routing study (above + this note) concluded the
FP lanes 8-11 -> J10 lanes 4-7 route has no planar path except AROUND J9 + over the J4 apex + down J10's outer side, which
crosses ~12 Face S AUX LS nets (3V3_AUX_S, FS_SMB_SDA/SCL, FS_PWR_EN/GOOD, FS_MOD_LED_N, FS_THERM_*, FS_PRSNT_N) and the
USB2_FACES L3/L4 stack; est. 120-130 mm per lane. Not started. Superseded by v3 (kicad/macpro62-backplane-v3).
