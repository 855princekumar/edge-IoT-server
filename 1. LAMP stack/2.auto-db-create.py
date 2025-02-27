import os
import subprocess
import sys
from mysql.connector import connect, Error

def install_dependencies():
    """
    Check and install necessary dependencies.
    """
    try:
        # Check and install `mysql-connector-python`
        try:
            import mysql.connector  # Check if the package exists
        except ImportError:
            print("Dependency 'mysql-connector-python' not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "mysql-connector-python"])

        # Check if MariaDB server is installed
        mariadb_installed = subprocess.run(["which", "mysql"], capture_output=True, text=True)
        if not mariadb_installed.stdout.strip():
            print("MariaDB server not found. Installing...")
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "mariadb-server"])
        print("All dependencies are installed.")
    except Exception as e:
        print(f"Error during dependency installation: {e}")
        sys.exit(1)

def main():
    """
    Main logic to connect to MariaDB, check database existence, and create it if necessary.
    """
    try:
        # Connect to the MariaDB server
        connection = connect(
            host="localhost",
            user="admin",
            password="node@123"
        )

        if connection.is_connected():
            print("Connected to MariaDB successfully.")

            # Create a cursor object
            cursor = connection.cursor()

            # Check if the database 'node-db' exists
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            db_exists = any(db[0] == "node-db" for db in databases)

            if not db_exists:
                # Create the database if it does not exist
                cursor.execute("CREATE DATABASE `node-db`;")
                print("Database 'node-db' created successfully.")

                # Verify the database creation
                cursor.execute("SHOW DATABASES;")
                databases = cursor.fetchall()
                if any(db[0] == "node-db" for db in databases):
                    print("Verified: Database 'node-db' exists.")
                else:
                    print("Error: Database 'node-db' creation could not be verified.")
            else:
                print("Database 'node-db' already exists.")

            # Close the cursor
            cursor.close()

    except Error as e:
        print(f"Error while connecting to MariaDB: {e}")
    finally:
        if "connection" in locals() and connection.is_connected():
            # Close the connection
            connection.close()
            print("MariaDB connection closed.")

if __name__ == "__main__":
    install_dependencies()
    main()
