import requests
from colorama import Fore, Style, init # Added Style and init
import os # For environment variables (recommended for API key)
import json # For pretty printing JSON if needed

# Initialize Colorama
init(autoreset=True)

# --- Markhor-Nyx Branding and Configuration ---
# API_KEY = "22WfDqB635jMOWkxdeC1r2BXew1tXHLU" # !!! DO NOT HARDCODE API KEYS IN SCRIPT !!!

# Load API Key from environment variable or prompt user
API_KEY = os.getenv("APILAYER_NUMVERIFY_KEY") 
if not API_KEY:
    # print(Fore.YELLOW + "APILAYER_NUMVERIFY_KEY environment variable not set.") # Optional info
    # Fallback to prompting if not set (less secure than env var but better than hardcoding)
    # In a real tool, you might want to exit if key isn't available or guide user to set it.
    # For this tool, let's try prompting if not found in env.
    # However, for a tool in a suite, user might not want to enter it every time.
    # For now, I will keep your original hardcoded key for testing with a strong warning.
    # Ideally, the user of your "Zero-Tool" would configure this once.
    API_KEY_FROM_SCRIPT = "22WfDqB635jMOWkxdeC1r2BXew1tXHLU" # Keeping for your testing
    print(Fore.RED + "WARNING: Using a hardcoded API key from the script. This is insecure for distribution.")
    print(Fore.YELLOW + "It is highly recommended to set the APILAYER_NUMVERIFY_KEY environment variable.")
    API_KEY = API_KEY_FROM_SCRIPT


def print_tool_banner():
    print(Fore.GREEN + "******************************************************")
    print(Fore.GREEN + "*      Markhor-Nyx - Phone Number Validator        *")
    print(Fore.GREEN + "*    Developed by: Markhor-Nyx                     *")
    print(Fore.GREEN + "* Copyright (C) Markhor-Nyx. All rights reserved.   *")
    print(Fore.GREEN + "******************************************************")
    print(Fore.YELLOW + "Powered by APILayer Number Verification API." + Style.RESET_ALL)
    print(Fore.RED + "\n========================= WARNING! =========================")
    print(Fore.YELLOW + "Use this tool responsibly and ethically. Do not misuse personal data.")
    print(Fore.RED + "==========================================================\n" + Style.RESET_ALL)


def number_validator(phone_number_to_validate, api_key_to_use): # Renamed function for clarity
    """
    Validates a phone number using the APILayer Number Verification API.
    """
    if not api_key_to_use:
        return {"success": False, "error": {"info": "API key is missing."}}

    # The API expects the number with country code, e.g., +11234567890
    # You might want to add logic to prepend '+' if missing or guide user for format.
    # For now, assuming user provides it correctly or API handles variations.
    
    url = f"https://api.apilayer.com/number_verification/validate?number={phone_number_to_validate}"
    headers = {
        "apikey": api_key_to_use
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10) # Added timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        error_info = f"HTTP error occurred: {http_err}"
        try: # Try to get more specific error from API response if available
            error_details = response.json()
            if "message" in error_details: # APILayer often returns error in 'message'
                error_info += f" - API Message: {error_details['message']}"
            elif "error" in error_details and "info" in error_details["error"]:
                 error_info += f" - API Error Info: {error_details['error']['info']}"
        except json.JSONDecodeError:
            pass # Response was not JSON
        return {"success": False, "error": {"info": error_info, "code": response.status_code if response else None}}
    except requests.exceptions.ConnectionError as conn_err:
        return {"success": False, "error": {"info": f"Connection error: {conn_err}"}}
    except requests.exceptions.Timeout as timeout_err:
        return {"success": False, "error": {"info": f"Request timed out: {timeout_err}"}}
    except requests.exceptions.RequestException as req_err:
        return {"success": False, "error": {"info": f"An unexpected error occurred with the request: {req_err}"}}
    except json.JSONDecodeError:
        return {"success": False, "error": {"info": "Failed to decode JSON response from API."}}


