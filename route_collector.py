from lxml import etree               # Required for converting RPC responses to XML strings
import jxmlease                      # Converts XML to native Python dictionaries


def get_bgp_peers_summary(dev):
    """
    Collects BGP peer information from a Junos device using both summary and neighbor RPCs.

    Returns:
        List[dict]: One dictionary per peer with routing state, prefix counts, and RIB table.
    """
    peers = []

    try:
        # === Step 1: Get BGP summary (prefix counts, state, etc.) ===
        summary_rpc = dev.rpc.get_bgp_summary_information()
        summary_xml = etree.tostring(summary_rpc, pretty_print=True, encoding="unicode")
        summary_data = jxmlease.parse(summary_xml)

        bgp_info = summary_data.get("bgp-information", {})
        peer_entries = bgp_info.get("bgp-peer", [])

        if not isinstance(peer_entries, list):
            peer_entries = [peer_entries]

        for peer in peer_entries:
            peer_ip = peer.get("peer-address", "N/A")

            # Default values (fallbacks in case neighbor RPC fails)
            accepted = peer.get("accepted-prefix-count", "N/A")
            received = peer.get("received-prefix-count", "N/A")
            active = peer.get("active-prefix-count", "N/A")
            suppressed = peer.get("suppressed-prefix-count", "N/A")
            advertised = "N/A"
            rib_table = "N/A"
            local_addr = "N/A"
            local_asn = "N/A"
            peer_group = "N/A"
            peer_rti = "N/A"
            peer_type = "N/A"

            # === Step 2: Get BGP neighbor information (for RIB + advertised count) ===
            try:
                neighbor_rpc = dev.rpc.get_bgp_neighbor_information(neighbor_address=peer_ip)
                neighbor_xml = etree.tostring(neighbor_rpc, pretty_print=True, encoding="unicode")
                neighbor_data = jxmlease.parse(neighbor_xml)

                bgp_peer_info = neighbor_data.get("bgp-information", {}).get("bgp-peer", {})

                if isinstance(bgp_peer_info, dict):
                    # Extract common fields
                    rib = bgp_peer_info.get("bgp-rib", {})
                    if isinstance(rib, dict):
                        rib_table = rib.get("name", "N/A")
                        # Prefer neighbor-level prefix counts (more accurate)
                        received = rib.get("received-prefix-count", received)
                        accepted = rib.get("accepted-prefix-count", accepted)
                        active = rib.get("active-prefix-count", active)
                        suppressed = rib.get("suppressed-prefix-count", suppressed)
                        advertised = rib.get("advertised-prefix-count", "N/A")

                    local_addr = bgp_peer_info.get("local-address", "N/A")
                    local_asn = bgp_peer_info.get("local-as", "N/A")
                    peer_group = bgp_peer_info.get("peer-group", "N/A")
                    peer_rti = bgp_peer_info.get("peer-cfg-rti", "N/A")
                    peer_type = bgp_peer_info.get("peer-type", "N/A")

            except Exception as e:
                print(f"[!] Warning: Failed to fetch neighbor details for {peer_ip}: {e}")

            peer_info = {
                "peer_ip": peer_ip,
                "peer_as": peer.get("peer-as", "N/A"),
                "state": peer.get("peer-state", "N/A"),
                "elapsed_time": peer.get("elapsed-time", "N/A"),
                "accepted_prefixes": accepted,
                "received_prefixes": received,
                "active_prefixes": active,
                "suppressed_prefixes": suppressed,
                "advertised_prefixes": advertised,
                "rib_table": rib_table,
                "local_address": local_addr,
                "local_as": local_asn,
                "peer_group": peer_group,
                "peer_rti": peer_rti,
                "peer_type": peer_type,
            }

            peers.append(peer_info)

        print(f"✅ Parsed {len(peers)} BGP peers (summary + neighbor info).")
        return peers

    except Exception as e:
        print(f"[!] Error during BGP summary collection: {e}")
        return []
