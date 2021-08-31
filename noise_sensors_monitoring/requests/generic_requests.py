from abc import abstractmethod, ABC
from typing import Dict, Optional


class Request(ABC):
    @abstractmethod
    def __init__(self, request_dict: Dict):
        """Receives a sensor reading for validation"""
        self.request_dict = request_dict
        self.errors = []

    @abstractmethod
    def __bool__(self):
        """True if the sensor_reading is valid. False if the sensor reading is invalid"""
        pass

    @abstractmethod
    def has_errors(self):
        pass


class InvalidRequest(Request):
    def __init__(self, request_dict: Optional[Dict]):
        self.request_dict = request_dict
        self.errors = []

    def has_errors(self):
        return len(self.errors) > 0

    def add_error(self, error_type: str, message: str):
        self.errors.append({"type": error_type, "message": message})

    def __bool__(self):
        return False


class ValidRequest(Request):
    def __init__(self, request_dict: Dict):
        self.request_dict = request_dict

    def __bool__(self):
        return True

    def has_errors(self):
        return False
