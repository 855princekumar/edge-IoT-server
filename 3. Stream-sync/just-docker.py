#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import shutil
import sys
import json
import platform
import time

STATE_DIR = "/var/lib/docker-bootstrap"
STATE_FILE = f"{STATE_DIR}/state.json"

def sh(cmd):
    print(f"\nâ–¶ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def require_root():
    if os.geteuid() != 0:
        print("âŒ Run as root: sudo -i")
        sys.exit(1)

def detect_pkg_manager():
    for mgr in ("apt", "dnf", "pacman"):
        if shutil.which(mgr):
            return mgr
    return None

def docker_installed():
    return shutil.which("docker") is not None

def install_docker(pkg_mgr):
    print("\nðŸ“¦ Installing Docker (with visible progress)")
    if pkg_mgr in ("apt", "dnf"):
        sh(
            "export DEBIAN_FRONTEND=noninteractive APT_PROGRESS_FD=1 && "
            "curl -fsSL https://get.docker.com | sed 's/-qq//g' | sh"
        )
    elif pkg_mgr == "pacman":
        sh("pacman -Sy --noconfirm docker docker-compose")
    else:
        print("âŒ Unsupported Linux distro")
        sys.exit(1)

def enable_docker():
    sh("systemctl enable docker")
    sh("systemctl start docker")

def setup_group():
    user = os.environ.get("SUDO_USER")
    if user:
        sh("groupadd docker || true")
        sh(f"usermod -aG docker {user}")

def save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    require_root()

    pkg_mgr = detect_pkg_manager()
    arch = platform.machine()

    if docker_installed():
        print("âš  Docker already installed â€” nothing to do")
        return

    print("ðŸ” System detected")
    print(f"   Package manager : {pkg_mgr}")
    print(f"   Architecture    : {arch}")

    install_docker(pkg_mgr)
    enable_docker()
    setup_group()

    save_state({
        "installed_by_script": True,
        "pkg_manager": pkg_mgr,
        "arch": arch
    })

    print("""
âœ… Docker installation completed successfully

â„¹ IMPORTANT:
â€¢ Logout & login ONCE to use Docker without sudo
â€¢ Rollback available via rollback script
""")

if __name__ == "__main__":
    main()
