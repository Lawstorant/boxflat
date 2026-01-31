# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.hid_handler import MozaAxis, AxisData

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler):
        self._brake_calibration_row = None
        self._curve_rows: dict[str, BoxflatEqRow] = {}
        self._inverted = False
        self._pedal_pages: dict[str, Gtk.Widget] = {}
        self._pedal_swap_map: dict[str, str] = {}  # maps page_name -> actual_pedal_name
        self._view_stack = None

        self._presets = [
            [20, 40, 60, 80, 100], # Linear
            [ 8, 24, 76, 92, 100], # S Curve
            [ 6, 14, 28, 54, 100], # Exponential
            [46, 72, 86, 94, 100]  # Parabolic
        ]

        super().__init__("Pedals", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("pedals-throttle-dir", self.active)


    def set_brake_calibration_active(self, active: int):
        self._brake_calibration_row.set_active(active)


    def _get_actual_pedal_name(self, page_pedal: str) -> str:
        """Get the actual pedal name whose data should be displayed on this page.

        When inverted is enabled, the Throttle page shows Clutch's data and
        the Clutch page shows Throttle's data. Brake page never changes.

        Args:
            page_pedal: The pedal name for this page (THROTTLE, BRAKE, or CLUTCH)

        Returns:
            The actual pedal name whose data should be displayed
        """
        return self._pedal_swap_map.get(page_pedal, page_pedal)


    def set_inverted_pedals(self, inverted: int) -> None:
        """Update pedal page titles and value routing when inversion state changes.

        This is a global setting that affects all pedal devices uniformly.
        The inversion toggle applies to the entire pedal configuration, not
        per-device. All pedal pages show the same swapped labels when inverted.

        Page titles keep their original names and only add a star indicator
        when inverted to show which pedals are affected.
        """
        self._inverted = bool(inverted)

        # Update which pedal each page displays
        if self._inverted:
            self._pedal_swap_map[MozaAxis.THROTTLE.name] = MozaAxis.CLUTCH.name
            self._pedal_swap_map[MozaAxis.CLUTCH.name] = MozaAxis.THROTTLE.name
        else:
            self._pedal_swap_map[MozaAxis.THROTTLE.name] = MozaAxis.THROTTLE.name
            self._pedal_swap_map[MozaAxis.CLUTCH.name] = MozaAxis.CLUTCH.name

        # Brake page never swaps
        self._pedal_swap_map[MozaAxis.BRAKE.name] = MozaAxis.BRAKE.name

        # Update Throttle page title - always "Throttle" (with * when inverted)
        if MozaAxis.THROTTLE.name in self._pedal_pages and self._view_stack:
            stack_page = self._view_stack.get_page(self._pedal_pages[MozaAxis.THROTTLE.name])
            if stack_page:
                title = "Throttle"
                title = f"{title} *" if self._inverted else title
                stack_page.set_title(title)

        # Update Clutch page title - always "Clutch" (with * when inverted)
        if MozaAxis.CLUTCH.name in self._pedal_pages and self._view_stack:
            stack_page = self._view_stack.get_page(self._pedal_pages[MozaAxis.CLUTCH.name])
            if stack_page:
                title = "Clutch"
                title = f"{title} *" if self._inverted else title
                stack_page.set_title(title)

        # Brake page never changes - no update needed


    def prepare_ui(self):
        self.add_view_stack()
        self._view_stack = self._current_stack
        for pedal in [MozaAxis.THROTTLE, MozaAxis.BRAKE, MozaAxis.CLUTCH]:
            self._prepare_pedal(pedal)


    def _prepare_pedal(self, pedal: AxisData):
        self.add_preferences_page(pedal.name.title())
        self._pedal_pages[pedal.name] = self._current_page
        self.add_preferences_group(f"{pedal.name.title()} Curve", level_bar=1)
        self._current_group.set_bar_max(65_534)

        # Subscribe to the actual pedal's HID data (swapped when inverted)
        actual_pedal = self._get_actual_pedal_name(pedal.name)
        self._hid_handler.subscribe(actual_pedal, self._current_group.set_bar_level)

        self._curve_rows[pedal.name] = BoxflatEqRow("", 5, suffix="%")
        self._add_row(self._curve_rows[pedal.name])
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(280)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)
        self._curve_rows[pedal.name].set_height(290)
        self._current_row.subscribe(self._set_curve_preset, pedal.name)
        for i in range(5):
            self._curve_rows[pedal.name].subscribe_slider(i, self._set_curve_point, i, pedal.name)
            # Subscribe to actual pedal's curve settings
            self._cm.subscribe(f"pedals-{actual_pedal}-y{i+1}", self._get_curve, i, pedal.name)

        self.add_preferences_group(f"{pedal.name.title()} Range")
        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        # Subscribe to actual pedal's min setting
        self._current_row.subscribe(self._cm.set_setting, f"pedals-{actual_pedal}-min")
        self._cm.subscribe(f"pedals-{actual_pedal}-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        # Subscribe to actual pedal's max setting
        self._current_row.subscribe(self._cm.set_setting, f"pedals-{actual_pedal}-max")
        self._cm.subscribe(f"pedals-{actual_pedal}-max", self._current_row.set_value)

        if pedal == MozaAxis.BRAKE:
            self._add_row(BoxflatSliderRow("Sensor ratio", suffix="%", subtitle="0% = Only Angle Sensor\n100% = Only Load Cell"))
            self._current_row.add_marks(25, 50, 75)
            self._current_row.subscribe(self._cm.set_setting, "pedals-brake-angle-ratio")
            self._cm.subscribe("pedals-brake-angle-ratio", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        # Subscribe to actual pedal's direction setting
        self._current_row.subscribe(self._cm.set_setting, f"pedals-{actual_pedal}-dir")
        self._cm.subscribe(f"pedals-{actual_pedal}-dir", self._current_row.set_value)

        self._add_row(BoxflatCalibrationRow("Calibration", f"Fully depress {pedal.name} once"))
        # Subscribe to actual pedal's calibration settings
        self._current_row.subscribe("calibration-start", self._cm.set_setting, f"pedals-{actual_pedal}-calibration-start", True)
        self._current_row.subscribe("calibration-stop", self._cm.set_setting, f"pedals-{actual_pedal}-calibration-stop", True)
        if pedal == MozaAxis.BRAKE:
            self._brake_calibration_row = self._current_row

        self.add_preferences_group()
        self._add_row(BoxflatButtonRow("Restore default settings", "Reset"))
        self._current_row.subscribe(lambda v: self.reset(pedal.name))


    def _set_curve_preset(self, value: int, pedal: str):
        self._set_curve(self._presets[value], pedal)


    def _set_curve_point(self, value: int, index: int, pedal: str):
        # Write to the actual pedal's settings (swapped when inverted)
        actual_pedal = self._get_actual_pedal_name(pedal)
        self._cm.set_setting(value, f"pedals-{actual_pedal}-y{index+1}")


    def _set_curve(self, values: list, pedal: str):
        self._curve_rows[pedal].set_sliders_value(values, mute=False)


    def _get_curve(self, value: int, sindex: int, pedal: str):
        index = -1
        row = self._curve_rows[pedal]

        values = row.get_sliders_value()
        values[sindex] = value

        if values in self._presets:
            index = self._presets.index(values)

        row.set_button_value(index)
        row.set_slider_value(value, sindex)


    def reset(self, pedal: str, *_) -> None:
        # Reset the actual pedal's settings (swapped when inverted)
        actual_pedal = self._get_actual_pedal_name(pedal)

        self._set_curve_preset(0, pedal)

        self._cm.set_setting(0, f"pedals-{actual_pedal}-min")
        self._cm.set_setting(100, f"pedals-{actual_pedal}-max")
        self._cm.set_setting(0, f"pedals-{actual_pedal}-dir")
        if actual_pedal == MozaAxis.BRAKE.name:
            self._cm.set_setting(50, "pedals-brake-angle-ratio")

        self._set_curve_preset(0, pedal)
