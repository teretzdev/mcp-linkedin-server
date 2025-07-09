import argparse
import sys
import asyncio
from linkedin_browser_mcp import main as mcp_main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Phase 1: LinkedIn Job Scraping (one-command entry point)")
    parser.add_argument("--query", type=str, required=True, help="Job search query.")
    parser.add_argument("--location", type=str, default="", help="Job location.")
    parser.add_argument("--count", type=int, default=10, help="Number of jobs to scrape.")
    parser.add_argument("--email", type=str, default=None, help="LinkedIn email/username (optional, overrides env)")
    parser.add_argument("--password", type=str, default=None, help="LinkedIn password (optional, overrides env)")
    parser.add_argument('--headless', action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    # Patch args for linkedin_browser_mcp.py main()
    class Args:
        pass
    mcp_args = Args()
    mcp_args.query = args.query
    mcp_args.location = args.location
    mcp_args.count = args.count
    mcp_args.email = args.email
    mcp_args.password = args.password
    mcp_args.headless = args.headless
    mcp_args.source = 'phase1_script'

    # Ensure credentials are present
    import os
    email = mcp_args.email or os.getenv("LINKEDIN_EMAIL") or os.getenv("LINKEDIN_USERNAME")
    password = mcp_args.password or os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        print("[PHASE1_FATAL] LinkedIn credentials not found in arguments or environment. Please set LINKEDIN_EMAIL/USERNAME and LINKEDIN_PASSWORD in your .env file or pass as arguments.", file=sys.stderr)
        sys.exit(1)

    print(f"[PHASE1] Starting Phase 1 job scraping with: query={args.query}, location={args.location}, count={args.count}")
    try:
        asyncio.run(mcp_main(mcp_args))
    except Exception as e:
        print(f"[PHASE1] Phase 1 failed: {e}", file=sys.stderr)
        sys.exit(1)
    print("[PHASE1] Phase 1 completed.") 