# utils/junos_upgrade.py

from netmiko import ConnectHandler
import datetime
import os

def install_junos_cli(device_info, remote_image_path, log_dir="logs"):
    """
    Uses Netmiko to install Junos OS image with full CLI visibility and optional logging.

    Args:
        device_info (dict): Device connection info.
        remote_image_path (str): Full path to image on Juniper device.
        log_dir (str): Directory to store logs (default: 'logs/').

    Returns:
        bool: True if command executed successfully, False otherwise.
    """
    try:
        print(f"[+] Connecting to {device_info['name']} for CLI-based Junos upgrade...")

        connection = ConnectHandler(
            device_type="juniper",
            host=device_info["ip"],
            username=device_info["username"],
            password=device_info["password"]
        )

        # Prepare install command
        install_cmd = f"request system software add {remote_image_path} no-copy no-validate"
        print(f"\n[+] Sending install command:\n    {install_cmd}")

        # Run install and capture full output
        output = connection.send_command_timing(install_cmd, strip_prompt=False, strip_command=False)

        # Optional: wait a moment and collect continued output (if needed)
        more_output = connection.send_command_timing("", strip_prompt=False)
        full_output = output + "\n" + more_output

        # Print output to screen
        print("\n[📟] Junos CLI Output:\n" + "-"*60)
        print(full_output.strip())
        print("-"*60 + "\n")

        # Optional: Save output to a log file
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        hostname = device_info["name"].replace(" ", "_")
        os.makedirs(log_dir, exist_ok=True)
        logfile = os.path.join(log_dir, f"{hostname}-install-{timestamp}.log")

        with open(logfile, "w") as f:
            f.write(f"Install command:\n{install_cmd}\n\n")
            f.write(full_output)

        print(f"[✓] Install output saved to: {logfile}")

        # Basic success signal (could improve this logic later)
        if "Reboot the system" in full_output or "installing package" in full_output.lower():
            print("[✓] Install completed. Manual reboot required.")
            return True
        else:
            print("[!] Install output didn't contain expected success message. Review log.")
            return False

    except Exception as e:
        print(f"[!] CLI upgrade failed: {e}")
        return False
    
from utils.junos_upgrade import install_junos_cli

# --- Phase 3: Junos OS Upgrade (CLI-Based) ---
print("\n--- Phase 3: Junos OS Upgrade ---")

upgrade_success = install_junos_cli(device, remote_path)

if upgrade_success:
    print(f"[✓] Junos OS upgrade process completed. Please review output above and manually reboot when ready.")
else:
    print("[!] Junos upgrade failed or uncertain. Check the CLI output above and logs for more info.")