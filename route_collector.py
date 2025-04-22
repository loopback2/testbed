import jxmlease
from jnpr.junos.exception import RpcError

def get_bgp_peers_summary(dev, logger):
    try:
        response = dev.rpc.get_bgp_summary_information()
        xml_str = str(response)

        if "<rpc-reply" not in xml_str:
            logger.error("❌ RPC response is not valid XML.")
            return []

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

        return peers

    except RpcError as e:
        logger.error(f"❌ RPC Error: {e}")
        return []
    except Exception as e:
        logger.exception(f"❌ Unexpected error during BGP peer parsing: {e}")
        return []
