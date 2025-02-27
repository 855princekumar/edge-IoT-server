import os
import subprocess
import getpass

def run_command(command):
    """Run a shell command and print output."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Error: {}".format(stderr.decode("utf-8").strip()))
    else:
        print(stdout.decode("utf-8").strip())

def install_docker():
    print("Updating package lists...")
    run_command("apt-get update -y")

    print("Installing prerequisite packages...")
    run_command("apt-get install -y apt-transport-https ca-certificates curl software-properties-common")

    print("Adding Docker's official GPG key...")
    run_command("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -")

    print("Setting up the Docker stable repository...")
    run_command("add-apt-repository \"deb [arch=arm64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\"")

    print("Updating package lists again...")
    run_command("apt-get update -y")

    print("Installing Docker...")
    run_command("apt-get install -y docker-ce")

    print("Adding current user to Docker group...")
    username = getpass.getuser()
    run_command("groupadd docker || true")  # Create docker group if it doesn't exist
    run_command(f"usermod -aG docker {username}")

    print("Enabling and starting Docker service...")
    run_command("systemctl enable docker")
    run_command("systemctl start docker")

def install_docker_compose():
    print("Downloading Docker Compose binary...")
    # Corrected download link to match architecture
    run_command("curl -L \"https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-linux-aarch64\" -o /usr/local/bin/docker-compose")

    print("Applying executable permissions to the Docker Compose binary...")
    run_command("chmod +x /usr/local/bin/docker-compose")

    print("Creating a symbolic link (optional)...")
    run_command("ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose || true")  # Skip if link exists

    print("Verifying Docker Compose installation...")
    run_command("docker-compose --version")

def refresh_group_membership():
    print("Refreshing group membership for Docker access...")
    run_command("newgrp docker")

if __name__ == "__main__":
    install_docker()
    install_docker_compose()
    refresh_group_membership()
    print("Docker and Docker Compose installation completed. You can now run Docker commands without sudo.")
