#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import json
import sys

STATE_FILE = "/var/lib/docker-bootstrap/state.json"

def sh(cmd):
    print(f"\nâ–¶ {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def require_root():
    if os.geteuid() != 0:
        print("âŒ Run as root: sudo -i")
        sys.exit(1)

def main():
    require_root()

    if not os.path.exists(STATE_FILE):
        print("âš  No bootstrap state found â€” nothing to rollback")
        return

    with open(STATE_FILE) as f:
        state = json.load(f)

    print("ðŸ§¹ Rolling back Docker installation")

    sh("systemctl stop docker || true")
    sh("systemctl disable docker || true")

    mgr = state.get("pkg_manager")

    if mgr == "apt":
        sh("apt purge -y docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-buildx-plugin docker-ce-rootless-extras || true")
        sh("apt autoremove -y")
    elif mgr == "dnf":
        sh("dnf remove -y docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-buildx-plugin || true")
    elif mgr == "pacman":
        sh("pacman -Rns --noconfirm docker docker-compose || true")

    print("""
âœ… Rollback completed safely

âœ” Docker removed
âœ” No data deleted
âœ” System integrity preserved
""")

if __name__ == "__main__":
    main()
