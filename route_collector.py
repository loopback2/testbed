from jnpr.junos.exception import RpcError
from jnpr.junos.utils.config import Config
from jnpr.junos import Device
import jxmlease

def get_bgp_peers_summary(dev: Device):
    try:
        response = dev.rpc.get_bgp_summary_information()
        parser = jxmlease.Parser()
        data = parser(str(response))

        peers = []

        summary_info = data.get("bgp-information", {}).get("bgp-peer", [])
        if not isinstance(summary_info, list):
            summary_info = [summary_info]

        for peer in summary_info:
            peer_dict = {
                "peer_ip": peer.get("peer-address"),
                "group": peer.get("peer-group"),
                "peer_as": peer.get("peer-as"),
                "instance": peer.get("bgp-rib", {}).get("@name"),  # VRF
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
        print(f"[!] RPC Error collecting BGP summary: {e}")
        return []
