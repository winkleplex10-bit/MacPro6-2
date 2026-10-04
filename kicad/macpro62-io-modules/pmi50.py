"""PMI-50 v2 port-module interface (D-IO16 rev 2026-10-02 ~13:40 ET) - ONE source for the main-board schematic, the module flexes and the docs.
DF40C-50DS-0.4V(51) on the main board (JMn) <- DF40C-50DP-0.4V(51) on the module paddle. Position k = 1..25 counted from the FOLD end of the paddle.
Row A = odd pin 2k-1 (module +v side), row B = even pin 2k (module -v side).
v2 orders each row so that a 2-layer flex routes straight through: every row-A/B signal arrives on its own tail lane, lanes are ordered by k
(innermost lane = smallest k), VBUS is fed between the rows at the fold end, GND pads via between the rows, ID / 3V3 at the far end next to the EEPROM.
High-speed positions are lane pairs HSn_A / HSn_B (A = smaller k = inner lane); the polarity on each is fixed PER MODULE TYPE (ROLES) so that the
module fan-out needs no P/N crossover. The slots are typed (C1-C6 MOD-C, A1-A4 MOD-A, HDMI MOD-H), so the main board wires each JMn for its type."""
PMI = [("VBUS", "VBUS")] * 6 + [("GND", "GND"),
       ("USB2_A", "LS_B1"), ("USB2_B", "LS_B2"), ("GND", "GND"), ("LS_A1", "SPARE_B1"), ("LS_A2", "SPARE_B2"), ("GND", "GND"),
       ("HS3_A", "HS2_A"), ("HS3_B", "HS2_B"), ("GND", "GND"), ("HS0_A", "HS1_A"), ("HS0_B", "HS1_B"), ("GND", "GND"),
       ("UTIL", "SPARE_B3"), ("GND", "GND"), ("ID_SCL", "PRSNT#"), ("ID_SDA", "3V3_MOD"), ("LED#", "GND"), ("GND", "GND")]
assert len(PMI) == 25
def pins(role):
    out = []
    for k, (a, b) in enumerate(PMI):
        if a == role: out.append(2 * k + 1)
        if b == role: out.append(2 * k + 2)
    return out
def kpos(role):   # (k, row) of a single-pin role
    for k, (a, b) in enumerate(PMI):
        if a == role: return k + 1, "A"
        if b == role: return k + 1, "B"
# per module type: PMI position -> module net (connector function). Missing = not connected on that module.
ROLES = {
 "USBC": {"USB2_A": "D_P", "USB2_B": "D_N", "LS_A1": "CC1", "LS_A2": "SBU1", "HS3_A": "SSRX2_P", "HS3_B": "SSRX2_N", "HS0_A": "SSTX1_N", "HS0_B": "SSTX1_P",
          "LS_B1": "CC2", "LS_B2": "SBU2", "HS2_A": "SSTX2_P", "HS2_B": "SSTX2_N", "HS1_A": "SSRX1_N", "HS1_B": "SSRX1_P"},
 "USBA": {"HS3_A": "SSRX_N", "HS3_B": "SSRX_P", "HS0_A": "SSTX_N", "HS0_B": "SSTX_P", "LS_B1": "D_P", "LS_B2": "D_N"},
 "HDMI": {"LS_A2": "DDC_SDA", "HS3_A": "CK_N", "HS3_B": "CK_P", "HS0_A": "D1_N", "HS0_B": "D1_P", "LS_B1": "HPD", "LS_B2": "DDC_SCL",
          "HS2_A": "D0_N", "HS2_B": "D0_P", "HS1_A": "D2_N", "HS1_B": "D2_P"},
}
# module net -> main-board net suffix / name (slot prefix p: "C1", "A1"; HDMI absolute)
MB = {
 "USBC": lambda p: {"D_P": p + "_USB2_DP", "D_N": p + "_USB2_DN", "CC1": p + "_CC1", "CC2": p + "_CC2", "SBU1": p + "_SBU1", "SBU2": p + "_SBU2",
                    "SSTX1_P": p + "_SS_TX1_P", "SSTX1_N": p + "_SS_TX1_N", "SSRX1_P": p + "_SS_RX1_P", "SSRX1_N": p + "_SS_RX1_N",
                    "SSTX2_P": p + "_SS_TX2_P", "SSTX2_N": p + "_SS_TX2_N", "SSRX2_P": p + "_SS_RX2_P", "SSRX2_N": p + "_SS_RX2_N"},
 "USBA": lambda p: {"D_P": p + "_USB2_DP", "D_N": p + "_USB2_DN", "SSTX_P": p + "_SS_TX_P", "SSTX_N": p + "_SS_TX_N", "SSRX_P": p + "_SS_RX_P", "SSRX_N": p + "_SS_RX_N"},
 "HDMI": lambda p: {"D2_P": "TMDS_D2_P", "D2_N": "TMDS_D2_N", "D1_P": "TMDS_D1_P", "D1_N": "TMDS_D1_N", "D0_P": "TMDS_D0_P", "D0_N": "TMDS_D0_N",
                    "CK_P": "TMDS_CK_P", "CK_N": "TMDS_CK_N", "DDC_SCL": "HDMI_SCL", "DDC_SDA": "HDMI_SDA", "HPD": "HDMI_HPD"},
}
if __name__ == "__main__":
    for k, (a, b) in enumerate(PMI): print(k + 1, 2 * k + 1, a, 2 * k + 2, b)
    print({r: len(pins(r)) for r in ("VBUS", "GND")})
