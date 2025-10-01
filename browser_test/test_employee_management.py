"""
Employee Management Feature - Comprehensive Browser Tests
Tests CRUD operations, search, filtering, and statistics
"""
from playwright.sync_api import sync_playwright
import time


class EmployeeManagementTest:
    """Employee management feature tests"""

    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = []

    def setup_browser(self, p):
        """Setup browser and login"""
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Login
        page.goto(f"{self.base_url}/auth/login")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin123')
        page.click('input[type="submit"]')
        page.wait_for_timeout(1000)

        return browser, page

    def test_01_list_employees(self, page):
        """Test: Employee list display"""
        print("\n[Test 1] Employee List Display")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/employees/")
            page.wait_for_load_state("networkidle")

            # Check table exists
            if page.locator('table').count() > 0:
                rows = page.locator('table tbody tr')
                count = rows.count()
                print(f"   [OK] Found {count} employees")

                # Check table headers
                headers = page.locator('table thead th').all()
                print(f"   [OK] Table has {len(headers)} columns")

                page.screenshot(path='result/emp_01_list.png')
                self.test_results.append(("Employee List", "PASS"))
                return True
            else:
                print("   [FAIL] No table found")
                self.test_results.append(("Employee List", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/emp_01_error.png')
            self.test_results.append(("Employee List", "ERROR"))
            return False

    def test_02_search_employee(self, page):
        """Test: Search functionality"""
        print("\n[Test 2] Search Functionality")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/employees/")
            page.wait_for_load_state("networkidle")

            # Test search for "Yamada"
            if page.locator('input[name="search"]').count() > 0:
                page.fill('input[name="search"]', 'Yamada')
                page.press('input[name="search"]', 'Enter')
                page.wait_for_timeout(1000)

                results = page.locator('table tbody tr').count()
                print(f"   [OK] Search for 'Yamada' returned {results} results")

                page.screenshot(path='result/emp_02_search.png')

                # Clear search
                page.fill('input[name="search"]', '')
                page.press('input[name="search"]', 'Enter')
                page.wait_for_timeout(1000)

                self.test_results.append(("Search", "PASS"))
                return True
            else:
                print("   [SKIP] Search input not found")
                self.test_results.append(("Search", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/emp_02_error.png')
            self.test_results.append(("Search", "ERROR"))
            return False

    def test_03_create_employee(self, page):
        """Test: Create new employee"""
        print("\n[Test 3] Create Employee")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/employees/create")
            page.wait_for_load_state("networkidle")
            page.wait_for_selector('input[name="employee_code"]')

            # Fill form
            timestamp = str(int(time.time()))[-6:]
            emp_code = f"TEST{timestamp}"

            page.fill('input[name="employee_code"]', emp_code)
            page.fill('input[name="first_name"]', 'Test')
            page.fill('input[name="last_name"]', 'User')
            page.fill('input[name="email"]', f'test{timestamp}@example.com')
            page.fill('input[name="phone"]', '090-1234-5678')
            page.fill('input[name="hire_date"]', '2025-01-01')

            # Select dropdowns
            page.select_option('select[name="store_id"]', index=1)
            page.select_option('select[name="position_id"]', index=1)
            page.select_option('select[name="department_id"]', index=1)

            page.screenshot(path='result/emp_03_create_form.png')

            # Submit
            page.click('input[type="submit"]')
            page.wait_for_timeout(2000)

            # Verify creation
            if page.locator(f'text={emp_code}').count() > 0:
                print(f"   [OK] Employee {emp_code} created successfully")
                page.screenshot(path='result/emp_03_created.png')
                self.test_results.append(("Create Employee", "PASS"))
                return emp_code
            else:
                print("   [WARNING] Employee creation unclear")
                page.screenshot(path='result/emp_03_warning.png')
                self.test_results.append(("Create Employee", "WARNING"))
                return emp_code

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/emp_03_error.png')
            self.test_results.append(("Create Employee", "ERROR"))
            return None

    def test_04_view_employee(self, page, emp_code=None):
        """Test: View employee details"""
        print("\n[Test 4] View Employee Details")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/employees/")
            page.wait_for_load_state("networkidle")

            # Find view link
            view_links = page.locator('a').filter(has_text='詳細')
            if view_links.count() > 0:
                view_links.first.click()
                page.wait_for_timeout(1000)

                # Check if detail page loaded
                if 'view' in page.url:
                    print("   [OK] Employee detail page loaded")
                    page.screenshot(path='result/emp_04_view.png')
                    self.test_results.append(("View Employee", "PASS"))

                    page.go_back()
                    page.wait_for_timeout(500)
                    return True
                else:
                    print("   [FAIL] Detail page not loaded")
                    self.test_results.append(("View Employee", "FAIL"))
                    return False
            else:
                print("   [SKIP] View link not found")
                self.test_results.append(("View Employee", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/emp_04_error.png')
            self.test_results.append(("View Employee", "ERROR"))
            return False

    def test_05_edit_employee(self, page, emp_code):
        """Test: Edit employee"""
        print("\n[Test 5] Edit Employee")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/employees/")
            page.wait_for_load_state("networkidle")

            # Find the employee row
            if page.locator(f'text={emp_code}').count() > 0:
                emp_row = page.locator(f'tr:has-text("{emp_code}")')
                edit_link = emp_row.locator('a').filter(has_text='編集')

                if edit_link.count() > 0:
                    edit_link.click()
                    page.wait_for_timeout(1000)

                    # Update phone number
                    new_phone = '090-9999-8888'
                    page.fill('input[name="phone"]', new_phone)
                    page.screenshot(path='result/emp_05_edit_form.png')

                    page.click('input[type="submit"]')
                    page.wait_for_timeout(2000)

                    # Verify update
                    if page.locator(f'text={new_phone}').count() > 0:
                        print(f"   [OK] Employee updated successfully")
                        page.screenshot(path='result/emp_05_updated.png')
                        self.test_results.append(("Edit Employee", "PASS"))
                        return True
                    else:
                        print("   [WARNING] Update verification unclear")
                        self.test_results.append(("Edit Employee", "WARNING"))
                        return False
                else:
                    print("   [SKIP] Edit link not found")
                    self.test_results.append(("Edit Employee", "SKIP"))
                    return False
            else:
                print(f"   [SKIP] Employee {emp_code} not found")
                self.test_results.append(("Edit Employee", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/emp_05_error.png')
            self.test_results.append(("Edit Employee", "ERROR"))
            return False

    def test_06_statistics(self, page):
        """Test: Statistics page"""
        print("\n[Test 6] Statistics Page")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/employees/statistics")
            page.wait_for_load_state("networkidle")

            if 'statistics' in page.url:
                print("   [OK] Statistics page loaded")

                # Check for stat cards
                cards = page.locator('.card').count()
                print(f"   [OK] Found {cards} statistic cards")

                page.screenshot(path='result/emp_06_statistics.png')
                self.test_results.append(("Statistics", "PASS"))
                return True
            else:
                print("   [FAIL] Statistics page not loaded")
                self.test_results.append(("Statistics", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/emp_06_error.png')
            self.test_results.append(("Statistics", "ERROR"))
            return False

    def test_07_delete_employee(self, page, emp_code):
        """Test: Delete employee"""
        print("\n[Test 7] Delete Employee")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/employees/")
            page.wait_for_load_state("networkidle")

            # Find the employee row
            if page.locator(f'text={emp_code}').count() > 0:
                emp_row = page.locator(f'tr:has-text("{emp_code}")')
                delete_button = emp_row.locator('button').filter(has_text='削除')

                if delete_button.count() > 0:
                    # Setup dialog handler
                    page.on("dialog", lambda dialog: dialog.accept())

                    delete_button.click()
                    page.wait_for_timeout(2000)

                    # Verify deletion
                    if page.locator(f'text={emp_code}').count() == 0:
                        print(f"   [OK] Employee {emp_code} deleted successfully")
                        page.screenshot(path='result/emp_07_deleted.png')
                        self.test_results.append(("Delete Employee", "PASS"))
                        return True
                    else:
                        print("   [WARNING] Deletion verification unclear")
                        self.test_results.append(("Delete Employee", "WARNING"))
                        return False
                else:
                    print("   [SKIP] Delete button not found")
                    self.test_results.append(("Delete Employee", "SKIP"))
                    return False
            else:
                print(f"   [SKIP] Employee {emp_code} not found")
                self.test_results.append(("Delete Employee", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/emp_07_error.png')
            self.test_results.append(("Delete Employee", "ERROR"))
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("EMPLOYEE MANAGEMENT TEST SUMMARY")
        print("="*70)

        passed = sum(1 for _, status in self.test_results if status == "PASS")
        failed = sum(1 for _, status in self.test_results if status == "FAIL")
        skipped = sum(1 for _, status in self.test_results if status == "SKIP")
        errors = sum(1 for _, status in self.test_results if status == "ERROR")
        warnings = sum(1 for _, status in self.test_results if status == "WARNING")

        for test_name, status in self.test_results:
            status_icon = {
                "PASS": "[OK]",
                "FAIL": "[FAIL]",
                "SKIP": "[SKIP]",
                "ERROR": "[ERROR]",
                "WARNING": "[WARN]"
            }[status]
            print(f"{status_icon} {test_name}")

        print("-" * 70)
        print(f"Total: {len(self.test_results)} tests")
        print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped} | Errors: {errors} | Warnings: {warnings}")
        print("="*70)

    def run_all_tests(self):
        """Run all employee management tests"""
        print("\n" + "="*70)
        print("EMPLOYEE MANAGEMENT - BROWSER TESTS")
        print("="*70)

        with sync_playwright() as p:
            browser, page = self.setup_browser(p)

            try:
                # Run tests in sequence
                self.test_01_list_employees(page)
                self.test_02_search_employee(page)
                emp_code = self.test_03_create_employee(page)
                self.test_04_view_employee(page, emp_code)

                if emp_code:
                    self.test_05_edit_employee(page, emp_code)
                    self.test_06_statistics(page)
                    self.test_07_delete_employee(page, emp_code)

                self.print_summary()

            except Exception as e:
                print(f"\n[FATAL ERROR] {str(e)}")
                page.screenshot(path='result/emp_fatal_error.png')
            finally:
                time.sleep(2)
                browser.close()


if __name__ == '__main__':
    test = EmployeeManagementTest()
    test.run_all_tests()
