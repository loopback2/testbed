from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease
from lxml.builder import E


def extract_route_destinations(xml_data):
    """
    Parses XML and returns a list of all <rt-destination> entries.
    """
    try:
        parsed = jxmlease.parse(xml_data)
        routes = parsed.get("route-information", {}).get("rt", [])
        if not isinstance(routes, list):
            routes = [routes]

        destinations = []
        for route in routes:
            dest = route.get("rt-destination")
            if dest:
                destinations.append(dest)
        return destinations
    except Exception as e:
        return [f"[!] Failed to parse XML: {e}"]


def collect_routes(dev, peers, hostname, timestamp):
    """
    Collects advertised and received BGP routes for each peer and writes them to a file.
    """
    route_filename = f"{hostname}-BGP-Routes-{timestamp}.txt"

    with open(route_filename, "w") as f:
        f.write(f"BGP Route Collection for {hostname}\nGenerated: {timestamp}\n\n")

        for peer in peers:
            peer_ip = peer["peer_ip"]
            rib = peer["rib_table"]

            f.write(f"== Peer: {peer_ip} | Table: {rib} ==\n")

            # ----------------------
            # ADVERTISED ROUTES
            # ----------------------
            f.write("\n--- ADVERTISED ROUTES ---\n")
            try:
                advertised_rpc = E.get_route_information(
                    E.table(rib),
                    E("advertising-protocol-name", "bgp"),
                    E.neighbor(peer_ip)
                )
                adv_response = dev.rpc(advertised_rpc)
                adv_xml = etree.tostring(adv_response, pretty_print=True, encoding="unicode")
                adv_routes = extract_route_destinations(adv_xml)

                if adv_routes:
                    for route in adv_routes:
                        f.write(f"- {route}\n")
                else:
                    f.write("No advertised routes found.\n")

                print(f"📤 Advertised routes collected for {peer_ip}")

            except RpcError as e:
                msg = f"[!] Failed to get advertised routes for {peer_ip}: {e}"
                print(msg)
                f.write(msg + "\n")

            # ----------------------
            # RECEIVED ROUTES
            # ----------------------
            f.write("\n--- RECEIVED ROUTES ---\n")
            try:
                recv_rpc = dev.rpc.get_route_information(
                    receive_protocol_name="bgp",
                    peer=peer_ip,
                    table=rib
                )
                recv_xml = etree.tostring(recv_rpc, pretty_print=True, encoding="unicode")
                recv_routes = extract_route_destinations(recv_xml)

                if recv_routes:
                    for route in recv_routes:
                        f.write(f"- {route}\n")
                else:
                    f.write("No received routes found.\n")

                print(f"📥 Received routes collected for {peer_ip}")

            except RpcError as e:
                msg = f"[!] Failed to get received routes for {peer_ip}: {e}"
                print(msg)
                f.write(msg + "\n")

            f.write("=" * 60 + "\n\n")

    print(f"\n✅ All route data written to: {route_filename}")
