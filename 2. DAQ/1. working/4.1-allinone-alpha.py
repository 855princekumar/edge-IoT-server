import threading
import time
import json
import psutil
import mysql.connector
from smbus2 import SMBus
import bme280
import os
import glob
import logging
import subprocess

# Configure logging
logging.basicConfig(filename='sensor_data.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# Database configuration
db_config = {
    'user': 'admin',
    'password': 'node@123',
    'host': 'localhost',
    'database': 'node-db',
}

# Initialize DS18B20
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')

if device_folders:
    device_folder = device_folders[0]
    device_file = device_folder + '/w1_slave'
    logging.info(f"DS18B20 sensor found: {device_folder}")

    def read_temp_raw():
        with open(device_file, 'r') as f:
            lines = f.readlines()
        return lines

    def read_temp():
        lines = read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
else:
    logging.error("No DS18B20 temperature sensor found.")
    def read_temp():
        return None

# Initialize BME280
port = 1
address = 0x77
bus = SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

def read_bme280():
    data = bme280.sample(bus, address, calibration_params)
    return data.temperature, data.humidity, data.pressure

# Fallback to vcgencmd for CPU temperature
def get_cpu_temp_vcgencmd():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        temp_str = output.split('=')[1].split("'")[0]
        return float(temp_str)
    except Exception as e:
        logging.error(f"Failed to get CPU temperature using vcgencmd: {e}")
        return 0.0  # Return 0 if vcgencmd also fails

# Database connection
def db_connect():
    return mysql.connector.connect(**db_config)

def create_tables():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outer_sensor (
            id INT AUTO_INCREMENT PRIMARY KEY,
            temperature FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inner_sensor (
            id INT AUTO_INCREMENT PRIMARY KEY,
            temperature FLOAT,
            humidity FLOAT,
            pressure FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS board_health (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cpu_usage FLOAT,
            ram_usage FLOAT,
            cpu_temp FLOAT,
            disk_usage FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

create_tables()

# Collect and store sensor data
def collect_and_store_data():
    while True:
        outer_temp = read_temp()
        if outer_temp is not None:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO outer_sensor (temperature) VALUES (%s)", (outer_temp,))
            conn.commit()
            cursor.close()
            conn.close()
        else:
            logging.warning("Outer temperature reading is None.")

        inner_temp, inner_humidity, inner_pressure = read_bme280()

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inner_sensor (temperature, humidity, pressure) VALUES (%s, %s, %s)",
                       (inner_temp, inner_humidity, inner_pressure))
        conn.commit()

        # Collect and insert board health data
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        temperatures = psutil.sensors_temperatures()
        cpu_temp = temperatures.get('cpu-thermal', [{'current': 0.0}])[0]['current']

        # Check if cpu_temp is zero, then use vcgencmd
        if cpu_temp == 0.0:
            cpu_temp = get_cpu_temp_vcgencmd()

        disk_usage = psutil.disk_usage('/').percent

        cursor.execute("""
            INSERT INTO board_health (cpu_usage, ram_usage, cpu_temp, disk_usage)
            VALUES (%s, %s, %s, %s)
        """, (cpu_usage, ram_usage, cpu_temp, disk_usage))
        conn.commit()

        cursor.close()
        conn.close()

        time.sleep(5)

data_thread = threading.Thread(target=collect_and_store_data)
data_thread.start()
