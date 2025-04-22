from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease

def get_bgp_peers_summary(dev):
    """
    Retrieves basic BGP summary info from a Junos device using RPC.
    Properly extracts nested prefix data from inside <bgp-rib>.
    """
    try:
        print("📡 Sending <get-bgp-summary-information/> RPC...")
        rpc = dev.rpc.get_bgp_summary_information()
        rpc_xml = etree.tostring(rpc, pretty_print=True, encoding="unicode")

        # Parse using jxmlease
        result = jxmlease.parse(rpc_xml)
        bgp_peers = result.get("bgp-information", {}).get("bgp-peer", [])

        # Ensure it's always a list
        if not isinstance(bgp_peers, list):
            bgp_peers = [bgp_peers]

        peers = []
        for peer in bgp_peers:
            # Default values
            active = accepted = suppressed = "N/A"

            # Check if bgp-rib exists and extract prefix counts
            bgp_rib = peer.get("bgp-rib")
            if bgp_rib:
                if isinstance(bgp_rib, list):  # handle multiple ribs, just take first
                    bgp_rib = bgp_rib[0]
                active = bgp_rib.get("active-prefix-count", "N/A")
                accepted = bgp_rib.get("accepted-prefix-count", "N/A")
                suppressed = bgp_rib.get("suppressed-prefix-count", "N/A")

            peer_summary = {
                "peer_ip": peer.get("peer-address", "N/A"),
                "peer_as": peer.get("peer-as", "N/A"),
                "state": peer.get("peer-state", "N/A"),
                "active_prefixes": active,
                "accepted_prefixes": accepted,
                "suppressed_prefixes": suppressed,
            }

            peers.append(peer_summary)

        print(f"✅ Parsed {len(peers)} BGP peers.")
        return peers

    except RpcError as e:
        print(f"[!] RPC Error: {e}")
        return []
    except Exception as e:
        print(f"[!] Error while retrieving BGP summary: {e}")
        return []
