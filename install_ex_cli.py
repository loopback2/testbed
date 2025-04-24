from datetime import datetime
import os
import time
from netmiko import ConnectHandler


def log_output(device_name, phase, content):
    """
    Saves the provided output content to a timestamped log file.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")
    return log_path


def get_ex_success_strings():
    """
    Defines the list of success indicators specific to EX4300/EX4400 platforms.
    """
    return [
        "Validation succeeded",
        "activated at next reboot",
        "commit complete"
    ]


def install_ex_cli(device, image_filename):
    """
    Handles Junos installation via CLI for EX4300/EX4400 using Netmiko.
    Monitors real-time output to detect success markers.
    """
    print("\n--- Phase 3: Junos OS Install (EX Series) ---")
    try:
        ip = device["ip"]
        username = device["username"]
        password = device["password"]
        name = device["name"]
        image_path = f"/var/tmp/{image_filename}"
        command = f"request system software add {image_path} no-copy"

        print(f"[→] Connecting via Netmiko to {ip}...")
        connection = ConnectHandler(
            device_type="juniper",
            host=ip,
            username=username,
            password=password,
        )

        print(f"[📦] Sending install command: {command}")
        connection.write_channel(command + "\n")
        time.sleep(2)

        output = ""
        success_strings = get_ex_success_strings()
        timeout = 600
        start_time = time.time()

        print("[⏳] Waiting for install", end="", flush=True)

        while True:
            chunk = connection.read_channel()
            if chunk:
                print(chunk, end="")  # live feedback to user
                output += chunk

            # Always check full buffer for success
            if all(success.lower() in output.lower() for success in success_strings):
                print("\n[✅] Found all success markers.")
                log_output(name, "phase3-install", output)
                connection.disconnect()
                return True

            # Backup: check for final CLI prompt + partial success
            if "{master:0}" in output and "Validation succeeded" in output:
                print("\n[✅] Install appears complete (prompt returned).")
                log_output(name, "phase3-install", output)
                connection.disconnect()
                return True

            if time.time() - start_time > timeout:
                print("\n[!] Timeout reached. Installation result unclear.")
                break

            print(".", end="", flush=True)
            time.sleep(1)

        connection.disconnect()
        log_output(name, "phase3-install", output)
        print(f"\n[✖] Installation may have failed. Review log file.")
        return False

    except Exception as e:
        print(f"[✖] Installation failed: {e}")
        return False
