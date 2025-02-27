import os
import sys
import subprocess

# Helper function to install pip packages
def install_package(package_name, force=False):
    try:
        # Check if the package is already installed
        subprocess.check_call(["pip", "show", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{package_name} is already installed.")
        return True
    except subprocess.CalledProcessError:
        print(f"{package_name} not found. Attempting to install...")
        try:
            install_cmd = ["pip", "install", package_name]
            # For Raspberry Pi or specific systems, use --break-system-packages if force is enabled
            if force:
                install_cmd.append("--break-system-packages")
            subprocess.check_call(install_cmd)
            print(f"{package_name} installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package_name}: {e}")
            return False

# Check and install all dependencies
def check_dependencies():
    print("Checking dependencies...")
    pending_tasks = []

    # Check for pip
    try:
        subprocess.check_call(["pip", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("pip is installed.")
    except subprocess.CalledProcessError:
        print("pip is not installed. Attempting to install pip...")
        os.system('sudo apt install python3-pip -y')
        try:
            subprocess.check_call(["pip", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("pip installed successfully.")
        except subprocess.CalledProcessError:
            pending_tasks.append("Install pip manually.")
            print("pip installation failed. Please install manually.")

    # Check for mysql-connector-python
    is_raspberry_pi = os.uname().machine.startswith("arm")
    force_install = is_raspberry_pi
    if not install_package("mysql-connector-python", force=force_install):
        pending_tasks.append("Install mysql-connector-python manually.")

    # Return list of pending tasks
    return pending_tasks

def install_apache():
    print("Installing Apache Web Server...")
    os.system('sudo apt update')
    os.system('sudo apt install apache2 -y')
    os.system('sudo systemctl start apache2')
    os.system('sudo systemctl enable apache2')
    print("Apache installation complete.")

def install_php():
    print("Installing PHP...")
    os.system('sudo apt install php libapache2-mod-php php-mysql -y')
    print("PHP installation complete.")

def install_mariadb():
    print("Installing MariaDB Server...")
    os.system('sudo apt install mariadb-server -y')
    os.system('sudo systemctl start mariadb')
    os.system('sudo systemctl enable mariadb')
    print("MariaDB installation complete.")

def secure_mariadb():
    print("Securing MariaDB...")
    os.system('sudo mysql_secure_installation')
    print("MariaDB secured.")

def create_mariadb_user():
    print("Creating MariaDB user 'admin' with full privileges...")
    os.system("""sudo mysql -e "CREATE USER 'admin'@'localhost' IDENTIFIED BY 'node@123';" """)
    os.system("""sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' WITH GRANT OPTION;" """)
    os.system('sudo mysql -e "FLUSH PRIVILEGES;"')
    print("MariaDB user 'admin' created with full privileges.")

def configure_mariadb_remote_access():
    print("Configuring MariaDB for remote access...")
    os.system("sudo sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf")
    os.system('sudo systemctl restart mariadb')
    print("MariaDB remote access configured.")

def install_phpmyadmin():
    print("Installing phpMyAdmin...")
    os.system('sudo apt install phpmyadmin php-mbstring php-zip php-gd php-json php-curl -y')
    os.system('sudo phpenmod mbstring')
    os.system('sudo systemctl restart apache2')
    print("phpMyAdmin installation complete.")

def configure_phpmyadmin():
    print("Configuring phpMyAdmin...")
    os.system('sudo mysql -e "CREATE USER \'phpmyadmin\'@\'localhost\' IDENTIFIED BY \'node@123\';"')
    os.system('sudo mysql -e "GRANT ALL PRIVILEGES ON phpmyadmin.* TO \'phpmyadmin\'@\'localhost\';"')
    os.system('sudo mysql -e "FLUSH PRIVILEGES;"')

    # Include phpMyAdmin config in Apache
    config_command = "echo 'Include /etc/phpmyadmin/apache.conf' | sudo tee -a /etc/apache2/apache2.conf"
    os.system(config_command)
    os.system('sudo systemctl restart apache2')
    print("phpMyAdmin configuration complete.")

def create_database():
    print("Finalizing setup by creating database 'node-db'...")

    def attempt_database_creation():
        try:
            # Connect to MariaDB using admin credentials
            connection = mysql.connector.connect(
                host='localhost',
                user='admin',
                password='node@123'
            )

            if connection.is_connected():
                print("Connected to MariaDB successfully for database creation.")

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
            return False
        finally:
            if 'connection' in locals() and connection.is_connected():
                # Close the connection
                connection.close()
                print("MariaDB connection closed.")
        return True

    # Attempt database creation
    if not attempt_database_creation():
        print("Custom DB not created as there's some technical fault. Please login and create one manually.")

if __name__ == "__main__":
    pending_tasks = check_dependencies()
    install_apache()
    install_php()
    install_mariadb()
    secure_mariadb()
    create_mariadb_user()
    configure_mariadb_remote_access()
    install_phpmyadmin()
    configure_phpmyadmin()
    create_database()

    if pending_tasks:
        print("\nThe following tasks need to be done manually:")
        for task in pending_tasks:
            print(f"- {task}")

    print("LAMP Stack Setup with MariaDB, phpMyAdmin, and 'node-db' database creation complete!")