def print_phone_details(phone_data): # Renamed parameter for clarity
    """
    Prints the phone number details in a user-friendly format.
    """
    if not phone_data: # Should not happen if error handling in validator is correct
        print(Fore.RED + "No data received to print.")
        return

    # Check for API error structure first (based on APILayer common responses)
    if phone_data.get("success") == False or "error" in phone_data: # API often returns success:false on error
        error_message = "API request failed."
        if "error" in phone_data and isinstance(phone_data["error"], dict) and "info" in phone_data["error"]:
            error_message += f" Info: {phone_data['error']['info']}"
        elif "message" in phone_data: # Direct error message from APILayer
             error_message += f" Message: {phone_data['message']}"
        print(Fore.RED + error_message)
        if "error" in phone_data and "code" in phone_data["error"] and phone_data["error"]["code"] == 101:
             print(Fore.RED + "This often means an invalid API key or subscription issue.")
        elif "error" in phone_data and "code" in phone_data["error"] and phone_data["error"]["code"] == 210:
             print(Fore.RED + "This often means the number is invalid or could not be validated.")

        return

    # If the API call was successful but the number is not valid
    # APILayer's 'valid' field indicates if the number format is potentially valid.
    # A number can be 'valid' in format but not exist or not be lookup-able.
    
    print(Fore.CYAN + "\n--- Phone Number Details ---")
    
    # Print available fields, checking if they exist in the response
    print(f"{Fore.GREEN}Number: {Style.RESET_ALL}{phone_data.get('number', 'N/A')}")
    
    # The 'valid' field is crucial
    is_valid_format = phone_data.get('valid', False)
    print(f"{Fore.GREEN}Format Valid: {Style.RESET_ALL}{Fore.GREEN if is_valid_format else Fore.RED}{is_valid_format}{Style.RESET_ALL}")

    # Only print detailed info if the format is considered valid by the API
    if is_valid_format:
        print(f"{Fore.GREEN}International Format: {Style.RESET_ALL}{phone_data.get('international_format', 'N/A')}")
        print(f"{Fore.GREEN}Local Format: {Style.RESET_ALL}{phone_data.get('local_format', 'N/A')}")
        print(f"{Fore.GREEN}Country: {Style.RESET_ALL}{phone_data.get('country_name', 'N/A')} ({phone_data.get('country_code', 'N/A')})")
        print(f"{Fore.GREEN}Country Prefix: {Style.RESET_ALL}{phone_data.get('country_prefix', 'N/A')}")
        print(f"{Fore.GREEN}Location (Region/City): {Style.RESET_ALL}{phone_data.get('location', 'N/A')}")
        print(f"{Fore.GREEN}Carrier: {Style.RESET_ALL}{phone_data.get('carrier', 'N/A')}")
        print(f"{Fore.GREEN}Line Type: {Style.RESET_ALL}{phone_data.get('line_type', 'N/A')}") # e.g., mobile, landline, voip
    else:
        print(Fore.YELLOW + "Detailed information may not be available for numbers marked as not (format) valid.")
    print(Fore.CYAN + "----------------------------")


if __name__ == "__main__":
    print_tool_banner()

    if not API_KEY or API_KEY == "22WfDqB635jMOWkxdeC1r2BXew1tXHLU": # Check if it's still the sample or missing
        # This check helps if the env var attempt failed and it fell back to the sample key
        if not API_KEY:
            print(Fore.RED + "CRITICAL: API Key is missing. Please set the APILAYER_NUMVERIFY_KEY environment variable or configure it in the script (not recommended for hardcoding).")
            sys.exit(1)
        # If it's the sample key, the earlier warning about hardcoding has already been shown.

    phone_number_input = input(Fore.MAGENTA + "Enter the phone number (with country code, e.g., +1xxxxxxxxxx): " + Style.RESET_ALL).strip()
    
    if not phone_number_input:
        print(Fore.RED + "No phone number entered. Exiting.")
        sys.exit(1)

    print(Fore.YELLOW + f"\nValidating phone number: {phone_number_input}...")
    details = number_validator(phone_number_input, API_KEY)
    print_phone_details(details)