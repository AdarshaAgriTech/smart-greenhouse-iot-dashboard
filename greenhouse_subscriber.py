import paho.mqtt.client as mqtt

broker = "localhost"

def on_message(client, userdata, msg):
    topic = msg.topic
    value = msg.payload.decode()

    print(f"{topic} --> {value}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_message = on_message

client.connect(broker, 1883, 60)

client.subscribe("greenhouse/#")

print("Listening to all greenhouse data...\n")

client.loop_forever()