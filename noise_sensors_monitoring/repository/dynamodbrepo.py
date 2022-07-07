from datetime import datetime
from typing import Dict
import boto3
from noise_sensors_monitoring.domain.sensor import Sensor
from noise_sensors_monitoring.repository.time_series_repo_interface import SensorReadingRepo

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('sensor-metrics')


class DynamodbRepo(SensorReadingRepo):

    def __init__(self):
        pass

    def add_new_sensor_reading(self, sensor_reading: Dict):
        sensor = Sensor.from_dict(sensor_reading)
        data = {
            'deviceId': sensor.deviceId,
            'pV': sensor.pV,
            'bV': sensor.bV,
            'signalStrength': sensor.sigStrength,
            'dataBalance': sensor.DataBalance,
            'dbLevel': sensor.dbLevel,
            'lastRecorded': sensor.LastRec,
            'lastUploaded': sensor.LastUpl,
            'date': str(datetime.now())
        }
        table.put_item(Item=data)

    def get_latest_sensor_reading(self) -> Sensor:
        pass
