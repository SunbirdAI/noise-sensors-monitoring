from datetime import datetime
from typing import Dict

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS

from noise_sensors_monitoring.domain.sensor import Sensor
from noise_sensors_monitoring.repository.time_series_repo_interface import (
    SensorReadingRepo,
)


class InfluxDBRepo(SensorReadingRepo):
    def __init__(self, configuration):
        self.db_url = configuration["influx_url"]
        self.db_token = configuration["influx_token"]
        self.org = configuration["influx_org"]
        self.bucket = configuration["influx_bucket"]

        self.db_client = InfluxDBClient(url=self.db_url, token=self.db_token)
        self.write_api = self.db_client.write_api(write_options=SYNCHRONOUS)

    def write_measurement(self, measurement: str, value: int, sensor_reading: Sensor):
        # TODO: Perhaps replace latitude and longitude with location
        point = Point(measurement).tag("deviceId", sensor_reading.deviceId)
        if sensor_reading.latitude != 0 and sensor_reading.longitude != 0:
            point = point.tag("latitude", sensor_reading.latitude).tag(
                "longitude", sensor_reading.longitude
            )
        point = point.field(measurement.lower(), value).time(
            datetime.utcnow(), WritePrecision.NS
        )

        try:
            self.write_api.write(self.bucket, self.org, point)
        except Exception as exc:
            # TODO: add proper logging for errors
            print(f"Failed to write {exc}")

    def add_new_sensor_reading(self, sensor_reading: Dict):
        sensor = Sensor.from_dict(sensor_reading)
        self.write_measurement("BATTERY_VOLTAGE", sensor.bV, sensor)
        self.write_measurement("PANEL_VOLTAGE", sensor.pV, sensor)
        self.write_measurement("SIGNAL_STRENGTH", sensor.sigStrength, sensor)
        self.write_measurement("DB_LEVEL", sensor.dbLevel, sensor)
        self.write_measurement("DATA_BALANCE", sensor.DataBalance, sensor)
        self.write_measurement("LAST_RECORDED", sensor.LastRec, sensor)
        self.write_measurement("LAST_UPLOADED", sensor.LastUpl, sensor)

    def get_latest_sensor_reading(self) -> Sensor:
        pass
