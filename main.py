import os
import sys
import time
from getpass import getpass
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from device_handler import load_inventory
from route_collector import get_bgp_peers_summary
from route_dump import collect_received_routes, collect_advertised_routes


def main():
    # Load YAML inventory
    print("\U0001F4C2 Loading YAML...")
    inventory = load_inventory("inventory.yml")
    if not inventory:
        print("[!] Failed to load inventory file.")
        sys.exit(1)

    device_info = inventory["device"]
    print(f"✔️  Loaded device: {device_info['host']} with username: {device_info['username']}")

    # Ask for password
    password = getpass(f"Enter password for {device_info['host']}: ")

    # Connect to device
    print(f"\U0001F50E Attempting connection to device...")
    try:
        with Device(host=device_info["host"], user=device_info["username"], passwd=password) as dev:
            print(f"[+] Connected to {device_info['host']}")

            # Get hostname
            hostname = dev.facts.get("hostname", device_info["host"])

            # Collect BGP Peer Summary and Neighbor Info
            print("\U0001F5C3️ Sending <get-bgp-summary-information/> RPC...")
            peers = get_bgp_peers_summary(dev)
            print(f"✔️  Parsed {len(peers)} BGP peers (summary + neighbor info).")

            # Generate timestamp
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            summary_filename = f"{hostname}-BGP-Summary-{timestamp}.txt"
            routes_filename = f"{hostname}-BGP-Routes-{timestamp}.txt"

            # Write BGP summary to file
            with open(summary_filename, "w") as f:
                f.write(f"BGP Summary Report for {hostname}\n")
                f.write(f"Generated: {timestamp}\n")
                f.write("=" * 60 + "\n")
                for peer in peers:
                    f.write(f"Peer IP: {peer['peer_address']}\n")
                    f.write(f"State: {peer['peer_state']}\n")
                    f.write(f"Elapsed Time: {peer['elapsed_time']}\n")
                    f.write(f"Peer Type: {peer['peer_type']}\n")
                    f.write(f"Peer Group: {peer['peer_group']}\n")
                    f.write(f"Routing-Instance: {peer['routing_instance']}\n")
                    f.write(f"Peer ASN: {peer['peer_as']}\n")
                    f.write(f"Local ASN: {peer['local_as']}\n")
                    f.write(f"Local Address: {peer['local_address']}\n")
                    f.write(f"Route Table (RIB): {peer.get('rib_table', 'N/A')}\n")
                    f.write("Prefixes:\n")
                    f.write(f"  Received: {peer['received_prefix_count']}\n")
                    f.write(f"  Accepted: {peer['accepted_prefix_count']}\n")
                    f.write(f"  Advertised: {peer['advertised_prefix_count']}\n")
                    f.write(f"  Active: {peer['active_prefix_count']}\n")
                    f.write(f"  Suppressed: {peer['suppressed_prefix_count']}\n")
                    f.write("-" * 60 + "\n")
            print(f"\u2705 Summary saved to: {summary_filename}")

            # Write Received and Advertised Routes
            with open(routes_filename, "w") as f:
                f.write(f"BGP Route Collection for {hostname}\n")
                f.write(f"Generated: {timestamp}\n")
                f.write("=" * 60 + "\n")
                for peer in peers:
                    f.write(f"== Peer: {peer['peer_address']} | Table: {peer.get('rib_table', 'N/A')} ==\n")

                    # Collect advertised routes first (optional)
                    f.write("\n--- ADVERTISED ROUTES ---\n")
                    collect_advertised_routes(dev, peer, f)

                    # Collect received routes
                    f.write("\n--- RECEIVED ROUTES ---\n")
                    collect_received_routes(dev, peer, f)

                    f.write("\n" + "=" * 60 + "\n")

            print(f"\u2705 All route data saved to: {routes_filename}")

    except ConnectError as e:
        print(f"[!] Connection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
