from noise_sensors_monitoring.requests.sensor_reading import Request


class ResponseTypes:
    INVALID_INPUT_ERROR = "InvalidInputError"
    SYSTEM_ERROR = "SystemError"
    SUCCESS = "Success"


class ResponseSuccess:
    def __init__(self, value=None):
        self.type = ResponseTypes.SUCCESS
        self.value = value

    def __bool__(self):
        return True


class ResponseFailure:
    def __init__(self, type_, message):
        self.type = type_
        self.message = self._format_message(message)

    def _format_message(self, msg):
        if isinstance(msg, Exception):
            return f"{msg.__class__.__name__}: {msg}"
        return msg

    def __bool__(self):
        return False

    @property
    def value(self):
        return {"type": self.type, "message": self.message}


def build_response_from_invalid_request(invalid_request: Request):
    message = "\n".join(
        [f"{err['type']}: {err['message']}" for err in invalid_request.errors]
    )

    return ResponseFailure(ResponseTypes.INVALID_INPUT_ERROR, message)
