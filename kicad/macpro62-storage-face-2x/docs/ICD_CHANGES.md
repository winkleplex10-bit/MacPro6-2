# S2X (2-drive switchless Face S module): host-side changes, deviations and approvals
Status 2026-10-08 18:30 ET. Proposals only: `macpro62-interface-control.md`, the CB (`kicad/macpro62-lga1700`) and the BP were NOT modified.

## 1. What the module needs from the host
| J1 (MCIO 124) | Slot A (J5) | Slot B (J6) |
|---|---|---|
| Lanes | 0-3 (FS_PET/PER0-3, as today) | **4-7 (new; BP rev A leaves them unconnected)** |
| REFCLK | REFCLK0± (B11/B12), as today | **REFCLK1± (B29/B30), needs a source** |
| PERST# | PERST0# (A11) | **PERST1# (A29), needs a driver** |
| CLKREQ# / WAKE# | CLKREQ0# B8 / WAKE0# B9 | CLKREQ1# B26 / WAKE1# B27 |
| MCIO_PRSNT# | A12 tied to GND | A30 tied to GND |
On the module: each PERST# is re-buffered (2 x 2N7002, pull-up to that slot's own 3V3) so a slot without power never back-drives the host;
CLKREQ#/WAKE# go straight to J1 (open drain, host side pulls up). With BP rev A only **slot A** works; slot B needs the changes below.

## 2. Host changes (CPU board / BP / ICD)
1. **Lane source for slot B: CPU PEG in 2 x 8 bifurcation.** The Face S x4 today is CPU PEG60 (x4, cannot be split). ADL-S/RPL-S PEG x16
   supports only 1x16 or 2x8 (no x8+x4+x4). Use PEG 2x8: Face P = PEG port 1 at x8, slot B = PEG port 2 trained at x4.
   - Face P loses nothing: the Navi 23 GPU is natively PCIe 4.0 **x8**.
   - Z790 supports PEG x8/x8 (CB plan line 43). The bifurcation strap (CFG[6:5]) or FSP/BIOS setting is **[Unverified]** for this CB.
   - **CPU-LINK pinout is unchanged:** FP lanes 8-11 already cross CPU-LINK. The **BP** re-routes FP lanes 8-11 from J9 to J10 lanes 4-7
     (plus a redriver site per the G5 loss budget if needed). FP lanes 12-15 become unused.
   - Alternative without bifurcation: PCH RP5-8 (x4, today reserved for the AQC107). That needs a CPU-LINK re-pin (PCH lanes are not on CPU-LINK for Face S).
2. **REFCLK1 for slot B.** Pick one:
   - (a) the CB routes a spare PCH CLKOUT_SRC over 2 of the 14 CPU-LINK RSVD fingers (CB + ICD §2 change; the SRC choice is part of U-12), or
   - (b) **no CB change:** a 1:2 HCSL fan-out buffer on the BP from FS_REFCLK (e.g. Renesas 9DBL0242 / 9DBV0241, public datasheets) drives REFCLK0 and REFCLK1 on J10.
   The module has no clock buffer (decision 17:10: no part, no extended fee).
3. **PERST1#** on the BP: PLTRST# ∧ FACE_S_RDY (same logic as PERST0#). **CLKREQ1#** terminated on the BP (clock always on, like CLKREQ0#). **WAKE1#** ORed into CPU-LINK WAKE0#.
4. **ICD text:** §5 "Set B (REFCLK1, PERST1#, …): not driven by BP rev A" → driven from BP rev B for S2X; §12 lane map: Face S = CPU PEG60 x4 (slot A) + PEG port 2 x4 (slot B), Face P = PEG x8;
   §2 FS_REFCLK/RSVD per option 2a or 2b; §11 FACE_S_SMB: INA238 at 0x40 (same address as the INA228 slot), TMP1075 0x48/0x49, EEPROM 0x50 (unchanged map).

## 3. Deviations (need Aidan's OK)
- **D-2X-1 hot-spot centroid.** The two SSD controllers sit at about (58, 75) in the module frame; face spec R3 [Proposal] puts the hot spot near (52, 69.5). The die-pad window on L1 (X 40.1-63.7, Y 58.6-80.2, 151 thermal vias) and the B-side gap-pad areas follow the real location.
- **D-2X-2 data-lane polarity inversion.** On both slots, every data lane's P/N is swapped at the M.2 socket (host TX and module TX). PCIe receivers must support lane polarity inversion (PCIe Base spec, Physical Layer "Lane Polarity Inversion": detected and corrected in Polling during link training), so the link works, but it is a deliberate dependency on that feature. It lets each of 16 data pairs route with 0 skew and at most 2 vias without crossing pairs. **REFCLK polarity is not inverted** (no inversion for REFCLK; kept with a crossed via corner, skew trimmed to −0.001 mm). Lane *reversal* (optional in the spec) is **not** used.
- **D-S1 no X-bracket** (as SM-1).
- **INA238** (C2868250) instead of the face-spec INA228 (C2887910 has 0 JLC stock). Same 0x40 address scheme; register map differs (16-bit vs 20-bit) → firmware note. **INA226** (C49851, $0.76) is a further cost option (≈ $7.5/board) and needs approval.
- No PCIe AC caps on the module: M.2 SSDs carry their own TX caps; host TX caps are on the CB.

## 4. Layout notes
- 4L JLC04161H-7628: L1 signal + GND pour, L2 solid GND, L3 GND + 3V3_A / 3V3_B islands (X 1-57.6 / 58.4-103, Y 55-81), L4 (B) all parts + signals.
- 18 HS pairs (8 lanes x 2 + 2 REFCLK) at 0.26/0.13 (85 Ω; JLC calc 83.1 Ω for 0.26/0.125). AM3 pair 0 vias on B; every other HS net exactly 2 vias. Data skew 0.000 mm by construction.
- Power: 12 V lugs → TPS259470 eFuse → 2 mΩ shunt (INA238) → 2 x TPS54331 3 A bucks (one per slot) → L3 islands → socket 3V3 pin combs. Shunt R5 rotated 180° (placement only).
- PG: FACE_PWR_GOOD = 3V3_A ∧ 3V3_B (Q5-Q7); Q7 moved to (85, 58.5) inside island B.
