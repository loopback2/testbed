import argparse
from utils.inventory_loader import load_inventory
from utils.pyez_connector import connect_and_get_facts
from utils.storage_cleanup import run_storage_cleanup
from utils.scp_transfer import scp_file_to_juniper

# Parse CLI arguments
parser = argparse.ArgumentParser(description="Junos OS Upgrade Script")
parser.add_argument("--skip-cleanup", action="store_true", help="Skip storage cleanup step")
args = parser.parse_args()

# Load inventory
upgrade_version, upgrade_image, device = load_inventory()
remote_path = f"/var/tmp/{upgrade_image.split('/')[-1]}"

print("\n===============================================")
print("         Juniper Junos OS Upgrade Tool         ")
print("===============================================\n")

print(f"Target Device  : {device['name']} ({device['ip']})")
print(f"Junos Version  : {upgrade_version}")
print(f"Upgrade Image  : {upgrade_image}\n")

# --- Phase 1: Discovery & Cleanup ---
print("\n--- Phase 1: Discovery & Cleanup ---")
facts = connect_and_get_facts(device)

if facts:
    print(f"[✓] Connected to {facts['hostname']} | Model: {facts['model']} | Current Version: {facts['version']}")

    # Run storage cleanup unless skipped via --skip-cleanup
    if not args.skip_cleanup:
        print("[+] Performing system storage cleanup...")
        cleanup_output = run_storage_cleanup(device)
        if cleanup_output:
            print(f"[✓] Storage cleanup successful.")
        else:
            print("[!] Storage cleanup failed. Check logs.")
    else:
        print("[!] Skipping storage cleanup as per user request.")
else:
    print("[!] Could not retrieve device facts. Aborting upgrade.")
    exit(1)

# --- Phase 2: SCP File Transfer ---
print("\n--- Phase 2: SCP File Transfer ---")

scp_success = scp_file_to_juniper(device, upgrade_image, remote_path)

if scp_success:
    print(f"[✓] File successfully transferred to {remote_path}.")
else:
    print("[!] SCP transfer failed. Check logs.")
    exit(1)

print("\n[✓] SCP Phase Completed Successfully. Ready for Upgrade.")