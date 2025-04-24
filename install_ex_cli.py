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


def get_ex_success_strings():
    return [
        "Validation succeeded",
        "commit complete",
        "will be activated at next reboot"
    ]


def install_ex_cli(device, image_filename):
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

        print(f"[📦] Sending install command: {command}\n")
        connection.write_channel(command + "\n")
        time.sleep(2)

        output = ""
        timeout = 800  # Up to ~13 mins
        start_time = time.time()
        success_strings = get_ex_success_strings()

        while True:
            out = connection.read_channel()
            if out:
                print(out, end="")  # Live CLI stream
                output += out

                for s in success_strings:
                    if s.lower() in out.lower():
                        print(f"\n[✅] Found EX install success marker: '{s}'")
                        connection.disconnect()
                        log_output(name, "phase3-install", output)
                        return True

            if time.time() - start_time > timeout:
                print(f"\n[!] Timeout reached on EX install. Could not confirm success.")
                break

            time.sleep(1)

        connection.disconnect()
        log_output(name, "phase3-install", output)
        print("[✖] EX installation may have failed. Review log.")
        return False

    except Exception as e:
        print(f"[✖] EX installation failed: {e}")
        return False
