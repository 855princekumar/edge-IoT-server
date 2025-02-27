import os
import subprocess

def run_command(command, check=True):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, check=check, shell=True)
        print(f"Successfully ran: {command}")
    except subprocess.CalledProcessError:
        print(f"Error running: {command}")

def check_csi_camera_driver():
    """Check if the CSI camera driver is loaded and load it if necessary."""
    print("Checking for CSI camera driver (bcm2835-v4l2)...")
    result = subprocess.run("lsmod | grep bcm2835_v4l2", shell=True, stdout=subprocess.PIPE)
    
    if result.returncode != 0:
        print("CSI camera driver is not installed. Installing the driver...")
        run_command("sudo modprobe bcm2835-v4l2")
        # Add the module to /etc/modules to load on boot
        run_command("echo 'bcm2835-v4l2' | sudo tee -a /etc/modules")
    else:
        print("CSI camera driver is already installed.")

def install_required_packages():
    """Install the required drivers and tools for CSI and USB cameras."""
    print("Installing required drivers and packages (v4l2, ffmpeg, etc.)...")
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y v4l-utils ffmpeg")

def install_docker():
    """Install Docker on Raspberry Pi."""
    print("Installing Docker...")
    run_command("curl -fsSL https://get.docker.com -o get-docker.sh")
    run_command("sudo sh get-docker.sh")

def reinstall_docker_compose():
    """Re-install Docker Compose on Raspberry Pi."""
    print("Re-installing Docker Compose...")
    
    # Remove the existing docker-compose if present
    run_command("sudo rm /usr/local/bin/docker-compose", check=False)
    
    # Download and install the correct version of docker-compose
    run_command('sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose')
    
    # Make docker-compose executable
    run_command("sudo chmod +x /usr/local/bin/docker-compose")
    
    # Verify the installation
    run_command("docker-compose --version")

def add_user_to_docker_group():
    """Add the current user to the Docker group to run Docker without sudo."""
    print("Adding user to the Docker group...")
    run_command("sudo usermod -aG docker $USER")

def create_motioneye_directory():
    """Create directory for MotionEye configuration."""
    print("Creating MotionEye directory...")
    run_command("mkdir ~/motioneye")
    run_command("cd ~/motioneye")

def create_docker_compose_file():
    """Create docker-compose.yml file for MotionEye."""
    print("Creating docker-compose.yml for MotionEye...")
    docker_compose_content = '''
    version: '3.7'
    services:
      motioneye:
        image: ghcr.io/motioneye-project/motioneye:edge
        container_name: motioneye
        restart: always
        ports:
          - "8765:8765"
          - "9081:9081"
        volumes:
          - ./config:/etc/motioneye
          - ./media:/var/lib/motioneye
        environment:
          - "TZ=Asia/Kolkata"  # Timezone set to India
        devices:
          - "/dev/video1:/dev/video1"  # USB camera
          - "/dev/video0:/dev/video0"  # CSI camera
    '''
    with open(os.path.expanduser("~/motioneye/docker-compose.yml"), "w") as f:
        f.write(docker_compose_content)

def start_motioneye():
    """Start MotionEye service using Docker Compose."""
    print("Starting MotionEye service...")
    run_command("cd ~/motioneye && sudo docker compose up -d")

if __name__ == "__main__":
    print("Starting Raspberry Pi Docker and MotionEye setup...")

    # Install required drivers and tools
    check_csi_camera_driver()
    install_required_packages()

    # Install Docker and re-install Docker Compose
    install_docker()
    reinstall_docker_compose()

    # Add user to Docker group and set up MotionEye directory and files
    add_user_to_docker_group()
    create_motioneye_directory()
    create_docker_compose_file()

    # Start MotionEye service
    start_motioneye()

    print("MotionEye setup complete! Please log out and log back in to apply Docker group changes.")
