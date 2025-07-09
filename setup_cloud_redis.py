import time
from playwright.sync_api import sync_playwright, Page, expect
import os

def setup_cloud_redis_from_existing_browser():
    """
    Connects to an existing Chrome instance to automate creating a free Redis database on Upstash.
    """
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            print("--- Successfully connected to the existing browser. ---")
        except Exception as e:
            print(f"--- Error connecting to browser: {e}")
            print("--- Please ensure you have launched Chrome with 'start chrome --remote-debugging-port=9222' ---")
            return

        page.goto("https://console.upstash.com/dashboard")

        # Wait for dashboard to be ready
        page.wait_for_selector("h2:has-text('Databases')", timeout=60000)
        print("--- Upstash dashboard loaded. ---")

        # Check if a database named "mcp-linkedin-dev" already exists
        db_link_selector = "a:has-text('mcp-linkedin-dev')"
        if page.locator(db_link_selector).is_visible():
            print("--- Database 'mcp-linkedin-dev' already exists. Fetching credentials. ---")
            page.locator(db_link_selector).click()
        else:
            print("--- Database not found. Creating a new one... ---")
            page.goto("https://console.upstash.com/redis/create")
            page.wait_for_selector("input#name")

            # Fill in database details
            page.locator("input#name").fill("mcp-linkedin-dev")
            # Select the first free region
            page.locator("[class*='RadioGroupV2_item']").first.click()
            time.sleep(1) # a small wait for UI to update

            print("--- Creating database... ---")
            page.locator("button:has-text('Create Database')").click()

        # Wait for the database details page to load
        page.wait_for_selector("h2:has-text('Details')", timeout=120000)
        print("--- Database created/selected. Extracting credentials... ---")

        # Get credentials using more robust selectors
        endpoint = page.locator("div:has-text('Endpoint') ~ div").inner_text()
        port = page.locator("div:has-text('Port') ~ div").inner_text()
        password = page.locator("div:has-text('Password') ~ div button").get_attribute('data-clipboard-text')

        # If password is not in clipboard attribute, try another way
        if not password:
             page.locator("div:has-text('Password') ~ div button").click()
             # Use JS to read from clipboard as a fallback
             password = page.evaluate("() => navigator.clipboard.readText()")

        print("\n" + "="*80)
        print("--- Redis Credentials Acquired! ---")
        print(f"HOST={endpoint}")
        print(f"PORT={port}")
        print(f"PASSWORD={password}")
        print(f"USERNAME=default")
        print("="*80 + "\n")

        # Save to a .env file
        with open(".env_redis", "w") as f:
            f.write(f"REDIS_HOST={endpoint}\n")
            f.write(f"REDIS_PORT={port}\n")
            f.write(f"REDIS_PASSWORD={password}\n")
            f.write(f"REDIS_USERNAME=default\n")

        print("Credentials saved to .env_redis file.")
        print("You can now close the browser window.")
        # We don't close the browser as we didn't launch it
        # browser.close()

if __name__ == "__main__":
    setup_cloud_redis_from_existing_browser() 