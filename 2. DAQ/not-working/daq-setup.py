import subprocess
import os
import sys

def install_dependencies():
    # Update and install system packages
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "python3-pip", "i2c-tools", "python3-smbus", "python3-pandas", "python3-mysql.connector", "systemd"], check=True)
    
    # Install Python packages
    subprocess.run(["sudo", "pip3", "install", "adafruit-circuitpython-bme280", "mysql-connector-python", "psutil"], check=True)

def enable_interfaces():
    # Enable I2C interface
    subprocess.run(["sudo", "raspi-config", "nonint", "do_i2c", "0"], check=True)
    # Enable 1-Wire interface
    subprocess.run(["sudo", "raspi-config", "nonint", "do_onewire", "0"], check=True)

def create_sensor_script():
    script_content = '''#!/usr/bin/env python3
import mysql.connector
import psutil
import board
import adafruit_bme280
import time
from datetime import datetime

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="node@123",
    database="node-db"
)
cursor = db.cursor()

# Create tables if they don't exist
tables = {
    "inner_sensor": (
        "CREATE TABLE IF NOT EXISTS inner_sensor ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "timestamp DATETIME, "
        "temperature FLOAT, "
        "humidity FLOAT, "
        "pressure FLOAT"
        ")"
    ),
    "outer_sensor": (
        "CREATE TABLE IF NOT EXISTS outer_sensor ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "timestamp DATETIME, "
        "temperature FLOAT"
        ")"
    ),
    "board_health": (
        "CREATE TABLE IF NOT EXISTS board_health ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "timestamp DATETIME, "
        "cpu_temp FLOAT, "
        "ram_usage FLOAT, "
        "cpu_usage FLOAT, "
        "disk_usage FLOAT, "
        "net_up FLOAT, "
        "net_down FLOAT, "
        "arm_speed FLOAT, "
        "core_speed FLOAT, "
        "h264_speed FLOAT, "
        "isp_speed FLOAT, "
        "v3d_speed FLOAT, "
        "uart_speed FLOAT, "
        "emmc_speed FLOAT, "
        "pixel_speed FLOAT, "
        "hdmi_speed FLOAT, "
        "core_volts FLOAT, "
        "sdram_c_volts FLOAT, "
        "sdram_i_volts FLOAT, "
        "sdram_p_volts FLOAT, "
        "arm_memory FLOAT, "
        "gpu_memory FLOAT, "
        "throttled_state INT"
        ")"
    )
}

for table_name, table_ddl in tables.items():
    cursor.execute(table_ddl)

db.commit()

# Setup sensor
i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

def read_sensor():
    return {
        "temperature": bme280.temperature,
        "humidity": bme280.humidity,
        "pressure": bme280.pressure
    }

def get_board_health():
    return {
        "cpu_temp": psutil.sensors_temperatures().get('coretemp', [])[0].current if psutil.sensors_temperatures().get('coretemp') else None,
        "ram_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage('/').percent,
        "net_up": psutil.net_io_counters().bytes_sent,
        "net_down": psutil.net_io_counters().bytes_recv,
        "arm_speed": None,
        "core_speed": None,
        "h264_speed": None,
        "isp_speed": None,
        "v3d_speed": None,
        "uart_speed": None,
        "emmc_speed": None,
        "pixel_speed": None,
        "hdmi_speed": None,
        "core_volts": None,
        "sdram_c_volts": None,
        "sdram_i_volts": None,
        "sdram_p_volts": None,
        "arm_memory": psutil.virtual_memory().available,
        "gpu_memory": None,
        "throttled_state": None
    }

def insert_data():
    while True:
        timestamp = datetime.now()
        sensor_data = read_sensor()
        board_health = get_board_health()
        
        cursor.execute("INSERT INTO inner_sensor (timestamp, temperature, humidity, pressure) VALUES (%s, %s, %s, %s)",
                       (timestamp, sensor_data['temperature'], sensor_data['humidity'], sensor_data['pressure']))
        
        cursor.execute("INSERT INTO board_health (timestamp, cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down, "
                       "arm_speed, core_speed, h264_speed, isp_speed, v3d_speed, uart_speed, emmc_speed, pixel_speed, hdmi_speed, "
                       "core_volts, sdram_c_volts, sdram_i_volts, sdram_p_volts, arm_memory, gpu_memory, throttled_state) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (timestamp, board_health['cpu_temp'], board_health['ram_usage'], board_health['cpu_usage'], board_health['disk_usage'],
                        board_health['net_up'], board_health['net_down'], board_health['arm_speed'], board_health['core_speed'],
                        board_health['h264_speed'], board_health['isp_speed'], board_health['v3d_speed'], board_health['uart_speed'],
                        board_health['emmc_speed'], board_health['pixel_speed'], board_health['hdmi_speed'], board_health['core_volts'],
                        board_health['sdram_c_volts'], board_health['sdram_i_volts'], board_health['sdram_p_volts'],
                        board_health['arm_memory'], board_health['gpu_memory'], board_health['throttled_state']))
        
        db.commit()
        time.sleep(60)  # Sleep for 60 seconds

if __name__ == "__main__":
    insert_data()
'''

    with open('/usr/local/bin/sensor_interfacing_script.py', 'w') as f:
        f.write(script_content)
    
    # Make the script executable
    subprocess.run(["sudo", "chmod", "+x", "/usr/local/bin/sensor_interfacing_script.py"], check=True)

def create_service():
    service_content = '''
[Unit]
Description=Sensor Interfacing Script

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/sensor_interfacing_script.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
    '''
    with open('/etc/systemd/system/sensor_interfacing.service', 'w') as f:
        f.write(service_content)
    
    # Reload systemd and enable the service
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    subprocess.run(["sudo", "systemctl", "enable", "sensor_interfacing.service"], check=True)

def main():
    install_dependencies()
    enable_interfaces()
    create_sensor_script()
    create_service()

if __name__ == "__main__":
    main()
