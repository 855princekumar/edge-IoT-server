#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import mysql.connector
from mysql.connector import Error
import subprocess
import psutil

# Database configuration
db_config = {
    'user': 'admin',
    'password': 'node@123',
    'host': 'localhost',
    'database': 'node-db'
}

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
    try:
        cursor.execute(create_board_health_table)
        print("Table created or verified successfully.")
    except Error as e:
        print(f"Error creating table: {e}")

def get_system_metrics():
    """Fetch the required system metrics."""
    metrics = {}
    try:
        # Fetch CPU temperature
        metrics["cpu_temp"] = psutil.sensors_temperatures()['cpu_thermal'][0].current
        
        # RAM and CPU usage
        metrics["ram_usage"] = psutil.virtual_memory().percent
        metrics["cpu_usage"] = psutil.cpu_percent(interval=1)
        
        # Disk usage
        metrics["disk_usage"] = psutil.disk_usage('/').percent
        
        # Network usage
        net_io = psutil.net_io_counters()
        metrics["net_up"] = net_io.bytes_sent
        metrics["net_down"] = net_io.bytes_recv
        
        # Core voltage and speed
        metrics["core_volts"] = float(subprocess.check_output("vcgencmd measure_volts core", shell=True).decode().strip().split('=')[1].split('V')[0])
        metrics["core_speed"] = float(subprocess.check_output("vcgencmd measure_clock core", shell=True).decode().strip().split('=')[1])
        
        # ARM and GPU memory
        metrics["arm_memory"] = float(subprocess.check_output("vcgencmd get_mem arm", shell=True).decode().strip().split('=')[1].split('M')[0])
        metrics["gpu_memory"] = float(subprocess.check_output("vcgencmd get_mem gpu", shell=True).decode().strip().split('=')[1].split('M')[0])
        
        # Throttled state
        metrics["throttled_state"] = subprocess.check_output("vcgencmd get_throttled", shell=True).decode().strip()
        
        # Uptime
        uptime = subprocess.check_output("uptime -p", shell=True).decode().strip()
        metrics["uptime"] = uptime

    except (subprocess.CalledProcessError, KeyError) as e:
        print(f"Error retrieving system metrics: {e}")
    
    return metrics

def main():
    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            # Check and create tables if they don't exist
            check_and_create_table(cursor)

            while True:
                # Get system metrics
                metrics = get_system_metrics()
                print(metrics)

                # Insert metrics into the database
                cursor.execute("""
                    INSERT INTO board_health 
                    (cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down, core_volts, core_speed, arm_memory, gpu_memory, throttled_state, uptime) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    metrics.get('cpu_temp'), metrics.get('ram_usage'), metrics.get('cpu_usage'), metrics.get('disk_usage'),
                    metrics.get('net_up'), metrics.get('net_down'), metrics.get('core_volts'), metrics.get('core_speed'),
                    metrics.get('arm_memory'), metrics.get('gpu_memory'), metrics.get('throttled_state'), metrics.get('uptime')
                ))

                # Commit the transaction
                connection.commit()

                # Sleep for 5 seconds before the next reading
                time.sleep(5)

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    main()
