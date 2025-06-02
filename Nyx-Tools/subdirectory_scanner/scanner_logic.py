import requests
import os
import colorama # Assuming you use colorama here too for consistency

# Initialize colorama if you use it within this logic file directly
# colorama.init(autoreset=True) # Or handle init in main_launcher.py

# --- Configuration ---
# The DEFAULT_WORDLIST_FILE is now relative to this script's directory, inside 'wordlists'
DEFAULT_WORDLIST_FILE = os.path.join('wordlists', 'large_subdomain_list.txt')
REQUEST_TIMEOUT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
CHECK_PROTOCOLS = ['https', 'http']

def load_wordlist(script_file_path):
    """
    Loads subdomains from the wordlist file.
    The wordlist path is resolved relative to the script_file_path's directory.
    """
    base_dir = os.path.dirname(script_file_path) # Get directory of this script
    filepath = os.path.join(base_dir, DEFAULT_WORDLIST_FILE)

    if not os.path.exists(filepath):
        print(f"{colorama.Fore.RED}[!] Error: Wordlist file '{filepath}' not found.")
        return None
    try:
        with open(filepath, 'r') as f:
            subdomains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if not subdomains:
            print(f"{colorama.Fore.YELLOW}[!] Warning: Wordlist file '{filepath}' is empty or only has comments.")
            return []
        return subdomains
    except Exception as e:
        print(f"{colorama.Fore.RED}[!] Error reading wordlist file '{filepath}': {e}")
        return None

def clean_domain_input(domain_input):
    clean = domain_input.lower().strip()
    clean = clean.replace("https://", "").replace("http://", "")
    if clean.count('.') >= 1:
        parts = clean.split('.')
        if parts[0] == 'www' and len(parts) > 2:
             clean = ".".join(parts[1:])
    return clean.rstrip('/')

def perform_scan(base_domain, subdomains_list):
    """
    Performs the actual subdomain scanning logic.
    (This is the renamed scan_subdomains function from previous examples)
    """
    print(f"{colorama.Fore.CYAN}[*] Starting subdomain scan for: {base_domain}")
    # Wordlist path is now handled by load_wordlist relative to this script
    print(f"{colorama.Fore.CYAN}[*] Using wordlist: {DEFAULT_WORDLIST_FILE} (relative to scanner script)")
    print(f"{colorama.Fore.CYAN}[*] Checking {len(subdomains_list)} potential subdomains...\n")

    found_subdomains_details = [] # Store (url, status_code, final_url if redirected)
    headers = {'User-Agent': USER_AGENT}
    first_found_header_printed = False

    for sub in subdomains_list:
        if not sub: continue
        fqdn = f"{sub}.{base_domain}"

        for protocol in CHECK_PROTOCOLS:
            url_to_check = f"{protocol}://{fqdn}"
            try:
                response = requests.get(url_to_check, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
                status_code = response.status_code
                final_url_after_redirect = response.url # Will be same as url_to_check if no redirect

                if 200 <= status_code < 400 or status_code == 401 or status_code == 403:
                    if not first_found_header_printed:
                        print(f"{colorama.Fore.GREEN}[+] Found potential live subdomains:")
                        first_found_header_printed = True
                    
                    status_info = f"(Status: {status_code})"
                    redirect_info = ""
                    if response.history: # If there were redirects
                         if base_domain not in final_url_after_redirect:
                             redirect_info = f" (Redirected to: {final_url_after_redirect})"
                    
                    print(f"  {colorama.Fore.GREEN}[+] {url_to_check} {status_info}{redirect_info}")
                    found_subdomains_details.append((url_to_check, status_code, final_url_after_redirect))
                    break 
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except requests.exceptions.RequestException:
                pass

    if not found_subdomains_details:
        print(f"\n{colorama.Fore.YELLOW}[-] No live subdomains found from the list for '{base_domain}'.")
    else:
        print(f"\n{colorama.Fore.GREEN}[*] Scan complete. Found {len(found_subdomains_details)} potential live subdomain(s).")
    return found_subdomains_details # Return list of found details

def run_subdomain_scan():
    """
    Main function to be called by the launcher.
    It handles user input and orchestrates the scan.
    """
    # Initialize colorama here if not done globally in launcher
    # import colorama 
    # colorama.init(autoreset=True)

    print(colorama.Fore.BLUE + "--- Markhor-Nyx Subdomain Scanner ---")
    domain_input = input(colorama.Fore.MAGENTA + "Enter the ROOT domain name (e.g., example.com): " + colorama.Style.RESET_ALL).strip()
    
    if not domain_input:
        print(f"{colorama.Fore.RED}[!] No domain entered. Aborting scan." + colorama.Style.RESET_ALL)
        return

    base_domain = clean_domain_input(domain_input)
    if not base_domain:
        print(f"{colorama.Fore.RED}[!] Invalid domain format after cleaning. Aborting." + colorama.Style.RESET_ALL)
        return

    print(f"{colorama.Fore.CYAN}[*] Target base domain set to: {base_domain}")

    # __file__ gives the path of the current script (scanner_logic.py)
    # This ensures load_wordlist finds the wordlist relative to this script.
    subdomains_from_list = load_wordlist(os.path.abspath(__file__)) 
    
    if subdomains_from_list is None: # Fatal error loading
        print(f"{colorama.Fore.RED}[!] Could not load wordlist. Aborting scan." + colorama.Style.RESET_ALL)
        return
    if not subdomains_from_list: # Empty list
        print(f"{colorama.Fore.YELLOW}[!] Wordlist is empty. Nothing to scan." + colorama.Style.RESET_ALL)
        return

    perform_scan(base_domain, subdomains_from_list)

# This allows testing scanner_logic.py directly if needed
if __name__ == "__main__":
    # If running this script directly, initialize colorama
    import colorama
    colorama.init(autoreset=True)
    run_subdomain_scan()