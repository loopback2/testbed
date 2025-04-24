# install_junos_cli.py

from netmiko import ConnectHandler
import os
import time
from datetime import datetime
from colorama import Fore, Style

# Success markers that can be seen across various models
SUCCESS_MARKERS = [
    "Install completed",
    "Validation succeeded",
    "commit complete",
    "will be activated at next reboot",
    "Upgrade package verification succeeded"
]

def install_junos_cli(device, image_filename):
    """
    Installs Junos OS on a Juniper device using CLI via Netmiko.
    Saves full session log and returns success/failure.
    """
    # Prepare command and session log file
    install_command = f"request system software add /var/tmp/{image_filename}"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    hostname = device.get("hostname", "unknown")
    log_file = f"logs/{hostname}-phase3-install-{timestamp}.log"

    print(f"\n--- Phase 3: Junos OS Install ---")
    print(f"{Fore.CYAN}[→] Connecting via Netmiko to {device['ip']}...{Style.RESET_ALL}")

    try:
        conn = ConnectHandler(
            device_type="juniper",
            host=device["ip"],
            username=device["username"],
            password=device["password"],
            fast_cli=False,
        )

        print(f"{Fore.CYAN}[⚙️] Sending install command: {install_command}{Style.RESET_ALL}")
        output = conn.send_command(
            install_command,
            expect_string=r"[>#]",
            read_timeout=600,
            delay_factor=5
        )

        # Save raw output
        with open(log_file, "w") as f:
            f.write(output)

        # Check for known success markers
        found_marker = False
        for marker in SUCCESS_MARKERS:
            if marker.lower() in output.lower():
                print(f"{Fore.GREEN}[✓] Found success string: '{marker}'{Style.RESET_ALL}")
                found_marker = True
                break

        if found_marker:
            print(f"{Fore.CYAN}[🗂] Log saved to: {log_file}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}[!] Junos OS install output did not match known success markers. Review log.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[🗂] Log saved to: {log_file}{Style.RESET_ALL}")
            return False

    except Exception as e:
        print(f"{Fore.RED}[✖] Installation failed: {e}{Style.RESET_ALL}")
        return False
