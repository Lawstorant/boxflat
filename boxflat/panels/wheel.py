from boxflat.panels.settings_panel import SettingsPanel
import boxflat.connection_manager as connection_manager

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        self._split = None
        super(WheelSettings, self).__init__("Wheel", button_callback)


    def prepare_ui(self) -> None:
        self.add_preferences_page()
        self.add_preferences_group("Input settings")
        self.add_toggle_button_row("Dual Clutch Paddles Mode", ["Combined", "Split", "Buttons"], callback=self._set_paddles_mode)
        self._split = self.add_slider_row(
            "Clutch Split Point", 0 , 100, 50,
            marks=[25, 50, 75],
            mark_suffix=" %",
            subtitle="Left paddle cutoff",
            callback=self._set_clutch_point
        )
        self.add_toggle_button_row("Left Stick Mode", ["Buttons", "D-Pad"], callback=self._set_stick_mode)

        self.add_preferences_group("Indicator settings")
        self.add_toggle_button_row("RPM Indicator Mode", ["RPM", "On", "Off"], callback=self._set_indicator_mode)

        self.add_toggle_button_row("RPM Indicator Display Mode", ["Mode 1", "Mode 2"], callback=self._set_display_mode)
        # # TODO: Add custom timing with a vertical sliders widget
        self.add_toggle_button_row("RPM Indicator Timing", ["Early", "Normal", "Late"], callback=self._set_indicator_timings)
        # # TODO: Add color picker for every light
        self.add_slider_row("Brightness", 0 , 100, 50,
                             marks=[25, 50, 75], mark_suffix=" %",
                             subtitle="RPM and buttons",
                             callback=self._set_brightness)

        # self.add_preferences_group("Indicator colors")
        # for i in range(0, 10):
        #     self.add_color_picker_row(f"Light {i+1}")


    def _set_paddles_mode(self, label: str) -> None:
        if label == "Combined":
            self._split(True)
            connection_manager.set_wheel_setting("paddles-mode", 2)
        elif label == "Split":
            self._split(False)
            connection_manager.set_wheel_setting("paddles-mode", 3)
        elif label == "Buttons":
            self._split(False)
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


    def _set_display_mode(self, label: str) -> None:
        if label != None:
            connection_manager.set_wheel_setting("display-mode", int(label[-1]))


    def _set_indicator_timings(self, label:str) -> None:
        if label == "Early":
            value = bytes([65, 69, 72, 75, 78, 80, 83, 85, 88, 91])
            connection_manager.set_wheel_setting("indicator-timings", byte_value=value)
        elif label == "Normal":
            value = bytes([75, 79, 82, 85, 87, 88, 89, 90, 92, 94])
            connection_manager.set_wheel_setting("indicator-timings", byte_value=value)
        elif label == "Late":
            value = bytes([80, 83, 86, 89, 91, 92, 93, 94, 96, 97])
            connection_manager.set_wheel_setting("indicator-timings", byte_value=value)