import sys
from utils.discovery_and_cleanup import discover_and_cleanup
from utils.scp_transfer import transfer_image
from utils.install_junos_cli import install_junos_cli
from utils.device_inventory import get_device_inventory
from utils.display import print_header, print_phase

def confirm_image_installation(filename):
    print(f"\n[?] Confirm image selected: \033[1m{filename}\033[0m")
    choice = input("    Proceed with install? (y/n): ").strip().lower()
    return choice == 'y'

def main():
    print_header("Junos OS Upgrade Tool")

    # Load device info
    inventory_data = get_device_inventory()
    device = inventory_data[0]

    # Phase 1: Discovery & Cleanup
    print_phase("Phase 1: Discovery & Cleanup")
    cleanup_success, hostname, model, version = discover_and_cleanup(device)
    if not cleanup_success:
        print("[!] Phase 1 failed. Aborting.")
        sys.exit(1)

    # Phase 2: SCP File Transfer
    print_phase("Phase 2: SCP File Transfer")
    image_filename = transfer_image(device, model)
    if not image_filename:
        print("[!] Phase 2 failed. Aborting.")
        sys.exit(1)

    if not confirm_image_installation(image_filename):
        print("[!] Install aborted by user.")
        sys.exit(0)

    # Phase 3: Junos OS Install
    print_phase("Phase 3: Junos OS Install")
    install_success = install_junos_cli(device, image_filename)
    if not install_success:
        print("[!] Phase 3 failed. Upgrade unsuccessful.")
        sys.exit(1)

    print("[✓] Phase 3 completed successfully.")

if __name__ == "__main__":
    main()
