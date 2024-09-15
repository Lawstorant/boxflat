from .connection_manager import MozaConnectionManager

class MozaPresetHandler():
    def __init__(self, connection_manager: MozaConnectionManager):
        self._settings = []
        self._cm = connection_manager


    def append_setting(self, setting_name: str):
        self._settings.append(setting_name)


    def add_settings(self, *setting_names: str):
        self._settings.extend(setting_names)


    def remove_setting(self, setting_name: str):
        self._settings.remove(setting_name)


    def reset_settings(self):
        self._settings.clear()


    def save_preset(self) -> bool:
        return True


    def read_preset(self) -> bool:
        return True
