from netmiko import ConnectHandler
from jnpr.junos import Device
import time
import os
from datetime import datetime


def log_output(device_name, phase, content):
    """
    Saves CLI or RPC output to a timestamped log file in the logs directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")


def discover_and_cleanup(device):
    """
    Phase 1: Connects to the device, runs storage cleanup, and gathers hostname/model/version.

    Returns:
        success (bool)
        hostname (str)
        model (str)
        version (str)
    """
    print("\n--- Phase 1: Discovery & Cleanup ---")
    print(f"[🛠️] Connecting to {device['name']}...")

    try:
        # Step 1: Storage cleanup via Netmiko
        conn = ConnectHandler(
            device_type="juniper",
            host=device["ip"],
            username=device["username"],
            password=device["password"]
        )

        print(f"[🧹] Running: request system storage cleanup no-confirm")
        output = conn.send_command_timing("request system storage cleanup no-confirm", strip_prompt=False)
        output += conn.send_command_timing("", strip_prompt=False)
        conn.disconnect()

        log_output(device["name"], "phase1-discovery-cleanup", output)
        print("[✓] Storage cleanup completed.")

        # Step 2: Collect structured device facts via PyEZ
        with Device(
            host=device["ip"],
            user=device["username"],
            passwd=device["password"]
        ) as dev:
            dev.open()

            hostname = dev.facts.get("hostname", "unknown")
            model = dev.facts.get("model", "unknown")
            version = dev.facts.get("version", "unknown")

            print(f"[📟] Hostname      : {hostname}")
            print(f"[🧬] Model         : {model}")
            print(f"[📦] Junos Version : {version}")

            return True, hostname, model, version

    except Exception as e:
        print(f"[✖] Error during discovery or cleanup: {e}")
        return False, None, None, None
