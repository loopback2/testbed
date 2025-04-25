def get_bgp_peers_summary(dev):
    """
    Gathers BGP peer data using both summary and neighbor RPCs.
    Properly preserves prefix data from each source.
    """
    peers = []

    try:
        # --- Step 1: Run summary RPC ---
        summary_rpc = dev.rpc.get_bgp_summary_information()
        summary_xml = etree.tostring(summary_rpc, pretty_print=True, encoding="unicode")
        summary_data = jxmlease.parse(summary_xml)
        summary_peers = summary_data.get("bgp-information", {}).get("bgp-peer", [])

        if not isinstance(summary_peers, list):
            summary_peers = [summary_peers]

        for summary_peer in summary_peers:
            peer_ip = summary_peer.get("peer-address", "N/A")

            peer_info = {
                "peer_ip": peer_ip,
                "peer_as": summary_peer.get("peer-as", "N/A"),
                "state": summary_peer.get("peer-state", "N/A"),
                "elapsed_time": summary_peer.get("elapsed-time", "N/A"),
                "received_prefixes": summary_peer.get("received-prefix-count", "N/A"),
                "accepted_prefixes": summary_peer.get("accepted-prefix-count", "N/A"),
                "active_prefixes": summary_peer.get("active-prefix-count", "N/A"),
                "suppressed_prefixes": summary_peer.get("suppressed-prefix-count", "N/A"),
                "advertised_prefixes": "N/A",  # Will fill in below
                "rib_table": "N/A",
                "local_address": "N/A",
                "local_as": "N/A",
                "peer_group": "N/A",
                "peer_rti": "N/A",
                "peer_type": "N/A",
            }

            # --- Step 2: Get neighbor info ---
            try:
                neighbor_rpc = dev.rpc.get_bgp_neighbor_information(neighbor_address=peer_ip)
                neighbor_xml = etree.tostring(neighbor_rpc, pretty_print=True, encoding="unicode")
                neighbor_data = jxmlease.parse(neighbor_xml)
                bgp_peer_info = neighbor_data.get("bgp-information", {}).get("bgp-peer", {})

                if isinstance(bgp_peer_info, dict):
                    rib = bgp_peer_info.get("bgp-rib", {})
                    if isinstance(rib, dict):
                        peer_info["rib_table"] = rib.get("name", "N/A")
                        peer_info["advertised_prefixes"] = rib.get("advertised-prefix-count", "N/A")

                    # Other metadata
                    peer_info["local_address"] = bgp_peer_info.get("local-address", "N/A")
                    peer_info["local_as"] = bgp_peer_info.get("local-as", "N/A")
                    peer_info["peer_group"] = bgp_peer_info.get("peer-group", "N/A")
                    peer_info["peer_rti"] = bgp_peer_info.get("peer-cfg-rti", "N/A")
                    peer_info["peer_type"] = bgp_peer_info.get("peer-type", "N/A")

            except Exception as e:
                print(f"[!] Failed to fetch neighbor info for {peer_ip}: {e}")

            peers.append(peer_info)

        print(f"✅ Parsed {len(peers)} BGP peers (summary + neighbor info).")
        return peers

    except Exception as e:
        print(f"[!] Error during BGP summary collection: {e}")
        return []
