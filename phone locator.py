import requests
import re
from colorama import Fore, Style, init
import os
import json

# Initialize Colorama
init(autoreset=True)

# --- Markhor-Nyx Branding ---
# (Banner code from previous phone_lookup.py example can be reused here)
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


def validate_apilayer_key_format(key_to_validate):
    """
    Validates if the provided key matches the typical APILayer format.
    APILayer keys are usually 32 alphanumeric characters.
    """
    if key_to_validate and len(key_to_validate) == 32 and key_to_validate.isalnum():
        # isalnum() checks for A-Z, a-z, 0-9. APILayer keys might be only A-Z, 0-9.
        # A more specific regex like r"^[A-Z0-9]{32}$" could be used if only uppercase and digits.
        # For now, isalnum() is a good general check.
        return True
    return False

def get_api_key():
    """
    Tries to get API key from environment variable, then prompts user if not found.
    Validates the format of the user-provided key.
    """
    api_key = os.getenv("APILAYER_NUMVERIFY_KEY")
    if api_key and validate_apilayer_key_format(api_key):
        print(Fore.GREEN + "Using API Key from APILAYER_NUMVERIFY_KEY environment variable.")
        return api_key
    
    if api_key and not validate_apilayer_key_format(api_key):
        print(Fore.YELLOW + "Warning: API Key from environment variable has an unexpected format. Please check it.")
        # Proceed to ask user for a key.

    print(Fore.CYAN + "APILayer Number Verification API Key is required.")
    print(Fore.YELLOW + "You can get a free key from https://apilayer.com/marketplace/number_verification-api")
    
    while True:
        user_api_key = input(Fore.MAGENTA + "Enter your APILayer API Key: " + Style.RESET_ALL).strip()
        if validate_apilayer_key_format(user_api_key):
            print(Fore.GREEN + "API Key format appears valid.")
            return user_api_key
        else:
            print(Fore.RED + "Invalid API Key format. It should typically be 32 alphanumeric characters.")
            retry = input(Fore.YELLOW + "Try again? (yes/no): " + Style.RESET_ALL).lower()
            if retry != 'yes':
                print(Fore.RED + "Exiting because a valid API key is required.")
                sys.exit(1)


def number_validator(phone_number_to_validate, api_key_to_use):
    # (This function is the same as in the previous phone_lookup.py example)
    # (It includes timeout, error handling for HTTPError, ConnectionError, etc.)
    if not api_key_to_use:
        return {"success": False, "error": {"info": "API key is missing."}}
    url = f"https://api.apilayer.com/number_verification/validate?number={phone_number_to_validate}"
    headers = {"apikey": api_key_to_use}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        error_info = f"HTTP error: {http_err}"
        try:
            error_details = response.json()
            if "message" in error_details: error_info += f" - API: {error_details['message']}"
        except json.JSONDecodeError: pass
        return {"success": False, "error": {"info": error_info, "code": response.status_code if response else None}}
    except requests.exceptions.ConnectionError as conn_err:
        return {"success": False, "error": {"info": f"Connection error: {conn_err}"}}
    except requests.exceptions.Timeout as timeout_err:
        return {"success": False, "error": {"info": f"Request timed out: {timeout_err}"}}
    except requests.exceptions.RequestException as req_err:
        return {"success": False, "error": {"info": f"Request error: {req_err}"}}
    except json.JSONDecodeError:
        return {"success": False, "error": {"info": "Failed to decode API JSON response."}}


def print_phone_details(phone_data):
    # (This function is the same as in the previous phone_lookup.py example)
    # (It handles printing details and API errors gracefully)
    if not phone_data: print(Fore.RED + "No data received."); return

    if phone_data.get("success") == False or "error" in phone_data:
        error_message = "API request failed."
        if "error" in phone_data and isinstance(phone_data["error"], dict) and "info" in phone_data["error"]:
            error_message += f" Info: {phone_data['error']['info']}"
        elif "message" in phone_data: error_message += f" Message: {phone_data['message']}"
        print(Fore.RED + error_message)
        # ... (rest of error code specific messages like 101, 210 from previous example) ...
        return

    print(Fore.CYAN + "\n--- Phone Number Details ---")
    is_valid_format = phone_data.get('valid', False)
    print(f"{Fore.GREEN}Number: {Style.RESET_ALL}{phone_data.get('number', 'N/A')}")
    print(f"{Fore.GREEN}Format Valid: {Style.RESET_ALL}{Fore.GREEN if is_valid_format else Fore.RED}{is_valid_format}{Style.RESET_ALL}")
    if is_valid_format:
        print(f"{Fore.GREEN}International Format: {Style.RESET_ALL}{phone_data.get('international_format', 'N/A')}")
        print(f"{Fore.GREEN}Local Format: {Style.RESET_ALL}{phone_data.get('local_format', 'N/A')}")
        print(f"{Fore.GREEN}Country: {Style.RESET_ALL}{phone_data.get('country_name', 'N/A')} ({phone_data.get('country_code', 'N/A')})")
        print(f"{Fore.GREEN}Country Prefix: {Style.RESET_ALL}{phone_data.get('country_prefix', 'N/A')}")
        print(f"{Fore.GREEN}Location: {Style.RESET_ALL}{phone_data.get('location', 'N/A')}")
        print(f"{Fore.GREEN}Carrier: {Style.RESET_ALL}{phone_data.get('carrier', 'N/A')}")
        print(f"{Fore.GREEN}Line Type: {Style.RESET_ALL}{phone_data.get('line_type', 'N/A')}")
    else:
        print(Fore.YELLOW + "Detailed information may not be available for numbers with invalid format.")
    print(Fore.CYAN + "----------------------------")


if __name__ == "__main__":
    print_tool_banner()
    
    # Get and validate API Key
    current_api_key = get_api_key()
    if not current_api_key: # Should be handled by sys.exit in get_api_key if user opts out
        sys.exit(1)

    phone_number_input = input(Fore.MAGENTA + "Enter phone number (with country code, e.g., +1xxxxxxxxxx): " + Style.RESET_ALL).strip()
    if not phone_number_input:
        print(Fore.RED + "No phone number entered. Exiting.")
        sys.exit(1)

    print(Fore.YELLOW + f"\nValidating phone number: {phone_number_input}...")
    details = number_validator(phone_number_input, current_api_key)
    print_phone_details(details)