from device_handler import load_device_from_yaml, connect_to_device
from route_collector import get_bgp_peers_summary

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

    print("📊 Gathering BGP peer summary...")
    peers = get_bgp_peers_summary(dev)

    if peers:
        print("\n=== BGP PEER SUMMARY ===")
        for peer in peers:
            print(f"Peer IP: {peer['peer_ip']} | VRF: {peer['instance']} | Group: {peer['group']}")
            print(f"  ASN: {peer['peer_as']} | Type: {peer['type']} | State: {peer['state']}")
            print(f"  Prefixes - Active: {peer['active_prefixes']} | "
                  f"Received: {peer['received_prefixes']} | "
                  f"Accepted: {peer['accepted_prefixes']} | "
                  f"Advertised: {peer['advertised_prefixes']}")
            print("-" * 60)
    else:
        print("⚠️ No BGP peers found or failed to parse.")

    dev.close()
    print("🔒 Connection closed.")

if __name__ == "__main__":
    main()
