# Capture: AB6 Basic Settings — axes + FFB mode (2026-08-17)

USBPcap + Wireshark capture, provided by the user. In Cockpit's AB6 Basic
Settings page: moved the X/Y/Z axes, then cycled **FFB Mode** Telemetry →
DirectInput → Telemetry → Integrated → Telemetry.

See [`AB6_STATUS.md`](../../AB6_STATUS.md) → "FFB Mode: the first
confirmed, editable AB6 setting" for the full writeup. Result:
`data/serial.yml`'s `ab6.ffb-mode` (group 30 read / 31 write, id 133,
0 = Telemetry / 1 = DirectInput / 2 = Integrated) — confirmed three ways
(the write, the read-back, and the firmware's diagnostic log all agree at
every transition), and wired up as a working control in `panels/ab6.py`.

Also present but not mapped: continuous changes on ids 184/185/215/216
(group 30, device 18) during the axis movement, almost certainly live axis
telemetry redundant with what HID already provides — see "Bonus: live axis
telemetry, unmapped" in `AB6_STATUS.md`.

Regenerated from the original `.pcapng` with:

```bash
python3 tools/ab6_pcap_decode.py <capture>.pcapng --out-dir captures/2026-08-17-basic-settings-axes-ffb-mode
```
