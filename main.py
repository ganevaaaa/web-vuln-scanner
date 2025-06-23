
import argparse
import logging
from scanner import run_scanner

def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(
        description="Web Vulnerability Scanner – Use only on authorized targets."
    )
    parser.add_argument("--url", required=True, help="Start URL to scan")
    parser.add_argument("--max-pages", type=int, default=30, help="Maximum number of pages to crawl")
    parser.add_argument("--i-understand", action="store_true",
                        help="Confirm you have permission to scan the target")

    args = parser.parse_args()

    # Block unauthorized scans
    if "vulnweb.com" not in args.url and not args.i_understand:
        print("❌ You must pass the --i-understand flag to scan non-demo targets.")
        return

    run_scanner(args.url, args.max_pages, confirm=args.i_understand)

if __name__ == "__main__":
    main()
