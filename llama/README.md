# Local LLM Manager

This tool streamlines the configuration of `llama-server` by providing an interactive interface to set common parameters like model path, context size, and GPU layers. It helps you quickly generate complex command-line arguments by providing default values.

## Prerequisites
-   Python 3

## Usage

To make this tool easy to run from anywhere, add the following alias to your shell configuration (e.g., `~/.zshrc` or `~/.bashrc`):

```bash
alias llama='/path/to/llama/main.py'
```

1. Now you can simply type `llama` in your terminal to start the builder. 
2. The tool will automatically look for your models in the directory provided in the `config` (it will ask you to configure the path on first run).
3. Follow the interactive prompts to configure your server parameters.
4. Choose to execute the command or copy the generated string.
