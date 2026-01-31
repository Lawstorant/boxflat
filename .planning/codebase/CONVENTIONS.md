# Coding Conventions

**Analysis Date:** 2025-01-31

## Naming Patterns

**Files:**
- `lowercase_with_underscores.py` for modules (e.g., `connection_manager.py`, `settings_handler.py`)
- Panel files named after device (e.g., `base.py`, `wheel.py`, `pedals.py`)
- Widget files end with `_row.py` (e.g., `slider_row.py`, `switch_row.py`)

**Functions:**
- `snake_case` for all functions and methods
- Private methods prefixed with underscore: `_serial_loader()`, `_handle_devices()`
- Event handlers: `_on_` or descriptive name: `_handle_udev_dialog()`, `_read_loop()`

**Variables:**
- `snake_case` for local variables
- Private instance variables prefixed with underscore: `._settings`, `._cm`, `._hid_handler`
- Constants: `UPPER_SNAKE_CASE` (e.g., `MOZA_COMMAND_READ`, `JOYSTICK_RANGE`)

**Types/Classes:**
- `PascalCase` for class names: `MozaConnectionManager`, `SettingsPanel`, `SerialHandler`
- Panel suffix pattern: `{Device}Settings` (e.g., `BaseSettings`, `WheelSettings`)
- Widget suffix pattern: `{Type}Row` (e.g., `SliderRow`, `SwitchRow`)
- Handler suffix: `{Type}Handler` (e.g., `SettingsHandler`, `PresetHandler`)

**Events:**
- `lowercase-with-hyphens` for event names: `device-connected`, `hid-device-connected`
- Pattern: `{device}-{command}` for settings events: `base-ffb-strength`

## Code Style

**Formatting:**
- No explicit formatter configured (no .prettierrc, black, or similar)
- Indentation: 4 spaces (standard Python)
- Line length: Not enforced (some lines > 100 characters)

**Linting:**
- No linter configuration present (no .eslintrc, pylint, ruff, etc.)
- Type hints: Used sparingly (e.g., `dict[str, MozaSerialDevice]` in connection_manager.py)
- Docstrings: Not used (copyright headers only)

## Import Organization

**Order:**
1. Standard library imports
2. Third-party imports (gi, evdev, serial, yaml, etc.)
3. Local imports (boxflat.*)

**Examples:**
```python
# Standard library
import os
import sys
from threading import Thread, Event

# Third-party
from gi.repository import Gtk, Gdk, Adw
import evdev
from serial import Serial

# Local
from boxflat.connection_manager import MozaConnectionManager
from boxflat.panels import *
```

**Path Aliases:**
- No path aliases configured (all imports are full paths from boxflat package)
- All imports use absolute imports from boxflat root

**Wildcard imports:**
- Extensive use in panels: `from boxflat.widgets import *`
- Used for widgets to avoid repetitive imports
- Panel modules: `from boxflat.panels import *` (in app.py)

## Error Handling

**Patterns:**
- Try-except with bare `except:` blocks common in I/O code
- Print statements for error logging (no logging framework)
- Return `None` or default values on failure
- Retry loops with `sleep()` for transient failures

**Examples:**
```python
# Serial connection retry
while self._serial is None and not self._shutdown.is_set():
    try:
        self._serial = Serial(...)
    except:
        self._serial = None
        sleep(0.2)

# HID read loop
try:
    for event in device.read_loop():
        # process events
except Exception as e:
    device.close()
    device = None
```

**Silent Failures:**
- Many bare except blocks that silently continue
- Common in cleanup code: `try: ... except: pass`

## Logging

**Framework:** Print statements only (console stdout/stderr)

**Patterns:**
- Status prints: `print(f"HID device found: {hid.name}")`
- Debug prints: Commented out in many places
- Error prints: `print(f"Command not found: {command_name}")`
- No log levels, no structured logging

**When to log:**
- Device connection/disconnection
- Major errors/failures
- Telemetry reader status (AC dashboard)
- Debug prints available for protocol debugging (commented out)

## Comments

