import os
import subprocess
import zipfile
import mysql.connector
from datetime import datetime

# Database Credentials and Configuration
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASS = "node@123"
DB_NAME = "node-db"
OUTPUT_DIR = "/tmp/node_db_backup"
ZIP_FILE = "/tmp/node_db_backup.zip"

def connect_to_database():
    """Establish connection to the MariaDB database."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        print("[INFO] Connected to database.")
        return conn
    except mysql.connector.Error as err:
        print(f"[ERROR] Database connection failed: {err}")
        exit(1)

def export_tables_to_sql(conn):
    """Export all tables in the database to SQL files."""
    cursor = conn.cursor()
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        file_path = os.path.join(OUTPUT_DIR, f"{table_name}.sql")
        print(f"[INFO] Exporting table {table_name} to {file_path}...")
        command = f"mysqldump -u {DB_USER} -p{DB_PASS} {DB_NAME} {table_name} > {file_path}"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"[ERROR] Failed to export table {table_name}: {result.stderr.decode()}")
            exit(1)
        else:
            print(f"[INFO] Table {table_name} exported successfully.")

    cursor.close()
    print("[INFO] All tables exported.")

def zip_sql_files():
    """Zip all exported SQL files."""
    print(f"[INFO] Creating zip archive at {ZIP_FILE}...")
    with zipfile.ZipFile(ZIP_FILE, "w") as zipf:
        for root, _, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file)
    print(f"[INFO] SQL files zipped into {ZIP_FILE}.")

def validate_zip():
    """Validate the integrity of the zip file."""
    print(f"[INFO] Validating zip file {ZIP_FILE}...")
    try:
        with zipfile.ZipFile(ZIP_FILE, 'r') as zipf:
            if zipf.testzip() is None:
                print("[INFO] Zip file validation passed.")
            else:
                print("[ERROR] Zip file is corrupted.")
                exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to validate zip file: {e}")
        exit(1)

def drop_all_tables(conn):
    """Drop all tables in the database."""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        print(f"[INFO] Dropping table {table_name}...")
        cursor.execute(f"DROP TABLE {table_name};")
    
    cursor.close()
    print("[INFO] All tables dropped. Database is fresh now.")

def cleanup():
    """Remove SQL files after zipping."""
    print("[INFO] Cleaning up temporary SQL files...")
    for root, _, files in os.walk(OUTPUT_DIR):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(OUTPUT_DIR)
    print("[INFO] Temporary SQL files removed.")

def main():
    """Main script execution."""
    print("[INFO] Script started.")
    conn = connect_to_database()
    try:
        export_tables_to_sql(conn)
        zip_sql_files()
        validate_zip()
        drop_all_tables(conn)
        cleanup()
    finally:
        conn.close()
        print("[INFO] Database connection closed.")

if __name__ == "__main__":
    main()
