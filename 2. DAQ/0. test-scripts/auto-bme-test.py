import os
import subprocess
import sys

# List of required packages
REQUIRED_PACKAGES = [
    "board",
    "adafruit-circuitpython-busdevice",
    "adafruit-circuitpython-bme280"
]

def check_and_install(package):
    """
    Check if a package is installed. If not, install it using pip with --break-system-packages.
    """
    try:
        __import__(package)
        print(f"{package} is already installed.")
    except ImportError:
        print(f"{package} not found. Attempting to install...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "--break-system-packages"],
                check=True
            )
            print(f"{package} installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")

def main():
    # Ensure pip is installed
    print("Checking dependencies...")
    try:
        subprocess.run(["pip", "--version"], check=True, stdout=subprocess.DEVNULL)
        print("pip is installed.")
    except subprocess.CalledProcessError:
        print("pip not found. Please install pip and try again.")
        sys.exit(1)

    # Install required packages
    for package in REQUIRED_PACKAGES:
        check_and_install(package)

    # Import sensor-specific modules after ensuring installation
    try:
        import board
        import busio
        from adafruit_bme280 import basic as adafruit_bme280

        # Initialize I2C and BME280 sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

        # Print sensor data
        print(f"Temperature: {bme280.temperature:.2f} °C")
        print(f"Humidity: {bme280.humidity:.2f} %")
        print(f"Pressure: {bme280.pressure:.2f} hPa")

    except ImportError as e:
        print(f"Error importing module: {e}")
        print("Please ensure all dependencies are installed correctly.")

if __name__ == "__main__":
    main()
