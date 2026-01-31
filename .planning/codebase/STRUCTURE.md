# Codebase Structure

**Analysis Date:** 2025-01-31

## Directory Layout

```
boxflat/
├── boxflat/               # Main application package
│   ├── panels/           # Device-specific UI panels
│   ├── widgets/          # Custom GTK/libadwaita widgets
│   └── dashboard/        # Assetto Corsa web dashboard
├── data/                 # Application data files
├── icons/                # Application icons
├── udev/                 # Udev rules for device access
├── screens/              # Documentation screenshots
├── .github/              # GitHub CI/CD templates
└── .planning/            # Planning documentation (this directory)
```

## Directory Purposes

**boxflat/:**
- Purpose: Main Python package containing all application code
- Contains: 50 Python files (~9,300 lines of code)
- Key files:
  - `app.py` - Main application class, window management
  - `connection_manager.py` - Serial device orchestration
  - `serial_handler.py` - Low-level serial I/O
  - `hid_handler.py` - HID device monitoring and virtual device creation
  - `moza_command.py` - Protocol encoding/decoding
  - `subscription.py` - Event pub/sub system
  - `settings_handler.py` - Settings persistence
  - `preset_handler.py` - Preset save/load logic
  - `bitwise.py` - Bit manipulation utilities
  - `ac_telemetry.py` - Assetto Corsa telemetry reader (standalone)
  - `ac_web_dashboard.py` - Web server for AC dashboard
  - `process_handler.py` - Process monitoring (auto-load presets)

**boxflat/panels/:**
- Purpose: Device-specific settings UI panels
- Contains: 16 panel modules
- Key files:
  - `settings_panel.py` - Base class for all panels
  - `base.py` - Wheelbase FFB settings
  - `wheel.py` - Steering wheel settings (new version)
  - `wheel_old.py` - Steering wheel settings (legacy)
  - `pedals.py` - Pedal calibration and curves
  - `h_pattern.py` - H-pattern shifter configuration
  - `sequential.py` - Sequential shifter configuration
  - `handbrake.py` - Handbrake configuration
  - `hub.py` - Universal hub settings
  - `stalks.py` - Multi-function stalk compatibility settings
  - `dash.py` - Dashboard LED configuration
  - `ac_dashboard.py` - Assetto Corsa integration settings
  - `presets.py` - Preset management UI
  - `home.py` - Home panel with device status
  - `others.py` - Application settings (background mode, updates, etc.)
  - `generic.py` - Generic HID device configuration

**boxflat/widgets/:**
- Purpose: Reusable GTK/libadwaita widgets
- Contains: 20 widget modules (~1,500 lines)
- Key files:
  - `row.py` - Base row widget
  - `slider_row.py` - Numeric adjustment row
  - `switch_row.py` - Toggle switch row
  - `combo_row.py` - Dropdown selection row
  - `color_picker_row.py` - Color selection row (old version)
  - `new_color_picker_row.py` - Color selection row (new version)
  - `equalizer_row.py` - FFB equalizer curve row
  - `calibration_row.py` - Pedal calibration row
  - `preset_dialog.py` - Preset save/load dialog
  - `preferences_group.py` - Settings group container

**boxflat/dashboard/:**
- Purpose: Assetto Corsa web dashboard resources
- Contains: HTML themes, JavaScript, icons, configuration
- Key files:
  - `themes/default.html` - Default dashboard theme
  - `themes/porsche.html` - Porsche-style theme
  - `themes/template.html` - Theme template
  - `scripts/dashboard.js` - Dashboard frontend logic
  - `icons/*.svg` - Dashboard icons (engine, brakes, lights, etc.)
  - `shm_ui_map.json` - Shared memory offset configuration

**data/:**
- Purpose: Runtime data files
- Contains:
  - `serial.yml` - Moza protocol command database (30KB, 400+ lines)
  - `version` - Application version string (v1.36.0)
  - `style.css` - GTK UI styling
  - `udev-warning-install.txt` - Udev install prompt
  - `udev-warning-guide.txt` - Udev manual setup guide
  - `autostart.desktop` - Autostart desktop entry template

**icons/:**
- Purpose: Application icon files
- Contains: Scalable SVG icons for various sizes
- Used by: Desktop entry, window decoration, system tray

**udev/:**
- Purpose: Udev rules for device access
- Contains: `99-boxflat.rules` - Rules for Moza USB devices

## Key File Locations

**Entry Points:**
- `entrypoint.py`: Application entry point, CLI argument parsing, tray icon setup
- `boxflat/app.py`: MyApp class, panel initialization, window management

