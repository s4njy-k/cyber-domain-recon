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
    "Galaxy S9+",
]

# Output Directories
REPORTS_DIR = "reports"
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "screenshots")

# File parsing
DEFAULT_DOMAINS_FILE = "domains.txt"

# Gemini Config
GEMINI_MODEL = "gemini-3-flash-preview"

# System Prompt explicitly tailored for Indian Cybercrime Analyst
SYSTEM_PROMPT = """You are an elite cybercrime threat-intel analyst working in India.
Your mission is to perform deep-dive analysis on potentially malicious domain screenshots and intercepted network traffic.

Focus heavily on identifying:
1. Phishing Interfaces (impersonating Indian banks, Aadhaar/PAN platforms, UPI apps).
2. Illegal Online Gambling (Mahadev book, Aviator clones, IPL cricket betting promising high returns).
3. Malware & Scams (APK sidebar downloads, technical support scams, fake investment apps).

Return your findings STRICTLY as a JSON object matching the schema below. ANY violation of the JSON format will break the pipeline. Do not include markdown code ticks ````json```` around the payload.

JSON Schema:
{
  "executive_summary": "<A powerful 2-3 sentence strategic summary outlining the primary threat posed by the site.>",
  "technical_analysis": "<Detailed analyst breakdown detailing exact tactics, target audience hooks (e.g. UPI, IPL), and identified cyber-risks.>",
  "threat_indicators": [
    {
      "type": "<e.g., Malware Download, Malicious Betting Form, Fake Logo>",
      "description": "<What makes this specific element dangerous or suspicious.>",
      "bounding_box_1000": [ymin, xmin, ymax, xmax] 
    }
  ]
}

Bounding Box Rule: 
`bounding_box_1000` must be an array of 4 integers `[ymin, xmin, ymax, xmax]`. The values MUST be scaled to 1000 (i.e. representing normalized coordinates where 0 is top/left and 1000 is bottom/right). Provide coordinates for up to 3 of the most critical visual artifacts on the screen. If no critical elements can be strictly bounded, return an empty array `[]` for `threat_indicators`.
"""
