import os
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError, Page

# --- Advanced Stealth Import ---
# This block, based on your research, tries multiple ways to import the stealth
# library, making our script far more resilient to version changes.
try:
    from playwright_stealth import stealth_sync
    print("✅ Stealth library loaded (method 1).")
except ImportError:
    try:
        from playwright_stealth import stealth as stealth_sync
        print("✅ Stealth library loaded (method 2).")
    except ImportError:
        stealth_sync = None
        print("⚠️ Warning: playwright_stealth library not found. Applying manual techniques.")

# --- Configuration ---
LOGIN_URL = "https://www.quantconnect.com/login"
DASHBOARD_URL = "https://www.quantconnect.com/dashboard"
SCREENSHOT_FILENAME = "login_failure_screenshot.png"

def apply_manual_stealth(page: Page):
    """Applies manual JavaScript patches to hide automation signs."""
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3],
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
    """)
    print("✅ Manual stealth techniques applied.")


def main():
    """
    Main function to orchestrate the login process using all our combined techniques.
    """
    print("--- QuantConnect Auto-Login Script Started (v6 - Final) ---")

    email = os.getenv("QC_EMAIL")
    password = os.getenv("QC_PASSWORD")

    if not email or not password:
        print("🛑 ERROR: QC_EMAIL or QC_PASSWORD secrets are not set.")
        sys.exit(1)

    print("✅ Credentials successfully loaded.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        )
        page = context.new_page()

        # Apply stealth using the best available method
        if stealth_sync:
            stealth_sync(page)
        else:
            apply_manual_stealth(page)

        try:
            print(f"Navigating to login page: {LOGIN_URL}")
            page.goto(LOGIN_URL, wait_until='networkidle', timeout=60000)

            print("Waiting for login form to be ready...")
            page.wait_for_selector('input[name="email"]', timeout=30000)
            time.sleep(1)

            print("Entering credentials...")
            page.fill('input[name="email"]', email)
            page.fill('input[name="password"]', password)
            time.sleep(1)

            print("Clicking 'Sign In' button...")
            page.click('//button[normalize-space()="Sign In"]')
            
            print(f"Verifying login by waiting for URL to become '{DASHBOARD_URL}'...")
            page.wait_for_url(f"{DASHBOARD_URL}**", timeout=30000)

            print(f"\n✅✅✅ Login Successful! Final URL: {page.url}")

        except TimeoutError:
            print("\n🛑 ERROR: Login verification failed in Final Stealth Mode.")
            print("The URL did not change to the dashboard in time. This may indicate a CAPTCHA or a final block.")
            
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
