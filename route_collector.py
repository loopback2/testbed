from jnpr.junos.exception import RpcError

def get_bgp_peers_summary(dev):
    """
    Use PyEZ's native .to_dict() method to retrieve and parse BGP summary info.
    Returns a list of BGP peer dictionaries.
    """
    try:
        print("📡 Sending <get-bgp-summary-information/> RPC...")
        response = dev.rpc.get_bgp_summary_information()
        
        # Convert to Python dict using PyEZ native method
        data = response.to_dict()

        # Debug: top-level keys
        print(f"🧪 Top-level keys: {list(data.keys())}")

        bgp_info = data.get("bgp-information")
        print("🧪 bgp-information block:")
        print(bgp_info)

        if not bgp_info or "bgp-peer" not in bgp_info:
            print("⚠️ No 'bgp-peer' block found in response.")
            return []

        peers_raw = bgp_info["bgp-peer"]
        
        # If there's only one peer, convert it to a list for consistency
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
        print(f"[!] Unexpected error: {e}")
        return []
