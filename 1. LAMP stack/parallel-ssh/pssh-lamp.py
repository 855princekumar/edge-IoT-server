from pssh import ParallelSSHClient

# List of all Pi nodes
hosts = [
    "picnode1@10.1.56.211",
    "picnode2@10.1.56.194",
    "picnode3@10.1.56.201",
    "picnode4@10.1.56.243",
    "picnode5@10.1.56.196",
    "picnode6@10.1.56.198",
    "picnode7@10.1.56.199"
]

# SSH Password for all nodes
password = 'node@123'

# Commands to install LAMP stack
commands = [
    'sudo apt update',
    'sudo apt install apache2 -y',
    'sudo systemctl start apache2',
    'sudo systemctl enable apache2',
    'sudo apt install php libapache2-mod-php php-mysql -y',
    'sudo apt install mariadb-server -y',
    'sudo systemctl start mariadb',
    'sudo systemctl enable mariadb',
    'sudo mysql_secure_installation',
    "sudo mysql -e \"CREATE USER 'admin'@'localhost' IDENTIFIED BY 'node@123';\"",
    "sudo mysql -e \"GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' WITH GRANT OPTION;\"",
    'sudo mysql -e "FLUSH PRIVILEGES;"',
    "sudo sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf",
    'sudo systemctl restart mariadb',
    'sudo apt install phpmyadmin php-mbstring php-zip php-gd php-json php-curl -y',
    'sudo phpenmod mbstring',
    'sudo systemctl restart apache2',
    "sudo mysql -e \"CREATE USER 'phpmyadmin'@'localhost' IDENTIFIED BY 'node@123';\"",
    "sudo mysql -e \"GRANT ALL PRIVILEGES ON phpmyadmin.* TO 'phpmyadmin'@'localhost';\"",
    'sudo mysql -e "FLUSH PRIVILEGES;"',
    "echo 'Include /etc/phpmyadmin/apache.conf' | sudo tee -a /etc/apache2/apache2.conf",
    'sudo systemctl restart apache2'
]

# Initialize ParallelSSH client
client = ParallelSSHClient(hosts, password=password)

# Execute commands in parallel
def install_lamp_stack():
    print("Starting LAMP stack installation on all nodes...")
    for command in commands:
        # Run command in parallel on all nodes
        output = client.run_command(command)
        
        # Process output and error for each host
        for host, stdout, stderr in output.items():
            if stdout:
                print(f"Output from {host}: {stdout}")
            if stderr:
                print(f"Errors from {host}: {stderr}")
        
        # Check if there was any issue with the command execution
        failed_hosts = [host for host, result in output.items() if result.exit_code != 0]
        if failed_hosts:
            print(f"Command failed on the following hosts: {', '.join(failed_hosts)}")

    print("LAMP Stack Setup with MariaDB, phpMyAdmin, and remote access complete on all nodes!")

if __name__ == "__main__":
    install_lamp_stack()
