import requests
import os

# --- Configuration ---
DEFAULT_WORDLIST_FILE = 'basiclist.txt'
REQUEST_TIMEOUT = 5  # seconds
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
CHECK_PROTOCOLS = ['https', 'http'] # Protocols to check, in order of preference

def display_banner():
    """Displays the tool's banner and credits."""
    print("----------------------------------------------------")
    print("           Subdomain Scanner by Markhor-Nyx        ")
    print("      Copyright (C) Markhor-Nyx. All rights reserved.   ")
    print("----------------------------------------------------")
    print("Scans for common subdomains for a given domain.\n")

def load_wordlist(filepath):
    """Loads subdomains from the specified wordlist file."""
    if not os.path.exists(filepath):
        print(f"[!] Error: Wordlist file '{filepath}' not found.")
        return None
    try:
        with open(filepath, 'r') as f:
            subdomains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if not subdomains:
            print(f"[!] Warning: Wordlist file '{filepath}' is empty or contains only comments.")
            return []
        return subdomains
    except Exception as e:
        print(f"[!] Error reading wordlist file '{filepath}': {e}")
        return None

def clean_domain_input(domain_input):
    """Cleans the user-provided domain input."""
    clean = domain_input.lower().strip()
    clean = clean.replace("https://", "").replace("http://", "")
    # Remove common prefixes that are not part of the root domain for subdomain scanning
    prefixes_to_remove = ["www.", "ftp.", "mail.", "webmail."]
    for prefix in prefixes_to_remove:
        if clean.startswith(prefix):
            # Be careful not to strip if the domain itself is short, e.g., "m.example.com" -> user enters "m.example.com"
            # This part might need more sophisticated logic if domains like "www.co.uk" are common targets
            # For simple cases, this is a basic approach.
            # A better way is to ask user for the "root" domain like "example.com"
            pass # Let's assume user provides root domain, or we adjust this logic

    # For subdomain scanning, we typically want the apex domain (e.g., example.com)
    # If user enters www.example.com, we should probably use example.com
    if clean.count('.') >= 1: # Simple check
        parts = clean.split('.')
        if parts[0] == 'www' and len(parts) > 2 : # like www.example.com, not www.com
             clean = ".".join(parts[1:])

    return clean.rstrip('/')


def scan_subdomains(base_domain, subdomains_list):
    """
    Scans for active subdomains.
    """
    print(f"[*] Starting subdomain scan for: {base_domain}")
    print(f"[*] Using wordlist: {DEFAULT_WORDLIST_FILE}")
    print(f"[*] Checking {len(subdomains_list)} potential subdomains...\n")

    found_subdomains = []
    headers = {'User-Agent': USER_AGENT}
    first_found_header_printed = False

    for sub in subdomains_list:
        if not sub: continue # Skip empty lines from wordlist

        # Construct the FQDN (Fully Qualified Domain Name)
        fqdn = f"{sub}.{base_domain}"

        for protocol in CHECK_PROTOCOLS:
            url_to_check = f"{protocol}://{fqdn}"
            try:
                # We are interested if the FQDN resolves and gives a web response.
                # For pure DNS resolution check, a DNS library would be better.
                # Here, requests.get() checks if a web server is listening.
                response = requests.get(url_to_check, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)

                # Consider a wider range of success codes or just that a response was received
                # 2xx codes are success. 3xx are redirects (often means it exists).
                # 401/403 can also mean it exists but needs auth / is forbidden.
                if 200 <= response.status_code < 400 or response.status_code == 401 or response.status_code == 403:
                    if not first_found_header_printed:
                        print("[+] Found potential live subdomains:")
                        first_found_header_printed = True

                    status_info = f"(Status: {response.status_code})"
                    # Check if it redirected to a different domain (common for www.sub.example.com -> sub.example.com)
                    if response.history: # If there were redirects
                        final_url = response.url
                        if base_domain not in final_url: # Redirected away from target domain
                             status_info += f" (Redirected to: {final_url})"

                    print(f"  [+] {url_to_check} {status_info}")
                    found_subdomains.append(url_to_check)
                    break # Found with this protocol, no need to check other protocol for this FQDN

            except requests.exceptions.Timeout:
                # print(f"  [-] Timeout for: {url_to_check}") # Verbose
                # If one protocol times out, the other might still work
                pass
            except requests.exceptions.ConnectionError:
                # This is the most common case for non-existent subdomains or no web server
                # print(f"  [-] Connection error for: {url_to_check}") # Verbose
                # If one protocol fails to connect, try the next for the same FQDN
                pass
            except requests.exceptions.RequestException as e:
                # print(f"  [-] Unexpected error for {url_to_check}: {e}") # Verbose
                pass

    if not found_subdomains:
        print(f"\n[-] No live subdomains found from the list for '{base_domain}'.")
    else:
        print(f"\n[*] Scan complete. Found {len(found_subdomains)} potential live subdomain(s).")

def main():
    display_banner()

    domain_input = input("Enter the ROOT domain name (e.g., example.com): ").strip()

    if not domain_input:
        print("[!] No domain entered. Exiting.")
        return

    # Clean the input to get the base domain for subdomain enumeration
    base_domain = clean_domain_input(domain_input)
    if not base_domain: # If cleaning results in empty string
        print("[!] Invalid domain format after cleaning. Exiting.")
        return

    print(f"[*] Target base domain set to: {base_domain}")

    subdomains_from_list = load_wordlist(DEFAULT_WORDLIST_FILE)
    if subdomains_from_list is None: # Fatal error loading
        return
    if not subdomains_from_list: # Empty list
        print("[!] Wordlist is empty. Nothing to scan. Exiting.")
        return

    scan_subdomains(base_domain, subdomains_from_list)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Scan aborted by user (Ctrl+C). Exiting.")
    except Exception as e:
        print(f"\n[!] An unexpected error occurred: {e}")