# Testing Patterns

**Analysis Date:** 2025-01-31

## Test Framework

**Runner:**
- None (no test framework configured)

**Assertion Library:**
- None (no testing present)

**Run Commands:**
```bash
# Not applicable - no tests exist
```

## Test File Organization

**Location:**
- No test directory present
- No test files found in codebase
- Test command not present in install scripts

**Naming:**
- Not applicable (no tests)

**Structure:**
```
# No test structure exists
```

## Test Structure

**Suite Organization:**
- Not applicable (no tests)

**Patterns:**
- Not applicable (no tests)

## Mocking

**Framework:** None

**Patterns:**
- Dry-run mode: `--dry-run` flag prevents actual serial writes
- Virtual device creation for testing HID compatibility
- No formal mocking framework

**What to Mock:**
- Not applicable (no tests)

**What NOT to Mock:**
- Not applicable (no tests)

## Fixtures and Factories

**Test Data:**
- `data/serial.yml` - Contains all device command definitions
- Can be used for protocol testing

**Location:**
- `data/` directory contains configuration files

## Coverage

**Requirements:** None (no enforced coverage)

**View Coverage:**
```bash
# Not applicable - no coverage tracking
```

## Test Types

**Unit Tests:**
- None (no unit test suite)

**Integration Tests:**
- None (no integration test suite)

**E2E Tests:**
- None (no end-to-end tests)

**Manual Testing:**
- Application testing done manually with actual hardware
- Dry-run mode available for testing without hardware: `./entrypoint.py --dry-run --local`

## Debugging Tools

**Print-based Debugging:**
- Extensive use of print statements for debugging
- Common pattern: `print(f"Device connected: {name}")`
- Commented-out debug prints throughout codebase

**Dry-run Mode:**
- `--dry-run` flag prevents serial writes
- Allows UI testing without hardware

**Development Mode:**
- `--local` flag uses local data directory
- `--custom` flag enables custom command entry
- `--flatpak` flag for Flatpak sandbox testing

## Testing Recommendations

**Suggested Test Framework:**
- pytest for Python testing
- pytest-asyncio for async code testing (AC dashboard)
- unittest.mock for mocking serial/HID devices

**Areas Requiring Tests:**
- Protocol encoding/decoding (`moza_command.py`)
- Event dispatcher (`subscription.py`)
- Settings persistence (`settings_handler.py`)
- Preset save/load (`preset_handler.py`)
- Bit manipulation utilities (`bitwise.py`)

**Hardware-abstraction Mocks Needed:**
- Mock SerialHandler for protocol testing
- Mock evdev devices for HID testing
- Mock shared memory for telemetry testing

**Integration Tests Needed:**
- Device discovery and connection flow
- Command send/receive cycle
- Preset save and load operations
- Event subscription and dispatching

**Manual Testing Checklist:**
- Device connection/disconnection
- All setting changes for each device type
- Preset save/load functionality
- Assetto Corsa telemetry integration
- Web dashboard accessibility from browser
- Udev rule installation

## Common Patterns

**Async Testing:**
```python
# Not applicable - no async tests
# Async code exists in ac_web_dashboard.py but no tests
```

**Error Testing:**
```python
# Not applicable - no error tests
# Error handling exists but no test coverage
```

---

*Testing analysis: 2025-01-31*
