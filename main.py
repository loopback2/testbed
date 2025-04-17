from utils.inventory_loader import load_device_config
from utils.discovery_and_cleanup import discover_and_cleanup
from utils.scp_transfer import scp_image_to_device
import os


def main():
    print("\n==============================")
    print("  Junos OS Upgrade Tool")
    print("  Phase 1 & 2 Execution")
    print("==============================")

    # Load device details from YAML config
    device = load_device_config("config/device.yml")

    # --- Phase 1: Discovery & Storage Cleanup ---
    success, hostname, model, version = discover_and_cleanup(device)

    if not success:
        print("[✖] Phase 1 failed. Cannot continue.")
        return

    # Store facts for future use
    device["hostname"] = hostname
    device["model"] = model
    device["version"] = version

    # --- Phase 2: SCP File Transfer ---
    scp_success = scp_image_to_device(device, model)

    if not scp_success:
        print("[✖] Phase 2 failed. Aborting.")
        return

    print("[✓] Phase 2 completed successfully.")


if __name__ == "__main__":
    main()
