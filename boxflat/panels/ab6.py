# Copyright (c) 2026, Boxflat contributors

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import MozaAxis
from boxflat.widgets import *


def format_version(value: int) -> str:
    """Render a packed version int as a four-part version.

    Group 4 ignores the command id, so the whole payload is version data:
    the base answers 0x01010604 and the grip 0x01010b01. Cockpit itself
    displays those as "1.1.4.6" and "1.1.1.11" (confirmed against real
    hardware) - the wire order is major.minor.BUILD.patch, so the last two
    bytes need swapping to match what Cockpit shows. See AB6_STATUS.md.
    """
    if value is None or value < 0:
        return "Unknown"

    major, minor, build, patch = value.to_bytes(4, "big")
    return f"{major}.{minor}.{patch}.{build}"


class AB6Settings(SettingsPanel):
    """Flight base panel.

    Deliberately limited to what the hardware has actually been observed to
    answer. The AB6 does not implement the racing command set, so this
    panel exposes only the settings confirmed against real hardware so far
    (see AB6_STATUS.md) rather than the full Basic Settings page Cockpit
    shows - Spring/Damper/Inertia/Friction curve shaping, Axis Travel,
    Panel Settings and Expert Settings remain unmapped.
    """

    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler):
        super().__init__("AB6 Base", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("ab6-version", self.active)


    def prepare_ui(self):
        self.add_preferences_group("Device")

        self._add_row(BoxflatLabelRow("Firmware version"))
        self._current_row.set_label("Unknown")
        self._cm.subscribe("ab6-version", self._set_version, self._current_row)

        self._add_row(BoxflatLabelRow("Protocol version"))
        self._current_row.set_label("Unknown")
        self._cm.subscribe("ab6-protocol-version", self._set_version, self._current_row)

        # Axis assignments confirmed with tools/ab6_axes.py. The names come
        # from boxflat's shared racing map, so they are relabelled here for
        # what the control actually is on a flight stick.
        self.add_preferences_group("Stick axes")

        self._add_row(BoxflatLevelRow("Roll", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.STEERING.name, self._current_row.set_value)

        self._add_row(BoxflatLevelRow("Pitch", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.COMBINED_PADDLES.name, self._current_row.set_value)

        # The manual puts the two analog sliders on the base itself.
        self.add_preferences_group("Sliders")

        self._add_row(BoxflatLevelRow("Slider 1", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.CLUTCH.name, self._current_row.set_value)

        self._add_row(BoxflatLevelRow("Slider 2", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.HANDBRAKE.name, self._current_row.set_value)

        # Confirmed against real hardware (see data/serial.yml) by cycling
        # each control in Cockpit and matching the write - and for FFB Mode
        # and Torque, the read-back too - against the firmware's own
        # diagnostic log, one-for-one across every transition.
        self.add_preferences_group("Settings")

        self._add_row(BoxflatToggleButtonRow("FFB Mode"))
        self._current_row.add_buttons("Telemetry", "DirectInput", "Integrated")
        self._current_row.subscribe(self._cm.set_setting, "ab6-ffb-mode")
        self._cm.subscribe("ab6-ffb-mode", self._current_row.set_value)

        # Only Conservative/Aggressive were exercised; a third mode at
        # value 0 is plausible but unconfirmed - see data/serial.yml.
        self._add_row(BoxflatToggleButtonRow("Temperature Control Mode"))
        self._current_row.add_buttons("Conservative", "Aggressive")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting, "ab6-temp-control-mode")
        self._cm.subscribe("ab6-temp-control-mode", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Maximum Torque Output", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-torque")
        self._cm.subscribe("ab6-torque", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Overall Force Feedback Intensity", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-ffb-intensity")
        self._cm.subscribe("ab6-ffb-intensity", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Spring", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-spring")
        self._cm.subscribe("ab6-spring", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Damper", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-damper")
        self._cm.subscribe("ab6-damper", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Inertia", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-inertia")
        self._cm.subscribe("ab6-inertia", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Friction", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-friction")
        self._cm.subscribe("ab6-friction", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Game Force Feedback Gain", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-game-ffb-gain")
        self._cm.subscribe("ab6-game-ffb-gain", self._current_row.set_value)

        # Confirmed against real hardware from the X/Y stick calibration
        # captures - see data/serial.yml. Each is a single write-only
        # trigger; the firmware ends the hand-calibration on its own once
        # the stick is released, no separate stop needed. A "Z" axis
        # attempt on the AB6 itself was logged as invalid by the firmware -
        # the AB6 has no such axis; Yaw calibration is under the MHG panel.
        self.add_preferences_group("Stick Calibration")

        self._add_row(BoxflatButtonRow("Roll Axis Calibration", "Start Calibration",
            subtitle="Move the stick through its full range when prompted"))
        self._current_row.subscribe(self._start_stick_x_calibration)

        self._add_row(BoxflatButtonRow("Pitch Axis Calibration", "Start Calibration",
            subtitle="Move the stick through its full range when prompted"))
        self._current_row.subscribe(self._start_stick_y_calibration)

        # Confirmed against real hardware from the Slider Axis Calibration
        # capture - see data/serial.yml. Cockpit's single "Start
        # Calibration" button actually fires one trigger per slider; this
        # mirrors that with a single button too, rather than exposing two
        # separate ones for a single physical wizard flow.
        self.add_preferences_group("Panel Settings")

        self._add_row(BoxflatButtonRow("Slider Axis Calibration", "Start Calibration",
            subtitle="Move both sliders through their full range when prompted"))
        self._current_row.subscribe(self._start_slider_calibration)

        # Confirmed against real hardware from the Panel Settings page
        # capture - see data/serial.yml: ab6-light-color, ab6-backlit-brightness.
        self.add_preferences_group("Panel Lighting")

        self._add_row(BoxflatSliderRow("Backlit Brightness", range_end=15))
        self._current_row.subscribe(self._cm.set_setting, "ab6-backlit-brightness")
        self._cm.subscribe("ab6-backlit-brightness", self._current_row.set_value)

        self._light_color_row = BoxflatNewColorPickerRow("Light Color", pickers=1)
        self._add_row(self._light_color_row)
        self._current_row.subscribe("color0", self._set_light_color)
        self._cm.subscribe("ab6-light-color", self._set_light_color_row)

        # Confirmed against real hardware from the Advanced Settings ->
        # Centering page capture - see data/serial.yml. Other controls on
        # this page (Deadzone, the Link checkboxes, Adaptive Centering
        # Compensation, Hands-off Detection) weren't confidently attributed
        # and are left out rather than guessed.
        self.add_preferences_group("Centering")

        self._add_row(BoxflatSliderRow("Effect Strength", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-centering-effect-strength")
        self._cm.subscribe("ab6-centering-effect-strength", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Compensation Effective Range", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-centering-compensation-range")
        self._cm.subscribe("ab6-centering-compensation-range", self._current_row.set_value)

        # Confirmed against real hardware from the Advanced Settings ->
        # Trim/Autopilot Following pages capture - see data/serial.yml.
        # Everything else on those pages (the Trim/Autopilot Following
        # toggles themselves, Axis follow mode, the Follow preset buttons,
        # follow rate/scale sliders, Sidestick AP Lock) wasn't touched in
        # the capture or wasn't confidently attributed.
        #
        # Reported by a user: Moza documents Autopilot Following as an
        # AB9-only feature. The AB6 still accepts these writes over this
        # same protocol, so the controls below work in the sense that the
        # device acknowledges them - they may just have no physical effect
        # on AB6 hardware, which has no motorized trim to drive.
        self.add_preferences_group("Trim & Autopilot Following")

        self._add_row(BoxflatLabelRow(
            "AB9 feature",
            "Reported to only have a physical effect on the AB9. The AB6 "
            "accepts these settings but may not act on them."))

        self._add_row(BoxflatSliderRow("Physical Stick Follow Ratio X", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-follow-ratio-x")
        self._cm.subscribe("ab6-follow-ratio-x", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Physical Stick Follow Ratio Y", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-follow-ratio-y")
        self._cm.subscribe("ab6-follow-ratio-y", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Roll Breakout Force Strength", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-breakout-force-strength-roll")
        self._cm.subscribe("ab6-breakout-force-strength-roll", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Pitch Breakout Force Strength", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-breakout-force-strength-pitch")
        self._cm.subscribe("ab6-breakout-force-strength-pitch", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Roll Breakout Force Range", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-breakout-force-range-roll")
        self._cm.subscribe("ab6-breakout-force-range-roll", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Pitch Breakout Force Range", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-breakout-force-range-pitch")
        self._cm.subscribe("ab6-breakout-force-range-pitch", self._current_row.set_value)

        # Confirmed against real hardware from the Advanced Settings ->
        # Axis Travel page capture - see data/serial.yml. WHICH physical
        # axis is "1" vs "2" isn't confirmed (order-inferred only), so
        # they're labeled generically rather than X/Y/Z - see the label
        # subtitles and data/serial.yml for what that means in practice.
        # The Output Mapping Curve, Invert Axis, Axis Offset and the third
        # axis weren't confidently attributed and are left out.
        self.add_preferences_group("Axis Travel")

        self._add_row(BoxflatSliderRow("Axis 1 Positive Travel Limit", suffix="%",
            subtitle="Physical axis identity (which stick axis this is) unconfirmed"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-axis-travel-limit-1-positive")
        self._cm.subscribe("ab6-axis-travel-limit-1-positive", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Axis 1 Negative Travel Limit", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-axis-travel-limit-1-negative")
        self._cm.subscribe("ab6-axis-travel-limit-1-negative", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Axis 2 Positive Travel Limit", suffix="%",
            subtitle="Physical axis identity (which stick axis this is) unconfirmed"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-axis-travel-limit-2-positive")
        self._cm.subscribe("ab6-axis-travel-limit-2-positive", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Axis 2 Negative Travel Limit", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-axis-travel-limit-2-negative")
        self._cm.subscribe("ab6-axis-travel-limit-2-negative", self._current_row.set_value)

        # Confirmed against real hardware from the "Special" page capture -
        # a page not in the original inventory, found by the user browsing
        # Cockpit's tabs. See data/serial.yml. Hardware Trim Mode, Trim
        # Mode (Direct Input/Hardware), the trim button bindings, Base
        # Force Model Selection, Grip Removal Protection and Extend Travel
        # Range weren't confidently attributed and are left out.
        self.add_preferences_group("Special")

        self._add_row(BoxflatSliderRow("Trim Follow Rate", range_start=1, range_end=20))
        self._current_row.subscribe(self._cm.set_setting, "ab6-trim-follow-rate")
        self._cm.subscribe("ab6-trim-follow-rate", self._current_row.set_value)

        subtitle = "Which physical direction this is (+X/-X/+Y/-Y) is unconfirmed"
        self._add_row(BoxflatSliderRow("Trim Range 1", suffix="%", subtitle=subtitle))
        self._current_row.subscribe(self._cm.set_setting, "ab6-trim-range-0")
        self._cm.subscribe("ab6-trim-range-0", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Trim Range 2", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-trim-range-1")
        self._cm.subscribe("ab6-trim-range-1", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Trim Range 3", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-trim-range-2")
        self._cm.subscribe("ab6-trim-range-2", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Trim Range 4", suffix="%"))
        self._current_row.subscribe(self._cm.set_setting, "ab6-trim-range-3")
        self._cm.subscribe("ab6-trim-range-3", self._current_row.set_value)


    def _set_version(self, value: int, row: BoxflatLabelRow) -> None:
        row.set_label(format_version(value))


    def _set_light_color(self, value: list) -> None:
        # Wire format is [0, 0, R, G, B] - see data/serial.yml.
        self._cm.set_setting([0, 0] + value, "ab6-light-color")


    def _set_light_color_row(self, value: list) -> None:
        if not isinstance(value, list) or len(value) != 5:
            return
        self._light_color_row.set_led_value(value[2:], 0)


    def _start_slider_calibration(self, *_) -> None:
        self._cm.set_setting(1, "ab6-slider-calibration-start-1")
        self._cm.set_setting(1, "ab6-slider-calibration-start-2")


    def _start_stick_x_calibration(self, *_) -> None:
        self._cm.set_setting(0, "ab6-stick-x-calibration-start")


    def _start_stick_y_calibration(self, *_) -> None:
        self._cm.set_setting(0, "ab6-stick-y-calibration-start")
