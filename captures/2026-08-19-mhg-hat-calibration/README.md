# Capture: MHG Basic Settings — Grip Hat Axis Calibration (2026-08-19)

USBPcap + Wireshark capture, provided by the user, of the MHG grip's
mini-stick (thumb hat, X and Y) calibration.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Stick and Cogging Torque
calibration: five more triggers" for the full writeup. Found a **third
group on the grip**, distinct from its usual read (50) / write (51) pair:
group 52, write-only. Cockpit's single "Grip Hat Axis Calibration" button
fires two writes together, ids 4 (X) and 5 (Y), value 1 to start and 0 to
stop a few seconds later:

```
04 01   id 4 (X), value 1 (start)
05 01   id 5 (Y), value 1 (start)
  ... (user moves the mini-stick) ...
04 00   id 4 (X), value 0 (stop)
05 00   id 5 (Y), value 0 (stop)
```

Added as `mhg-hat-x-calibration` / `mhg-hat-y-calibration`, wired up as a
single `BoxflatCalibrationRow` in `panels/mhg.py` firing both together,
matching Cockpit's one-button UX.

Result (Table 13 params 9–14: max/min/mid for X then Y) is
firmware-computed and logged directly
(`thumb_x theta: [calib_min: ..., calib_mid: ..., calib_max: ...]`) — no
read/write id for it was seen.

Regenerated with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-19-mhg-hat-calibration
```
