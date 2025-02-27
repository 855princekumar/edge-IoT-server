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

if __name__ == "__main__":
    install_apache()
    install_php()
    install_mariadb()
    secure_mariadb()
    create_mariadb_user()
    configure_mariadb_remote_access()
    install_phpmyadmin()
    configure_phpmyadmin()
    print("LAMP Stack Setup with MariaDB, phpMyAdmin, and remote access complete!")
