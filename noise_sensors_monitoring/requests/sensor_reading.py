from typing import Optional, Dict

from noise_sensors_monitoring.requests.generic_requests import Request, InvalidRequest, ValidRequest

REQUIRED_FIELDS = ["deviceId", "dbLevel", "connected", "longitude", "latitude", "batteryLevel", "sigStrength"]
REQUIRED_TYPES = {
    "deviceId": str,
    "dbLevel": int,
    "connected": bool,
    "longitude": float,
    "latitude": float,
    "batteryLevel": int,
    "sigStrength": int
}
TYPE_TO_WORD = {
    str: "string",
    int: "integer",
    bool: "boolean",
    float: "floating point"
}


def build_sensor_reading_request(sensor_reading_dict: Optional[Dict] = None) -> Request:
    invalid_req = InvalidRequest(sensor_reading_dict)
    if sensor_reading_dict is None:
        invalid_req.add_error("No data", "The sensor reading has no data")
        return invalid_req

    for field in REQUIRED_FIELDS:
        if field not in sensor_reading_dict:
            invalid_req.add_error("Missing values", f"{field} is required.")

    for (key, value) in sensor_reading_dict.items():
        if key not in REQUIRED_FIELDS:
            invalid_req.add_error("Invalid field", f"{key} is not a valid field for sensor data")
        elif type(value) != REQUIRED_TYPES[key]:
            req_type = TYPE_TO_WORD[REQUIRED_TYPES[key]]
            invalid_req.add_error("Invalid type", f"Field '{key}' should have {req_type} data type.")

    if invalid_req.has_errors():
        return invalid_req

    return ValidRequest(sensor_reading_dict)
