import yaml
from jnpr.junos import Device
from getpass import getpass

def load_device_from_yaml(path):
    """
    Load the first device from a YAML inventory file.
    Returns a dictionary with device connection info.
    """
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        device = data["devices"][0]  # We're only supporting one device for now
        return device
    except Exception as e:
        print(f"[!] Error loading YAML inventory: {e}")
        raise

def connect_to_device(device_info):
    """
    Attempt to connect to a Junos device using NETCONF over SSH (port 830).
    Returns an open Device object or None if connection fails.
    """
    try:
        print(f"🔑 Connecting to {device_info['host']} as {device_info['username']}...")
        password = getpass(f"Enter password for {device_info['host']}: ")

        dev = Device(
            host=device_info["host"],
            user=device_info["username"],
            passwd=password,
            port=830,
            gather_facts=False  # Keep it lightweight
        )
        dev.open()
        print(f"[+] Connected to {device_info['host']}")
        return dev

    except Exception as e:
        print(f"[!] Failed to connect to {device_info['host']}: {e}")
        return None
