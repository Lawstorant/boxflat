# Capture: AB6 Axis Travel (2026-08-18)

USBPcap + Wireshark capture, provided by the user, of Cockpit's **Axis
Travel** page for the AB6's X/Y/Z stick axes (Output Mapping Curve, Invert
Axis, Axis Positive/Negative Travel Limit, Axis Offset — the Z axis column
was cropped from the screenshot below "Output Mapping Curve").

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Axis Travel: travel limits
confirmed, curve and offset still open" for the full writeup. Result: four
settings added to `data/serial.yml` under `ab6:`:

| Setting | id | `data/serial.yml` name |
| :-- | --: | :-- |
| Axis 1 Positive Travel Limit | `[171, 1]` | `axis-travel-limit-1-positive` |
| Axis 1 Negative Travel Limit | `[171, 2]` | `axis-travel-limit-1-negative` |
| Axis 2 Positive Travel Limit | `[172, 1]` | `axis-travel-limit-2-positive` |
| Axis 2 Negative Travel Limit | `[172, 2]` | `axis-travel-limit-2-negative` |

Both pairs ended at 100%/100%, matching the screenshot exactly. **Which
physical axis (X, Y or Z) is "1" and which is "2" is not independently
confirmed** — only inferred from touch order and from where these ids fall
in the connect-time settings-read burst (both agree with each other and
with the page's left-to-right layout, but neither is a value-level proof
the way the percentages themselves are). Labeled generically in the panel
for that reason.

Also found but **not** added, all lower-confidence or too complex to
attribute safely in one pass:

- **Output Mapping Curve** (id 15/`0x0f` on Table 2) — a compound command
  that writes 4 Table 2 params per curve-point drag, with a payload shaped
  `[point_selector, 16-bit value]`. The exact point-index / axis encoding
  wasn't pinned down from this capture alone.
- **Axis Offset** (id 173) — one sample per axis, wire value `175`, which
  fits a `value + 100` bias around the screenshot's `-75..75` range (175 -
  100 = 75, one extreme) but is unconfirmed — could easily be a different
  bias or scale.
- **Invert Axis** — two boolean candidates (Table 7 params 19, 46) whose
  touch order contradicts their id order (unlike everything else in this
  file, where the two have always agreed), so confidence is too low to
  attribute even generically.
- **A "Reset" button click** (Table 2 param 9, id 90) — single value
  1-then-0, shaped like a button press rather than a persistent setting.

Regenerated from the original `.pcapng` with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-18-axis-travel
```
