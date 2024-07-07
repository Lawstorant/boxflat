from boxflat.panels.settings_panel import SettingsPanel

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(PedalsSettings, self).__init__("Pedals", button_callback)

    def prepare_ui(self) -> None:
        self.add_preferences_page()

        # Throttle
        self.add_preferences_group("Throttle settings", level_bar=1)
        self.add_switch_row("Reverse Direction")
        self.add_button_row("Pedal Calibration", "Calibrate")

        # Brake
        self.add_preferences_group("Brake settings", level_bar=1)
        self.add_switch_row("Reverse Direction")
        self.add_slider_row(
            "Brake pedal max force",
            0,
            200,
            50,
            marks=[50, 100, 150],
            mark_suffix=" kg",
            subtitle="Not everyone is a Hulk"
        )
        self.add_button_row("Pedal Calibration", "Calibrate")

        # Clutch
        self.add_preferences_group("Clutch settings", level_bar=1)
        self.add_switch_row("Reverse Direction")
        self.add_button_row("Pedal Calibration", "Calibrate")
