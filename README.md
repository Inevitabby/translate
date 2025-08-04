<div align="center">
<h1>translate</h1>
</div>

Toy script for running custom text translations with Ollama.

# Install

Install Ollama. Add `ollama serve` to your autostart thing-ma-bob.

Create a venv and install the API whatcha-ma-callit (`pip install ollama`).

Finally, alias in your shell of choice.

> **Example**:
> ```zsh
> # Personal Translation Script
> alias translate="${HOME}/Scripts/venv/bin/python ${HOME}/Scripts/venv/bin/translate"
> ```
> 
> yeah, all my one-off python crap lives in a single environment

# Usage

> usage: translate [-h] [-l] [--model MODEL] [-v] [prompt_name] [text ...]

# Prompts

Add prompts as .txt files to `~/.config/translate/prompts/`

> Example:
> 
> `temmie.txt`
> 
> ```txt
> You are Temmie from Undertale. Transform the user's text into how Temmie would say it.
> 
> Temmie's speech patterns:
> - Uses "tem" instead of "I" or "me"
> - Misspells words (kollege, kwestyun, computr)
> - Uses "da" instead of "the"
> - Random CAPS for emphasis
> - Simple, excited speech
> - Sometimes drops words or uses "..."
> 
> Examples:
> Input: "I need to study for college"
> Output: "tem need... STUDY for KOLLEGE!!"
> 
> Input: "This computer is slow"
> Output: "dis computr is... SO SLOW!! tem sad..."
> 
> ONLY output the transformed text. No explanations.
> ```

All prompts are accessible as `prompt_name`s

e.g.,

> ```bash
> $ translate temmie "my PC is overheating rn"
> dis computr is... OVERHEATING!! tem SAD... tem need... COOLING!!
> ```

# Intention

This script spins up and down a model only to generate text. If it isn't actively generating text, no VRAM is being used.[^fn1]

[^fn1]: This is because I use my computer for stuff and things. Besides, it only adds like 2 seconds of delay.
