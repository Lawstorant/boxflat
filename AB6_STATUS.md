# Moza AB6 Support — Status & Continuation Guide

Tracking work on Moza AB6 FFB Base support for boxflat on Linux.
Upstream issue: [Lawstorant/boxflat#157](https://github.com/Lawstorant/boxflat/issues/157)

## Background

The AB6 is Moza's force-feedback flight joystick base:

| Property | Value |
| :-- | :-- |
| HID device name | `Gudsen MOZA AB6 FFB Base` |
| USB vendor:product | `346e:1002` |
| Serial interface | CDC-ACM (`/dev/ttyACM*`), 115200 baud, same framing as racing gear |
| Expected by-id path | `/dev/serial/by-id/usb-Gudsen_MOZA_AB6_FFB_Base_<serial>-if00` |

The reported problem (issue #157): the device works as a plain joystick with
default autocenter, but boxflat never detects it, so no settings can be
changed. `dmesg` also shows `Invalid code 768-777 type 1` and
"device has unknown autocenter control method" — those come from the kernel
HID/FFB layer, not from boxflat (see "Out of scope" below).

## Why boxflat didn't detect it

Both discovery paths in boxflat match device names against regex patterns in
`boxflat/hid_handler.py` (`MozaHidDevice`):

1. **HID discovery** — evdev device names are matched against
   `MozaHidDevice.BASE`, which only covered racing bases
   (`gudsen (moza )?r[0-9]{1,2} …`).
2. **Serial discovery** — `MozaConnectionManager.device_discovery()` reuses
   the same patterns (spaces replaced with underscores) against
   `/dev/serial/by-id` entries.

"MOZA AB6 FFB Base" matched neither, so the device was invisible to both.

## What's done (this branch)

Branch: `claude/moza-ab6-linux-support-i12g16`, commit `e790ea6`.

- **`boxflat/hid_handler.py`** — `MozaHidDevice.BASE` pattern extended to:
  `gudsen (moza )?(r[0-9]{1,2} (ultra base|base|racing wheel and pedals)|ab[0-9]{1,2} ffb base)`.
  One change covers both HID and serial discovery. The AB6 is treated as a
  base, so the Base/Home panels and generic base serial commands (FFB
  strength, rotation limit, damper, torque, etc.) apply to it. The Moza
  serial protocol is hardware-agnostic, so these are expected to work where
  the AB6 firmware implements them.
- **`boxflat/hid_handler.py`** — `_update_axis()` now skips axis codes with
  no mapping instead of raising `KeyError`. The AB6 exposes joystick axes
  with no racing counterpart; previously an unknown axis crashed the HID
  read loop, which closed and reopened the device forever.
- **`README.md`** — AB6 row added to the device table.

Verified so far (no hardware available in this environment):

- Pattern matches `gudsen moza ab6 ffb base` (HID) and
  `usb-gudsen_moza_ab6_ffb_base_…-if00` (serial), still matches
  R5/R9/R12/R25 Ultra bases, and does not match pedals/handbrake/hub.
- Modified files compile cleanly.

## Not yet verified (needs real hardware)

1. **Detection** — run boxflat with the AB6 plugged in. Expected console
   output: `HID device found: Gudsen MOZA AB6 FFB Base` and
   `"base" connected`.
2. **Panel activation** — the Base and Home panels activate only if the
   device answers a `base-limit` serial read. If they stay greyed out, the
   AB6 answers on a different device ID or command group (see next section).
3. **Settings round-trip** — change FFB strength / rotation limit in the
   Base panel, confirm the device behavior changes, re-read after replug.
4. **By-id name** — confirm the actual `/dev/serial/by-id` entry name;
   if manufacturer/product strings differ from the expected form, the serial
   pattern needs adjusting (`ls -l /dev/serial/by-id/`).

## How to continue

### If the Base panel doesn't activate

The AB6 likely uses its own device ID or command groups. To find out:

- Uncomment the debug print in `SerialHandler._serial_write_handler` and add
  one in `_serial_read_handler` to log raw traffic while boxflat polls.
- Alternatively capture Moza Cockpit ↔ AB6 traffic on Windows with
  Wireshark + USBPcap, filtering the CDC-ACM interface. The framing is
  documented in [`moza-protocol.md`](./moza-protocol.md):
  `0x7e | length | group | device-id | command-id | payload | checksum`
  (checksum = (13 + sum of bytes) % 256).
- If the AB6 answers on a new device ID, add it to `device-ids` /
  `ids-to-names` in `data/serial.yml` and, if needed, a new `ab6` command
  section — the YAML is the single source of truth for commands.

### AB6-specific settings panel (follow-up feature)

Moza Cockpit exposes joystick-specific settings (spring/trim, per-axis
behavior). Once captures exist:

1. Add an `ab6` command section to `data/serial.yml`.
2. Create `boxflat/panels/ab6.py` modeled on `panels/base.py`, register it
   in `boxflat/app.py:_prepare_settings()` and `panels/__init__.py`.
3. Gate activation on an AB6-only command via
   `self._cm.subscribe_connected("ab6-<something>", self.active)`.

### Upstreaming

The change is deliberately minimal and style-consistent. To upstream, open a
PR from this branch against `Lawstorant/boxflat` `main` referencing
issue #157, ideally after hardware confirmation from the issue reporter
(they offered to provide logs/testing).

## Out of scope

Missing force feedback itself ("unknown autocenter control method",
`Invalid code 768-777` in dmesg) is a kernel HID FFB driver concern —
see [universal-pidff](https://github.com/JacKeTUs/universal-pidff) /
`hid-universal-pidff`. Boxflat only manages device settings; once the kernel
driver handles the AB6's PID descriptors, games get FFB regardless of
boxflat.
