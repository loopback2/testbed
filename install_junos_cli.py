from datetime import datetime
import os
import time
from netmiko import ConnectHandler


def log_output(device_name, phase, content):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")
    return log_path


def get_success_strings(model):
    model = model.upper()
    if "QFX5120" in model and "YM" in model:
        return [
            "Install completed",
            "Host OS upgrade staged",
            "Reboot the system to complete installation",
        ]
    elif "QFX5120" in model:
        return [
            "Install completed",
            "activated at next reboot",
        ]
    return ["Install completed"]


def install_junos_cli(device, image_filename):
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
        timeout = 600
        start_time = time.time()
        success_strings = get_success_strings(model)

        while True:
            out = connection.read_channel()
            if out:
                print(out, end="")  # live real-time stream
                output += out

                for s in success_strings:
                    if s.lower() in out.lower():
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
        print("[✖] Installation may have failed. Review log file.")
        return False

    except Exception as e:
        print(f"[✖] Installation failed: {e}")
        return False