**Configuration:**
- `data/serial.yml`: Moza protocol database (all device commands, IDs, groups)
- `boxflat/settings_handler.py`: Settings persistence layer
- `~/.config/boxflat/settings.yml`: User settings (created at runtime)

**Core Logic:**
- `boxflat/connection_manager.py`: Device discovery and command orchestration
- `boxflat/moza_command.py`: Protocol encoding/decoding
- `boxflat/serial_handler.py`: Serial I/O threading and multiprocessing
- `boxflat/hid_handler.py`: HID device monitoring and compatibility shims

**Testing:**
- No test directory (no tests present)

**Documentation:**
- `README.md`: User-facing documentation
- `moza-protocol.md`: Protocol documentation for developers
- `screens/`: Screenshots for README
- `.github/ISSUE_TEMPLATE/`: Bug report and feature request templates

## Naming Conventions

**Files:**
- Modules: `lowercase_with_underscores.py` (e.g., `connection_manager.py`)
- Panels: Match device name (e.g., `base.py`, `wheel.py`, `pedals.py`)
- Widgets: Descriptive with `_row` suffix (e.g., `slider_row.py`, `switch_row.py`)

**Directories:**
- All lowercase with underscores (e.g., `boxflat/`, `boxflat/panels/`)

**Classes:**
- PascalCase: `MozaConnectionManager`, `SettingsPanel`, `SerialHandler`
- Panel classes: `{Device}Settings` (e.g., `BaseSettings`, `WheelSettings`)

**Functions/Methods:**
- snake_case: `get_setting()`, `set_payload()`, `device_discovery()`
- Private methods: Leading underscore (e.g., `_serial_loader()`, `_handle_devices()`)

**Constants:**
- UPPER_SNAKE_CASE: `MOZA_COMMAND_READ`, `MOZA_GEAR_UP`, `JOYSTICK_RANGE`
- Module-level: e.g., `HidDeviceMapping`, `SerialDeviceMapping`

**Events:**
- lowercase-with-hyphens: `device-connected`, `hid-device-connected`, `base-ffb-strength`

## Where to Add New Code

**New Device Panel:**
- Primary code: `boxflat/panels/{device_name}.py`
- Inherits from: `SettingsPanel`
- Register in: `boxflat/panels/__init__.py`
- Initialize in: `boxflat/app.py:_prepare_settings()`

**New Widget:**
- Implementation: `boxflat/widgets/{widget_name}.py`
- Export in: `boxflat/widgets/__init__.py`
- Use in panels: `from boxflat.widgets import *`

**New Command/Device:**
- Add to: `data/serial.yml` under `commands:` section
- Format: read-group, write-group, id array, bytes count, type
- Device ID: Add to `device-ids:` and `ids-to-names:` mappings

**New Telemetry Integration:**
- Reader: `boxflat/{game}_telemetry.py` (similar to `ac_telemetry.py`)
- Panel: `boxflat/panels/{game}_dashboard.py`
- Shared memory mapping: `boxflat/dashboard/shm_ui_map.json`

**Utility Functions:**
- Shared helpers: `boxflat/{utility_name}.py` (e.g., `bitwise.py`)
- Import where needed: `from boxflat import {utility_name}`

## Special Directories

**.planning/:**
- Purpose: GSD (AI agent) planning documentation
- Generated: Yes (by Claude Code)
- Committed: Yes (to repository)

**__pycache__/:**
- Purpose: Python bytecode cache
- Generated: Yes (automatically by Python)
- Committed: No (in .gitignore)

**.github/ISSUE_TEMPLATE/:**
- Purpose: GitHub issue templates
- Generated: No
- Committed: Yes

**screens/flathub/:**
- Purpose: Flathub store screenshots
- Generated: No
- Committed: Yes

## File Size Distribution

**Largest files (by line count):**
1. `boxflat/hid_handler.py` - 907 lines (HID compatibility layer, large event handlers)
2. `boxflat/panels/wheel.py` - 623 lines (complex wheel configuration)
3. `boxflat/panels/wheel_old.py` - 592 lines (legacy wheel support)
4. `boxflat/ac_web_dashboard.py` - 493 lines (web server and telemetry)
5. `boxflat/panels/base.py` - 448 lines (FFB settings)
6. `boxflat/preset_handler.py` - 430 lines (preset save/load logic)
7. `boxflat/connection_manager.py` - 399 lines (device orchestration)
8. `boxflat/app.py` - 380 lines (main application)
9. `boxflat/panels/dash.py` - 337 lines (LED dashboard)
10. `boxflat/subscription.py` - 275 lines (event system)

---

*Structure analysis: 2025-01-31*
