import time
import sqlite3
import board
import adafruit_bme280
import psutil
import subprocess

# Constants
DB_PATH = '/home/nodeL3/daq/sensor_data.db'
BME280_ADDRESS = 0x77

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create tables if not exist
def create_tables():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inner_sensor (
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        pressure REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS outer_sensor (
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS board_health (
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        cpu_temp REAL,
        ram_usage REAL,
        cpu_usage REAL,
        disk_usage REAL,
        net_up REAL,
        net_down REAL,
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
    ''')

    conn.commit()

def log_sensor_data():
    # Setup BME280
    i2c = board.I2C()
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=BME280_ADDRESS)

    while True:
        # Read BME280 sensor data
        try:
            temp_bme280 = bme280.temperature
            humidity_bme280 = bme280.humidity
            pressure_bme280 = bme280.pressure
            cursor.execute('''
            INSERT INTO inner_sensor (temperature, humidity, pressure)
            VALUES (?, ?, ?)
            ''', (temp_bme280, humidity_bme280, pressure_bme280))
        except Exception as e:
            print(f"Error reading BME280 sensor: {e}")

        # Read DS18B20 sensor data
        try:
            ds18b20_temp = get_ds18b20_temp()
            cursor.execute('''
            INSERT INTO outer_sensor (temperature)
            VALUES (?)
            ''', (ds18b20_temp,))
        except Exception as e:
            print(f"Error reading DS18B20 sensor: {e}")

        # Read board health data
        try:
            board_health = get_board_health()
            cursor.execute('''
            INSERT INTO board_health (
                cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down,
                arm_speed, core_speed, h264_speed, isp_speed, v3d_speed, uart_speed,
                emmc_speed, pixel_speed, hdmi_speed, core_volts, sdram_c_volts,
                sdram_i_volts, sdram_p_volts, arm_memory, gpu_memory, throttled_state
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', board_health)
        except Exception as e:
            print(f"Error reading board health: {e}")

        conn.commit()
        time.sleep(60)  # Wait before next read

def get_ds18b20_temp():
    try:
        # Example DS18B20 temperature reading
        # Implement reading logic based on your setup
        # Replace with actual temperature reading code
        return 25.0  # Placeholder
    except Exception as e:
        print(f"Error reading DS18B20 sensor: {e}")
        return None

def get_board_health():
    # Example implementation, replace with actual board health monitoring
    try:
        cpu_temp = psutil.sensors_temperatures().get('coretemp', [])[0].current
        ram_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=1)
        disk_usage = psutil.disk_usage('/').percent
        net_up = psutil.net_io_counters().bytes_sent
        net_down = psutil.net_io_counters().bytes_recv
        arm_speed = 0
        core_speed = 0
        h264_speed = 0
        isp_speed = 0
        v3d_speed = 0
        uart_speed = 0
        emmc_speed = 0
        pixel_speed = 0
        hdmi_speed = 0
        core_volts = 0
        sdram_c_volts = 0
        sdram_i_volts = 0
        sdram_p_volts = 0
        arm_memory = psutil.virtual_memory().available
        gpu_memory = 0
        throttled_state = 'OK'
        
        return (cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down,
                arm_speed, core_speed, h264_speed, isp_speed, v3d_speed, uart_speed,
                emmc_speed, pixel_speed, hdmi_speed, core_volts, sdram_c_volts,
                sdram_i_volts, sdram_p_volts, arm_memory, gpu_memory, throttled_state)
    except Exception as e:
        print(f"Error reading board health: {e}")
        return (None,) * 21

if __name__ == "__main__":
    create_tables()
    log_sensor_data()
