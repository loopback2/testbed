from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease


def extract_destinations_from_rib(xml_data, expected_table):
    """
    Extracts only <rt-destination> values from the matching route table.
    """
    try:
        parsed = jxmlease.parse(xml_data)
        tables = parsed.get("route-information", {}).get("route-table", [])
        if not isinstance(tables, list):
            tables = [tables]

        matched_routes = []
        for table in tables:
            name = table.get("table-name", "")
            if name == expected_table:
                routes = table.get("rt", [])
                if not isinstance(routes, list):
                    routes = [routes]

                for route in routes:
                    dest = route.get("rt-destination")
                    if dest:
                        matched_routes.append(dest)

        return matched_routes or ["[!] No routes found in matching rib."]
    except Exception as e:
        return [f"[!] Error extracting routes: {e}"]


def collect_routes(dev, peers, hostname, timestamp):
    """
    Collects ONLY received routes for each BGP peer and writes to a file.
    """
    filename = f"{hostname}-BGP-Routes-{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(f"BGP Route Collection for {hostname}\nGenerated: {timestamp}\n\n")

        for peer in peers:
            peer_ip = peer["peer_ip"]
            rib = peer["rib_table"]

            f.write(f"== Peer: {peer_ip} | Table: {rib or 'N/A'} ==\n")

            if not rib or rib == "N/A":
                msg = f"[!] Skipping {peer_ip} — no rib table defined.\n"
                print(msg.strip())
                f.write(msg + "\n")
                f.write("=" * 60 + "\n\n")
                continue

            f.write("\n--- RECEIVED ROUTES ---\n")
            try:
                rpc = dev.rpc.get_route_information(
                    receive_protocol_name="bgp",
                    peer=peer_ip,
                    table=rib
                )
                rpc_xml = etree.tostring(rpc, pretty_print=True, encoding="unicode")
                routes = extract_destinations_from_rib(rpc_xml, rib)

                for route in routes:
                    f.write(f"- {route}\n")
                print(f"📥 Received routes collected for {peer_ip}")

            except RpcError as e:
                msg = f"[!] Failed to get received routes for {peer_ip}: {e}"
                print(msg)
                f.write(msg + "\n")

            f.write("=" * 60 + "\n\n")

    print(f"\n✅ Received route data saved to: {filename}")
