from .settings_panel import SettingsPanel
from .base import BaseSettings
from .wheel import WheelSettings
from .home import HomeSettings
from .pedals import PedalsSettings
from .h_pattern import HPatternSettings
from .sequential import SequentialSettings
from .handbrake import HandbrakeSettings
from boxflat.connection_manager import MozaConnectionManager

_panels = {}

def prepare_panels(button_callback, data_path: str, dry_run: bool) -> dict:
    cm = MozaConnectionManager(f"{data_path}/serial.yml", dry_run)

    _panels["Home"] = HomeSettings(button_callback, dry_run)
    # _panels["Base"] = BaseSettings(button_callback, cm)
    # _panels["Wheel"] = WheelSettings(button_callback, cm)
    # _panels["Pedals"] = PedalsSettings(button_callback, cm)
    # _panels["H-Pattern Shifter"] = HPatternSettings(button_callback, cm)
    _panels["Sequential Shifter"] = SequentialSettings(button_callback, cm)
    _panels["Handbrake"] = HandbrakeSettings(button_callback, cm)

    # TODO: Add Dash,Hub and other settings panel

    cm.refresh()

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
