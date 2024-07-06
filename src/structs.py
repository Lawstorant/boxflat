from gi.repository import GObject

PICKER_COLORS = [
    "",
    ""
]

class ComboRow(GObject.Object):
    __gtype_name__ = 'ComboRow'

    def __init__(self, row_id: str, row_name: str):
        super().__init__()

        self._row_id = row_id
        self._row_name = row_name

    @GObject.Property
    def row_id(self) -> str:
        return self._row_id

    @GObject.Property
    def row_name(self) -> str:
        return self._row_name

class BaseImportantSettings():
    rotation = 540
    ffb_strength = 100

class BaseBasicSettings():
    speed = 80
    spring = 0
    damper = 10

class BaseAdvancedSettings():
    reversal = False
    torque = 100
    protection = False
    protection_inertia = 2800
    inertia = 150
    friction = 30
    speed_damping_level = 0
    speed_damping_point = 200

class BaseEqualizerSettings():
    pass

class BaseFFBCurveSettings():
    pass

class BaseMiscSettings():
    pass

