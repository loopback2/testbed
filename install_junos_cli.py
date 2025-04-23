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


def install_junos_cli(device, image_filename):
    """
    Installs the Junos image using Netmiko. 
    Returns True if "will be activated at next reboot" is found in output.
    """
    print("\n--- Phase 3: Junos OS Install ---")

    try:
        # Connect to device
        connection = ConnectHandler(
            device_type="juniper",
            host=device["ip"],
            username=device["username"],
            password=device["password"]
        )

        # Build and send install command
        image_path = f"/var/tmp/{image_filename}"
        command = f"request system software add {image_path} no-copy no-validate"
        print(f"[→] Executing: {command}\n")

        connection.write_channel(command + "\n")
        time.sleep(1)

        output_log = ""
        timeout = 600  # Max wait time: 10 minutes
        start_time = time.time()

        # Read and print output in real time
        while True:
            if time.time() - start_time > timeout:
                print("[✖] Timeout waiting for upgrade process.")
                break

            output = connection.read_channel()
            if output:
                print(output, end="")
                output_log += output

                if "will be activated at next reboot" in output:
                    break

            time.sleep(0.5)

        output_log += connection.read_channel()
        connection.disconnect()

        # Save session output
        log_output(device["name"], "phase3-install", output_log)

        if "will be activated at next reboot" in output_log:
            print("[✅] Junos image successfully installed and pending reboot.")
            return True
        else:
            print("[✖] Install completed but success confirmation not detected.")
            return False

    except Exception as e:
        print(f"[✖] Installation failed: {e}")
        return False
