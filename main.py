from device_handler import load_device_from_yaml, connect_to_device
from route_collector import get_bgp_peers_summary
from route_dump import collect_received_routes, collect_advertised_routes
from datetime import datetime


def main():
    print("\n📁 Loading YAML...")
    device_info = load_device_from_yaml("device.yml")

    for device in device_info['devices']:
        ip = device['ip']
        username = device['username']
        print(f"✅ Loaded device: {ip} with username: {username}")
        print(f"🔌 Attempting connection to device...")

        dev = connect_to_device(device)
        if not dev:
            print(f"[!] Failed to connect to {ip}")
            continue

        print("🛰️  Sending <get-bgp-summary-information/> RPC...")
        peers = get_bgp_peers_summary(dev)
        print(f"✅ Parsed {len(peers)} BGP peers (summary + neighbor info).\n")

        hostname = dev.facts.get("hostname", ip)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        summary_filename = f"{hostname}-BGP-Summary-{timestamp}.txt"
        routes_filename = f"{hostname}-BGP-Routes-{timestamp}.txt"

        with open(summary_filename, "w") as summary_file:
            print("\n" + "=" * 60, file=summary_file)
            print(f"BGP Summary Report for {hostname}", file=summary_file)
            print(f"Generated: {timestamp}", file=summary_file)
            print("=" * 60 + "\n", file=summary_file)

            for peer in peers:
                print(f"📦 Peer IP: {peer['peer_address']}")
                print(f"Peer IP: {peer['peer_address']}", file=summary_file)
                print(f"  State: {peer['peer_state']}", file=summary_file)
                print(f"  ASN: {peer['peer_as']}", file=summary_file)
                print(f"  Routing-Instance: {peer['routing_instance']}", file=summary_file)
                print(f"  Group: {peer['peer_group']}", file=summary_file)
                print(f"  Type: {peer['peer_type']}", file=summary_file)
                print(f"  Local Address: {peer['local_address']}", file=summary_file)
                print(f"  Elapsed Time: {peer['elapsed_time']}", file=summary_file)
                print(f"  Received: {peer['received_prefix_count']}", file=summary_file)
                print(f"  Accepted: {peer['accepted_prefix_count']}", file=summary_file)
                print(f"  Advertised: {peer['advertised_prefix_count']}", file=summary_file)
                print(f"  Active: {peer['active_prefix_count']}", file=summary_file)
                print(f"  Suppressed: {peer['suppressed_prefix_count']}", file=summary_file)
                rib = peer.get("rib_table", "N/A")
                print(f"  Route Table (RIB): {rib}", file=summary_file)
                print("-" * 60, file=summary_file)

        print(f"✅ Summary saved to: {summary_filename}\n")

        print("📬 Gathering advertised and received route data...")
        with open(routes_filename, "w") as route_file:
            print(f"BGP Route Collection for {hostname}", file=route_file)
            print(f"Generated: {timestamp}\n", file=route_file)

            for peer in peers:
                print(f"== Peer: {peer['peer_address']} | Table: {peer.get('rib_table', 'N/A')} ==", file=route_file)

                print("\n--- ADVERTISED ROUTES ---", file=route_file)
                advertised_count = collect_advertised_routes(dev, peer, route_file)

                print("\n--- RECEIVED ROUTES ---", file=route_file)
                received_count = collect_received_routes(dev, peer, route_file)

                print("\n" + ("=" * 60) + "\n", file=route_file)

        print(f"✅ All route data saved to: {routes_filename}\n")
        print("🔒 Connection closed.")
        dev.close()


if __name__ == "__main__":
    main()
