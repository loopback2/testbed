import os
from lxml import etree
from jnpr.junos.exception import RpcError
from datetime import datetime

def collect_received_routes(dev, hostname, peers):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{hostname}-BGP-Routes-{timestamp}.txt"

    with open(output_file, "w") as file:
        file.write(f"BGP Route Collection for {hostname}\n")
        file.write(f"Generated: {timestamp}\n\n")

        for peer in peers:
            peer_ip = peer['peer_ip']
            rib = peer.get("rib_table", "N/A")
            file.write(f"== Peer: {peer_ip} | Table: {rib} ==\n")

            if rib == "N/A":
                file.write("[!] Skipping (no RIB table found)\n\n")
                continue

            # --- RECEIVED ROUTES ---
            file.write("--- RECEIVED ROUTES ---\n")
            try:
                received_rpc = dev.rpc.get_route_information(
                    table=rib,
                    receive_protocol_name="bgp",
                    peer=peer_ip
                )
                routes = received_rpc.findall(".//rt")
                if not routes:
                    file.write("No received routes found.\n\n")
                    continue

                file.write(f"[✓] Received routes collected for {peer_ip} ({len(routes)} routes)\n")
                for route in routes:
                    destination = route.findtext("rt-destination", default="N/A")
                    next_hop = route.findtext("rt-entry/nh/to", default="N/A")
                    file.write(f"- {destination}, Next hop: {next_hop}\n")
                file.write("\n")

            except RpcError as e:
                file.write(f"[!] Failed to get received routes for {peer_ip}: {e}\n\n")

    print(f"\n[✓] All route data saved to: {output_file}\n")
    return output_file


def collect_advertised_routes(dev, hostname, peers):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{hostname}-BGP-Routes-{timestamp}.txt"

    with open(output_file, "a") as file:
        for peer in peers:
            peer_ip = peer['peer_ip']
            rib = peer.get("rib_table", "N/A")
            file.write(f"== Peer: {peer_ip} | Table: {rib} ==\n")

            if rib == "N/A":
                file.write("[!] Skipping (no RIB table found)\n\n")
                continue

            # --- ADVERTISED ROUTES ---
            file.write("--- ADVERTISED ROUTES ---\n")
            try:
                adv_rpc = dev.rpc.get_route_information(
                    table=rib,
                    advertising_protocol_name="bgp",
                    neighbor=peer_ip
                )
                routes = adv_rpc.findall(".//rt")
                if not routes:
                    file.write("No advertised routes found.\n\n")
                    continue

                file.write(f"[✓] Advertised routes collected for {peer_ip} ({len(routes)} routes)\n")
                for route in routes:
                    destination = route.findtext("rt-destination", default="N/A")
                    next_hop = route.findtext("rt-entry/nh/to", default="N/A")
                    file.write(f"- {destination}, Next hop: {next_hop}\n")
                file.write("\n")

            except RpcError as e:
                file.write(f"[!] Failed to get advertised routes for {peer_ip}: {e}\n\n")

    print(f"[✓] All advertised route data appended to: {output_file}\n")
    return output_file