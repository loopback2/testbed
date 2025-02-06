import paramiko
import getpass
import logging
import os
import subprocess
import ipaddress
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

# Logging setup
logging.basicConfig(filename="non_juniper_devices.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def generate_ip_list(ip_input):
    """Generates a list of IP addresses from either an IP range or a subnet."""
    ip_list = []
    try:
        if "/" in ip_input:  # Subnet notation
            network = ipaddress.IPv4Network(ip_input, strict=False)
            ip_list = [str(ip) for ip in network.hosts()]  # Excludes network & broadcast addresses
        elif "-" in ip_input:  # IP range notation
            start_ip, end_ip = map(str.strip, ip_input.split("-"))
            start = ipaddress.IPv4Address(start_ip)
            end = ipaddress.IPv4Address(end_ip)
            if start > end:
                raise ValueError("Start IP must be less than or equal to End IP")
            ip_list = [str(ipaddress.IPv4Address(ip)) for ip in range(int(start), int(end) + 1)]
        else:
            raise ValueError("Invalid input format. Use '192.168.0.0/24' or '192.168.0.1 - 192.168.0.254'.")
    except ValueError as e:
        print(f"Error: {e}")
        return []
    return ip_list

def check_ssh_availability(ip, username, password, timeout=2):
    """Quickly checks if SSH is open and authentication works before running any commands."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=username, password=password, timeout=timeout)
        ssh.close()
        return True
    except paramiko.AuthenticationException:
        logging.info(f"{ip} - Authentication failed, skipping.")
        print(f"❌ {ip} - Authentication failed. Skipping...")
        return False
    except (paramiko.SSHException, paramiko.ChannelException):
        return False
    except Exception:
        return False

def get_juniper_device_info(ip, username, password, timeout=3):
    """Retrieves Juniper device details (hostname, model, version)."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=username, password=password, timeout=timeout)
        stdin, stdout, stderr = ssh.exec_command("show version | no-more", timeout=3)
        output = stdout.read().decode().strip()
        ssh.close()
        if "Juniper Networks" in output or "JUNOS" in output:
            hostname, model, version = "Unknown", "Unknown", "Unknown"
            for line in output.split("\n"):
                if "Hostname:" in line:
                    hostname = line.split(":")[1].strip()
                if "Model:" in line:
                    model = line.split(":")[1].strip()
                if "JUNOS Software Release" in line:
                    version = line.split("[")[1].split("]")[0].strip() if "[" in line else line.split(":")[1].strip()
            return {"host": ip, "hostname": hostname, "model": model, "version": version}
        else:
            logging.info(f"{ip} - Non-Juniper device detected.")
            return None
    except Exception:
        logging.info(f"{ip} - Unreachable or SSH failed.")
        return None

def process_device(ip, username, password):
    """Processes a single device: Checks SSH, then fetches Juniper details if valid."""
    if not check_ssh_availability(ip, username, password):
        return None
    return get_juniper_device_info(ip, username, password)

def process_devices(ip_list, username, password, max_workers=10):
    """Iterates through devices using concurrency, safely handling multiple SSH sessions."""
    inventory = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(process_device, ip, username, password): ip for ip in ip_list}
        
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                device_info = future.result()
                if device_info:
                    site_name = "Site-1"
                    if site_name not in inventory:
                        inventory[site_name] = {"hosts": []}
                    inventory[site_name]["hosts"].append(device_info)
            except Exception as e:
                logging.info(f"{ip} - Error occurred: {e}")

    print(f"\n✅ Found {len(inventory.get('Site-1', {}).get('hosts', []))} Juniper devices.")
    return inventory

def save_to_yaml(inventory, filename="device_inventory.yml"):
    """Saves the Juniper device inventory to a YAML file."""
    with open(filename, "w") as file:
        yaml.dump(inventory, file, default_flow_style=False)
    print(f"📄 Inventory saved to {filename}")

# Main execution
if __name__ == "__main__":
    ip_input = input("Enter IP range or subnet (e.g., '192.168.0.0/24' or '192.168.0.1 - 192.168.0.254'): ")
    username = input("Enter SSH username: ")
    password = getpass.getpass("Enter SSH password: ")  # Secure password input

    ip_list = generate_ip_list(ip_input)
    inventory = process_devices(ip_list, username, password, max_workers=10)  # Adjust worker count if needed
    save_to_yaml(inventory)
