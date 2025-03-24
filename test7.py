from jnpr.junos import Device
from jnpr.junos.utils.sw import SW

def progress_callback(dev, report):
    """Displays real-time progress during the install process."""
    print(f"[{dev.hostname}] {report}")

def install_junos(device_info, remote_image_path, validate=True, auto_reboot=False):
    """
    Installs the Junos OS image on a Juniper device using PyEZ.

    Args:
        device_info (dict): IP, username, password, etc.
        remote_image_path (str): Full path to the image on the Juniper device (e.g. /var/tmp/...)
        validate (bool): Run pre-install validation. Default is True.
        auto_reboot (bool): Reboot the switch after successful install.

    Returns:
        bool: True if install succeeded, False otherwise.
    """
    try:
        print(f"[+] Connecting to {device_info['name']} for Junos upgrade...")

        with Device(
            host=device_info["ip"],
            user=device_info["username"],
            passwd=device_info["password"],
            normalize=True
        ) as dev:
            sw = SW(dev)

            print(f"[+] Starting Junos installation using image: {remote_image_path}")
            status, message = sw.install(
                package=remote_image_path,
                validate=validate,
                progress=progress_callback
            )

            if status:
                print(f"[✓] Junos install completed successfully.")
                print(f"[📄] Install message: {message}")

                if auto_reboot:
                    print(f"[↻] Auto-reboot enabled. Rebooting device...")
                    sw.reboot()
                    print(f"[✓] Reboot initiated.")

                return True
            else:
                print(f"[!] Install failed. Device reported: {message}")
                return False

    except Exception as e:
        print(f"[!] Exception during upgrade: {e}")
        return False