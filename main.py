import asyncio
import argparse
import os
import logging
from config import DEFAULT_DOMAINS_FILE
from scanner import DomainScanner
from analyzer import AnalystEngine
from reporter import MarkdownReporter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Cybercrime Domain Reconnaissance Tool")
    parser.add_argument("-d", "--domains", help="Path to text file containing domains (one per line)", default=DEFAULT_DOMAINS_FILE)
    parser.add_argument("--dry-run", action="store_true", help="Run a dry-run to test imports without connecting.")
    args = parser.parse_args()

    if args.dry_run:
        logger.info("Dry run successful. Modules loaded.")
        return

    if not os.path.exists(args.domains):
        logger.error(f"Domains file not found: {args.domains}. Please create it and add domains.")
        return

    # Load domains
    with open(args.domains, "r") as f:
        domains = [line.strip() for line in f if line.strip()]

    if not domains:
         logger.warning("Domain list is empty.")
         return

    # Initialize components
    scanner = DomainScanner()
    analyzer = AnalystEngine()
    reporter = MarkdownReporter()

    final_results = []

    # Step 1: Scan
    logger.info("Starting reconnaissance phase...")
    scan_results = await scanner.scan_all(domains)
    
    # Step 2: Analyze
    logger.info("Starting AI analysis phase...")
    for domain, data in scan_results.items():
        analysis_data = analyzer.analyze_domain(data, domain)
        
        final_results.append({
            "domain": domain,
            "data": data,
            "analysis_data": analysis_data
        })
        
    # Step 3: Report
    logger.info("Generating final report...")
    report_path = reporter.generate(final_results)
    
    logger.info(f"Done! Report saved to: {report_path}")

if __name__ == "__main__":
    # Ensure Playwright dependencies exist. We run asyncio.run
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
