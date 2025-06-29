import os
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError

# --- Configuration ---
LOGIN_URL = "https://www.quantconnect.com/login"
SUCCESS_SELECTOR = "//h2[text()='My Projects']"
SCREENSHOT_FILENAME = "login_failure_screenshot.png"

# --- Human-like Browser Configuration ---
# This mimics a standard Google Chrome browser on a Windows 10 machine.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"

def main():
    """
    Main function to orchestrate the login process with human-like behavior.
    """
    print("--- QuantConnect Auto-Login Script Started (v3 - Human Mode) ---")

    email = os.getenv("QC_EMAIL")
    password = os.getenv("QC_PASSWORD")

    if not email or not password:
        print("🛑 ERROR: QC_EMAIL or QC_PASSWORD secrets are not set.")
        sys.exit(1)

    print("✅ Credentials successfully loaded.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a new browser context with our custom user agent
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        try:
            print(f"Navigating to login page: {LOGIN_URL}")
            page.goto(LOGIN_URL, wait_until='networkidle', timeout=60000)

            # --- More Human-like Interaction ---
            print("Waiting for login form to be ready...")
            # Wait for the email field to ensure the page is fully loaded.
            page.wait_for_selector('input[name="email"]', timeout=30000)
            time.sleep(1) # A brief pause, like a human would take.

            print("Entering email slowly...")
            page.locator('input[name="email"]').press_sequentially(email, delay=50) # Types like a human

            print("Entering password slowly...")
            page.locator('input[name="password"]').press_sequentially(password, delay=50)

            time.sleep(0.5) # Pause before clicking

            print("Clicking the 'Sign In' button...")
            # Use a more specific selector for the button.
            page.locator("//button[normalize-space()='Sign In']").click()
            
            # --- Verification ---
            print("Verifying login success...")
            page.wait_for_selector(SUCCESS_SELECTOR, timeout=30000)
            
            print(f"Login successful. Current URL: {page.url}")
            print("\n✅✅✅ Login Successful! Verification complete.")

        except TimeoutError:
            print("\n🛑 ERROR: Login verification failed after human-like attempt.")
            print(f"Could not find success element ('{SUCCESS_SELECTOR}') or another element timed out.")
            
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
