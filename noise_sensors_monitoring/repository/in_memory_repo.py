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
        self.send_data_to_api(sensor.deviceId)

    def send_data_to_api(self, device_id: str):
        # check if there is enough data (i.e ==60 records)
        if len(self.metrics[device_id]) < 60:
            return
        # calculate the average db level, max db level
        aggregate_metric = self.calculate_aggregate_stats(device_id)

        # send data to api
        self.send_data(aggregate_metric)

        # reset metrics for device to empty list
        self.metrics[device_id] = []

    def calculate_aggregate_stats(self, device_id: str) -> AggregateSensorMetric:
        sensor_metrics = self.metrics[device_id]

        # calculate average DB level
        db_avg = 0
        max_db_level = 0
        exceedances = 0
        for sensor in sensor_metrics:
            db_avg += sensor.dbLevel
            max_db_level = max(max_db_level, sensor.dbLevel)
            if sensor.dbLevel >= 70:
                exceedances += 1

        db_avg //= len(sensor_metrics)
        last_sensor = sensor_metrics[-1]
        return AggregateSensorMetric.from_dict({
            "device": device_id,
            "db_level": last_sensor.dbLevel,
            "avg_db_level": db_avg,
            "max_db_level": max_db_level,
            "no_of_exceedances": exceedances,
            "sig_strength": last_sensor.sigStrength,
            "last_rec": last_sensor.LastRec,
            "last_upl": last_sensor.LastUpl,
            "panel_voltage": last_sensor.pV,
            "battery_voltage": last_sensor.bV,
            "data_balance": last_sensor.DataBalance
        })

    @staticmethod
    def send_data(aggregate_metric: AggregateSensorMetric):
        url = f"{BASE_URL}/device_metrics/"
        payload = json.dumps(aggregate_metric.to_dict())
        headers = {
            'Content-Type': 'application/json'
        }
        requests.request("POST", url, headers=headers, data=payload)

    def get_latest_sensor_reading(self) -> Sensor:
        pass
