import paho.mqtt.client as mqtt

broker = "localhost"
topic = "greenhouse/temp"

def on_message(client, userdata, msg):
    print(f"Received Temperature: {msg.payload.decode()} °C")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message

client.connect(broker, 1883, 60)

client.subscribe(topic)

print("Listening for temperature data...")

client.loop_forever()