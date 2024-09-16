from .settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.preset_handler import MozaPresetHandler
import os

class PresetSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._includes = {}
        self._name_row = Adw.EntryRow()
        self._name_row.set_title("Preset Name")
        self._save_row = None
        self._presets_path = os.path.expanduser("~/.config/boxflat/presets")
        self._presets_list_group = None
        self._presets = []
        super().__init__("Presets", button_callback, connection_manager)
        self.list_presets()


    def prepare_ui(self) -> None:
        self.add_preferences_group("Saving")
        self._add_row(self._name_row)

        self._add_row(BoxflatSwitchRow("Include Base Settings"))
        self._append_sub_connected("base-limit", self._current_row.set_active, 1)
        self._includes["base"] = self._current_row.get_value

        self._add_row(BoxflatSwitchRow("Include Wheel Settings"))
        self._append_sub_connected("wheel-stick-mode", self._current_row.set_active, 1)
        self._includes["wheel"] = self._current_row.get_value

        self._add_row(BoxflatSwitchRow("Include Pedals Settings"))
        self._append_sub_connected("pedals-throttle-dir", self._current_row.set_active, 1)
        self._includes["pedals"] = self._current_row.get_value

        self._add_row(BoxflatSwitchRow("Include Handbrake Settings"))
        self._append_sub_connected("handbrake-direction", self._current_row.set_active, 1)
        self._includes["handbrake"] = self._current_row.get_value

        self._save_row = BoxflatButtonRow("Save preset", "Save")
        self._add_row(self._save_row)
        self._current_row.subscribe(self._save_preset)
        self._current_row.set_active(False)
        self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_active(e.get_text_length()))

        self.add_preferences_group("Preset list")
        self._presets_list_group = self._current_group


    def _save_preset(self, *args):
        pm = MozaPresetHandler(self._cm)
        pm.set_path(self._presets_path)
        pm.set_name(self._name_row.get_text())
        pm.set_callback(self.list_presets)

        for key, method in self._includes.items():
            if method():
                pm.add_device_settings(key)

        pm.save_preset()
        self.list_presets()


    def _load_preset(self, preset_name: str, *args):
        print(f"Loading preset {preset_name}")

        pm = MozaPresetHandler(self._cm)
        pm.set_path(self._presets_path)
        pm.set_name(preset_name)
        pm.set_callback(self.list_presets)
        pm.load_preset()


    def _delete_preset(self, value, preset_name: str, *args):
        filepath = os.path.join(self._presets_path, preset_name)

        if not os.path.isfile(filepath):
            filepath += ".yml"

        if not os.path.isfile(filepath):
            return

        os.remove(filepath)
        self.list_presets()


    def list_presets(self):
        if not self._presets_list_group:
            return

        self._presets_list_group.clear_children()

        files = []
        if os.path.exists(self._presets_path):
            files = os.listdir(self._presets_path)

        files.sort()
        for file in files:
            filepath = os.path.join(self._presets_path, file)
            if os.path.isfile(filepath):
                row = BoxflatButtonRow(file.removesuffix(".yml"))
                row.add_button("Load", self._load_preset, file)
                row.add_button("Delete")
                self._presets_list_group.add(row)
                row.subscribe(self._delete_preset, file)

