# Architecture

**Analysis Date:** 2025-01-31

## Pattern Overview

**Overall:** Event-driven GTK4 application with serial/HID device communication layers

**Key Characteristics:**
- Publisher/subscriber event system for loose coupling between components
- Thread-per-device model for serial and HID communication
- Panel-based UI architecture (each device has its own settings panel)
- Protocol-driven command system (YAML-based device command definitions)
- Virtual device layer for input device compatibility

## Layers

**UI Layer (GTK4/libadwaita):**
- Purpose: User interface for device configuration
- Location: `boxflat/app.py`, `boxflat/panels/`, `boxflat/widgets/`
- Contains: MainWindow, MyApp, device-specific settings panels, custom widgets
- Depends on: ConnectionManager, HidHandler, SettingsHandler
- Used by: User interaction

**Communication Layer:**
- Purpose: Handle serial and HID device communication
- Location: `boxflat/connection_manager.py`, `boxflat/serial_handler.py`, `boxflat/hid_handler.py`
- Contains: MozaConnectionManager, SerialHandler, HidHandler
- Depends on: MozaCommand (protocol), evdev (HID), pyserial (serial)
- Used by: UI panels, preset system

**Protocol Layer:**
- Purpose: Encode/decode Moza serial protocol messages
- Location: `boxflat/moza_command.py`, `data/serial.yml`
- Contains: MozaCommand class, protocol definitions, bit manipulation utilities
- Depends on: boxflat.bitwise
- Used by: ConnectionManager

**Data Persistence Layer:**
- Purpose: Store and retrieve user settings and presets
- Location: `boxflat/settings_handler.py`, `boxflat/preset_handler.py`
- Contains: SettingsHandler, MozaPresetHandler
- Depends on: YAML files
- Used by: UI panels

**Event System:**
- Purpose: Enable pub/sub communication between components
- Location: `boxflat/subscription.py`
- Contains: EventDispatcher, Subscription, SubscriptionList, BlockingValue
- Depends on: Python threading primitives
- Used by: All layers

**Telemetry Layer (Assetto Corsa):**
- Purpose: Read and broadcast AC telemetry data
- Location: `boxflat/ac_telemetry.py`, `boxflat/ac_web_dashboard.py`
- Contains: ACTelemetryReader (two versions - direct and web dashboard)
- Depends on: POSIX shared memory, aiohttp (web version)
- Used by: ACDashboardSettings panel

## Data Flow

**Device Discovery:**
1. `MozaConnectionManager.device_discovery()` scans `/dev/serial/by-id/`
2. For each Moza device found, creates `SerialHandler` process
3. Serial handler spawns read/write threads
4. HID devices discovered via `evdev.list_devices()` with regex pattern matching
5. `HidHandler._configure_device()` sets up evdev input monitoring
6. Events dispatched: "device-connected", "hid-device-connected"

**Command Flow (Write):**
1. UI panel calls `MozaConnectionManager.set_setting(value, command_name)`
2. Connection manager splits command_name into device and command parts
3. Creates `MozaCommand` object, sets device ID and payload
4. Calls `MozaCommand.prepare_message()` to encode protocol bytes
5. Serial handler writes bytes to device via `pyserial`
6. Device responds (handled in read flow)

**Command Flow (Read):**
1. Polling thread calls `get_setting(command_name)` every 2 seconds
2. Creates MozaCommand with read operation
3. Serial handler sends read request
4. Serial read handler receives response bytes
5. `MozaCommand.value_from_response()` decodes response
6. Event dispatched with command name and value
7. UI panel subscriber receives update and updates UI

**Preset Save Flow:**
1. User clicks "Save Preset" in Presets panel
2. `MozaPresetHandler.save_preset()` iterates through registered settings
3. For each setting, calls `MozaConnectionManager.get_setting()` with blocking value
4. Collects all values into YAML structure
5. Writes to `~/.config/boxflat/presets/{name}.yml`

