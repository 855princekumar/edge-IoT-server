import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

# Create I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)

# Create BME280 object.
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Optionally, you can change the I2C address (if it's not the default 0x76).
# bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)

# Print sensor data.
print(f"Temperature: {bme280.temperature:.2f} °C")
print(f"Humidity: {bme280.humidity:.2f} %")
print(f"Pressure: {bme280.pressure:.2f} hPa")
