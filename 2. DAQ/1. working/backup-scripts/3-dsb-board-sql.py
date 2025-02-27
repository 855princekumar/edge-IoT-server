#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import time
import mysql.connector
from mysql.connector import Error
import subprocess

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
        subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'vnstat'])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")

def check_and_create_table(cursor):
    """Check and create necessary tables if they don't exist."""
    create_outer_sensor_table = '''
    CREATE TABLE IF NOT EXISTS outer_sensor (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL
    )
    '''
    
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
    
    try:
        cursor.execute(create_outer_sensor_table)
        cursor.execute(create_board_health_table)
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

def read_temp_raw(device_file):
    """Read the raw temperature data from the sensor."""
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp(device_file):
    """Parse the raw temperature data and return the temperature."""
    lines = read_temp_raw(device_file)
    # Wait until the sensor output is valid
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    # Find the position of the temperature data
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        # Extract and convert the temperature value
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    else:
        return None

def main():
    # Check and install missing dependencies
    install_dependencies()

    # Load the required kernel modules for One-Wire interface
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    # Base directory for the One-Wire device files
    base_dir = '/sys/bus/w1/devices/'
    # Find the directory for the DS18B20 sensor
    device_folder = glob.glob(base_dir + '28*')[0] if glob.glob(base_dir + '28*') else None
    device_file = device_folder + '/w1_slave' if device_folder else None

    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            # Check and create tables if they don't exist
            check_and_create_table(cursor)
            print("Database connected successfully.")

            while True:
                # If DS18B20 sensor is connected, fetch the temperature
                temperature_c = None
                if device_file:
                    try:
                        temperature_c = read_temp(device_file)
                    except Exception as e:
                        print(f"Error reading temperature: {e}")
                
                # Get system metrics
                system_metrics = get_system_metrics()

                # Insert system metrics into the board_health table
                insert_health_query = """
                    INSERT INTO board_health (cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down, arm_speed, core_speed, h264_speed, isp_speed, v3d_speed, uart_speed, emmc_speed, pixel_speed, hdmi_speed, core_volts, sdram_c_volts, sdram_i_volts, sdram_p_volts, arm_memory, gpu_memory, throttled_state)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_health_query, (
                    system_metrics.get("cpu_temp"),
                    system_metrics.get("ram_usage"),
                    system_metrics.get("cpu_usage"),
                    system_metrics.get("disk_usage"),
                    system_metrics.get("net_up"),
                    system_metrics.get("net_down"),
                    system_metrics.get("arm_speed"),
                    system_metrics.get("core_speed"),
                    system_metrics.get("h264_speed"),
                    system_metrics.get("isp_speed"),
                    system_metrics.get("v3d_speed"),
                    system_metrics.get("uart_speed"),
                    system_metrics.get("emmc_speed"),
                    system_metrics.get("pixel_speed"),
                    system_metrics.get("hdmi_speed"),
                    system_metrics.get("core_volts"),
                    system_metrics.get("sdram_c_volts"),
                    system_metrics.get("sdram_i_volts"),
                    system_metrics.get("sdram_p_volts"),
                    system_metrics.get("arm_memory"),
                    system_metrics.get("gpu_memory"),
                    system_metrics.get("throttled_state")
                ))

                # If temperature data is available, log it
                if temperature_c is not None:
                    insert_sensor_query = "INSERT INTO outer_sensor (temperature) VALUES (%s)"
                    cursor.execute(insert_sensor_query, (temperature_c,))
                    print(f"Logged temperature: {temperature_c}\u00B0C")

                # Commit the transactions to the database
                connection.commit()

                # Wait before the next logging cycle
                time.sleep(5)

    except Error as e:
        print(f"Database connection error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
