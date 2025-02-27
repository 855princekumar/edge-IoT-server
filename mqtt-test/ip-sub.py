import csv
import time
import ssl  # Required for secure connections
import paho.mqtt.client as mqtt

# MQTT Broker Details
BROKER = "33f8ce768f42482dbf8326a53213ea9d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "roboloverpk"
PASSWORD = "Open4you@123"
TOPIC_PREFIX = "network/"
CSV_FILE = "node_ips.csv"

# Initialize the MQTT client
client = mqtt.Client("SubscriberClient")
client.username_pw_set(USERNAME, PASSWORD)

# Enable TLS
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)  # For testing only, set to False in production

# Function to read topics from CSV
def read_topics_from_csv():
    topics = {}
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 3:
                    serial_no, timestamp, node_name = row[:3]
                    topics[node_name] = serial_no
    except FileNotFoundError:
        print("CSV file not found. Creating a new file.")
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Serial No", "Timestamp", "Node Name", "IP"])
    return topics

# Function to update CSV with IP data
def update_csv_with_ip(serial_no, timestamp, node_name, ip):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([serial_no, timestamp, node_name, ip])

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        print("Connection successful")
        # Subscribing to topics dynamically
        topics = read_topics_from_csv()
        for topic, serial_no in topics.items():
            client.subscribe(TOPIC_PREFIX + topic)
    else:
        print("Connection failed")

def on_message(client, userdata, msg):
    topic = msg.topic[len(TOPIC_PREFIX):]
    payload = msg.payload.decode("utf-8")
    timestamp, ip = payload.split(',')
    serial_no = topics.get(topic)
    if serial_no:
        update_csv_with_ip(serial_no, timestamp, topic, ip)
    else:
        print(f"Unrecognized topic: {topic}")

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")

# Attach callback functions
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    client.disconnect()
