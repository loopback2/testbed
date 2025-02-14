import time
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
import subprocess
import ipaddress
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Logging setup
logging.basicConfig(filename="device_identification.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# SSH Credentials
SSH_USERNAME = "admin"
SSH_PASSWORD = "password"

# Device classification
juniper_devices = []
palo_alto_devices = []
aruba_devices = []
failed_auth_devices = []
ssh_not_available_count = 0  # Count of devices where SSH is not available


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
    global ssh_not_available_count
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
            ssh_not_available_count += 1
            return None

    except subprocess.TimeoutExpired:
        ssh_not_available_count += 1
        return None
    except Exception as e:
        ssh_not_available_count += 1
        return None


def ssh_identify_device(ip):
    """Uses Netmiko to SSH into a device and determine if it's Juniper, Palo Alto, or Aruba."""
    device_params = {
        "device_type": "autodetect",
        "host": ip,
        "username": SSH_USERNAME,
        "password": SSH_PASSWORD,
        "timeout": 15,
        "global_delay_factor": 2,  # Increases wait time for CLI readiness
    }

    try:
        print(f"🟢 {ip} - Connecting via SSH...")
        net_connect = ConnectHandler(**device_params)
        print(f"✅ {ip} - Connected successfully!")

        # **Explicit Delay to Ensure CLI is Fully Loaded**
        time.sleep(5)

        # **Wait for CLI Readiness**
        max_wait_time = 15
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            prompt = net_connect.find_prompt()
            if "#" in prompt or ">" in prompt or "PA-VM" in prompt or "admin@" in prompt:
                print(f"✅ {ip} - CLI Ready!")
                break
            time.sleep(1)

        # Run Juniper Identification: "show version"
        output = net_connect.send_command("show version", read_timeout=10)
        if "JUNOS" in output or "Junos" in output:
            juniper_devices.append(ip)
            print(f"🔍 {ip} - Identified as **Juniper**")
            logging.info(f"{ip} - Identified as Juniper")
            net_connect.disconnect()
            return "Juniper"

        # Run Palo Alto Identification: "show system info"
        output = net_connect.send_command("show system info", read_timeout=10)
        if "sw-version" in output or "paloaltonetworks" in output:
            palo_alto_devices.append(ip)
            print(f"🔍 {ip} - Identified as **Palo Alto**")
            logging.info(f"{ip} - Identified as Palo Alto")
            net_connect.disconnect()
            return "Palo Alto"

        # Run Aruba Identification: "show version"
        output = net_connect.send_command("show version", read_timeout=10)
        if "Aruba" in output or "HP ProCurve" in output:
            aruba_devices.append(ip)
            print(f"🔍 {ip} - Identified as **Aruba**")
            logging.info(f"{ip} - Identified as Aruba")
            net_connect.disconnect()
            return "Aruba"

        # If no match, assume unknown
        net_connect.disconnect()
        return "Unknown"

    except NetmikoAuthenticationException:
        print(f"❌ {ip} - Authentication failed")
        failed_auth_devices.append(ip)
        logging.info(f"{ip} - Authentication failed")
        return "Authentication Failed"
    except NetmikoTimeoutException:
        print(f"⚠️ {ip} - Connection timed out")
        return "Timeout"
    except Exception as e:
        print(f"⚠️ {ip} - SSH OS detection failed: {e}")
        return "Unknown"
    finally:
        if "net_connect" in locals():
            net_connect.disconnect()
            print(f"🔴 {ip} - SSH session closed.")


def process_devices(ip_list, max_workers=10):
    """Scans multiple devices concurrently using Nmap and identifies OS."""
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
    print(f"❌ Total devices with SSH **not available**: {ssh_not_available_count}")

    # Identify OS for each SSH-enabled device
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(ssh_identify_device, ip): ip for ip in ssh_open_devices}

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                logging.info(f"{ip} - Identified as {result}")
            except Exception as e:
                logging.info(f"{ip} - Error occurred: {e}")

    # Display organized results
    print("\n🎯 **Identification Summary:**")
    print(f"🔹 **Juniper Devices ({len(juniper_devices)}):** {juniper_devices}")
    print(f"🔹 **Palo Alto Devices ({len(palo_alto_devices)}):** {palo_alto_devices}")
    print(f"🔹 **Aruba Devices ({len(aruba_devices)}):** {aruba_devices}")
    print(f"❌ **Failed Authentication ({len(failed_auth_devices)}):** {failed_auth_devices}")
    print(f"❌ **Total Devices with SSH Not Available**: {ssh_not_available_count}")

    return {
        "Juniper": juniper_devices,
        "Palo Alto": palo_alto_devices,
        "Aruba": aruba_devices,
        "Failed Authentication": failed_auth_devices,
        "SSH Not Available Count": ssh_not_available_count
    }


# Main execution
if __name__ == "__main__":
    ip_input = input("Enter IP range or subnet (e.g., '192.168.0.0/24' or '192.168.0.1 - 192.168.0.254'): ")
    ip_list = generate_ip_list(ip_input)
    devices = process_devices(ip_list, max_workers=10)