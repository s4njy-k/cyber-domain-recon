# Cybercrime Domain Reconnaissance Tool

An automated web reconnaissance and analysis tool built for cybercrime analysts. The tool takes a list of domains, visits them using masked profiles (emulated devices, rotating proxies), intercepts suspicious downloads or API requests, and securely captures screenshots. 

The collected footprint is then analyzed using Google's Gemini AI to generate a contextual, structured intelligence report targeting threats like Phishing, Online Gambling, and Malware Distribution.

## Setup

1. Assemble your Python environment (Python 3.10+):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Export your Gemini API Key:
   ```bash
   export GOOGLE_API_KEY="AIzaSyCSzhSQlSCo2Dx5svVTu0TUq9VC5ZmZ490"
   ```

3. Configure your proxies (Optional):
   - Edit `config.py` to add your list of proxy endpoints in the `PROXIES` variable.

## Usage

1. Create a `domains.txt` file in the root directory. Add one domain per line:
   ```text
   example.com
   test-phishing-domain.net
   ```

2. Run the main orchestrator:
   ```bash
   python main.py
   ```

3. Review the outputs inside the dynamically generated `reports` folder.
   - The final consolidated report will be stored at `reports/report.md`.
   - Raw screenshots are saved inside `reports/screenshots/`.
