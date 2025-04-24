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
    return log_path


def get_ex_success_strings():
    return [
        "Install completed",
        "Validation succeeded",
        "commit complete",
        "pending' set will be activated at next reboot",
    ]


def install_ex_cli(device, image_filename):
    print("\n🔧 [EX Mode] Using install_ex_cli.py for EX4300/EX4400 devices.\n")
    print("--- Phase 3: Junos OS Install (EX Series) ---")
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

        output = "### INSTALL METHOD: install_ex_cli.py ###\n"
        timeout = 900  # 15 minutes max
        start_time = time.time()
        success_strings = get_ex_success_strings()

        while True:
            out = connection.read_channel()
            if out:
                print(out, end="")  # Real-time output
                output += out

                for s in success_strings:
                    if s.lower() in output.lower():
                        print(f"\n[✅] Found success string: '{s}'")
                        connection.disconnect()
                        log_output(name, "phase3-install", output)
                        return True

            if time.time() - start_time > timeout:
                print(f"\n[!] Timeout reached. Installation result unclear.")
                break

            time.sleep(1)

        connection.disconnect()
        log_output(name, "phase3-install", output)
        print(f"[✖] Installation may have failed. Review log file.")
        return False

    except Exception as e:
        print(f"[✖] Installation failed: {e}")
        return False
