# State: Boxflat v1.1

**Milestone:** v1.1 - Inverted Pedals Feature
**Last Updated:** 2025-01-31

## Project Reference

**Core Value:** Sim racers can fully configure their Moza Racing gear on Linux without needing Windows Pit House.

**Current Focus:** Delivering Inverted Pedals feature to enable clutch/throttle axis swapping for inverted pedal configurations.

## Current Position

**Phase:** Phase 1 - Core Inversion UI and Behavior
**Plan:** 01 of 2 (Add Inverted Pedals Toggle)
**Status:** In Progress
**Progress:** 10% (1 of 10 plans complete across all phases)

**Current Work:** Completed plan 01-01 (Inverted Pedals toggle). Ready for plan 01-02 (pedal panel display updates).

## Performance Metrics

*Milestone-level metrics updated after phase completion.*

## Accumulated Context

### Decisions Made

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
**Stopped At:** Completed plan 01-01 (Add Inverted Pedals Toggle)
**Resume File:** None (plan complete, ready for next plan)

**Completed:**
- Plan 01-01: Inverted Pedals toggle in Other settings panel (commit a76a18d)
- User verification: Approved (toggle works correctly)

**Next Steps:**
1. Execute plan 01-02: Update pedal panels to consume inversion events
2. Implement label swapping (clutch ↔ throttle) in Home/Pedals settings
3. Implement value swapping in telemetry displays

**Open Questions:** None

---
*State updated: 2026-01-31*
