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
        arm_speed REAL,
        core_speed REAL,
        h264_speed REAL,
        isp_speed REAL,
        v3d_speed REAL,
        uart_speed REAL,
        emmc_speed REAL,
        pixel_speed REAL,
        hdmi_speed REAL,
        core_volts REAL,
        sdram_c_volts REAL,
        sdram_i_volts REAL,
        sdram_p_volts REAL,
        arm_memory REAL,
        gpu_memory REAL,
        throttled_state TEXT
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
    """Fetch system metrics using vcgencmd and other available tools."""
    metrics = {}
    try:
        # Fetch system metrics using vcgencmd
        metrics["cpu_temp"] = float(subprocess.check_output("vcgencmd measure_temp", shell=True).decode().strip().split('=')[1].split("'")[0])
        metrics["ram_usage"] = float(subprocess.check_output("free | grep Mem | awk '{print $3/$2 * 100.0}'", shell=True).decode().strip())
        
        # Use top command to get CPU usage, calculating (100 - idle percentage)
        cpu_usage_str = subprocess.check_output("top -bn1 | grep 'Cpu(s)'", shell=True).decode().strip()
        cpu_usage_values = cpu_usage_str.split(',')
        cpu_idle = float(cpu_usage_values[3].split()[0])  # This extracts the idle percentage (e.g., 91.7)
        metrics["cpu_usage"] = 100.0 - cpu_idle  # CPU usage is 100 - idle percentage

        metrics["disk_usage"] = float(subprocess.check_output("df / | awk 'NR==2 {print $5}'", shell=True).decode().strip().replace('%', ''))

        # Fetch network usage using vnstat
        try:
            net_up_str = subprocess.check_output("vnstat --oneline | awk -F';' '{print $9}'", shell=True).decode().strip()
            net_down_str = subprocess.check_output("vnstat --oneline | awk -F';' '{print $10}'", shell=True).decode().strip()

            # Ensure the strings contain values
            if net_up_str and net_down_str:
                # Extract numeric values from vnstat output
                net_up = ''.join(filter(str.isdigit, net_up_str.split()[0])) if net_up_str.split() else None
                net_down = ''.join(filter(str.isdigit, net_down_str.split()[0])) if net_down_str.split() else None
                
                metrics["net_up"] = int(net_up) if net_up else None
                metrics["net_down"] = int(net_down) if net_down else None
            else:
                print("vnstat output seems to be empty or incomplete.")
                metrics["net_up"] = None
                metrics["net_down"] = None

        except subprocess.CalledProcessError as e:
            print(f"vnstat not found or failed: {e}")
            metrics["net_up"] = None
            metrics["net_down"] = None

        # Fetch various clock speeds and voltages
        metrics["arm_speed"] = float(subprocess.check_output("vcgencmd measure_clock arm", shell=True).decode().strip().split('=')[1])
        metrics["core_speed"] = float(subprocess.check_output("vcgencmd measure_clock core", shell=True).decode().strip().split('=')[1])
        metrics["h264_speed"] = float(subprocess.check_output("vcgencmd measure_clock h264", shell=True).decode().strip().split('=')[1])
        metrics["isp_speed"] = float(subprocess.check_output("vcgencmd measure_clock isp", shell=True).decode().strip().split('=')[1])
        metrics["v3d_speed"] = float(subprocess.check_output("vcgencmd measure_clock v3d", shell=True).decode().strip().split('=')[1])
        metrics["uart_speed"] = float(subprocess.check_output("vcgencmd measure_clock uart", shell=True).decode().strip().split('=')[1])
        metrics["emmc_speed"] = float(subprocess.check_output("vcgencmd measure_clock emmc", shell=True).decode().strip().split('=')[1])
        metrics["pixel_speed"] = float(subprocess.check_output("vcgencmd measure_clock pixel", shell=True).decode().strip().split('=')[1])
        metrics["hdmi_speed"] = float(subprocess.check_output("vcgencmd measure_clock hdmi", shell=True).decode().strip().split('=')[1])
        metrics["core_volts"] = float(subprocess.check_output("vcgencmd measure_volts core", shell=True).decode().strip().split('=')[1].split('V')[0])
        metrics["sdram_c_volts"] = float(subprocess.check_output("vcgencmd measure_volts sdram_c", shell=True).decode().strip().split('=')[1].split('V')[0])
        metrics["sdram_i_volts"] = float(subprocess.check_output("vcgencmd measure_volts sdram_i", shell=True).decode().strip().split('=')[1].split('V')[0])
        metrics["sdram_p_volts"] = float(subprocess.check_output("vcgencmd measure_volts sdram_p", shell=True).decode().strip().split('=')[1].split('V')[0])
        metrics["arm_memory"] = float(subprocess.check_output("vcgencmd get_mem arm", shell=True).decode().strip().split('=')[1].split('M')[0])
        metrics["gpu_memory"] = float(subprocess.check_output("vcgencmd get_mem gpu", shell=True).decode().strip().split('=')[1].split('M')[0])
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
    # Check and install missing dependencies
    install_dependencies()

    # Setup BME280 sensor
    bme280 = setup_bme280()

    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Check and create tables if they don't exist
        check_and_create_table(cursor)

        while True:
            bme_temperature = bme280.temperature
            bme_humidity = bme280.humidity
            bme_pressure = bme280.pressure

            print(f"BME280 Temperature: {bme_temperature:.2f} °C")
            print(f"BME280 Humidity: {bme_humidity:.2f} %")
            print(f"BME280 Pressure: {bme_pressure:.2f} hPa")

            # Fetch system metrics
            metrics = get_system_metrics()

            # Debug print system metrics
            print(f"System Metrics: {metrics}")

            # Insert data into the database
            insert_inner_query = '''
            INSERT INTO inner_sensor (temperature, humidity, pressure) VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_inner_query, (bme_temperature, bme_humidity, bme_pressure))

            insert_health_query = '''
            INSERT INTO board_health (cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down, arm_speed, core_speed,
                h264_speed, isp_speed, v3d_speed, uart_speed, emmc_speed, pixel_speed, hdmi_speed, core_volts, sdram_c_volts,
                sdram_i_volts, sdram_p_volts, arm_memory, gpu_memory, throttled_state) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_health_query, (
                metrics["cpu_temp"], metrics["ram_usage"], metrics["cpu_usage"], metrics["disk_usage"], metrics["net_up"],
                metrics["net_down"], metrics["arm_speed"], metrics["core_speed"], metrics["h264_speed"], metrics["isp_speed"],
                metrics["v3d_speed"], metrics["uart_speed"], metrics["emmc_speed"], metrics["pixel_speed"], metrics["hdmi_speed"],
                metrics["core_volts"], metrics["sdram_c_volts"], metrics["sdram_i_volts"], metrics["sdram_p_volts"], metrics["arm_memory"],
                metrics["gpu_memory"], metrics["throttled_state"]
            ))

            # Commit the transaction
            connection.commit()

            # Sleep for 30 seconds before the next reading
            time.sleep(5)

    except Error as e:
        print(f"Error connecting to MySQL: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    main()
