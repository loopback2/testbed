from utils.inventory_loader import load_device_config
from utils.discovery_and_cleanup import discover_and_cleanup


def main():
    print("\n==============================")
    print("  Junos OS Upgrade Tool - Phase 1")
    print("==============================")

    device = load_device_config("config/device.yml")
    success, hostname, model = discover_and_cleanup(device)

    if not success:
        print("[!] Phase 1 failed. Cannot continue.")
        return

    # Save these variables for later phases
    device["hostname"] = hostname
    device["model"] = model


if __name__ == "__main__":
    main()
