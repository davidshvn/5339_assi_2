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

import paho.mqtt.publish as publish

publish.single(topic, message, hostname=broker, retain=True)