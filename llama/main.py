#!/usr/bin/env python3
import os
import sys
from utils import (
    prompt_bool, prompt_model_selection, prompt_value, get_model_dir, 
    check_command_exists, get_total_system_memory, format_bytes, is_port_in_use,
    get_advanced_memory_stats
)


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
    print("=" * 40)
    print("Llama Command Builder")
    print("=" * 40)
    
    # Check for binary
    if not check_command_exists("llama-server"):
        print("\n[WARNING] 'llama-server' binary not found in PATH.")
        print("You may need to install it or ensure it's in your PATH.")
        if not prompt_bool("Continue anyway?", True):
            return

    # Calculate System RAM info
    total_ram = get_total_system_memory()
    advanced_stats = get_advanced_memory_stats()
    safe_ram_limit = None
    ram_msg = None
    
    if total_ram:
        ram_msg = f"System RAM: {format_bytes(total_ram)}"
        
        if advanced_stats:
            wired = advanced_stats.get('wired', 0)
            compressed = advanced_stats.get('compressed', 0) 
            # Estimate OS overhead roughly as Wired + Compressed + 2GB Buffer
            os_overhead = wired + compressed + (2 * 1024 * 1024 * 1024)
            safe_ram_limit = total_ram - os_overhead
            if safe_ram_limit < 0: safe_ram_limit = 0
            
            ram_msg += f" (Est. Available: {format_bytes(safe_ram_limit)})"

    # Calculate the limit to use for all subsequent checks
    limit_to_use = safe_ram_limit if safe_ram_limit is not None else total_ram

    model = prompt_model_selection(default_model, ram_info=ram_msg)
    
    # Check RAM vs Model Size (Preliminary)
    if model and os.path.exists(model) and total_ram and limit_to_use is not None:
        size = os.path.getsize(model)
        
        if size > limit_to_use:
            print(f"\n[CRITICAL] Model size ({format_bytes(size)}) exceeds estimated available RAM ({format_bytes(limit_to_use)})!")
            if not prompt_bool("Are you sure you want to use this model?", False):
                return
    
    # Check RAM vs Model Size + Context
    model_size = 0
    if model and os.path.exists(model):
        model_size = os.path.getsize(model)
        
    # Calculate Dynamic Default Context
    current_default_ctx = default_ctx
    
    if limit_to_use is not None and model_size > 0:
        available_for_ctx = limit_to_use - model_size
        if available_for_ctx > 0:
            # Check standard sizes in decreasing order
            options = [65536, 32768, 16384, 8192]
            for opt in options:
                est_usage = opt * 0.25 * 1024 * 1024
                if est_usage <= available_for_ctx:
                    current_default_ctx = str(opt)
                    break
            # If none fit (e.g. very tight), fallback to 4096 or keep original default
            if int(current_default_ctx) > 32768: # Cap default at reasonable high if needed or just let it float
                 pass 

    alias = prompt_value(
        "Alias (--alias)", 
        default_alias, 
        description="A recognizable name for ease of use with agents."
    )
    
    ctx_input = prompt_value(
        "Context Size (-c)", 
        current_default_ctx, 
        description="Size of the prompt context (tokens). Higher values use more VRAM."
    )
    
    while True:
        try:
            ctx_val = int(ctx_input)
        except ValueError:
            ctx_val = 0
            
        kv_cache_size = ctx_val * 0.25 * 1024 * 1024 
        total_est_usage = model_size + kv_cache_size
        
        if total_ram and limit_to_use is not None:
            if total_est_usage > limit_to_use:
                 print(f"\n[WARNING] Est. usage (Model {format_bytes(model_size)} + KV {format_bytes(kv_cache_size)} = {format_bytes(total_est_usage)}) exceeds estimated available RAM ({format_bytes(limit_to_use)})!")
                 print("This might cause swapping depending on the model architecture.")
                 if not prompt_bool("Continue with this context size?", False):
                     ctx_input = prompt_value("Enter a smaller context size", current_default_ctx)
                     continue
        
        break

    ctx = ctx_input
    
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
    
    port_input = prompt_value(
        "Port (--port)", 
        default_port, 
        description="Port listener for the server."
    )
    
    if is_port_in_use(port_input):
         print(f"\n[WARNING] Port {port_input} appears to be in use.")
         if not prompt_bool("Use this port anyway?", False):
              while is_port_in_use(port_input):
                  port_input = prompt_value("Enter a different port", "8081")
                  if not is_port_in_use(port_input):
                      break
                  print(f"Port {port_input} is also in use.")

    port = port_input

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
