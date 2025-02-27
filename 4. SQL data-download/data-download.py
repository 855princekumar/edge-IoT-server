import mysql.connector
import subprocess
import sys
import warnings

# Suppress specific warning about pandas and SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy connectable.*")

# Function to check and install pandas if not available
def install_pandas():
    try:
        import pandas as pd
    except ImportError:
        print("Pandas is not installed. Installing...")
        try:
            # Try installing pandas
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
        except subprocess.CalledProcessError as e:
            print("Error installing pandas. Trying with --break-system-packages...")
            try:
                # Try installing pandas with --break-system-packages
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "pandas"])
            except subprocess.CalledProcessError:
                print("Failed to install pandas. Please install it manually.")
                sys.exit(1)

# Install pandas if necessary
install_pandas()

# Import pandas now that we are sure it is installed
import pandas as pd

# Database connection details
host = 'pi5node2'  #replace with your host name
username = 'admin' #replace with your username
password = 'node@123' #replace with your password
db_name = 'node-db' #replace with your DataBase name

# Establish the connection to the MySQL database
conn = mysql.connector.connect(
    host=host,
    user=username,
    password=password,
    database=db_name
)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Query to retrieve all table names from the database
cursor.execute("SHOW TABLES")

# Fetch all tables
tables = cursor.fetchall()

# Iterate over each table and download its content as CSV
for (table,) in tables:
    # Query to select all rows from the table
    query = f"SELECT * FROM {table}"
    
    # Using pandas to execute the query and save the result as a CSV
    df = pd.read_sql(query, conn)
    
    # Define the CSV file path for the table
    csv_filename = f"{table}.csv"
    
    # Save the table to CSV
    df.to_csv(csv_filename, index=False)
    print(f"Table '{table}' has been downloaded as {csv_filename}")

# Close the cursor and connection
cursor.close()
conn.close()
