# Capture: AB6 Basic Settings — Y (Pitch) stick calibration (2026-08-19)

USBPcap + Wireshark capture, provided by the user, of the AB6 base's own
Pitch axis ("motor_y" in the firmware's own log) hand-calibration.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Stick and Cogging Torque
calibration: five more triggers" for the full writeup. Same shape as the
X (Roll) calibration: single write-only trigger, group 31, id 129, payload
always `[0x00, 0x00]`. Added as `ab6-stick-y-calibration-start`.

Result (Table 7 params 58/59, symmetric `+/-max_pos` in radians) is
entirely firmware-computed and logged
(`hand_cali end, max_pos: 1.49535, min_pos: -1.49535`) — no read/write id
for it was seen.

Regenerated with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-19-y-calibration
```
