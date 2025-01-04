from enum import Enum, auto

class DeviceType(Enum):
    BASE       = auto()
    PEDALS     = auto()
    SEQUENTIAL = auto()
    HPATTERN   = auto()
    HANDBRAKE  = auto()
    WHEEL      = auto()
    GENERIC    = auto()
