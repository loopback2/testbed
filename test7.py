from utils.post_upgrade_verification import verify_post_upgrade

# --- Phase 4: Reboot & Monitoring ---
print("\n--- Phase 4: Reboot & SSH Monitoring ---")

# Send reboot command
if trigger_reboot(device):
    print("[...] Reboot initiated. Monitoring SSH availability...")
    reboot_success = monitor_ssh_status(device["ip"])

    if reboot_success:
        print("[✓] Device is back online. Proceeding to post-upgrade verification.")

        # --- Phase 5: Post-Upgrade Verification ---
        print("\n--- Phase 5: Post-Upgrade Verification ---")
        verify_post_upgrade(device, target_version)

    else:
        print("[!] Device did not return within expected time. Manual check required.")

else:
    print("[!] Reboot could not be triggered. Skipping monitoring phase.")