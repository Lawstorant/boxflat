# Copyright (c) 2025, Ryan Orth Using CachyOS BTW
# Telemetry panel for SimAPI integration

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.simapi_handler import SimApiHandler
from boxflat.widgets import *
from boxflat.settings_handler import SettingsHandler

from gi.repository import GLib


class TelemetrySettings(SettingsPanel):
    """
    Panel for configuring SimAPI telemetry integration.
    Allows users to enable/disable telemetry feed to dashboard and wheel,
    and monitor connection status. RPM thresholds are configured in the
    respective Wheel/Dashboard panels.
    """

    def __init__(self, button_callback, connection_manager: MozaConnectionManager,
                 hid_handler, settings: SettingsHandler, simapi_handler: SimApiHandler):
        self._settings = settings
        self._simapi = simapi_handler

        # UI element references
        self._status_label = None
        self._sim_label = None
        self._car_label = None
        self._rpm_level = None
        self._gear_label = None
        self._dash_switch = None
        self._wheel_switch = None
        self._wheel_old_switch = None
        self._poll_rate_slider = None

        super().__init__("Telemetry", button_callback, connection_manager, hid_handler)

        # Subscribe to SimAPI events
        self._simapi.subscribe("connected", self._on_connected)
        self._simapi.subscribe("rpm-percent", self._on_rpm_percent)
        self._simapi.subscribe("rpm-raw", self._on_rpm_raw)
        self._simapi.subscribe("gear", self._on_gear)
        self._simapi.subscribe("sim-status", self._on_sim_status)
        self._simapi.subscribe("car-name", self._on_car_name)

        # Auto-detect wheel type based on which wheel responds
        self._cm.subscribe_connected("wheel-telemetry-mode", self._on_new_wheel_detected)
        self._cm.subscribe_connected("wheel-rpm-value1", self._on_old_wheel_detected)

        # Always visible (no device dependency)
        self.active(1)

        # Load saved settings
        self._load_settings()

        # Start simapi handler
        self._simapi.start()

    def prepare_ui(self):
        self.add_view_stack()

        # Status page
        self.add_preferences_page("Status")
        self.add_preferences_group("SimAPI Connection")

        self._status_label = BoxflatLabelRow("Status", "SimAPI daemon connection", "Checking...")
        self._add_row(self._status_label)

        self._sim_label = BoxflatLabelRow("Simulator", "Current simulation", "None")
        self._add_row(self._sim_label)

        self._car_label = BoxflatLabelRow("Car", "Current vehicle", "None")
        self._add_row(self._car_label)

        self.add_preferences_group("Live Telemetry")
        self._rpm_raw_label = BoxflatLabelRow("Raw RPM", "Current / Max (effective) / Idle", "0 / 0 (0) / 0")
        self._add_row(self._rpm_raw_label)

        self._rpm_level = BoxflatLevelRow("RPM %", max_value=100)
        self._rpm_level.set_bar_width(400)
        self._add_row(self._rpm_level)

        self._gear_label = BoxflatLabelRow("Gear", "", "N")
        self._add_row(self._gear_label)

        self.add_preferences_group("Calibration")
        self._current_group.set_description("Auto-calibrates max RPM when game doesn't provide it")
        self._add_row(BoxflatButtonRow("Reset RPM Calibration", "Reset", "Rev to max RPM to recalibrate"))
        self._current_row.subscribe(self._reset_calibration)

        # Settings page
        self.add_preferences_page("Settings")
        self.add_preferences_group("Telemetry Output")
        self._current_group.set_description("Enable telemetry output to your Moza devices")

        self._dash_switch = BoxflatSwitchRow("Dashboard RPM LEDs", "Send telemetry to dashboard")
        self._add_row(self._dash_switch)
        self._dash_switch.subscribe(self._on_dash_toggle)

        self._wheel_switch = BoxflatSwitchRow("Wheel RPM LEDs", "Send telemetry to wheel")
        self._add_row(self._wheel_switch)
        self._wheel_switch.subscribe(self._on_wheel_toggle)

        self._wheel_old_switch = BoxflatSwitchRow("ES Wheel (Old Protocol)", "Enable for ES wheel compatibility")
        self._add_row(self._wheel_old_switch)
        self._wheel_old_switch.subscribe(self._on_wheel_old_toggle)

        self.add_preferences_group("Performance")
        self._poll_rate_slider = BoxflatSliderRow("Update Rate", range_start=30, range_end=120,
                                                   subtitle="Updates per second", suffix=" Hz")
        self._poll_rate_slider.add_marks(30, 60, 90, 120)
        self._poll_rate_slider.set_value(60)
        self._add_row(self._poll_rate_slider)
        self._poll_rate_slider.subscribe(self._on_poll_rate_change)

    def _load_settings(self):
        """Load saved settings from config file."""
        # Load dash enabled
        dash_enabled = self._settings.read_setting("telemetry-dash-enabled")
        if dash_enabled is not None:
            self._dash_switch.set_value(dash_enabled)
            self._simapi.set_dash_enabled(bool(dash_enabled))

        # Load wheel old protocol (must be before wheel enabled)
        wheel_old = self._settings.read_setting("telemetry-wheel-old-protocol")
        if wheel_old is not None:
            self._wheel_old_switch.set_value(wheel_old)
            self._simapi.set_wheel_old_protocol(bool(wheel_old))

        # Load wheel enabled
        wheel_enabled = self._settings.read_setting("telemetry-wheel-enabled")
        if wheel_enabled is not None:
            self._wheel_switch.set_value(wheel_enabled)
            self._simapi.set_wheel_enabled(bool(wheel_enabled))

        # Load poll rate
        poll_rate = self._settings.read_setting("telemetry-poll-rate")
        if poll_rate is not None:
            self._poll_rate_slider.set_value(poll_rate)
            self._simapi.set_poll_rate(poll_rate)

    def _on_connected(self, connected: bool):
        """Handle SimAPI connection status change."""
        if connected:
            GLib.idle_add(self._status_label.set_label, "Connected")
        else:
            GLib.idle_add(self._status_label.set_label, "Not available")
            GLib.idle_add(self._sim_label.set_label, "None")
            GLib.idle_add(self._car_label.set_label, "None")
            GLib.idle_add(self._rpm_level.set_value, 0)
            GLib.idle_add(self._rpm_raw_label.set_label, "0 / 0 (0) / 0")
            GLib.idle_add(self._gear_label.set_label, "N")

    def _on_rpm_percent(self, percent: int):
        """Handle RPM percentage update."""
        GLib.idle_add(self._rpm_level.set_value, percent)

    def _on_rpm_raw(self, data: tuple):
        """Handle raw RPM data update."""
        rpm, maxrpm, idlerpm, effective_max = data
        # Show effective max in parentheses if different from reported max
        if maxrpm != effective_max and effective_max > 0:
            GLib.idle_add(self._rpm_raw_label.set_label, f"{rpm} / {maxrpm} ({effective_max}) / {idlerpm}")
        else:
            GLib.idle_add(self._rpm_raw_label.set_label, f"{rpm} / {maxrpm} / {idlerpm}")

    def _on_gear(self, gear: int):
        """Handle gear change."""
        if gear == 0:
            gear_str = "R"
        elif gear == 1:
            gear_str = "N"
        else:
            gear_str = str(gear - 1)
        GLib.idle_add(self._gear_label.set_label, gear_str)

    def _on_sim_status(self, status: int):
        """Handle simulation status change."""
        status_map = {
            0: "Off",
            1: "In Menu",
            2: "Active"
        }
        GLib.idle_add(self._sim_label.set_label, status_map.get(status, "Unknown"))

    def _on_car_name(self, car_name: str):
        """Handle car name update."""
        GLib.idle_add(self._car_label.set_label, car_name)

    def _reset_calibration(self, *_):
        """Reset RPM auto-calibration."""
        self._simapi.reset_calibration()
        self.show_toast("RPM calibration reset - rev to max RPM to recalibrate")

    def _on_dash_toggle(self, value: int):
        """Handle dashboard telemetry toggle."""
        enabled = bool(value)
        self._simapi.set_dash_enabled(enabled)
        self._settings.write_setting(value, "telemetry-dash-enabled")

        # Set dash to telemetry mode when enabled
        if enabled and self._cm:
            self._cm.set_setting(1, "dash-rpm-indicator-mode")

    def _on_wheel_toggle(self, value: int):
        """Handle wheel telemetry toggle."""
        enabled = bool(value)
        self._simapi.set_wheel_enabled(enabled)
        self._settings.write_setting(value, "telemetry-wheel-enabled")

        # Set wheel to appropriate mode when enabled
        if enabled and self._cm:
            old_protocol = self._wheel_old_switch.get_value() if self._wheel_old_switch else False
            if old_protocol:
                # ES wheel uses rpm-indicator-mode
                self._cm.set_setting(1, "wheel-rpm-indicator-mode")
            else:
                # New wheels use telemetry-mode
                self._cm.set_setting(1, "wheel-telemetry-mode")

    def _on_wheel_old_toggle(self, value: int):
        """Handle old wheel protocol toggle."""
        old_protocol = bool(value)
        self._simapi.set_wheel_old_protocol(old_protocol)
        self._settings.write_setting(value, "telemetry-wheel-old-protocol")

        # If wheel is currently enabled, update the mode setting
        if self._wheel_switch and self._wheel_switch.get_value() and self._cm:
            if old_protocol:
                self._cm.set_setting(1, "wheel-rpm-indicator-mode")
            else:
                self._cm.set_setting(1, "wheel-telemetry-mode")

    def _on_new_wheel_detected(self, value: int):
        """Auto-detect new wheel protocol when wheel-telemetry-mode responds."""
        if value >= 0:  # Valid response means new wheel detected
            self._simapi.set_wheel_old_protocol(False)
            if self._wheel_old_switch:
                GLib.idle_add(self._wheel_old_switch.set_value, 0)

    def _on_old_wheel_detected(self, value: int):
        """Auto-detect old wheel protocol (ES wheel) when wheel-rpm-value1 responds."""
        if value >= 0:  # Valid response means old wheel detected
            self._simapi.set_wheel_old_protocol(True)
            if self._wheel_old_switch:
                GLib.idle_add(self._wheel_old_switch.set_value, 1)

    def _on_poll_rate_change(self, value: int):
        """Handle poll rate change."""
        self._simapi.set_poll_rate(value)
        self._settings.write_setting(value, "telemetry-poll-rate")

    def active(self, value: int):
        """Override to always show this panel (no device dependency)."""
        # Don't call super().active() - we manage visibility ourselves
        if value > -1:
            GLib.idle_add(self._button.set_visible, True)

    def shutdown(self, *args):
        """Clean up on application shutdown."""
        self._simapi.stop()
        super().shutdown(*args)
