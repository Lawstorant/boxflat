# Capture: MHG Basic Settings — Cogging Torque Calibration (2026-08-18)

USBPcap + Wireshark capture, provided by the user, split into two parts
(`part0`, `part1` — `part1` has no USB enumeration frames of its own,
decoded with `--device-address 14` carried over from `part0`).

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Stick and Cogging Torque
calibration: five more triggers" for the full writeup.

**The button lives on the MHG page in Cockpit, but targets the AB6
base's own motors** (device 18, firmware's own `steer.c`/
`motor_middleware_cogging.c`). Makes sense once you consider why it's
needed: the correct cogging compensation depends on the inertia (weight)
loaded onto the motor shaft — i.e. whichever grip is attached (the AB6
supports several: MHG, MH16, MA3X) — so Cockpit surfaces it per-grip even
though the command itself still targets the base. Single write-only
trigger, group 31, id 194, payload always `[0x00, 0x00]`, same shape as
`ab6-stick-x/y-calibration-start`. Added as
`ab6-cogging-torque-calibration-start`.

**After the trigger, the calibration runs entirely on its own** for a long
time (`part1` alone is ~45,000 CDC frames) and produces a genuinely large
firmware-internal result: **246 values across two 123-entry tables**
(Table 5 and Table 6, params 5–127, almost certainly one per motor axis) —
a cogging-torque compensation lookup table sampled across the motor's full
rotation, e.g.:

```
Table 6, Param 113 Written: -1.49803
Table 6, Param 114 Written: -6.02352
Table 6, Param 115 Written: -24.21960
Table 6, Param 116 Written: -97.37842
```

**Not modeled as individual settings** — this is nowhere close to
something a user would view or edit entry-by-entry, and no read id was
seen for it regardless. Only the trigger is exposed.

Regenerated with:

```bash
python3 tools/ab6_pcap_decode.py part0.pcapng --out-dir captures/2026-08-18-mhg-cogging-torque-calibration/part0
python3 tools/ab6_pcap_decode.py part1.pcapng --device-address 14 --out-dir captures/2026-08-18-mhg-cogging-torque-calibration/part1
```
