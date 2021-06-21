from noise_sensors_monitoring.domain.sensor import Sensor


def test_sensor_model_init():
    sensor = Sensor(
        deviceId="SB1001",
        dbLevel=76,
        connected=True,
        longitude=1.034,
        latitude=0.564,
        batteryLevel=30,
        sigStrength=26
    )

    assert sensor.deviceId == "SB1001"
    assert sensor.dbLevel == 76
    assert sensor.connected == True
    assert sensor.longitude == 1.034
    assert sensor.latitude == 0.564
    assert sensor.batteryLevel == 30
    assert sensor.sigStrength == 26

def test_from_dict_init():
    init_dict = {
        "deviceId": "SB1001",
        "dbLevel": 76,
        "connected": True,
        "longitude": 1.034,
        "latitude": 0.564,
        "batteryLevel": 30,
        "sigStrength": 26
    }

    sensor = Sensor.from_dict(init_dict)

    assert sensor.deviceId == "SB1001"
    assert sensor.dbLevel == 76
    assert sensor.connected == True
    assert sensor.longitude == 1.034
    assert sensor.latitude == 0.564
    assert sensor.batteryLevel == 30
    assert sensor.sigStrength == 26
