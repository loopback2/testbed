from netmiko import ConnectHandler
import subprocess
import time
from yaspin import yaspin


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
    Monitors the SSH (port 22) status using nmap with a real-time CLI spinner using yaspin.

    Args:
        ip (str): IP address of the device to monitor.
        check_interval (int): Seconds between each nmap check.
        timeout (int): Max seconds to wait for SSH to return.

    Returns:
        bool: True if SSH is detected as online, False if timeout reached.
    """
    print(f"\n[🔍] Waiting 10 seconds for device to begin shutdown...")
    time.sleep(10)

    print(f"\n[📡] Monitoring SSH status for {ip}...\n")

    start_time = time.time()
    last_check = 0
    ssh_state = "OFFLINE"

    with yaspin(text="Waiting for device to reboot...", color="cyan", spinner="dots12") as spinner:
        while time.time() - start_time < timeout:
            now = time.time()

            if now - last_check >= check_interval:
                try:
                    result = subprocess.run(
                        ["nmap", "-p", "22", "-Pn", ip],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if "22/tcp open" in result.stdout:
                        ssh_state = "ONLINE"
                    elif "22/tcp filtered" in result.stdout or "22/tcp closed" in result.stdout:
                        ssh_state = "OFFLINE"
                    else:
                        ssh_state = "UNKNOWN"

                    if ssh_state == "ONLINE":
                        spinner.ok("✅")
                        print(f"[✓] SSH is now reachable on {ip}.")
                        return True

                    last_check = now

                except subprocess.TimeoutExpired:
                    spinner.text = "nmap timeout... retrying..."
                except Exception as e:
                    spinner.text = f"Error: {str(e)}"

            # Update spinner text on each cycle
            spinner.text = f"Waiting for SSH... ({ssh_state}) on {ip}"
            time.sleep(0.2)

        spinner.fail("✖")
        print(f"[!] Timeout reached. Device did not come back online within {timeout} seconds.")
        return False