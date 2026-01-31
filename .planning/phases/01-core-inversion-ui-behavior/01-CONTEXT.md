# Phase 1: Core Inversion UI and Behavior - Context

**Gathered:** 2025-01-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can toggle Inverted Pedals mode and see clutch/throttle values swapped across all pedal panels. This phase adds the UI toggle, implements label/value swapping in the UI layer, and ensures the setting persists across restarts. Preset integration is Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Toggle placement and style
- Toggle appears in the "Other settings" panel at the bottom of the list
- Uses a switch toggle widget (not checkbox)
- Label: "Inverted Pedals"
- Subtitle: "Swap clutch and throttle axes"
- Toggle only visible when pedals are connected (hidden when no pedal devices)
- Default position: OFF (disabled)

### Label swapping mechanism
- Swapping applies UI-wide (anywhere clutch/throttle labels appear)
- When inverted, labels swap their text:
  - Throttle label shows: "Clutch ★"
  - Clutch label shows: "Throttle ★"
- Star (★) indicator appears only on swapped pedals (clutch and throttle)
- Brake label unchanged (no star)
- Labels update instantly when toggle changes (no animation)

### Value display behavior
- When inverted, values swap with labels (throttle label shows clutch's physical value)
- Swapped values use same format/unit as non-inverted values
- Values update instantly when toggle changes
- When no pedals connected: toggle hidden (pedal panels already hidden in this case)

### Visual feedback indicators
- Toggle state indicated by position only (no color/border change)
- Pedal panels: star (★) on labels is only visual feedback
- Star tooltip: "Swapped with [other axis]" (e.g., "Swapped with throttle")
- No other tooltips or help text
- No animation on labels/values when toggling (instant change)

### Claude's Discretion
- Exact spacing and typography of toggle in Other settings
- Exact shade/size of star indicator
- Tooltip positioning and timing

</decisions>

<specifics>
## Specific Ideas

- Star indicator should be subtle but visible (similar to other UI indicators in Boxflat)
- User wants instant updates — no lag between toggle change and UI update
- Toggle visibility should match pedal panel visibility (hide when no pedals)

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-core-inversion-ui-behavior*
*Context gathered: 2025-01-31*
