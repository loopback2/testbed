import os
import dotenv
from datetime import datetime
from pathlib import Path

def load_env(env_path="secrets/.env"):
    dotenv.load_dotenv(env_path)
    return {
        "primary_user": os.getenv("PRIMARY_USERNAME"),
        "primary_pass": os.getenv("PRIMARY_PASSWORD"),
        "backup_user": os.getenv("BACKUP_USERNAME"),
        "backup_pass": os.getenv("BACKUP_PASSWORD"),
    }

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M")

def create_backup_path(site, role, hostname, timestamp):
    path = Path(f"backups/{site}/{role}/{hostname}/{timestamp}")
    path.mkdir(parents=True, exist_ok=True)
    return path

def print_summary(summary):
    from rich import print
    from rich.table import Table

    table = Table(title="Backup Summary", show_lines=True)
    table.add_column("Site", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="green")
    table.add_column("IP", style="magenta")
    table.add_column("Status", style="bold")
    table.add_column("Auth Used", style="yellow")

    success_count = 0
    fail_count = 0
    fallback_used = 0

    for item in summary:
        status = "✅ SUCCESS" if item["success"] else "❌ FAILED"
        table.add_row(item["site"], item["hostname"], item["ip"], status, item["auth_used"])
        if item["success"]:
            success_count += 1
            if item["auth_used"] == "BACKUP":
                fallback_used += 1
        else:
            fail_count += 1

    print("\n")
    print(table)
    print(f"✔ Backups completed: {success_count}")
    print(f"✖ Failures: {fail_count}")
    print(f"🔁 Fallback logins used: {fallback_used}")
