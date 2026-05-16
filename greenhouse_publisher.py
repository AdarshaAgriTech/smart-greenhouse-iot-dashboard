import paho.mqtt.client as mqtt
import random
import time

broker = "localhost"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(broker, 1883, 60)

while True:

    temperature = round(random.uniform(25, 35), 2)
    humidity = round(random.uniform(55, 75), 2)
    ec = round(random.uniform(1.5, 2.5), 2)
    ph = round(random.uniform(5.5, 6.5), 2)

    client.publish("greenhouse/temp", temperature)
    client.publish("greenhouse/rh", humidity)
    client.publish("greenhouse/ec", ec)
    client.publish("greenhouse/ph", ph)

    print("Published:")
    print(f"Temperature: {temperature} °C")
    print(f"Humidity: {humidity} %")
    print(f"EC: {ec}")
    print(f"pH: {ph}")
    print("----------------------")

    time.sleep(3)