import subprocess
import mysql.connector
from mysql.connector import Error

def install_and_configure_chrony():
    try:
        # Check for Chrony
        chrony_installed = subprocess.run(["which", "chronyd"], capture_output=True, text=True).returncode == 0

        if not chrony_installed:
            print("Chrony is not installed. Installing Chrony...")
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "chrony"], check=True)

        # Start and enable Chrony
        print("Starting and enabling Chrony service...")
        try:
            subprocess.run(["sudo", "systemctl", "start", "chrony"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "chrony"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error while starting or enabling Chrony service: {e}")

        # Force time synchronization
        print("Forcing time synchronization with Chrony...")
        try:
            subprocess.run(["sudo", "chronyc", "makestep"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error forcing time synchronization: {e}")

    except subprocess.CalledProcessError as e:
        print(f"Error while installing and configuring Chrony: {e}")

def configure_mariadb():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='node@123'
        )

        cursor = conn.cursor()

        # Configure MariaDB time zone
        tz_string = '+05:30'  # Store the time zone string in a variable
        print(f"Configuring MariaDB time zone to {tz_string}...")
        query = f"SET GLOBAL time_zone='{tz_string}'"
        try:
            cursor.execute(query)
            conn.commit()
        except Error as e:
            print(f"Error configuring MariaDB time zone: {e}")

    except Error as e:
        print(f"Error while configuring MariaDB: {e}")

if __name__ == "__main__":
    install_and_configure_chrony()
    configure_mariadb()