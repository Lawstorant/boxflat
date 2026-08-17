# AB6 Protocol Capture — Action List

Field checklist for capturing Moza Cockpit ↔ AB6 traffic on Windows, so the
AB6 command set can be added to `data/serial.yml`.

Companion to [`AB6_STATUS.md`](./AB6_STATUS.md). Read the "Key finding"
section there first — the framing is already known and confirmed, so this
capture only needs to discover **command groups, command ids, and payload
semantics**.

## Pick your tool

The AB6 is CDC-ACM, so Cockpit is talking to a plain COM port.

- **Preferred — serial port sniffer** on the AB6's COM port. Gives you the
  byte stream already framed the way `moza-protocol.md` describes. No USB
  decoding, no endpoint filtering.
- **Fallback — USBPcap + Wireshark**, filtered to the CDC-ACM data
  interface. Works, but you decode the USB layer before you reach the bytes.

Either way, sanity-check before doing real work: open Cockpit and confirm
you see frames beginning `0x7e`. If not, fix the capture setup first —
everything below is wasted otherwise.

## Pre-flight

- [ ] Unplug the AB6 from the Linux box (nothing else may hold the port)
- [ ] Note the AB6 firmware version shown in Cockpit
- [ ] Note the COM port number assigned to the AB6
- [ ] Close all other Moza software
- [ ] Open a plain text log file — you will write timestamped notes as you go
- [ ] Confirm capture works (frames starting `0x7e` appear)

## Phase 0 — Idle baseline

*Why: identifies unsolicited/heartbeat traffic so you can filter it out of
every later capture.*

- [ ] Cockpit **closed**, device connected, capture running
- [ ] Record ~60 seconds of nothing
- [ ] Save as `00-idle.*`

## Phase 1 — Connect / startup

*Why: highest value per minute. Cockpit polls settings on connect, so this
single passive capture likely reveals the read group plus a large fraction
of the command ids at once — with zero risk of mislabeling.*

- [ ] Start capture **first**, then launch Cockpit
- [ ] Wait until the AB6 page is fully loaded and populated
- [ ] **Touch no control**
- [ ] Stop capture, save as `01-startup.*`

## Phase 2 — Page tour, reads only

*Why: page switches trigger reads for that page's group. This is how you
find out whether the AB6 uses several groups (spring/trim/per-axis settings
may each live in their own).*

Cockpit's page structure, per the AB6 manual — visit these in order:

- [ ] **Basic Settings** — base parameters, real-time status
- [ ] **Expert Settings** — advanced per-aircraft tuning
- [ ] **Telemetry FFB** — telemetry-driven effects config
- [ ] **Axis Travel** — axis output curves
- [ ] **Panel Settings** — the 2 sliders and 8 RGB buttons
- [ ] **MHG grip page** — click the grip icon on the main page

Then:

- [ ] Pause ~3s on each page
- [ ] **Change nothing**
- [ ] Log each page name with its timestamp as you go
- [ ] Save as `02-page-tour.*`

> **Watch the main page for the grip.** The manual says the MHG appears there
> with its own firmware version. Whatever Cockpit sends to learn that version
> is the grip's identity command — and the equivalent of `base-limit` for
> gating an MHG panel in boxflat. It is one of the most valuable frames in
> this whole capture.

## Phase 3 — Per-setting writes

*Why: this is the write side and the payload semantics — scaling, ranges,
byte count — which reads alone cannot tell you.*

Rules for this phase:

- **One setting at a time. Never batch.** Command ids are attributable only
  if you know exactly which setting you touched.
- **Type exact values; don't drag sliders.** Dragging streams a burst of
  writes and buries the boundaries.
- **Use distinct, memorable values** so you can spot the payload in hex.
- **Pause ~2s between actions** so bursts separate visually.

