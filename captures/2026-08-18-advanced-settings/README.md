# Capture: AB6 Advanced Settings (2026-08-18)

USBPcap + Wireshark capture, provided by the user, split into two parts
(`part0`, `part1` — a long session saved in chunks; `part1` has no USB
enumeration frames of its own, decoded with `--device-address 14` carried
over from `part0`'s autodetected address). Covers three Cockpit pages under
Advanced Settings:

- **Centering** — Deadzone, Link +/- and Link X/Y checkboxes, Adaptive
  Centering Compensation, Hands-off Detection, Effect Strength,
  Compensation Effective Range.
- **Physics Model Settings** (Simplified mode) — the same seven sliders
  already confirmed in `captures/2026-08-17-basic-settings-other-settings/`;
  re-touched here and re-confirmed with identical values, no new mapping.
- **Trim Following Setting** / **Autopilot Following** — Axis follow mode,
  X/Y-axis follow ratio, Follow options presets (Light/Heavy/Custom
  Aircraft), physical stick follow rate/ratio, Trim-stick curve, Sidestick
  AP Lock, Roll/Pitch Follow Scale, Roll/Pitch Breakout Force Strength/
  Range, Roll/Pitch Follow Rate.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Advanced Settings: Centering
and Trim/Autopilot Following" for the full writeup. Six new settings
confirmed and added to `data/serial.yml` under `ab6:`:

| Setting | Table | Param | Group 31 id | `data/serial.yml` name |
| :-- | --: | --: | :-- | :-- |
| Effect Strength | 7 | 209 | 209 | `centering-effect-strength` |
| Compensation Effective Range | 7 | 210 | 210 | `centering-compensation-range` |
| Physical Stick Follow Ratio X | 8 | 36/40 | `[225, 9, 0]` | `follow-ratio-x` |
| Physical Stick Follow Ratio Y | 8 | 36/40 | `[225, 9, 1]` | `follow-ratio-y` |
| Roll Breakout Force Strength | 8 | 37/41 | `[225, 10, 0]` | `breakout-force-strength-roll` |
| Pitch Breakout Force Strength | 8 | 37/41 | `[225, 10, 1]` | `breakout-force-strength-pitch` |
| Roll Breakout Force Range | 8 | 38/42 | `[225, 11, 0]` | `breakout-force-range-roll` |
| Pitch Breakout Force Range | 8 | 38/42 | `[225, 11, 1]` | `breakout-force-range-pitch` |

All eight are direct 0–100 wire percentages, matching the screenshot's
values exactly. Table 8's own internal storage does something non-linear
with the two "Breakout Force Range" values — irrelevant to boxflat, which
only needs the wire format.

Also found but not attributed to a name: two single-value booleans in
Table 7 (params 116, 121 — plausibly the Centering page's Link +/- and
Link X/Y checkboxes, order-only evidence), three single-value booleans in
Table 8 (params 32, 33, 34), and a compound "preset select" command
(id 225 with category bytes `0x0e`/`0x0f`/`0x11`) that cascades into a
burst of downstream Table 8 writes, likely the Follow options preset
buttons (Light/Heavy/Custom Aircraft) or the Axis follow mode selector.
Not decoded further — see `AB6_STATUS.md`.

Regenerated from the original `.pcapng` files with:

```bash
python3 tools/ab6_pcap_decode.py part0.pcapng --out-dir captures/2026-08-18-advanced-settings/part0
python3 tools/ab6_pcap_decode.py part1.pcapng --device-address 14 --out-dir captures/2026-08-18-advanced-settings/part1
```
