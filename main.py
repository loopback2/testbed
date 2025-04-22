from device_handler import load_device_from_yaml, connect_to_device
from route_collector import get_bgp_peers_summary
from output_formatter import print_peer_summary
from logger import setup_logger

logger = setup_logger()

def main():
    logger.info("🔧 Loading device inventory...")
    device_info = load_device_from_yaml("inventory.yml")

    logger.info(f"🔌 Connecting to {device_info['host']}...")
    dev = connect_to_device(device_info)
    if not dev:
        logger.error(f"❌ Failed to connect to {device_info['host']}")
        return

    logger.info(f"📡 Connected to {device_info['host']}, gathering BGP peers...")
    peer_data = get_bgp_peers_summary(dev, logger)

    if peer_data:
        logger.info(f"✅ Found {len(peer_data)} BGP peers.")
        print_peer_summary(device_info["host"], peer_data)
    else:
        logger.warning("⚠️ No BGP peer data returned or parsing failed.")

    dev.close()
    logger.info("🔒 Device session closed.")
