import json
import subprocess
import sys
import datetime  # Import datetime for handling datetime objects
import time  # Import time for sleep function

# Function to check and install required libraries
def install_library(library_name):
    try:
        # Attempt to import the library
        __import__(library_name)
    except ImportError:
        print(f"{library_name} not found. Installing...")
        try:
            # Attempt to install the library individually using pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", library_name, "--break-system-packages"])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {library_name}: {e}")

# Check and install required libraries
install_library("paho-mqtt")
install_library("mysql-connector-python")

import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error

# MQTT connection parameters
MQTT_BROKER = "10.1.56.46"  # Replace with your MQTT broker address
MQTT_PORT = 1883  # Replace with your MQTT broker port
MQTT_TOPIC = "nodeL2"  # Topic to publish the nested JSON data
MQTT_KEEPALIVE = 5  # Keepalive interval in seconds

# MySQL database connection parameters
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASSWORD = "node@123"
DB_NAME = "node-db"

# Initialize MQTT Client
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

client.on_connect = on_connect

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)

def publish_nested_data_to_mqtt():
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            nested_json_data = {}

            for table in tables:
                table_name = table[0]
                query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 1"
                cursor.execute(query)
                row = cursor.fetchone()

                if row:
                    # Assuming the row data needs to be published as JSON
                    columns = [desc[0] for desc in cursor.description]
                    table_data = dict(zip(columns, row))
                    
                    # Convert datetime objects to string
                    for key, value in table_data.items():
                        if isinstance(value, datetime.datetime):
                            table_data[key] = value.isoformat()  # Convert to ISO format

                    # Add each table's data to the nested JSON
                    nested_json_data[table_name] = table_data

            # Convert the nested data to JSON
            nested_json_payload = json.dumps(nested_json_data)
            
            # Publish the nested JSON data to the MQTT topic with QoS 0
            client.publish(MQTT_TOPIC, nested_json_payload, qos=0)
            print(f"Published nested JSON data to MQTT topic '{MQTT_TOPIC}'")
            print(nested_json_payload)  # For debugging, to see the structure

    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

# Run the data fetch and publish process every 5 seconds
try:
    while True:
        publish_nested_data_to_mqtt()
        time.sleep(5)  # Wait for 5 seconds before publishing again
except KeyboardInterrupt:
    print("Publishing stopped by user.")

# Loop to ensure the MQTT client runs continuously
client.loop_start()  # Use loop_start to allow the script to publish data and maintain the MQTT connection
