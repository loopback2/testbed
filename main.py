from utils.inventory_loader import load_device_config
from utils.discovery_and_cleanup import discover_and_cleanup


def main():
    print("\n==============================")
    print("  Junos OS Upgrade Tool")
    print("  Phase 1: Discovery & Cleanup")
    print("==============================")

    # Load target device from YAML config
    device = load_device_config("config/device.yml")

    # Run Phase 1: Cleanup and gather facts
    success, hostname, model, version = discover_and_cleanup(device)

    if not success:
        print("[!] Phase 1 failed. Cannot continue.")
        return

    # Store gathered facts into device dictionary for future use
    device["hostname"] = hostname
    device["model"] = model
    device["version"] = version


if __name__ == "__main__":
    main()
