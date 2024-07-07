from panels.settings_panel import SettingsPanel
import connection_manager

class SequentialSettings(SettingsPanel):
    colorS1 = 0
    colorS2 = 0

    def __init__(self, button_callback) -> None:
        super(SequentialSettings, self).__init__("Sequential Shifter", button_callback)

    def _prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Shifter Settings")
        self._add_switch_row("Reverse Shift Direction", subtitle="Why would you do that?", callback=self._set_direction)
        self._add_switch_row("Paddle Shifter Synchronization", callback=self._set_paddle_sync)

        self._add_slider_row(
            "Button Brightness", 0, 10, 8,
            marks=[5],
            callback=self._set_brightness
        )

        self._add_color_picker_row("S1 Color", callback=lambda color: self._set_colors(1, color))
        self._add_color_picker_row("S2 Color", callback=lambda color: self._set_colors(2, color))


    def _set_colors(self, button: int, color: int) -> None:
        if color == None:
            return
        if button == 1:
            self.colorS1 = color
        if button == 2:
            self.colorS2 = color

        connection_manager.set_sequential_setting("lights", 0)
        connection_manager.set_sequential_setting("lights", self.colorS1*256)
        connection_manager.set_sequential_setting("lights", self.colorS1*256 + self.colorS2)


    def _set_brightness(self, value: int) -> None:
        if value != None:
            connection_manager.set_sequential_setting("brightness", value)


    def _set_direction(self, value: int) -> None:
        if value != None:
            connection_manager.set_sequential_setting("direction", value)


    def _set_paddle_sync(self, value: int) -> None:
        if value != None:
            connection_manager.set_sequential_setting("paddle-sync", value)
