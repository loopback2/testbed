import os
from datetime import datetime


def get_timestamp():
    """Returns a formatted timestamp."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def log_to_file(filename, content):
    """Appends content to the specified log file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a") as f:
        f.write(content + "\n")


def create_phase_log_file(device_name, phase):
    """Generates a log file path using device name, phase, and timestamp."""
    timestamp = get_timestamp()
    safe_name = device_name.replace(" ", "_")
    filename = f"logs/{safe_name}-{phase}-{timestamp}.log"
    return filename