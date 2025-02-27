#!/usr/bin/env python3
import os
import glob
import time

# Load the required kernel modules for One-Wire interface
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Base directory for the One-Wire device files
base_dir = '/sys/bus/w1/devices/'
# Find the directory for the DS18B20 sensor
device_folder = glob.glob(base_dir + '28*')[0]
# The file that contains the temperature reading
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    """Read the raw temperature data from the sensor."""
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    """Parse the raw temperature data and return the temperature."""
    lines = read_temp_raw()
    # Wait until the sensor output is valid
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    # Find the position of the temperature data
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        # Extract and convert the temperature value
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    else:
        return None

try:
    while True:
        temperature_c = read_temp()
        if temperature_c is not None:
            print(f"Temperature: {temperature_c:.2f} °C")
        else:
            print("Error reading temperature.")
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated by user.")
