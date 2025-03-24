# utils/junos_upgrade.py

from netmiko import ConnectHandler
from time import sleep

def install_junos_cli(device_info, remote_image_path):
    """
    Uses Netmiko to upgrade Junos OS via CLI with full output visibility.

    Args:
        device_info (dict): Device connection info.
        remote_image_path (str): Full path to the Junos image on the Juniper switch.

    Returns:
        bool: True if installation initiated successfully, False if error encountered.
    """
    try:
        print(f"[+] Connecting to {device_info['name']} for CLI-based Junos upgrade...")

        connection = ConnectHandler(
            device_type="juniper",
            host=device_info["ip"],
            username=device_info["username"],
            password=device_info["password"]
        )

        print(f"[+] Sending software install command via CLI...")
        install_cmd = f"request system software add {remote_image_path} no-copy no-validate"
        output = connection.send_command_timing(install_cmd)

        # Display CLI output line by line for full visibility
        print("\n[📟] Junos CLI Output:\n" + "-"*50)
        print(output.strip())
        print("-"*50 + "\n")

        # Look for key text to determine if successful
        if "Reboot the system" in output or "verify the configuration" in output or "installing package" in output.lower():
            print("[✓] Junos install completed. Manual reboot is now required.")
            return True
        elif "ERROR" in output or "couldn't" in output.lower():
            print("[!] Junos install failed. Error detected in output.")
            return False
        else:
            print("[!] Install output did not confirm success. Please verify manually.")
            return False

    except Exception as e:
        print(f"[!] CLI upgrade failed: {e}")
        return False
    

print("\n--- Phase 3: Junos OS Upgrade ---")

upgrade_success = install_junos_cli(device, remote_path)

if upgrade_success:
    print(f"[✓] Junos OS upgrade process completed. Please review output above and manually reboot when ready.")
else:
    print("[!] Junos upgrade failed or uncertain. Check the CLI output above and logs for more info.")