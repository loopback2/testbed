from netmiko import ConnectHandler
import time
import os
from datetime import datetime


def log_output(device_name, phase, content):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")


def discover_and_cleanup(device):
    print("\n--- Phase 1: Discovery & Cleanup ---")
    print(f"[🛠️] Connecting to {device['name']}...")

    try:
        conn = ConnectHandler(
            device_type="juniper",
            host=device["ip"],
            username=device["username"],
            password=device["password"]
        )

        # Discover model + hostname
        hostname = conn.send_command("show configuration system host-name")
        model = conn.send_command("show chassis hardware | match 'Model'")
        print(f"[📟] Hostname: {hostname.strip()}")
        print(f"[🧬] Model: {model.strip()}")

        # Storage cleanup
        print(f"[🧹] Running: request system storage cleanup no-confirm")
        output = conn.send_command_timing("request system storage cleanup no-confirm", strip_prompt=False)
        output += conn.send_command_timing("", strip_prompt=False)  # Flush buffer

        conn.disconnect()

        log_output(device["name"], "phase1-discovery-cleanup", output)

        print("[✓] Storage cleanup completed successfully.")
        return True, hostname.strip(), model.strip()

    except Exception as e:
        print(f"[✖] Error during cleanup: {e}")
        return False, None, None
