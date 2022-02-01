import os
import json
import requests
from dotenv import load_dotenv

from noise_sensors_monitoring.domain.sensor import Sensor, AggregateSensorMetric
from noise_sensors_monitoring.repository.time_series_repo_interface import SensorReadingRepo
from typing import Dict, List

load_dotenv()
BASE_URL = os.getenv('HTTP_APP_HOST')


class InMemoryRepo(SensorReadingRepo):

    def __init__(self):
        self.metrics: Dict[str, List[Sensor]] = {}

    def add_new_sensor_reading(self, sensor_reading: Dict):
        sensor = Sensor.from_dict(sensor_reading)
        if sensor.deviceId not in self.metrics:
            self.metrics[sensor.deviceId] = []

        self.metrics[sensor.deviceId].append(sensor)

    def send_data_to_api(self, device_id: str):
        # check if there is enough data (i.e ==60 records)
        # if there is, then calculate the average db level, max db level, min db level,
        # and the latest values for the rest of the metrics
        # send data to api
        # reset metrics for device to empty list
        pass

    def calculate_aggregate_stats(self, device_id: str) -> AggregateSensorMetric:
        sensor_metrics = self.metrics[device_id]

        # calculate average DB level
        db_avg = 0
        for sensor in sensor_metrics:
            db_avg += sensor.dbLevel

        db_avg //= len(sensor_metrics)
        last_sensor = sensor_metrics[-1]
        return AggregateSensorMetric.from_dict({
            "device": device_id,
            "db_level": db_avg,
            "sig_strength": last_sensor.sigStrength,
            "last_rec": last_sensor.LastRec,
            "last_upl": last_sensor.LastUpl,
            "panel_voltage": last_sensor.pV,
            "battery_voltage": last_sensor.bV,
            "data_balance": last_sensor.DataBalance
        })

    def send_data(self):
        pass

    def get_latest_sensor_reading(self) -> Sensor:
        pass
