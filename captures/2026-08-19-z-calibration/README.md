# Capture: AB6 Basic Settings — "Z" calibration attempt, invalid (2026-08-19)

USBPcap + Wireshark capture, provided by the user, of an attempted "Z
axis" calibration on the AB6 base. The firmware's own diagnostic log:

```
[INFO]stick_yaw.c:202 Stick_yaw calib start!
[INFO]stick_yaw.c:238 Stick_yaw calib invalid!
Stick_yaw calib_min_value: 12.07415, calib_mid_value: 12.34882, calib_max_value: 13.73861
```

**The calibration was rejected by the firmware as invalid, and no host
write was found anywhere in this capture** — unlike X/Y calibration
(`ab6-stick-x/y-calibration-start`), there's no trigger to add here at
all. The user confirmed the AB6 base has no such axis of its own; real
Yaw/twist calibration belongs to the MHG grip — see
[`captures/2026-08-19-mhg-yaw-calibration/`](../2026-08-19-mhg-yaw-calibration/)
and [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Stick and Cogging Torque
calibration: five more triggers".

Kept for the record — it's useful negative evidence, and explains the
"invalid" rejection rather than leaving it a mystery.
