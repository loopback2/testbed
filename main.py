from datetime import datetime
from device_handler import load_device_from_yaml, connect_to_device
from route_collector import get_bgp_peers_summary
from route_dump import collect_received_routes, collect_advertised_routes

def main():
    print("📁 Loading YAML...")
    try:
        device = load_device_from_yaml("inventory.yml")
        print(f"📡 Loaded device: {device['host']} with username: {device['username']}")
    except Exception as e:
        print(f"[!] Failed to load YAML or missing keys: {e}")
        return

    print("🔌 Attempting connection to device...")
    dev = connect_to_device(device)
    if not dev:
        print("[!] Connection failed.")
        return

    dev_hostname = dev.facts.get("hostname", device["host"])
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    summary_file = f"{dev_hostname}-BGP-Summary-{timestamp}.txt"
    routes_file = f"{dev_hostname}-BGP-Routes-{timestamp}.txt"

    peers = get_bgp_peers_summary(dev)

    if peers:
        # --- Summary Output ---
        with open(summary_file, "w") as f:
            f.write(f"BGP Peer Summary for {dev_hostname} ({device['host']})\n")
            f.write(f"Generated: {timestamp}\n\n")
            for peer in peers:
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
                    f"  Route Table (RIB): {peer.get('rib_table', 'N/A')}",
                    f"  Prefixes:",
                    f"    Received: {peer['received_prefixes']}",
                    f"    Accepted: {peer['accepted_prefixes']}",
                    f"    Advertised: {peer['advertised_prefixes']}",
                    f"    Active: {peer['active_prefixes']}",
                    f"    Suppressed: {peer['suppressed_prefixes']}",
                    "-" * 60,
                ]
                for line in block:
                    print(line)
                    f.write(line + "\n")
        print(f"\n✅ Summary saved to: {summary_file}")

        # --- Routes Output ---
        with open(routes_file, "w") as f:
            f.write(f"BGP Route Collection for {dev_hostname}\nGenerated: {timestamp}\n\n")
            for peer in peers:
                peer_ip = peer["peer_ip"]
                rib = peer["rib_table"]
                f.write(f"== Peer: {peer_ip} | Table: {rib or 'N/A'} ==\n")

                # Advertised
                f.write("\n--- ADVERTISED ROUTES ---\n")
                if not rib or rib == "N/A":
                    f.write("No rib defined, skipping advertised.\n")
                else:
                    adv = collect_advertised_routes(dev, peer_ip, rib)
                    for route in adv:
                        f.write(route + "\n")

                # Received
                f.write("\n--- RECEIVED ROUTES ---\n")
                if not rib or rib == "N/A":
                    f.write("No rib defined, skipping received.\n")
                else:
                    recv = collect_received_routes(dev, peer_ip, rib)
                    for route in recv:
                        f.write(route + "\n")

                f.write("=" * 60 + "\n\n")

        print(f"\n✅ Route data saved to: {routes_file}")
    else:
        print("⚠️ No BGP peers found or failed to parse.")

    dev.close()
    print("🔒 Connection closed.")

if __name__ == "__main__":
    main()
