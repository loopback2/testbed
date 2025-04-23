from device_handler import load_device_from_yaml, connect_to_device
from route_collector import get_bgp_peers_summary
from route_dump import collect_routes, collect_advertised_routes  # <- NEW
from datetime import datetime


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
    summary_filename = f"{dev_hostname}-BGP-Summary-{timestamp}.txt"

    print("📊 Gathering BGP peer summary and neighbor info...")
    peers = get_bgp_peers_summary(dev)

    if peers:
        print("\n=== BGP PEER SUMMARY ===")
        with open(summary_filename, "w") as f:
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
                    print(line)
                    f.write(line + "\n")
        print(f"\n✅ Summary saved to: {summary_filename}")

        # 🔄 Collect received and advertised routes
        collect_routes(dev, peers, dev_hostname, timestamp)
        collect_advertised_routes(dev, peers, dev_hostname, timestamp)  # <- NEW

    else:
        print("⚠️ No BGP peers found or failed to parse.")

    dev.close()
    print("🔒 Connection closed.")


if __name__ == "__main__":
    main()
