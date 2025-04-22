import jxmlease
from jnpr.junos.exception import RpcError

def get_bgp_peers_summary(dev):
    """
    Get BGP summary info from the device using RPC and return a list of peer dictionaries.
    """
    try:
        print("📡 Sending <get-bgp-summary-information/> RPC...")
        response = dev.rpc.get_bgp_summary_information()
        xml_str = str(response)

        # Optional: save raw XML for troubleshooting
        with open("raw_bgp_summary.xml", "w") as f:
            f.write(xml_str)

        print("📄 Parsing XML with jxmlease...")
        parser = jxmlease.Parser()
        data = parser(xml_str)

        summary_info = data.get("bgp-information", {}).get("bgp-peer", [])
        if not isinstance(summary_info, list):
            summary_info = [summary_info]

        peers = []
        for peer in summary_info:
            peer_dict = {
                "peer_ip": peer.get("peer-address"),
                "group": peer.get("peer-group"),
                "peer_as": peer.get("peer-as"),
                "instance": peer.get("bgp-rib", {}).get("@name"),
                "type": peer.get("peer-type"),
                "state": peer.get("peer-state"),
                "active_prefixes": peer.get("active-prefix-count"),
                "received_prefixes": peer.get("received-prefix-count"),
                "accepted_prefixes": peer.get("accepted-prefix-count"),
                "advertised_prefixes": peer.get("advertised-prefix-count"),
            }
            peers.append(peer_dict)

        print(f"✅ Parsed {len(peers)} BGP peers.")
        return peers

    except RpcError as e:
        print(f"[!] RPC Error: {e}")
        return []
    except Exception as e:
        print(f"[!] General error while retrieving BGP peer summary: {e}")
        return []
