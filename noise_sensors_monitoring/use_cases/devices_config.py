from noise_sensors_monitoring.repository.devices_repo import DevicesRepo
from noise_sensors_monitoring.requests.generic_requests import Request
from noise_sensors_monitoring.responses import (
    ResponseFailure,
    ResponseSuccess,
    ResponseTypes,
    build_response_from_invalid_request,
)


def get_device_config(request: Request, repo: DevicesRepo):
    if not request:
        return build_response_from_invalid_request(request)

    device_config = repo.get_device_configuration_by_imei(request.request_dict)
    if "errors" in device_config:
        return ResponseFailure(
            ResponseTypes.INVALID_INPUT_ERROR, device_config["errors"]
        )
    else:
        return ResponseSuccess(device_config)
