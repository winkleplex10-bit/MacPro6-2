> **Rev 2026-10-02 ≈ 14:55 ET:**
> - **Geometry:** rebuilt on the new stack. The plate is 1.4 thick and glued, with the flex flat and no pocket, which moves everything 0.2. HDMI is back on the stock +X side: MOD-H is fitted rotated 180° into JM11 (rot 0).
> - **Routing status** (`python3 tools/build_modules.py build|route|finish [mod]`, then kicad-cli DRC; reports in `mod_*/drc_report.txt`, lengths in `mod_*/route_report.json`):
>   - **mod_usba:** complete. DRC 0 errors (2 silk warnings). Skew D −2.6, SSRX +2.7, SSTX +2.6, set by the THT pitch; compensate on the main board.
>   - **mod_hdmi:** complete. DRC 0 errors (1 silk warning). Skew CK −0.58, D0 −0.50, D1 −0.65, D2 −0.52.
>   - **mod_usbc:** **open.** 8 unconnected (A-row inner group CC1 / D± A / SBU1 / SSRX2±) and 1 clearance (CC2–shell tab 0.073). The placeholder shell tabs block the centre channel. Next step: the real HYCW417 land pattern plus a hand fan-out on L2 under the stiffened port.
> - **Router:** the DSN now offers a second via of 0.40 / 0.20 (JLC 2-layer FPC standard; extra cost only below a 0.15 hole) and allows max 500 passes.
> - **TDR coupons:** `tools/build_tdr.py` → `tdr/tdr_coupon_c50` (90 / 100 Ω solid and bend-hatch, 50 Ω SE) and `tdr/tdr_coupon_a25` (MOD-A 90 Ω cross-hatch). DRC 0.
> - **Pin 1:** `tools/check_pin1_3d.py` → `pin1_check.json`, `pin1_check_3d.png`. C1, C4, A1, A3 and HDMI all OK.
> - **Parts:**
>   - EEPROM BL24C02F-NTRC (C2828222).
>   - USB-A HC-USB3.0-L137-WJ (C7501870).
>   - ESD on the main board under each JMn: TPD4E02B04DQAR / TPD4E05U06DQAR, D200–D228.

# MP62 swappable port modules (D-IO16), rev A0 2026-10-02 ≈ 12:45 ET

Each USB-C, USB-A and HDMI port is a **flex-only module**. The receptacle is soldered straight to a JLC 2-layer FPC, like the stock audio jack on its flex. There is **no rigid PCB**. The FPC has a local FR4 1.0 stiffener under the port and a second one under the board-to-board header. The RJ45 jacks stay on the main board.

```
        plate (R 111.2) ── mouth normal to the plate (full plug seating)
            │ receptacle shell ── SUS304 0.2 sleeve (bonded) ── 1.0 collar ── under the clamp plate (MJF PA12 1.6, M2 → SMT standoffs on the main board)
            │ receptacle body (SMD pads / THT legs)
  ═══════════ FPC 0.11 ── PSA 0.05 ── FR4 stiffener 1.0 ── rests on the cradle ledges (MJF PA12, one cradle per group)
  ╰─ flap ─╮  180° C-fold, R 2.3–3.2
           ╰──── return run under the module ──── paddle: FR4 1.0 + DF40C-50DP (faces down) + 24C02 ID EEPROM + 100 nF
                                                   ▼ mates with DF40C-50DS (JM1–JM11) on the main board F side
```

## Modules

