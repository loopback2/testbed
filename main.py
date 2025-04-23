# main.py

# === Module Imports ===
# These imports are modular function calls from our supporting scripts.
# load_device_from_yaml loads connection info; connect_to_device handles NETCONF session.
from device_handler import load_device_from_yaml, connect_to_device

# get_bgp_peers_summary retrieves peer summary using RPCs (show bgp neighbor + summary).
from route_collector import get_bgp_peers_summary

# collect_routes fetches received routes, collect_advertised_routes fetches outbound advertisements.
from route_dump import collect_routes, collect_advertised_routes

# Used to generate timestamped output files.
from datetime import datetime


def main():
    # === Step 1: Load Device from YAML Inventory ===
    print("📁 Loading YAML...")

    try:
        # Attempt to load device connection info from inventory.yml.
        device = load_device_from_yaml("inventory.yml")
        print(f"📡 Loaded device: {device['host']} with username: {device['username']}")
    except Exception as e:
        print(f"[!] Failed to load YAML or missing keys: {e}")
        return  # Stop script if inventory is missing or malformed.

    # === Step 2: Connect to the Juniper Device via NETCONF ===
    print("🔌 Attempting connection to device...")
    dev = connect_to_device(device)

    if not dev:
        print("[!] Connection failed.")
        return  # Exit if unable to connect (device offline, auth fail, etc.)

    # === Step 3: Prepare Timestamped Output Filenames ===
    dev_hostname = dev.facts.get("hostname", device["host"])  # Prefer Junos hostname if available.
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Used in filenames to version outputs.
    summary_filename = f"{dev_hostname}-BGP-Summary-{timestamp}.txt"  # File to save BGP peer info.

    # === Step 4: Collect BGP Peer Summary via Junos RPC ===
    print("📊 Gathering BGP peer summary and neighbor info...")
    peers = get_bgp_peers_summary(dev)  # Returns list of peer dictionaries with detailed metadata.

    # === Step 5: Output Summary to Terminal and File ===
    if peers:
        print("\n=== BGP PEER SUMMARY ===")
        with open(summary_filename, "w") as f:
            # File header for context and tracking.
            f.write(f"BGP Peer Summary for {dev_hostname} ({device['host']})\n")
            f.write(f"Generated: {timestamp}\n\n")

            for peer in peers:
                # Each peer is printed as a human-readable block for quick troubleshooting or auditing.
                block = [
                    f"Peer IP: {peer['peer_ip']}",
                    f"  State: {peer['state']}",
                    f"  Elapsed Time: {peer['elapsed_time']}",
                    f"  Peer Type: {peer['peer_type']}",
                    f"  Peer Group: {peer['peer_group']}",
                    f"  Routing-Instance: {peer['peer_rti']}",
                    f"  Peer ASN: {peer['peer_as']}",
                    f"  Local ASN: {peer['local_as']}",
                    f"  Local Address: {peer['local_address']}",
                    f"  Route Table (RIB): {peer['rib_table']}",
                    f"  Prefixes:",
                    f"    Received: {peer['received_prefixes']}",
                    f"    Accepted: {peer['accepted_prefixes']}",
                    f"    Advertised: {peer['advertised_prefixes']}",
                    f"    Active: {peer['active_prefixes']}",
                    f"    Suppressed: {peer['suppressed_prefixes']}",
                    "-" * 60,
                ]

                for line in block:
                    print(line)       # Print to screen for live review.
                    f.write(line + "\n")  # Write to file for documentation.
        print(f"\n✅ Summary saved to: {summary_filename}")

        # === Step 6: Gather Detailed Route Tables ===
        # This is your deep-dive data used for validating routing state before/after changes.
        collect_routes(dev, peers, dev_hostname, timestamp)             # Received routes (via `show route receive-protocol bgp`)
        collect_advertised_routes(dev, peers, dev_hostname, timestamp)  # Advertised routes (via `show route advertising-protocol bgp`)

    else:
        print("⚠️ No BGP peers found or failed to parse.")  # Fallback if no data parsed.

    # === Step 7: Cleanup ===
    dev.close()  # Always close the NETCONF session.
    print("🔒 Connection closed.")


# This ensures the script only runs when executed directly, not when imported.
if __name__ == "__main__":
    main()
