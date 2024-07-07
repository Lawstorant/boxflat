import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from src.panels.settings_panel import SettingsPanel
import src.connection_manager as connection_manager

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(WheelSettings, self).__init__("Wheel", button_callback)


    def _prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Input settings")
        self._add_toggle_button_row("Dual Clutch Paddles Mode", ["Combined", "Split", "Buttons"], callback=self._set_paddles_mode)
        self._add_slider_row("Clutch Split Point", 0 , 100, 50,
                             marks=[25, 50, 75],
                             mark_suffix=" %",
                             callback=self._set_clutch_point)
        self._add_toggle_button_row("Left Stick Mode", ["Buttons", "D-Pad"], callback=self._set_stick_mode)

        self._add_preferences_group("Indicator settings")
        self._add_toggle_button_row("RPM Indicator Mode", ["RPM", "On", "Off"], callback=self._set_indicator_mode)

        # self._add_toggle_button_row("RPM Indicator Display Mode", ["Mode 1", "Mode 2"])
        # # TODO: Add custom timing with a vertical sliders widget
        # self._add_toggle_button_row("RPM Indicator Timing", ["Early", "Normal", "Late"])
        # # TODO: Add color picker for every light
        self._add_slider_row("Brightness", 0 , 100, 50,
                             marks=[25, 50, 75], mark_suffix=" %",
                             subtitle="RPM and buttons",
                             callback=self._set_brightness)

        # self._add_preferences_group("Indicator colors")
        # for i in range(0, 10):
        #     self._add_color_picker_row(f"Light {i+1}")


    def _set_paddles_mode(self, label: str) -> None:
        if label == "Combined":
            connection_manager.set_wheel_setting("paddles-mode", 2)
        elif label == "Split":
            connection_manager.set_wheel_setting("paddles-mode", 3)
        elif label == "Buttons":
            connection_manager.set_wheel_setting("paddles-mode", 1)


    def _set_clutch_point(self, value: int) -> None:
        if value != None:
            connection_manager.set_wheel_setting("clutch-point", value)


    def _set_stick_mode(self, label: str) -> None:
        if label == "Buttons":
            connection_manager.set_wheel_setting("stick-mode", 0)
        elif label == "D-Pad":
            connection_manager.set_wheel_setting("stick-mode", 256)


    def _set_indicator_mode(self, label: str) -> None:
        if label == "RPM":
            connection_manager.set_wheel_setting("indicator-mode", 1)
        elif label == "Off":
            connection_manager.set_wheel_setting("indicator-mode", 2)
        elif label == "On":
            connection_manager.set_wheel_setting("indicator-mode", 3)

    def _set_brightness(self, value: int) -> None:
        if value != None:
            connection_manager.set_wheel_setting("brightness", value)
