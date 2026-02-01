import os
import shutil
import socket
import subprocess
import sys

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")

def get_total_system_memory():
    """
    Returns total system memory in bytes.
    On Mac, uses sysctl. On others, returns None.
    """
    if sys.platform == "darwin":
        try:
            return int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip())
        except (subprocess.CalledProcessError, ValueError):
            return None
    # TODO Add Linux suport
    return None

def get_advanced_memory_stats():
    """
    Returns a dict with 'wired', 'active', 'compressed' memory in bytes.
    Refines available memory estimation.
    """
    stats = {}
    if sys.platform == "darwin":
        try:
            output = subprocess.check_output(["vm_stat"]).decode("utf-8")
            lines = output.strip().split("\n")
            page_size = 4096 # fallback
            # First line usually: Mach Virtual Memory Statistics: (page size of 16384 bytes)
            if "page size of" in lines[0]:
                try:
                    page_size = int(lines[0].split("page size of")[1].split("bytes")[0].strip())
                except:
                    pass
            
            for line in lines[1:]:
                parts = line.split(":")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    val = parts[1].strip().replace(".", "")
                    if key == "Pages wired down":
                        stats["wired"] = int(val) * page_size
                    elif key == "Pages active":
                        stats["active"] = int(val) * page_size
                    elif key == "Pages occupied by compressor":
                        stats["compressed"] = int(val) * page_size
        except Exception:
            pass
    return stats

def format_bytes(size):
    """
    Returns a human-readable string for file size.
    """
    power = 1024
    n = size
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    curr = 0
    while n > power and curr < 4:
        n /= power
        curr += 1
    return f"{n:.2f}{power_labels[curr]}B"

def get_local_ip():
    """
    Returns the local IP address of this machine on the LAN.
    Returns None if unable to determine.
    """
    try:
        # Create a socket and connect to an external address (doesn't actually send data)
        # This helps us determine which network interface would be used
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None

def is_port_in_use(port):
    """
    Checks if a TCP port is currently in use.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', int(port))) == 0

def check_command_exists(cmd):
    """
    Checks if a command exists in the system PATH.
    """
    return shutil.which(cmd) is not None

def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception:
            pass
    return config

def get_model_dir():
    config = load_config()
    return config.get("model_dir")

def get_gguf_files():
    """
    Returns a list of .gguf files.
    Checks only the configured directory.
    If no models found, returns None/empty.
    """
    files = []
    
    model_dir = get_model_dir()
    if model_dir:
        expanded_dir = os.path.expanduser(model_dir)
        if os.path.isdir(expanded_dir):
            files = [os.path.join(expanded_dir, f) for f in os.listdir(expanded_dir) if f.endswith(".gguf")]
            if files:
                return sorted(files)
             
    return []

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")

def prompt_for_config_setup():
    """
    Prompts user to set up the model directory config.
    Returns the path they enter (or None).
    """
    print("\nNo GGUF models found.")
    print("It looks like this is your first time running this tool (or no models were found).")
    
    user_input = ""
    while not user_input:
        user_input = input(f"\nEnter the path to your .gguf models directory: ").strip()
        if not user_input:
            print("Path cannot be empty. Please enter a valid path.")
            
    path = user_input
        
    expanded_path = os.path.expanduser(path)
    if not os.path.isdir(expanded_path):
        print(f"\nWarning: '{expanded_path}' does not exist or is not a directory.")
        create = input("Create it? (y/n) [n]: ").strip().lower()
        if create in ["y", "yes"]:
            try:
                os.makedirs(expanded_path)
                print(f"Created {expanded_path}")
            except OSError as e:
                print(f"Error creating directory: {e}")
                return None
        else:
            return None

    save_config({"model_dir": path})
    print(f"Configuration saved to {CONFIG_FILE}")
    return path


def prompt_value(param_name, default_value, description=None):
    """
    Prompts the user for a value, showing the default.
    Returns the user input or the default if input is empty.
    """
    prompt_text = f"{param_name} [{default_value}]: "
    if description:
        print(f"\n# {description}")
    
    user_input = input(prompt_text).strip()
    if user_input == "":
        return default_value
    return user_input

def prompt_bool(param_name, default_value, description=None):
    """
    Prompts for a boolean value (y/n).
    """
    if description:
        print(f"\n# {description}")

    default_str = "y" if default_value else "n"
    prompt_text = f"{param_name} (y/n) [{default_str}]: "
    
    while True:
        user_input = input(prompt_text).strip().lower()
        if user_input == "":
            return default_value
        if user_input in ["y", "yes"]:
            return True
        if user_input in ["n", "no"]:
            return False
        print("Please enter 'y' or 'n'.")

def prompt_model_selection(ram_info=None):
    """
    Lists available .gguf models and prompts user to select one by number.
    Only allows selection from configured model directory.
    """
    gguf_files = get_gguf_files()
    
    if not gguf_files:
        # Try to setup config if no files found
        new_dir = prompt_for_config_setup()
        if new_dir:
            # Retry fetching files
            gguf_files = get_gguf_files()

    if not gguf_files:
        print("\n[ERROR] No .gguf models found in the configured directory.")
        print("Please add models to your configured directory and try again.")
        sys.exit(1)

    print("\nAvailable Models:")
    
    # Display numbered list
    for i, f in enumerate(gguf_files):
        size = os.path.getsize(f)
        print(f"{i+1}) {os.path.basename(f)} ({format_bytes(size)})")
    
    print("-"*40)
    if ram_info:
        print(ram_info)
        
    # Prompt for selection
    while True:
        user_input = input("\nSelect a model by number: ").strip()
        
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(gguf_files):
                selected_model = gguf_files[idx]
                print(f"Selected: {os.path.basename(selected_model)}")
                return selected_model
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(gguf_files)}.")
        else:
            print("Please enter a valid number.")
