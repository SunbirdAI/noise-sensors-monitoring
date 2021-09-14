from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class Sensor:
    deviceId: str
    dbLevel: float
    connected: bool
    longitude: float
    latitude: float
    batteryLevel: float
    sigStrength: float
    DataBalance: float

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)
    
    def to_dict(self):
        return asdict(self)