**Preset Load Flow:**
1. User selects preset from dropdown
2. `MozaPresetHandler.load_preset()` reads YAML file
3. For each setting value, calls `MozaConnectionManager.set_setting()` with exclusive access
4. Values written to device one-by-one with delays
5. UI panels update via event subscriptions

**Telemetry Flow (Assetto Corsa):**
1. ACTelemetryReader opens POSIX shared memory (`/acpmf_physics`, `/acpmf_graphics`)
2. Background thread reads physics data at ~60 FPS
3. RPM value extracted and scaled
4. Callback invoked with RPM value
5. ACDashboardSettings panel sends RPM to device (updates wheel LEDs)

**State Management:**
- Settings stored in YAML (`~/.config/boxflat/settings.yml`)
- Device state cached in memory (last known values)
- UI state (window size, maximized) persisted
- Presets stored separately with optional linked process (auto-load on game start)

## Key Abstractions

**EventDispatcher:**
- Purpose: Pub/sub messaging system
- Examples: `boxflat/subscription.py:96-198`
- Pattern: Register events → Subscribe callbacks → Dispatch events
- Thread-safe: Yes (Lock-based)

**SettingsPanel:**
- Purpose: Base class for all device configuration UI panels
- Examples: `boxflat/panels/base.py`, `boxflat/panels/wheel.py`, etc.
- Pattern: Initialize UI → Subscribe to events → Update UI on events
- Lifecycle: active(-2) → active(1) → shutdown()

**MozaCommand:**
- Purpose: Protocol encoder/decoder
- Examples: `boxflat/moza_command.py:12-224`
- Pattern: Set data from name → Set payload → Prepare message (encode) / value_from_response (decode)
- Supports: int, float, array, hex payload types

**AxisValue:**
- Purpose: Thread-safe HID axis value storage
- Examples: `boxflat/hid_handler.py:128-149`
- Pattern: Lock-protected getter/setter
- Used for: Steering, throttle, brake, clutch, paddles, etc.

## Entry Points

**entrypoint.py:**
- Location: `/entrypoint.py`
- Triggers: Application launch
- Responsibilities:
  - Parse CLI arguments (--local, --dry-run, --flatpak, --custom, --autostart)
  - Set up data path (/usr/share/boxflat/data or ./data)
  - Initialize MyApp
  - Set up system tray icon (optional, requires trayer)
  - Run GTK application

**MyApp.__init__:**
- Location: `boxflat/app.py:134-199`
- Triggers: Called by entrypoint.py
- Responsibilities:
  - Initialize MozaConnectionManager with serial.yml
  - Initialize HidHandler
  - Initialize SettingsHandler
  - Create all settings panels (Home, Base, Wheel, Pedals, etc.)
  - Set up GTK navigation structure
  - Load CSS styling

**MainWindow.on_activate:**
- Location: `boxflat/app.py:217-252`
- Triggers: GTK activate signal
- Responsibilities:
  - Create window
  - Check udev rules (prompt install if missing)
  - Restore window state from settings
  - Present window (unless autostart hidden mode)

## Error Handling

**Strategy:** Try-except with print-based logging, no formal error tracking

**Patterns:**
- Serial connection failures: Retry in `_serial_loader()` with 0.2s delay
- HID device disconnection: Cleanup and restart in `_hid_read_loop()`
- Invalid commands: Print error message, return None
- File I/O errors: Bare except blocks, print error, continue operation
- Shared memory errors (telemetry): Cleanup and reconnect

**Critique:** No structured error handling, extensive use of bare except blocks, silent failures in some paths

## Cross-Cutting Concerns

**Logging:**
- Print statements only (no logging framework)
- Debug prints can be enabled by modifying code
- No log levels or log files

**Validation:**
- Range checks in settings handlers (e.g., 0-100 for percentages)
- Device ID validation in MozaCommand
- YAML validation via safe_load

**Authentication:**
- pkexec for privilege elevation (udev rule installation)
- No user authentication (local application)

**Threading Model:**
- Daemon threads for all background operations
- Process for serial I/O (uses multiprocessing fork)
- Lock-based synchronization for shared state
- Event-based coordination (threading.Event)

---

*Architecture analysis: 2025-01-31*
