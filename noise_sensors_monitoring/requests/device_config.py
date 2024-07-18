from typing import Dict, Optional

from noise_sensors_monitoring.requests.generic_requests import (
    InvalidRequest,
    ValidRequest,
)


def build_device_config_request(config_dict: Optional[Dict] = None):
    invalid_req = InvalidRequest(config_dict)
    if config_dict is None:
        invalid_req.add_error("No data", "The configuration request has no data")
        return invalid_req

    if "imei" not in config_dict:
        invalid_req.add_error("Missing values", "imei is required.")

    imei = str(config_dict["imei"])
    if len(imei) != 15 or not imei.isnumeric():
        invalid_req.add_error(
            "Invalid value", "The imei value should be a 15-digit numeric value"
        )

    if invalid_req.has_errors():
        return invalid_req

    return ValidRequest(config_dict)
