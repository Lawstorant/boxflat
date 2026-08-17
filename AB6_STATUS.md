# Moza AB6 Support — Status & Continuation Guide

Tracking work on Moza AB6 FFB Base support for boxflat on Linux.
Upstream issue: [Lawstorant/boxflat#157](https://github.com/Lawstorant/boxflat/issues/157)

**Status as of 2026-08-17 — tested on real hardware.**

| Area | State |
| :-- | :-- |
| Detection (HID + serial) | ✅ Works |
| Base panel activation | ❌ Device answers no racing commands |
| Settings round-trip | ⛔ Blocked on the above |
| Protocol framing | ✅ Shared with racing gear, decoder reusable |
| Command set | ❌ Different — firmware identifies as `Stick` |
| AB6's own groups | 🔍 Found — 8 groups return stable data |
| AB6 settings table | 🔍 Found — group 14, 9 command ids |
| Diagnostic log | 🔍 Found — firmware streams ASCII internals |
| AB6 panel in boxflat | ✅ Works — gated on a real firmware read |
| Home page | ✅ Now lists only detected hardware |

Short version: the branch successfully makes the AB6 **detected**, and that
is where it stops for now. The AB6 uses the same wire framing as racing gear
but a different command set, so no settings are readable or writable yet.

A read-only sweep has since found where it *does* answer — groups 2, 4, 5, 6,
10, 12, 14 and 19 return stable payloads, including two version-shaped and
one UID-shaped reply — plus a live ASCII diagnostic log. See "Sweep results".
Next step is mapping command ids inside those groups.

## Background

The AB6 is Moza's force-feedback flight joystick base:

| Property | Value |
| :-- | :-- |
| HID device name | `Gudsen MOZA AB6 FFB Base` |
| USB vendor:product | `346e:1002` |
| Serial interface | CDC-ACM (`/dev/ttyACM*`), 115200 baud, same framing as racing gear |
| Expected by-id path | `/dev/serial/by-id/usb-Gudsen_MOZA_AB6_FFB_Base_<serial>-if00` |

All four confirmed on real hardware 2026-08-17 (see "Hardware test results").
The by-id path is exactly as predicted:
`/dev/serial/by-id/usb-Gudsen_MOZA_AB6_FFB_Base_4D0040000551353133383438-if00`.

### Device topology

From the [AB6 user manual](https://www.mozaracing.com) and MOZA's
[AB6 guide](https://support.mozaracing.com/en/support/solutions/articles/70000684201-ab6-force-feedback-base-complete-guide):

The AB6 is a **base with a detachable grip**, not a single device. The MHG
flightstick connects to the base's aviation connector and "will appear on the
main page along with its firmware version" in Cockpit. That is structurally
the same arrangement boxflat already models for racing gear — a wheel on a
wheelbase, with its own device ID on the serial bus.

**Implication:** expect *two* addressable devices, not one. The grip almost
certainly answers on its own device ID, and grip settings (button lighting,
mini-stick calibration) are a separate command surface from base settings.
This is also what the Home panel needs in order to list "AB6 base" and "MHG
flightstick" separately.

Hardware inventory, for correlating with evdev axes:

| Element | Detail |
| :-- | :-- |
| Base torque | 4.4 N·m continuous, 6 N·m peak, dual servo |
| Encoder | 15-bit magnetic, 1000 Hz USB polling |
| Base inputs | 2 analog throttle sliders, 8 RGB-backlit buttons |
| Grip (MHG) | mini-stick (X/Y), Z-axis twist, dual-stage trigger, several switches |
| Accessory ports | RJ11 — rudder pedals, throttle, dash display |
| Compatible grips | MH16, MHG, MA3X, plus third-party |

This lines up with the 10 evdev axes observed: `ABS_X`/`ABS_Y` (stick),
`ABS_RX`/`ABS_RY` (mini-stick), `ABS_RZ` (twist), `ABS_THROTTLE`/`ABS_RUDDER`
(the two sliders), `ABS_Z`, and `ABS_HAT0X`/`ABS_HAT0Y`.

Note the manual's warning: *"Do not use MOZA flight sim gear with the MOZA
racing gear."*

### The problem

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
  strength, rotation limit, damper, torque, etc.) apply to it.

  > **Superseded by hardware testing.** This bullet originally assumed "the
  > Moza serial protocol is hardware-agnostic, so these are expected to work
  > where the AB6 firmware implements them". That is now known to be wrong:
  > the AB6 shares the *framing* but not the *command set*, and answers none
  > of the racing commands. See "Hardware test results".

- **`boxflat/hid_handler.py`** — `_update_axis()` now skips axis codes with
  no mapping instead of raising `KeyError`. The AB6 exposes joystick axes
  with no racing counterpart; previously an unknown axis crashed the HID
  read loop, which closed and reopened the device forever.

  > **Not exercised by this device.** All 10 axes the AB6 actually exposes
  > are already mapped, so the guard never fires here. See "Hardware test
  > results". Harmless, but it is not fixing anything on the AB6.

- **`README.md`** — AB6 row added to the device table. The row claims
  "Detection, base settings"; **the "base settings" half is wrong** and
  should be corrected before upstreaming.

Verified without hardware (still true):

- Pattern matches `gudsen moza ab6 ffb base` (HID) and
  `usb-gudsen_moza_ab6_ffb_base_…-if00` (serial), still matches
  R5/R9/R12/R25 Ultra bases, and does not match pedals/handbrake/hub.
- Modified files compile cleanly.

## Hardware test results (2026-08-17)

Tested on CachyOS (Linux 7.1.8), Wayland/KDE, real AB6 attached, running the
branch from a checkout with `python3 -u entrypoint.py --local`. All serial
traffic below was **read-only**; no setting was written to the device.

Environment was ready: udev rule installed, `/dev/ttyACM0` mode `0666`,
`/dev/input/event24` reachable via ACL, all Python deps present.

### 1. Detection — PASS

Console output is exactly what this document predicted:

```
"base" connected
HID device found: Gudsen MOZA AB6 FFB Base
```

Both device nodes are genuinely opened by the process (confirmed via
`/proc/<pid>/fd`): `/dev/input/event24` (HID) and `/dev/ttyACM0` (serial).
Serial discovery registers the AB6 under the name `base`. The regex change
works on both discovery paths, with no regression for racing bases.

Note: these prints are invisible when stdout is redirected to a file without
`-u` — Python block-buffers them. Use `python3 -u` when capturing logs.

### 2. Panel activation — FAIL

The Base panel never activates, so it never appears in the sidebar (sidebar
shows only Home / Presets / Generic Devices / Other). `BaseSettings` gates
itself on `subscribe_connected("base-limit", self.active)`
(`boxflat/panels/base.py:44`), and that read never succeeds.

### 3. Settings round-trip — BLOCKED

Every readable command in `data/serial.yml` was tried against the device
using boxflat's own message builder. **0 of 231 commands responded:**

| section | responded | section | responded |
| :-- | :-- | :-- | :-- |
| `main` | 0/11 | `dash` | 0/34 |
| `base` | 0/45 | `hpattern` | 0/6 |
| `pedals` | 0/31 | `sequential` | 0/8 |
| `wheel` | 0/75 | `handbrake` | 0/12 |
| `estop` | 0/2 | `hub` | 0/7 |

### 4. By-id name — PASS

`/dev/serial/by-id/usb-Gudsen_MOZA_AB6_FFB_Base_4D0040000551353133383438-if00`,
matching the expected form. No pattern adjustment needed.

### Key finding: the AB6 speaks a different command set

The device is not silent — it *rejects* the racing commands. Raw reply to a
`base-limit` read:

```
7e:21:0e:31:05:53:74:69:63:6b:20:45:72:72:6f:72:20:43:6d:64:3a:20
5b:6d:61:69:6e:5f:63:6d:64:3a:20:34:30:5d:0a:5e
```

Decoded with the framing in [`moza-protocol.md`](./moza-protocol.md):

| field | value |
| :-- | :-- |
| start | `0x7e` |
| length | 33 |
| group | `0x0e` |
| device-id | 49 |
| command-id | `0x05` |
| payload | `Stick Error Cmd: [main_cmd: 40]\n` |
| checksum | `0x5e` — **validates** against `(13 + sum) % 256` |

Two things follow, and they matter for the plan below:

- **The framing is shared.** The reply parses cleanly under the documented
  structure and its checksum validates, so `moza-protocol.md` and boxflat's
  `MozaCommand` encoder/decoder are reusable as-is.
- **The command set is not.** `40` = `0x28`, the read-group byte for the
  wheelbase `limit` command. The firmware calls itself a **`Stick`** and
  rejects that `main_cmd` outright.

This is *not* a device-ID mismatch. Sweeping IDs 16–31 with the wheelbase
commands fails at every ID, and only the "Stick Error" reply ever comes
back. Hypothesis (2) in "How to continue" below — "answers on a different
device ID" — is therefore ruled out; it is the command groups that differ.

The error string is itself a useful probe: the firmware echoes back the
`main_cmd` it rejected, so a sweep of group bytes should separate accepted
from rejected groups without needing Windows captures. Note that hand-rolled
frames get silently ignored — a group sweep must be built through
`MozaCommand.prepare_message()` to be framed correctly.

## Sweep results — the AB6 does answer, on its own groups

Run with `tools/ab6_sweep.py` (read-only) over all 256 group bytes at device
id 19. This supersedes the bleaker reading above: the racing commands all
fail, but the device is far from mute.

| Outcome | Count |
| :-- | --: |
| Carried a real payload | 14 |
| Empty ack (group exists, command id 1 isn't one of its) | 67 |
| Rejected with `Stick Error` | 49 |
| Silent | 126 |

### Groups that return real data

Byte-identical across repeated runs, so these are stable responses, not
noise. The payload echoes the requested command id (`01`) and then the value:

| Group | Payload | Reading |
| :-- | :-- | :-- |
| 2 | `02` | single byte, no id echo |
| 4 | `01:01:0b:01` | id 1 → `1.11.1`? version-shaped |
| 5 | `01:02:03:03` | id 1 → `2.3.3`? version-shaped |
| 6 | `2d:57:3b:c4:80:73:30:0c:34:38:34:31` | 12 bytes, no id echo — UID/serial-shaped |
| 10 | `01:00:01` | id 1 → 1 |
| 12 | `01:00:00:00` | id 1 → 0 |
| 14 | `01:00:01:ff:ff:ff:ff` | id 1 → 1, plus `ff` padding |
| 19 | `01:00:01` | id 1 → 1 |

Groups 4, 5 and 6 are the most promising leads: two version-shaped replies
and one UID-shaped reply are exactly the kind of identity command needed to
gate a panel, the AB6's equivalent of `base-limit`.

### Command ids within those groups

Mapped with `tools/ab6_sweep.py --ids <group>`. The groups fall into three
kinds, and telling them apart matters — two of them look like results but
are not.

**1. Fixed queries — ignore the command id entirely.** Every id returns the
same reply, so these are single commands, not addressable tables:

| Group | Fixed payload | Reading |
| :-- | :-- | :-- |
| 2 | `02` | constant |
| 4 | `01:01:0b:01` | version-shaped — `1.11.1`? |
| 5 | `01:02:03:03` | version-shaped — `2.3.3`? |
| 6 | `2d:57:3b:c4:80:73:30:0c:34:38:34:31` | UID/serial-shaped |

Two version-shaped replies is suggestive given the two-device topology —
plausibly base firmware and grip firmware, though unconfirmed.

**2. Status/ack — echo the id but return a constant.** Groups 10, 12 and 19
echo every id back and answer with the same value each time (`1`, `0`, `1`
respectively, across all 48 ids tested). They parse the request but carry no
per-id information. **Do not map these as separate commands.**

**3. A real settings table — group 14.** Nine ids, seven distinct values:

| Id | Value | Note |
| :-- | :-- | :-- |
| 0 | `00:01:00:00:80:00` | contains `0x8000` = 32768, centre-shaped |
| 1 | `00:01:ff:ff:ff:ff` | |
| 2 | `00:01:ff:ff:ff:ff` | |
| 4 | `00:01:00:00` | |
| 9 | `00:01` | |
| 10 | `00:01:01:00` | |
| 11 | `00:01` | |
| 12 | `7f:ff:7f:ff:7f:ff:00:00` | three × `0x7fff` — axis maxima for 3 axes? |
| 32 | `00:00` | |

Note that **id 5 is absent** from that list — because group 14 / id 5 is the
diagnostic log channel below, which replies with ASCII rather than an echoed
id. The two coexist on the same group, which is a good consistency check on
the mapping.

### The device has an ASCII diagnostic log

Probing high groups produced framed **text** on response group 14, command
id 5 — the same channel the `Stick Error` messages arrive on:

```
[INFO]stick_diag.c:126 Stick heart beat log
thumb_y theta: [calib_min: 8.86844, calib_mid: 29.04191, calib_…
hall_joystick_parm theta: [parm0: 0, parm1: 1, parm2: 0]
thumb_x theta: [threshold_high 0: 49.29419, threshold_high 1: 4…
```

The firmware streams live internal diagnostics — mini-stick (`thumb_x` /
`thumb_y`) calibration bounds, hall sensor parameters, thresholds, and a
heartbeat.

Two consequences:

- **Caveat on the sweep output.** These lines are asynchronous, so any
  "data" result whose *reply* group is 14 while a different group was
  requested is a log line that happened to land in the window, not an answer.
  The eight groups tabulated above all replied on the group they were asked,
  which is why they are trustworthy.
- **This is a free instrument.** Listening to group 14 / id 5 while Cockpit
  drives the device may reveal internals directly, and the log names source
  files and parameters. Worth a passive listen before any Windows capture.

## Two devices, confirmed at protocol level

The device sweep settled the topology question. Sending an identity read
across all device IDs produced diagnostic lines from **two** distinct
sources:

| Reply byte | Swapped ID | Identity | Firmware (group 4) |
| :-- | :-- | :-- | :-- |
| `0x21` | 18 | **Base** — `main_diag.c`, "Base heart beat log" | `01:06:04` → 1.6.4 |
| `0x31` | 19 | **Grip** — `stick_diag.c`, "Stick heart beat log" | `01:0b:01` → 1.11.1 |

The grip's diagnostics name `thumb_x`, `thumb_y`, `axis_z` and `hall_button`,
which matches the MHG's mini-stick, twist axis and buttons.

**Group 6 is the serial number.** At device 18 it returns
`4d:00:40:00:05:51:35:31:33:38:34:38`, which is exactly the USB serial
`4D0040000551353133383438` from the by-id path. The grip returns a different
one, as expected for a separate device.

Group 5 answers `02:03:03` on *both* devices, so it is a shared protocol
version rather than per-device firmware.

> **Correction.** An earlier revision of this document treated ID 19 as the
> AB6 base, making "AB6 firmware 1.11.1" wrong — 1.11.1 is the *grip*. The
> base is ID 18 at 1.6.4. Note that ID 18 is `main` and ID 19 is `base` in
> the racing map, which is exactly the trap: the AB6's own map is separate.

## The AB6 panel — implemented and working

The AB6 is now its own device throughout boxflat rather than being disguised
as a racing base, which is what lets it resolve against its own command set.

- `MozaHidDevice.AB6` is a separate pattern; `BASE` is back to matching only
  racing bases. `_update_axis` and `_configure_device` treat AB6 alongside
  BASE so the axis map still applies.
- `SerialDeviceMapping` / `HidDeviceMapping` register it as `"ab6"`. This is
  the key move: `MozaCommand.value_from_response` only rewrote the device
  name for `base` and `hub`, so any other name resolves against its own
  section — no changes to racing behaviour.
- Because the AB6 carries *two* devices on one port, `"ab6"` joins that
  rewrite list and resolves through its own `ab6-ids-to-names` map
  (18 → `ab6`, 19 → `mhg`). The racing map is untouched.
- `_get_device_handler` falls back to the `ab6` handler, so the grip — which
  has no port of its own — is reached through the base.
- `get_device_id` excludes `ab6` alongside `base` from the "addressed as
  main" rule, since the AB6 has its own port but answers on its own ID.
- `data/serial.yml` gains `ab6:` and `mhg:` sections.
- `boxflat/panels/ab6.py` and `panels/mhg.py` add **AB6 Base** and **MHG
  Grip** panels, each gated on `subscribe_connected(..., self.active)`
  against a real hardware read — the same mechanism the racing panels use.

Verified on hardware: both panels appear in the sidebar, and Home shows the
base at **1.6.4** with live Roll/Pitch bars plus the grip at **1.11.1**,
each appearing only when its device answers.

The panels deliberately report identity and live axis state only. Group 14's
ids are located but their meanings are not decoded, so there is nothing yet
that can honestly be presented as an editable setting.

## Home panel now lists only detected hardware

Independent of the protocol work, the Home panel hardcodes three groups —
`Wheelbase`, `Pedals`, `Handbrake` (`boxflat/panels/home.py:28,48,63`) —
built unconditionally at UI construction. They are wired to `set_active`,
which greys them out rather than hiding them, so an AB6-only setup still
shows all three racing sections greyed on the Home page.

Desired behavior: **only show what is actually detected**, i.e. an AB6 base
and an MHG flightstick for this setup. The fix is to drive these groups by
visibility rather than sensitivity — compare `SettingsPanel.active()`, which
already hides correctly via
`GLib.idle_add(self._button.set_visible, value)` (`settings_panel.py:143`).

Populating Home with AB6/MHG entries depends on the protocol work above,
since nothing about the AB6 is currently readable to drive that detection.
Per "Device topology", the MHG grip reports its own firmware version to
Cockpit, so it should end up as its own entry driven by its own device ID —
mirroring how a wheel is listed separately from its wheelbase today.

## How to continue

### Next step: map the AB6 command groups

This is now the blocking task — the Base panel definitively does not
activate, and the cause is known to be the command set, not the device ID.

1. **Group sweep (cheapest, no Windows needed).** Build messages via
   `MozaCommand.prepare_message()` and vary only the read-group byte,
   reading the reply for each. The firmware names the rejected `main_cmd` in
   its error string, so accepted groups are the ones that answer with
   something other than `Stick Error`. Hand-built frames are silently
   dropped, so go through the real encoder.
2. **Windows capture (authoritative).** Capture Moza Cockpit ↔ AB6 traffic
   with Wireshark + USBPcap on the CDC-ACM interface. Framing is documented
   in [`moza-protocol.md`](./moza-protocol.md):
   `0x7e | length | group | device-id | command-id | payload | checksum`
   (checksum = (13 + sum of bytes) % 256) — confirmed still accurate for the
   AB6, so captures can be decoded with the existing tooling.
3. Add the discovered commands as a new `ab6` section in `data/serial.yml` —
   the YAML is the single source of truth for commands.

Debug tip: uncomment the print in `SerialHandler._serial_write_handler` and
add one in `_serial_read_handler` to log raw traffic while boxflat polls.

Ruled out by testing: a different **device ID**. Wheelbase commands fail at
every ID from 16–31, so only the group/command mapping needs discovering.

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
issue #157.

Hardware confirmation now exists (see "Hardware test results"), so the PR no
longer needs to wait on the issue reporter. Two things to fix first:

- **Correct the README row.** It currently promises "base settings", which
  do not work. Detection is the honest claim.
- **Consider dropping the `_update_axis` change** from this PR, or keep it
  as an explicit standalone hardening commit — it does not affect the AB6
  and the commit message overstates what it fixes.

Framed accurately, this is still a worthwhile PR: it takes the AB6 from
completely invisible to detected and connected on both transports, which is
the prerequisite for all the settings work.

## Out of scope

Missing force feedback itself ("unknown autocenter control method",
`Invalid code 768-777` in dmesg) is a kernel HID FFB driver concern —
see [universal-pidff](https://github.com/JacKeTUs/universal-pidff) /
`hid-universal-pidff`. Boxflat only manages device settings; once the kernel
driver handles the AB6's PID descriptors, games get FFB regardless of
boxflat.
