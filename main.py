from device_handler import load_device_from_yaml, connect_to_device

def main():
    print("📁 Loading YAML...")

    try:
        device = load_device_from_yaml("inventory.yml")
        print(f"📡 Loaded device: {device['host']} with username: {device['username']}")
    except Exception as e:
        print(f"[!] Failed to load YAML or missing keys: {e}")
        return

    print("🔌 Attempting connection to device...")
    dev = connect_to_device(device)

    if dev:
        print("[+] Connection successful!")
        dev.close()
        print("🔒 Connection closed.")
    else:
        print("[!] Connection failed.")

if __name__ == "__main__":
    main()
