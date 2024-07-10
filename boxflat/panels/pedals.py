from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        super(PedalsSettings, self).__init__("Pedals", button_callback, connection_manager)

    def prepare_ui(self) -> None:
        self.add_preferences_page()

        # Throttle
        self.add_preferences_group("Throttle settings", level_bar=1)
        self.add_switch_row("Reverse Direction",
            callback=lambda value: self._set_pedal_direction("throttle", value))
        self.add_slider_row(
            "Range Start",
            0,
            100,
            0,
            marks=[50],
            mark_suffix=" %",
            callback=lambda value: self._set_pedal_min_max("throttle-min", value)
        )
        self.add_slider_row(
            "Range End",
            0,
            100,
            100,
            marks=[50],
            mark_suffix=" %",
            callback=lambda value: self._set_pedal_min_max("throttle-max", value)
        )
        self.add_calibration_button_row("Calibration", "Calibrate",
            callback1=lambda: self._set_pedal_calibration("throttle", "start"),
            callback2=lambda: self._set_pedal_calibration("throttle", "stop"))

        # Brake
        self.add_preferences_group("Brake settings", level_bar=1)
        self.add_switch_row("Reverse Direction",
            callback=lambda value: self._set_pedal_direction("brake", value))
        self.add_slider_row(
            "Range Start",
            0,
            100,
            50,
            marks=[50],
            mark_suffix=" %",
            callback=lambda value: self._set_pedal_min_max("brake-min", value)
        )
        self.add_slider_row(
            "Range End",
            0,
            100,
            0,
            marks=[50],
            mark_suffix=" %",
            callback=lambda value: self._set_pedal_min_max("brake-max", value)
        )
        self.add_slider_row(
            "Brake pressure force",
            0,
            100,
            50,
            marks=[25, 50, 75],
            mark_suffix="%",
            subtitle="This seems to work backwards?",
            callback=self._set_brake_max_force
        )
        # self.add_calibration_button_row("Calibration", "Calibrate",
        #     callback1=lambda: self._set_pedal_calibration("brake", "start"),
        #     callback2=lambda: self._set_pedal_calibration("brake", "stop"))

        # Clutch
        self.add_preferences_group("Clutch settings", level_bar=1)
        self.add_switch_row("Reverse Direction",
            callback=lambda value: self._set_pedal_direction("clutch", value))
        self.add_slider_row(
            "Range Start",
            0,
            100,
            0,
            marks=[50],
            mark_suffix=" %",
            callback=lambda value: self._set_pedal_min_max("clutch-min", value)
        )
        self.add_slider_row(
            "Range End",
            0,
            100,
            100,
            marks=[50],
            mark_suffix=" %",
            callback=lambda value: self._set_pedal_min_max("clutch-max", value)
        )
        self.add_calibration_button_row("Calibration", "Calibrate",
            callback1=lambda: self._set_pedal_calibration("clutch", "start"),
            callback2=lambda: self._set_pedal_calibration("clutch", "stop"))


    def _set_pedal_direction(self, pedal: str, value: int) -> None:
        self._cm.set_setting(f"pedals-{pedal}-dir", int(value))

    def _set_pedal_min_max(self, pedal: str, value: int) -> None:
        self._cm.set_setting(f"pedals-{pedal}", value)

    def _set_brake_max_force(self, value: int) -> None:
        self._cm.set_setting("pedals-brake-max-force", value)

    def _set_pedal_calibration(self, pedal: str, hint: str) -> None:
        self._cm.set_setting(f"pedals-{pedal}-{hint}-calibration", 0)


