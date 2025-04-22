from device_handler import load_device_from_yaml, connect_to_device

def main():
    device = load_device_from_yaml("inventory.yml")
    dev = connect_to_device(device)

    if dev:
        print("[+] Connection successful!")
        dev.close()
    else:
        print("[!] Connection failed.")

if __name__ == "__main__":
    main()
