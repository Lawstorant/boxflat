# Technology Stack

**Analysis Date:** 2025-01-31

## Languages

**Primary:**
- Python 3.11+ - Core application logic, GTK4 UI, serial communication

**Secondary:**
- JavaScript - Assetto Corsa web dashboard frontend (`boxflat/dashboard/scripts/dashboard.js`)
- HTML/CSS - Dashboard themes (`boxflat/dashboard/themes/`)
- JSON - Configuration and shared memory mapping

## Runtime

**Environment:**
- Python 3.11+ (required, not tested with older versions)
- Linux (targeted platform)

**Package Manager:**
- pip (via `requirements.txt`)
- Lockfile: Not present (versions specified in requirements.txt)
- Flatpak support for containerized deployment

## Frameworks

**Core UI:**
- GTK4 4.0 - Native Linux GUI framework
- libadwaita 1.6+ - GNOME UI components (Adw.PreferencesPage, Adw.ToolbarView, etc.)
- PyGObject 3.50.0 - Python bindings for GTK
- pycairo 1.27.0 - Cairo graphics bindings (required 1.18+)

**Testing:**
- Not detected (no test framework present)

**Build/Dev:**
- setuptools/pip (standard Python packaging)

## Key Dependencies

**Hardware Communication:**
- pyserial 3.5 - Serial port communication with Moza devices
- evdev 1.7.1 - Linux input device handling (HID)
- dbus-python 1.4.0 - D-Bus integration for system services

**Async/Web:**
- aiohttp - Web server for Assetto Corsa dashboard (WebSocket support)

**System:**
- psutil 6.1.0 - System process monitoring
- PyYAML 6.0.2 - Configuration file parsing (`data/serial.yml`, settings)
- trayer 0.1.1 - System tray icon support (optional)

## Configuration

**Environment:**
- Config files: YAML (`data/serial.yml`, `~/.config/boxflat/settings.yml`)
- Key configs required:
  - `serial.yml` - Moza protocol command definitions (device IDs, read/write groups, command structure)
  - `settings.yml` - User settings persistence

**Build:**
- No build config (Python interpreted)
- CSS styling: `data/style.css` for GTK UI theming
- Shared memory mapping: `boxflat/dashboard/shm_ui_map.json` for Assetto Corsa telemetry

## Platform Requirements

**Development:**
- Python 3.11+
- GTK4 development libraries
- libadwaita 1.6+
- gobject-introspection
- Linux with /dev/input/event* access (for HID)
- Serial port access (/dev/ttyACM* or /dev/serial/by-id/)

**Production:**
- Native Linux: System installation via `install.sh`
- Flathub: Flatpak sandbox with appropriate device permissions
- AUR: Arch Linux package
- Void Linux: XBPS package
- Udev rules for device access (automatically installed via pkexec)

**Special Requirements:**
- pkexec (optional) - For privilege elevation when installing udev rules
- simshmbridge (external) - Required for Assetto Corsa telemetry shared memory bridge
- libc.so.6 - Direct shm_open calls for shared memory access

---

*Stack analysis: 2025-01-31*
