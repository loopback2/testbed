from jnpr.junos.exception import RpcError
from lxml import etree

def collect_routes(dev, peers, hostname, timestamp):
    """
    For each peer, collect all received and advertised BGP routes and
    write to a timestamped route output file.
    """
    route_filename = f"{hostname}-BGP-Routes-{timestamp}.txt"

    with open(route_filename, "w") as f:
        f.write(f"BGP Route Collection for {hostname}\nGenerated: {timestamp}\n\n")

        for peer in peers:
            peer_ip = peer["peer_ip"]
            rib = peer["rib_table"]

            f.write(f"== Peer: {peer_ip} | Table: {rib} ==\n")

            # --- Received Routes ---
            try:
                recv_rpc = dev.rpc.get_route_information(
                    receive_protocol_name="bgp",
                    peer=peer_ip,
                    table=rib
                )
                recv_text = etree.tostring(recv_rpc, pretty_print=True, encoding="unicode")
                f.write(f"\n--- RECEIVED ROUTES ---\n")
                f.write(recv_text + "\n")
                print(f"📥 Received routes collected for {peer_ip}")
            except RpcError as e:
                msg = f"[!] Failed to get received routes for {peer_ip}: {e}"
                print(msg)
                f.write(f"\n{msg}\n")

            # --- Advertised Routes ---
            try:
                adv_rpc = dev.rpc.get_route_information(
                    peer=peer_ip,
                    table=rib,
                    advertised=True
                )
                adv_text = etree.tostring(adv_rpc, pretty_print=True, encoding="unicode")
                f.write(f"\n--- ADVERTISED ROUTES ---\n")
                f.write(adv_text + "\n")
                print(f"📤 Advertised routes collected for {peer_ip}")
            except RpcError as e:
                msg = f"[!] Failed to get advertised routes for {peer_ip}: {e}"
                print(msg)
                f.write(f"\n{msg}\n")

            f.write("=" * 60 + "\n\n")

    print(f"✅ All route data written to {route_filename}")
