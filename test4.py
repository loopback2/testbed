import subprocess
import ipaddress
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Logging setup
logging.basicConfig(filename="ssh_open_devices.log", level=logging.INFO, format="%(asctime)s - %(message)s")


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


def run_nmap_scan(ip):
    """Runs an Nmap scan on the given IP to check if port 22 is open."""
    try:
        result = subprocess.run(["nmap", ip, "-p", "22", "-Pn"], capture_output=True, text=True, timeout=5)
        output = result.stdout

        # Use regex to match "22/tcp open ssh" exactly
        match = re.search(r"22\/tcp\s+open\s+ssh", output)

        if match:
            logging.info(f"{ip} - SSH port is open")
            print(f"✅ {ip} - SSH port is open")
            return ip  # Return IPs where SSH is open
        else:
            print(f"❌ {ip} - SSH not available")
            return None

    except subprocess.TimeoutExpired:
        print(f"⚠️ {ip} - Nmap scan timed out")
        return None
    except Exception as e:
        print(f"⚠️ {ip} - Error occurred: {e}")
        return None


def process_devices(ip_list, max_workers=10):
    """Scans multiple devices concurrently using Nmap and logs only those with open SSH ports."""
    ssh_open_devices = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(run_nmap_scan, ip): ip for ip in ip_list}

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                if result:
                    ssh_open_devices.append(result)
            except Exception as e:
                logging.info(f"{ip} - Error occurred: {e}")

    print(f"\n✅ Total devices with SSH open: {len(ssh_open_devices)}")
    return ssh_open_devices


# Main execution
if __name__ == "__main__":
    ip_input = input("Enter IP range or subnet (e.g., '192.168.0.0/24' or '192.168.0.1 - 192.168.0.254'): ")
    ip_list = generate_ip_list(ip_input)
    ssh_open_devices = process_devices(ip_list, max_workers=10)  # Adjust workers as needed