**When to Comment:**
- Section headers in code (e.g., "Even less important settings")
- TODO/FIXME comments for future work
- Copyright headers in all files
- Protocol-specific notes (e.g., byte swapping)

**JSDoc/TSDoc:**
- Not used (no docstrings on functions/classes)
- Type hints used sparingly

**Comment Style:**
- `#` for single-line comments
- Multi-line comments as consecutive `#` lines
- Inline comments for protocol logic

## Function Design

**Size:**
- No strict size limits
- Functions range from 3-200+ lines
- Many large functions (e.g., `_hid_read_loop()` at 40 lines, `_blip_handler_worker()` at 50+ lines)

**Parameters:**
- Positional parameters for required values
- Keyword parameters for optional values
- `*args` used for event callback arguments
- Default values common in UI callbacks: `def active(self, value: int)`

**Return Values:**
- Explicit `return` for all functions
- `None` implicit for functions without return value
- Tuple returns common: `return command_name, device_name`
- Return `None` or `-1` for error/failure cases

**Example patterns:**
```python
# Simple setter
def set_setting(self, value, command_name: str):
    self._handle_setting(value, name, device, MOZA_COMMAND_WRITE)

# Getter with blocking
def get_setting(self, command_name: str, exclusive=False, custom_value=1):
    value = BlockingValue()
    sub = self.subscribe_once(command_name, value.set_value)
    self._get_setting(command_name, exclusive, custom_value)
    return value.get_value_no_clear()
```

## Module Design

**Exports:**
- `__all__` not used
- Explicit exports in `__init__.py` files
- Pattern: `from .module import ClassName`

**Barrel Files:**
- `boxflat/panels/__init__.py` exports all panel classes
- `boxflat/widgets/__init__.py` exports all widget classes
- Allows `from boxflat.panels import *` pattern

**Circular Imports:**
- Avoided by using lazy imports or reorganization
- Connection manager imported by most panels
- Event dispatcher pattern reduces coupling

## Threading Patterns

**Thread Creation:**
```python
# Daemon threads for background tasks
Thread(target=self._thread_spawner, daemon=True).start()
Thread(target=self._axis_data_polling, daemon=True).start()

# Threaded event callbacks
def _dispatch(self, event_name: str, *values):
    Thread(target=super()._dispatch, args=[event_name, *values], daemon=True).start()
```

**Synchronization:**
- `threading.Lock` for protecting shared state
- `threading.Event` for coordination and shutdown signals
- `multiprocessing.Queue` for inter-process communication
- `with lock:` context manager pattern

**Shutdown Pattern:**
```python
self._shutdown.set()  # Signal thread to stop
# Thread checks: while not self._shutdown.is_set()
```

## GTK/libadwaita Patterns

**Widget Creation:**
- Programmatic widget construction (no UI builder files)
- Set properties via methods: `button.set_halign(Gtk.Align.FILL)`
- Connect signals: `button.connect("clicked", callback)`

**UI Updates:**
- Use `GLib.idle_add()` for UI updates from background threads:
  ```python
  GLib.idle_add(self._banner.set_revealed, value)
  GLib.idle_add(self._button.set_visible, value)
  ```

**Panel Structure:**
- Inherit from `SettingsPanel` or `Adw.PreferencesPage`
- Use `add_preferences_group()` to create settings sections
- Use custom row widgets for settings controls
- Call `active(1)` when device connected, `active(-2)` when disconnected

## Protocol Implementation Patterns

**Command Encoding:**
```python
command = MozaCommand()
command.set_data_from_name(name, commands_data, device_name)
command.device_id = device_id
command.set_payload(value)
message = command.prepare_message(start_value, rw, magic_value)
```

**Response Decoding:**
```python
command, value = MozaCommand.value_from_response(
    data, device_name, commands_data, device_ids
)
```

**YAML Structure:**
- Device IDs mapped in `device-ids:` section
- Commands defined per device with: read group, write group, id array, bytes, type
- Types: `int`, `float`, `array`, `hex`

---

*Convention analysis: 2025-01-31*
