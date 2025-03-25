# Phase 4: Reboot + SSH Monitoring
print("\n--- Phase 4: Reboot & SSH Monitoring ---")
if trigger_reboot(device_info):
    if monitor_ssh_status(device_info["ip"]):
        
        # ✅ Phase 5: Post-Upgrade Verification
        print("\n--- Phase 5: Post-Upgrade Verification ---")
        verify_post_upgrade(device_info, target_version)

    else:
        print("[!] Device did not come back online. Cannot verify upgrade.")
else:
    print("[!] Reboot aborted. Skipping verification.")