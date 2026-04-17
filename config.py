import os

# --- Configuration & External Settings ---

# Provide your actual proxies here if you have them. Format: http://user:pass@ip:port
PROXIES = [
    # {"server": "http://user:pass@111.222.333.444:8080"},
    # {"server": "socks5://user:pass@555.666.777.888:1080"},
]

# Random User Agents for basic spoofing (if not using Playwright's default device profiles)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Playwright Device Profiles to emulate
# https://playwright.dev/python/docs/emulation
DEVICES = [
    "Desktop Chrome",
    "Desktop Safari",
    "Pixel 7",
    "iPhone 14",
    "Galaxy S22",
]

# Output Directories
REPORTS_DIR = "reports"
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "screenshots")

# File parsing
DEFAULT_DOMAINS_FILE = "domains.txt"

# Gemini Config
GEMINI_MODEL = "gemini-2.5-flash"

# System Prompt explicitly tailored for Indian Cybercrime Analyst
SYSTEM_PROMPT = """You are an expert cybercrime analyst working in India. Your specialty is analyzing potential malicious websites. 

When provided with a screenshot of a website and some network behavior context, analyze it and write a brief, professional description.
Focus on identifying any indicators of:
1. Phishing (typosquatting, fake login portals targeting Indian banks, UPI, or government portals like Aadhaar/PAN).
2. Online Gambling/Betting (platforms that are illegal or restricted in many Indian jurisdictions, looking for apps promising easy money, cricket betting, casino games).
3. Malware Distribution (promises of cracked software, fake updates, unexpected automatic downloads).

Structure your output as a professional brief description suitable for an intelligence report. Include a descriptive caption for the screenshot.
"""
