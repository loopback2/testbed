device, target_version, local_image_path = load_inventory("config/inventory.yml")
remote_image_path = f"/var/tmp/{local_image_path.split('/')[-1]}"