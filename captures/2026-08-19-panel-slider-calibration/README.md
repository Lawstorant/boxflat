# Capture: AB6 Panel Settings — Slider Calibration (2026-08-19)

USBPcap + Wireshark capture, provided by the user, of Cockpit's Panel
Settings → **Slider Axis Calibration** wizard ("Start Calibration").

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Slider calibration: a
trigger, and the firmware's own margin formula" for the full writeup.

**The trigger, confirmed and wired up:**

Clicking Cockpit's single "Start Calibration" button sends two writes —
group 31, id 112, payload `[selector, 1]`, selector 0 for slider 1 and 1
for slider 2:

```
70 00 01   ->  id 112, selector 0 (slider 1), value 1 (start)
70 01 01   ->  id 112, selector 1 (slider 2), value 1 (start)
```

Added as `slider-calibration-start-1`/`-2` (write-only, `read: -1`, same
convention as every other calibration-start command in this file) and
wired up as a single "Start Calibration" button in `panels/ab6.py` that
fires both, matching the real Cockpit UX (one button, both sliders).

**Not exposed, but worth recording — the firmware's own margin formula:**

The diagnostic log names the raw measurement in plain English, twice (once
per slider):

```
[INFO]main_panel.c:580 Panel calib start!
[INFO]main_panel.c:580 Panel calib start!
Panel calib_min_value: 22578, calib_max_value: 41989
Panel calib_min_value: 21623, calib_max_value: 44408
[INFO]param_manage.c:340 Table 2, Param 47 Written: 23328 0.00000
[INFO]param_manage.c:340 Table 2, Param 48 Written: 22373 0.00000
[INFO]param_manage.c:340 Table 2, Param 49 Written: 41239 0.00000
[INFO]param_manage.c:340 Table 2, Param 50 Written: 43658 0.00000
```

The stored values are the raw measurement with an exact **750-unit inward
margin** — `23328 = 22578 + 750`, `22373 = 21623 + 750`,
`41239 = 41989 - 750`, `43658 = 44408 - 750` — i.e. Param 47/48 are the two
sliders' calibrated minimums, Param 49/50 the maximums, each pulled in
from the raw physical extreme by exactly 750.

This is entirely a **firmware-internal** computation — the host never
sends these four values, only the start trigger — and no read/write id for
them was seen in this capture (Cockpit didn't read them back afterward),
so there's nothing to add as a "read the calibrated range" command yet.
Recorded here in case a future capture (e.g. reopening the page after
calibrating) finds the read side.

Regenerated from the original `.pcapng` with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-19-panel-slider-calibration
```
