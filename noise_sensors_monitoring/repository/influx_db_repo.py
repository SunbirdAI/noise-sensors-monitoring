from noise_sensors_monitoring.repository.time_series_repo_interface import SensorReadingRepo
from noise_sensors_monitoring.domain.sensor import Sensor

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

from datetime import datetime

MEASUREMENTS = ["BATTERY_LEVEL", "CONNECTED", "SIGNAL_STRENGTH", "DB_LEVEL"]


class InfluxDBRepo(SensorReadingRepo):

    def __init__(self, configuration):
        self.db_url = configuration['influx_url']
        self.db_token = configuration['influx_token']
        self.org = configuration['influx_org']
        self.bucket = configuration['influx_bucket']

        self.db_client = InfluxDBClient(url=self.db_url, token=self.db_token)
        self.write_api = self.db_client.write_api(write_options=ASYNCHRONOUS)

    def write_measurement(self, measurement: str, value: int, sensor_reading: Sensor):
        # TODO: Perhaps replace latitude and longitude with location
        point = Point(measurement) \
            .tag("deviceId", sensor_reading.deviceId) \
            .tag("latitude", sensor_reading.latitude) \
            .tag("longitude", sensor_reading.longitude) \
            .field(measurement.lower(), value) \
            .time(datetime.utcnow(), WritePrecision.NS)

        self.write_api.write(self.bucket, self.org, point)

    def add_new_sensor_reading(self, sensor_reading: Sensor):
        self.write_measurement(MEASUREMENTS[0], sensor_reading.batteryLevel, sensor_reading)
        self.write_measurement(MEASUREMENTS[1], sensor_reading.connected, sensor_reading)
        self.write_measurement(MEASUREMENTS[2], sensor_reading.sigStrength, sensor_reading)
        self.write_measurement(MEASUREMENTS[3], sensor_reading.dbLevel, sensor_reading)

    def get_latest_sensor_reading(self) -> Sensor:
        pass
