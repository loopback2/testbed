# route_dump.py

# === Juniper + XML Libraries ===
# RpcError helps catch NETCONF-related RPC failures.
from jnpr.junos.exception import RpcError

# etree is used to convert Junos RPC XML responses into raw strings.
from lxml import etree

# jxmlease parses Junos XML into Python-native dictionaries.
import jxmlease


def extract_destinations_from_rib(xml_data, expected_table):
    """
    Parses Junos XML and extracts BGP route destinations and next hops from a specific RIB table.

    Parameters:
        xml_data (str): Raw XML string from Junos RPC output.
        expected_table (str): Route table name (e.g. "CORE.inet.0") to filter for.

    Returns:
        matched_routes (list[str]): Formatted route entries like "- 10.0.0.0/24, Next hop: 10.1.1.1".
        count (int): Total number of routes matched in that table.
    """
    try:
        # Convert XML to a structured Python dict
        parsed = jxmlease.parse(xml_data)

        # Extract list of route-tables. Junos can return multiple.
        tables = parsed.get("route-information", {}).get("route-table", [])
        if not isinstance(tables, list):
            tables = [tables]

        matched_routes = []

        for table in tables:
            name = table.get("table-name", "")
            if name == expected_table:
                # Grab the list of individual routes ("rt" = route).
                routes = table.get("rt", [])
                if not isinstance(routes, list):
                    routes = [routes]

                for route in routes:
                    dest = route.get("rt-destination", "N/A")  # Destination prefix
                    nh_to = "N/A"  # Next-hop placeholder

                    # Extract <nh><to> value (next-hop)
                    try:
                        rt_entry = route.get("rt-entry", {})
                        nh_data = rt_entry.get("nh", {})

                        if isinstance(nh_data, list):
                            nh_to = nh_data[0].get("to", "N/A")
                        else:
                            nh_to = nh_data.get("to", "N/A")
                    except Exception:
                        pass  # Next-hop not critical, fallback to N/A

                    # Append formatted string to results
                    matched_routes.append(f"- {dest}, Next hop: {nh_to}")

        return matched_routes, len(matched_routes)

    except Exception as e:
        return [f"[!] Error extracting routes: {e}"], 0


def collect_routes(dev, peers, hostname, timestamp):
    """
    Collects RECEIVED BGP routes for each peer using the Junos RPC:
        <get-route-information receive-protocol-name="bgp" .../>

    Output:
        Creates a timestamped file showing received routes per BGP peer.
    """
    filename = f"{hostname}-BGP-Routes-{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(f"BGP Route Collection for {hostname}\nGenerated: {timestamp}\n\n")

        for peer in peers:
            peer_ip = peer["peer_ip"]
            rib = peer["rib_table"]

            # Skip peers with no RIB (e.g., inactive or misconfigured).
            if not rib or rib == "N/A":
                msg = f"== Peer: {peer_ip} | Table: N/A | Routes: 0 ==\n"
                print(f"[!] Skipping {peer_ip} — no rib table defined.")
                f.write(msg)
                f.write("[!] Skipped — no rib table defined.\n")
                f.write("=" * 60 + "\n\n")
                continue

            try:
                # Perform the RPC call to fetch received BGP routes for this peer.
                rpc = dev.rpc.get_route_information(
                    receive_protocol_name="bgp",
                    peer=peer_ip,
                    table=rib
                )
                # Convert raw XML to string and extract desired data
                rpc_xml = etree.tostring(rpc, pretty_print=True, encoding="unicode")
                routes, route_count = extract_destinations_from_rib(rpc_xml, rib)

                # Write routes to file, grouped by peer
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
    Collects ADVERTISED BGP routes per peer using the Junos RPC:
        <get-route-information advertising-protocol-name="bgp" .../>

    Output:
        Writes advertised route data to a timestamped text file for each peer.
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
                # Call Junos RPC to get advertised routes sent TO the neighbor
                rpc = dev.rpc.get_route_information(
                    advertising_protocol_name="bgp",
                    neighbor=peer_ip,
                    table=rib
                )
                rpc_xml = etree.tostring(rpc, pretty_print=True, encoding="unicode")
                routes, route_count = extract_destinations_from_rib(rpc_xml, rib)

                # Write header + route list
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
