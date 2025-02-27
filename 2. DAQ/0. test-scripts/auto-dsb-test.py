#!/usr/bin/env python3
import os
import glob
import time
import subprocess

def run_command(command):
    """Run a shell command and return its output."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode(), result.stderr.decode()

def verify_kernel_modules():
    """Check if w1_gpio and w1_therm modules are loaded."""
    print("Verifying One-Wire kernel modules...")
    stdout, _ = run_command("lsmod | grep w1")
    if "w1_gpio" in stdout and "w1_therm" in stdout:
        print("Kernel modules w1_gpio and w1_therm are already loaded.")
    else:
        print("Kernel modules not loaded. Loading now...")
        os.system("sudo modprobe w1-gpio")
        os.system("sudo modprobe w1-therm")
        print("Kernel modules loaded successfully.")

def verify_config_txt():
    """Ensure One-Wire interface is enabled in /boot/firmware/config.txt."""
    print("Verifying /boot/firmware/config.txt configuration...")
    config_file = "/boot/firmware/config.txt"
    
    with open(config_file, 'r') as file:
        config = file.read()
        
    if "dtoverlay=w1-gpio,gpiopin=4" in config:
        print("One-Wire already enabled on GPIO4.")
    else:
        print("Enabling One-Wire on GPIO4...")
        with open(config_file, 'a') as file:
            file.write("\ndtoverlay=w1-gpio,gpiopin=4\n")
        print("Configuration updated.")

def check_sensor_connection():
    """Check if DS18B20 sensor is connected."""
    print("Checking DS18B20 sensor connection...")
    stdout, _ = run_command("ls /sys/bus/w1/devices/")
    if "28-" in stdout:
        sensor_id = stdout.strip().split()[0]
        print(f"Sensor detected: {sensor_id}")
        return sensor_id
    else:
        print("Sensor not detected. Check wiring and connections.")
        return None

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

def test_temperature_sensor(sensor_id):
    """Test if the temperature sensor is working."""
    print("Testing temperature sensor...")
    device_folder = f"/sys/bus/w1/devices/{sensor_id}"
    device_file = device_folder + "/w1_slave"
    
    try:
        while True:
            temperature_c = read_temp(device_file)
            if temperature_c is not None:
                print(f"Temperature: {temperature_c:.2f} °C")
            else:
                print("Error reading temperature.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Temperature reading terminated by user.")

def main():
    verify_kernel_modules()
    verify_config_txt()
    
    sensor_id = check_sensor_connection()
    if sensor_id:
        test_temperature_sensor(sensor_id)
    
    reboot_confirm = input("Do you want to reboot the system now? (y/n): ")
    if reboot_confirm.lower() == 'y':
        print("Rebooting now...")
        os.system("sudo reboot")
    else:
        print("Reboot cancelled. System will not be rebooted.")

if __name__ == "__main__":
    main()
