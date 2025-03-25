from utils.inventory_loader import load_inventory
from utils.storage_cleanup import perform_storage_cleanup
from utils.scp_transfer import scp_image_to_device
from utils.install_junos_cli import install_junos_cli
from utils.reboot_monitor import trigger_reboot, monitor_ssh_status
from utils.post_upgrade_verification import verify_post_upgrade
from utils.logger import get_timestamp
import argparse


def main():
    print("\n==============================")
    print("  Juniper Junos OS Upgrade Tool")
    print("==============================")

    # --- Load Inventory ---
    inventory_data = load_inventory("config/inventory.yml")
    device = inventory_data["device"]
    target_version = inventory_data["upgrade_version"]
    local_image_path = inventory_data["upgrade_image"]
    remote_image_path = f"/var/tmp/{local_image_path.split('/')[-1]}"

    print(f"\nTarget Device : {device['name']} ({device['ip']})")
    print(f"Junos Version : {target_version}")
    print(f"Upgrade Image : {local_image_path}")

    # --- Handle optional CLI args ---
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip storage cleanup")
    args = parser.parse_args()

    # --- Phase 1: Discovery & Cleanup ---
    print("\n--- Phase 1: Discovery & Cleanup ---")
    if args.skip_cleanup:
        print("[↷] Skipping storage cleanup as per user request.")
    else:
        cleanup_success = perform_storage_cleanup(device)
        if not cleanup_success:
            print("[✖] Storage cleanup failed. Aborting upgrade.")
            return

    # --- Phase 2: SCP File Transfer ---
    print("\n--- Phase 2: SCP File Transfer ---")
    scp_success = scp_image_to_device(device, local_image_path, remote_image_path)
    if not scp_success:
        print("[✖] SCP transfer failed. Aborting upgrade.")
        return
    print("[✓] SCP Phase Completed Successfully. Ready for Upgrade.")

    # --- Phase 3: Junos OS Upgrade ---
    upgrade_success = install_junos_cli(device, remote_image_path)
    if not upgrade_success:
        print("[✖] Junos upgrade failed or uncertain. Check output above and logs.")
        return

    # --- Phase 4: Reboot & Monitoring ---
    print("\n--- Phase 4: Reboot & SSH Monitoring ---")
    if trigger_reboot(device):
        print("[→] Reboot initiated. Monitoring SSH availability...")
        reboot_success = monitor_ssh_status(device["ip"])

        if reboot_success:
            print("[✓] Device is back online. Proceeding to post-upgrade verification.")

            # --- Phase 5: Post-Upgrade Verification ---
            verify_post_upgrade(device, target_version)
        else:
            print("[✖] Device did not return within expected time. Manual check required.")
    else:
        print("[✖] Reboot could not be triggered. Skipping monitoring phase.")


if __name__ == "__main__":
    main()