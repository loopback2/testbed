from datetime import datetime
import os
from netmiko import ConnectHandler
import time

def log_output(device_name, phase, content):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")

def get_success_strings(model):
    model = model.upper()
    if "QFX5120" in model and "YM" in model:
        return [
            "Install completed",
            "Host OS upgrade staged",
            "Reboot the system to complete installation",
        ]
    elif "QFX5120" in model:
        return ["Install completed", "activated at next reboot"]
    elif "EX4300" in model or "EX4400" in model:
        return ["Install completed", "activated at next reboot"]
    return ["Install completed"]

def install_junos_cli(device, image_filename):
    print("\n--- Phase 3: Junos OS Install ---")
    try:
        ip = device["ip"]
        username = device["username"]
        password = device["password"]
        model = device["model"]
        image_path = f"/var/tmp/{image_filename}"
        command = f"request system software add {image_path} no-copy"

        print(f"[→] Connecting via Netmiko to {ip}...")
        connection = ConnectHandler(
            device_type="juniper",
            host=ip,
            username=username,
            password=password,
        )

        print(f"[📦] Sending install command: {command}\n")
        output = connection.send_command(
            command,
            expect_string=r"#|%|>",
            delay_factor=8,  # ← Makes Netmiko wait longer between reads
            max_loops=1000,  # ← Max number of output read cycles
        )

        connection.disconnect()

        log_output(device["name"], "phase3-install", output)

        success_strings = get_success_strings(model)
        for keyword in success_strings:
            if keyword.lower() in output.lower():
                print(f"\n[✅] Junos OS install appears successful. Awaiting reboot.")
                return True

        print(f"\n[✖] Junos OS install output did not match known success markers. Review log.")
        return False

    except Exception as e:
        print(f"[✖] Installation failed: {e}")
        return False
