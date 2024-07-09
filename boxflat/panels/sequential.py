from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

class SequentialSettings(SettingsPanel):
    colorS1 = 0
    colorS2 = 0

    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        super(SequentialSettings, self).__init__("Sequential Shifter", button_callback, connection_manager)

    def prepare_ui(self) -> None:
        self.add_preferences_page()
        self.add_preferences_group("Shifter Settings")
        self.add_switch_row("Reverse Shift Direction", subtitle="Why would you do that?", callback=self._set_direction)
        self.add_switch_row("Paddle Shifter Synchronization", callback=self._set_paddle_sync)

        self.add_slider_row(
            "Button Brightness", 0, 10, 8,
            marks=[5],
            callback=self._set_brightness
        )

        self.add_color_picker_row("S1 Color", callback=lambda color: self._set_colors(1, color))
        self.add_color_picker_row("S2 Color", callback=lambda color: self._set_colors(2, color))


    def _set_colors(self, button: int, color: int) -> None:
        if color == None:
            return
        if button == 1:
            self.colorS1 = color
        if button == 2:
            self.colorS2 = color

        self._cm.set_sequential_setting("lights", 0)
        self._cm.set_sequential_setting("lights", self.colorS1*256)
        self._cm.set_sequential_setting("lights", self.colorS1*256 + self.colorS2)


    def _set_brightness(self, value: int) -> None:
        if value != None:
            self._cm.set_sequential_setting("brightness", value)


    def _set_direction(self, value: int) -> None:
        if value != None:
            self._cm.set_sequential_setting("direction", value)


    def _set_paddle_sync(self, value: int) -> None:
        if value != None:
            self._cm.set_sequential_setting("paddle-sync", value)
