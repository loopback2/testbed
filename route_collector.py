from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease

def get_bgp_peers_summary(dev):
    """
    Retrieves BGP peer summary and neighbor details from two RPCs.
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
            peer_ip = peer.get("peer-address", "N/A")
            peer_as = peer.get("peer-as", "N/A")
            state = peer.get("peer-state", "N/A")
            elapsed = peer.get("elapsed-time", "N/A")

            # Defaults for nested <bgp-rib>
            active = accepted = suppressed = received = "N/A"
            bgp_rib = peer.get("bgp-rib")
            if bgp_rib:
                if isinstance(bgp_rib, list):
                    bgp_rib = bgp_rib[0]
                active = bgp_rib.get("active-prefix-count", "N/A")
                accepted = bgp_rib.get("accepted-prefix-count", "N/A")
                suppressed = bgp_rib.get("suppressed-prefix-count", "N/A")
                received = bgp_rib.get("received-prefix-count", "N/A")

            # 🔍 Additional data via get-bgp-neighbor-information
            local_addr = local_as = peer_group = peer_rti = peer_type = "N/A"
            try:
                neighbor_rpc = dev.rpc.get_bgp_neighbor_information(
                    neighbor_address=peer_ip
                )
                neighbor_xml = etree.tostring(neighbor_rpc, pretty_print=True, encoding="unicode")
                neighbor_data = jxmlease.parse(neighbor_xml)

                peer_data = neighbor_data.get("bgp-information", {}).get("bgp-peer", {})
                local_addr = peer_data.get("local-address", "N/A")
                local_as = peer_data.get("local-as", "N/A")
                peer_group = peer_data.get("peer-group", "N/A")
                peer_rti = peer_data.get("peer-cfg-rti", "N/A")
                peer_type = peer_data.get("peer-type", "N/A")

            except Exception as e:
                print(f"[!] Could not retrieve neighbor details for {peer_ip}: {e}")

            # Final peer summary
            peer_summary = {
                "peer_ip": peer_ip,
                "peer_as": peer_as,
                "state": state,
                "elapsed_time": elapsed,
                "active_prefixes": active,
                "accepted_prefixes": accepted,
                "suppressed_prefixes": suppressed,
                "received_prefixes": received,
                "local_address": local_addr,
                "local_as": local_as,
                "peer_group": peer_group,
                "peer_rti": peer_rti,
                "peer_type": peer_type,
            }

            peers.append(peer_summary)

        print(f"✅ Parsed {len(peers)} BGP peers (summary + neighbor info).")
        return peers

    except RpcError as e:
        print(f"[!] RPC Error: {e}")
        return []
    except Exception as e:
        print(f"[!] Error while retrieving BGP summary: {e}")
        return []
