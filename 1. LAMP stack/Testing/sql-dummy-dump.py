import mysql.connector
from mysql.connector import errorcode

# Database connection parameters
db_config = {
    'user': 'jetson',
    'password': 'node@123',
    'host': '10.1.58.87',
    'database': 'iot-node'
}

# Create a connection to the MySQL database
try:
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # SQL query to check if the table exists
    table_name = 'dummy_data'
    check_table_query = f"""
    SELECT COUNT(*)
    FROM information_schema.tables 
    WHERE table_schema = '{db_config['database']}' 
    AND table_name = '{table_name}';
    """
    cursor.execute(check_table_query)
    result = cursor.fetchone()

    # If the table doesn't exist, create it
    if result[0] == 0:
        create_table_query = f"""
        CREATE TABLE {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            node_name VARCHAR(50),
            temperature FLOAT,
            humidity FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        print(f"Table '{table_name}' created successfully.")

    # Insert dummy data into the table
    insert_dummy_data_query = f"""
    INSERT INTO {table_name} (node_name, temperature, humidity)
    VALUES (%s, %s, %s);
    """
    dummy_data = [
        ('Node_A', 23.5, 45.2),
        ('Node_B', 26.3, 50.7),
        ('Node_C', 22.9, 47.5)
    ]
    
    cursor.executemany(insert_dummy_data_query, dummy_data)
    cnx.commit()  # Save changes

    print(f"Inserted {cursor.rowcount} rows of dummy data into '{table_name}'.")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your username or password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist.")
    else:
        print(err)

finally:
    if cursor:
        cursor.close()
    if cnx:
        cnx.close()
