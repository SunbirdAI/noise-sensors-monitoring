from abc import ABC
from abc import abstractmethod
from noise_sensors_monitoring.domain.sensor import Sensor


class SensorReadingRepo(ABC):
    @abstractmethod
    def add_new_sensor_reading(sensor_reading: Sensor):
        '''Adds a new sensor reading'''
        pass

    @abstractmethod
    def get_latest_sensor_reading() -> Sensor:
        '''Returns the latest sensor reading'''
        pass
