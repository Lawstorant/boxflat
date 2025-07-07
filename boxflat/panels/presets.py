# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from .settings_panel import SettingsPanel
from .h_pattern import HPatternSettings
from .stalks import StalksSettings
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.preset_handler import MozaPresetHandler
from boxflat.settings_handler import SettingsHandler
import os
from threading import Thread
from time import sleep

from gi.repository.Gio import Notification, NotificationPriority

class PresetSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, settings: SettingsHandler,
                 hpattern: HPatternSettings, stalks: StalksSettings):
        self._settings = settings

        self._hpattern = hpattern
        self._stalks = stalks

        self._includes = {}
        self._name_row = Adw.EntryRow()
        self._name_row.set_title("Preset Name")

        self._save_row = None
        self._presets_path = os.path.join(self._settings.get_path(), "presets")
        self._presets_list_group = None
        self._presets = []
        self._default_preset = None
        super().__init__("Presets", button_callback, connection_manager)
        self.list_presets()

        if self._settings.read_setting("default-preset-on-startup"):
            Thread(target=self._load_default, args=[5], daemon=True).start()


    def prepare_ui(self):
        self.add_preferences_group("Saving")
        self._current_group.set_description("Doesn't overwrite unavailable devices")
        self._add_row(self._name_row)

        expander = Adw.ExpanderRow(title="Include Devices")
        self._add_row(expander)

        row = BoxflatSwitchRow("Base")
        expander.add_row(row)
        row.set_value(1)
        row.set_value(self._settings.read_setting("presets-include-base"))
        row.subscribe(self._settings.write_setting, "presets-include-base")
        self._cm.subscribe_connected("base-limit", row.set_active, 1, True)
        self._includes["base"] = row.get_value

        row = BoxflatSwitchRow("Dash")
        expander.add_row(row)
        row.set_value(1)
        row.set_value(self._settings.read_setting("presets-include-dash"))
        row.subscribe(self._settings.write_setting, "presets-include-dash")
        self._cm.subscribe_connected("dash-rpm-indicator-mode", row.set_active, 1, True)
        self._includes["dash"] = row.get_value

        row = BoxflatSwitchRow("Dash Colors")
        expander.add_row(row)
        row.set_value(1)
        row.set_value(self._settings.read_setting("presets-include-dash-color"))
        row.subscribe(self._settings.write_setting, "presets-include-dash-color")
        self._cm.subscribe_connected("dash-rpm-indicator-mode", row.set_active, 1, True)
        self._includes["dash-colors"] = row.get_value

        row = BoxflatSwitchRow("Wheel")
        expander.add_row(row)
        row.set_value(1)
        row.set_value(self._settings.read_setting("presets-include-wheel"))
        row.subscribe(self._settings.write_setting, "presets-include-wheel")
        self._cm.subscribe_connected("wheel-rpm-indicator-mode", row.set_active, 1, True)
        self._includes["wheel"] = row.get_value

        row = BoxflatSwitchRow("Wheel Colors")
        expander.add_row(row)
        row.set_value(0)
        row.set_value(self._settings.read_setting("presets-include-wheel-colors"))
        row.subscribe(self._settings.write_setting, "presets-include-wheel-colors")
        self._cm.subscribe_connected("wheel-rpm-indicator-mode", row.set_active, 1, True)
        self._includes["wheel-colors"] = row.get_value

        row = BoxflatSwitchRow("Pedals")
        expander.add_row(row)
        row.set_value(1)
        row.set_value(self._settings.read_setting("presets-include-pedals"))
        row.subscribe(self._settings.write_setting, "presets-include-pedals")
        self._cm.subscribe_connected("pedals-throttle-dir", row.set_active, 1, True)
        self._includes["pedals"] = row.get_value

        row = BoxflatSwitchRow("H-Pattern Shifter")
        expander.add_row(row)
        row.set_value(0)
        row.set_active(0, off_when_inactive=True)
        row.set_value(self._settings.read_setting("presets-include-hpattern"))
        row.subscribe(self._settings.write_setting, "presets-include-hpattern")
        self._hpattern.subscribe("active", row.set_active, 0, True)
        self._includes["hpattern"] = row.get_value

        row = BoxflatSwitchRow("Sequential Shifter")
        expander.add_row(row)
        row.set_value(1)
        row.set_value(self._settings.read_setting("presets-include-sequential"))
        row.subscribe(self._settings.write_setting, "presets-include-sequential")
        self._cm.subscribe_connected("sequential-paddle-sync", row.set_active, 1, True)
        self._includes["sequential"] = row.get_value

        row = BoxflatSwitchRow("Handbrake")
        expander.add_row(row)
        row.set_value(1)
        row.set_value(self._settings.read_setting("presets-include-handbrake"))
        row.subscribe(self._settings.write_setting, "presets-include-handbrake")
        self._cm.subscribe_connected("handbrake-direction", row.set_active, 1, True)
        self._includes["handbrake"] = row.get_value

        row = BoxflatSwitchRow("Multifunction Stalks")
        expander.add_row(row)
        row.set_value(0)
        row.set_active(0, off_when_inactive=True)
        row.set_value(self._settings.read_setting("presets-include-stalks"))
        row.subscribe(self._settings.write_setting, "presets-include-stalks")
        self._stalks.subscribe("active", row.set_active, 0, True)
        self._includes["stalks"] = row.get_value

        self._observer = process_handler.ProcessObserver()
        self._observer.subscribe("no-games", self._load_default)

        if Adw.get_minor_version() >= 6:
            self._save_row = Adw.ButtonRow(title="Save")
            self._save_row.add_css_class("suggested-action")
            self._save_row.set_end_icon_name("document-save-symbolic")
            self._add_row(self._save_row)
            self._save_row.connect("activated", self._save_preset)
            self._save_row.connect("activated", lambda v: expander.set_expanded(False))
            self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_sensitive(e.get_text_length()))
            self._save_row.set_sensitive(False)

        # compatibility with libadwaita older than 1.6
        else:
            self._save_row = BoxflatButtonRow("Save preset", "Save")
            self._add_row(self._save_row)
            self._current_row.subscribe(self._save_preset)
            self._current_row.subscribe(lambda v: expander.set_expanded(False))
            self._current_row.set_active(False)
            self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_active(e.get_text_length()))



    def _save_preset(self, *rest):
        self.show_toast(f"Saving preset \"{self._name_row.get_text()}\"", 1.5)
        self._save_row.set_sensitive(False)

        pm = MozaPresetHandler(self._cm)
        pm.set_path(self._presets_path)
        pm.set_name(self._name_row.get_text())

        pm.subscribe(self.list_presets)
        pm.subscribe(self._activate_save)

        for key, method in self._includes.items():
            if method():
                pm.add_device_settings(key)

        pm.set_hpattern_settings(self._hpattern.get_settings())
        pm.set_stalks_settings(self._stalks.get_settings())

        pm.save_preset()


    def _activate_save(self, *rest):
        GLib.idle_add(self._save_row.set_sensitive, True)


    def _load_preset(self, preset_name: str, automatic=False, default=False):
        preset_name = preset_name.removesuffix(".yml")
        print(f"Loading preset \"{preset_name}\"")

        GLib.idle_add(self._name_row.set_text, preset_name)
        pm = MozaPresetHandler(self._cm)
        pm.set_path(self._presets_path)
        pm.set_name(preset_name)
        pm.load_preset(self._hpattern, self._stalks)

        if not automatic and not default:
            return

        notif = Notification()
        app = self._application

        notif.set_title(f"Detected: {pm.get_linked_process()}" if automatic else "No games detected")
        notif.set_body(f"Loading {"default" if default else ""} preset: {preset_name}")
        notif.set_priority(NotificationPriority.NORMAL)

        app.send_notification("preset", notif)
        sleep(10)
        app.withdraw_notification("preset")


    def _delete_preset(self, preset_name: str, *args):
        filepath = os.path.join(self._presets_path, preset_name)

        if not os.path.isfile(filepath):
            filepath += ".yml"

        if not os.path.isfile(filepath):
            return

        os.remove(filepath)
        self.list_presets()


    def list_presets(self, *rest):
        self.remove_preferences_group(self._presets_list_group)

        if not os.path.exists(self._presets_path):
            return

        files = os.listdir(self._presets_path)
        files.sort()

        self.add_preferences_group("Preset list")
        self._presets_list_group = self._current_group

        pm = MozaPresetHandler(None)
        pm.set_path(self._presets_path)
        self._observer.deregister_all_processes()
        self._default_preset = None

        for file in files:
            filepath = os.path.join(self._presets_path, file)
            if not os.path.isfile(filepath):
                continue

            preset_name = file.removesuffix(".yml")
            row = BoxflatButtonRow(preset_name)
            row.add_button("Load", self._load_preset, file)
            row.add_button("Settings", self._show_preset_dialog, file)
            # row.add_button("Delete", self._delete_preset, file).add_css_class("destructive-action")
            self._add_row(row)

            pm.set_name(file)
            process = pm.get_linked_process()
            self._observer.register_process(process)
            self._observer.subscribe(process, self._load_preset, preset_name, True)

            if pm.is_default():
                print(f"Found default preset: {preset_name}")
                self._default_preset = preset_name
                self._presets_list_group.set_description(f"Default: {preset_name}")


    def _handle_preset_save(self, file_name: str):
        if not os.path.exists(self._presets_path):
            return

        files = os.listdir(self._presets_path)
        pm = MozaPresetHandler(None)
        pm.set_path(self._presets_path)
        pm.set_name(file_name)

        if not pm.is_default():
            self.list_presets()
            return

        for file in files:
            if file_name in file:
                continue

            filepath = os.path.join(self._presets_path, file)
            if not os.path.isfile(filepath):
                continue

            pm.set_name(file)
            pm.set_default(False)

        self.list_presets()


    def _show_preset_dialog(self, file_name: str):
        if not file_name:
            return

        if file_name == "":
            return

        dialog = BoxflatPresetDialog(self._presets_path, file_name)
        dialog.subscribe("save", self._handle_preset_save)
        dialog.subscribe("delete", self._delete_preset)
        dialog.present(self._content)


    def _load_default(self, delay: int=0) -> None:
        if not self._default_preset:
            print("No default preset to load")
            return

        if delay > 0:
            sleep(delay)

        print(f"Loading default preset: {self._default_preset}")
        self._load_preset(self._default_preset, default=True)
