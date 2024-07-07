from src.panels.settings_panel import SettingsPanel
from src.panels.base import BaseSettings
from src.panels.wheel import WheelSettings
from src.panels.home import HomeSettings
from src.panels.pedals import PedalsSettings
from src.panels.h_pattern import HPatternSettings
from src.panels.sequential import SequentialSettings
from src.panels.handbrake import HandbrakeSettings

_panels = {}

def prepare_panels(button_callback) -> dict:
    _panels["Home"] = HomeSettings(button_callback)
    _panels["Base"] = BaseSettings(button_callback)
    _panels["Wheel"] = WheelSettings(button_callback)
    # _panels["Pedals"] = PedalsSettings(button_callback)
    _panels["H-Pattern Shifter"] = HPatternSettings(button_callback)
    _panels["Sequential Shifter"] = SequentialSettings(button_callback)
    _panels["Handbrake"] = HandbrakeSettings(button_callback)

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
