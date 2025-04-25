from lxml import etree
import jxmlease

def get_bgp_peers_summary(dev):
    """
    Fetches BGP summary and neighbor information using RPCs.
    Returns a list of dictionaries, one per BGP peer.
    """
    peers = []

    try:
        # Step 1: Get BGP summary (peer IP, ASN, state, etc.)
        summary_rpc = dev.rpc.get_bgp_summary_information()
        summary_xml = etree.tostring(summary_rpc, pretty_print=True, encoding="unicode")
        summary_data = jxmlease.parse(summary_xml)

        bgp_info = summary_data.get("bgp-information", {})
        peer_entries = bgp_info.get("bgp-peer", [])

        if not isinstance(peer_entries, list):
            peer_entries = [peer_entries]

        for peer in peer_entries:
            peer_ip = peer.get("peer-address", "N/A")

            # Step 2: Get neighbor-specific info (for rib and next-hop data)
            neighbor_rpc = dev.rpc.get_bgp_neighbor_information(neighbor_address=peer_ip)
            neighbor_xml = etree.tostring(neighbor_rpc, pretty_print=True, encoding="unicode")
            neighbor_data = jxmlease.parse(neighbor_xml)

            # Extract deeper fields from neighbor block
            bgp_peer_info = neighbor_data.get("bgp-information", {}).get("bgp-peer", {})
            rib_table = "N/A"
            if isinstance(bgp_peer_info, dict):
                rib = bgp_peer_info.get("bgp-rib", {})
                if isinstance(rib, dict):
                    rib_table = rib.get("name", "N/A")

            # Merge summary + neighbor data
            peer_info = {
                "peer_ip": peer_ip,
                "peer_as": peer.get("peer-as", "N/A"),
                "state": peer.get("peer-state", "N/A"),
                "elapsed_time": peer.get("elapsed-time", "N/A"),

                # Pull these from summary RPC (original)
                "accepted_prefixes": peer.get("accepted-prefix-count", "N/A"),
                "received_prefixes": peer.get("received-prefix-count", "N/A"),
                "advertised_prefixes": peer.get("advertised-prefix-count", "N/A"),
                "active_prefixes": peer.get("active-prefix-count", "N/A"),
                "suppressed_prefixes": peer.get("suppressed-prefix-count", "N/A"),

                # Pull these from neighbor RPC
                "rib_table": rib_table,
                "local_address": bgp_peer_info.get("local-address", "N/A"),
                "local_as": bgp_peer_info.get("local-as", "N/A"),
                "peer_group": bgp_peer_info.get("peer-group", "N/A"),
                "peer_rti": bgp_peer_info.get("peer-cfg-rti", "N/A"),
                "peer_type": bgp_peer_info.get("peer-type", "N/A"),
            }

            peers.append(peer_info)

        print(f"✅ Parsed {len(peers)} BGP peers (summary + neighbor info).")
        return peers

    except Exception as e:
        print(f"[!] Error gathering BGP peer summary: {e}")
        return []
