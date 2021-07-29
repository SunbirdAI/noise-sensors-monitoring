import json
import os

from dotenv import load_dotenv

from noise_sensors_monitoring.repository.influx_db_repo import InfluxDBRepo
from noise_sensors_monitoring.use_cases.sensor_reading import add_new_sensor_reading
from noise_sensors_monitoring.requests.sensor_reading import build_sensor_reading_request

load_dotenv()

repo = InfluxDBRepo({
    "influx_url": os.environ["INFLUX_DB_URL"],
    "influx_token": os.environ["INFLUX_DB_TOKEN"],
    "influx_org": os.environ["INFLUX_ORG"],
    "influx_bucket": os.environ["INFLUX_BUCKET"]
})


def on_message(_, __, message):
    topic = message.topic
    # TODO: First validate if this is valid json
    print(message.payload.decode('utf-8'))
    message_content = json.loads(message.payload.decode('utf-8'))
    if topic == 'sb/sensor':
        request = build_sensor_reading_request(message_content)
        response = add_new_sensor_reading(request, repo)
        print(response.value)  # Use logs for this
