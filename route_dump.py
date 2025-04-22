from jnpr.junos.exception import RpcError
from lxml import etree
import jxmlease
from datetime import datetime


def collect_received_routes(dev, peer_ip, rib):
    try:
        print(f"\n[+] Collecting received routes for {peer_ip} in table {rib}...")
        rpc = dev.rpc.get_route_information(
            table=rib,
            receive_protocol_name="bgp",
            peer=peer_ip
        )
        xml_str = etree.tostring(rpc, encoding="unicode")
        parsed = jxmlease.parse(xml_str)

        routes = []
        for rt in parsed.get("route-information", {}).get("route-table", []):
            if rt.get("table-name") != rib:
                continue
            for route in rt.get("rt", []):
                dest = route.get("rt-destination", "N/A")
                nhop = "N/A"
                nh = route.get("rt-entry", {}).get("nh")
                if nh:
                    nhop = nh.get("to", "N/A")
                routes.append(f"- {dest}, Next hop: {nhop}")

        return routes

    except RpcError as e:
        return [f"[!] Failed to get received routes for {peer_ip}: {str(e)}"]


def collect_advertised_routes(dev, peer_ip, rib):
    try:
        print(f"\n[+] Collecting advertised routes for {peer_ip} in table {rib}...")
        rpc = dev.rpc.get_route_information(
            table=rib,
            advertising_protocol_name="bgp",
            neighbor=peer_ip
        )
        xml_str = etree.tostring(rpc, encoding="unicode")
        parsed = jxmlease.parse(xml_str)

        routes = []
        for rt in parsed.get("route-information", {}).get("route-table", []):
            if rt.get("table-name") != rib:
                continue
            for route in rt.get("rt", []):
                dest = route.get("rt-destination", "N/A")
                nhop = "N/A"
                nh = route.get("rt-entry", {}).get("nh")
                if nh:
                    nhop = nh.get("to", "N/A")
                routes.append(f"- {dest}, Next hop: {nhop}")

        return routes

    except RpcError as e:
        return [f"[!] Failed to get advertised routes for {peer_ip}: {str(e)}"]
