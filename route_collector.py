from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease

def get_bgp_peers_summary(dev):
    """
    Retrieve basic BGP summary info using RPC and parse with jxmlease.
    Only extracts core fields from <get-bgp-summary-information/>.
    """
    try:
        print("📡 Sending <get-bgp-summary-information/> RPC...")
        rpc = dev.rpc.get_bgp_summary_information()
        rpc_xml = etree.tostring(rpc, pretty_print=True, encoding="unicode")

        result = jxmlease.parse(rpc_xml)
        bgp_peers = result.get("bgp-information", {}).get("bgp-peer", [])

        if not isinstance(bgp_peers, list):
            bgp_peers = [bgp_peers]

        peers = []
        for peer in bgp_peers:
            peer_summary = {
                "peer_ip": peer.get("peer-address", "N/A"),
                "peer_as": peer.get("peer-as", "N/A"),
                "state": peer.get("peer-state", "N/A"),
                "active_prefixes": peer.get("active-prefix-count", "N/A"),
                "accepted_prefixes": peer.get("accepted-prefix-count", "N/A"),
                "suppressed_prefixes": peer.get("suppressed-prefix-count", "N/A"),
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
