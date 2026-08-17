# AB6 Protocol Capture — Action List

Field checklist for capturing Moza Cockpit ↔ AB6 traffic on Windows, so the
AB6 command set can be added to `data/serial.yml`.

Companion to [`AB6_STATUS.md`](./AB6_STATUS.md).

> **Phase 1 is done.** A user-provided USBPcap capture of Cockpit's launch
> (passive, no control touched) is decoded in
> [`captures/2026-08-17-cockpit-launch/`](./captures/2026-08-17-cockpit-launch/)
> — see "Windows capture analysis" in `AB6_STATUS.md` for the full writeup.
> It found 129 settings values across 4 parameter tables via a plain-ASCII
> diagnostic log, and caught a real version-display bug by cross-checking
> against Cockpit's own UI. **Read that section before repeating any of
> Phases 0–2 below** — most of what they'd find is already known. What's
> still missing is *attribution*: matching a `(table, param)` address to
> the Cockpit control that changes it, which is what Phase 3 is for. Try
> the "cheap path" noted there first — it may make the rest of this
> document (and Wireshark entirely) unnecessary.

## Already solved — do not re-derive

The local sweep succeeded, so most of Phases 0–2 are done. Confirmed on
hardware with `tools/ab6_sweep.py`, `tools/ab6_axes.py`, and the Windows
capture above:

| Fact | Value |
| :-- | :-- |
| Base device ID | `18` — replies `0x21`, "Base heart beat" |
| Grip device ID | `19` — replies `0x31`, "Stick heart beat" |
| Base firmware | group 4 → `1.1.4.6` (Cockpit's own display — see version-format note below) |
| Grip firmware | group 4 → `1.1.1.11` |
| Protocol version | group 5 → `1.2.3.3`, same on both |
| Serial number | group 6 — matches the USB serial exactly |
| **Settings — ASCII log** | **129 values across 4 tables (2, 7, 8 on the base; 13 on the grip), read but not attributed to Cockpit labels — see `captures/2026-08-17-cockpit-launch/param_writes.csv`** |
| **Settings — binary** | **Groups 30/31 (base) and 51/67 (grip) read in a burst at connect; ids located, not attributed** |
| Diagnostic log | group 14 / id 5, ASCII, streams continuously — **its group byte is NOT bit7-toggled**, unlike every other reply (see `AB6_STATUS.md`) |

> **Version-format trap.** The wire byte order is
> major.minor.**build**.**patch**, not major.minor.patch.build — a plain
> big-endian read of the 4-byte payload gives the *wrong* display string
> (e.g. `1.1.6.4` instead of the correct `1.1.4.6`). This was found by
> comparing the raw payload against what Cockpit itself displays. Fixed in
> `format_version()` in `boxflat/panels/ab6.py`. If you decode a version
> field by hand while doing this capture, swap the last two bytes before
> trusting it, and cross-check against Cockpit's UI wherever possible —
> that UI is ground truth, this repo's inferences are not.

Both devices are detected, both panels work, and every axis is mapped.

**What this capture is still for: attributing table/param addresses (or
binary group/id addresses) to named Cockpit settings.** That needs writes
to correlate, which a read-only capture cannot do on its own. Phase 3 is
the point of the exercise; the earlier phases are now confirmation rather
than discovery — skip straight there unless something below turns out to
be wrong.

> **The ID trap.** In the *racing* map ID 18 is `main` and ID 19 is `base`,
> so reading the AB6 through that map attributes the grip's firmware to the
> base. The AB6 has its own map. This already produced one wrong result.

> **Versions are four-part.** Group 4 ignores the command id, so the whole
> 4-byte payload is version data. Reading 3 bytes silently drops a field.

An interactive version of this checklist, which stamps the time as you tick
each step:
<https://claude.ai/code/artifact/9ad549c7-1775-42fd-b75b-0270baf83f9f>

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

> **Try this first, before Wireshark.** The 2026-08-17 capture found that
> the firmware logs every setting it loads at boot as plain ASCII —
> `Table N, Param M Written: <raw> <float>` — on the existing diagnostic
> channel (group 14 / id 5). If live writes get logged the same way (not
> yet confirmed), you can do this entire phase by just watching the serial
> port's text output while changing one Cockpit control at a time — no
> USBPcap, no Wireshark, no frame decoding. Check this before setting up a
> full capture: plug the AB6 into Linux, run something that prints the
> group-14/id-5 text stream (or reuse `tools/ab6_pcap_decode.py`'s
> reassembly logic against a live serial read instead of a pcap), then
> switch to Windows and change **one** setting. If a new `Table N, Param M
> Written` line appears, this phase is just "repeat that per setting" — see
> `AB6_STATUS.md` → "Windows capture analysis" → "Revised Phase 3
> recommendation". If nothing appears, live writes aren't logged this way,
> and the checklist below (full USB capture) is necessary after all.

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
| Device-id seen | `49` (`0x31`) in AB6 replies (nibble-swapped `0x21`/`0x31` → 18/19 for base/grip) |

> **The diagnostic log is the one exception to bit7-toggling.** Every other
> reply sets bit 7 on the group byte (`toggle_bit(byte, 7)` recovers the
> real group). The async diagnostic-log pushes (group 14 / id 5) do **not**
> — their group byte is the plain, untoggled value `14`. Code that assumes
> uniform toggling (including earlier revisions of this repo's own tooling)
> misreads it as group 142. See `AB6_STATUS.md` → "Windows capture
> analysis" → "Framing correction".

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

To decode a new capture, run:

```bash
python3 tools/ab6_pcap_decode.py capture.pcapng --out-dir captures/<name>
```

It extracts the AB6's CDC traffic by USB VID:PID automatically, reassembles
the diagnostic log (handling the async-push framing correctly), pulls out
any `Table N, Param M Written` lines, and summarizes the binary group/id
traffic seen. See `captures/2026-08-17-cockpit-launch/` for the shape of
its output.

> **The "shortcut" already paid off once.** A passive Phase-1-only capture
> (Cockpit launch, no control touched) found 129 settings values and caught
> a real bug — see `AB6_STATUS.md` → "Windows capture analysis". Reads
> alone got much further than expected; **try the Phase 3 "cheap path"
> above before planning a full write-by-write capture.**
