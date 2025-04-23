from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease


def extract_destinations_from_rib(xml_data, expected_table):
    """
    Parses XML and extracts route destinations with next hops from the matching rib table.
    Returns a list of strings and a count of valid routes.
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
                    dest = route.get("rt-destination", "N/A")
                    nh_to = "N/A"
                    try:
                        rt_entry = route.get("rt-entry", {})
                        nh_data = rt_entry.get("nh", {})
                        if isinstance(nh_data, list):
                            nh_to = nh_data[0].get("to", "N/A")
                        else:
                            nh_to = nh_data.get("to", "N/A")
                    except Exception:
                        pass

                    matched_routes.append(f"- {dest}, Next hop: {nh_to}")

        return matched_routes, len(matched_routes)
    except Exception as e:
        return [f"[!] Error extracting routes: {e}"], 0


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

            if not rib or rib == "N/A":
                msg = f"== Peer: {peer_ip} | Table: N/A | Routes: 0 ==\n"
                print(f"[!] Skipping {peer_ip} — no rib table defined.")
                f.write(msg)
                f.write("[!] Skipped — no rib table defined.\n")
                f.write("=" * 60 + "\n\n")
                continue

            try:
                rpc = dev.rpc.get_route_information(
                    receive_protocol_name="bgp",
                    peer=peer_ip,
                    table=rib
                )
                rpc_xml = etree.tostring(rpc, pretty_print=True, encoding="unicode")
                routes, route_count = extract_destinations_from_rib(rpc_xml, rib)

                f.write(f"== Peer: {peer_ip} | Table: {rib} | Routes: {route_count} ==\n")
                f.write("\n--- RECEIVED ROUTES ---\n")
                for route in routes:
                    f.write(f"{route}\n")

                print(f"📥 Received routes collected for {peer_ip} ({route_count} routes)")

            except RpcError as e:
                msg = f"[!] Failed to get received routes for {peer_ip}: {e}"
                print(msg)
                f.write(f"== Peer: {peer_ip} | Table: {rib} | Routes: 0 ==\n")
                f.write("\n--- RECEIVED ROUTES ---\n")
                f.write(msg + "\n")

            f.write("=" * 60 + "\n\n")

    print(f"\n✅ Received route data saved to: {filename}")


def collect_advertised_routes(dev, peers, hostname, timestamp):
    """
    Collects ONLY advertised routes for each BGP peer and writes to a separate file.
    """
    filename = f"{hostname}-BGP-Advertised-Routes-{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(f"BGP Advertised Route Collection for {hostname}\nGenerated: {timestamp}\n\n")

        for peer in peers:
            peer_ip = peer["peer_ip"]
            rib = peer["rib_table"]

            if not rib or rib == "N/A":
                msg = f"== Peer: {peer_ip} | Table: N/A | Routes: 0 ==\n"
                print(f"[!] Skipping {peer_ip} — no rib table defined.")
                f.write(msg)
                f.write("[!] Skipped — no rib table defined.\n")
                f.write("=" * 60 + "\n\n")
                continue

            try:
                rpc = dev.rpc.get_route_information(
                    advertising_protocol_name="bgp",
                    neighbor=peer_ip,
                    table=rib
                )
                rpc_xml = etree.tostring(rpc, pretty_print=True, encoding="unicode")
                routes, route_count = extract_destinations_from_rib(rpc_xml, rib)

                f.write(f"== Peer: {peer_ip} | Table: {rib} | Routes: {route_count} ==\n")
                f.write("\n--- ADVERTISED ROUTES ---\n")
                for route in routes:
                    f.write(f"{route}\n")

                print(f"📤 Advertised routes collected for {peer_ip} ({route_count} routes)")

            except RpcError as e:
                msg = f"[!] Failed to get advertised routes for {peer_ip}: {e}"
                print(msg)
                f.write(f"== Peer: {peer_ip} | Table: {rib} | Routes: 0 ==\n")
                f.write("\n--- ADVERTISED ROUTES ---\n")
                f.write(msg + "\n")

            f.write("=" * 60 + "\n\n")

    print(f"\n✅ Advertised route data saved to: {filename}")
