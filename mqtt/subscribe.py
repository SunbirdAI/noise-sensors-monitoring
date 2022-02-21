import json
import os

from dotenv import load_dotenv

from json import JSONDecodeError

from noise_sensors_monitoring.repository.influx_db_repo import InfluxDBRepo
from noise_sensors_monitoring.use_cases.sensor_reading import add_new_sensor_reading
from noise_sensors_monitoring.requests.sensor_reading import build_sensor_reading_request

from noise_sensors_monitoring.requests.device_config import build_device_config_request
from noise_sensors_monitoring.repository.devices_repo import DevicesRepo
from noise_sensors_monitoring.repository.in_memory_repo import InMemoryRepo
from noise_sensors_monitoring.use_cases.devices_config import get_device_config

from mqtt.publish import publish_device_configuration

load_dotenv()

repo = InfluxDBRepo({
    "influx_url": os.environ["INFLUX_DB_URL"],
    "influx_token": os.environ["INFLUX_DB_TOKEN"],
    "influx_org": os.environ["INFLUX_ORG"],
    "influx_bucket": os.environ["INFLUX_BUCKET"]
})
devices_repo = DevicesRepo()
in_memory_repo = InMemoryRepo()


def on_message(_, __, message):
    topic = message.topic
    try:
        message_content = json.loads(message.payload.decode('utf-8'))
        print(message_content)
    except JSONDecodeError:
        print("Received Invalid json.")
        return
    if topic == 'sb/sensor/logs':
        request = build_sensor_reading_request(message_content)
        response = add_new_sensor_reading(request, repo, in_memory_repo)
        print(response.value)  # TODO: Use logs for this
    elif topic == 'sb/sensor/configs':
        request = build_device_config_request(message_content)
        response = get_device_config(request, devices_repo)
        if response:
            publish_device_configuration(response.value, request.request_dict["imei"])
            print(response.value)  # TODO: Use logs for this
        else:
            print(response.value)  # TODO: Use logs for this
