from device_handler import load_device_from_yaml, connect_to_device
from route_collector import get_bgp_peers_summary
from output_formatter import print_peer_summary

def main():
    # Load device info (single device for now)
    device_info = load_device_from_yaml("inventory.yml")

    # Connect via PyEZ
    dev = connect_to_device(device_info)
    if not dev:
        print(f"[!] Failed to connect to {device_info['host']}")
        return

    # Gather BGP peer summary using RPC
    peer_data = get_bgp_peers_summary(dev)

    # Format and display summary in terminal
    print_peer_summary(device_info["host"], peer_data)

    dev.close()

if __name__ == "__main__":
    main()
