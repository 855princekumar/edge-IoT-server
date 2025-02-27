import os
import subprocess
import sys

# Function to run shell commands and capture output
def run_command(command, use_sudo=False):
    try:
        if use_sudo:
            command = f"sudo {command}"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error while running command '{command}': {e.stderr}")
        return None

# Install uptimed and related packages
def install_uptimed():
    print("Installing uptimed...")
    try:
        # Ensure uptimed is installed without apt-get update
        output = run_command("apt-get install -y uptimed", use_sudo=True)
        if output:
            print(output)
        else:
            print("Failed to install uptimed.")
            sys.exit(1)
    except Exception as e:
        print(f"Error while installing uptimed: {str(e)}")
        sys.exit(1)

# Set up crontab for logging every 15 minutes
def setup_crontab():
    print("Setting up crontab for uptime logging every 15 minutes...")
    crontab_entry = "*/15 * * * * uprecords >> /home/nodeL2/uptime_log.txt 2>&1"
    try:
        # Get the current crontab entries for root
        crontab_list = run_command("crontab -l", use_sudo=True)
        if crontab_list:
            if crontab_entry not in crontab_list:
                # Add the entry if it's not already there
                with open("/tmp/crontab", "w") as f:
                    f.write(crontab_list + "\n" + crontab_entry + "\n")  # Ensure newline at EOF
                run_command("crontab /tmp/crontab", use_sudo=True)
                print("Crontab entry added successfully.")
            else:
                print("Crontab entry already exists.")
        else:
            print("No crontab exists for root. Creating new crontab.")
            with open("/tmp/crontab", "w") as f:
                f.write(crontab_entry + "\n")
            run_command("crontab /tmp/crontab", use_sudo=True)
            print("Crontab created successfully.")
    except Exception as e:
        print(f"Error while setting up crontab: {str(e)}")
        sys.exit(1)

# Check and fix uptimed database issue
def fix_uptimed_db_issue():
    print("Checking uptimed database...")
    try:
        # Run uprecords to see if there's a database issue
        output = run_command("uprecords")
        if "no useable database found" in output:
            print("No usable database found. Attempting to fix...")
            # Reinitialize the uptimed database
            run_command("sudo uptimed --setup", use_sudo=True)
            print("Uptimed database has been reinitialized.")
        else:
            print("Uptimed is working correctly.")
    except Exception as e:
        print(f"Error while checking or fixing uptimed database: {str(e)}")
        sys.exit(1)

# Set up logrotate for uptime_log.txt to manage log rotation
def setup_logrotate():
    print("Setting up logrotate for uptime_log.txt...")
    logrotate_conf = """
/home/nodeL2/uptime_log.txt {
    rotate 7
    daily
    compress
    missingok
    notifempty
    create 644 nodeL2 nodeL2
}
    """
    try:
        # Create a logrotate configuration file for uptime_log with sudo
        with open("/tmp/uptime_log.conf", "w") as f:
            f.write(logrotate_conf)
        run_command("sudo mv /tmp/uptime_log.conf /etc/logrotate.d/uptime_log", use_sudo=True)
        print("Logrotate configuration for uptime_log.txt has been set up.")
    except Exception as e:
        print(f"Error while setting up logrotate: {str(e)}")
        sys.exit(1)

# Main function to execute the setup
def main():
    # Step 1: Install uptimed
    install_uptimed()

    # Step 2: Check and fix database issue if needed
    fix_uptimed_db_issue()

    # Step 3: Setup crontab for logging uptime every 15 minutes
    setup_crontab()

    # Step 4: Set up logrotate for uptime_log.txt
    setup_logrotate()

    print("Uptimed setup, cron job, and logrotate configured successfully!")

if __name__ == "__main__":
    main()
