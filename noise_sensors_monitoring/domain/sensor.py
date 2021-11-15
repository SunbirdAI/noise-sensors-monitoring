from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class Sensor:
    deviceId: str
    dbLevel: float
    connected: bool
    longitude: float
    latitude: float
    bV: float
    pV: float
    LastRec: float
    LastUpl: float
    sigStrength: float
    DataBalance: float

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)
    
    def to_dict(self):
        return asdict(self)
