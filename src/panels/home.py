from src.panels.settings_panel import SettingsPanel

class HomeSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super().__init__("Home", button_callback)
        self.hide_banner()

    def open_github(self, *args) -> None:
        self.open_url("https://github.com/Lawstorant/boxflat")

    def open_github2(self, *args) -> None:
        self.open_url("https://github.com/JacKeTUs/moza-ff")

    def _prepare_ui(self) -> None:
        super()._prepare_ui()

        self._add_preferences_page()
        self._add_preferences_group("")
        self._add_title_row("~Welcome to Boxflat~")
        self._add_button_row("Go to the project page", "GitHub", callback=self.open_github, subtitle="Thanks")
        self._add_button_row(
            "Go to the universal-ff driver page",
            "GitHub",
            callback=self.open_github2,
            subtitle="FFB Driver"
        )

        self._add_preferences_group("")
        self._add_title_row("About boxflat")

