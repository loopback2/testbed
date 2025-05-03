import argparse
import re
from collections import defaultdict


def parse_routes(file_path):
    peer_routes = defaultdict(dict)
    current_peer = None
    in_routes = False

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()

            # Match peer line
            if line.startswith("== Peer:"):
                match = re.match(r"== Peer: (\S+) \| Table: (\S+)", line)
                if match:
                    current_peer = match.group(1)
                    in_routes = False  # reset flag

            elif line.startswith("--- RECEIVED ROUTES ---"):
                in_routes = True
                continue

            elif in_routes and current_peer:
                # actual route line
                if line.startswith("- "):
                    route_data = line[2:]
                    prefix, nh_part = route_data.split(", Next hop: ")
                    peer_routes[current_peer][prefix.strip()] = nh_part.strip()

    return peer_routes


def diff_routes(before_routes, after_routes):
    all_peers = sorted(set(before_routes.keys()) | set(after_routes.keys()))

    for peer in all_peers:
        print(f"\n=== Diff for Peer: {peer} ===")

        before = before_routes.get(peer, {})
        after = after_routes.get(peer, {})

        all_prefixes = sorted(set(before.keys()) | set(after.keys()))

        for prefix in all_prefixes:
            nh_before = before.get(prefix)
            nh_after = after.get(prefix)

            if nh_before and not nh_after:
                print(f"- {prefix} (was: {nh_before})")
            elif not nh_before and nh_after:
                print(f"+ {prefix} (new: {nh_after})")
            elif nh_before != nh_after:
                print(f"~ {prefix} (next-hop changed: {nh_before} → {nh_after})")

        print("-" * 50)


def main():
    parser = argparse.ArgumentParser(description="Diff received BGP routes between two files.")
    parser.add_argument('--before', required=True, help='Path to pre-change received routes file')
    parser.add_argument('--after', required=True, help='Path to post-change received routes file')

    args = parser.parse_args()

    before_routes = parse_routes(args.before)
    after_routes = parse_routes(args.after)

    diff_routes(before_routes, after_routes)


if __name__ == "__main__":
    main()
