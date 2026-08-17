# Capture: Moza Cockpit launch (2026-08-17)

USBPcap + Wireshark capture of MOZA Cockpit on Windows connecting to a real
AB6 (base + MHG grip), captured and provided by the user. Passive only — no
Cockpit control was touched, so this is a "Phase 1 — Connect / startup"
capture in [`../../AB6_CAPTURE_PLAN.md`](../../AB6_CAPTURE_PLAN.md)'s terms.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Windows capture analysis
(2026-08-17)" for the full writeup. Summary of what's in this directory:

- **`diag_log_device18.txt`** / **`diag_log_device19.txt`** — the AB6's
  asynchronous ASCII diagnostic log (group 14, command id 5), reassembled
  in order, per device (18 = base, 19 = grip). Includes the boot-time
  parameter load and the grip's hall-sensor calibration values in plain
  text.
- **`param_writes.csv`** — every `Table N, Param M Written: <raw> <float>`
  line extracted from the diagnostic log, as `device,table,param,raw_int32,
  float_value`. 129 rows across 4 tables (2, 7, 8 on the base; 13 on the
  grip).
- **`binary_traffic_summary.txt`** — group/device-id/command-id breakdown of
  every binary (non-diagnostic) frame seen, both directions.

Regenerated from the original `.pcapng` with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-17-cockpit-launch
```

The original `.pcapng` itself is not committed (it's large and the decoded
artifacts here carry everything currently useful out of it). If the raw
capture is needed again — e.g. to check a byte this decode doesn't
surface — ask the user, who has the original file.
