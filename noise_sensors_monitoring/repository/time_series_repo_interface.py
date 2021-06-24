from abc import ABC
from abc import abstractmethod
from noise_sensors_monitoring.domain.sensor import Sensor
from typing import Dict


class SensorReadingRepo(ABC):
    @abstractmethod
    def add_new_sensor_reading(self, sensor_reading: Dict):
        """Adds a new sensor reading"""
        pass

    @abstractmethod
    def get_latest_sensor_reading(self) -> Sensor:
        """Returns the latest sensor reading"""
        pass
