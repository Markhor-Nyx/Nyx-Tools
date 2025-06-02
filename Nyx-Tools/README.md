# NYX TOOLS

**Developed by: Markhor-Nyx**
**Copyright (C) Markhor-Nyx. All rights reserved.**

---

## 📜 Description

NYX TOOLS is a personal, private collection of command-line utilities developed for educational purposes in the field of cybersecurity and ethical hacking. This suite includes a variety of tools designed to assist in learning about network scanning, web reconnaissance, system utilities, and understanding potential security vulnerabilities.

**⚠️ IMPORTANT WARNING & DISCLAIMER ⚠️**

These tools are intended STRICTLY for educational use and for authorized testing on systems and networks where you have explicit, written permission. Unauthorized use of these tools against systems or networks without consent is illegal and unethical. The developer (Markhor-Nyx) assumes NO liability and is NOT responsible for any misuse or damage caused by these tools. You are solely responsible for your actions. Use with extreme caution and adhere to all applicable laws and ethical guidelines.

---

## 🛠️ Tools Included

This suite currently includes the following tools, accessible via the main launcher:

1.  **Subdirectory Scanner:** Discovers hidden subdirectories on a web server.
2.  **Subdomain Scanner:** Enumerates subdomains for a given domain.
3.  **Port Scanner:** Scans for open ports on a target host with threading and basic banner grabbing.
4.  **HTTP Flooder (DDoS Tool):** A utility for testing network/server resilience against HTTP GET/POST floods (Use responsibly).
5.  **Email Bomber:** A tool for sending multiple emails, with threading and HTML support (Use responsibly, avoid spamming).
6.  **Phone Number Validator:** Verifies phone number details using an external API.
7.  **Discord Token Grabber:** Demonstrates how Discord tokens can be potentially extracted (EDUCATIONAL USE ONLY, EXTREME WARNING).
8.  **Discord Nuke Bot:** A powerful tool for Discord server moderation and testing (Node.js based - Use with EXTREME caution and only on servers you own).
    *   _(Aap yahan aur tools add kar sakte hain jab woh `main_launcher.py` mein shamil hon)_

---

## 🚀 Getting Started with NYX TOOLS

Follow these steps to set up and run the NYX TOOLS suite:

**Prerequisites:**

*   **Python:** Version 3.7 or higher is recommended.
*   **Git:** To clone the repository.
*   **Node.js & npm:** Required **only** if you intend to use the "Discord Nuke Bot". LTS version of Node.js is recommended.
*   **pip:** Python package installer (usually comes with Python).

**Setup Instructions:**

1.  **Clone the Repository:**
    Open your terminal or command prompt and clone the private repository:
    ```bash
    git clone https://github.com/Markhor-Nyx/Nyx-Tools.git
    ```
    (You will need appropriate authentication for a private repository).

2.  **Navigate to the Project Directory:**
    ```bash
    cd Nyx-Tools
    ```

3.  **Install Python Dependencies:**
    Install all required Python libraries for the tools using the `requirements.txt` file located in the root directory:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If `pip` refers to Python 2 on your system, try `pip3 install -r requirements.txt`.*

4.  **(Optional) Setup for Discord Nuke Bot (Node.js):**
    If you plan to use the Discord Nuke Bot, you need to install its Node.js dependencies.
    Navigate to its directory and run `npm install`:
    ```bash
    cd discord_nuke_bot
    npm install
    cd .. 
    ```
    (This command should be run from within the `discord_nuke_bot` directory).

**Running the Tools:**

All Python-based tools are accessible through the main launcher script.

1.  **Run the Main Launcher:**
    From the root `Nyx-Tools` directory, execute:
    ```bash
    python main_launcher.py
    ```

2.  **Select a Tool:**
    A menu will appear listing all available tools. Enter the number corresponding to the tool you wish to use and press Enter.

3.  **Follow On-Screen Prompts:**
    Each tool will then guide you with specific prompts for required inputs (e.g., target domain, API keys, email details, etc.).

    *   **API Keys:** Some tools (like Phone Number Validator) require API keys. It's recommended to set these as environment variables or manage them securely. The tool might prompt you if a key is not found. Refer to individual tool notes or code comments for specific API key requirements.
    *   **Sensitive Tools:** Tools like the Discord Token Grabber and Discord Nuke Bot will have additional warnings and confirmation steps due to their sensitive nature. **Proceed with extreme caution and only with proper authorization.**

**Using in Termux (Android):**

The setup process for Termux is similar:

1.  Open Termux and install prerequisites:
    ```bash
    pkg update && pkg upgrade -y
    pkg install git python nodejs-lts -y 
    ```
2.  Clone the repository: `git clone https://github.com/Markhor-Nyx/Nyx-Tools.git`
3.  Navigate to the directory: `cd Nyx-Tools`
4.  Install Python dependencies: `pip install -r requirements.txt`
5.  (Optional) Setup Nuke Bot: `cd discord_nuke_bot && npm install && cd ..`
6.  Run the launcher: `python main_launcher.py`

    *Note: Not all tools (especially those interacting with desktop environments like the Token Grabber) will function identically or at all in Termux as they would on a desktop OS.*

---

## 📝 Notes & Future Development

*   This is an ongoing personal project for learning and development.
*   Future plans include adding more tools and refining existing ones with enhanced features and better error handling.
*   Contributions are not currently sought as this is a private learning repository.

---

**Remember: With great power comes great responsibility. Use these tools wisely and ethically.**