Settings to cover, per
[MOZA's Flight FFB documentation](https://support.mozaracing.com/en/support/solutions/articles/70000684205-force-feedback-telemetry-settings)
— all shown as percentages in Cockpit:

| Setting | Existing boxflat `base` equivalent |
| :-- | :-- |
| Overall Strength | `ffb-strength` |
| Spring / Centering | `spring` |
| Damping | `damper` |
| Inertia | `inertia` |
| Friction | `friction` |
| **Vibration** | **none — new** |

Five of the six already exist as racing-base commands with the same
vocabulary, which fits the "shared framing, different command set" finding.
**Vibration and the FFB mode switch are the genuinely new ones** — capture
those most carefully.

For each setting:

- [ ] Log the setting name and its current value
- [ ] Set to a low value (e.g. `10`), pause 2s
- [ ] Set to a high value (e.g. `90`), pause 2s
- [ ] Set back to the original, pause 2s
- [ ] Log the displayed UI value at each step

FFB modes are likely their own command — stamp each switch:

- [ ] Switch to **Standard** FFB mode (DirectInput, no telemetry)
- [ ] Switch to **Telemetry** FFB mode
- [ ] Switch to **MCLS** mode (DCS control-loading model)

### Beyond FFB — other command families

The manual describes several surfaces that are not FFB settings at all. Each
is probably its own command group, and none of them exist in boxflat today
for a flight device:

- [ ] **Slider mapping mode** — cycle Button → Axis → Mixed
- [ ] **Button RGB lighting** — set a static color, then change it
- [ ] **Lighting effect** — cycle static / blinking / breathing / telemetry
- [ ] **Lighting brightness** — low, then high
- [ ] **Axis Travel curve** — move one curve point, then reset

> `boxflat/panels/base.py` already has curve infrastructure (`_curve_x`,
> `_curve_presets`) for racing bases. If the AB6's Axis Travel curves use the
> same shape, that UI is largely reusable — worth capturing carefully.

### MHG grip settings

Separate device, separate command surface (see "Device topology" in
`AB6_STATUS.md`):

- [ ] Open the grip page, change a **button lighting** setting
- [ ] Change a **grip button mapping**, if Cockpit exposes one
- [ ] Note the grip's firmware version as displayed

Cockpit shows these as percentages; watch for scaling to the 0–65535 range
the racing commands use.

Save one capture per setting where practical (`03-<setting>.*`), or one
continuous capture with a precise log.

## Phase 4 — Round-trip verification

*Why: confirms which settings persist on the device versus living only in
Cockpit, and confirms your read/write pairing is real.*

- [ ] Change one setting, close Cockpit, reopen — does the read reflect it?
- [ ] Replug the device, reopen Cockpit — did it persist?
- [ ] Save as `04-roundtrip.*`

## Do not capture

- **Firmware update** — never.
- **Stick motion / FFB effect traffic** — continuous, high volume, not
  settings. Keep the stick still during capture.
- **Telemetry-driven FFB with a sim running** — same problem. Moza's
  telemetry mode streams continuously (DCS, MSFS, X-Plane, IL-2) and will
  bury the settings traffic.
- **Calibration wizards** — the AB6 has three (slider calibration, grip axis
  calibration, and **cogging torque calibration**). They write a lot and drive
  the motors. Capture separately and clearly labeled, if at all — never mixed
  into a settings capture.

## Log template

Keep this alongside the captures. Timestamps plus notes are what make a
capture attributable — this is the step people skip and regret.

> There is an interactive version of this checklist that stamps the time
> automatically as you tick each step, and exports the filled-in table below
> with "Copy log":
> <https://claude.ai/code/artifact/9ad549c7-1775-42fd-b75b-0270baf83f9f>
>
> Stamps come from the clock of the machine *viewing* that page — open it on
> the Windows capture machine, or note the offset between the two clocks.

| Time | Phase | Action | UI value |
| :-- | :-- | :-- | :-- |
| 14:02:11 | 1 | Launched Cockpit, no input | — |
| 14:05:03 | 3 | Spring strength → low | 10 |
| 14:05:14 | 3 | Spring strength → high | 90 |

## Decode reference

Frame structure (confirmed still accurate for the AB6):

```
0x7e | length | group | device-id | command-id | payload | checksum
```

| Fact | Value |
| :-- | :-- |
| Checksum | `(13 + sum of preceding bytes) % 256` |
| Payload ints | 2 bytes, **big-endian**, in all existing racing commands |
| Write group | `read group + 1` (e.g. base is read 40 / write 41) |
| Rejection reply | `Stick Error Cmd: [main_cmd: N]` — names the rejected group |
| Device-id seen | `49` (`0x31`) in AB6 replies |

What each discovered setting needs, to become a `serial.yml` entry:

```yaml
<name>: {read: <group>, write: <group+1>, id: [<cmd-id>], bytes: 2, type: int}
```

## Bring back

- [ ] All capture files
- [ ] The timestamped log
- [ ] Firmware version noted in pre-flight

Then add an `ab6:` section to `data/serial.yml` and update
[`AB6_STATUS.md`](./AB6_STATUS.md) with what was found.

> **Possible shortcut — try before booting Windows.** The local group sweep
> described in `AB6_STATUS.md` may cover Phases 1–2 for free, since the
> firmware names the rejected `main_cmd` in its error reply. Reads are what
> gate the UI, so a sweep alone might get the Base panel activating. The
> capture's unique value is Phase 3 onward.
