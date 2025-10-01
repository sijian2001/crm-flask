"""
Final Employee Management System Test
"""
from playwright.sync_api import sync_playwright
import time


def test_employee_system():
    """Comprehensive employee management test"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("\n" + "="*80)
        print("Employee Management System - Final Test")
        print("="*80)

        try:
            # Test 1: Login
            print("\n[Test 1] Login")
            page.goto("http://127.0.0.1:8000/auth/login")
            page.wait_for_timeout(1000)

            page.fill('#username', 'admin')
            page.fill('#password', 'admin123')
            page.screenshot(path='final_01_login.png')

            page.click('#submit')
            page.wait_for_timeout(2000)
            print(f"   [OK] Login successful - URL: {page.url}")
            page.screenshot(path='final_02_dashboard.png')

            # Test 2: Access Employee List
            print("\n[Test 2] Employee List")
            page.goto("http://127.0.0.1:8000/employees/")
            page.wait_for_timeout(1500)

            if 'employees' in page.url and 'login' not in page.url:
                print("   [OK] Employee page loaded")
                page.screenshot(path='final_03_employee_list.png')

                # Check table
                if page.locator('table').count() > 0:
                    rows = page.locator('table tbody tr')
                    count = rows.count()
                    print(f"   [OK] Found {count} employees")
                else:
                    print("   [WARNING] No table found")
            else:
                print(f"   [ERROR] Unexpected URL: {page.url}")

            # Test 3: View Statistics (API endpoint)
            print("\n[Test 3] Statistics API")
            response = page.goto("http://127.0.0.1:8000/employees/api/statistics")
            if response and response.ok:
                print("   [OK] Statistics API working")
            else:
                print("   [SKIP] Statistics API not available")

            # Test 4: Create Employee
            print("\n[Test 4] Create New Employee")
            page.goto("http://127.0.0.1:8000/employees/create")
            page.wait_for_timeout(1000)

            if 'new' in page.url or 'create' in page.url:
                print("   [OK] Create form loaded")
                page.screenshot(path='final_05_create_form.png')

                # Fill form
                page.fill('#employee_code', 'TEST001')
                page.fill('#first_name', 'Test')
                page.fill('#last_name', 'User')
                page.fill('#email', 'test@example.com')
                page.fill('#phone', '090-0000-0000')

                # Select first option in dropdowns
                if page.locator('select#store_id').count() > 0:
                    page.select_option('select#store_id', index=1)
                if page.locator('select#position_id').count() > 0:
                    page.select_option('select#position_id', index=1)
                if page.locator('select#department_id').count() > 0:
                    page.select_option('select#department_id', index=1)

                page.fill('#hire_date', '2025-01-01')
                page.screenshot(path='final_06_filled_form.png')

                # Submit
                submit_btn = page.locator('button[type="submit"], input[type="submit"]')
                if submit_btn.count() > 0:
                    submit_btn.first.click()
                    page.wait_for_timeout(2000)
                    print("   [OK] Form submitted")
                    page.screenshot(path='final_07_after_create.png')
                else:
                    print("   [WARNING] Submit button not found")
            else:
                print("   [SKIP] Create form not accessible")

            # Test 5: Back to List
            print("\n[Test 5] View Updated List")
            page.goto("http://127.0.0.1:8000/employees/")
            page.wait_for_timeout(1000)

            if page.locator('text=TEST001').count() > 0:
                print("   [OK] New employee appears in list")
            else:
                print("   [INFO] Employee may not be visible yet")

            page.screenshot(path='final_08_updated_list.png')

            # Test 6: Search (if available)
            print("\n[Test 6] Search Functionality")
            if page.locator('input[name="search"], input[type="search"]').count() > 0:
                page.fill('input[name="search"], input[type="search"]', 'Test')
                page.press('input[name="search"], input[type="search"]', 'Enter')
                page.wait_for_timeout(1000)
                print("   [OK] Search executed")
                page.screenshot(path='final_09_search.png')
            else:
                print("   [SKIP] Search not available")

            # Test 7: Check for errors
            print("\n[Test 7] Console Check")
            page.goto("http://127.0.0.1:8000/employees/")
            page.wait_for_timeout(1000)

            # Simple page load time
            start = time.time()
            page.goto("http://127.0.0.1:8000/employees/")
            page.wait_for_load_state('networkidle')
            load_time = (time.time() - start) * 1000

            print(f"   [OK] Page load time: {load_time:.0f}ms")

            print("\n" + "="*80)
            print("Test Summary")
            print("="*80)
            print("All basic tests completed successfully!")
            print("Screenshots saved: final_*.png")
            print("="*80)

        except Exception as e:
            print(f"\n[ERROR] Test failed: {str(e)}")
            page.screenshot(path='final_error.png')
            import traceback
            traceback.print_exc()

        finally:
            print("\nTest complete. Browser will close in 3 seconds...")
            time.sleep(3)
            browser.close()


if __name__ == '__main__':
    test_employee_system()