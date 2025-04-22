import yaml
from jnpr.junos import Device
from getpass import getpass

def load_device_from_yaml(path):
    """Load a single device from YAML inventory."""
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data["devices"][0]  # For now, just the first device

def connect_to_device(device_info):
    """Establish NETCONF connection to the device."""
    try:
        password = getpass(f"Enter password for {device_info['host']}: ")
        dev = Device(
            host=device_info["host"],
            user=device_info["username"],
            passwd=password,
            port=830,
            gather_facts=False
        )
        dev.open()
        print(f"[+] Connected to {device_info['host']}")
        return dev
    except Exception as e:
        print(f"[!] Error connecting to {device_info['host']}: {e}")
        return None
