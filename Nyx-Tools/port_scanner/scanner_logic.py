import sys
import socket
from datetime import datetime
import threading
from queue import Queue # For distributing ports to threads
import colorama
import time # For delays if needed

# Initialize Colorama
colorama.init(autoreset=True)

# --- Global Variables for Threading ---
print_lock = threading.Lock() # To ensure clean printing from threads
open_ports_list = []
queue = Queue() # Port queue for threads

# --- Markhor-Nyx Branding ---
def print_banner():
    # (Banner code same as previous Port Scanner example)
    print(colorama.Fore.GREEN + "*************************************************************")
    print(colorama.Fore.GREEN + "*    Markhor-Nyx - Advanced Threaded Port Scanner (v2)    *")
    print(colorama.Fore.GREEN + "*           Developed by: Markhor-Nyx                     *")
    print(colorama.Fore.GREEN + "*      Copyright (C) Markhor-Nyx. All rights reserved.     *")
    print(colorama.Fore.GREEN + "*************************************************************")
    print(colorama.Fore.RED + "\n========================= WARNING! =========================")
    print(colorama.Fore.YELLOW + "This tool is for EDUCATIONAL AND AUTHORIZED TESTING ONLY.")
    print(colorama.Fore.YELLOW + "Unauthorized port scanning can be illegal and intrusive.")
    print(colorama.Fore.YELLOW + "You are solely responsible for your actions.")
    print(colorama.Fore.RED + "==========================================================\n" + colorama.Style.RESET_ALL)


def resolve_host(target_host_input):
    try:
        target_ip = socket.gethostbyname(target_host_input)
        return target_ip
    except socket.gaierror:
        with print_lock:
            print(colorama.Fore.RED + f"Error: Hostname '{target_host_input}' could not be resolved.")
        return None

def grab_banner(s):
    """Attempts to grab a banner from an open socket."""
    try:
        s.settimeout(0.5) # Short timeout for banner grabbing
        banner_data = s.recv(1024) # Receive up to 1024 bytes
        return banner_data.decode(errors='ignore').strip()
    except socket.timeout:
        return "Timeout receiving banner"
    except Exception:
        return "Error grabbing banner"


def scan_port_worker(target_ip, scan_timeout_per_port):
    """Worker function for threads to scan ports from the queue."""
    while not queue.empty():
        try:
            port = queue.get_nowait() # Get port from queue without blocking
        except Exception: # Queue might be empty due to race condition
            return 

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(scan_timeout_per_port)
            result = s.connect_ex((target_ip, port))

            if result == 0: # Port is open
                banner_info = grab_banner(s) # Attempt to grab banner
                with print_lock:
                    open_ports_list.append((port, banner_info))
                    # Try to get service name
                    try:
                        service_name = socket.getservbyport(port)
                    except OSError:
                        service_name = "Unknown"

                    # Clear progress line before printing open port
                    sys.stdout.write("\r" + " " * 80 + "\r") 
                    print(colorama.Fore.GREEN + f"[+] Port {port:<5} ({service_name:<15}) is open | Banner: {banner_info[:60]}{'...' if len(banner_info)>60 else ''}")
            s.close()
        except socket.error:
            pass # Silently ignore connection errors for closed/filtered ports
        except Exception:
            pass # Silently ignore other errors within a scan attempt
        finally:
            queue.task_done() # Signal that this task from queue is done


