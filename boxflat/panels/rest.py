from boxflat.panels.settings_panel import SettingsPanel
from boxflat.panels import SettingsPanel
from boxflat.widgets import *

class OtherSettings(SettingsPanel):
    def __init__(self, button_callback, dry_run: bool) -> None:
        self._test_text = "inactive"
        if dry_run:
            self._test_text = "active"

        super().__init__("Other", button_callback)


    def prepare_ui(self) -> None:
        self._add_row(BoxflatRow("Other settings"))
        self._current_row.subtitle = "Work in progress"
