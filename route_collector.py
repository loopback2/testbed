from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease

def get_bgp_peers_summary(dev):
    """
    Run <get-bgp-summary-information/> RPC, flatten XML, and parse using jxmlease.
    Returns a list of structured peer summaries.
    """
    try:
        print("📡 Sending <get-bgp-summary-information/> RPC...")
        rpc = dev.rpc.get_bgp_summary_information()
        rpc_xml = etree.tostring(rpc, pretty_print=True, encoding="unicode")

        # Debug: print first few characters
        print("\n🧪 Flattened XML (start):")
        print(rpc_xml[:500])

        # Parse with jxmlease
        result = jxmlease.parse(rpc_xml)

        # Dive into result
        bgp_peers = result.get("bgp-information", {}).get("bgp-peer", [])
        if not isinstance(bgp_peers, list):
            bgp_peers = [bgp_peers]

        peers = []
        for peer in bgp_peers:
            peer_dict = {
                "peer_ip": peer.get("peer-address", "N/A"),
                "group": peer.get("peer-group", "N/A"),
                "peer_as": peer.get("peer-as", "N/A"),
                "instance": peer.get("bgp-rib", {}).get("@name") if "bgp-rib" in peer else "N/A",
                "type": peer.get("peer-type", "N/A"),
                "state": peer.get("peer-state", "N/A"),
                "active_prefixes": peer.get("active-prefix-count", "N/A"),
                "received_prefixes": peer.get("received-prefix-count", "N/A"),
                "accepted_prefixes": peer.get("accepted-prefix-count", "N/A"),
                "advertised_prefixes": peer.get("advertised-prefix-count", "N/A"),
            }
            peers.append(peer_dict)

        print(f"✅ Parsed {len(peers)} BGP peers.")
        return peers

    except RpcError as e:
        print(f"[!] RPC Error: {e}")
        return []
    except Exception as e:
        print(f"[!] Unexpected error while parsing BGP summary: {e}")
        return []
