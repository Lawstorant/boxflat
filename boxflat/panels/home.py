from boxflat.panels.settings_panel import SettingsPanel
from boxflat.widgets import *

class HomeSettings(SettingsPanel):
    def __init__(self, button_callback, dry_run: bool, version: str="") -> None:
        self._test_text = "inactive"
        if dry_run:
            self._test_text = "active"

        self._version = version

        super().__init__("Home", button_callback)


    def prepare_ui(self) -> None:
        self.add_preferences_group()
        self._add_row(BoxflatRow("Welcome to Boxflat", subtitle=f"Version: {self._version}"))

        self.add_preferences_group()
        self._add_row(BoxflatButtonRow("Go to the project page", "GitHub", subtitle="Leave a star!"))
        self._current_row.subscribe(lambda value: self.open_url("https://github.com/Lawstorant/boxflat"))

        self._add_row(BoxflatButtonRow("Go to the universal-pidff driver page", "GitHub", subtitle="FFB Driver"))
        self._current_row.subscribe(lambda value: self.open_url("https://github.com/JacKeTUs/universal-pidff"))

        self.add_preferences_group()
        self._add_row(BoxflatRow(f"Test mode:  {self._test_text}"))
