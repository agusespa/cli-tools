import subprocess
from utils import check_command_exists, prompt_bool, Spinner


def check_and_install_llama() -> bool:
    """Check for llama-server, offer to install or update via Homebrew.
    Returns True if we should continue, False if the user chose to abort."""
    with Spinner("Checking llama.cpp installation..."):
        has_binary = check_command_exists("llama-server")
        has_brew = check_command_exists("brew")

    if not has_binary:
        print("\n[WARNING] 'llama-server' not found in PATH.")
        if has_brew:
            if prompt_bool("Install llama.cpp via Homebrew?", True):
                print("Running: brew install llama.cpp")
                result = subprocess.run(["brew", "install", "llama.cpp"])
                if result.returncode != 0:
                    print("\n[ERROR] Homebrew install failed.")
                    return prompt_bool("Continue anyway?", False)
                print("\n[OK] llama.cpp installed successfully.")
            else:
                print("\n[NOTE] If you continue, the CLI will only generate the command")
                print("but it won't be able to run the server.")
                return prompt_bool("Continue anyway?", False)
        else:
            print("Homebrew not found. Install llama.cpp manually")
            print("\n[NOTE] If you continue, the CLI will only generate the command")
            print("but it won't be able to run the server.")
            return prompt_bool("Continue anyway?", False)
    else:
        # Binary found — optionally check for updates
        if has_brew:
            try:
                with Spinner("Checking for llama.cpp updates..."):
                    result = subprocess.run(
                        ["brew", "outdated", "llama.cpp"],
                        capture_output=True,
                        text=True,
                    )
                is_outdated = "llama.cpp" in result.stdout
            except Exception:
                is_outdated = False

            if is_outdated:
                print("\n[INFO] A newer version of llama.cpp is available via Homebrew.")
                if prompt_bool("Update now?", False):
                    print("Running: brew upgrade llama.cpp")
                    subprocess.run(["brew", "upgrade", "llama.cpp"])

    return True
