import asyncio
import os
import random
import logging
from playwright.async_api import async_playwright, Download
from config import PROXIES, DEVICES, SCREENSHOTS_DIR

logger = logging.getLogger(__name__)

class DomainScanner:
    def __init__(self):
        self.results = {}
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    async def scan_domain(self, domain: str, pContext):
        """Scans a single domain."""
        url = domain if domain.startswith("http") else f"https://{domain}"
        domain_name = url.replace("https://", "").replace("http://", "").split("/")[0]
        
        # Select random proxy and device profile
        proxy = random.choice(PROXIES) if PROXIES else None
        device_name = random.choice(DEVICES)
        device = pContext.devices[device_name]
        
        logger.info(f"Scanning {url} using {device_name}")
        
        context_args = {**device}
        if proxy:
             context_args["proxy"] = proxy

        context = await pContext.chromium.launch_persistent_context(
            user_data_dir=os.path.join(SCREENSHOTS_DIR, f".tmp_{domain_name}"),
            **context_args,
            accept_downloads=True
        )

        downloads = []
        suspicious_requests = []

        # Listeners
        context.on("download", lambda d: downloads.append(d))
        
        page = await context.new_page()

        def request_handler(request):
            url = request.url.lower()
            if any(ext in url for ext in ['.exe', '.apk', '.bat', '.ps1', '.sh', '.bin']):
                suspicious_requests.append(url)

        page.on("request", request_handler)

        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{domain_name}.png")
        
        error = None
        try:
            # Short timeout to avoid hanging on dead sites
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            # Additional small wait to let dynamic content / downloads trigger
            await asyncio.sleep(3)
            
            await page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            error = str(e)
            logger.error(f"Error scanning {url}: {error}")
        finally:
            await context.close()

        # Clean up tmp profile
        try:
             import shutil
             shutil.rmtree(os.path.join(SCREENSHOTS_DIR, f".tmp_{domain_name}"), ignore_errors=True)
        except:
             pass

        download_urls = [d.url for d in downloads] if downloads else []

        self.results[domain_name] = {
            "url": url,
            "device_emulated": device_name,
            "proxy_used": proxy["server"] if proxy else "None",
            "screenshot_path": screenshot_path if not error else None,
            "downloads_detected": download_urls,
            "suspicious_requests": suspicious_requests,
            "error": error
        }
        return self.results[domain_name]

    async def scan_all(self, domains: list[str]):
        """Scans a list of domains concurrently."""
        logger.info(f"Starting scan for {len(domains)} domains...")
        async with async_playwright() as p:
            # We run sequentially here or in limited batches depending on needs.
            # To avoid overloading local CPU/Memory, doing it one by one in this MVP.
            for domain in domains:
                await self.scan_domain(domain, p)
        return self.results
