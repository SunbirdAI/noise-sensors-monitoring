from noise_sensors_monitoring.domain.sensor import Sensor
from noise_sensors_monitoring.repository.time_series_repo_interface import SensorReadingRepo

from noise_sensors_monitoring.requests.sensor_reading import Request
from noise_sensors_monitoring.responses import (
    ResponseSuccess, ResponseFailure, ResponseTypes, build_response_from_invalid_request
)


def add_new_sensor_reading(request: Request, repo: SensorReadingRepo):
    if not request:
        return build_response_from_invalid_request(request)
    try:
        repo.add_new_sensor_reading(request.request_dict)
        return ResponseSuccess("Successfully added the new sensor reading")
    except Exception as exc:
        return ResponseFailure(ResponseTypes.SYSTEM_ERROR, exc)


def get_latest_sensor_reading(repo: SensorReadingRepo) -> Sensor:
    # TODO: add error handling e.g for when there aren't any sensor readings
    return repo.get_latest_sensor_reading()
