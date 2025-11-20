#!/usr/bin/env python3
import subprocess
import time

SSID = "wifi-Name"
PASSWORD = "password"
STATIC_IP = "IP/23"
GATEWAY = "Gateway"
DNS = "8.8.8.8,1.1.1.1"


def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except:
        return ""


def remove_old_wifi():
    print("🧹 Removing old WiFi profiles...")

    connections = run("nmcli -t -f NAME,TYPE connection show").split("\n")
    for c in connections:
        if ":wifi" in c:
            name = c.split(":")[0]
            print(f"   🔥 Removing: {name}")
            run(f"nmcli connection delete '{name}'")


def add_new_wifi():
    print("📡 Adding NEW WiFi connection...")
    run(f"nmcli device wifi connect \"{SSID}\" password \"{PASSWORD}\" ifname wlan0")
    time.sleep(1)

    # Rename it so we know it
    run("nmcli connection modify 'IOT LAB' connection.id IOT-LAB")
    print("✅ WiFi added as: IOT-LAB")


def apply_static_ip():
    print("⚙️ Setting STATIC IP using NetworkManager...")

    run(f"nmcli connection modify IOT-LAB ipv4.addresses {STATIC_IP}")
    run(f"nmcli connection modify IOT-LAB ipv4.gateway {GATEWAY}")
    run(f"nmcli connection modify IOT-LAB ipv4.dns \"{DNS}\"")
    run("nmcli connection modify IOT-LAB ipv4.method manual")

    print("✅ Static IP applied.")


def disable_auto_DHCP_profiles():
    print("🛑 Disabling NetworkManager auto-generated DHCP WiFi...")
    run("nmcli connection modify IOT-LAB connection.autoconnect yes")
    run("nmcli connection reload")


def reboot_system():
    print("🔁 Rebooting in 5 seconds...")
    time.sleep(5)
    subprocess.run(["sudo", "reboot"])


def main():
    print("🚀 Raspberry Pi WiFi + Static IP Setup (Bookworm Compatible)")

    remove_old_wifi()
    add_new_wifi()
    apply_static_ip()
    disable_auto_DHCP_profiles()

    reboot_system()


if __name__ == "__main__":
    main()
