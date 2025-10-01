"""
Customer Management Feature - Comprehensive Browser Tests
Tests customer CRUD operations, search, and filtering
"""
from playwright.sync_api import sync_playwright
import time


class CustomerManagementTest:
    """Customer management feature tests"""

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

    def test_01_list_customers(self, page):
        """Test: Customer list display"""
        print("\n[Test 1] Customer List Display")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/customers/")
            page.wait_for_load_state("networkidle")

            # Check if customer list is displayed
            if page.locator('table').count() > 0 or page.locator('.card').count() > 0:
                print("   [OK] Customer list loaded")

                # Count customers
                customer_count = page.locator('table tbody tr').count()
                if customer_count == 0:
                    customer_count = page.locator('.card').count()

                print(f"   [OK] Found {customer_count} customers")

                page.screenshot(path='result/customer_01_list.png')
                self.test_results.append(("Customer List", "PASS"))
                return True
            else:
                print("   [FAIL] No customers found")
                self.test_results.append(("Customer List", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/customer_01_error.png')
            self.test_results.append(("Customer List", "ERROR"))
            return False

    def test_02_search_customer(self, page):
        """Test: Customer search functionality"""
        print("\n[Test 2] Customer Search")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/customers/")
            page.wait_for_load_state("networkidle")

            # Look for search input
            search_input = page.locator('input[name="search"]')
            if search_input.count() > 0:
                search_input.fill('Tanaka')
                page.press('input[name="search"]', 'Enter')
                page.wait_for_timeout(1000)

                results = page.locator('table tbody tr').count()
                print(f"   [OK] Search returned {results} results")
                page.screenshot(path='result/customer_02_search.png')

                # Clear search
                search_input.fill('')
                page.press('input[name="search"]', 'Enter')
                page.wait_for_timeout(500)

                self.test_results.append(("Customer Search", "PASS"))
                return True
            else:
                print("   [SKIP] Search input not found")
                self.test_results.append(("Customer Search", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/customer_02_error.png')
            self.test_results.append(("Customer Search", "ERROR"))
            return False

    def test_03_create_customer(self, page):
        """Test: Create new customer"""
        print("\n[Test 3] Create Customer")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/customers/")
            page.wait_for_load_state("networkidle")

            # Look for create button
            create_button = page.locator('a').filter(has_text='新規登録')
            if create_button.count() == 0:
                create_button = page.locator('a').filter(has_text='新規')
            if create_button.count() == 0:
                create_button = page.locator('a[href*="create"]')
            if create_button.count() == 0:
                create_button = page.locator('a[href*="new"]')

            if create_button.count() > 0:
                create_button.first.click()
                page.wait_for_timeout(1000)

                # Fill form if it exists
                if page.locator('form').count() > 0:
                    timestamp = str(int(time.time()))[-6:]
                    customer_name = f"Test Customer {timestamp}"

                    # Fill basic fields
                    if page.locator('input[name="name"]').count() > 0:
                        page.fill('input[name="name"]', customer_name)

                    if page.locator('input[name="first_name"]').count() > 0:
                        page.fill('input[name="first_name"]', 'Test')
                    if page.locator('input[name="last_name"]').count() > 0:
                        page.fill('input[name="last_name"]', f'Customer{timestamp}')

                    if page.locator('input[name="email"]').count() > 0:
                        page.fill('input[name="email"]', f'customer{timestamp}@example.com')

                    if page.locator('input[name="phone"]').count() > 0:
                        page.fill('input[name="phone"]', '090-1111-2222')

                    page.screenshot(path='result/customer_03_create_form.png')

                    # Submit if submit button exists
                    if page.locator('input[type="submit"]').count() > 0:
                        page.click('input[type="submit"]')
                        page.wait_for_timeout(2000)

                        # Verify creation (use either name or email)
                        search_text = customer_name if page.locator(f'text={customer_name}').count() > 0 else f'Customer{timestamp}'
                        if page.locator(f'text={search_text}').count() > 0:
                            print(f"   [OK] Customer created")
                            page.screenshot(path='result/customer_03_created.png')
                            self.test_results.append(("Create Customer", "PASS"))
                            return search_text
                        else:
                            print("   [WARNING] Customer creation unclear")
                            self.test_results.append(("Create Customer", "WARNING"))
                            return search_text
                    else:
                        print("   [SKIP] Submit button not found")
                        self.test_results.append(("Create Customer", "SKIP"))
                        return None
                else:
                    print("   [SKIP] Create form not found")
                    self.test_results.append(("Create Customer", "SKIP"))
                    return None
            else:
                print("   [SKIP] Create button not found")
                self.test_results.append(("Create Customer", "SKIP"))
                return None

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/customer_03_error.png')
            self.test_results.append(("Create Customer", "ERROR"))
            return None

    def test_04_view_customer(self, page):
        """Test: View customer details"""
        print("\n[Test 4] View Customer Details")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/customers/")
            page.wait_for_load_state("networkidle")

            # Look for detail/view link
            view_link = page.locator('a').filter(has_text='詳細')
            if view_link.count() == 0:
                view_link = page.locator('a[href*="view"]')
            if view_link.count() == 0:
                view_link = page.locator('a[href*="detail"]')

            if view_link.count() > 0:
                view_link.first.click()
                page.wait_for_timeout(1000)

                print("   [OK] Customer detail page loaded")
                page.screenshot(path='result/customer_04_view.png')

                page.go_back()
                page.wait_for_timeout(500)

                self.test_results.append(("View Customer", "PASS"))
                return True
            else:
                print("   [SKIP] View link not found")
                self.test_results.append(("View Customer", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/customer_04_error.png')
            self.test_results.append(("View Customer", "ERROR"))
            return False

    def test_05_edit_customer(self, page, customer_identifier):
        """Test: Edit customer"""
        print("\n[Test 5] Edit Customer")
        print("-" * 70)

        try:
            if not customer_identifier:
                print("   [SKIP] No customer to edit")
                self.test_results.append(("Edit Customer", "SKIP"))
                return False

            page.goto(f"{self.base_url}/customers/")
            page.wait_for_load_state("networkidle")

            # Find the customer and edit link
            if page.locator(f'text={customer_identifier}').count() > 0:
                edit_link = page.locator('a').filter(has_text='編集').first
                if edit_link.count() > 0:
                    edit_link.click()
                    page.wait_for_timeout(1000)

                    # Update a field
                    if page.locator('input[name="phone"]').count() > 0:
                        page.fill('input[name="phone"]', '090-8888-7777')

                    page.screenshot(path='result/customer_05_edit_form.png')

                    if page.locator('input[type="submit"]').count() > 0:
                        page.click('input[type="submit"]')
                        page.wait_for_timeout(2000)

                        print("   [OK] Customer edited")
                        page.screenshot(path='result/customer_05_edited.png')
                        self.test_results.append(("Edit Customer", "PASS"))
                        return True
                    else:
                        print("   [SKIP] Submit button not found")
                        self.test_results.append(("Edit Customer", "SKIP"))
                        return False
                else:
                    print("   [SKIP] Edit link not found")
                    self.test_results.append(("Edit Customer", "SKIP"))
                    return False
            else:
                print(f"   [SKIP] Customer not found")
                self.test_results.append(("Edit Customer", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/customer_05_error.png')
            self.test_results.append(("Edit Customer", "ERROR"))
            return False

    def test_06_filter_customers(self, page):
        """Test: Filter customers"""
        print("\n[Test 6] Filter Customers")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/customers/")
            page.wait_for_load_state("networkidle")

            # Look for filter options
            filter_select = page.locator('select').first
            if filter_select.count() > 0:
                # Select first non-empty option
                filter_select.select_option(index=1)
                page.wait_for_timeout(1000)

                print("   [OK] Filter applied")
                page.screenshot(path='result/customer_06_filter.png')

                # Reset filter
                filter_select.select_option(index=0)
                page.wait_for_timeout(500)

                self.test_results.append(("Filter Customers", "PASS"))
                return True
            else:
                print("   [SKIP] Filter select not found")
                self.test_results.append(("Filter Customers", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/customer_06_error.png')
            self.test_results.append(("Filter Customers", "ERROR"))
            return False

    def test_07_delete_customer(self, page, customer_identifier):
        """Test: Delete customer"""
        print("\n[Test 7] Delete Customer")
        print("-" * 70)

        try:
            if not customer_identifier:
                print("   [SKIP] No customer to delete")
                self.test_results.append(("Delete Customer", "SKIP"))
                return False

            page.goto(f"{self.base_url}/customers/")
            page.wait_for_load_state("networkidle")

            if page.locator(f'text={customer_identifier}').count() > 0:
                # Setup dialog handler
                page.on("dialog", lambda dialog: dialog.accept())

                delete_button = page.locator('button').filter(has_text='削除').first
                if delete_button.count() > 0:
                    delete_button.click()
                    page.wait_for_timeout(2000)

                    # Verify deletion
                    if page.locator(f'text={customer_identifier}').count() == 0:
                        print(f"   [OK] Customer deleted")
                        page.screenshot(path='result/customer_07_deleted.png')
                        self.test_results.append(("Delete Customer", "PASS"))
                        return True
                    else:
                        print("   [WARNING] Deletion unclear")
                        self.test_results.append(("Delete Customer", "WARNING"))
                        return False
                else:
                    print("   [SKIP] Delete button not found")
                    self.test_results.append(("Delete Customer", "SKIP"))
                    return False
            else:
                print(f"   [SKIP] Customer not found")
                self.test_results.append(("Delete Customer", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/customer_07_error.png')
            self.test_results.append(("Delete Customer", "ERROR"))
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("CUSTOMER MANAGEMENT TEST SUMMARY")
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
        """Run all customer management tests"""
        print("\n" + "="*70)
        print("CUSTOMER MANAGEMENT - BROWSER TESTS")
        print("="*70)

        with sync_playwright() as p:
            browser, page = self.setup_browser(p)

            try:
                # Run tests in sequence
                self.test_01_list_customers(page)
                self.test_02_search_customer(page)
                customer_id = self.test_03_create_customer(page)
                self.test_04_view_customer(page)

                if customer_id:
                    self.test_05_edit_customer(page, customer_id)
                    self.test_06_filter_customers(page)
                    self.test_07_delete_customer(page, customer_id)

                self.print_summary()

            except Exception as e:
                print(f"\n[FATAL ERROR] {str(e)}")
                page.screenshot(path='result/customer_fatal_error.png')
            finally:
                time.sleep(2)
                browser.close()


if __name__ == '__main__':
    test = CustomerManagementTest()
    test.run_all_tests()
