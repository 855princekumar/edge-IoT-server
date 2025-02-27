import os
import shutil
import requests
import tarfile
import subprocess
import glob
import sys

# Define paths and constants
phpmyadmin_dir = "/usr/share/phpmyadmin"
backup_dir = "/usr/share/phpmyadmin_backup"
download_url = "https://www.phpmyadmin.net/downloads/phpMyAdmin-latest-all-languages.tar.gz"
download_path = "/tmp/phpmyadmin-latest.tar.gz"
extract_path = "/tmp/phpmyadmin_extracted"

# Function to log and execute shell commands
def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr.decode()}")
        return False
    return True

# Step 1: Backup the current phpMyAdmin directory
def backup_phpmyadmin():
    print("Backing up the current phpMyAdmin...")
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    shutil.copytree(phpmyadmin_dir, backup_dir)
    print(f"Backup completed at {backup_dir}")

# Step 2: Download the latest phpMyAdmin version
def download_phpmyadmin():
    print("Downloading the latest phpMyAdmin version...")
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        with open(download_path, 'wb') as f:
            f.write(response.content)
        print("Download completed.")
    else:
        print(f"Failed to download phpMyAdmin. HTTP status code: {response.status_code}")
        sys.exit(1)

# Step 3: Extract the downloaded tarball
def extract_phpmyadmin():
    print("Extracting phpMyAdmin...")
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    os.makedirs(extract_path)
    
    with tarfile.open(download_path, "r:gz") as tar:
        tar.extractall(extract_path)
    print("Extraction completed.")

# Step 4: Find the extracted phpMyAdmin directory
def find_new_phpmyadmin_dir():
    print("Looking for the new phpMyAdmin directory...")
    extracted_dirs = glob.glob(os.path.join(extract_path, "phpMyAdmin-*"))
    if extracted_dirs:
        print(f"Found new phpMyAdmin directory: {extracted_dirs[0]}")
        return extracted_dirs[0]
    else:
        print("Error: New phpMyAdmin directory not found.")
        sys.exit(1)

# Step 5: Replace the current phpMyAdmin with the updated version
def replace_phpmyadmin(new_phpmyadmin_dir):
    print("Replacing the current phpMyAdmin with the new version...")
    if os.path.exists(new_phpmyadmin_dir):
        shutil.rmtree(phpmyadmin_dir)
        shutil.move(new_phpmyadmin_dir, phpmyadmin_dir)
    else:
        print("Error: New phpMyAdmin directory not found.")
        sys.exit(1)
    print("Replacement completed.")

# Step 6: Restore the config.inc.php file
def restore_config():
    config_file = os.path.join(backup_dir, "config.inc.php")
    if os.path.exists(config_file):
        shutil.copy(config_file, phpmyadmin_dir)
        print("config.inc.php restored.")
    else:
        print("Warning: config.inc.php not found in the backup!")

# Step 7: Set correct permissions
def set_permissions():
    print("Setting permissions for phpMyAdmin...")
    if not run_command(f"sudo chown -R www-data:www-data {phpmyadmin_dir}"):
        print("Failed to set ownership.")
    if not run_command(f"sudo chmod -R 755 {phpmyadmin_dir}"):
        print("Failed to set permissions.")

# Step 8: Restart Apache server
def restart_apache():
    print("Restarting Apache server...")
    if not run_command("sudo systemctl restart apache2"):
        print("Failed to restart Apache. Please check logs for more information.")

# Step 9: Error handling function
def handle_errors():
    print("Analyzing errors and attempting to resolve...")

    # Check if Apache is running
    apache_status = run_command("sudo systemctl status apache2")
    if not apache_status:
        print("Apache server is not running. Attempting to start Apache...")
        run_command("sudo systemctl start apache2")
    
    # Check Apache logs for errors
    print("Checking Apache logs...")
    run_command("sudo tail -n 20 /var/log/apache2/error.log")

# Main function to execute the update process
def update_phpmyadmin():
    try:
        backup_phpmyadmin()
        download_phpmyadmin()
        extract_phpmyadmin()
        new_phpmyadmin_dir = find_new_phpmyadmin_dir()
        replace_phpmyadmin(new_phpmyadmin_dir)
        restore_config()
        set_permissions()
        restart_apache()
        print("phpMyAdmin update completed successfully!")
    except Exception as e:
        print(f"An error occurred during the update process: {e}")
        handle_errors()

# Run the update process
if __name__ == "__main__":
    update_phpmyadmin()
