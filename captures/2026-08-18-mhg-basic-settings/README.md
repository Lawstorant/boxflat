# Capture: MHG Basic Settings (2026-08-18)

USBPcap + Wireshark capture, provided by the user, of Cockpit's **MHG**
page — its only settings tab (per the user: "no other settings tabs for
it"). Covers Grip Settings (Cogging Torque Calibration, Yaw Axis
Settings, Mode 1/Mode 2 mapping, Axis Calibration, Mapping Range) and two
independent lighting zones, Status Light and Button Light (each with Light
Mode, Light Effect, Backlit Brightness, Light Color). The button-map panel
on the right is a live HID display (already covered by boxflat's existing
axis/button handling), not a serial setting.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "The grip has its own
command set: two lighting zones confirmed" for the full writeup. Key
finding: **the grip uses a different write group than the AB6 base** -
group 50 (read) / 51 (write), not the base's 30/31 - discovered because
the base's group/id convention produced zero matches until the actual
group was found by inspecting the raw traffic. Six settings confirmed and
added to `data/serial.yml` under `mhg:`:

| Setting | id | `data/serial.yml` name |
| :-- | --: | :-- |
| Status Light Brightness | `[98, 0]` | `status-light-brightness` |
| Button Light Brightness | `[98, 1]` | `button-light-brightness` |
| Status Light Color | `[99, 0]` | `status-light-color` |
| Button Light Color | `[99, 1]` | `button-light-color` |
| Status Light Effect | `[100, 0]` | `status-light-effect` |
| Button Light Effect | `[100, 1]` | `button-light-effect` |

Brightness and Color matched the screenshot exactly (12/15 and
`RGB(76,0,0)`/`RGB(49,0,0)`). Light Effect matched more weakly — both zones
landed on the same wire value (1), consistent with both showing "Always
On" in the screenshot, but that's one data point out of an observed 0–3
range, not a full sweep — added to `data/serial.yml` but not wired into
the panel, matching how the AB6 base's own unconfirmed Light Effect finding
was handled.

Also found but not attributed: four more Table 13 booleans/small-int
params (18, 22, 25, 27 — candidates include Enable Yaw Axis Output, Press
stick to switch mode, and the Mode 1/Mode 2 dropdowns) and an odd
inconsistency around params 23/24 where two different ids (101, 102)
appeared to write the same param with values that didn't match the
diagnostic log's stored value — not decoded.

Regenerated from the original `.pcapng` with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-18-mhg-basic-settings
```
