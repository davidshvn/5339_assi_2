import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

port = 1883
broker = "test.mosquitto.org"  # or your local broker
topic = "streamlit/demo/data"

# Sydney bounding box
LAT_MIN, LAT_MAX = -34.3, -33.3
LON_MIN, LON_MAX = 150.75, 151.5

client = mqtt.Client()
client.connect(broker, 1883, 60)

brands = ['coles', '711', 'shell']
fuel_types = ['92', '94', '97']

try:
    while True:
        prices = [{
            "fuel": fuel,
            "price": random.randint(100, 999),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        } for fuel in fuel_types]

        data = {
            "timestamp": time.time(),
            "lat": random.uniform(LAT_MIN, LAT_MAX),
            "lon": random.uniform(LON_MIN, LON_MAX),
            "brand": random.choice(brands),
            "prices": prices
        }

        print(data)
        payload = json.dumps(data)
        client.publish(topic, payload)
        #print("Published:", data)
        time.sleep(5)

except KeyboardInterrupt:
    client.disconnect()