from jnpr.junos import Device
from netmiko import ConnectHandler
from lxml import etree
from datetime import datetime
import os

def log_output(device_name, phase, content):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")
    return log_path

def discover_and_cleanup(device):
    print("\n--- Phase 1: Discovery & Cleanup ---")
    hostname = model = version = None

    try:
        # Run storage cleanup using Netmiko
        netmiko_device = {
            "device_type": "juniper",
            "host": device["ip"],
            "username": device["username"],
            "password": device["password"],
        }

        try:
            print(f"[↪] Connecting via Netmiko to run cleanup...")
            net_connect = ConnectHandler(**netmiko_device)
            cleanup_cmd = "request system storage cleanup no-confirm"
            print(f"[↪] Running: {cleanup_cmd}")
            output = net_connect.send_command(cleanup_cmd, expect_string=r"#")
            net_connect.disconnect()

            if "command not found" in output.lower() or "error" in output.lower():
                print("[✖] Storage cleanup failed. See log for details.")
            else:
                print("[✓] Storage cleanup completed.")
        except Exception as e:
            output = f"[✖] Netmiko connection or command failed: {e}"
            print(output)

        # Get device facts using PyEZ
        with Device(host=device["ip"], user=device["username"], passwd=device["password"]) as dev:
            hostname = dev.facts.get("hostname", "UNKNOWN")
            model = dev.facts.get("model", "UNKNOWN")
            version = dev.facts.get("version", "UNKNOWN")

        output += f"\nHostname: {hostname}\nModel: {model}\nVersion: {version}\n"
        log_output(hostname, "phase1-discovery-cleanup", output)

        return True, hostname, model, version

    except Exception as e:
        print(f"[✖] Discovery or cleanup failed: {e}")
        return False, hostname, model, version


def discover_only(device):
    print("\n--- Phase 1: Silent Discovery ---")
    hostname = model = version = None

    try:
        with Device(host=device["ip"], user=device["username"], passwd=device["password"]) as dev:
            hostname = dev.facts.get("hostname", "UNKNOWN")
            model = dev.facts.get("model", "UNKNOWN")
            version = dev.facts.get("version", "UNKNOWN")

            output = f"Hostname: {hostname}\nModel: {model}\nVersion: {version}\n"
            log_output(hostname, "phase1-discovery-only", output)

        return True, hostname, model, version

    except Exception as e:
        print(f"[✖] Discovery failed: {e}")
        return False, hostname, model, version