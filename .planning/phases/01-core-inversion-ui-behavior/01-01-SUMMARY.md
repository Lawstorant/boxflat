---
phase: 01-core-inversion-ui-behavior
plan: 01
title: Add Inverted Pedals Toggle to Other Settings
one-liner: "BoxflatSwitchRow UI toggle with event dispatch and settings persistence"
status: complete
completed: 2026-01-31

tech-stack:
  added: []
  patterns:
    - Event-driven UI toggle pattern
    - Settings persistence via SettingsHandler
    - Conditional visibility based on device connection

key-files:
  created: []
  modified:
    - path: boxflat/panels/others.py
      lines: "86-94"
      changes: "Added Inverted Pedals toggle with event registration and persistence"

decisions:
  - text: "Event name: inverted-pedals-enabled"
    rationale: "Consistent with existing event naming (brake-calibration-enabled, moza-detection-fix-enabled)"
    impact: "Other panels will subscribe to this event to update their displays"
  - text: "Settings key: inverted-pedals"
    rationale: "Simple, descriptive key following existing pattern"
    impact: "Persists to ~/.config/boxflat/settings.yml"
  - text: "Default state: disabled (0)"
    rationale: "User requirement INVT-03: defaults to disabled for safety"
    impact: "First launch shows OFF position"

metrics:
  duration: "Plan executed by previous agent; checkpoint approved by user"
  tasks_completed: 1
  deviations: 0
---

# Phase 1 Plan 01: Add Inverted Pedals Toggle Summary

**Status:** COMPLETE
**Completed:** 2026-01-31
**Commit:** a76a18d

## Overview

Implemented the foundational Inverted Pedals toggle in the Other settings panel. This toggle serves as the control point for the entire Inverted Pedals feature - when enabled, it dispatches events that other panels subscribe to for updating their displays (swapping clutch/throttle labels and values).

## Implementation Details

### Location
**File:** `boxflat/panels/others.py`
**Lines:** 86-94
**Position:** After "Enable Moza detection fixes" toggle, before "Start hidden" toggle

### Code Implementation

```python
inversion_row = BoxflatSwitchRow("Inverted Pedals", "Swap clutch and throttle axes")
self._inverted_pedals_row = inversion_row
self._add_row(inversion_row)

self._register_event("inverted-pedals-enabled")
inversion_row.subscribe(self._settings.write_setting, "inverted-pedals")
inversion_row.subscribe(lambda v: self._dispatch("inverted-pedals-enabled", v))
inversion_row.set_value(self._settings.read_setting("inverted-pedals") or 0)
self._cm.subscribe_connected("pedals-throttle-dir", inversion_row.set_active, 1)
```

### Key Features

1. **Toggle Display**
   - Title: "Inverted Pedals"
   - Subtitle: "Swap clutch and throttle axes"
   - UI Widget: `BoxflatSwitchRow`

2. **Event System**
   - Event name: `inverted-pedals-enabled`
   - Registered via: `self._register_event()`
   - Dispatches on: Every toggle state change
   - Payload: Current toggle value (0 or 1)
   - Purpose: Other panels subscribe to this event to update their displays

3. **Settings Persistence**
   - Settings key: `inverted-pedals`
   - Handler: `SettingsHandler.write_setting()`
   - Storage: `~/.config/boxflat/settings.yml`
   - Values: 0 (disabled) or 1 (enabled)

4. **Default State**
   - Defaults to: OFF (disabled)
   - Implementation: `or 0` pattern returns 0 if setting doesn't exist
   - Rationale: User requirement INVT-03 - disabled by default for safety

5. **Visibility Control**
   - Hidden when: No pedals connected
   - Visible when: Pedals with throttle axis connect
   - Mechanism: `subscribe_connected("pedals-throttle-dir", set_active, 1)`
   - Rationale: Only relevant when pedal hardware is present

## Integration Points

### Event Subscription (for future panels)

Other panels can subscribe to the inversion toggle:

```python
# In pedal panels (HomeSettings, PedalsSettings)
self._other_panel.subscribe("inverted-pedals-enabled", self._handle_inversion_change)
```

### Settings Access

Read current inversion state:

```python
inversion_enabled = settings.read_setting("inverted-pedals") or 0
```

## User Verification Completed

User tested the following:
- ✓ Toggle appears in Other settings panel
- ✓ Toggle is visible when pedals are connected
- ✓ Toggle is hidden when no pedals are connected
- ✓ Clicking toggle writes to settings.yml (inverted-pedals: 0 or 1)
- ✓ Toggle state persists across application restarts
- ✓ Event dispatches without errors

## Deviations from Plan

**None.** Plan executed exactly as written.

## Authentication Gates

**None.** No external authentication required.

## Next Steps

This plan (01-01) is complete. The toggle is ready for consumption by pedal panels.

**Plan 01-02** will implement the display updates in Home and Pedals settings panels to:
- Subscribe to `inverted-pedals-enabled` event
- Swap clutch/throttle labels when inversion is enabled
- Swap clutch/throttle values when inversion is enabled
- Update telemetry displays accordingly

## Files Modified

- `boxflat/panels/others.py` (10 lines added)

## Commit

```
a76a18d feat(01-01): add Inverted Pedals toggle to Other settings panel

- Created BoxflatSwitchRow with title 'Inverted Pedals' and subtitle 'Swap clutch and throttle axes'
- Registered event 'inverted-pedals-enabled' for other panels to subscribe
- Subscribed toggle to settings persistence under 'inverted-pedals' key
- Added visibility control: toggle shows only when pedals are connected
- Default state: OFF (disabled) via 'or 0' pattern
- Event dispatches current value on toggle state change
- UI-layer only: no protocol/HID modifications
```
