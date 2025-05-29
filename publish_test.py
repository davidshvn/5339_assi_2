import paho.mqtt.client as mqtt

# MQTT broker settings
#broker = "172.17.34.107"
broker = "test.mosquitto.org"
port = 1883
topic = "test/paho/retain"
message = "This is a retained message!"

import paho.mqtt.client as mqtt

#client = mqtt.Client(protocol=mqtt.MQTTv311)  # Avoid deprecated v1
#client.connect(broker, 1883, 60)
#client.publish(topic, "Updated client call")
#client.disconnect()

#import paho.mqtt.publish as publish

#publish.single(topic, message, hostname=broker, retain=True)

# publisher.py
import paho.mqtt.client as mqtt
import json
import time
import random

broker = "test.mosquitto.org"  # or your local broker
topic = "streamlit/demo/data"

# Sydney bounding box
LAT_MIN, LAT_MAX = -34.3, -33.3
LON_MIN, LON_MAX = 150.75, 151.5

client = mqtt.Client()
client.connect(broker, 1883, 60)

brands = ['coles', '711', 'shell']

try:
    while True:
        data = {
            "timestamp": time.time(),
            "lat": random.uniform(LAT_MIN, LAT_MAX),
            "lon": random.uniform(LON_MIN, LON_MAX),
            "brand": random.choice(brands),
            "92": random.randint(100, 999),
            "94": random.randint(100, 999),
            "97": random.randint(100, 999)
        }
        payload = json.dumps(data)
        client.publish(topic, payload)
        #print("Published:", data)
        time.sleep(5)

except KeyboardInterrupt:
    client.disconnect()