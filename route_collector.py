from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease

def get_bgp_peers_summary(dev):
    """
    Retrieves full BGP summary, neighbor info, and route table (RIB) name per peer.
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

            # Prefix counts + RIB table name
            active = accepted = suppressed = received = advertised = rib_table = "N/A"
            bgp_rib = peer.get("bgp-rib")
            if bgp_rib:
                if isinstance(bgp_rib, list):
                    bgp_rib = bgp_rib[0]
                active = bgp_rib.get("active-prefix-count", "N/A")
                accepted = bgp_rib.get("accepted-prefix-count", "N/A")
                suppressed = bgp_rib.get("suppressed-prefix-count", "N/A")
                received = bgp_rib.get("received-prefix-count", "N/A")
                advertised = bgp_rib.get("advertised-prefix-count", "N/A")
                rib_table = bgp_rib.get("name", "N/A")

            # Neighbor RPC
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

            peer_summary = {
                "peer_ip": peer_ip,
                "peer_as": peer_as,
                "state": state,
                "elapsed_time": elapsed,
                "peer_type": peer_type,
                "peer_group": peer_group,
                "peer_rti": peer_rti,
                "local_as": local_as,
                "local_address": local_addr,
                "rib_table": rib_table,
                "received_prefixes": received,
                "accepted_prefixes": accepted,
                "advertised_prefixes": advertised,
                "active_prefixes": active,
                "suppressed_prefixes": suppressed,
            }

            peers.append(peer_summary)

        print(f"✅ Parsed {len(peers)} BGP peers (summary + neighbor info + RIB).")
        return peers

    except RpcError as e:
        print(f"[!] RPC Error: {e}")
        return []
    except Exception as e:
        print(f"[!] Error while retrieving BGP summary: {e}")
        return []
