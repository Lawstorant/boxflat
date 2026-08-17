# Capture: AB6 Panel Settings (2026-08-17)

USBPcap + Wireshark capture, provided by the user, of Cockpit's AB6 **Panel
Settings** page (Slider Axis Calibration/Mode, Button Light Mode/Effect/
Pattern, Backlit Brightness, Light Color). Per the user: "Start Calibration"
was not touched; everything else on the page was. An accompanying
screenshot shows the final state.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "Panel lighting: two more
confirmed, plus a structural finding" for the full writeup. Results, added
to `data/serial.yml` under `ab6:`:

| Setting | id | Confidence |
| :-- | --: | :-- |
| `light-color` | 102 | High — final value `RGB(91,0,0)` matched the screenshot exactly |
| `backlit-brightness` | 103 | High — wire value is the direct 0–15 UI range |
| `slider-mode-left` / `-right` | 113 (2nd id byte 0/1) | Wire format confirmed; **option meaning (which value = which menu choice) is not** |

Three more ids were touched (101, 104, 105 — likely Light Mode, Pattern,
and Light Effect in some order) but weren't attributed confidently enough
to add — see `AB6_STATUS.md` for why, and what a follow-up capture would
need to nail them down (explicit before/after values per control, the way
the previous two captures had unique screenshot values to match against).

Regenerated from the original `.pcapng` with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-17-panel-settings
```
