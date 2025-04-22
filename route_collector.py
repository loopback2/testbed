from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease

def get_bgp_peers_summary(dev):
    """
    Retrieves BGP peer summary data including prefix counts and elapsed time.
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
            # Defaults
            active = accepted = suppressed = received = elapsed = "N/A"

            # Prefix stats
            bgp_rib = peer.get("bgp-rib")
            if bgp_rib:
                if isinstance(bgp_rib, list):
                    bgp_rib = bgp_rib[0]
                active = bgp_rib.get("active-prefix-count", "N/A")
                accepted = bgp_rib.get("accepted-prefix-count", "N/A")
                suppressed = bgp_rib.get("suppressed-prefix-count", "N/A")
                received = bgp_rib.get("received-prefix-count", "N/A")

            # Elapsed time
            elapsed = peer.get("elapsed-time", "N/A")

            peer_summary = {
                "peer_ip": peer.get("peer-address", "N/A"),
                "peer_as": peer.get("peer-as", "N/A"),
                "state": peer.get("peer-state", "N/A"),
                "elapsed_time": elapsed,
                "active_prefixes": active,
                "accepted_prefixes": accepted,
                "suppressed_prefixes": suppressed,
                "received_prefixes": received,
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
