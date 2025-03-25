# utils/reboot_monitor.py

from netmiko import ConnectHandler
import time
import subprocess


def trigger_reboot(device_info):
    """
    Triggers a reboot using 'request system reboot at now'.

    Args:
        device_info (dict): Connection info for the Junos device.
    """
    try:
        print(f"\n[↻] Sending reboot command to {device_info['name']}...")

        connection = ConnectHandler(
            device_type="juniper",
            host=device_info["ip"],
            username=device_info["username"],
            password=device_info["password"]
        )

        reboot_cmd = "request system reboot at now"
        output = connection.send_command_timing(reboot_cmd)
        print(f"\n[📟] Reboot Output:\n{output.strip()}\n")

        print("[✓] Reboot command sent successfully. Closing session.")
        connection.disconnect()

        return True

    except Exception as e:
        print(f"[!] Failed to send reboot command: {e}")
        return False


def monitor_ssh_status(ip, check_interval=10, timeout=600):
    """
    Monitors SSH (port 22) status using nmap.
    Waits until port 22 is detected as 'open'.

    Args:
        ip (str): IP address of the device to check
        check_interval (int): Time in seconds between checks
        timeout (int): Max time to wait (in seconds)

    Returns:
        bool: True if SSH came back up, False if timeout hit
    """
    print(f"\n[🔍] Waiting 10 seconds for device to begin shutdown...")
    time.sleep(10)

    print(f"[📡] Monitoring SSH (port 22) status for {ip}...\n")
    previous_state = None
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(
                ["nmap", "-p", "22", "-Pn", ip],
                capture_output=True,
                text=True,
                timeout=15
            )

            if "22/tcp open" in result.stdout:
                current_state = "open"
            elif "22/tcp filtered" in result.stdout or "22/tcp closed" in result.stdout:
                current_state = "down"
            else:
                current_state = "unknown"

            # Only print when state changes
            if current_state != previous_state:
                timestamp = time.strftime('%H:%M:%S')
                if current_state == "open":
                    print(f"[{timestamp}] [✓] SSH is now reachable on {ip}.")
                    return True
                elif current_state == "down":
                    print(f"[{timestamp}] [!] SSH is down. Waiting for reboot...")
                else:
                    print(f"[{timestamp}] [!] Unknown SSH state.")

            previous_state = current_state
            time.sleep(check_interval)

        except subprocess.TimeoutExpired:
            print(f"[!] Nmap timed out while scanning {ip}. Retrying...")
        except Exception as e:
            print(f"[!] Error during SSH monitoring: {e}")

    print(f"[!] Timeout reached. Device did not come back online within {timeout} seconds.")
    return False


from utils.reboot_monitor import trigger_reboot, monitor_ssh_status

# --- Phase 4: Reboot & Monitoring ---
print("\n--- Phase 4: Reboot & SSH Monitoring ---")

# Send reboot command
if trigger_reboot(device):
    print("[...] Reboot initiated. Monitoring SSH availability...")
    reboot_success = monitor_ssh_status(device["ip"])
    
    if reboot_success:
        print("[✓] Device is back online. Proceeding to post-upgrade verification.")
    else:
        print("[!] Device did not return within expected time. Manual check required.")
else:
    print("[!] Reboot could not be triggered. Skipping monitoring phase.")