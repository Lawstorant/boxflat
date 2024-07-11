from boxflat.panels.settings_panel import SettingsPanel
from boxflat.panels.base import BaseSettings
from boxflat.panels.wheel import WheelSettings
from boxflat.panels.home import HomeSettings
from boxflat.panels.pedals import PedalsSettings
from boxflat.panels.h_pattern import HPatternSettings
from boxflat.panels.sequential import SequentialSettings
from boxflat.panels.handbrake import HandbrakeSettings
from boxflat.connection_manager import MozaConnectionManager

_panels = {}

def prepare_panels(button_callback, data_path: str, dry_run: bool) -> dict:
    cm = MozaConnectionManager(f"{data_path}/serial.yml", dry_run)

    _panels["Home"] = HomeSettings(button_callback, dry_run)
    # _panels["Base"] = BaseSettings(button_callback, cm)
    # _panels["Wheel"] = WheelSettings(button_callback, cm)
    # _panels["Pedals"] = PedalsSettings(button_callback, cm)
    # _panels["H-Pattern Shifter"] = HPatternSettings(button_callback, cm)
    # _panels["Sequential Shifter"] = SequentialSettings(button_callback, cm)
    _panels["Handbrake"] = HandbrakeSettings(button_callback, cm)

    # TODO: Add Dash,Hub and other settings panel

    return _panels

def activate_default() -> SettingsPanel:
    for panel in _panels.values():
        panel.button.set_active(False)

    _panels["Home"].button.set_active(True)
    return _panels["Home"]

def panels() -> dict:
    return _panels

def buttons() -> list:
    buttons = []
    for panel in _panels.values():
        buttons.append(panel.button)

    return buttons
