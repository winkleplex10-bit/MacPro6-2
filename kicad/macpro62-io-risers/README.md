# MP62 I/O port risers (D-IO14), rev A0 2026-10-02 ≈ 10:50 ET

Five small tilted riser PCBs carry the I/O-wall ports. Each port axis is radial to the I/O cover (R 111.2 from D0 18.0 / 16.5), and each mouth is tangent to the plate face.

| PCB | Fit | Ports | Tilt | Size | Link to the main board | Power |
|---|---|---|---|---|---|---|
| `riser_c` | × 2 (RC_H as drawn, RC_O rotated 180°) | 3 × USB-C SHOU HAN TYPE-C 24PLT-H10.5 (C3151750) | −5.27 / +5.47° | 16.8 × 34.2, 2 notches for the frame standoff | DF40C-80DS-0.4V(51) C312960 + FPC jumper (2 × DF40C-80DP) → main JR1/JR2 | 6 × VBUS + 2 × GND pogo targets |
| `riser_a` | × 2 (RA_H, RA_O rotated) | 2 × USB-A KH-3.0AF180ZJ-11.5JB (C2979037) | −5.25 / +5.51° | 21.4 × 21.7 | DF40C-50DS (outboard strip) → JR3/JR4 | VBUS through the DF40 (1.5 A/port) |
| `riser_hdmi` | × 1 | HDMI HOAUC HYC79-HDMIA19-105 (C711353) | −5.33° | 24.8 × 14.4 | DF40C-40DS → JR5 | 5 V through the DF40 |

- **Stackup.** JLC04161H-7628 4-layer 1.6, ENIG.
- **Mounting.** Each riser bolts with 2 × M2 to a printed PA12 wedge cradle; the cradle bolts to the main board with 2 × M2.
- **Status.** Placement level (A0): outline, connectors, link, pogo targets and holes. DRC 0 on all three.
- **Geometry source.** `risers.json`, computed by `../macpro62-io-board/tools/risers_geom.py` from the plate stack. Rebuild with `python3 tools/build_risers.py`.
- **Still to do:**
  - Riser schematics and pin maps: DF40 G-S-S-G pinning, ESD arrays per port.
  - Routing.
  - FPC jumper design: 2-layer, 90 Ω CPW over L2 GND, C-fold R ≥ 1.2.
  - Vendor land patterns (all MP62_* footprints are PLACEHOLDERS).
