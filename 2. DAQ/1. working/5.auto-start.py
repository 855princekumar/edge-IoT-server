#!/usr/bin/env python3
import os
import shutil
import subprocess

SOURCE_FILENAME = "4.0-bme-dsb-sql.py"
DEST_FILENAME = "bme-dsb-sql.py"
DEST_PATH = f"/usr/local/bin/{DEST_FILENAME}"
SERVICE_PATH = "/etc/systemd/system/bme-dsb-sql.service"

def run_command(cmd):
    """Run a shell command with error reporting."""
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f" Command failed: {cmd}")
        print(f"   Error: {e}")
        exit(1)

def main():
    print(" Setting up auto-start for BME+DSB SQL script...\n")

    # 1. Check source file
    if not os.path.exists(SOURCE_FILENAME):
        print(f" Source file '{SOURCE_FILENAME}' not found in current directory.")
        exit(1)

    # 2. Copy and rename
    try:
        shutil.copyfile(SOURCE_FILENAME, DEST_PATH)
        os.chmod(DEST_PATH, 0o755)
        print(f" Copied and renamed to: {DEST_PATH}")
    except Exception as e:
        print(f" Failed to move and chmod the script: {e}")
        exit(1)

    # 3. Ask for username
    user = input(" Enter the username that will run the service (e.g., pi): ").strip()
    if not user:
        print(" Username cannot be empty.")
        exit(1)

    # 4. Create systemd service file
    service_content = f"""[Unit]
Description=IoT Edge Logger for BME280 + DS18B20 + SQL
After=network.target mysql.service

[Service]
ExecStart=/usr/bin/python3 {DEST_PATH}
WorkingDirectory=/usr/local/bin/
StandardOutput=journal
StandardError=journal
Restart=on-failure
User={user}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""

    try:
        with open(SERVICE_PATH, 'w') as f:
            f.write(service_content)
        print(f" Service file created: {SERVICE_PATH}")
    except Exception as e:
        print(f" Failed to write service file: {e}")
        exit(1)

    # 5. Reload and enable systemd service
    try:
        print("\n🔄 Enabling and starting the service...")
        run_command("sudo systemctl daemon-reexec")
        run_command("sudo systemctl daemon-reload")
        run_command("sudo systemctl enable bme-dsb-sql.service")
        run_command("sudo systemctl start bme-dsb-sql.service")
        print("\n📡 Service is now active. Status:")
        run_command("sudo systemctl status bme-dsb-sql.service")
    except Exception as e:
        print(f" Failed to activate service: {e}")
        exit(1)

    print("\n🎉 Setup complete! Script will run automatically on boot.")

if __name__ == "__main__":
    main()
