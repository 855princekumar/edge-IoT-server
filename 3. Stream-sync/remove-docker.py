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

def remove_docker():
    print("Removing Docker...")

    # Stop the Docker service
    run_command("systemctl stop docker")

    # Remove Docker
    run_command("apt-get purge -y docker-ce")

    # Remove any leftover dependencies
    run_command("apt-get autoremove -y")

    print("Docker has been removed.")

def remove_docker_compose():
    print("Removing Docker Compose...")

    # Remove Docker Compose binary
    run_command("rm -f /usr/local/bin/docker-compose")

    print("Docker Compose has been removed.")

def remove_docker_group():
    print("Removing Docker group...")

    username = getpass.getuser()
    run_command(f"gpasswd -d {username} docker || true")  # Remove user from docker group
    run_command("groupdel docker || true")  # Delete the docker group if it exists

    print("Docker group has been removed.")

if __name__ == "__main__":
    remove_docker()
    remove_docker_compose()
    remove_docker_group()
    print("Docker and Docker Compose removal completed.")
