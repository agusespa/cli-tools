import os


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")

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
    print("\n" + "="*40)
    print("Output: No GGUF models found.")
    print("It looks like this is your first time running this tool (or no models were found).")
    print("="*40)
    
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

    # Save to config
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

def prompt_model_selection(default_model):
    """
    Lists available .gguf models and prompts user to select one.
    """
    gguf_files = get_gguf_files()
    
    if not gguf_files:
        # Try to setup config if no files found
        new_dir = prompt_for_config_setup()
        if new_dir:
            # Retry fetching files
             gguf_files = get_gguf_files()

    if not gguf_files:
        # Fallback to manual entry
        return prompt_value(
            "Model Path (-m)", 
            default_model, 
            description="Path to the GGUF model file"
        )

    print("\n" + "="*40)
    print("Available Models:")
    for i, f in enumerate(gguf_files):
        print(f"{i+1}) {os.path.basename(f)}")
    print("="*40)

    print("\n# Select a model by number, or enter a custom path.")
    prompt_text = f"Model Path (-m) [{default_model}]: "
    
    while True:
        user_input = input(prompt_text).strip()
        
        if user_input == "":
             return default_model
        
        # Check if user entered a number
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(gguf_files):
                return gguf_files[idx]
            else:
                print("Invalid selection number.")
                continue
        
        # Assume custom path
        return user_input
