import yaml
import argparse
from backup_engine import juniper
from backup_engine.utils import load_env, get_timestamp, create_backup_path, print_summary

# Load .env
secrets = load_env()

# Parse CLI arguments
parser = argparse.ArgumentParser(description="NetConfigVault - Juniper Config Backup")
parser.add_argument("--site", help="Run backups for a specific site only")
args = parser.parse_args()

# Load inventory
with open("inventory/inventory.yml") as f:
    inventory = yaml.safe_load(f)

# Track results
summary = []

# Loop through sites
for site, roles in inventory.items():
    if args.site and site.upper() != args.site.upper():
        continue

    for role, devices in roles.items():
        for device in devices:
            hostname = device["hostname"]
            ip = device["ip"]
            port = device.get("port", 22)

            print(f"🔄 Connecting to {hostname} ({ip})...")

            result = juniper.backup_device(
                hostname=hostname,
                ip=ip,
                port=port,
                credentials=secrets,
                site=site,
                role=role
            )

            summary.append(result)

# Print summary
print_summary(summary)
