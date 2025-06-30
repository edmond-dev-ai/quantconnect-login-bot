import os
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth import stealth_sync

# --- Configuration ---
LOGIN_URL = "https://www.quantconnect.com/login"
# The URL we expect to land on after a successful login.
DASHBOARD_URL = "https://www.quantconnect.com/dashboard"
SCREENSHOT_FILENAME = "login_failure_screenshot.png"

def main():
    """
    Main function to orchestrate the login process using a stealth browser.
    """
    print("--- QuantConnect Auto-Login Script Started (v4 - Stealth Mode) ---")

    email = os.getenv("QC_EMAIL")
    password = os.getenv("QC_PASSWORD")

    if not email or not password:
        print("🛑 ERROR: QC_EMAIL or QC_PASSWORD secrets are not set.")
        sys.exit(1)

    print("✅ Credentials successfully loaded.")

    with sync_playwright() as p:
        # --- THIS IS THE KEY CHANGE ---
        # We are launching a "stealth" version of the browser.
        # This applies patches to evade detection.
        browser = stealth_sync(p.chromium).launch(headless=True)
        page = browser.new_page()

        try:
            print(f"Navigating to login page: {LOGIN_URL}")
            page.goto(LOGIN_URL, wait_until='networkidle', timeout=60000)
            
            print("Waiting for login form to be ready...")
            page.wait_for_selector('input[name="email"]', timeout=30000)
            time.sleep(1)

            print("Entering email...")
            page.locator('input[name="email"]').press_sequentially(email, delay=100)

            print("Entering password...")
            page.locator('input[name="password"]').press_sequentially(password, delay=100)
            
            time.sleep(1) # Final pause

            print("Clicking the 'Sign In' button...")
            page.locator("//button[normalize-space()='Sign In']").click()
            
            # --- NEW VERIFICATION METHOD ---
            # Instead of looking for an element, we wait for the URL to change.
            # This is often more reliable against sites that dynamically load content.
            print(f"Verifying login by waiting for URL to become '{DASHBOARD_URL}'...")
            page.wait_for_url(f"{DASHBOARD_URL}**", timeout=30000) # The ** is a wildcard
            
            print(f"Login successful. Current URL: {page.url}")
            print("\n✅✅✅ Login Successful! Verification complete.")

        except TimeoutError:
            print("\n🛑 ERROR: Login verification failed in Stealth Mode.")
            print(f"The URL did not change to the dashboard in time.")
            
            print(f"📸 Taking a screenshot: {SCREENSHOT_FILENAME}")
            page.screenshot(path=SCREENSHOT_FILENAME)
            print("Screenshot saved. Check the artifacts of the GitHub Actions run.")
            sys.exit(1)
        except Exception as e:
            print(f"\n🛑 An unexpected error occurred: {e}")
            page.screenshot(path=SCREENSHOT_FILENAME)
            print("📸 An unexpected error occurred, taking screenshot.")
            sys.exit(1)
        finally:
            browser.close()
            print("\n--- Script Finished ---")

if __name__ == "__main__":
    main()
