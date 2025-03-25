from netmiko import ConnectHandler
import time
import datetime
import os


def install_junos_cli(device_info, remote_image_path, log_dir="logs"):
    """
    Uses Netmiko to install Junos OS via CLI with full output visibility and logs.

    Args:
        device_info (dict): Connection information for the device
        remote_image_path (str): Path to the image on the Juniper device (/var/tmp/...)
        log_dir (str): Directory where CLI output logs will be stored

    Returns:
        bool: True if install completed successfully, False otherwise
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

        # Send the install command and begin watching output
        connection.write_channel(command + "\n")
        time.sleep(1)

        full_output = ""
        timeout = 180  # seconds to wait for output completion
        start_time = time.time()

        # Define known success markers
        success_phrases = [
            "pending will be activated",
            "pending set will be activated",
            "set will be activated",
            "activated at next reboot",
            "notice: 'pending'",
        ]

        while True:
            if time.time() - start_time > timeout:
                print("[!] Timeout reached while waiting for install output.")
                break

            # Read output from device
            out = connection.read_channel()
            if out:
                print(out, end="")  # live terminal-style output
                full_output += out

                # Check if we found a known success message
                if any(phrase in out.lower() for phrase in success_phrases):
                    print("\n[✓] Found success marker in output.")
                    break

            time.sleep(1)

        # Final buffer flush
        full_output += connection.read_channel()

        # Prepare log path
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        hostname = device_info["name"].replace(" ", "_")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"{hostname}-install-{timestamp}.log")

        with open(log_path, "w") as f:
            f.write(f"Command: {command}\n\n")
            f.write(full_output)

        print(f"\n[✓] Full install session saved to: {log_path}")

        # Confirm successful upgrade
        if any(phrase in full_output.lower() for phrase in success_phrases):
            print("[✓] Junos install completed successfully. Manual reboot required.")
            return True
        else:
            print("[!] Install output captured, but success marker not found. Please verify manually.")
            return False

    except Exception as e:
        print(f"[!] Exception during CLI install: {e}")
        return False