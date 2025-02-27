import mysql.connector
from mysql.connector import Error

def main():
    try:
        # Connect to the MariaDB server
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='node@123'
        )

        if connection.is_connected():
            print("Connected to MariaDB successfully.")

            # Create a cursor object
            cursor = connection.cursor()

            # Check if the database 'node-db' exists
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            db_exists = any(db[0] == 'node-db' for db in databases)

            if not db_exists:
                # Create the database if it does not exist
                cursor.execute("CREATE DATABASE `node-db`;")
                print("Database 'node-db' created successfully.")

                # Verify the database creation
                cursor.execute("SHOW DATABASES;")
                databases = cursor.fetchall()
                if any(db[0] == 'node-db' for db in databases):
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
        if connection.is_connected():
            # Close the connection
            connection.close()
            print("MariaDB connection closed.")

if __name__ == "__main__":
    main()
