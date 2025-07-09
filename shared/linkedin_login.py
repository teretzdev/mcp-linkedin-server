import os
import pickle
import time

COOKIE_FILE = os.path.join(os.path.dirname(__file__), '../linkedin_cookies.pkl')

# For Selenium

def save_cookies_selenium(driver, path=COOKIE_FILE):
    with open(path, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookies_selenium(driver, path=COOKIE_FILE):
    with open(path, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

def robust_linkedin_login_selenium(driver):
    driver.get("https://www.linkedin.com/")
    # Try to use cookies if available
    if os.path.exists(COOKIE_FILE):
        load_cookies_selenium(driver, COOKIE_FILE)
        driver.refresh()
        time.sleep(2)
        if "feed" in driver.current_url:
            print("Logged in using cookies!")
            return True
        else:
            print("Cookies found but invalid or expired. Manual login required.")
    else:
        print("No cookie file found. Manual login required.")
    print("Please log in to LinkedIn manually in the opened browser window.")
    print("After you have successfully logged in and see your feed, press Enter here to continue...")
    input()
    if "feed" in driver.current_url:
        save_cookies_selenium(driver, COOKIE_FILE)
        print("Manual login successful, cookies saved.")
        return True
    else:
        print("Manual login failed or not on feed page.")
        try:
            driver.save_screenshot("login_debug.png")
            print("Screenshot saved as login_debug.png")
        except Exception as ss_e:
            print(f"Failed to save screenshot: {ss_e}")
        return False

# For Playwright (async)
import json
from pathlib import Path
import traceback

COOKIE_FILE_PLAYWRIGHT = os.path.join(os.path.dirname(__file__), '../sessions/playwright_cookies.json')

async def save_cookies_playwright(context, path=COOKIE_FILE_PLAYWRIGHT):
    cookies = await context.cookies()
    with open(path, 'w') as f:
        json.dump(cookies, f)

async def load_cookies_playwright(context, path=COOKIE_FILE_PLAYWRIGHT):
    if not os.path.exists(path):
        return False
    with open(path, 'r') as f:
        cookies = json.load(f)
    await context.add_cookies(cookies)
    return True

async def robust_linkedin_login_playwright(context, page):
    # This function had a bug where it was still calling input() causing a crash.
    # This version definitively removes the input() and relies on URL detection.
    print("[LOGIN_DEBUG] Attempting robust login...")
    try:
        cookies_loaded = await load_cookies_playwright(context)
        await page.goto("https://www.linkedin.com/")

        if cookies_loaded:
            print("[LOGIN_DEBUG] Cookies were loaded. Reloading page to apply session.")
            await page.reload()
            if "feed" in page.url:
                print("Logged in using cookies!")
                return True
        
        # If cookies are invalid or not found, proceed with automated login using credentials from .env
        email = os.getenv("LINKEDIN_EMAIL") or os.getenv("LINKEDIN_USERNAME")
        password = os.getenv("LINKEDIN_PASSWORD")
        if not email or not password:
            print("[LOGIN_FATAL] LinkedIn credentials not found in environment variables. Please set LINKEDIN_EMAIL/USERNAME and LINKEDIN_PASSWORD in your .env file.")
            return False
        await page.goto("https://www.linkedin.com/login")
        await page.fill('input[name="session_key"]', email)
        await page.fill('input[name="session_password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(5000)
        if "feed" in page.url:
            print("Automated login successful!")
            await save_cookies_playwright(context)
            return True
        else:
            print("[LOGIN_FATAL] Automated login failed. Check credentials or for LinkedIn blocks.")
            return False

    except Exception as e:
        print(f"[LOGIN_FATAL] A critical error occurred during the login process: {e}")
        traceback.print_exc()
        try:
            await page.screenshot(path="login_debug_fatal.png")
            print("Fatal error screenshot saved as login_debug_fatal.png")
        except Exception as ss_e:
            print(f"Failed to save screenshot during fatal error: {ss_e}")
        return False 