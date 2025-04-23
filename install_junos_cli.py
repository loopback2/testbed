from netmiko import ConnectHandler
import time
from datetime import datetime
import os


def log_output(device_name, phase, content):
    """
    Saves CLI output to a timestamped log file.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")


# Model to success string mapping
SUCCESS_STRINGS = {
    "QFX5120-YM": [
        "Host OS upgrade staged",
        "Reboot the system to complete installation",
        "Install completed"
    ],
    "QFX5120-Y": ["activated at next reboot"],
    "EX4300": ["activated at next reboot"],
    "EX4400": ["activated at next reboot"],
}


def get_success_strings(model):
    """
    Match partial model to expected success messages.
    """
    model = model.upper()
    if "QFX5120" in model and "YM" in model:
        return SUCCESS_STRINGS["QFX5120-YM"]
    elif "QFX5120" in model:
        return SUCCESS_STRINGS["QFX5120-Y"]
    elif "EX4300" in model:
        return SUCCESS_STRINGS["EX4300"]
    elif "EX4400" in model:
        return SUCCESS_STRINGS["EX4400"]
    return ["activated at next reboot"]


def install_junos_cli(device, image_filename):
    """
    Runs 'request system software add' with real-time output capture.
    Ends cleanly as soon as install completes and matches success string.
    """
    print("\n--- Phase 3: Junos OS Install ---")

    try:
        connection = ConnectHandler(
            device_type="juniper",
            host=device["ip"],
            username=device["username"],
            password=device["password"]
        )

        image_path = f"/var/tmp/{image_filename}"
        command = f"request system software add {image_path} no-copy"

        print(f"[→] Sending install command:\n{command}\n")
        connection.write_channel(command + "\n")
        time.sleep(1)

        output_log = ""
        timeout = 900  # 15 minutes max
        start_time = time.time()

        success_strings = get_success_strings(device["model"])
        found_success = False
        buffer = ""

        while True:
            if time.time() - start_time > timeout:
                print("[✖] Timeout waiting for install to complete.")
                break

            out = connection.read_channel()
            if out:
                print(out, end="")
                output_log += out
                buffer += out

                for keyword in success_strings:
                    if keyword.lower() in buffer.lower():
                        found_success = True
                        break

                if found_success:
                    time.sleep(3)  # wait briefly to collect final CLI output
                    output_log += connection.read_channel()
                    break

            time.sleep(1)

        connection.disconnect()
        log_output(device["name"], "phase3-install", output_log)

        if found_success:
            print("\n[✅] Junos OS upgrade appears successful and pending reboot.")
            return True
        else:
            print("\n[✖] Could not confirm success string. Manual review recommended.")
            return False

    except Exception as e:
        print(f"[✖] Installation failed: {e}")
        return False
