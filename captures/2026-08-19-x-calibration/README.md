# Capture: AB6 Basic Settings — X (Roll) stick calibration (2026-08-19)

USBPcap + Wireshark capture, provided by the user, of the AB6 base's own
Roll axis ("motor_x" in the firmware's own log) hand-calibration.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Stick and Cogging Torque
calibration: five more triggers" for the full writeup. Single write-only
trigger confirmed: group 31, id 128, payload always `[0x00, 0x00]`. Added
as `ab6-stick-x-calibration-start`.

The firmware measures the physical range itself
(`[INFO]steer.c:1594 motor_x hand_cali start` → `hand_cali end, max_pos:
1.80925, min_pos: -1.80925`) and stores a symmetric `+/-max_pos` (radians)
into Table 7 params 55/56 — entirely firmware-computed, no read/write id
seen for the result, same treatment as every other calibration result in
this project.

Regenerated with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-19-x-calibration
```
