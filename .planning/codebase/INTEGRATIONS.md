# External Integrations

**Analysis Date:** 2025-01-31

## APIs & External Services

**Moza Racing Hardware:**
- Serial communication protocol via `/dev/ttyACM*` or `/dev/serial/by-id/`
  - Custom binary protocol documented in `moza-protocol.md`
  - Baudrate: 115200
  - Command structure: start byte (0x7e), payload length, group, device ID, command ID, value, checksum
  - Protocol definitions: `data/serial.yml` (30KB file with all device commands)
  - Device IDs: Base (0x13), Wheel (0x17), Pedals (0x19), H-pattern (0x1a), etc.
  - Implementation: `boxflat/serial_handler.py`, `boxflat/moza_command.py`

**Assetto Corsa (Sim Racing Game):**
- Shared memory telemetry integration via POSIX shared memory
  - Physics data: `/acpmf_physics` (RPM, speed, gear, fuel, etc.)
  - Graphics data: `/acpmf_graphics` (TC, ABS, lap times)
  - Static data: `/acpmf_static` (max RPM, car info)
  - Requires simshmbridge external tool
  - Implementation: `boxflat/ac_telemetry.py` (standalone reader)
  - Mapping config: `boxflat/dashboard/shm_ui_map.json`

## Data Storage

**Databases:**
- None (file-based only)

**File Storage:**
- YAML configuration files:
  - `~/.config/boxflat/settings.yml` - User settings
  - User presets directory (configurable) - Device configuration presets
- Data files: `/usr/share/boxflat/data/` (or `./data/` for local dev)
  - `serial.yml` - Moza protocol command database
  - `version` - Application version string
  - `style.css` - GTK UI styling
  - `udev-warning-*.txt` - User-facing udev installation prompts

**Caching:**
- Settings cached in memory via `boxflat/settings_handler.py`
- No persistent cache

## Authentication & Identity

**Auth Provider:**
- None (local application)

**Permissions:**
- udev rules for device access: `/etc/udev/rules.d/99-boxflat.rules`
- D-Bus/polkit integration for pkexec (udev rule installation)
- Flatpak portal permissions for device access

## Monitoring & Observability

**Error Tracking:**
- None (print statements for debugging)

**Logs:**
- Console stdout/stderr only
- Debug prints in serial handlers, HID handlers, telemetry readers
- No structured logging

## CI/CD & Deployment

**Hosting:**
- Flathub: Main distribution channel
- AUR: Arch Linux User Repository (boxflat-git)
- Void Linux: Official repository
- Manual: System-wide installation via `install.sh`

**CI Pipeline:**
- GitHub Actions workflows in `.github/`
- Issue templates: `bug_report.md`, `feature_request.md`

## Environment Configuration

**Required env vars:**
- `BOXFLAT_FLATPAK_EDITION` - Set to "true" when running in Flatpak
- `AC_DASHBOARD_THEME` - Dashboard theme selection (for web dashboard)

**Optional env vars:**
- None (CLI args used instead)

**Secrets location:**
- No secrets (local application only)

## Webhooks & Callbacks

**Incoming:**
- None (no server component except AC dashboard)

**Outgoing:**
- None (application initiates all connections)

## Internal Communication

**Event System:**
- Custom pub/sub implementation: `boxflat/subscription.py`
- EventDispatcher, ThreadedEventDispatcher, SimpleEventDispatcher classes
- Used for device connection events, telemetry updates, setting changes

**Threading:**
- Extensive use of daemon threads for:
  - Serial read/write handlers (`boxflat/serial_handler.py`)
  - HID event polling (`boxflat/hid_handler.py`)
  - Telemetry reading (`boxflat/ac_telemetry.py`)
  - Preset save/load (`boxflat/preset_handler.py`)

**Inter-process:**
- Shared memory for Assetto Corsa telemetry (POSIX shm_open)
- D-Bus for system integration (pkexec)

## Device Detection

**HID Device Detection:**
- Linux evdev API via `evdev` library
- Pattern-based device matching: `boxflat/hid_handler.py`
- Regex patterns for Moza devices (base, pedals, shifters, hub, stalks)
- Virtual device creation via `evdev.UInput` for "detection fix"
- Button and axis event handling

**Serial Device Detection:**
- Scans `/dev/serial/by-id/` for "gudsen" devices
- Automatic reconnection on device plug/unplug
- Device discovery polling thread

---

*Integration audit: 2025-01-31*
