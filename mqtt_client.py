import os
import time

import paho.mqtt.client as mqtt

from dotenv import load_dotenv
from mqtt.subscribe import on_message

load_dotenv()
TOPICS = [("sb/sensor", 1)]

mqttBroker = os.environ['MQTT_BROKER']
client = mqtt.Client("SB_Server")
client.connect(mqttBroker)

client.loop_start()
client.subscribe(TOPICS)
client.on_message = on_message

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("exiting")

client.loop_stop()