| Module | Slots | Receptacle (LCSC) | Mount | Stiffener (port) | Flat length | Flap / fold R | Sleeve seat → collar |
|---|---|---|---|---|---|---|---|
| MOD-C (`mod_usbc/`) | C1–C6 (one design; O-column modules are the same part rotated 180°) | HOAUC HYCW417-USBC24-180B (C5342202), vertical, **all SMD**, L 10.0. $1.13 at 1, $0.84 at 30. Only 196 in stock. | SMT only | 12.0 × 8.8 | 38.8 | 1.5 / 3.2 | 5.0 |
| MOD-A (`mod_usba/`) | A1–A4 | kinghelm KH-3.0AF180ZJ-11.5JB (C2979037), vertical USB 3.0, THT signal pins + shell legs, H 11.5, ≈ $0.16. **Only 2 in stock at 12:45 ET; 4 needed.** Second source: Hong Cheng HC-USB3.0-L137-WJ (C7501870, 645 in stock, ≈ $0.12), but it is H 13.7, which would drop the seat 2.2 mm and the fold R to about 1.2. Re-run modules_geom with CONN_H 13.7 before switching. | Selective solder through FPC + drilled FR4 | 16.8 × 8.8 | 39.7 | 0.5 / 2.3 | 6.65 |
| MOD-H (`mod_hdmi/`) | HDMI | HOAUC HYC79-HDMIA19-105 (C711353), vertical, SMD signals + THT shell legs, $0.49 at 1, 2,365 in stock | SMT + selective solder | 19.2 × 9.4 | 43.4 | 0.5 / 2.7 | 5.7 |

No all-SMD vertical USB-A 3.0 or HDMI receptacle is stocked at LCSC. Both use THT legs that pass through the FPC and the drilled FR4 stiffener. JLC FPC assembly offers THT (wave or selective solder, $23.57 per fixture). The leg tips sit inside the cradle's ledge window. Keep ≥ 0.5 mm below the tips.

## Force path (plug loads never pass through the flex or the solder joints)

| Load | Value (spec) | Path |
|---|---|---|
| Insertion (push) | USB-C ≤ 20 N, USB-A 3.0 ≤ 35 N, HDMI ≤ 44 N | Receptacle body bears on the FPC (compression only) → PSA → FR4 stiffener → cradle ledges (2 × 0.85 mm × stiffener length; HDMI 2 × 1.15). About 1 MPa on PA12. |
| Withdrawal (pull) | USB-C 8–20 N, USB-A ≥ 10 N, HDMI ≤ 39 N | Shell → bonded SUS304 sleeve → collar → clamp plate → 2 × M2 screws → blind SMT standoffs on the main board. The pads see no tension. |
| Side / levering | Abuse | Sleeve in the clamp-plate aperture (0.1 clearance) + stiffener in the cradle pocket walls (0.1 clearance). |
| Main-board DF40 | 0 | The fold leaves slack. The DF40 carries only its own retention. |

Clamp plate deflection estimate (PA12, E 1.7 GPa, 1.6 thick, about 30 wide): 20 N at mid-span between the two C posts (21.5 mm) gives ≈ 0.24 mm, and ≈ 0.05 mm at the C1 overhang. That is acceptable, but add a rib or a third post if A0 parts flex.

Sleeve bond: solder if the shell is tin plated, structural epoxy (e.g. 3M DP420) if it is stainless. **TO MEASURE** (shell plating). The sleeve also grounds to the module's GND ring (coverlay opening) and carries a spring finger to the metal I/O frame.

## PMI-50 standard module interface (DF40C-50DP on the module ↔ DF40C-50DS on the main board)

Row A holds the odd pins (2k−1) and row B the even pins (2k).

| k | A | B | k | A | B |
|---|---|---|---|---|---|
| 1–6 | VBUS | VBUS | 18 | CC1 | HPD |
| 7–8 | GND | GND | 19 | CC2 | UTIL |
| 9 | HS0_P | HS2_P | 20 | GND | GND |
| 10 | HS0_N | HS2_N | 21 | ID_SCL | ID_SDA |
| 11 | GND | GND | 22 | 3V3_MOD | PRSNT# |
| 12 | HS1_P | HS3_P | 23 | LED# | GND |
| 13 | HS1_N | HS3_N | 24–25 | GND | GND |
| 14 | GND | GND | | | |
| 15 | USB2_DP | SBU1 | | | |
| 16 | USB2_DN | SBU2 | | | |
| 17 | GND | GND | | | |

