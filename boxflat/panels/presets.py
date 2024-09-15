from .settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.preset_handler import MozaPresetHandler

class PresetSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._includes = {}
        self._name_row = Adw.EntryRow()
        self._name_row.set_title("Preset Name")
        self._save_row = None
        super().__init__("Presets", button_callback, connection_manager)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Saving")
        self._add_row(self._name_row)

        self._add_row(BoxflatSwitchRow("Include Base Settings"))
        self._includes["base"] = self._current_row.get_value

        self._add_row(BoxflatSwitchRow("Include Wheel Settings"))
        self._includes["wheel"] = self._current_row.get_value

        self._add_row(BoxflatSwitchRow("Include Pedals Settings"))
        self._includes["pedals"] = self._current_row.get_value

        self._add_row(BoxflatSwitchRow("Include Handbrake Settings"))
        self._includes["handbrake"] = self._current_row.get_value

        self._save_row = BoxflatButtonRow("Save preset", "Save")
        self._add_row(self._save_row)
        self._current_row.subscribe(self._save_preset)
        self._current_row.set_active(False)
        self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_active(e.get_text_length()))

        self.add_preferences_group("Presets list")
        self._add_row(BoxflatButtonRow("Read Preset", "Load"))


    def _save_preset(self, *args):
        pm = MozaPresetHandler(self._cm)
        pm.set_path(f"~/.config/boxflat/presets")
        pm.set_name(self._name_row.get_text())

        for key, method in self._includes.items():
            if method():
                pm.add_device_settings(key)

        pm.save_preset()


    def read_preset(self, *args):
        pm = MozaPresetHandler(self._cm)
        pm._load_preset()


