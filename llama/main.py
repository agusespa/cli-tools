#!/usr/bin/env python3
import os
import sys
from utils import prompt_bool, prompt_model_selection, prompt_value, get_model_dir


default_model = None
default_alias = None
default_ctx = "32768"
default_n_predict = "8192"
default_ngl = "99"
default_batch = "2048"
default_ubatch = "1024"
default_port = "8080"
default_np = "1"
default_fa = False
default_jinja = True

def main():
    print("Llama Command Builder")

    model = prompt_model_selection(default_model)
    
    alias = prompt_value(
        "Alias (--alias)", 
        default_alias, 
        description="A recognizable name for ease of use with agents."
    )
    
    ctx = prompt_value(
        "Context Size (-c)", 
        default_ctx, 
        description="Size of the prompt context (tokens). Higher values use more VRAM."
    )
    
    n_predict = prompt_value(
        "Predict Length (-n)", 
        default_n_predict, 
        description="Maximum number of tokens to predict/generate."
    )
    
    ngl = prompt_value(
        "GPU Layers (-ngl)", 
        default_ngl, 
        description="Number of layers to offload to GPU. 99 usually means all layers."
    )
    
    batch = prompt_value(
        "Batch Size (-b)", 
        default_batch, 
        description="Logical batch size for prompt processing."
    )
    
    ubatch = prompt_value(
        "UBatch Size (-ub)", 
        default_ubatch, 
        description="Physical batch size."
    )
    
    port = prompt_value(
        "Port (--port)", 
        default_port, 
        description="Port listener for the server."
    )

    np_slots = prompt_value(
        "Parallel Slots (-np)", 
        default_np, 
        description="Number of simultaneous requests to process."
    )
    
    flash_attn = prompt_bool(
        "Flash Attention (-fa)", 
        default_fa, 
        description="Enable Flash Attention (optimizes speed/memory, recommended for Apple Silicon)."
    )
    
    jinja = prompt_bool(
        "Enable Jinja Templates (--jinja)", 
        default_jinja, 
        description="Enable jinja2 template support for chat templates."
    )

    cmd_parts = [
        "llama-server",
        f"-m {model}",
        f"--alias {alias}",
        f"-c {ctx}",
        f"-n {n_predict}",
        f"-ngl {ngl}",
        f"-b {batch}",
        f"-ub {ubatch}",
        f"--port {port}",
        f"-np {np_slots}"
    ]

    if flash_attn:
        cmd_parts.append("-fa")

    if jinja:
        cmd_parts.append("--jinja")

    full_command = " ".join(cmd_parts)

    print("\nGenerated Command:")
    print("-" * 40)
    print(full_command)
    print("-" * 40)

    if prompt_bool("\nRun this command now?", True, description="Execute the server command immediately."):
        cwd = None
        
        model_dir = get_model_dir()
        if model_dir:
             expanded_dir = os.path.expanduser(model_dir)
             if os.path.isdir(expanded_dir):
                 cwd = expanded_dir
        
        if not cwd:
            print("\nError: Could not determine model directory from configuration.")
            print("Please ensure ~/.llama_cli_config exists and has a valid 'model_dir'.")
            return

        print(f"\nExample: Switching to directory: {cwd}")
        print("Starting server...")

        try:
            os.chdir(cwd)
            
            final_args = ["llama-server", "-m", model, "--alias", alias, "-c", ctx,
                         "-n", n_predict, "-ngl", ngl, "-b", batch, "-ub", ubatch, 
                         "--port", port, "-np", np_slots]
            
            if flash_attn:
                final_args.append("-fa")
            if jinja:
                final_args.append("--jinja")

            os.execvp("llama-server", final_args)
        except FileNotFoundError:
             print("\nError: 'llama-server' command not found in PATH.")
        except Exception as e:
             print(f"\nError executing command: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
