# Capture: AB6 Telemetry FFB — Dynamic Damping (Aileron) (2026-08-18)

USBPcap + Wireshark capture, provided by the user, of Cockpit's
**Telemetry FFB** page — the first capture of this page, described as
"loads of options" and "first example" of what's likely a series. Shows
the "Dynamic Damping (Aileron)" effect under the Q-feel category, filtered
to aircraft "Jet 27".

**Zero writes in this capture** — the user viewed the effect (Enable
Effect off, Effect Strength at its default 50%, Aerodynamic Damping on,
curve untouched) without changing anything, so there is nothing to
correlate the way every other capture in this project has been decoded.
`param_writes.csv` is empty and no `diag_log_device18.txt` was produced at
all (the base logged nothing new).

Kept for reference: `binary_traffic_summary.txt` shows only the AB6's
usual continuous read polling (groups 30/32 on the base, matching prior
captures) plus one new constant read on the grip (group 50, id 85,
payload `00` throughout) — plausibly a "telemetry connected" status flag,
matching the screenshot's "Telemetry Data Pending" state, but this is a
guess with only one observed value, not a confirmed finding.

See [`AB6_CAPTURE_PLAN.md`](../../AB6_CAPTURE_PLAN.md)'s Telemetry FFB
entry for page scope notes and what a follow-up capture needs (an actual
control change, logged to a specific value — same recipe as every
successful capture so far).
