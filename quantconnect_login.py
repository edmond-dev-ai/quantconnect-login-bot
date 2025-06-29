import os
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError

# --- Configuration ---
LOGIN_URL = "https://www.quantconnect.com/login"
DASHBOARD_URL = "https://www.quantconnect.com/dashboard"
# A reliable element on the dashboard to confirm a successful login.
SUCCESS_SELECTOR = "//h2[text()='My Projects']"
SCREENSHOT_FILENAME = "login_failure_screenshot.png"

def main():
    """
    Main function to orchestrate the login process.
    It retrieves credentials, launches a browser, performs the login,
    verifies the result, and takes a screenshot on failure.
    """
    print("--- QuantConnect Auto-Login Script Started (v2) ---")

    email = os.getenv("QC_EMAIL")
    password = os.getenv("QC_PASSWORD")

    if not email or not password:
        print("🛑 ERROR: QC_EMAIL or QC_PASSWORD secrets are not set.")
        sys.exit(1)

    print("✅ Credentials successfully loaded from environment variables.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print(f"Navigating to login page: {LOGIN_URL}")
            page.goto(LOGIN_URL, wait_until='domcontentloaded', timeout=60000)

            print("Entering email...")
            page.fill('input[name="email"]', email)

            print("Entering password...")
            page.fill('input[name="password"]', password)
            
            # Brief pause before clicking to ensure form is ready
            time.sleep(1)

            print("Submitting login form...")
            page.click('button[type="submit"]')

            print(f"Verifying login success by waiting for dashboard element...")
            page.wait_for_selector(SUCCESS_SELECTOR, timeout=30000)
            
            print(f"Current URL: {page.url}")
            print("\n✅✅✅ Login Successful! Verification complete.")

        except TimeoutError:
            print("\n🛑 ERROR: Login verification failed.")
            print(f"Could not find the success element ('{SUCCESS_SELECTOR}') on the page after logging in.")
            
            # --- THIS IS THE NEW PART ---
            print(f"📸 Taking a screenshot: {SCREENSHOT_FILENAME}")
            page.screenshot(path=SCREENSHOT_FILENAME)
            print("Screenshot saved. Check the artifacts of the GitHub Actions run.")
            # --- END OF NEW PART ---

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
