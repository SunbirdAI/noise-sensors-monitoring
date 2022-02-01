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
    DataBalance: float = 0.0
    connected: bool = True
    longitude: float = 0
    latitude: float = 0

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

    def to_dict(self):
        return asdict(self)


@dataclass
class AggregateSensorMetric:
    device: str
    db_level: int
    # minDbLevel: float TODO: Add these later, when they're implemented in the API
    # maxDbLevel: float
    sig_strength: int
    last_rec: int
    last_upl: int
    panel_voltage: int
    battery_voltage: int
    data_balance: int

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

    def to_dict(self):
        return asdict(self)
