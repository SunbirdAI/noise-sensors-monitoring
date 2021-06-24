import pytest
from noise_sensors_monitoring.domain.sensor import Sensor
from noise_sensors_monitoring.repository.time_series_repo_interface import SensorReadingRepo
from noise_sensors_monitoring.use_cases.sensor_reading import add_new_sensor_reading, get_latest_sensor_reading



class InMemorySensorDb(SensorReadingRepo):
    def __init__(self) -> None:
        self.data = []
    
    def add_new_sensor_reading(self, sensor_reading: Sensor):
        self.data.append(sensor_reading.to_dict())
    
    def get_latest_sensor_reading(self) -> Sensor:
        if len(self.data) == 0:
            # throw an error
            return None
        return Sensor.from_dict(self.data[-1])

@pytest.fixture
def sensor_repo() -> InMemorySensorDb:
    return InMemorySensorDb()


def test_new_sensor_reading(sensor_repo): 
    repo: SensorReadingRepo = sensor_repo
    sensor = Sensor(
        deviceId="SB1001",
        dbLevel=76,
        connected=True,
        longitude=1.034,
        latitude=0.564,
        batteryLevel=30,
        sigStrength=26
    )
    
    add_new_sensor_reading(sensor, repo)

    latest_sensor = get_latest_sensor_reading(repo)

    assert sensor == latest_sensor
