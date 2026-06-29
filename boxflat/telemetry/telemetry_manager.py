import enum

from boxflat.telemetry.assetto_corsa_rally import AssettoCorsaRally
from boxflat.telemetry.dirt_rally_2 import DirtRally2


class Telemetries(enum.Enum):
    acr = AssettoCorsaRally
    dr2 = DirtRally2


def get_telemetries():
    telemetries = []
    for telemetry in Telemetries:
        telemetries.append((telemetry.name, telemetry.value))
    return telemetries

def telemetry_from_game_name(game_name: str):
    for telemetry in Telemetries:
        if telemetry.value.GAME_NAME == game_name:
            return telemetry.value()
    return None
