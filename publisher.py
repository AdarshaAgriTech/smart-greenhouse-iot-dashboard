import paho.mqtt.client as mqtt
import time
import random

broker = "localhost"
topic = "greenhouse/temp"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(broker, 1883, 60)

while True:
    temp = round(random.uniform(25, 35), 2)

    client.publish(topic, temp)

    print(f"Published Temperature: {temp} °C")

    time.sleep(2)