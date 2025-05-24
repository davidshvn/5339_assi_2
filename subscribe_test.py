# subscriber.py
import paho.mqtt.client as mqtt
import json

broker = "test.mosquitto.org"
topic = "streamlit/demo/data"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(topic)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("Received dict:", data)
    except json.JSONDecodeError:
        print("Invalid JSON:", msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, 1883, 60)
client.loop_forever()