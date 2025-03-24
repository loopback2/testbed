# utils/junos_upgrade.py

from netmiko import ConnectHandler
import time
import datetime
import os

def install_junos_cli(device_info, remote_image_path, log_dir="logs"):
    """
    Executes 'request system software add' via CLI and captures full output.

    Args:
        device_info (dict): Connection info
        remote_image_path (str): e.g. /var/tmp/junos-install.tgz
        log_dir (str): Folder for logs (default: logs/)

    Returns:
        bool: True if install completed successfully
    """
    try:
        print(f"[+] Connecting to {device_info['name']} for CLI-based Junos upgrade...")

        connection = ConnectHandler(
            device_type="juniper",
            host=device_info["ip"],
            username=device_info["username"],
            password=device_info["password"]
        )

        command = f"request system software add {remote_image_path} no-copy no-validate"
        print(f"\n[+] Sending install command:\n    {command}\n")

        # Send the command and get into interactive mode
        connection.write_channel(command + "\n")
        time.sleep(1)

        full_output = ""
        timeout = 120  # max time to collect output
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                print("[!] Timeout reached while waiting for install output.")
                break

            # Read any available output
            out = connection.read_channel()
            if out:
                print(out, end="")  # live display
                full_output += out

                # Look for known completion string
                if "pending will be activated" in out or "Reboot the system" in out:
                    break

            time.sleep(1)

        # Final prompt read
        full_output += connection.read_channel()

        # Save full output to log
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        hostname = device_info["name"].replace(" ", "_")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"{hostname}-install-{timestamp}.log")

        with open(log_path, "w") as f:
            f.write(f"Command: {command}\n\n")
            f.write(full_output)

        print(f"\n[✓] Full install session saved to: {log_path}")

        if "pending will be activated" in full_output:
            print("[✓] Junos install completed. Manual reboot required.")
            return True
        else:
            print("[!] Install output captured, but success marker not found. Please verify manually.")
            return False

    except Exception as e:
        print(f"[!] Exception during CLI install: {e}")
        return False