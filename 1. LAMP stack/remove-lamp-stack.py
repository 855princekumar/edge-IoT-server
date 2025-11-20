import os

def remove_phpmyadmin():
    print("Removing phpMyAdmin...")
    os.system('sudo apt purge phpmyadmin php-mbstring php-zip php-gd php-json php-curl -y')
    os.system('sudo apt autoremove -y')
    os.system("sudo sed -i '/Include \\/etc\\/phpmyadmin\\/apache.conf/d' /etc/apache2/apache2.conf")
    os.system('sudo rm -rf /etc/phpmyadmin')
    print("phpMyAdmin removed.")

def remove_mariadb_users():
    print("Removing MariaDB users created earlier...")
    os.system("""sudo mysql -e "DROP USER IF EXISTS 'admin'@'localhost';" """)
    os.system("""sudo mysql -e "DROP USER IF EXISTS 'phpmyadmin'@'localhost';" """)
    os.system('sudo mysql -e "FLUSH PRIVILEGES;"')
    print("MariaDB users removed.")

def rollback_mariadb_config():
    print("Rolling back MariaDB configuration...")

    # Restore bind-address to default
    os.system("sudo sed -i 's/^bind-address.*/#bind-address = 127.0.0.1/' /etc/mysql/mariadb.conf.d/50-server.cnf")

    os.system('sudo systemctl restart mariadb')
    print("MariaDB config restored.")

def remove_mariadb():
    print("Removing MariaDB...")
    os.system('sudo systemctl stop mariadb')
    os.system('sudo systemctl disable mariadb')
    os.system('sudo apt purge mariadb-server mariadb-client -y')
    os.system('sudo apt autoremove -y')
    os.system('sudo rm -rf /var/lib/mysql')
    os.system('sudo rm -rf /etc/mysql')
    print("MariaDB removed.")

def remove_php():
    print("Removing PHP...")
    os.system('sudo apt purge php libapache2-mod-php php-mysql -y')
    os.system('sudo apt autoremove -y')
    print("PHP removed.")

def remove_apache():
    print("Removing Apache...")
    os.system('sudo systemctl stop apache2')
    os.system('sudo systemctl disable apache2')
    os.system('sudo apt purge apache2 apache2-utils apache2-bin apache2.2-common -y')
    os.system('sudo apt autoremove -y')
    os.system('sudo rm -rf /etc/apache2')
    print("Apache removed.")

def cleanup():
    print("Final cleanup...")
    os.system('sudo apt autoremove -y')
    os.system('sudo apt autoclean -y')
    print("Cleanup done.")

if __name__ == "__main__":
    print("Starting rollback of LAMP + phpMyAdmin setup...")

    remove_phpmyadmin()
    remove_mariadb_users()
    rollback_mariadb_config()
    remove_mariadb()
    remove_php()
    remove_apache()
    cleanup()

    print("\nRollback complete! System restored to pre-LAMP state.")
