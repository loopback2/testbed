from datetime import datetime
import os
from netmiko import ConnectHandler
import time


def log_output(device_name, phase, content):
    """
    Logs command output to a timestamped file in the logs directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")
    return log_path


def get_success_strings(model):
    """
    Returns a list of known success strings based on the device model.
    """
    model = model.upper()

    common_strings = [
        "Install completed",
        "Validation succeeded",
        "commit complete",
        "activated at next reboot",
        "Host OS upgrade staged",
        "Reboot the system to complete installation"
    ]

    if "QFX5120" in model and "YM" in model:
        return common_strings
    elif "QFX5120" in model:
        return common_strings
    elif "EX4400" in model:
        return common_strings
    elif "EX4300" in model:
        return common_strings

    return ["Install completed"]


def install_junos_cli(device, image_filename):
    """
    Connects to the Junos device via Netmiko and installs the Junos OS image.
    Detects success markers in output to determine upgrade completion.
    """
    print("\n--- Phase 3: Junos OS Install ---")
    try:
        ip = device["ip"]
        username = device["username"]
        password = device["password"]
        model = device["model"]
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

        print(f"[📦] Sending install command: {command}\n")
        connection.write_channel(command + "\n")
        time.sleep(2)

        output = ""
        timeout = 600  # 10 minutes
        start_time = time.time()
        success_strings = get_success_strings(model)

        while True:
            out = connection.read_channel()
            if out:
                print(out, end="")  # Live terminal output
                output += out

            # Check the full output for any known success strings
            for s in success_strings:
                if s.lower() in output.lower():
                    print(f"\n[✅] Found success string: '{s}'")
                    connection.disconnect()
                    log_output(name, "phase3-install", output)
                    return True

            if time.time() - start_time > timeout:
                print("\n[!] Timeout reached. Installation result unclear.")
                break

            time.sleep(1)

        connection.disconnect()
        log_output(name, "phase3-install", output)
        print(f"[✖] Installation may have failed. Review log file.")
        return False

    except Exception as e:
        print(f"[✖] Installation failed: {e}")
        return False
