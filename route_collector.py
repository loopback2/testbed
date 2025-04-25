# route_collector.py

from lxml import etree  # Used to convert Junos RPC responses to XML strings
import jxmlease         # Converts Junos XML into Python-native dictionaries


def get_bgp_peers_summary(dev):
    """
    Collects BGP peer information from a Junos device.

    Steps:
    1. Run <get-bgp-summary-information/> to gather basic peer stats.
    2. Run <get-bgp-neighbor-information neighbor=x.x.x.x/> for deeper info (e.g., RIB table).
    3. Return a list of dictionaries representing all known BGP peers and their metadata.

    Args:
        dev (Device): Junos PyEZ device object (NETCONF connection)

    Returns:
        List[dict]: One dictionary per peer containing BGP state, prefix counters, and rib info
    """
    peers = []

    try:
        # === STEP 1: Get BGP summary ===
        summary_rpc = dev.rpc.get_bgp_summary_information()
        summary_xml = etree.tostring(summary_rpc, pretty_print=True, encoding="unicode")
        summary_data = jxmlease.parse(summary_xml)

        bgp_info = summary_data.get("bgp-information", {})
        peer_entries = bgp_info.get("bgp-peer", [])

        if not isinstance(peer_entries, list):
            peer_entries = [peer_entries]

        for peer in peer_entries:
            peer_ip = peer.get("peer-address", "N/A")

            # === STEP 2: Query deeper neighbor info ===
            neighbor_rpc = dev.rpc.get_bgp_neighbor_information(neighbor_address=peer_ip)
            neighbor_xml = etree.tostring(neighbor_rpc, pretty_print=True, encoding="unicode")
            neighbor_data = jxmlease.parse(neighbor_xml)

            bgp_peer_info = neighbor_data.get("bgp-information", {}).get("bgp-peer", {})
            rib_table = "N/A"

            if isinstance(bgp_peer_info, dict):
                rib = bgp_peer_info.get("bgp-rib", {})
                if isinstance(rib, dict):
                    rib_table = rib.get("name", "N/A")
            else:
                rib = {}

            # === Extract prefix counters from summary 'bgp-rib' ===
            rib_data = peer.get("bgp-rib", {})
            if isinstance(rib_data, dict):
                received = rib_data.get("received-prefix-count", "N/A")
                accepted = rib_data.get("accepted-prefix-count", "N/A")
                advertised = rib_data.get("advertised-prefix-count", "N/A")
                active = rib_data.get("active-prefix-count", "N/A")
                suppressed = rib_data.get("suppressed-prefix-count", "N/A")
            else:
                received = accepted = advertised = active = suppressed = "N/A"

            # === Compile peer summary ===
            peer_info = {
                "peer_ip": peer_ip,
                "peer_as": peer.get("peer-as", "N/A"),
                "state": peer.get("peer-state", "N/A"),
                "elapsed_time": peer.get("elapsed-time", "N/A"),
                "accepted_prefixes": accepted,
                "received_prefixes": received,
                "advertised_prefixes": advertised,
                "active_prefixes": active,
                "suppressed_prefixes": suppressed,
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
