from noise_sensors_monitoring.domain.sensor import Sensor
from noise_sensors_monitoring.repository.time_series_repo_interface import SensorReadingRepo

from typing import Dict


def add_new_sensor_reading(sensor_reading: Dict, repo: SensorReadingRepo):
    repo.add_new_sensor_reading(sensor_reading)


def get_latest_sensor_reading(repo: SensorReadingRepo) -> Sensor:
    # TODO: add error handling e.g for when there aren't any sensor readings
    return repo.get_latest_sensor_reading()
