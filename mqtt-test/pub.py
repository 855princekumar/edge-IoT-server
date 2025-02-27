import paho.mqtt.client as mqtt

broker_address = "33f8ce768f42482dbf8326a53213ea9d.s1.eu.hivemq.cloud"
port = 8883  # Secure MQTT port for HiveMQ Cloud
topic = "test/hihello"
username = "roboloverpk"
password = "Open4you@123"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to HiveMQ successfully")
        client.publish(topic, "Hi from MQTT publisher!")
    else:
        print(f"Failed to connect. Error code: {rc}")

client = mqtt.Client("PublisherClient")

# Set authentication and enable secure communication
client.username_pw_set(username, password)
client.tls_set()  # Use default certificates for secure connection

client.on_connect = on_connect

try:
    client.connect(broker_address, port)
    client.loop_start()
    input("Press Enter to exit...\n")  # Keep the script running
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    client.disconnect()
    print("Publisher disconnected.")
