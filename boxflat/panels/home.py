from boxflat.panels.settings_panel import SettingsPanel

class HomeSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super().__init__("Home", button_callback)
        self.hide_banner()

    def open_github(self, *args) -> None:
        self.open_url("https://github.com/Lawstorant/boxflat")

    def open_github2(self, *args) -> None:
        self.open_url("https://github.com/JacKeTUs/moza-ff")

    def prepare_ui(self) -> None:
        super().prepare_ui()

        self.add_preferences_page()
        self.add_preferences_group("")
        self.add_title_row("~Welcome to Boxflat~")
        self.add_button_row("Go to the project page", "GitHub", callback=self.open_github, subtitle="Thanks")
        self.add_button_row(
            "Go to the universal-ff driver page",
            "GitHub",
            callback=self.open_github2,
            subtitle="FFB Driver"
        )

        # self.add_preferences_group("")
        # self.add_title_row("About boxflat")

