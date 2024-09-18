from .settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.preset_handler import MozaPresetHandler
import os

class PresetSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager, config_path: str) -> None:
        self._includes = {}
        self._name_row = Adw.EntryRow()
        self._name_row.set_title("Preset Name")
        self._save_row = None
        self._presets_path = os.path.expanduser(os.path.join(config_path, "presets"))
        self._presets_list_group = None
        self._presets = []
        super().__init__("Presets", button_callback, connection_manager)
        self.list_presets()


    def prepare_ui(self) -> None:
        self.add_preferences_group("Saving")
        self._add_row(self._name_row)

        expander = Adw.ExpanderRow(title="Include Devices")
        self._add_row(expander)

        row = BoxflatSwitchRow("Base")
        expander.add_row(row)
        row.set_value(1)
        self._append_sub_connected("base-limit", row.set_active, 1, True)
        self._includes["base"] = row.get_value

        row = BoxflatSwitchRow("Wheel")
        expander.add_row(row)
        row.set_value(1)
        self._append_sub_connected("wheel-rpm-brightness", row.set_active, 1, True)
        self._includes["wheel"] = row.get_value

        row = BoxflatSwitchRow("Wheel Colors")
        expander.add_row(row)
        row.set_value(1)
        self._append_sub_connected("wheel-rpm-brightness", row.set_active, 1, True)
        self._includes["wheel-colors"] = row.get_value

        row = BoxflatSwitchRow("Pedals")
        expander.add_row(row)
        row.set_value(1)
        self._append_sub_connected("pedals-throttle-dir", row.set_active, 1, True)
        self._includes["pedals"] = row.get_value

        row = BoxflatSwitchRow("Sequential Shifter")
        expander.add_row(row)
        row.set_value(1)
        self._append_sub_connected("sequential-paddle-sync", row.set_active, 1, True)
        self._includes["sequential"] = row.get_value

        row = BoxflatSwitchRow("Handbrake")
        expander.add_row(row)
        row.set_value(1)
        self._append_sub_connected("handbrake-direction", row.set_active, 1, True)
        self._includes["handbrake"] = row.get_value

        self._save_row = BoxflatButtonRow("Save preset", "Save")
        self._add_row(self._save_row)
        self._current_row.subscribe(self._save_preset)
        self._current_row.subscribe(lambda v: expander.set_expanded(False))
        self._current_row.set_active(False)
        self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_active(e.get_text_length()))


    def _save_preset(self, button: Gtk.Button, *args):
        self.show_toast(f"Saving preset \"{self._name_row.get_text()}\"", 1.5)
        self._save_row.set_active(False)

        pm = MozaPresetHandler(self._cm)
        pm.set_path(self._presets_path)
        pm.set_name(self._name_row.get_text())
        pm.add_callback(self.list_presets)
        pm.add_callback(self._save_row.set_active)

        for key, method in self._includes.items():
            if method():
                pm.add_device_settings(key)

        pm.save_preset()


    def _load_preset(self, preset_name: str, *args):
        print(f"\nLoading preset {preset_name}")

        self._name_row.set_text(preset_name.removesuffix(".yml"))

        pm = MozaPresetHandler(self._cm)
        pm.set_path(self._presets_path)
        pm.set_name(preset_name)
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
        self.remove_preferences_group(self._presets_list_group)

        if not os.path.exists(self._presets_path):
            return

        files = os.listdir(self._presets_path)
        files.sort()

        self.add_preferences_group("Preset list")
        self._presets_list_group = self._current_group

        for file in files:
            filepath = os.path.join(self._presets_path, file)
            if os.path.isfile(filepath):
                row = BoxflatButtonRow(file.removesuffix(".yml"))
                row.add_button("Load", self._load_preset, file)
                row.add_button("Delete")
                row.subscribe(self._delete_preset, file)
                self._add_row(row)


