import os
import subprocess
import sys
import json
import time

try:
    # Check if paho-mqtt is installed
    import paho.mqtt.client as mqtt
except ImportError:
    print("paho-mqtt is not installed. Installing now...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paho-mqtt"])
    except subprocess.CalledProcessError:
        print("Initial installation failed. Retrying with --break-system-packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paho-mqtt", "--break-system-packages"])
    finally:
        import paho.mqtt.client as mqtt

# MQTT Broker details
BROKER = "10.1.56.46"
PORT = 1883
TOPIC = "nodeL3/logs"
QOS = 0

# Path to the uptime log file
LOG_FILE_PATH = "/home/nodeL3/uptime_log.txt"

# Function to read and format the uptime log
def get_uptime_log():
    try:
        with open(LOG_FILE_PATH, "r") as log_file:
            logs = log_file.read().strip()
        return {"node": "nodeL3", "uptime_logs": logs}
    except Exception as e:
        return {"node": "nodeL3", "error": str(e)}

# MQTT setup
client = mqtt.Client()

def publish_logs():
    while True:
        # Read the uptime log
        log_data = get_uptime_log()
        # Convert to JSON string
        payload = json.dumps(log_data)
        # Publish to MQTT broker
        client.publish(TOPIC, payload, qos=QOS)
        print(f"Published: {payload}")
        # Wait for 10 minutes (600 seconds)
        time.sleep(600)

if __name__ == "__main__":
    try:
        # Connect to the MQTT broker
        client.connect(BROKER, PORT)
        print(f"Connected to MQTT broker at {BROKER}:{PORT}")
        # Start publishing logs
        publish_logs()
    except Exception as e:
        print(f"Error: {e}")
