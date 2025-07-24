# Tmuxinator Helper Script

This script allows you to easily manage your [tmuxinator](https://github.com/tmuxinator/tmuxinator) configurations using an interactive terminal interface. 
It supports listing, selecting, editing, and creating new configurations using fuzzy search and interactive menus.

## Prerequisites
Ensure you have the following installed:
- [Tmuxinator](https://github.com/tmuxinator/tmuxinator)
- [`fzf`](https://github.com/junegunn/fzf) (for fuzzy searching)

## Installation
1. Copy the script to a directory in your `$PATH` (e.g., `~/.local/bin/mux`).
2. Give it execute permissions:
   ```sh
   chmod +x ~/.local/bin/mux
   ```
3. Ensure a template file named `template.yml` exists in your tmuxinator config directory for creating new configurations.

## Usage
Run the script with different flags to perform various actions:
### 1. List and Select a Configuration (`-l` `--list`)
```sh
mux -l
```
This will list all available tmuxinator configurations and allow you to select one using a numbered menu.

### 2. Start a Configuration (Default Mode)
```sh
mux
```
This will prompt you to type part of a configuration name and use `fzf` to filter matches interactively. Select one to start it.

### 3. Edit a Configuration (`-e` or `--edit`)
```sh
mux -e
```
This opens a fuzzy search menu to select an existing configuration and edit it with your default editor (`$EDITOR`, defaults to `nano`).

### 4. Create a New Configuration (`-n` or `--new`)
```sh
mux -n
```
This prompts for a new configuration name and creates it by duplicating `template.yml`. If the configuration already exists, it shows an error. Once created, the file opens in your default editor for modification.
