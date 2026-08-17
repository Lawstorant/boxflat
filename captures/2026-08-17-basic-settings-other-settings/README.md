# Capture: AB6 Basic Settings — other settings (2026-08-17)

USBPcap + Wireshark capture, provided by the user. In Cockpit's AB6 Basic
Settings page:

1. Changed **Temperature control mode** from its default to Conservative,
   then to Aggressive.
2. Cycled each of the seven remaining sliders — in on-screen top-to-bottom
   order — through 10% → 90% → 100%, then back to its original value. Final
   values, from the accompanying screenshot: Maximum Torque Output 100%,
   Overall Force Feedback Intensity 100%, Spring 48%, Damper 100%, Inertia
   70%, Friction 60%, Game Force Feedback Gain 100%.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Seven more settings confirmed
in one pass" for the full writeup and the correlation method. Result: eight
settings total (including FFB Mode from the previous capture) confirmed and
added to `data/serial.yml` under `ab6:`, all direct 0–100 (or 1/2 for the
temperature mode) integers on group 30 (read) / 31 (write):

| Setting | id | `data/serial.yml` name |
| :-- | --: | :-- |
| Maximum Torque Output | 169 | `torque` |
| Overall Force Feedback Intensity | 174 | `ffb-intensity` |
| Spring | 175 | `spring` |
| Damper | 176 | `damper` |
| Inertia | 177 | `inertia` |
| Friction | 178 | `friction` |
| Game Force Feedback Gain | 153 | `game-ffb-gain` |
| Temperature Control Mode | 192 | `temp-control-mode` |

Every value was confirmed by matching the binary write frame against the
firmware's own `Table 7, Param N Written` diagnostic-log line at the same
timestamp, across every transition (up to 4 per setting) — see
`param_writes.csv` and `diag_log_device18.txt`. `torque` additionally has a
confirmed read-back (it's polled continuously outside this page too); the
other six use the same read group by strong analogy (matches the
write+1 convention used everywhere else in `data/serial.yml`) but weren't
independently read-verified in this capture.

Regenerated from the original `.pcapng` with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-17-basic-settings-other-settings
```
