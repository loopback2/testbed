from netmiko import ConnectHandler
import subprocess
import time
import sys


def trigger_reboot(device_info):
    """
    Triggers a reboot on the Junos device using 'request system reboot at now',
    and automatically confirms the yes/no prompt.

    Args:
        device_info (dict): Dictionary containing device connection details.

    Returns:
        bool: True if the reboot command was successfully sent, False otherwise.
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

        if "Reboot the system" in output:
            output += connection.send_command_timing("yes")

        print(f"\n[📟] Reboot Output:\n{output.strip()}\n")
        print("[✓] Reboot command sent successfully. Closing session.")
        connection.disconnect()
        return True

    except Exception as e:
        print(f"[!] Failed to send reboot command: {e}")
        return False


def monitor_ssh_status(ip, check_interval=5, timeout=1200):
    """
    Monitors the SSH (port 22) status using nmap and displays a spinner while waiting.

    Args:
        ip (str): IP address of the device to monitor.
        check_interval (int): Seconds between each nmap check. Default is 5 seconds.
        timeout (int): Maximum number of seconds to wait for the device to come back online.

    Returns:
        bool: True if SSH service is detected as online within timeout, False otherwise.
    """
    print(f"\n[🔍] Waiting 10 seconds for device to begin shutdown...")
    time.sleep(10)

    print(f"\n[📡] Monitoring SSH status for {ip}...\n")

    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spin_index = 0
    start_time = time.time()
    current_state = None

    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(
                ["nmap", "-p", "22", "-Pn", ip],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "22/tcp open" in result.stdout:
                new_state = "ONLINE"
            elif "22/tcp filtered" in result.stdout or "22/tcp closed" in result.stdout:
                new_state = "OFFLINE"
            else:
                new_state = "UNKNOWN"

            # Animate spinner and update one-line status
            spinner_char = spinner[spin_index % len(spinner)]
            spin_index += 1

            sys.stdout.write(
                f"\r{spinner_char} SSH status: {new_state} on {ip}... "
            )
            sys.stdout.flush()

            if new_state == "ONLINE":
                print(f"\n[✓] SSH is now reachable on {ip}.")
                return True

            time.sleep(check_interval)

        except subprocess.TimeoutExpired:
            sys.stdout.write("\r[!] Nmap scan timed out. Retrying...             ")
            sys.stdout.flush()
            time.sleep(check_interval)
        except Exception as e:
            sys.stdout.write(f"\r[!] SSH check error: {e}                        ")
            sys.stdout.flush()
            time.sleep(check_interval)

    print(f"\n[!] Timeout reached. Device did not come back online within {timeout} seconds.")
    return False