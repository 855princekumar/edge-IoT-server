import paho.mqtt.client as mqtt

broker_address = "33f8ce768f42482dbf8326a53213ea9d.s1.eu.hivemq.cloud"
port = 8883
topic = "test/hihello"
username = "roboloverpk"
password = "Open4you@123"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to HiveMQ successfully")
        client.subscribe(topic)
        print(f"Subscribed to topic: {topic}")
    else:
        print(f"Failed to connect. Error code: {rc}")

def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()} from topic: {msg.topic}")

client = mqtt.Client("SubscriberClient")

client.username_pw_set(username, password)
client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(broker_address, port)
    client.loop_forever()
except Exception as e:
    print(f"Connection failed: {e}")
