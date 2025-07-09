import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
import json
import os
from dotenv import load_dotenv
import pickle

# Load credentials from .env or .env.alt.txt
env_loaded = False
if os.path.exists('.env'):
    load_dotenv('.env')
    print('Loaded environment variables from .env')
    env_loaded = True
elif os.path.exists('.env.alt.txt'):
    load_dotenv('.env.alt.txt')
    print('Loaded environment variables from .env.alt.txt')
    env_loaded = True
else:
    print('WARNING: No .env or .env.alt.txt file found!')

EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
print(f"Loaded EMAIL from env: {EMAIL}")
print(f"Loaded PASSWORD from env: {'*' * len(PASSWORD) if PASSWORD else None}")

# Load job preferences
with open("job_preferences.json", "r") as f:
    preferences = json.load(f)

COOKIE_FILE = "linkedin_cookies.pkl"

def save_cookies(driver, path):
    with open(path, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookies(driver, path):
    with open(path, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

def human_delay(a=0.5, b=1.5):
    time.sleep(random.uniform(a, b))

def login_linkedin(driver):
    driver.get("https://www.linkedin.com/")
    # Try to use cookies if available
    if os.path.exists(COOKIE_FILE):
        load_cookies(driver, COOKIE_FILE)
        driver.refresh()
        human_delay(2, 4)
        # Check if cookies are valid (i.e., we are on the feed page)
        if "feed" in driver.current_url:
            print("Logged in using cookies!")
            return True
        else:
            print("Cookies found but invalid or expired. Manual login required.")
    else:
        print("No cookie file found. Manual login required.")
    # Only reach here if cookies are missing or invalid
    email = os.getenv("LINKEDIN_EMAIL") or os.getenv("LINKEDIN_USERNAME")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        print("[LOGIN_FATAL] LinkedIn credentials not found in environment variables. Please set LINKEDIN_EMAIL/USERNAME and LINKEDIN_PASSWORD in your .env file.")
        return False
    driver.get("https://www.linkedin.com/login")
    driver.find_element_by_name("session_key").send_keys(email)
    driver.find_element_by_name("session_password").send_keys(password)
    driver.find_element_by_xpath('//button[@type="submit"]').click()
    human_delay(5, 7)
    if "feed" in driver.current_url:
        save_cookies(driver, COOKIE_FILE)
        print("Automated login successful, cookies saved.")
        return True
    else:
        print("[LOGIN_FATAL] Automated login failed. Check credentials or for LinkedIn blocks.")
        try:
            driver.save_screenshot("login_debug.png")
            print("Screenshot saved as login_debug.png")
        except Exception as ss_e:
            print(f"Failed to save screenshot: {ss_e}")
        return False

def search_jobs(driver, preferences):
    keywords = preferences.get("keywords", [])
    location = preferences.get("location", "Remote")
    # Build search URL
    search_query = "%20".join(keywords)
    url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location={location}"
    driver.get(url)
    human_delay(3, 5)
    print(f"Searching jobs with: {keywords} in {location}")
    # You can expand this to filter by experience, job type, etc.

def apply_to_easy_apply_jobs(driver):
    try:
        # Find all job cards on the page
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'div.job-card-container, li.jobs-search-results__list-item')
        if not job_cards:
            print("No job cards found on the page.")
            return
        applied_count = 0
        for idx, card in enumerate(job_cards):
            try:
                # Try to extract job title and company
                title = "Unknown Title"
                company = "Unknown Company"
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, 'h3, .job-card-list__title, .job-card-container__link')
                    title = title_elem.text.strip()
                except Exception:
                    pass
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, '.job-card-container__company-name, .job-card-list__company-name')
                    company = company_elem.text.strip()
                except Exception:
                    pass
                print(f"Job #{idx+1}: {title} at {company}")
                # Look for Easy Apply button within the card
                easy_apply_btn = None
                try:
                    easy_apply_btn = card.find_element(By.XPATH, ".//button[contains(@class, 'jobs-apply-button')]")
                except Exception:
                    print(f"  No Easy Apply button found for this job.")
                    continue
                # Scroll button into view and check interactability
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", easy_apply_btn)
                human_delay(0.5, 1.2)
                if easy_apply_btn.is_displayed() and easy_apply_btn.is_enabled():
                    easy_apply_btn.click()
                    print(f"  Clicked Easy Apply for: {title} at {company}")
                    human_delay(2, 3)
                    # Wait for modal to appear
                    try:
                        modal = driver.find_element(By.XPATH, "//div[contains(@role, 'dialog') and contains(@class, 'jobs-easy-apply-modal')]")
                        print(f"  Easy Apply modal appeared for: {title}")
                        # For now, just close the modal
                        try:
                            close_btn = modal.find_element(By.XPATH, ".//button[contains(@aria-label, 'Dismiss') or contains(@aria-label, 'Close')]")
                            close_btn.click()
                            print(f"  Closed modal for: {title}")
                        except Exception as close_e:
                            print(f"  Could not close modal for: {title}: {close_e}")
                        human_delay(1, 2)
                        applied_count += 1
                    except Exception:
                        print(f"  Easy Apply modal did not appear for: {title}")
                else:
                    print(f"  Easy Apply button not interactable for: {title}")
            except Exception as e:
                print(f"Error processing job card #{idx+1}: {e}")
                continue
        if applied_count == 0:
            print("No Easy Apply jobs were found or applied to on this page.")
        else:
            print(f"Applied to {applied_count} Easy Apply job(s) on this page.")
    except Exception as e:
        print(f"Error in apply_to_easy_apply_jobs: {e}")

def main():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    try:
        if not login_linkedin(driver):
            print("Exiting: Could not log in.")
            return
        search_jobs(driver, preferences)
        apply_to_easy_apply_jobs(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 