from netmiko import ConnectHandler
import time
from utils.logger import log_to_file, create_phase_log_file


def install_junos_cli(device_info, remote_image_path):
    """
    Executes the Junos software install command via Netmiko, streams real-time output.

    Returns:
        bool: True if install completed with success pattern, False otherwise.
    """
    print("\n--- Phase 3: Junos OS Upgrade (CLI-Based) ---")
    print(f"[🛠️] Connecting to {device_info['name']} for CLI-based Junos upgrade...\n")

    try:
        connection = ConnectHandler(
            device_type="juniper",
            host=device_info["ip"],
            username=device_info["username"],
            password=device_info["password"]
        )

        command = f"request system software add {remote_image_path} no-copy no-validate"
        print(f"[→] Sending install command:\n{command}\n")

        connection.write_channel(command + "\n")
        time.sleep(1)

        output_log = ""
        timeout = 300  # 5 minutes
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                print("[✖] Timeout reached while waiting for install output.")
                break

            out = connection.read_channel()
            if out:
                print(out, end="")  # Live display
                output_log += out

                if "will be activated at next reboot" in out or \
                   "set will be activated at next reboot" in out:
                    break

            time.sleep(0.5)

        # Final output read
        output_log += connection.read_channel()
        connection.disconnect()

        # Save to log
        log_path = create_phase_log_file(device_info["name"], "install")
        log_to_file(log_path, output_log)
        print(f"\n[💾] Full install session saved to: {log_path}")

        if "will be activated at next reboot" in output_log or \
           "set will be activated at next reboot" in output_log:
            print("[✅] Junos upgrade process completed successfully.")
            return True
        else:
            print("[✖] Install output captured, but success marker not found.")
            return False

    except Exception as e:
        print(f"[✖] Junos upgrade failed: {e}")
        return False