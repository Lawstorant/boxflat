---
phase: 01-core-inversion-ui-behavior
plan: 03
subsystem: ui
tags: [inverted-pedals, event-driven, gtk4, adwaita]

# Dependency graph
requires:
  - phase: 01-core-inversion-ui-behavior
    plan: 01
    provides: Inverted Pedals toggle with event dispatch (inverted-pedals-enabled)
provides:
  - Home panel pedal input rows that swap values and labels based on inversion state
  - Event bridging pattern from OtherSettings to HomeSettings via app.py
  - UI-layer only value routing using wrapper callbacks
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Value routing wrapper pattern for conditional display logic
    - Event-driven UI state propagation across panels
    - Dynamic title updates via set_title() method

key-files:
  created: []
  modified:
    - path: boxflat/panels/home.py
      lines: "18-20, 55-56, 64-65, 115-132, 135-151"
      changes: "Added inversion state tracking, row references, wrapper callbacks, and title update method"
    - path: boxflat/app.py
      lines: "326-327"
      changes: "Added Home panel subscription to inverted-pedals-enabled event with initialization"

key-decisions:
  - "Wrapper functions route values based on inversion state"
  - "Star indicator (*) shows swapped rows to user"
  - "Multiple subscriptions to same event supported (Home + Pedals)"

patterns-established:
  - "Value routing wrapper: Check state, route to appropriate display row"
  - "Event bridging: Other panel dispatches, consuming panels subscribe"

# Metrics
duration: 8min
completed: 2026-01-31
---

# Phase 1 Plan 03: Home Panel Value and Label Swapping Summary

**Value routing wrappers with dynamic title updates enable clutch/throttle swap at UI layer without HID/protocol changes**

## Performance

- **Duration:** 8 minutes
- **Started:** 2026-01-31T13:20:52Z
- **Completed:** 2026-01-31T13:28:52Z
- **Tasks:** 5
- **Files modified:** 2

## Accomplishments

- Home panel pedal input rows now display swapped values when Inverted Pedals is enabled
- Row titles preserve original names with star (*) indicator to show swapped state
- Value routing happens at UI layer only - HID subscriptions unchanged
- Event bridging connects OtherSettings toggle to HomeSettings display
- User verification passed: confirmed correct behavior with star indicator

## Task Commits

Each task was committed atomically:

1. **Tasks 1-4: Inversion state tracking, row references, wrappers, and title updates** - `1bef42c` (feat)
2. **Task 5: Event bridging from OtherSettings to HomeSettings** - `8f06b20` (feat)
3. **Bug fix: Keep original row titles with star indicator** - `dd956f7` (fix)
4. **Plan metadata:** `58742e8` (docs)

## Files Created/Modified

- `boxflat/panels/home.py` - Added inversion state tracking (_inverted, _throttle_row, _clutch_row), created _throttle_input_wrapper and _clutch_input_wrapper methods for value routing, added set_inverted_pedals method for title updates, updated HID subscriptions to use wrappers
- `boxflat/app.py` - Added Home panel subscription to inverted-pedals-enabled event with initial state setup

## Implementation Details

### Value Routing Pattern

When Inverted Pedals is enabled, physical pedal inputs are routed to swapped display rows:

**Normal state:**
- Physical throttle → "Throttle input" row
- Physical clutch → "Clutch input" row

**Inverted state:**
- Physical throttle → "Clutch input *" row (displays throttle value at clutch row)
- Physical clutch → "Throttle input *" row (displays clutch value at throttle row)

