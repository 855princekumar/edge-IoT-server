import os
import platform
import time
import paho.mqtt.client as mqtt

# Your MQTT broker details
BROKER = "33f8ce768f42482dbf8326a53213ea9d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "roboloverpk"
PASSWORD = "Open4you@123"

# Function to get the local IP address (Ethernet/WiFi only)
def get_local_ip():
    system_platform = platform.system()
    ip = None
    
    # For Linux (e.g., Raspberry Pi)
    if system_platform == "Linux":
        interfaces = ["eth0", "wlan0"]  # Ethernet and WiFi interfaces
        for interface in interfaces:
            try:
                # Use 'ip' or 'ifconfig' command to fetch the IP address for the interface
                result = os.popen(f"ip addr show {interface} | grep inet | awk '{{ print $2 }}'").read().strip()
                if result and not result.startswith("127."):  # Ignore localhost IP
                    ip = result.split("/")[0]  # Extract the actual IP from CIDR notation
                    break
            except Exception as e:
                print(f"Error fetching IP for {interface}: {e}")
    
    # For Windows
    elif system_platform == "Windows":
        interfaces = ["Ethernet", "Wi-Fi"]  # Ethernet and WiFi interfaces
        for interface in interfaces:
            try:
                # Use 'ipconfig' to get the IP address for the interface
                result = os.popen(f"ipconfig | findstr /C:\"{interface}\" /C:\"IPv4 Address\"").read()
                if result:
                    lines = result.splitlines()
                    for line in lines:
                        if "IPv4 Address" in line:
                            ip = line.split(":")[-1].strip()  # Extract the IP address
                            if ip != "127.0.0.1":  # Ensure it's not the localhost IP
                                break
            except Exception as e:
                print(f"Error fetching IP for {interface}: {e}")
    
    return ip

# Function to publish the IP address to MQTT
def publish_ip(client, ip):
    if ip:
        # Using the IP address as the topic name directly
        topic = ip
        payload = f"Publisher IP: {ip}"
        print(f"Publishing to topic '{topic}': {payload}")
        result = client.publish(topic, payload)
        print(f"Publish result: {result.rc}")  # Debugging the publish result
    else:
        print("No valid IP address found. Not publishing.")

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    ip = get_local_ip()
    publish_ip(client, ip)

def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")

# Initialize the MQTT client
client = mqtt.Client("PublisherClient")
client.username_pw_set(USERNAME, PASSWORD)

client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the MQTT broker
client.connect(BROKER, PORT, 60)

# Start the loop to handle incoming messages
client.loop_start()

# Keep running the script to periodically publish the IP address
try:
    while True:
        ip = get_local_ip()
        if ip:
            publish_ip(client, ip)
        else:
            print("No valid IP address found.")
        time.sleep(60)  # Publish every 60 seconds (adjust as needed)
except KeyboardInterrupt:
    print("Exiting...")
    client.disconnect()
