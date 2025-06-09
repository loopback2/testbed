from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException
from backup_engine.utils import get_timestamp, create_backup_path

def backup_device(hostname, ip, port, credentials, site, role):
    timestamp = get_timestamp()
    tried_users = [
        ("PRIMARY", credentials["primary_user"], credentials["primary_pass"]),
        ("BACKUP", credentials["backup_user"], credentials["backup_pass"])
    ]

    for label, user, password in tried_users:
        try:
            device = {
                "device_type": "juniper",
                "ip": ip,
                "username": user,
                "password": password,
                "port": port,
                "fast_cli": False
            }

            connection = ConnectHandler(**device)
            output = connection.send_command("show configuration | display set | no-more")
            connection.disconnect()

            # Save output
            backup_path = create_backup_path(site, role, hostname, timestamp)
            file_path = backup_path / f"{hostname}_config.txt"
            with open(file_path, "w") as f:
                f.write(output)

            return {
                "site": site,
                "hostname": hostname,
                "ip": ip,
                "success": True,
                "auth_used": label
            }

        except (NetmikoAuthenticationException, NetmikoTimeoutException) as e:
            continue

    return {
        "site": site,
        "hostname": hostname,
        "ip": ip,
        "success": False,
        "auth_used": "None"
    }
