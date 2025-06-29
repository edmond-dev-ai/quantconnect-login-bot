import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError

# --- Configuration ---
# The target URL for the QuantConnect login page.
LOGIN_URL = "https://www.quantconnect.com/login"
# The URL to verify a successful login. We expect to be redirected here.
DASHBOARD_URL = "https://www.quantconnect.com/dashboard"
# A specific, reliable element on the dashboard to confirm we've logged in.
# This XPath looks for a main heading with the text "My Projects".
SUCCESS_SELECTOR = "//h2[text()='My Projects']"

def main():
    """
    Main function to orchestrate the login process.
    It retrieves credentials, launches a browser, performs the login,
    and verifies the result.
    """
    print("--- QuantConnect Auto-Login Script Started ---")

    # --- 1. Retrieve Credentials from Environment Variables ---
    # This is the secure way to handle secrets in GitHub Actions.
    email = os.getenv("QC_EMAIL")
    password = os.getenv("QC_PASSWORD")

    if not email or not password:
        print("🛑 ERROR: QC_EMAIL or QC_PASSWORD secrets are not set.")
        print("Please configure them in your GitHub repository settings.")
        # Exit with a non-zero status code to indicate failure.
        sys.exit(1)

    print("✅ Credentials successfully loaded from environment variables.")

    # --- 2. Launch Browser and Automate Login ---
    with sync_playwright() as p:
        try:
            # We use Chromium, which is efficient for headless operations.
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print(f"Navigating to login page: {LOGIN_URL}")
            page.goto(LOGIN_URL, wait_until='domcontentloaded', timeout=60000)

            # --- Fill and submit the login form ---
            print("Entering email...")
            page.fill('input[name="email"]', email)

            print("Entering password...")
            page.fill('input[name="password"]', password)
            
            print("Submitting login form...")
            # We click the login button and wait for the navigation to the next page.
            page.click('button[type="submit"]')

            # --- 3. Verify Successful Login ---
            print(f"Verifying login success by waiting for dashboard element: '{SUCCESS_SELECTOR}'")
            # Wait for the success element to appear on the page.
            # If this fails, it will raise a TimeoutError.
            page.wait_for_selector(SUCCESS_SELECTOR, timeout=30000)

            # Extra verification: check if the current URL is the dashboard.
            if DASHBOARD_URL not in page.url:
                 print(f"⚠️ WARNING: Page URL is '{page.url}', not the expected '{DASHBOARD_URL}'.")
                 print("However, the success selector was found, so we will consider this a success.")

            print("\n✅✅✅ Login Successful! Verification complete.")

        except TimeoutError:
            print("\n🛑 ERROR: Login verification failed.")
            print(f"Could not find the success element ('{SUCCESS_SELECTOR}') on the page after logging in.")
            print("This could be due to incorrect credentials, a change in the website's layout, or a network issue.")
            sys.exit(1)
        except Exception as e:
            print(f"\n🛑 An unexpected error occurred: {e}")
            sys.exit(1)
        finally:
            if 'browser' in locals() and browser.is_connected():
                browser.close()
            print("\n--- Script Finished ---")


if __name__ == "__main__":
    main()
