# State: Boxflat v1.1

**Milestone:** v1.1 - Inverted Pedals Feature
**Last Updated:** 2025-01-31

## Project Reference

**Core Value:** Sim racers can fully configure their Moza Racing gear on Linux without needing Windows Pit House.

**Current Focus:** Delivering Inverted Pedals feature to enable clutch/throttle axis swapping for inverted pedal configurations.

## Current Position

**Phase:** Phase 1 - Core Inversion UI and Behavior
**Status:** Not Started
**Progress:** 0% (0 of 2 phases complete)

**Current Work:** Awaiting phase planning

## Performance Metrics

*Milestone-level metrics updated after phase completion.*

## Accumulated Context

### Decisions Made

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

**Last Action:** Created initial roadmap and state files for v1.1 milestone

**Next Steps:**
1. User approves roadmap structure
2. Execute `/gsd:plan-phase 1` to create detailed plan for Phase 1
3. Begin implementation of core inversion UI and behavior

**Open Questions:** None

---
*State updated: 2025-01-31*
