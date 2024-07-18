import json
import os

import paho.mqtt.client as mqtt


def publish_device_configuration(device_configuration, device_imei):
    mqtt_broker = os.environ["MOSQUITTO_URL"]
    client = mqtt.Client("SB_Server_Publish")
    client.connect(mqtt_broker)
    client.publish(f"sb/sensor/{device_imei}", json.dumps(device_configuration))