**Key insight:** Row titles preserve their original names - "Throttle input *" still shows the throttle row (but displaying clutch's value). The star (*) indicator visually confirms to users that the value is swapped, not the title.

### Wrapper Callback Methods

Two wrapper methods intercept HID events and route values based on `_inverted` state:

```python
def _throttle_input_wrapper(self, value: int) -> None:
    """Route throttle value to correct row based on inversion state."""
    if self._inverted:
        self._clutch_row.set_value(value)  # Inverted: throttle → clutch row
    else:
        self._throttle_row.set_value(value)  # Normal: throttle → throttle row

def _clutch_input_wrapper(self, value: int) -> None:
    """Route clutch value to correct row based on inversion state."""
    if self._inverted:
        self._throttle_row.set_value(value)  # Inverted: clutch → throttle row
    else:
        self._clutch_row.set_value(value)  # Normal: clutch → clutch row
```

### Dynamic Title Updates

The `set_inverted_pedals()` method updates row titles when inversion toggles:

```python
def set_inverted_pedals(self, inverted: int) -> None:
    self._inverted = bool(inverted)

    # Update Throttle row title - always "Throttle input" (with * when inverted)
    if self._throttle_row:
        title = "Throttle input"
        title = f"{title} *" if self._inverted else title
        self._throttle_row.set_title(title)

    # Update Clutch row title - always "Clutch input" (with * when inverted)
    if self._clutch_row:
        title = "Clutch input"
        title = f"{title} *" if self._inverted else title
        self._clutch_row.set_title(title)
```

**Important:** Row titles preserve their original names (Throttle input, Clutch input) - only the star (*) indicator is added when inverted. The star shows that the value is swapped, not the title.

### Event Bridging

The OtherSettings panel dispatches `inverted-pedals-enabled` events. Both HomeSettings and PedalsSettings subscribe:

```python
# In app.py _prepare_settings()
self._panels["Other"].subscribe("inverted-pedals-enabled", self._panels["Pedals"].set_inverted_pedals)
self._panels["Pedals"].set_inverted_pedals(self._panels["Other"].get_inverted_pedals_enabled())

self._panels["Other"].subscribe("inverted-pedals-enabled", self._panels["Home"].set_inverted_pedals)
self._panels["Home"].set_inverted_pedals(self._panels["Other"].get_inverted_pedals_enabled())
```

Multiple subscriptions to the same event are supported - both panels receive toggle changes.

## Decisions Made

**Wrapper functions for value routing**
- **Rationale:** Clean separation of concerns, allows conditional routing without changing HID subscriptions
- **Impact:** Values swap at UI layer only, no protocol/HID modifications required

**Star (*) indicator on swapped rows**
- **Rationale:** Clear visual feedback that row is displaying swapped axis
- **Impact:** Users can immediately identify which physical pedal is being displayed

**Multiple event subscriptions**
- **Rationale:** Both Home and Pedals panels need inversion state updates
- **Impact:** Event dispatcher supports multiple subscribers, pattern established for future panels

## Deviations from Plan

### Bug Fix Applied: Row Title Logic Correction

**Issue found during initial implementation:**
- Row titles were being swapped along with values (Throttle row became "Clutch input", Clutch row became "Throttle input")
- This was confusing because the row name didn't match which physical pedal's value was being displayed

**Fix applied (commit dd956f7):**
- Row titles now preserve their original names ("Throttle input", "Clutch input")
- Star (*) indicator added when inverted to show value is swapped
- "Throttle input *" = throttle row displaying clutch's value
- "Clutch input *" = clutch row displaying throttle's value

**User verification confirmed:**
- Row titles show "Throttle input *", "Brake input", "Clutch input *" when inverted
- Value routing works correctly
- Original row names preserved with star indicator

All other tasks completed as specified:
1. Added instance variables for inversion state and row references
2. Stored row references during pedal input row creation
3. Updated HID subscriptions to use wrapper callbacks
4. Created set_inverted_pedals method for title updates
5. Bridged inversion event from OtherSettings to HomeSettings in app.py

## Authentication Gates

**None.** No external authentication required.

## Next Phase Readiness

Home panel now correctly displays inverted pedal values and labels. User verification passed - implementation working as expected.

**Status:** Plan complete and verified.

**Remaining work in Phase 1:**
- Plans 01-01, 01-02, 01-03: Complete with user verification passed
- Subsequent plans: Additional UI components and preset integration

**Blockers:** None identified.

---
*Phase: 01-core-inversion-ui-behavior*
*Plan: 03*
*Completed: 2026-01-31*
