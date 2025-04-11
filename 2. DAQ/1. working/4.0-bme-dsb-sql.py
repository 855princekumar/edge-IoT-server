#!/usr/bin/env python3
import os
import glob
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
    try:
        vnstat_installed = subprocess.call(['which', 'vnstat'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        if not vnstat_installed:
            print("vnstat not found. Installing dependencies...")
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'vnstat', 'python3-adafruit-circuitpython-bme280'])
            print("Dependencies installed successfully.")
        else:
            print("vnstat already installed. Skipping dependency installation.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")

def check_and_create_table(cursor):
    create_outer_sensor_table = '''
    CREATE TABLE IF NOT EXISTS outer_sensor (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL
    )'''
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
    )'''
    create_inner_sensor_table = '''
    CREATE TABLE IF NOT EXISTS inner_sensor (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        pressure REAL
    )'''
    create_error_log_table = '''
    CREATE TABLE IF NOT EXISTS error_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        source VARCHAR(50),
        message TEXT
    )'''
    try:
        cursor.execute(create_outer_sensor_table)
        cursor.execute(create_board_health_table)
        cursor.execute(create_inner_sensor_table)
        cursor.execute(create_error_log_table)
        print("Tables created or verified successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")

def log_error(cursor, source, message):
    try:
        cursor.execute("INSERT INTO error_logs (source, message) VALUES (%s, %s)", (source, message))
    except Exception as e:
        print(f"Failed to log error to DB: {e}")

def get_system_metrics():
    metrics = {}
    try:
        metrics["cpu_temp"] = float(subprocess.check_output("vcgencmd measure_temp", shell=True).decode().strip().split('=')[1].split("'")[0])
        metrics["ram_usage"] = float(subprocess.check_output("free | grep Mem | awk '{print $3/$2 * 100.0}'", shell=True).decode().strip())
        cpu_usage_str = subprocess.check_output("top -bn1 | grep 'Cpu(s)'", shell=True).decode().strip()
        cpu_usage_values = cpu_usage_str.split(',')
        cpu_idle = float(cpu_usage_values[3].split()[0])
        metrics["cpu_usage"] = 100.0 - cpu_idle
        metrics["disk_usage"] = float(subprocess.check_output("df / | awk 'NR==2 {print $5}'", shell=True).decode().strip().replace('%', ''))
        try:
            net_up_str = subprocess.check_output("vnstat --oneline | awk -F';' '{print $9}'", shell=True).decode().strip()
            net_down_str = subprocess.check_output("vnstat --oneline | awk -F';' '{print $10}'", shell=True).decode().strip()
            net_up = ''.join(filter(str.isdigit, net_up_str.split()[0])) if net_up_str.split() else None
            net_down = ''.join(filter(str.isdigit, net_down_str.split()[0])) if net_down_str.split() else None
            metrics["net_up"] = int(net_up) if net_up else None
            metrics["net_down"] = int(net_down) if net_down else None
        except subprocess.CalledProcessError:
            metrics["net_up"] = None
            metrics["net_down"] = None
        metrics["core_speed"] = float(subprocess.check_output("vcgencmd measure_clock core", shell=True).decode().strip().split('=')[1])
        metrics["core_volts"] = float(subprocess.check_output("vcgencmd measure_volts core", shell=True).decode().strip().split('=')[1].split('V')[0])
        metrics["arm_memory"] = float(subprocess.check_output("vcgencmd get_mem arm", shell=True).decode().strip().split('=')[1].split('M')[0])
        metrics["gpu_memory"] = float(subprocess.check_output("vcgencmd get_mem gpu", shell=True).decode().strip().split('=')[1].split('M')[0])
        metrics["throttled_state"] = subprocess.check_output("vcgencmd get_throttled", shell=True).decode().strip()
        metrics["uptime"] = subprocess.check_output("uptime -p", shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving system metrics: {e}")
    return metrics

def setup_bme280():
    i2c = busio.I2C(board.SCL, board.SDA)
    return adafruit_bme280.Adafruit_BME280_I2C(i2c)

def read_temp(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            if lines[0].strip()[-3:] == 'YES':
                temp_pos = lines[1].find('t=')
                if temp_pos != -1:
                    temp_string = lines[1][temp_pos + 2:]
                    return float(temp_string) / 1000.0
    except Exception as e:
        print(f"Error reading temperature: {e}")
    return None

def main():
    install_dependencies()
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    device_file = None
    try:
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        device_file = device_folder + '/w1_slave'
    except IndexError:
        print("DS18B20 sensor not found at startup.")
    try:
        bme280 = setup_bme280()
    except Exception as e:
        print(f"Error initializing BME280 sensor: {e}")
        bme280 = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        check_and_create_table(cursor)
        while True:
            temperature_c = None
            bme_temperature = None
            bme_humidity = None
            bme_pressure = None
            try:
                if device_file:
                    temperature_c = read_temp(device_file)
                    if temperature_c is not None:
                        print(f"DS18B20 Temperature: {temperature_c} °C")
            except Exception as e:
                print(f"Error reading DS18B20: {e}")
                log_error(cursor, "DS18B20", str(e))
            try:
                if bme280:
                    bme_temperature = bme280.temperature
                    bme_humidity = bme280.humidity
                    bme_pressure = bme280.pressure
                    print(f"BME280 Temperature: {bme_temperature:.2f} °C")
                    print(f"BME280 Humidity: {bme_humidity:.2f} %")
                    print(f"BME280 Pressure: {bme_pressure:.2f} hPa")
            except Exception as e:
                print(f"Error reading BME280: {e}")
                log_error(cursor, "BME280", str(e))
            metrics = get_system_metrics()
            print(f"System Metrics: {metrics}")
            try:
                if temperature_c is not None:
                    cursor.execute("INSERT INTO outer_sensor (temperature) VALUES (%s)", (temperature_c,))
                if None not in (bme_temperature, bme_humidity, bme_pressure):
                    cursor.execute("INSERT INTO inner_sensor (temperature, humidity, pressure) VALUES (%s, %s, %s)",
                                   (bme_temperature, bme_humidity, bme_pressure))
                cursor.execute("""
                INSERT INTO board_health (
                    cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down,
                    core_volts, core_speed, arm_memory, gpu_memory, throttled_state, uptime
                ) VALUES (
                    %(cpu_temp)s, %(ram_usage)s, %(cpu_usage)s, %(disk_usage)s, %(net_up)s, %(net_down)s,
                    %(core_volts)s, %(core_speed)s, %(arm_memory)s, %(gpu_memory)s, %(throttled_state)s, %(uptime)s
                )""", metrics)
                connection.commit()
            except Exception as e:
                print(f"Error inserting into database: {e}")
                log_error(cursor, "MySQL Insert", str(e))
            time.sleep(5)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    main()
