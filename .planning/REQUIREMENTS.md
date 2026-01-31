# Requirements: Boxflat

**Defined:** 2025-01-31
**Core Value:** Sim racers can fully configure their Moza Racing gear on Linux without needing Windows Pit House.

## v1.1 Requirements - Inverted Pedals Feature

### Settings

- [ ] **INVT-01**: User can toggle "Inverted Pedals" in Other settings panel
- [ ] **INVT-02**: Inverted Pedals setting persists across application restarts
- [ ] **INVT-03**: Inverted Pedals setting defaults to disabled

### Pedal Behavior

- [ ] **PEDL-01**: When Inverted Pedals is enabled, clutch and throttle values are swapped in the UI
- [ ] **PEDL-02**: When Inverted Pedals is enabled, clutch and throttle axis labels are swapped in UI
- [ ] **PEDL-03**: Inverted Pedals setting applies to all pedal devices globally
- [ ] **PEDL-04**: Pedal swap occurs in UI layer only (not at protocol or HID layer)

### Presets

- [ ] **PRST-01**: Presets save and load the Inverted Pedals setting state
- [ ] **PRST-02**: When loading a preset, current inversion state updates to match preset

### UI Display

- [ ] **DISP-01**: Pedal panels display correct axis values based on inversion state
- [ ] **DISP-02**: Pedal axis labels update dynamically when inversion is toggled
- [ ] **DISP-03**: Other settings panel shows current inversion state with toggle switch

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Additional Inversions

- **INVT-01**: Support for brake inversion (three-way swap)
- **INVT-02**: Per-device inversion settings

### Other Features

- **TELM-01**: REST API/WebSocket telemetry ingestion for other sims
- **BRND-01**: Cammus device support
- **BRND-02**: PXN device support
- **BRND-03**: Simagic device support
- **HID-01**: H-Pattern and Sequential settings for arbitrary HID devices

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Protocol-level pedal swapping | User requested UI-layer only, simpler implementation |
| Per-device inversion | User requested global setting for all pedals |
| Brake pedal inversion | User specified clutch↔throttle swap only |
| Auto-detection of inversion needed | Manual toggle gives user explicit control |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INVT-01 | Phase 1 | Pending |
| INVT-02 | Phase 1 | Pending |
| INVT-03 | Phase 1 | Pending |
| PEDL-01 | Phase 1 | Pending |
| PEDL-02 | Phase 1 | Pending |
| PEDL-03 | Phase 1 | Pending |
| PEDL-04 | Phase 1 | Pending |
| PRST-01 | Phase 2 | Pending |
| PRST-02 | Phase 2 | Pending |
| DISP-01 | Phase 1 | Pending |
| DISP-02 | Phase 1 | Pending |
| DISP-03 | Phase 1 | Pending |

**Coverage:**
- v1.1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

---
*Requirements defined: 2025-01-31*
*Last updated: 2025-01-31 after initial definition*
