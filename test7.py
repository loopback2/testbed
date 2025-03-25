from netmiko import ConnectHandler
import subprocess
import time
from yaspin import yaspin
from utils.logger import log_to_file, create_phase_log_file


def trigger_reboot(device_info):
    """
    Sends the reboot command and confirms the prompt. Logs output.

    Returns:
        bool: True if reboot command was sent, False otherwise.
    """
    print(f"\n[↻] Sending reboot command to {device_info['name']}...")

    try:
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

        log_path = create_phase_log_file(device_info["name"], "reboot")
        log_to_file(log_path, output)

        print("[✓] Reboot command sent successfully.")
        print(f"[💾] Reboot output logged to: {log_path}")
        connection.disconnect()
        return True

    except Exception as e:
        print(f"[✖] Failed to send reboot command: {e}")
        return False


def monitor_ssh_status(ip, check_interval=5, timeout=1200):
    """
    Monitors SSH reachability using nmap. Uses a clean spinner and returns status.

    Returns:
        bool: True if SSH is reachable, False if timeout.
    """
    print(f"\n[🔄] Waiting 10 seconds for device to begin shutdown...")
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

            spinner.text = f"Waiting for SSH... ({ssh_state}) on {ip}"
            time.sleep(0.2)

        spinner.fail("✖")
        print(f"[✖] Timeout reached. Device did not come back online in {timeout} seconds.")
        return False