from typing import Dict, Optional

import pytest

from noise_sensors_monitoring.domain.sensor import Sensor
from noise_sensors_monitoring.repository.time_series_repo_interface import (
    SensorReadingRepo,
)
from noise_sensors_monitoring.requests.sensor_reading import (
    build_sensor_reading_request,
)
from noise_sensors_monitoring.use_cases.sensor_reading import (
    add_new_sensor_reading,
    get_latest_sensor_reading,
)


class InMemorySensorDb(SensorReadingRepo):
    def __init__(self) -> None:
        self.data = []

    def add_new_sensor_reading(self, sensor_reading: Dict):
        self.data.append(sensor_reading)

    def get_latest_sensor_reading(self) -> Optional[Sensor]:
        if len(self.data) == 0:
            # throw an error
            return None
        return Sensor.from_dict(self.data[-1])


@pytest.fixture
def sensor_repo() -> InMemorySensorDb:
    return InMemorySensorDb()


def test_new_sensor_reading(sensor_repo):
    repo: SensorReadingRepo = sensor_repo
    sensor_reading = Sensor(
        deviceId="SB1001",
        dbLevel=76.0,
        connected=True,
        longitude=1.034,
        latitude=0.564,
        bV=30,
        pV=30,
        LastRec=3,
        LastUpl=2,
        sigStrength=26.0,
        DataBalance=67,
    )

    request = build_sensor_reading_request(sensor_reading.to_dict())

    response = add_new_sensor_reading(request, repo, repo)

    latest_sensor = get_latest_sensor_reading(repo)

    assert bool(response) is True
    assert sensor_reading == latest_sensor
    assert response.value == "Successfully added the new sensor reading"
