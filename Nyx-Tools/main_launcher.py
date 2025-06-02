import os
import sys
import subprocess
import colorama # For colors

# --- Import tool-specific logic ---
# Make sure Python can find these modules.
# If Nyx-Tools is the current working directory, this should work.
# Otherwise, sys.path might need adjustment, or use relative imports if structured as a package.
try:
    from subdirectory_scanner.scanner_logic import run_subdirectory_scan
    from subdomain_scanner.scanner_logic import run_subdomain_scan
    from port_scanner.scanner_logic import run_port_scan
    from ddos_tool.flooder_logic import run_ddos_tool
    from email_bomber.bomber_logic import run_email_bomber
    from phone_validator.validator_logic import run_phone_validator
    from discord_token_grabber.grabber_logic import run_token_grabber # Ensure extreme warnings
except ImportError as e:
    print(f"{colorama.Fore.RED}Error importing tool modules: {e}")
    print(f"{colorama.Fore.YELLOW}Ensure you are in the 'Nyx-Tools' directory and all tool folders exist.")
    sys.exit(1)

colorama.init(autoreset=True)

def display_main_banner():
    print(colorama.Fore.CYAN + "**********************************************")
    print(colorama.Fore.CYAN + "*             Welcome to NYX TOOLS           *")
    print(colorama.Fore.CYAN + "*         A Suite by Markhor-Nyx             *")
    print(colorama.Fore.CYAN + "**********************************************\n")

def display_menu():
    print(colorama.Fore.YELLOW + "Please select a tool to use:")
    print(" 1. Subdirectory Scanner")
    print(" 2. Subdomain Scanner")
    print(" 3. Port Scanner")
    print(" 4. HTTP Flooder (DDoS Tool)")
    print(" 5. Email Bomber")
    print(" 6. Phone Number Validator")
    print(" 7. Discord Token Grabber (⚠️ Ethical Use Only!)")
    print(" 8. Discord Nuke Bot (Node.js - ⚠️ Extreme Caution!)")
    print(" 0. Exit")
    print("-" * 30)

def main():
    display_main_banner()
    while True:
        display_menu()
        choice = input(colorama.Fore.GREEN + "Enter your choice: " + colorama.Style.RESET_ALL).strip()

        if choice == '1':
            print(colorama.Fore.CYAN + "\n--- Subdirectory Scanner ---")
            run_subdirectory_scan()
        elif choice == '2':
            print(colorama.Fore.CYAN + "\n--- Subdomain Scanner ---")
            run_subdomain_scan()
        elif choice == '3':
            print(colorama.Fore.CYAN + "\n--- Port Scanner ---")
            run_port_scan()
        elif choice == '4':
            print(colorama.Fore.CYAN + "\n--- HTTP Flooder ---")
            run_ddos_tool()
        elif choice == '5':
            print(colorama.Fore.CYAN + "\n--- Email Bomber ---")
            run_email_bomber()
        elif choice == '6':
            print(colorama.Fore.CYAN + "\n--- Phone Number Validator ---")
            run_phone_validator()
        elif choice == '7':
            print(colorama.Fore.RED + "\n--- Discord Token Grabber ---")
            print(colorama.Fore.YELLOW + "WARNING: This tool is for educational purposes only. Misuse is illegal.")
            confirm_dangerous = input("Type 'understand' to proceed: ").lower()
            if confirm_dangerous == 'understand':
                run_token_grabber()
            else:
                print(colorama.Fore.YELLOW + "Token Grabber execution cancelled.")
        elif choice == '8':
            print(colorama.Fore.RED + "\n--- Discord Nuke Bot (Node.js) ---")
            print(colorama.Fore.YELLOW + "WARNING: This tool is extremely destructive. Use with EXTREME CAUTION on servers you OWN.")
            confirm_nuke = input("Type 'NUKEIT' to proceed: ") # Stricter confirmation
            if confirm_nuke == 'NUKEIT':
                print(colorama.Fore.CYAN + "Attempting to launch Nuke Bot...")
                try:
                    # Assuming NukeBot's Main.py launcher is in discord_nuke_bot/
                    # And index.js is also there.
                    # Adjust path if NukeBot's Python launcher itself calls node index.js
                    # Option 1: Directly call node index.js
                    # subprocess.run(['node', 'discord_nuke_bot/index.js'], check=True)
                    # Option 2: Call NukeBot's Python launcher (if it exists and handles node call)
                    nuke_bot_launcher_path = os.path.join("discord_nuke_bot", "Main.py") # Or whatever its launcher is named
                    if os.path.exists(nuke_bot_launcher_path):
                         # Check if nodejs is installed
                        try:
                            node_check = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
                            print(colorama.Fore.GREEN + f"Node.js found: {node_check.stdout.strip()}")
                            print(colorama.Fore.YELLOW + "Ensure Nuke Bot dependencies are installed in 'discord_nuke_bot/' folder with 'npm install'.")
                            subprocess.run([sys.executable, nuke_bot_launcher_path], cwd="discord_nuke_bot", check=True)
                        except FileNotFoundError:
                            print(colorama.Fore.RED + "Error: Node.js not found. Please install Node.js to run this tool.")
                        except subprocess.CalledProcessError as e:
                            print(colorama.Fore.RED + f"Nuke Bot script exited with an error: {e}")

                    else:
                         print(colorama.Fore.RED + f"Error: Nuke Bot launcher script not found at {nuke_bot_launcher_path}")
                except FileNotFoundError:
                    print(colorama.Fore.RED + "Error: Node.js or Nuke Bot script not found. Make sure Node.js is installed and paths are correct.")
                except subprocess.CalledProcessError as e:
                    print(colorama.Fore.RED + f"Nuke Bot script exited with an error: {e}")
                except Exception as e:
                    print(colorama.Fore.RED + f"An unexpected error occurred: {e}")
            else:
                print(colorama.Fore.YELLOW + "Nuke Bot execution cancelled.")

        elif choice == '0':
            print(colorama.Fore.BLUE + "Exiting NYX TOOLS. Goodbye!")
            break
        else:
            print(colorama.Fore.RED + "Invalid choice. Please try again.")
        
        input(colorama.Fore.CYAN + "\nPress Enter to return to the main menu...")
        os.system('cls' if os.name == 'nt' else 'clear') # Clear screen

if __name__ == "__main__":
    main()