from jnpr.junos import Device


def verify_post_upgrade(device_info, target_version):
    """
    Verifies the Junos version after reboot using PyEZ.

    Args:
        device_info (dict): Device info with IP, username, password, etc.
        target_version (str): The Junos version we expect after upgrade.

    Returns:
        bool: True if upgrade was successful, False otherwise.
    """
    print("\n[🛠️] Verifying Junos version after reboot...")

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

            print(f"[📟] Hostname: {hostname}")
            print(f"[📦] Current Version: {current_version}")
            print(f"[🎯] Target Version:  {target_version}")

            if current_version == target_version:
                print(f"[✅] Device successfully upgraded to {current_version}.")
                return True
            else:
                print(f"[❌] Version mismatch! Upgrade may have failed.")
                return False

    except Exception as e:
        print(f"[!] Post-upgrade verification failed: {e}")
        return False