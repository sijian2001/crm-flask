"""
Debug login page structure
"""
from playwright.sync_api import sync_playwright


def debug_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Loading login page...")
        page.goto("http://127.0.0.1:8000/auth/login")
        page.wait_for_load_state('networkidle')

        # Take screenshot
        page.screenshot(path='debug_login.png', full_page=True)
        print("Screenshot saved: debug_login.png")

        # Get all input fields
        print("\n=== All input fields ===")
        inputs = page.locator('input')
        count = inputs.count()
        print(f"Total inputs: {count}")

        for i in range(count):
            inp = inputs.nth(i)
            input_type = inp.get_attribute('type')
            input_name = inp.get_attribute('name')
            input_id = inp.get_attribute('id')
            print(f"{i+1}. type={input_type}, name={input_name}, id={input_id}")

        # Get all buttons
        print("\n=== All buttons ===")
        buttons = page.locator('button, input[type="submit"]')
        count = buttons.count()
        print(f"Total buttons: {count}")

        for i in range(count):
            btn = buttons.nth(i)
            btn_type = btn.get_attribute('type')
            btn_text = btn.text_content()
            print(f"{i+1}. type={btn_type}, text={btn_text}")

        # Get page HTML
        html = page.content()
        with open('debug_login.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\nHTML saved: debug_login.html")

        input("\nPress Enter to close browser...")
        browser.close()


if __name__ == '__main__':
    debug_login()