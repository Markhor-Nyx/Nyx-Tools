import requests
import os # For potential future path handling, though not strictly needed here yet

# --- Configuration ---
WORDLIST_FILE = 'list.txt'
REQUEST_TIMEOUT = 5  # seconds
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def display_banner():
    """Displays the tool's banner and credits."""
    print("----------------------------------------------------")
    print("           Subdirectory Scanner by Markhor-Nyx      ")
    print("         Copyright (C) Markhor-Nyx. All rights reserved.    ")
    print("----------------------------------------------------\n")

def load_wordlist(filepath):
    """Loads directories from the specified wordlist file."""
    if not os.path.exists(filepath):
        print(f"[!] Error: Wordlist file '{filepath}' not found.")
        return None
    try:
        with open(filepath, 'r') as f:
            # Read lines, strip whitespace, and filter out empty lines
            directories = [line.strip() for line in f if line.strip()]
        if not directories:
            print(f"[!] Warning: Wordlist file '{filepath}' is empty.")
            return []
        return directories
    except Exception as e:
        print(f"[!] Error reading wordlist file '{filepath}': {e}")
        return None

def scan_domain(domain, directories):
    """
    Scans the given domain for subdirectories listed in the directories list.
    Tries both HTTP and HTTPS.
    """
    if not domain:
        print("[!] Error: No domain provided for scanning.")
        return

    print(f"[*] Starting scan for domain: {domain}")
    print(f"[*] Using wordlist: {WORDLIST_FILE}")
    print(f"[*] Checking {len(directories)} potential subdirectories...\n")

    found_count = 0
    protocols = ['https', 'http'] # Try HTTPS first

    # Remove any existing protocol and trailing slashes from user input
    clean_domain = domain.replace("https://", "").replace("http://", "").rstrip('/')

    first_found_header_printed = False

    for directory in directories:
        # Ensure directory itself doesn't have leading/trailing slashes to avoid double slashes
        clean_directory = directory.strip('/')
        if not clean_directory: # Skip if directory entry was just slashes or empty
            continue

        for protocol in protocols:
            url = f"{protocol}://{clean_domain}/{clean_directory}"
            try:
                headers = {'User-Agent': USER_AGENT}
                response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True) # allow_redirects=True is default

                # Check for common success or "exists but forbidden" codes
                if response.status_code == 200:
                    if not first_found_header_printed:
                        print("[+] Found URLs:")
                        first_found_header_printed = True
                    print(f"  [+] {url} (Status: 200 OK)")
                    found_count += 1
                    break # Found with this protocol, no need to check other protocol for this directory
                elif response.status_code == 403:
                    if not first_found_header_printed:
                        print("[+] Found URLs (or indications of existence):")
                        first_found_header_printed = True
                    print(f"  [?] {url} (Status: 403 Forbidden - Likely exists but access denied)")
                    found_count += 1
                    break # Indication found, no need to check other protocol

                # You could add checks for other status codes if relevant (e.g., 301/302 if allow_redirects=False)

            except requests.exceptions.Timeout:
                # print(f"  [-] Timeout for: {url}") # Uncomment for verbose output
                pass
            except requests.exceptions.ConnectionError:
                # print(f"  [-] Connection error for: {url}") # Uncomment for verbose output
                # This can happen if the domain or subdomain doesn't resolve or server is down
                # Breaking here for this directory might be reasonable if one protocol fails to connect
                break
            except requests.exceptions.RequestException as e:
                # print(f"  [-] Error for {url}: {e}") # Uncomment for verbose output
                pass # Catch any other requests-related errors

    if found_count == 0:
        print("\n[-] No subdirectories found from the list for the specified domain.")
    else:
        print(f"\n[*] Scan complete. Found {found_count} potential item(s).")

def main():
    """Main function to run the subdirectory scanner."""
    display_banner()

    target_domain = input("Enter the target domain (e.g., example.com): ").strip()
    if not target_domain:
        print("[!] No domain entered. Exiting.")
        return

    directories_list = load_wordlist(WORDLIST_FILE)
    if directories_list is None: # Indicates a fatal error in loading wordlist
        print("[!] Could not load wordlist. Exiting.")
        return
    if not directories_list: # Indicates wordlist was empty but loaded
        print("[!] Wordlist is empty. Nothing to scan. Exiting.")
        return


    scan_domain(target_domain, directories_list)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Scan aborted by user (Ctrl+C). Exiting.")
    except Exception as e:
        print(f"\n[!] An unexpected error occurred: {e}")