import subprocess
import sys
import re
from colorama import init, Fore

# Initialize colorama
init()

# --- Markhor-Nyx Configuration ---
MARKHOR_NYX_GITHUB_URL = "https://github.com/YOUR_MARKHOR_NYX_USERNAME" # Update this if available

print(Fore.MAGENTA + "--- Markhor-Nyx Nuke Bot Launcher ---")
print(Fore.BLUE + "Developed by: Markhor-Nyx")
print(Fore.BLUE + "Copyright (C) Markhor-Nyx. All rights reserved.")
# if MARKHOR_NYX_GITHUB_URL != "https://github.com/YOUR_MARKHOR_NYX_USERNAME":
# print(Fore.YELLOW + f"Visit Markhor-Nyx on GitHub: {MARKHOR_NYX_GITHUB_URL}")
print(Fore.RED + "\nWARNING: THIS TOOL IS FOR ETHICAL AND AUTHORIZED USE ONLY.\n")


command = ['node', '--version']
node_major_version = 0

try:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    stdout, stderr = process.communicate(timeout=5) # Added timeout

    if process.returncode != 0:
        print(Fore.RED + f"Error checking Node.js version: {stderr.decode('utf-8', errors='ignore').strip()}")
        print(Fore.RED + "Please ensure Node.js is installed and in your PATH.")
        sys.exit(1)

    node_version = stdout.decode('utf-8', errors='ignore').strip()
    match = re.match(r"v(\d+)", node_version)
    if match:
        node_major_version = int(match.group(1))
    else:
        print(Fore.RED + f"Error: Failed to extract Node.js version from '{node_version}'.")
        sys.exit(1)
except FileNotFoundError:
    print(Fore.RED + "Error: Node.js command not found. Please install Node.js.")
    sys.exit(1)
except subprocess.TimeoutExpired:
    print(Fore.RED + "Error: Timeout while checking Node.js version.")
    sys.exit(1)


if node_major_version < 16: # discord.js v14 needs Node 16.9.0+
    print(Fore.RED + f"Error: Node.js version 16.9.0 or higher is required. You have v{node_major_version}.")
    print(Fore.RED + "Please upgrade your Node.js.")
    sys.exit(1)

print(Fore.GREEN + f"Node.js version {node_version} detected. Compatible.")
print(Fore.GREEN + "Starting Nuke Bot (Node.js script)...")

# Determine the path to index.js relative to the Zero-Tool launcher
# Assuming the main launcher is in Zero-Tool's parent directory.
# And this Main.py is directly called by the main launcher.
# The main launcher provides 'Zero-Tool/nuke-bot/main.py'
# So, index.js should be in 'Zero-Tool/nuke-bot/index.js'

# Path from the main project root (where Zero-Tool folder is)
script_path = 'Zero-Tool/nuke-bot/index.js'
# If this Main.py is *inside* Zero-Tool/nuke-bot/, then path is just 'index.js'
# Adjust if your structure is different.

command_run = ['node', script_path]

try:
    # Start the Node.js process
    # Using Popen without communicate/wait if the Python script is just a launcher
    # and the Node script will handle its own lifecycle.
    # If Python needs to wait for Node to finish, use process.wait().
    bot_process = subprocess.Popen(command_run, shell=False)
    
    # Option 1: Python script waits for Node script to exit
    bot_process.wait() 
    print(Fore.YELLOW + "Nuke Bot (Node.js script) has exited.")

    # Option 2: Python script exits after launching (Node script runs in background)
    # print(Fore.GREEN + "Nuke Bot launched. Python script will now exit.")
    # (No bot_process.wait() or communicate() here for Option 2)

except FileNotFoundError:
    print(Fore.RED + f"Error: Could not find the bot script at '{script_path}'.")
    print(Fore.RED + "Make sure 'index.js' is in the 'Zero-Tool/nuke-bot/' directory.")
    sys.exit(1)
except KeyboardInterrupt:
    print(Fore.YELLOW + "\nLauncher interrupted by user. If bot is running, it might still be active.")
    if 'bot_process' in locals() and bot_process.poll() is None:
        print(Fore.YELLOW + "Attempting to terminate the bot process...")
        bot_process.terminate() # Send SIGTERM
        try:
            bot_process.wait(timeout=5) # Wait for it to terminate
            print(Fore.GREEN + "Bot process terminated.")
        except subprocess.TimeoutExpired:
            print(Fore.RED + "Bot process did not terminate gracefully, may need to be killed manually.")
            bot_process.kill() # Force kill
            print(Fore.RED + "Bot process killed.")
except Exception as e:
    print(Fore.RED + f"An unexpected error occurred while running the bot: {e}")
    if 'bot_process' in locals() and bot_process.poll() is None:
        bot_process.kill() # Ensure child process is killed on error