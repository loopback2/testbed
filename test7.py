import paramiko
import os
from tqdm import tqdm

def file_exists_on_device(device_info, remote_path):
    """
    Check if a file already exists on the Juniper device.
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=device_info["ip"],
            username=device_info["username"],
            password=device_info["password"]
        )

        stdin, stdout, stderr = ssh.exec_command(f"ls {remote_path}")
        output = stdout.read().decode().strip()
        ssh.close()

        return remote_path in output  # Returns True if file is found
    except Exception as e:
        print(f"[!] Error checking file on device: {e}")
        return False

def scp_file_to_juniper(device_info, local_path, remote_path):
    """
    Transfer an upgrade image from Linux to Juniper /var/tmp using SCP.

    Args:
        device_info (dict): Device connection details.
        local_path (str): Local path to the Junos image file.
        remote_path (str): Remote destination path on Juniper.

    Returns:
        bool: True if transfer was successful, False otherwise.
    """
    try:
        if file_exists_on_device(device_info, remote_path):
            print(f"[✓] File already exists on Juniper ({remote_path}). Skipping SCP.")
            return True

        print(f"[+] Initiating SCP transfer to {device_info['name']}...")

        # Open SCP connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=device_info["ip"],
            username=device_info["username"],
            password=device_info["password"]
        )
        sftp = ssh.open_sftp()

        # Get file size for progress bar
        file_size = os.path.getsize(local_path)

        with tqdm(total=file_size, unit="B", unit_scale=True, desc="SCP Progress") as pbar:
            def progress_callback(sent, total):
                pbar.update(sent - pbar.n)

            # Perform SCP transfer
            sftp.put(local_path, remote_path, callback=progress_callback)

        sftp.close()
        ssh.close()

        # Verify that the file exists on Juniper after SCP
        if file_exists_on_device(device_info, remote_path):
            print(f"[✓] SCP transfer completed successfully. File verified on device.")
            return True
        else:
            print(f"[!] SCP transfer completed, but file verification failed!")
            return False

    except Exception as e:
        print(f"[!] SCP transfer failed: {e}")
        return False