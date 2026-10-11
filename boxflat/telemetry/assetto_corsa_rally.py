from boxflat.telemetry.base_telemetry import MmapTelemetry


class AssettoCorsaRally(MmapTelemetry):
    GAME_NAME = "Assetto Corsa Rally"
    PHYSICS_PATH = "/dev/shm/acpmf_physics" # mirror by e.g. DataLink needed
    PHYSICS_SIZE = 800

    OFFSET_RPM = 20
    OFFSET_CURRENT_MAX_RPM = 588
