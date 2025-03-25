from jnpr.junos import Device
from utils.logger import log_to_file, create_phase_log_file


def verify_post_upgrade(device_info, target_version):
    """
    Verifies the Junos version using PyEZ after reboot.

    Returns:
        bool: True if version matches target, False otherwise.
    """
    print("\n--- Phase 5: Post-Upgrade Verification ---")
    print("[🛠️] Verifying Junos version after reboot...\n")

    try:
        with Device(
            host=device_info["ip"],
            user=device_info["username"],
            passwd=device_info["password"],
            gather_facts=True,
            timeout=60
        ) as dev:

            hostname = dev.facts.get("hostname", "unknown")
            current_version = dev.facts.get("version", "unknown")

            log_output = (
                f"Hostname       : {hostname}\n"
                f"Current Version: {current_version}\n"
                f"Target Version : {target_version}"
            )

            print(f"[📟] Hostname        : {hostname}")
            print(f"[📦] Current Version : {current_version}")
            print(f"[🎯] Target Version  : {target_version}")

            log_path = create_phase_log_file(device_info["name"], "post-verify")
            log_to_file(log_path, log_output)
            print(f"[💾] Verification output saved to: {log_path}")

            if current_version == target_version:
                print(f"[✅] Device successfully upgraded to {current_version}.\n")
                return True
            else:
                print("[✖] Version mismatch! Upgrade may have failed.")
                return False

    except Exception as e:
        print(f"[✖] Post-upgrade verification failed: {e}")
        return False