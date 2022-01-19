from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class Sensor:
    deviceId: str
    dbLevel: float
    bV: float
    pV: float
    LastRec: float
    LastUpl: float
    sigStrength: float
    DataBalance: float = 0
    connected: bool = True
    longitude: float = 0
    latitude: float = 0

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)
    
    def to_dict(self):
        return asdict(self)