- **Pin budget:** 12 VBUS pins (0.3 A each, 3.6 A total; USB-C 3 A is 83 % of rating), 17 GND, 21 signals.
- **PRSNT#:** tied to GND on the module. It drives U97 (TCA9555) inputs, and U97's INT# goes to PD_INT_N.
- **ID EEPROM:** a 24C02 at 0x50 on every module, behind U95/U96 (TCA9548A at 0x70/0x71). Channels: C1–C6 = U95 ch 0–5, A1–A2 = U95 ch 6–7, A3–A4 = U96 ch 0–1, HDMI = U96 ch 2.
- **USB-C mapping:** HS0 TX1, HS1 RX1, HS2 TX2, HS3 RX2.
- **USB-A mapping:** HS0 SSTX, HS1 SSRX. HS2/HS3, CC, SBU and HPD are not connected.
- **HDMI mapping:** HS0 D2, HS1 D1, HS2 D0, HS3 CLK. SBU1/2 carry DDC SCL/SDA, HPD is HPD, UTIL is CEC (not connected), and VBUS is +5V.

## Flex construction (JLC FPC)

- **Layers:** 2-layer PI, 0.11 mm finished. L1 has the signals (microstrip) and L2 is solid GND. The VBUS strip runs on L2 at the tail edge.
- **Impedance:** 90 Ω differential for USB and 100 Ω for TMDS. Set the widths with the JLC FPC impedance calculator. JLC does **not** measure impedance on FPC, so order a coupon and TDR it.
- **EMI silver film (optional):** User.2 over L1. It changes the trace widths. It needs ≥ 2 coverlay openings Ø ≥ 1.0 to GND about every 30 mm, must stay ≥ 0.8 from pads, and is removed under stiffeners.
- **Stiffeners:** FR4 1.0 on the B side, extending ≥ 1.0 beyond the pads, minimum width 3. Stainless 0.2 is the alternative if FR4 chips (JLC warns about this).
- **Bend zone:** User.4 plus a rule area (no vias or pads). Bend radius ≥ 2.3 mm, well above 10 × the thickness.
- **Layer use:** User.1 is the stiffener outline and User.3 the cradle ledge footprint.

## Swap procedure (system off)

1. Remove the 2 clamp-plate screws for the group and lift the plate.
2. Lift the module out of its cradle pocket.
3. Unplug the DF40 by lifting straight up at the paddle stiffener.
4. Reverse to fit. DF40 is rated for about 30 mating cycles, so log the swaps.

## Costs (per module, LCSC unit price, prototype quantity)

| Item | MOD-C | MOD-A | MOD-H |
|---|---|---|---|
| Receptacle | 1.13 | 0.16 | 0.49 |
| DF40C-50DP (module) + DF40C-50DS (main board) | 0.6 + 0.84 | same | same |
| 24C02 + 0201 cap | ≈ 0.2 | ≈ 0.2 | ≈ 0.2 |
| SUS304 sleeve (laser cut + bent) | 1–3 | 1–3 | 1–3 |
| FPC + 2 FR4 stiffeners | JLC FPC 5–10 pcs about $15–30 per design, plus a stencil | | |
| Assembly | SMT setup + $23.57 THT fixture (MOD-A, MOD-H) | | |

## Rebuild

```
python3 ../macpro62-io-board/tools/modules_geom.py        # modules.json (plate features → geometry + checks)
python3 ../macpro62-io-board/tools/make_fps_modules.py    # MP62_MOD.pretty + main-board cradle footprints
python3 tools/build_modules.py                            # mod_usbc / mod_usba / mod_hdmi
for m in mod_usbc mod_usba mod_hdmi; do kicad-cli pcb drc -o $m/drc_report.txt $m/$m.kicad_pcb; done
```

## Status

- **Outlines, stiffeners, bend zones, footprints:** placed. DRC 0 / 0 on all three (`*/drc_report.txt`).
- **Routing:** not started. No nets are assigned yet; route after the land patterns are confirmed.
- **Placeholders:** the receptacle, DF40 and EEPROM land patterns are placeholders. Check them against the drawings.
- **EEPROM part:** the WLCSP-4 EEPROM (AT24CSW020-UUM0B class) has no LCSC number yet. If the paddle can grow by 1.5 mm, fall back to a SOT-23-5 24C02.
- **Geometry basis:** the geometry is for the default build (axis normal to the plate). Re-run `modules_geom.py` on the `_tilt12p5` features to get the stock-tilt variant.