# --- Main Execution ---
if __name__ == "__main__":
    print_banner()

    host_input = input(colorama.Fore.MAGENTA + "Enter target host (IP or hostname): " + colorama.Style.RESET_ALL).strip()
    if not host_input: print(colorama.Fore.RED + "No target. Exiting."); sys.exit(1)

    target_ip_address = resolve_host(host_input)
    if not target_ip_address: sys.exit(1)

    port_input_str = input(colorama.Fore.MAGENTA + "Enter ports (e.g., 80, 1-1024, 22,80,443): " + colorama.Style.RESET_ALL).strip()
    if not port_input_str: print(colorama.Fore.RED + "No ports. Exiting."); sys.exit(1)

    ports_to_scan_parsed = []
    try:
        port_parts = port_input_str.split(',')
        for part in port_parts:
            part = part.strip()
            if '-' in part:
                start_port, end_port = map(int, part.split('-'))
                if not (0 < start_port <= 65535 and 0 < end_port <= 65535 and start_port <= end_port):
                    raise ValueError("Invalid port range.")
                ports_to_scan_parsed.extend(range(start_port, end_port + 1))
            else:
                port_num = int(part)
                if not (0 < port_num <= 65535): raise ValueError("Port out of range.")
                ports_to_scan_parsed.append(port_num)
        ports_to_scan_parsed = sorted(list(set(ports_to_scan_parsed)))
        if not ports_to_scan_parsed: raise ValueError("No valid ports.")
    except ValueError as e:
        print(colorama.Fore.RED + f"Error: Invalid port spec: {e}."); sys.exit(1)

    try:
        num_threads = int(input(colorama.Fore.MAGENTA + "Enter number of threads (e.g., 50, default: 20): " + colorama.Style.RESET_ALL).strip() or "20")
        if num_threads <= 0: num_threads = 20
    except ValueError:
        print(colorama.Fore.YELLOW + "Invalid thread count. Using default 20."); num_threads = 20

    try:
        scan_timeout = float(input(colorama.Fore.MAGENTA + "Enter timeout per port (seconds, e.g., 0.5, default: 1): " + colorama.Style.RESET_ALL).strip() or "1")
        if scan_timeout <= 0: scan_timeout = 1.0
    except ValueError:
        print(colorama.Fore.YELLOW + "Invalid timeout. Using default 1 second."); scan_timeout = 1.0

    # Populate the queue with ports to scan
    for p in ports_to_scan_parsed:
        queue.put(p)

    total_ports_in_queue = queue.qsize() # Initial number of ports

    print(colorama.Fore.CYAN + "-" * 70)
    print(f"Scanning target: {colorama.Fore.YELLOW}{host_input} ({target_ip_address})")
    print(f"Ports to scan: {total_ports_in_queue} (From {min(ports_to_scan_parsed)} to {max(ports_to_scan_parsed)})")
    print(f"Threads: {num_threads} | Timeout per port: {scan_timeout}s")
    print(f"Scan started at: {colorama.Fore.YELLOW}{str(datetime.now())}")
    print(colorama.Fore.CYAN + "-" * 70 + colorama.Style.RESET_ALL)

    start_scan_time = datetime.now()
    threads = []

    # Start worker threads
    for _ in range(num_threads):
        thread = threading.Thread(target=scan_port_worker, args=(target_ip_address, scan_timeout))
        thread.daemon = True # Allow main program to exit even if threads are stuck
        thread.start()
        threads.append(thread)

    # Progress monitoring in main thread
    try:
        initial_q_size = total_ports_in_queue
        while not queue.empty() or any(t.is_alive() for t in threads):
            # Display progress
            ports_processed = initial_q_size - queue.qsize()
            progress_percent = (ports_processed / initial_q_size) * 100 if initial_q_size > 0 else 0

            with print_lock: # Ensure progress printing is not interrupted by open port prints
                sys.stdout.write(colorama.Fore.YELLOW + f"\rScanning... Processed: {ports_processed}/{initial_q_size} ({progress_percent:.1f}%) Open: {len(open_ports_list)}   ")
                sys.stdout.flush()
            time.sleep(0.2) # Update progress periodically

            # Check if all worker threads have finished and queue is empty
            if queue.empty() and not any(t.is_alive() for t in threads):
                break

    except KeyboardInterrupt:
        with print_lock:
            sys.stdout.write("\r" + " " * 80 + "\r") # Clear progress line
            print(colorama.Fore.YELLOW + "\n\n[!] Scan interrupted by user (Ctrl+C)." + colorama.Style.RESET_ALL)
        # No need to explicitly stop daemon threads, they will exit with main.
        # If non-daemon, would need a stop_event.
    except Exception as e:
        with print_lock:
            sys.stdout.write("\r" + " " * 80 + "\r")
            print(colorama.Fore.RED + f"\n\nAn unexpected error occurred: {e}")
    finally:
        # Wait for all tasks in the queue to be processed (if not interrupted)
        # queue.join() # This blocks until all task_done() are called

        # Wait for all daemon threads to finish naturally or be terminated on exit.
        # If using non-daemon threads, ensure they are joined or signaled to stop.
        # For daemon threads, this final join is mostly for cleanup if needed.
        # for t in threads:
        #     t.join(timeout=0.1) # Short join attempt

        sys.stdout.write("\r" + " " * 80 + "\r") # Final clear of progress line
        end_scan_time = datetime.now()
        total_scan_duration = end_scan_time - start_scan_time

        print(colorama.Fore.CYAN + "-" * 70)
        if open_ports_list:
            print(colorama.Fore.GREEN + "Scan Complete. Open ports found (sorted):")
            # Sort open ports by port number
            sorted_open_ports = sorted(open_ports_list, key=lambda x: x[0])
            for port, banner_text in sorted_open_ports:
                try:
                    service_name = socket.getservbyport(port)
                except OSError:
                    service_name = "Unknown"
                banner_display = banner_text[:60] + ('...' if len(banner_text) > 60 else '')
                print(f"  Port {colorama.Fore.YELLOW}{port:<5}{colorama.Style.RESET_ALL} ({service_name:<15}) | Banner: {banner_display}")
        else:
            print(colorama.Fore.YELLOW + "Scan Complete. No open ports found in the specified range.")

        print(f"\nScan finished at: {str(end_scan_time)}")
        print(f"Total scan duration: {total_scan_duration}")
        print(colorama.Fore.CYAN + "-" * 70 + colorama.Style.RESET_ALL)