import yaml
from os import path, makedirs
from threading import Lock
from typing import Any

class PersistentSettingsHandler():
    def __init__(self, config_path: str) -> None:
        self._settings_path = path.expanduser(config_path)
        self._settings_file = path.join(self._settings_path, "settings.yml")
        self._file_lock = Lock()

        if not path.exists(self._settings_path):
            makedirs(self._settings_path)

        if not path.isfile(self._settings_file):
            open(self._settings_file, "w").close()


    def _get_file_contents(self) -> Any:
        with self._file_lock, open(self._settings_file, "r") as file:
            return yaml.safe_load(file) or {}


    def _write_to_file(self, settings_data: Any) -> None:
        with self._file_lock, open(self._settings_file, "w") as file:
            yaml.safe_dump(settings_data, file)


    def write_setting(self, setting_value, setting_name: str) -> None:
        data = self._get_file_contents()
        data[setting_name] = setting_value
        self._write_to_file(data)


    def read_setting(self, setting_name: str) -> Any:
        data = self._get_file_contents()
        if setting_name in data:
            return data[setting_name]
        return None


    def get_path(self) -> str:
        return self._settings_path
