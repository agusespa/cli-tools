# Local LLM Manager

This tool streamlines the configuration of `llama-server` by providing an interactive interface to set common parameters like model path, context size, and GPU layers. It helps you quickly generate complex command-line arguments by providing default values.

## Prerequisites
- Python 3.10+ (no additional dependencies required!)
- `llama-server` binary (the tool can help you install it via Homebrew on macOS)

## Setup
Add an alias to your shell configuration (e.g., `~/.zshrc` or `~/.bashrc`):

```bash
alias llama='/path/to/llama/main.py'
```

Ensure the file has executable permissions (`chmod +x /path/to/llama/main.py`).
Then reload your shell or run `source ~/.zshrc`

## Usage
1. Run `llama` in your terminal to start the builder
2. On first run, you'll be prompted to configure your models directory
3. Select your model from the list by entering its number
4. Configure server parameters through the prompts
5. Optionally enable LAN access to allow connections from other devices on your network
6. The tool will generate and optionally execute the `llama-server` command