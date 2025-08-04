#!/usr/bin/env python
import os
import argparse
import sys
import ollama
import subprocess
import re
from pathlib import Path

def log(message: str, verbose: bool = True):
    if verbose:
        print(message, file=sys.stderr, flush=True)

def load_prompt(prompt_name: str) -> str:
    prompt_file = Path.home() / ".config" / "translate" / "prompts" / f"{prompt_name}.txt"
    
    if not prompt_file.exists():
        return None
    
    try:
        return prompt_file.read_text().strip()
    except Exception:
        return None

def unload_model(model_name: str, verbose: bool = True):
    log(f"Unloading model '{model_name}'...", verbose)
    try:
        subprocess.run(
            ["ollama", "stop", model_name],
            check=True,
            capture_output=True,
            text=True
        )
        log(f"Model '{model_name}' unloaded successfully.", verbose)
    except FileNotFoundError:
        log("Error: 'ollama' command not found. Is Ollama installed and in your PATH?", verbose)
    except subprocess.CalledProcessError as e:
        if "no such model" in e.stderr:
            log(f"Info: Model '{model_name}' was not running.", verbose)
        else:
            log(f"Error unloading model: {e.stderr.strip()}", verbose)

def clean_model_output(content: str) -> str:
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    content = re.sub(r'\[.*?\]:', '', content).strip()
    content = re.sub(r'^(Output:|.*says?:?)\s*', '', content, flags=re.IGNORECASE).strip()
    return content

def transform_text(text_to_transform: str, system_prompt: str, model_name: str, verbose: bool = True) -> str:
    try:
        log(f"Loading model '{model_name}' and transforming text...", verbose)
        
        response = ollama.chat(
            model=model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text_to_transform},
            ],
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'repeat_penalty': 1.1,
                'num_predict': 100,
            }
        )
        
        content = response['message']['content'].strip()
        return clean_model_output(content)
        
    except ollama.ResponseError as e:
        if "model not found" in e.error:
            return f"Error: Model '{model_name}' not found. Pull it with `ollama pull {model_name}`."
        return f"Ollama API Error: {e.error}"
    except Exception as e:
        return f"Error: Could not connect to Ollama. Is the server running?\nDetails: {e}"

def list_prompts():
    prompts_dir = Path.home() / ".config" / "translate" / "prompts"
    
    if not prompts_dir.exists():
        print("No prompts directory found. Create: ~/.config/translate/prompts/")
        return
    
    prompt_files = list(prompts_dir.glob("*.txt"))
    
    if not prompt_files:
        print("No prompts found in ~/.config/translate/prompts/")
        return
    
    print("Available prompts:")
    for prompt_file in sorted(prompt_files):
        print(f"  {prompt_file.stem}")

def main():
    parser = argparse.ArgumentParser(
        description="Transforms text using prompts from ~/.config/translate/prompts/"
    )
    parser.add_argument(
        "prompt_name",
        nargs="?",
        help="Name of the prompt file (without .txt extension)"
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="The input string to be transformed."
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available prompts"
    )
    parser.add_argument(
        "--model",
        default="gemma3:4b",
        help="The Ollama model to use. Recommended: llama3.2:3b, phi3:mini, or qwen2.5:3b"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show loading/unloading messages and other status information."
    )
    args = parser.parse_args()

    if args.list:
        list_prompts()
        return

    if not args.prompt_name:
        parser.error("prompt_name is required unless using --list")
    
    if not args.text:
        parser.error("text is required")

    system_prompt = load_prompt(args.prompt_name)
    if system_prompt is None:
        prompt_path = Path.home() / ".config" / "translate" / "prompts" / f"{args.prompt_name}.txt"
        log(f"Error: Prompt file not found: {prompt_path}", True)
        sys.exit(1)

    try:
        input_text = " ".join(args.text)
        log(f"Input: {input_text}", args.verbose)
        log(f"Using prompt: {args.prompt_name}", args.verbose)
        
        transformed_text = transform_text(input_text, system_prompt, args.model, args.verbose)

        if transformed_text and not transformed_text.startswith("Error:"):
            print(transformed_text, flush=True)
        else:
            log(f"Model output issue: {transformed_text}", args.verbose)
            print("Error: Could not transform text", flush=True)
            sys.exit(1)

    except Exception as e:
        log(f"An unexpected critical error occurred: {e}", args.verbose)
        sys.exit(1)
    finally:
        unload_model(args.model, args.verbose)

if __name__ == "__main__":
    main()
