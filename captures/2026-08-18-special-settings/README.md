# Capture: AB6 Special settings (2026-08-18)

USBPcap + Wireshark capture, provided by the user, of Cockpit's
**Special** page — not in this project's original page inventory (see
`AB6_CAPTURE_PLAN.md`'s original "Cockpit's page structure" list), found
by the user browsing Cockpit's tabs. Covers **Controls** (Hardware Trim
Mode, Trim Mode Direct Input/Hardware, hardware trim button bindings
[NOSE UP/DOWN, LWD/RWD, FORCE TRIM, RE-CENTER], Trim Follow Rate, Trim
Range) and **Miscellaneous** (Base Force Model Selection Flight Base/
Shifter, Grip Removal Protection, Extend Travel Range).

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "A page we didn't know
about: Special settings" for the full writeup. Five settings confirmed
and added to `data/serial.yml` under `ab6:`:

| Setting | id | `data/serial.yml` name |
| :-- | --: | :-- |
| Trim Follow Rate | 196 | `trim-follow-rate` |
| Trim Range (direction unconfirmed) | `[198, 0]` | `trim-range-0` |
| Trim Range (direction unconfirmed) | `[198, 1]` | `trim-range-1` |
| Trim Range (direction unconfirmed) | `[198, 2]` | `trim-range-2` |
| Trim Range (direction unconfirmed) | `[198, 3]` | `trim-range-3` |

Trim Follow Rate matched the screenshot's `8` exactly. All four Trim Range
selectors ended at wire value 100, matching the screenshot's four 100%
fields exactly — but since all four land on the identical value, there's
no way to tell from this capture which selector is `-X`/`+X`/`-Y`/`+Y`
(the same situation as `axis-travel-limit-1`/`-2` from the Axis Travel
capture). Named by selector number, not direction.

Also found but not attributed: five booleans (Table 7 params 102, 114,
122, 123; Table 2 param 44) — plausible candidates include Hardware Trim
Mode, Grip Removal Protection, Base Force Model Selection and Extend
Travel Range, but none confidently matched to a specific control. Two of
them (114 and 102) show a "touched, long gap, touched again" shape
suggestive of a top-level toggle that gates the visibility of the controls
below it, the same pattern the Centering page's Adaptive Centering
Compensation showed.

Regenerated from the original `.pcapng` with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-18-special-settings
```
