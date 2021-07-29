from abc import ABC, abstractmethod
from typing import Optional, Dict

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


class Request(ABC):
    @abstractmethod
    def __init__(self, sensor_reading: Dict):
        """Receives a sensor reading for validation"""
        self.sensor_reading = sensor_reading
        self.errors = []

    @abstractmethod
    def __bool__(self):
        """True if the sensor_reading is valid. False if the sensor reading is invalid"""
        pass

    @abstractmethod
    def has_errors(self):
        pass


class SensorReadingInvalidRequest(Request):
    def __init__(self, sensor_reading: Optional[Dict]):
        self.sensor_reading = sensor_reading
        self.errors = []

    def has_errors(self):
        return len(self.errors) > 0

    def add_error(self, error_type: str, message: str):
        self.errors.append({"type": error_type, "message": message})

    def __bool__(self):
        return False


class SensorReadingValidRequest(Request):
    def __init__(self, sensor_reading: Dict):
        self.sensor_reading = sensor_reading

    def __bool__(self):
        return True

    def has_errors(self):
        return False


def build_sensor_reading_request(sensor_reading_dict: Optional[Dict]=None) -> Request:
    invalid_req = SensorReadingInvalidRequest(sensor_reading_dict)
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

    return SensorReadingValidRequest(sensor_reading_dict)
