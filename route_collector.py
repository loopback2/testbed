import jxmlease
from jnpr.junos.exception import RpcError

def get_bgp_peers_summary(dev):
    """
    Get BGP summary info from the device using RPC and return a list of peer dictionaries.
    Includes debug output to inspect raw RPC response and troubleshoot malformed XML.
    """
    try:
        print("📡 Sending <get-bgp-summary-information/> RPC...")
        response = dev.rpc.get_bgp_summary_information()

        # Convert to string and preview the response
        xml_str = str(response)
        print("\n🧪 RAW RPC RESPONSE (first 500 chars):")
        print(xml_str[:500])

        # Save raw XML to file for deeper inspection
        with open("raw_bgp_summary.xml", "w") as f:
            f.write(xml_str)

        print("📄 Parsing XML with jxmlease...")
        parser = jxmlease.Parser()
        data = parser(xml_str)

        # Print top-level keys to verify structure
        print(f"🧪 Top-level keys: {list(data.keys())}")

        bgp_info = data.get("bgp-information")
        print("🧪 Raw 'bgp-information':")
        print(bgp_info)

        if not bgp_info:
            print("⚠️ 'bgp-information' block not found in parsed data.")
            return []

        peers_raw = bgp_info.get("bgp-peer")
        print("🧪 Raw 'bgp-peer':")
        print(peers_raw)

        if not peers_raw:
            print("⚠️ 'bgp-peer' block not found.")
            return []

        if not isinstance(peers_raw, list):
            peers_raw = [peers_raw]

        peers = []
        for peer in peers_raw:
            peer_dict = {
                "peer_ip": peer.get("peer-address"),
                "group": peer.get("peer-group"),
                "peer_as": peer.get("peer-as"),
                "instance": peer.get("bgp-rib", {}).get("@name") if "bgp-rib" in peer else None,
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
        print(f"[!] Failed to parse XML: {e}")
        return []
