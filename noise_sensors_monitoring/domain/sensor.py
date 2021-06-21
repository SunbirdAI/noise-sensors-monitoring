from dataclasses import dataclass

@dataclass
class Sensor:
    deviceId: str
    dbLevel: int
    connected: bool
    longitude: float
    latitude: float
    batteryLevel: int
    sigStrength: int
