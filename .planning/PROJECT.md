# Boxflat

## What This Is

Boxflat is a Linux native application for configuring and controlling Moza Racing sim racing equipment. It provides a GTK4-based GUI for adjusting wheelbase, steering wheel, pedals, shifters, and other device settings through serial communication. The application also includes Assetto Corsa telemetry integration for real-time dashboard updates.

## Core Value

Sim racers can fully configure their Moza Racing gear on Linux without needing Windows Pit House.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ **Device Configuration** — Base, wheel, pedals, shifters (H-pattern/sequential), handbrake, E-stop, stalks, universal hub settings
- ✓ **Preset System** — Save, load, and auto-load presets linked to game processes
- ✓ **HID Device Support** — Detection fix for game recognition, virtual device creation
- ✓ **Assetto Corsa Telemetry** — Real-time RPM data for dashboard LED control via shared memory and web dashboard
- ✓ **Multi-platform Deployment** — Flatpak (Flathub), AUR (Arch Linux), Void Linux, manual installation
- ✓ **Serial Protocol Implementation** — 30KB YAML database of Moza commands (read/write operations, device IDs, bit manipulation)

### Active

<!-- Current scope. Building toward these. -->

- [ ] **Inverted Pedals Feature** — Global toggle to swap clutch/throttle axes for inverted pedal configurations
- [ ] **Preset Integration for Inverted Pedals** — Save and load inversion state with device presets

## Current Milestone: v1.1 Inverted Pedals Feature

**Goal:** Enable sim racers with inverted pedal configurations to swap clutch and throttle axes globally

**Target features:**
- Inverted Pedals toggle in Other settings panel
- UI-layer clutch/throttle value swapping across all pedal devices
- Dynamic label updates (clutch ↔ throttle) when inversion is enabled
- Persistent setting across application restarts
- Preset save/load integration for inversion state

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- **Firmware upgrades** — EEPROM functions exist but bricking risk too high; users must use Windows Pit House
- **macOS/Windows support** — Linux-only by design (evdev, serial port handling)
- **OAuth/authentication** — Local application, no user accounts needed

## Context

**Technical Environment:**
- Python 3.11+ with GTK4/libadwaita for native Linux UI
- Event-driven architecture with custom pub/sub system (boxflat/subscription.py)
- Serial communication via pyserial, HID device handling via evdev
- Protocol-driven design: ~9,300 lines Python, 50 files, 16 device panels, 20 custom widgets

**Recent Work:**
- Assetto Corsa Dashboard Panel and Telemetry (latest commit)
- Tray icon support
- Python 3.14 compatibility fixes
- Moza R25 Ultra WheelBase support

**Known Issues:**
- Zero automated test coverage (high risk for refactoring)
- No structured logging (print statements only)
- Web dashboard listens on 0.0.0.0:8765 (security consideration)
- Serial polling every 2 seconds for all settings (performance)

**Community:**
- Active development, available on Flathub
- 6 documented supporters/contributors
- Featured on Sim Racing On Linux

## Constraints

- **Python version**: 3.11+ required — GTK4/PyGObject dependencies
- **Platform**: Linux only — evdev for HID, /dev access for serial
- **Hardware**: Moza Racing devices with proprietary serial protocol
- **Testing**: Manual hardware testing required — no device mocking framework
- **Protocol**: Reverse-engineered — incomplete understanding, may break with firmware changes

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Event-driven architecture | Loose coupling between UI, communication, and device layers | ✓ Good |
| YAML-based protocol database | Easy to add new commands without code changes | ✓ Good |
| Separate wheel_old.py | Support for old wheel settings protocol while maintaining new | — Pending |
| No test framework | Initial prototype grew into production app | ⚠️ Revisit |
| Print-based logging | Sufficient for development, insufficient for production debugging | ⚠️ Revisit |
| Flatpak first deployment | Sandbox security, easy updates across distros | ✓ Good |

---
*Last updated: 2025-01-31 after v1.1 milestone initialization*
