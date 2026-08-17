# Capture: MHG Basic Settings — Yaw Axis Calibration (2026-08-19)

USBPcap + Wireshark capture, provided by the user, of the MHG grip's
twist (yaw) axis calibration — the real yaw calibration for this system;
an AB6-base-side "Z axis" attempt (see
[`captures/2026-08-19-z-calibration/`](../2026-08-19-z-calibration/)) was
rejected by the firmware as invalid, and the user confirmed the base has
no such axis of its own.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Stick and Cogging Torque
calibration: five more triggers" for the full writeup. Same group 52 as
the Hat calibration, single id (6, one rotational axis rather than a
paired X/Y):

```
06 01   id 6, value 1 (start)
  ... (user twists the grip) ...
06 00   id 6, value 0 (stop)
```

Added as `mhg-yaw-calibration`, wired up as a `BoxflatCalibrationRow` in
`panels/mhg.py`.

Regenerated with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-19-mhg-yaw-calibration
```
