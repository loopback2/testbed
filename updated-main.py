from utils.inventory_loader import load_device_config
from utils.discovery_and_cleanup import discover_and_cleanup
from utils.scp_transfer import scp_image_to_device
from utils.install_junos_cli import install_junos_cli
import argparse


def main():
    print("\n==============================")
    print("  Junos OS Upgrade Tool")
    print("==============================")

    # CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip storage cleanup")
    parser.add_argument("--skip-scp", action="store_true", help="Skip SCP file transfer")
    args = parser.parse_args()

    # Load device config
    device = load_device_config("config/device.yml")

    # --- Phase 1: Discovery & Storage Cleanup ---
    if args.skip_cleanup:
        print("\n--- Phase 1: Skipped via flag ---")
        hostname = device["name"]
        model = device.get("model", "UNKNOWN")
        version = device.get("version", "UNKNOWN")
    else:
        success, hostname, model, version = discover_and_cleanup(device)
        if not success:
            print("[✖] Phase 1 failed. Aborting.")
            return

    device["hostname"] = hostname
    device["model"] = model
    device["version"] = version

    # --- Phase 2: SCP Transfer ---
    if args.skip_scp:
        print("\n--- Phase 2: Skipped via flag ---")
        image_filename = input("[?] Enter filename manually (e.g. junos.tgz): ").strip()
    else:
        image_filename = scp_image_to_device(device, model)
        if not image_filename:
            print("[✖] Phase 2 failed. Aborting.")
            return

    # Confirm image selection before install
    print(f"\n[?] Confirm image selected: \033[1m{image_filename}\033[0m")
    choice = input("    Proceed with install? (y/n): ").strip().lower()
    if choice != "y":
        print("[✖] Install aborted by user.")
        return

    # --- Phase 3: Install Junos OS ---
    install_success = install_junos_cli(device, image_filename)

    if not install_success:
        print("[✖] Phase 3 failed. Upgrade unsuccessful.")
        return

    print("[✓] Phase 3 completed successfully.")


if __name__ == "__main__":
    main()