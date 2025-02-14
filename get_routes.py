from netmiko import ConnectHandler
import getpass
import os

def get_juniper_routes():
    device = {
        'device_type': 'juniper',
        'host': input("Enter device IP: "),
        'username': input("Enter username: "),
        'password': getpass.getpass("Enter password: "),
    }
    
    # Ask user which command to run
    command_type = input("Enter 'advertised' for advertised routes or 'received' for received routes: ").strip().lower()
    
    if command_type not in ['advertised', 'received']:
        print("Invalid choice. Exiting.")
        return
    
    peer_ip = input("Enter BGP peer IP: ")
    route_table = input("Enter route table name: ")
    
    if command_type == 'advertised':
        command = f"show route advertised-protocol bgp {peer_ip} table {route_table}"
    else:
        command = f"show route receive-protocol bgp {peer_ip} table {route_table}"
    
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_command(command)
            
            # Define output file name
            filename = f"bgp_routes_{command_type}_{peer_ip}_{route_table.replace('.', '_')}.txt"
            
            # Save to file
            with open(filename, 'w') as file:
                file.write(output)
            
            print(f"Output saved to {filename}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_juniper_routes()
