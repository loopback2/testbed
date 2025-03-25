import subprocess
import time
import sys


def monitor_ssh_status(ip, check_interval=5, timeout=1200):
    print(f"\n[🔍] Waiting 10 seconds for device to begin shutdown...")
    time.sleep(10)

    print(f"\n[📡] Monitoring SSH status for {ip}...\n")

    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spin_index = 0
    start_time = time.time()
    current_state = None

    while time.time() - start_time < timeout:
        try:
            # Run nmap scan for port 22
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

            # Animate spinner + show current state (on same line)
            spinner_char = spinner[spin_index % len(spinner)]
            spin_index += 1

            sys.stdout.write(
                f"\r{spinner_char} SSH status: {new_state} on {ip}... "
            )
            sys.stdout.flush()

            # If SSH is up, break loop and return success
            if new_state == "ONLINE":
                print(f"\n[✓] SSH is now reachable on {ip}.")
                return True

            # Wait a bit before next check
            time.sleep(check_interval)

        except subprocess.TimeoutExpired:
            sys.stdout.write("\r[!] Nmap timed out. Retrying...           ")
            sys.stdout.flush()
            time.sleep(check_interval)
        except Exception as e:
            sys.stdout.write(f"\r[!] SSH check error: {e}                ")
            sys.stdout.flush()
            time.sleep(check_interval)

    print(f"\n[!] Timeout reached. Device did not come back online within {timeout} seconds.")
    return False