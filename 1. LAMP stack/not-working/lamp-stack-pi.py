import os

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

def install_mysql():
    print("Installing MySQL...")
    os.system('sudo apt install mysql-server -y')
    os.system('sudo systemctl start mysql')
    os.system('sudo systemctl enable mysql')
    print("MySQL installation complete.")

def create_mysql_user():
    print("Creating MySQL user 'admin' with full privileges...")
    create_user_query = """
    sudo mysql -e "CREATE USER 'admin'@'%' IDENTIFIED BY 'node@123';"
    sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;"
    sudo mysql -e "FLUSH PRIVILEGES;"
    """
    os.system(create_user_query)
    print("MySQL user 'admin' created with full privileges.")

def configure_mysql_remote_access():
    print("Configuring MySQL for remote access...")
    # Replace 'bind-address' value in MySQL config to allow remote connections
    os.system("sudo sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf")
    os.system('sudo systemctl restart mysql')
    print("MySQL remote access configured.")

def install_phpmyadmin():
    print("Installing phpMyAdmin...")
    os.system('sudo apt install phpmyadmin php-mbstring php-zip php-gd php-json php-curl -y')
    os.system('sudo phpenmod mbstring')
    os.system('sudo systemctl restart apache2')
    print("phpMyAdmin installation complete.")

def configure_phpmyadmin():
    print("Configuring phpMyAdmin...")
    config_command = """echo 'Include /etc/phpmyadmin/apache.conf' | sudo tee -a /etc/apache2/apache2.conf"""
    os.system(config_command)
    os.system('sudo systemctl restart apache2')
    print("phpMyAdmin configuration complete.")

if __name__ == "__main__":
    install_apache()
    install_php()
    install_mysql()
    create_mysql_user()
    configure_mysql_remote_access()
    install_phpmyadmin()
    configure_phpmyadmin()
    print("LAMP Stack Setup with MySQL remote access and phpMyAdmin Complete!")
