from noise_sensors_monitoring.requests.sensor_reading import build_sensor_reading_request


def test_build_request_without_data():
    request = build_sensor_reading_request()

    assert request.sensor_reading is None
    assert request.has_errors()
    assert request.errors[0]["type"] == "No data"
    assert bool(request) is False


def test_build_request_without_all_fields():
    request = build_sensor_reading_request({
        "deviceId": "SB1001",
        "dbLevel": 76
    })

    assert bool(request) is False
    assert request.has_errors()
    assert len(request.errors) == 5
    assert request.errors[0]["type"] == "Missing values"


def test_build_request_with_invalid_fields():
    request = build_sensor_reading_request({
        "deviceId": "SB1001",
        "dbLevel": 76,
        "connected": True,
        "longitude": 1.034,
        "latitude": 0.564,
        "batteryLevel": 30,
        "sigStrength": 26,
        "randomField": 26
    })

    assert bool(request) is False
    assert request.has_errors()
    assert len(request.errors) == 1
    assert request.errors[0]["type"] == "Invalid field"


def test_build_request_with_invalid_types():
    request = build_sensor_reading_request({
        "deviceId": "SB1001",
        "dbLevel": 76,
        "connected": 78,
        "longitude": 1.034,
        "latitude": 0.564,
        "batteryLevel": 30.9,
        "sigStrength": 26,
    })

    assert bool(request) is False
    assert request.has_errors()
    assert len(request.errors) == 2
    assert request.errors[0]["type"] == "Invalid type"
    assert request.errors[0]["message"] == "Field 'connected' should have boolean data type."


def test_build_valid_request():
    sensor_reading = {
        "deviceId": "SB1001",
        "dbLevel": 76,
        "connected": True,
        "longitude": 1.034,
        "latitude": 0.564,
        "batteryLevel": 30,
        "sigStrength": 26
    }
    request = build_sensor_reading_request(sensor_reading)

    assert bool(request) is True
    assert not request.has_errors()
    assert request.sensor_reading == sensor_reading
