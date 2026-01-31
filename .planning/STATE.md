# State: Boxflat v1.1

**Milestone:** v1.1 - Inverted Pedals Feature
**Last Updated:** 2025-01-31

## Project Reference

**Core Value:** Sim racers can fully configure their Moza Racing gear on Linux without needing Windows Pit House.

**Current Focus:** Delivering Inverted Pedals feature to enable clutch/throttle axis swapping for inverted pedal configurations.

## Current Position

**Phase:** Phase 1 - Core Inversion UI and Behavior
**Plan:** 03 of 10 (Home Panel Value and Label Swapping)
**Status:** Complete and verified
**Progress:** 30% (3 of 10 plans complete across all phases)

**Current Work:** Completed plan 01-03 with user verification passed. Home panel correctly displays swapped pedal values with star indicator on row titles.

## Performance Metrics

*Milestone-level metrics updated after phase completion.*

## Accumulated Context

### Decisions Made

**2026-01-31 - Plan 01-02 Bug Fix: ViewStackPage Title Updates**
- Root cause: set_title() was called on Adw.PreferencesPage instead of Adw.ViewStackPage wrapper
- ViewStack API: When pages added with add_titled_with_icon(), wrapper controls displayed title
- Fix: Store ViewStack reference, get wrapper with get_page(), call set_title() on wrapper
- Commits: 093d972, 5583b70

**2026-01-31 - Plan 01-02 Implementation: Pedals Panel Value Swapping**
- Initial approach: Swap map with dynamic HID re-subscription (commit 92275e2)
- Problem: Re-subscription caused duplicate subscriptions, both pages showed same data
- Final fix: Wrapper function pattern (commit 1b19ad8)
  - _throttle_hid_wrapper and _clutch_hid_wrapper route HID data based on _inverted state
  - Each page subscribes once to its original pedal's HID data
  - No subscription/unsubscription complexity
  - Matches Home panel pattern for consistency
- User verification passed: Confirmed correct page titles and value routing

**2026-01-31 - Plan 01-03 Implementation: Home Panel Value and Label Swapping**
- Value routing wrapper pattern: _throttle_input_wrapper and _clutch_input_wrapper route values based on _inverted state
- Star (*) indicator added to row titles when inverted to show swapped state
- Row titles preserve original names ("Throttle input", "Clutch input") with star when inverted
- Fix applied: Original implementation swapped titles along with values, corrected to keep original titles
- Row titles update dynamically via set_title() method when inversion toggles
- Event bridging: HomeSettings subscribes to inverted-pedals-enabled event from OtherSettings
- Multiple subscriptions to same event supported (both Home and Pedals panels receive events)
- UI-layer only: HID subscriptions unchanged, value swapping happens at display layer
- User verification passed: Confirmed correct behavior with star indicator

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
**Stopped At:** Completed plan 01-03 (Home panel value and label swapping)
**Resume File:** None (plan complete, ready to continue)

**Completed:**
- Plan 01-01: Inverted Pedals toggle in Other settings panel (commit a76a18d)
  - User verification: Approved (toggle works correctly)
- Plan 01-02: Pedals panel page title and value updates (commits c315198, e874466, 3bfa070, 021d02b, 093d972, 5583b70, 92275e2, 1b19ad8)
  - Bug fixes applied: ViewStackPage title updates (093d972), HID wrapper routing (1b19ad8)
  - User verification: Approved (page titles and value routing work correctly)
- Plan 01-03: Home panel value and label swapping (commits 1bef42c, 8f06b20, dd956f7)
  - Bug fix applied: Keep original row titles with star indicator (commit dd956f7)
  - User verification: Approved (values and labels swap correctly)

**Next Steps:**
1. Continue with remaining Phase 1 plans
2. Plans 01-04 through 01-10: Additional UI components and preset integration

**Open Questions:** None

---
*State updated: 2026-01-31*
