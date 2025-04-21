import mysql.connector
from datetime import datetime
import hashlib

def create_tables():
    try:
        # Database connection
        conn = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="node@123",
            database="node-db"
        )
        
        cursor = conn.cursor()
        
        # Create nodes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `node-stat` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `node_name` VARCHAR(255) NOT NULL,
            `node_ip` VARCHAR(15) NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY `unique_ip` (`node_ip`),
            UNIQUE KEY `unique_name` (`node_name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Create users table with hashed passwords
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `user-credentials` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `username` VARCHAR(255) NOT NULL,
            `password_hash` VARCHAR(255) NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY `unique_username` (`username`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Add default admin user if not exists
        default_password = "node@123"
        salt = "somesalt"  # In production, use unique salt per user
        password_hash = hashlib.sha256((default_password + salt).encode()).hexdigest()
        
        cursor.execute("SELECT id FROM `user-credentials` WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO `user-credentials` (username, password_hash) VALUES (%s, %s)",
                ('admin', password_hash)
            )
        
        print("Tables created successfully")
        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_tables()