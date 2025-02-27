#!/usr/bin/env python3
import os
import time
import mysql.connector
from mysql.connector import Error
import subprocess
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

# Database configuration
db_config = {
    'user': 'admin',
    'password': 'node@123',
    'host': 'localhost',
    'database': 'node-db'
}

def install_dependencies():
    """Install missing dependencies."""
    try:
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'vnstat', 'python3-adafruit-circuitpython-bme280'])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")

def check_and_create_table(cursor):
    """Check and create necessary tables if they don't exist."""
    create_board_health_table = '''
    CREATE TABLE IF NOT EXISTS board_health (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        cpu_temp REAL,
        ram_usage REAL,
        cpu_usage REAL,
        disk_usage REAL,
        net_up BIGINT,
        net_down BIGINT,
        core_volts REAL,
        core_speed REAL,
        arm_memory REAL,
        gpu_memory REAL,
        throttled_state TEXT,
        uptime TEXT
    )
    '''
    create_inner_sensor_table = '''
    CREATE TABLE IF NOT EXISTS inner_sensor (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        pressure REAL
    )
    '''
    try:
        cursor.execute(create_board_health_table)
        cursor.execute(create_inner_sensor_table)
        print("Tables created or verified successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")

def get_system_metrics():
    """Fetch system metrics including uptime."""
    metrics = {}
    try:
        # Get CPU temperature
        metrics["cpu_temp"] = float(subprocess.check_output("vcgencmd measure_temp", shell=True).decode().strip().split('=')[1].split("'")[0])
        metrics["ram_usage"] = float(subprocess.check_output("free | grep Mem | awk '{print $3/$2 * 100.0}'", shell=True).decode().strip())
        metrics["cpu_usage"] = 100.0 - float(subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $8}'", shell=True).decode().strip())
        metrics["disk_usage"] = float(subprocess.check_output("df / | awk 'NR==2 {print $5}'", shell=True).decode().strip().replace('%', ''))

        # Network usage
        metrics["net_up"] = int(subprocess.check_output("vnstat --oneline | awk -F';' '{print $9}'", shell=True).decode().strip().split()[0])
        metrics["net_down"] = int(subprocess.check_output("vnstat --oneline | awk -F';' '{print $10}'", shell=True).decode().strip().split()[0])

        # Voltage and Clock speeds
        metrics["core_volts"] = float(subprocess.check_output("vcgencmd measure_volts core", shell=True).decode().split('=')[1].split('V')[0])
        metrics["core_speed"] = float(subprocess.check_output("vcgencmd measure_clock core", shell=True).decode().split('=')[1])
        metrics["arm_memory"] = float(subprocess.check_output("vcgencmd get_mem arm", shell=True).decode().split('=')[1].split('M')[0])
        metrics["gpu_memory"] = float(subprocess.check_output("vcgencmd get_mem gpu", shell=True).decode().split('=')[1].split('M')[0])

        # Uptime
        uptime = subprocess.check_output("uptime -p", shell=True).decode().strip()
        metrics["uptime"] = uptime

        # Throttled state
        metrics["throttled_state"] = subprocess.check_output("vcgencmd get_throttled", shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving system metrics: {e}")
    return metrics

def setup_bme280():
    """Setup and return the BME280 sensor."""
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    return bme280

def main():
    install_dependencies()
    bme280 = setup_bme280()

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        check_and_create_table(cursor)

        while True:
            metrics = get_system_metrics()
            print(f"System Metrics: {metrics}")

            # Insert into database
            insert_health_query = '''
            INSERT INTO board_health (cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down, core_volts, core_speed,
                arm_memory, gpu_memory, throttled_state, uptime) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_health_query, (
                metrics["cpu_temp"], metrics["ram_usage"], metrics["cpu_usage"], metrics["disk_usage"], metrics["net_up"],
                metrics["net_down"], metrics["core_volts"], metrics["core_speed"], metrics["arm_memory"],
                metrics["gpu_memory"], metrics["throttled_state"], metrics["uptime"]
            ))

            connection.commit()
            time.sleep(60)

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
