from enum import Enum, auto

class DeviceType(Enum):
    WHEELBASE  = auto()
    PEDALS     = auto()
    SEQUENTIAL = auto()
    HPATTERN   = auto()
    HANDBRAKE  = auto()
    WHEEL      = auto()
    GENERIC    = auto()
