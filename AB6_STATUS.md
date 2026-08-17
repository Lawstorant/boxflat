# Moza AB6 Support — Status & Continuation Guide

Tracking work on Moza AB6 FFB Base support for boxflat on Linux.
Upstream issue: [Lawstorant/boxflat#157](https://github.com/Lawstorant/boxflat/issues/157)

**Status as of 2026-08-18 — tested on real hardware, plus ten Windows captures.**

| Area | State |
| :-- | :-- |
| Detection (HID + serial) | ✅ Works |
| Racing commands | ❌ Device answers none of them |
| Editable settings | ✅ **33 confirmed and wired up** — 27 on the AB6 base, 6 on the MHG grip |
| Protocol framing | ✅ Shared with racing gear; async pushes need a fix (see below) |
| Command set | ❌ Different — firmware identifies as `Stick` |
| AB6's own groups | ✅ Group 30 (read) / 31 (write) is the AB6 base's settings table — spans Tables 2, 7 and 8, with a multi-byte-id addressing style for some |
| **MHG's own groups** | ✅ **Group 50 (read) / 51 (write) — a different pair from the base**, same multi-byte-id shape, on Table 13 |
| Firmware/protocol version | ✅ Read correctly and **display-format bug fixed** |
| Settings tables | 🔍 4+ diagnostic-log tables (2, 7, 8, 13), 129+ params — 35 attributed so far |
| Diagnostic log | ✅ Reassembled and parsed — see "Windows capture analysis" |
| Live force feedback | ℹ️ Confirmed out of scope — runs over standard USB HID, not this protocol (see "Out of scope") |
| Telemetry FFB page | ℹ️ Likely never touches the serial protocol at all — see below |
| AB6 + MHG panels | ✅ Work — gated on real firmware reads, 33 settings live |
| Home page | ✅ Now lists only detected hardware |

Short version: the AB6 is detected, identified and displayed. It uses the
same wire framing as racing gear but its own command set, so the racing
commands stay dead. Ten user-provided Windows captures moved this
forward a lot:

1. A passive capture of Cockpit's startup handshake found that the firmware
   logs every setting it loads in **plain ASCII** on its existing
   diagnostic channel — 129 parameter values across 4 tables — and, cross
   -checked against what the user could read directly off Cockpit's UI,
   caught and fixed a real version-display bug already in this branch.
2. A capture of the user changing **FFB Mode** in Cockpit landed the first
   fully confirmed, three-way-correlated editable AB6 setting — see "FFB
   Mode: the first confirmed, editable AB6 setting" below.
3. A capture of the user cycling **seven more Basic Settings sliders plus
   Temperature Control Mode** confirmed all eight in one pass, using the
   same correlation method at scale — see "Seven more settings confirmed
   in one pass" below.
4. A capture of the **Panel Settings page** (button lighting, slider axis
   config) confirmed Light Color and Backlit Brightness exactly, and found
   the wire structure (though not the option meaning) of a Slider Axis
   Mode command — see "Panel lighting" below.
5. A capture of **Advanced Settings** (Centering, Trim/Autopilot Following)
   confirmed two more Centering settings and, for the first time, found a
   *multiplexed* addressing style where one id carries a category+side byte
   pair ahead of the value — used to confirm four Trim/Autopilot Following
   settings at once. See "Advanced Settings" below. (The user later reported
   that Autopilot Following is documented as **AB9-only** — the wire
   commands are still correct, they may just not do anything physical on
   an AB6.)
6. A capture of the **Axis Travel** page confirmed four Travel Limit
   settings the same multiplexed way, though which physical axis is which
   isn't independently confirmed this time — see "Axis Travel" below.
7. A capture of **MHG Basic Settings** — the grip's own, separate settings
   page — found that the grip uses an entirely different group pair (50/51
   read/write, not the base's 30/31), and confirmed both of its lighting
   zones' Brightness and Color. See "The grip has its own command set"
   below.
8. A capture of an actual **DCS session** with Integrated FFB active
   confirmed live force feedback runs over standard USB HID, not this
   protocol at all — see "Out of scope" below.
9. A capture of the **Telemetry FFB** page's "Dynamic Damping (Aileron)"
   effect had zero writes even after the user changed every control on
   it — evidence this whole page's settings never reach the device over
   the serial protocol in the first place. See "Telemetry FFB likely
   never touches the serial protocol at all" below.
10. A capture of the **Special** page — not in this project's original
    page inventory, found by the user browsing Cockpit's tabs directly —
    confirmed Trim Follow Rate and a 4-selector Trim Range. See "A page we
    didn't know about" below.

33 settings are now working controls across the AB6 and MHG panels — 27 on
the base, spanning three diagnostic-log tables (2, 7, 8) on group 30/31,
and 6 on the grip's own Table 13 on its own group 50/51. Two independent
general-purpose settings tables, same underlying framing and addressing
conventions, each previously seen only as an unattributed binary burst.

Boxflat now models it correctly as **two devices on one port**: the AB6 base
(ID 18, firmware 1.1.4.6) and the MHG grip (ID 19, firmware 1.1.1.11). Both
have panels, both are gated on real hardware reads, and the Home page lists
only hardware that actually answers.

What remains is **meaning** for everything still on the base's and grip's
own pages (Special's five unattributed booleans, Panel Settings' Light
Mode/Pattern/Effect, the Output Mapping Curve, Axis Offset, Invert Axis,
the rest of MHG's Grip Settings) — Telemetry FFB looks to be structurally
out of reach rather than merely unattributed, per above. 35 parameter
addresses are attributed to a specific Cockpit UI control so far (a few
more have a confirmed wire format but unconfirmed option meaning, or a
confirmed value but unconfirmed axis/direction identity — see "Panel
lighting", "Advanced Settings", "Axis Travel", "The grip has its own
command set", and "A page we didn't know about" below). See "Windows
capture analysis" for the correlation method, now demonstrated seven times
at increasing scale — repeating it against the Output Mapping Curve and
the rest of the MHG's own Grip Settings is the direct path to covering the
rest, and one more targeted capture (logging the specific value set at
each step) would resolve the three still-ambiguous Panel Settings ids.

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
| `0x21` | 18 | **Base** — `main_diag.c`, "Base heart beat log" | `01:01:06:04` → 1.1.6.4 |
| `0x31` | 19 | **Grip** — `stick_diag.c`, "Stick heart beat log" | `01:01:0b:01` → 1.1.11.1 |

The grip's diagnostics name `thumb_x`, `thumb_y`, `axis_z` and `hall_button`,
which matches the MHG's mini-stick, twist axis and buttons.

**Group 6 is the serial number.** At device 18 it returns
`4d:00:40:00:05:51:35:31:33:38:34:38`, which is exactly the USB serial
`4D0040000551353133383438` from the by-id path. The grip returns a different
one, as expected for a separate device.

Group 5 answers `01:02:03:03` on *both* devices, so it is a shared
protocol version rather than per-device firmware.

**Versions are four-part.** Because group 4 ignores the command id, the
whole 4-byte payload is version data — there is no id byte to strip. An
earlier revision read only 3 bytes and reported 1.6.4 / 1.11.1, dropping
the leading field. The `ab6`/`mhg` commands use an empty `id: []` so the
response parser strips nothing.

> **Correction.** An earlier revision of this document treated ID 19 as the
> AB6 base, making "AB6 firmware 1.11.1" wrong — that version is the *grip*'s.
> The base is ID 18. Note that ID 18 is `main` and ID 19 is `base` in
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
base and grip with live Roll/Pitch bars, each appearing only when its device
answers.

> **Correction (2026-08-17, Windows capture).** The panel displayed
> **1.1.6.4** / **1.1.11.1** at the time — a straight big-endian read of the
> raw `01:01:06:04` / `01:01:0b:01` payload. The user then reported the
> version Cockpit itself shows for the same hardware: **1.1.4.6** / **1.1.1.11**.
> Those are the same two bytes with the last pair swapped: the wire order is
> major.minor.**build**.**patch**, not major.minor.patch.build. Fixed in
> `format_version()` (`boxflat/panels/ab6.py`) — see "Windows capture
> analysis" below.

The panels deliberately report identity and live axis state only. Group 14's
ids are located but their meanings are not decoded, so there is nothing yet
that can honestly be presented as an editable setting.

## Windows capture analysis (2026-08-17)

The user captured Moza Cockpit's connection to a real AB6 on Windows with
USBPcap + Wireshark (`0x346e:0x1002`, ~4.3s of traffic covering both
devices' full startup handshake) and provided the `.pcapng`. This is
exactly the "Phase 1 — Connect / startup" capture that
[`AB6_CAPTURE_PLAN.md`](./AB6_CAPTURE_PLAN.md) called highest-value: no
control was touched, so it is entirely passive, read-only traffic — but
startup alone turned out to reveal far more than expected. Decoded with
the new `tools/ab6_pcap_decode.py`; raw extracted artifacts are in
[`captures/2026-08-17-cockpit-launch/`](./captures/2026-08-17-cockpit-launch/).

### Framing correction: async pushes aren't bit7-toggled

Every piece of tooling so far (`tools/ab6_sweep.py`, `MozaCommand`) assumed
a response's group byte always has bit 7 set, and recovers the real group
with `toggle_bit(byte, 7)`. That holds for synchronous replies (`0x84` →
group 4, `0x86` → group 6, etc. — confirmed against this capture, still
correct). It does **not** hold for the diagnostic log: those frames carry
the plain group byte `0x0e` (14), unset, because they are asynchronous
pushes, not a reply to any specific read. Applying the toggle uniformly
turns `14` into `142` and makes the log frames impossible to attribute
correctly. `tools/ab6_pcap_decode.py` filters on the raw untoggled byte for
group 14 specifically; anything reusing `MozaCommand`-style bit7 recovery
for this stream will misparse it.

### The version-format bug (see correction above)

This is the capture's most concrete outcome: comparing the raw `group 4`
payload against the version the user read directly off Cockpit's own UI
caught a real bug in already-merged code. Fixed in `format_version()`
(`boxflat/panels/ab6.py`) — the wire order is
major.minor.**build**.**patch**, confirmed against live Cockpit values for
both devices, not just one:

| Device | Raw payload | Old (wrong) display | Cockpit's actual display |
| :-- | :-- | :-- | :-- |
| Base (18) | `01:01:06:04` | 1.1.6.4 | **1.1.4.6** |
| Grip (19) | `01:01:0b:01` | 1.1.11.1 | **1.1.1.11** |

`protocol-version` (group 5, `01:02:03:03` on both devices) reuses the same
formatter. Whether Cockpit displays that value anywhere to cross-check
against is unknown — left as-is since there is no ground truth to verify
against, and a cosmetic mislabel there is low-stakes.

### The settings sync is a readable ASCII log, not just binary frames

The most useful discovery in this capture: at connect, both firmware images
log every configuration parameter they load, in plain ASCII, on the
existing group-14/id-5 diagnostic channel:

```
[INFO]param_manage.c:340 Table 7, Param 53 Written: 1060320051 0.70000
[INFO]param_manage.c:340 Table 7, Param 68 Written: 1095761920 13.00000
[INFO]param_manage.c:340 Table 8, Param 44 Written: 1120403456 100.00000
```

Each line names a `(table, param)` address and gives the same value twice —
as a raw `int32` and as that same 4 bytes reinterpreted as an IEEE-754
`float32` (`param_manage.c` logs generically and doesn't know per-param
type, so one of the two readings is nonsense for any given param — the
plausible one is usually obvious, e.g. `0.70000` for a param that looks
like a gain, versus `2147483008.00000` for one that's clearly not a float
at all).

129 param writes were captured across four tables — full dump in
[`captures/2026-08-17-cockpit-launch/param_writes.csv`](./captures/2026-08-17-cockpit-launch/param_writes.csv):

| Device | Table | Params | Param range | Reading (qualitative — unconfirmed) |
| :-- | --: | --: | :-- | :-- |
| Base (18) | 2 | 25 | 9–97 | Mostly near-zero/huge raw values that don't read as sane floats — likely motor/hall-sensor calibration constants, not user-facing settings |
| Base (18) | 7 | 52 | 11–120 | Values in 0–100 with repeated/paired entries (13,25,20,20,28,45,40,40,45,65,60,60,66,83,80,80…) shaped like a curve table — candidate for "Axis Travel" (see capture plan Phase 2). Trailing pairs `(0.5, 0.1)` × 2 are candidate **Vibration** gain/frequency defaults |
| Base (18) | 8 | 42 | 15–58 | 16 consecutive params all `1.0` (per-axis/per-effect gain matrix?), then three repeats of a `(1.0, 0.5, 0.1)` triple matching Table 7's vibration-shaped pair, then four repeats of a `(0, 100, 100)` triple (four FFB channels with the same default range?) |
| Grip (19) | 13 | 10 | 5–25 | Small integers (`65280`×3, `15`, `0`, `2`×2, `1`) — plausibly button/LED/mode config, not FFB |

None of this is attributed to a Cockpit UI label yet — that still needs a
Phase 3 capture where one control is changed at a time. But it changes what
Phase 3 needs to *be*: see "Revised Phase 3" below.

### The grip's calibration is already human-readable

Separately from the `Table/Param` writes, the grip's diagnostic log carries
plain descriptive lines — no decoding needed at all:

```
thumb_x theta: [calib_min: 10.74953, calib_mid: 29.64034, calib_max: 49.29419]
thumb_y theta: [calib_min: 8.86844, calib_mid: 29.04191, calib_max: 48.79039]
axis_z theta: [calib_min: 6.35722, calib_mid: 7.49560, calib_max: 9.11345]
hall_joystick_parm theta: [parm0: 0, parm1: 1, parm2: 0]
hall_button work_mode: [work_mode: 1]
```

`thumb_x`/`thumb_y` are the mini-stick, `axis_z` the twist axis — this is
its hall-sensor calibration range, streamed for free on every connect. This
could plausibly back a read-only "Grip calibration" diagnostic display in
`panels/mhg.py` without touching the binary protocol at all, though that is
a nice-to-have, not a blocker.

### An unattributed binary settings-read burst

Independent of the ASCII log, Cockpit also read two AB6-specific binary
groups in a tight ~50ms burst around the same time as the param-write log
(group **31**/device 18: 35 distinct ids in one burst; group **30**/device
18: 7 ids polled continuously and repeatedly, looking more like live status
than static settings). The grip saw smaller reads on groups **51** and
**67** (device 19) — group 67 is consistently rejected
(`Stick Error Cmd: [main_cmd: 67]`, repeating every ~0.4–1s for the whole
capture), so whatever Cockpit is polling there isn't implemented by this
grip firmware and can be ignored. Full group/id breakdown:
[`captures/2026-08-17-cockpit-launch/binary_traffic_summary.txt`](./captures/2026-08-17-cockpit-launch/binary_traffic_summary.txt).

The burst's timing (concurrent with the Table 7/8 param-write log lines)
and its id count (35, in the same ballpark as the 52+42 params in Tables
7/8) are suggestive of group 31 being how these same settings get read back
over the binary channel — but this is not confirmed, and no id has been
matched to a specific table/param yet.

### Revised Phase 3 recommendation

Given the above, `AB6_CAPTURE_PLAN.md`'s Phase 3 ("per-setting writes") can
likely be done far more cheaply than originally planned: **if live writes
get logged through the same `param_manage.c` path as the boot-time load**,
then changing one Cockpit control should produce one new
`Table N, Param M Written` line, readable directly off the serial port —
no Wireshark or USB decoding required, just a passive text capture. This is
an unverified hypothesis (this capture only shows the boot-time load, not a
live write), so it's the first thing to check in the next session: change
one known-safe setting, and see whether a matching log line appears. If it
does, `AB6_CAPTURE_PLAN.md` should be rewritten to lead with that method.

> **Confirmed true by the next capture, below.** Live writes do log through
> `param_manage.c` exactly like the boot-time load. The hypothesis paid off
> immediately.

## FFB Mode: the first confirmed, editable AB6 setting (2026-08-17)

The user captured a second Windows session: opened the AB6's **Basic
Settings** page in Cockpit, moved the X/Y/Z axes, then cycled **FFB Mode**
Telemetry → DirectInput → Telemetry → Integrated → Telemetry. Decoded the
same way, into
[`captures/2026-08-17-basic-settings-axes-ffb-mode/`](./captures/2026-08-17-basic-settings-axes-ffb-mode/).

### Three-way correlation

The diagnostic log showed exactly 4 `Table 7, Param 49 Written` lines —
matching the 4 mode *transitions* in the session — with values `1, 0, 2, 0`:

| Time | Written value | Matches transition |
| --: | --: | :-- |
| 31.903s | 1 | → DirectInput |
| 33.745s | 0 | → Telemetry |
| 35.072s | 2 | → Integrated |
| 36.389s | 0 | → Telemetry |

Cross-checking against the binary traffic at those same timestamps found
the actual wire command, on both directions:

- **Write:** group **31**, device 18, id **133** (`0x85`), 2-byte int
  payload — fires 60–200ms before each diagnostic-log line, every time,
  with the exact same value.
- **Read-back:** group **30**, device 18, id **133** — polled continuously
  throughout the session (part of the "Basic Settings" page's live-refresh
  burst; see "An unattributed binary settings-read burst" above), its value
  changes from `0` to `1` to `0` to `2` to `0` at the same four moments.

All three signals — the diagnostic log, the write, and the read-back — agree
on every value at every timestamp, with zero ambiguity. This is as solid an
attribution as a passive capture can produce.

### Result

```yaml
ffb-mode:
  read: 30
  write: 31
  id: [133]
  bytes: 2
  type: int
```

Added to `data/serial.yml` under `ab6:`, and wired up as a real
`BoxflatToggleButtonRow` in `panels/ab6.py`'s "Settings" group — Telemetry
/ DirectInput / Integrated, 0/1/2 respectively, no value offset needed
since the protocol is already 0-based. This is the first AB6 setting that
is both readable *and* writable through boxflat.

### Bonus: live axis telemetry, unmapped

Four more ids under the same group-30 burst (**184**, **185**, **215**,
**216** — all on device 18) changed continuously and rapidly throughout the
session, cycling through nearly the full signed 16-bit range including
wraparound near `0x7fff`/`0x8000`. This lines up with the user moving the
X/Y/Z axes during the capture and is almost certainly live axis position
telemetry over the serial channel — a second, redundant path to the same
data HID already provides via `MozaAxis`/`evdev` for the existing Roll/
Pitch bars in `panels/ab6.py`. Not decoded further since the panel's HID
axis display already covers this; noted here in case a future serial-only
telemetry feature wants it. `id 12` (`0x0c`, constant `0x7fff`) sitting
alongside them is plausibly an axis range/max constant.

## Seven more settings confirmed in one pass (2026-08-17)

A third capture, provided by the user: on the AB6's Basic Settings page,
changed **Temperature control mode** from its default to Conservative then
to Aggressive, then cycled each of the seven remaining sliders — in
on-screen top-to-bottom order, per the accompanying screenshot — through
10% → 90% → 100%, then back to original. Decoded into
[`captures/2026-08-17-basic-settings-other-settings/`](./captures/2026-08-17-basic-settings-other-settings/).

Applied the same method that confirmed FFB Mode, at scale: reassemble the
diagnostic log with per-fragment timestamps, find every `Table 7, Param N
Written` line, then search the ±1.5s window before each one for a group-31
write on device 18 whose payload matches. It worked cleanly for all eight
settings on the first pass — 34 param writes, all landing in exactly the
windows expected, values matching every transition exactly with no manual
correction needed:

| Setting | Table 7 param | Group 31 id | Values seen | Cockpit order |
| :-- | --: | --: | :-- | --: |
| Temperature Control Mode | 99 | 192 (`0xc0`) | `1, 2` | 1st (before sliders) |
| Maximum Torque Output | 100 (+17, 18) | 169 (`0xa9`) | `10, 90, 100` | 1st slider |
| Overall Force Feedback Intensity | 52 | 174 (`0xae`) | `10, 90, 100` | 2nd |
| Spring | 15 | 175 (`0xaf`) | `10, 90, 100, 48` | 3rd |
| Damper | 16 | 176 (`0xb0`) | `0, 1, 10, 90, 100` | 4th |
| Inertia | 53 | 177 (`0xb1`) | `10, 90, 100, 70` | 5th |
| Friction | 54 | 178 (`0xb2`) | `10, 90, 100, 60` | 6th |
| Game Force Feedback Gain | 101 | 153 (`0x99`) | `10, 90, 100` | 7th |

All are direct 0–100 percentages — no scaling, unlike some racing-base
commands (e.g. `base-ffb-strength` needs `*10`). Attribution confidence:

- **Order matches the screenshot exactly**, top to bottom, with no gaps or
  swaps.
- **The three sliders with non-default endings (Spring 48%, Inertia 70%,
  Friction 60%) landed on exactly their screenshot values.** These are
  specific, non-round numbers — a wrong id-to-setting mapping would need an
  implausible coincidence to reproduce three of them independently.
- **Every write matches the diagnostic log's value exactly, every
  transition** (up to 4 per setting), the same standard FFB Mode was held
  to.
- Unlike FFB Mode and `torque`, the other six **don't have an independently
  confirmed read-back** in this capture — no reply was seen on group 30
  (or on group 31 itself, checked as a second guess) for those ids at all,
  suggesting Cockpit doesn't round-trip-confirm a drag in progress. `read:
  30` for those six is inferred by analogy (matches `torque`, `ffb-mode`,
  and the write+1 convention used everywhere else in `data/serial.yml`),
  not independently verified. Worth confirming on a future capture that
  includes reopening the Basic Settings page.
- `torque`'s writes also touch two more Table 7 params (17 and 18) every
  time, always equal to each other, and equal to roughly `torque × 0.824`
  rather than the raw percentage — plausibly a pair of per-motor
  (dual-servo) effective-torque values the firmware derives internally.
  Not exposed as separate boxflat commands since `torque` (the percentage
  Cockpit actually shows and writes) is the one that matters for a control.

All eight settings (including `ffb-mode` from the previous capture) are now
in `data/serial.yml` under `ab6:` and wired up as working controls in
`panels/ab6.py`'s "Settings" group — `torque`/`ffb-intensity`/`spring`/
`damper`/`inertia`/`friction`/`game-ffb-gain` as sliders,
`temp-control-mode` as a toggle (only Conservative/Aggressive were
exercised; a third mode at value 0 is plausible but unconfirmed).

What's still unmapped from the Basic Settings page: axis output curves
(Spring/Damper/Inertia/Friction each likely have their own curve-shaping
sub-controls, going by the racing base's `ffb-curve-x1..4`/`y1..5`
precedent), and the Expert Settings / Telemetry FFB / Axis Travel / Panel
Settings pages entirely (see `AB6_CAPTURE_PLAN.md`'s Phase 2 checklist).

## Panel lighting: two more confirmed, plus a structural finding (2026-08-17)

A fourth capture, provided by the user: the AB6's **Panel Settings** page
(button lighting and slider axis config), with everything on the page
touched except "Start Calibration". Decoded into
[`captures/2026-08-17-panel-settings/`](./captures/2026-08-17-panel-settings/).

This time the writes land on **Table 2**, not Table 7 — and every id here
writes to *two* Table 2 params simultaneously with identical values, the
same shape as `torque`'s Param 17/18 side effect from the first settings
capture.

### High confidence: two settings confirmed exactly

- **`light-color`** (id 102): 5-byte wire payload `[0x00, 0x00, R, G, B]`.
  The last value written, `0x5b0000`, decodes to `RGB(91, 0, 0)` — an exact
  match for the screenshot's displayed color. Wired up with
  `BoxflatNewColorPickerRow` in `panels/ab6.py`, following the existing
  `wheel-idle-color` pattern, with a small wrapper to add/strip the
  leading `[0, 0]`.
- **`backlit-brightness`** (id 103): wire values were `15, 0, 11, 15` —
  directly the 0–15 range the screenshot's slider shows, no scaling
  needed. (Table 2's own copy multiplies this by ~17 internally to a
  0–255 byte, matching `15 × 17 = 255` exactly against the raw
  diagnostic-log value — but that scaling is firmware-internal and doesn't
  affect what boxflat sends.)

### A structural finding: `slider-mode-left` / `slider-mode-right`

id 113 was written with a **2-byte payload where the first byte is 0 for
the Left slider and 1 for the Right slider**, and the second byte the
actual mode value (0, 1, 2 all seen, ending at 0 for both sides). That
side-selector-as-payload-prefix is exactly the shape of a multi-byte `id`
already used throughout this file (e.g. `base.ffb-curve-x1`'s `id: [34,
1]`), so it maps cleanly to two commands:

```yaml
slider-mode-left:  { id: [113, 0], ... }
slider-mode-right: { id: [113, 1], ... }
```

**The wire format is confirmed; the option meaning is not.** We know values
0/1/2 exist and get written together on both sides, but not which UI
choice each one names. `AB6_CAPTURE_PLAN.md` already guessed this control
might be the manual's "Slider mapping mode — Button/Axis/Mixed" family;
that's the leading hypothesis, unconfirmed. Added to `data/serial.yml` for
the wire format (safe — it's independently verifiable and doesn't depend
on the guess), but **not** wired into a panel control, since shipping the
wrong option label would be worse than not shipping a label at all.

### Three ids found but not attributed: Light Mode, Pattern, Light Effect

Three more ids were touched, matching (in some order) the page's Light
Mode toggle (Telemetry/Device/Manual), Pattern toggle (Step/Strength), and
Light Effect dropdown ("Always On" in the screenshot):

| id | Table 2 params | Values seen | Best guess |
| --: | :-- | :-- | :-- |
| 101 (`0x65`) | 54, 59 | `2,1,0,1,0,1,2,1,0` (9 writes, ending at 0) | Light Mode — most transitions, fits a 3-way toggle clicked around |
| 104 (`0x68`) | 52, 57 | `1,0` (ending at 0) | Pattern — exactly 2 distinct values, fits a 2-way toggle |
| 105 (`0x69`) | 53, 58 | `4` (one write) | Light Effect — single pick, fits a dropdown with several options |

Unlike `light-color` and `backlit-brightness`, **none of these has a
unique final value to check against the screenshot** — "0", "0" and "4"
could each plausibly be several different UI states, and the "most
transitions → most-clicked toggle" reasoning above is a plausibility
argument, not proof. Not added to `data/serial.yml`. A follow-up capture
that logs the *specific* value set at each step (the way the previous
capture's screenshot uniquely fixed Spring/Inertia/Friction) would resolve
this in the same pass.

## Advanced Settings: Centering and Trim/Autopilot Following (2026-08-18)

A fifth capture, provided by the user, split into two parts (a long
session saved in chunks — `part1` has no USB enumeration frames of its
own, so `tools/ab6_pcap_decode.py` gained a `--device-address` flag to
carry over the address `part0` autodetected). Covers three pages:
Centering, Physics Model Settings (Simplified — the same seven sliders
already confirmed, re-touched and re-confirmed here with identical values,
nothing new there), and Trim/Autopilot Following. Decoded into
[`captures/2026-08-18-advanced-settings/`](./captures/2026-08-18-advanced-settings/).

### Centering: two more Table 7 settings

Same correlation method as before, same group 30/31:

| Setting | id | Values seen | Confidence |
| :-- | --: | :-- | :-- |
| Effect Strength | 209 | `10, 90, 100, 50` (final) | High — matches the screenshot's 50% exactly |
| Compensation Effective Range | 210 | `90, 100, 10` (final, wire values) | High — same wire convention, adjacent id number |

`centering-compensation-range` is worth a note: the *wire* values (90, 100,
10) are the usual direct percentages, but Table 7's own internal float
storage for this one doesn't scale linearly with them (wire 100 → stored
0.55, not 1.0). That's a firmware-internal detail — boxflat only sends and
reads the wire value, which behaves exactly like every other percentage
setting in this file.

Two more Table 7 ids were touched (116, 121 — single boolean values, no
pairing) — plausible candidates are the page's **Link + and -** / **Link X
and Y** checkboxes, in that order, but with no unique value to confirm
against (both are simple 0/1 toggles). Not added to `data/serial.yml`.

### Trim/Autopilot Following: a new addressing style, four more settings

This page's settings live in **Table 8**, and introduced something new:
instead of one `id` per setting (like everything found so far), **one id
(225) multiplexes many Table 8 sub-settings** behind a 3-byte payload
shaped `[category, side, value]`:

```
09 00 0a   ->  category 0x09, side 0 (X),    value 10   (Physical Stick Follow Ratio X)
09 01 0a   ->  category 0x09, side 1 (Y),    value 10   (Physical Stick Follow Ratio Y)
0a 00 0a   ->  category 0x0a, side 0 (Roll),  value 10   (Roll Breakout Force Strength)
0a 01 0a   ->  category 0x0a, side 1 (Pitch), value 10   (Pitch Breakout Force Strength)
0b 00 0a   ->  category 0x0b, side 0 (Roll),  value 10   (Roll Breakout Force Range)
0b 01 0a   ->  category 0x0b, side 1 (Pitch), value 10   (Pitch Breakout Force Range)
```

This is the same shape as `slider-mode-left`/`-right`'s `id: [113, side]`
finding from the Panel Settings capture, just one byte longer — modeled
the same way, as extra `id` bytes (`id: [225, category, side]`) rather
than as payload, so it's `data/serial.yml`'s existing multi-byte-id
convention (see `base.ffb-curve-x1`'s `id: [34, 1]`) scaled up by one
byte, not a new mechanism.

All six ended at values that matched the screenshot exactly — 100% for
both follow-ratio axes, 50% for both breakout-force-strength sides, 50%
for both breakout-force-range sides (again with the same "wire is linear,
Table 8's internal float isn't" pattern as `centering-compensation-range`,
and again irrelevant to what boxflat sends). Added as `follow-ratio-x`/
`-y`, `breakout-force-strength-roll`/`-pitch`, `breakout-force-range-roll`/
`-pitch`, and wired up as sliders in a new "Trim & Autopilot Following"
group in `panels/ab6.py`.

### What's still unresolved on these two pages

- **Three more single-value booleans** in Table 8 (params 32, 33, 34) —
  not attributed; candidates include the page's own Link +/- and Link X/Y
  checkboxes (this section has them too) or parts of the Trim/Autopilot
  Following toggles.
- **A compound "preset select" burst.** Around the same id (225), a
  different category byte pattern (`0x0e`, `0x0f`, `0x11` seen) triggers a
  *cascade* of writes across several Table 8 params at once, three times
  in quick succession. This has the shape of clicking through a 3-option
  preset selector — either **Axis follow mode** (No Follow / Full Follow /
  Custom) or **Follow options** (Light Aircraft / Heavy Aircraft / Custom),
  both 3-way selectors on this page. Not decoded — the payload structure
  and which of the two selectors it is are both unclear, and getting it
  wrong risks a command that changes several settings at once.
- **Everything not touched in this capture**: the Trim Following and
  Autopilot Following toggles themselves, Axis follow mode, X/Y-axis
  follow ratio (a *different* -1..1 ranged control from the 0-100%
  Physical Stick Follow Ratio confirmed above — easy to confuse, don't),
  physical stick follow rate (1-20 range), Trim-stick curve, Sidestick AP
  Lock, Roll/Pitch Follow Scale, Roll/Pitch Follow Rate. These simply never
  produced a write in this capture (left at their defaults), not something
  that was tried and failed to attribute.

> **Correction — Autopilot Following is reportedly AB9-only.** The user
> reports that Moza documents this feature (`follow-ratio-x`/`-y`,
> `breakout-force-strength`/`-range-roll`/`-pitch`) as only having a
> physical effect on the AB9, not the AB6. The wire commands above are
> still confirmed correct — the AB6 accepts and echoes them back over the
> same protocol — they may just be inert on this hardware, since the AB6
> has no motorized trim to physically follow an autopilot signal with.
> Left in `data/serial.yml` and the panel (now with a note in the UI
> itself), since the confirmed protocol work has value regardless of
> whether the AB6 acts on it, and Cockpit clearly still shows and accepts
> these settings for an AB6 user.

## Axis Travel: travel limits confirmed, curve and offset still open (2026-08-18)

A sixth capture, provided by the user: Cockpit's **Axis Travel** page
(Output Mapping Curve, Invert Axis, Axis Positive/Negative Travel Limit,
Axis Offset — per stick axis, X/Y/Z). Decoded into
[`captures/2026-08-18-axis-travel/`](./captures/2026-08-18-axis-travel/).

### Confirmed: Axis Travel Limit, both directions, two axes

Same method, same group 30/31, clean `[axis_id, direction, value]`
structure — direction byte 1 = positive, 2 = negative, matching the
already-established multi-byte-id convention:

| Setting | id | Values seen | Confidence |
| :-- | --: | :-- | :-- |
| Axis 1 Positive Travel Limit | `[171, 1]` | `1, 10, 90, 100` | High — matches screenshot's 100% |
| Axis 1 Negative Travel Limit | `[171, 2]` | `10, 90, 100` | High — matches screenshot's 100% |
| Axis 2 Positive Travel Limit | `[172, 1]` | `10, 90, 100` | High — matches screenshot's 100% |
| Axis 2 Negative Travel Limit | `[172, 2]` | `10, 90, 100` | High — matches screenshot's 100% |

**But which physical axis is "1" and which is "2" isn't independently
confirmed** — both pairs end at the identical value (100%), so there's no
unique number to disambiguate them the way Spring/Inertia/Friction's
distinct final percentages did back in the first settings capture. The
attribution rests on two *consistent but not proof-level* signals: id 171
was touched before id 172 in this capture, and 171 also precedes 172 in
the connect-time settings-read burst from the very first capture — both
agree with the page's left-to-right X/Y/Z layout, neither is a value
match. Labeled "Axis 1"/"Axis 2" in the panel rather than asserting X/Y,
with a subtitle noting the ambiguity, rather than risk a user constraining
the wrong physical axis while believing a UI label that isn't actually
confirmed.

### Found, not attributed: curve, offset, invert, and a reset button

- **Output Mapping Curve** (id 15/`0x0f` on **Table 2**, a new table for
  this session). Each drag of one of the curve's control points writes
  *four* Table 2 params at once, with a payload shaped
  `[point_selector_byte, 16-bit value]`. Multiple point selectors were seen
  (`0x80`, `0x81`, `0x84`) but the exact point-index/axis encoding wasn't
  pinned down — this needs a capture with one point moved to one specific,
  logged value, the same discipline that resolved everything else in this
  document.
- **Axis Offset** (id 173) — only one sample per axis: wire value `175`.
  The screenshot's range is `-75..75`; `175 - 100 = 75` fits one extreme of
  that range under a `value + 100` bias hypothesis, but with a single data
  point this isn't confirmed, and a wrong bias on a real axis-offset
  setting is a worse failure mode than a cosmetic mislabel. Not added.
- **Invert Axis** — two boolean candidates (Table 7 params 19 and 46,
  final value 0, matching the screenshot's "off" for every axis shown).
  Unlike every other id pair found this session, **their touch order
  contradicts their id order** (46 touched before 19, despite 19 < 46 and
  19 preceding 46 in the connect-time read burst) — the one internal
  consistency check that supported the Axis Travel Limit attribution above
  fails here. Not added, even generically.
- **A "Reset" button click** (Table 2, param 9, id 90) — single boolean,
  `1` then `0` in quick succession, shaped like a momentary button press
  (matching the page's per-axis "Reset" button) rather than a persisted
  setting. Not added — a button needs its own confirmed one-shot write
  semantics, not the read/write pair this file's commands assume.

## The grip has its own command set: two lighting zones confirmed (2026-08-18)

A seventh capture, provided by the user: Cockpit's **MHG** page — the
grip's only settings tab. Covers Grip Settings (Cogging Torque
Calibration, Yaw Axis, Mode 1/Mode 2 mapping, Axis Calibration, Mapping
Range) and two lighting zones, Status Light and Button Light. Decoded into
[`captures/2026-08-18-mhg-basic-settings/`](./captures/2026-08-18-mhg-basic-settings/).

### A different write group than the base

Every AB6 base setting confirmed so far — 22 of them, across three
diagnostic-log tables — landed on group 30 (read) / 31 (write). Applying
that same pair to the grip's writes found **nothing**: every correlation
attempt came back "no match". The actual traffic in this capture told a
different story: the grip's Table 13 settings go out on **group 50
(read) / 51 (write)** instead, on device id 19 as always. Once corrected,
every write matched the diagnostic log exactly, the same as every other
finding in this document.

### Two lighting zones, six settings, same multi-byte-id shape as the base

The grip has independently colored/lit **Status Light** and **Button
Light** zones. Each of three "categories" (brightness, color, effect) uses
one shared id with a side byte selecting which zone — structurally
identical to `slider-mode-left`/`-right` and the Axis Travel Limit
findings, just on the grip's own group 50/51:

| Setting | id | Values seen | Confidence |
| :-- | --: | :-- | :-- |
| Status Light Brightness | `[98, 0]` | `12` (one sample) | High — matches screenshot exactly |
| Button Light Brightness | `[98, 1]` | `7, 2, 15` | High — matches screenshot's 15 exactly |
| Status Light Color | `[99, 0]` | ends `RGB(76,0,0)` | High — matches screenshot exactly |
| Button Light Color | `[99, 1]` | ends `RGB(49,0,0)` | High — matches screenshot exactly |
| Status Light Effect | `[100, 0]` | `2, 3, 1` (ends 1) | Medium — see below |
| Button Light Effect | `[100, 1]` | `0, 3, 5, 2` → wire `1` (ends 1) | Medium — see below |

The color payload is `[side, R, G, B]` — 4 bytes, notably **without** the
AB6 base's leading `[0, 0]` padding (`light-color` there is 5 bytes for
the same 3-byte color). Don't assume the two devices' commands share a
byte layout just because they share a category-id/side-byte shape.

Light Effect's confidence is lower for a specific reason: both zones ended
at the *same* wire value (1), which matches both showing "Always On" in
the screenshot — a real confirmation, but only one data point out of an
observed 0–3 range, not a swept range like brightness's 0–15 or color's
full RGB. Added to `data/serial.yml` for the confirmed structure, but — matching how the AB6 base's own unconfirmed Light Effect finding (id 105)
was handled — **not** wired into the panel.

### What's still open

- **Four more Table 13 params** (18, 22, 25, 27) — booleans or small
  ints, plausible candidates include Enable Yaw Axis Output, Press Stick
  to Switch Mode, and the Mode 1/Mode 2 dropdowns, but none confidently
  attributed.
- **An inconsistency around params 23/24**: two different ids (101, 102)
  both appeared to target these params, with wire values that didn't match
  what the diagnostic log recorded as stored — unlike every other finding
  in this document, where wire value and stored value agreed (give or take
  a known firmware-internal transform). Not decoded; flagged rather than
  guessed past.
- **Cogging Torque Calibration, Yaw Axis Calibration, Axis Calibration**
  are all momentary actions (buttons), not persisted settings — need their
  own one-shot semantics, not this file's read/write pair, the same
  reasoning that excluded the AB6 base's "Reset" button above.

## Telemetry FFB likely never touches the serial protocol at all

The user changed every control on the "Dynamic Damping (Aileron)" effect
(Enable Effect, Effect Strength, Aerodynamic Damping, the curve) in a
follow-up to the capture noted in `AB6_CAPTURE_PLAN.md`'s Telemetry FFB
entry — and confirmed **nothing showed up on USB**. That's not a capture
mistake. It fits everything else observed about Telemetry FFB:

- The DCS session capture (see "Out of scope" above) showed live force
  feedback running entirely over standard USB HID interrupt transfers, not
  the CDC serial channel this document reverse-engineers.
- Telemetry FFB configuration is inherently per-aircraft (the page is
  filtered by airframe, e.g. "Jet 27") and Cockpit's own preset selector
  shows "DCS Hornet (Unsaved)" - language that fits a **local profile
  database on the PC**, not a value synced to the device's own settings
  table the way Basic/Advanced/Panel/Special settings all are.

Working theory: Telemetry FFB curves and strengths live entirely in
Cockpit's local per-aircraft profile, get evaluated against live telemetry
on the PC, and only ever reach the AB6 as computed HID PID force commands
during actual gameplay — never as a stored "setting" over the serial
protocol at all. If that's right, this page is **permanently out of scope**
for `data/serial.yml` in a way none of the other pages are - there's no
serial command to find, because none exists. Nothing to do here unless
this theory turns out to be wrong for some other effect or control on the
page.

## A page we didn't know about: Special settings (2026-08-18)

An eighth capture, provided by the user: Cockpit's **Special** page —
not in this project's original page inventory (`AB6_CAPTURE_PLAN.md`'s
"Cockpit's page structure" list predates knowing this tab existed), found
by the user browsing Cockpit's tabs directly. Covers **Controls**
(Hardware Trim Mode, Trim Mode Direct Input/Hardware, hardware trim button
bindings, Trim Follow Rate, Trim Range) and **Miscellaneous** (Base Force
Model Selection, Grip Removal Protection, Extend Travel Range). Decoded
into [`captures/2026-08-18-special-settings/`](./captures/2026-08-18-special-settings/).

### Confirmed: Trim Follow Rate, and a 4-selector Trim Range

Same method, same group 30/31:

| Setting | id | Values seen | Confidence |
| :-- | --: | :-- | :-- |
| Trim Follow Rate | 196 | `10, 8` (final) | High — matches screenshot's 8 exactly, direct 1-20 range |
| Trim Range (×4) | `[198, 0..3]` | each `X, 100` (final) | High on the value, unconfirmed on direction |

The four Trim Range selectors are the **same `[id, selector]` shape** as
`slider-mode-left`/`-right` and the Axis Travel Limit commands, just with
4 selectors instead of 2 — matching the page's 4-direction (+X/-X/+Y/-Y)
control. All four ended at wire value 100, matching all four screenshot
fields showing 100% — but with all four landing on the *same* value, same
situation as `axis-travel-limit-1`/`-2`: nothing to disambiguate which
selector is which physical direction. Added as `trim-range-0` through
`trim-range-3`, named by selector number rather than guessing a direction.

### Found, not attributed: five booleans, one on a different table

Params 102, 114, 122, 123 (Table 7) and 44 (Table 2, notably the only one
*not* on Table 7 like everything else on this page — recalls how the
Panel Settings lighting stuff also lived on Table 2 while Basic Settings
lived on Table 7). Plausible candidates for the five: Hardware Trim Mode,
Grip Removal Protection, Base Force Model Selection, Extend Travel Range —
one candidate short of the five available slots even before considering
that the trim button bindings (unbind/bind assignments) aren't settings
in this file's sense at all. Two of the five (params 102 and 114) show a
"touched near the start, long gap, touched again near the end" shape,
suggestive of a top-level toggle that gates the visibility of everything
below it — the same pattern the Centering page's Adaptive Centering
Compensation showed in an earlier capture. Not decoded further; the
button-binding controls and calibration buttons on this page also aren't
settings in this file's read/write sense and were excluded for the same
reason as the AB6 base's "Reset" button and the MHG's calibration buttons.

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

### Next step: attribute more parameters to Cockpit UI controls

The method is proven — FFB Mode (see above) went from "unknown parameter
table" to "working boxflat control" from one Wireshark capture, by
correlating three independent signals (the write, the read-back, and the
diagnostic log) at the timestamps where the user changed one thing at a
time. Repeat it per setting:

1. Capture Cockpit with one control changed at a time — ideally per
   [`AB6_CAPTURE_PLAN.md`](./AB6_CAPTURE_PLAN.md)'s Phase 3 checklist (one
   setting, low value, high value, back to original, ~2s pauses).
2. Decode with `tools/ab6_pcap_decode.py capture.pcapng --out-dir
   captures/<name>`.
3. Find the `Table N, Param M Written` lines that changed only around the
   moment that setting was touched (`param_writes.csv` plus the log's
   timestamps — see the FFB Mode section above for the exact method: search
   requests in a ±0.5s window around each log line's timestamp for a write
   whose payload matches the written value).
4. Confirm three-way: the write, a read-back on the matching group (writes
   and their read-back group appear to consistently differ by 1 — FFB
   Mode's is read 30 / write 31 — worth checking as a first guess for any
   new group pair), and the diagnostic log all agree at every timestamp.
   Two independent transitions matching is a coincidence; three or more,
   as with FFB Mode, is proof.
5. Add the confirmed `read`/`write` group and command id to `data/
   serial.yml` under `ab6:` (or `mhg:` for grip settings), and a row to
   `panels/ab6.py` / `panels/mhg.py` — see "AB6-specific settings panel"
   below for the exact pattern, now demonstrated once with FFB Mode.

Cross-check anything version-like or percentage-like against what Cockpit's
own UI shows wherever possible — that's what caught the version-display
bug earlier in this session. Cockpit's UI is ground truth, this repo's
inferences are not.

Debug tip: uncomment the print in `SerialHandler._serial_write_handler` and
add one in `_serial_read_handler` to log raw traffic while boxflat polls.

### AB6-specific settings panel (follow-up feature)

`panels/ab6.py` and `panels/mhg.py` already exist and are wired up (see
"The AB6 panel — implemented and working"), deliberately showing identity
and live axis state only. Once a setting is attributed per the step above:

1. Add its `read`/`write` group and command id to the `ab6` (or `mhg`)
   section of `data/serial.yml`.
2. Add a row to `panels/ab6.py` (or `panels/mhg.py`) under a real
   "Settings" group, following the pattern already used in
   `panels/base.py` — a widget, `self._cm.subscribe_connected(...)` for the
   value, `self._current_row.subscribe(self._cm.set_setting, ...)` for
   writes.

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

**Confirmed by a capture of an actual DCS session (2026-08-18, Integrated
FFB mode).** The user shared a USBPcap capture of live gameplay. Two
things worth recording:

- **Live force feedback goes over standard USB HID interrupt transfers**
  (report sizes 7–88 bytes, shaped like textbook HID PID — Set Effect, Set
  Envelope, Set Condition, Set Periodic, Effect Operation, etc.), not the
  CDC serial channel this document reverse-engineers. That's exactly
  `universal-pidff`'s territory, not boxflat's or `data/serial.yml`'s —
  independent confirmation that the "out of scope" line above is drawing
  the boundary in the right place.
- **The serial (CDC) traffic during the session was just the same
  connect-time settings load already documented** in "Windows capture
  analysis" above (Tables 2, 7, 8, same param numbers, same values) — a
  third independent capture landing on the identical boot sequence is good
  confirmation that model is right, but nothing new to attribute from it.
