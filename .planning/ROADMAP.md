# Roadmap: Boxflat v1.1 - Inverted Pedals Feature

**Milestone:** v1.1
**Created:** 2025-01-31
**Total Phases:** 2

## Overview

This roadmap delivers the Inverted Pedals feature for Boxflat, allowing sim racers to swap clutch and throttle axes for inverted pedal configurations. The feature includes a global toggle in the Other settings panel, UI-layer value swapping, preset integration, and dynamic display updates across all pedal devices.

## Phases

### Phase 1: Core Inversion UI and Behavior

**Goal:** Users can toggle Inverted Pedals mode and see clutch/throttle values swapped across all pedal panels

**Dependencies:** None (this is the first GSD-tracked milestone)

**Plans:** 3 plans

**Requirements:**
- INVT-01: User can toggle "Inverted Pedals" in Other settings panel
- INVT-02: Inverted Pedals setting persists across application restarts
- INVT-03: Inverted Pedals setting defaults to disabled
- PEDL-01: When Inverted Pedals is enabled, clutch and throttle values are swapped in the UI
- PEDL-02: When Inverted Pedals is enabled, clutch and throttle axis labels are swapped in UI
- PEDL-03: Inverted Pedals setting applies to all pedal devices globally
- PEDL-04: Pedal swap occurs in UI layer only (not at protocol or HID layer)
- DISP-01: Pedal panels display correct axis values based on inversion state
- DISP-02: Pedal axis labels update dynamically when inversion is toggled
- DISP-03: Other settings panel shows current inversion state with toggle switch

**Success Criteria:**
1. User can open Other settings panel and see an "Inverted Pedals" toggle switch
2. User can enable Inverted Pedals and see clutch/throttle values swap in all pedal panels
3. User can disable Inverted Pedals and see clutch/throttle values return to normal
4. User can restart application and see Inverted Pedals setting preserved
5. User can see clutch and throttle axis labels update dynamically when toggling inversion

**Plans:**
- [ ] 01-01-PLAN.md — Add Inverted Pedals toggle to Other settings panel
- [ ] 01-02-PLAN.md — Update Pedals panel page titles on inversion toggle
- [ ] 01-03-PLAN.md — Implement value/label swapping in Home panel

---

### Phase 2: Preset Integration

**Goal:** Users can save and load Inverted Pedals state as part of device presets

**Dependencies:** Phase 1 (core inversion feature must exist to be saved/loaded)

**Requirements:**
- PRST-01: Presets save and load the Inverted Pedals setting state
- PRST-02: When loading a preset, current inversion state updates to match preset

**Success Criteria:**
1. User can create a preset while Inverted Pedals is enabled and see the setting saved
2. User can load a preset saved with Inverted Pedals enabled and see inversion state applied
3. User can load a preset saved with Inverted Pedals disabled and see inversion state cleared
4. User can toggle between presets with different inversion states and see the UI update accordingly

---

## Progress

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 1: Core Inversion UI and Behavior | Not Started | 0% |
| Phase 2: Preset Integration | Not Started | 0% |

**Overall:** 0% (0 of 2 phases complete)

---

*Roadmap created: 2025-01-31*
