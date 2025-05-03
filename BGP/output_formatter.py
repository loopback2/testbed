def print_peer_summary(hostname, peers):
    print(f"\n==== BGP Peer Summary for {hostname} ====\n")
    for peer in peers:
        print(f"📡 Peer: {peer['peer_ip']} ({peer['instance']})")
        print(f"    Group: {peer['group']}")
        print(f"    AS: {peer['peer_as']}")
        print(f"    Type: {peer['type']}")
        print(f"    State: {peer['state']}")
        print(f"    Prefixes - Active: {peer['active_prefixes']}, "
              f"Received: {peer['received_prefixes']}, "
              f"Accepted: {peer['accepted_prefixes']}, "
              f"Advertised: {peer['advertised_prefixes']}")
        print("----------------------------------------------------")
