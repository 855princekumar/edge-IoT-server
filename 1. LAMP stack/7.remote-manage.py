import os
import subprocess

def install_cockpit_debian():
    """Install Cockpit on Debian/Ubuntu-based systems."""
    print("Detected Debian-based system. Installing Cockpit...")
    subprocess.run(['sudo', 'apt', 'update'], check=True)
    subprocess.run(['sudo', 'apt', 'install', '-y', 'cockpit'], check=True)
    subprocess.run(['sudo', 'systemctl', 'enable', '--now', 'cockpit.socket'], check=True)
    print("Cockpit installed and started.")

def install_cockpit_rhel():
    """Install Cockpit on RHEL/CentOS/Fedora-based systems."""
    print("Detected RedHat-based system. Installing Cockpit...")
    subprocess.run(['sudo', 'dnf', 'install', '-y', 'cockpit'], check=True)
    subprocess.run(['sudo', 'systemctl', 'enable', '--now', 'cockpit.socket'], check=True)
    print("Cockpit installed and started.")

def detect_distro():
    """Detect the distribution by reading the /etc/os-release file."""
    with open("/etc/os-release") as f:
        os_info = f.read()
    
    if "raspbian" in os_info.lower() or "debian" in os_info.lower():
        return "debian"
    elif "centos" in os_info.lower() or "fedora" in os_info.lower() or "rhel" in os_info.lower():
        return "rhel"
    else:
        return "unknown"

def install_cockpit():
    """Detect system type and install Cockpit."""
    distro = detect_distro()
    
    if distro == "debian":
        install_cockpit_debian()
    elif distro == "rhel":
        install_cockpit_rhel()
    else:
        print(f"Unsupported Linux distribution. Only Debian-based and RedHat-based systems are supported.")

if __name__ == "__main__":
    install_cockpit()
