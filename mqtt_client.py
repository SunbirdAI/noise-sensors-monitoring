import os
import time

import paho.mqtt.client as mqtt

from mqtt.subscribe import on_message

TOPICS = [("sb/sensor/logs", 1), ("sb/sensor/configs", 1)]

mqttBroker = os.environ['MOSQUITTO_URL']
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
