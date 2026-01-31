# State: Boxflat v1.1

**Milestone:** v1.1 - Inverted Pedals Feature
**Last Updated:** 2025-01-31

## Project Reference

**Core Value:** Sim racers can fully configure their Moza Racing gear on Linux without needing Windows Pit House.

**Current Focus:** Delivering Inverted Pedals feature to enable clutch/throttle axis swapping for inverted pedal configurations.

## Current Position

**Phase:** Phase 1 - Core Inversion UI and Behavior
**Plan:** 03 of 2 (Home Panel Value and Label Swapping)
**Status:** In Progress
**Progress:** 20% (2 of 10 plans complete across all phases)

**Current Work:** Completed plan 01-03 (Home panel swapping). Awaiting user verification at checkpoint.

## Performance Metrics

*Milestone-level metrics updated after phase completion.*

## Accumulated Context

### Decisions Made

**2026-01-31 - Plan 01-03 Implementation: Home Panel Value and Label Swapping**
- Value routing wrapper pattern: _throttle_input_wrapper and _clutch_input_wrapper route values based on _inverted state
- Star (*) indicator added to row titles when inverted to show swapped state
- Row titles update dynamically via set_title() method when inversion toggles
- Event bridging: HomeSettings subscribes to inverted-pedals-enabled event from OtherSettings
- Multiple subscriptions to same event supported (both Home and Pedals panels receive events)
- UI-layer only: HID subscriptions unchanged, value swapping happens at display layer

**2026-01-31 - Plan 01-01 Implementation: Inverted Pedals Toggle**
- Event name confirmed: "inverted-pedals-enabled" (consistent with existing pattern)
- Settings key confirmed: "inverted-pedals" (simple, descriptive)
- Default state: disabled (0) per requirement INVT-03
- Toggle visibility: controlled by pedal connection state
- Implementation location: boxflat/panels/others.py lines 86-94
- User verified: toggle works correctly, persistence confirmed

**2025-01-31 - Initial Roadmap Structure**
- Mapped 11 v1.1 requirements across 2 phases
- Phase 1 focuses on core UI and behavior (9 requirements)
- Phase 2 adds preset integration (2 requirements)
- Global inversion setting (not per-device) per user requirements
- UI-layer swap only (not protocol/HID layer) per user requirements

**Previous Decisions (from v1):**
- Event-driven architecture chosen for loose coupling
- YAML protocol database for easy command addition
- Linux-only platform commitment (evdev/serial requirements)

### Technical Notes

**Implementation Approach (from requirements):**
- Swap occurs in UI layer only, not at protocol or HID layer (PEDL-04)
- Setting applies to all pedal devices globally (PEDL-03)
- Setting must persist across restarts (INVT-02)
- Default to disabled state (INVT-03)

**Key Files to Modify:**
- Settings panel: Add Inverted Pedals toggle in Other settings
- Pedal panels: Update to display swapped values/labels based on inversion state
- Preset system: Include inversion state in save/load operations

### Blockers

- None currently identified

### Technical Debt

- Zero automated test coverage (highest priority)
- No structured logging framework
- Web dashboard security (binds to all interfaces)
- Serial polling inefficiency

### Known Issues

- Device ID cycling complexity (connection_manager.py:374-395)
- ES wheel reporting quirks (moza_command.py:61-65)
- Bare except blocks throughout codebase

## Session Continuity

**Last Session:** 2026-01-31
**Stopped At:** Completed plan 01-03 (Home Panel Value and Label Swapping)
**Resume File:** None (plan complete, awaiting user verification at checkpoint)

**Completed:**
- Plan 01-01: Inverted Pedals toggle in Other settings panel (commit a76a18d)
  - User verification: Approved (toggle works correctly)
- Plan 01-02: Pedals panel label swapping (unknown commit, executed prior)
- Plan 01-03: Home panel value and label swapping (commits 1bef42c, 8f06b20)
  - Status: Awaiting user verification

**Next Steps:**
1. User verification of plan 01-03: Test Home panel displays swapped values and labels correctly
2. Continue with remaining plans if verification passes

**Open Questions:** None

---
*State updated: 2026-01-31*
