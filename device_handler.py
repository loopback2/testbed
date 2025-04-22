import yaml
from jnpr.junos import Device
from getpass import getpass

def load_device_from_yaml(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    # Return only one device for now
    return data["devices"][0]

def connect_to_device(device_info):
    try:
        password = getpass(f"Enter password for {device_info['host']}: ")
        dev = Device(
            host=device_info["host"],
            user=device_info["username"],
            passwd=password,
            port=830
        )
        dev.open()
        print(f"[+] Connected to {device_info['host']}")
        return dev
    except Exception as e:
        print(f"[!] Error connecting to {device_info['host']}: {e}")
        return None
