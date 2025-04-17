import os
import paramiko
from tqdm import tqdm
from datetime import datetime


# Mapping Junos model names to image folder names
MODEL_FOLDER_MAP = {
    "QFX5120-48Y": "QFX5120-Y",
    "QFX5120-48YM-8C": "QFX5120-YM",
    "EX4300-48P": "EX4300",
    "EX4300": "EX4300",
    "EX4400-48T": "EX4400",
    "EX4400": "EX4400"
}


def log_output(device_name, phase, content):
    """
    Saves output to logs/<device>-<phase>-<timestamp>.log
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = device_name.replace(" ", "_")
    log_path = f"logs/{safe_name}-{phase}-{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "w") as f:
        f.write(content)
    print(f"[💾] Log saved to: {log_path}")


def get_image_folder_for_model(model):
    """
    Maps detected model to correct subfolder name in images directory.
    """
    return MODEL_FOLDER_MAP.get(model)


def list_images_in_folder(image_folder):
    """
    Lists available .tgz files in the given folder.
    """
    if not os.path.isdir(image_folder):
        print(f"[!] Folder not found: {image_folder}")
        return []

    return [f for f in os.listdir(image_folder) if f.endswith(".tgz")]


def prompt_user_to_select_image(images):
    """
    Displays list of images and prompts user to select one.
    """
    print("\n[📂] Available images:")
    for i, img in enumerate(images, 1):
        print(f"  {i}. {img}")

    while True:
        choice = input("\n[?] Select image number: ")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(images):
                return images[idx]
        print("[!] Invalid choice. Try again.")


def scp_image_to_device(device, model):
    """
    Transfers the selected image to /var/tmp on the target device using Paramiko + SCP.
    """
    print("\n--- Phase 2: SCP File Transfer ---")

    # Step 1: Map model to image folder
    image_root = "/home/jpando/images"
    model_folder = get_image_folder_for_model(model)
    if not model_folder:
        print(f"[✖] Unsupported model: {model}")
        return False

    full_folder_path = os.path.join(image_root, model_folder)
    available_images = list_images_in_folder(full_folder_path)
    if not available_images:
        print(f"[✖] No images found in: {full_folder_path}")
        return False

    # Step 2: Prompt user to choose image
    selected_image = prompt_user_to_select_image(available_images)
    local_image_path = os.path.join(full_folder_path, selected_image)
    remote_image_path = f"/var/tmp/{selected_image}"

    # Step 3: Begin SCP transfer using Paramiko
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=device["ip"],
            username=device["username"],
            password=device["password"],
            look_for_keys=False,
            allow_agent=False
        )

        sftp = ssh.open_sftp()

        # Check if file already exists
        try:
            sftp.stat(remote_image_path)
            print(f"[✓] File already exists on device. Skipping transfer.")
            return True
        except IOError:
            pass  # File does not exist — continue transfer

        print(f"[→] Transferring file: {selected_image} → {remote_image_path}")

        # Start upload with progress bar
        file_size = os.path.getsize(local_image_path)
        with tqdm(total=file_size, unit="B", unit_scale=True, desc="Uploading") as progress:
            with open(local_image_path, "rb") as src, sftp.open(remote_image_path, "wb") as dest:
                while True:
                    chunk = src.read(32768)
                    if not chunk:
                        break
                    dest.write(chunk)
                    progress.update(len(chunk))

        sftp.close()
        ssh.close()

        log_output(device["name"], "phase2-scp", f"Transferred: {remote_image_path}")
        print(f"[✓] File successfully transferred to: {remote_image_path}")
        return True

    except Exception as e:
        print(f"[✖] SCP transfer failed: {e}")
        return False
