import paramiko
import time
import os
from datetime import datetime


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


# Success strings by model
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
    Uses Paramiko to run Junos OS install command with real-time output.
    """
    print("\n--- Phase 3: Junos OS Install ---")
    try:
        ip = device["ip"]
        username = device["username"]
        password = device["password"]
        model = device["model"]
        image_path = f"/var/tmp/{image_filename}"
        command = f"request system software add {image_path} no-copy"

        print(f"[→] Connecting via SSH to {ip}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, look_for_keys=False)

        print(f"[→] Sending install command: {command}\n")

        shell = ssh.invoke_shell()
        shell.send(command + "\n")
        time.sleep(2)

        success_strings = get_success_strings(model)
        output_log = ""
        timeout = 900  # 15 mins
        start_time = time.time()
        found_success = False
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spin_index = 0

        while True:
            if time.time() - start_time > timeout:
                print("\n[✖] Timeout waiting for install to complete.")
                break

            if shell.recv_ready():
                output = shell.recv(65535).decode("utf-8", errors="ignore")
                print(output, end="")
                output_log += output

                for keyword in success_strings:
                    if keyword.lower() in output.lower():
                        found_success = True

            if found_success:
                break

            print(f"\r[⏳] Waiting... {spinner[spin_index % len(spinner)]}", end="", flush=True)
            spin_index += 1
            time.sleep(1)

        ssh.close()
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
