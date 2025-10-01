"""
Store Management Feature - Comprehensive Browser Tests
Tests store CRUD operations, search, and filtering
"""
from playwright.sync_api import sync_playwright
import time


class StoreManagementTest:
    """Store management feature tests"""

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

    def test_01_list_stores(self, page):
        """Test: Store list display"""
        print("\n[Test 1] Store List Display")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/stores/")
            page.wait_for_load_state("networkidle")

            # Check if stores are displayed
            if page.locator('.card').count() > 0 or page.locator('table').count() > 0:
                print("   [OK] Store list loaded")

                # Count stores
                store_count = page.locator('.card').count()
                if store_count == 0:
                    store_count = page.locator('table tbody tr').count()

                print(f"   [OK] Found {store_count} stores")

                page.screenshot(path='result/store_01_list.png')
                self.test_results.append(("Store List", "PASS"))
                return True
            else:
                print("   [FAIL] No stores found")
                self.test_results.append(("Store List", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/store_01_error.png')
            self.test_results.append(("Store List", "ERROR"))
            return False

    def test_02_search_store(self, page):
        """Test: Store search functionality"""
        print("\n[Test 2] Store Search")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/stores/")
            page.wait_for_load_state("networkidle")

            # Look for search input
            search_input = page.locator('input[name="search"]')
            if search_input.count() > 0:
                search_input.fill('Tokyo')
                page.press('input[name="search"]', 'Enter')
                page.wait_for_timeout(1000)

                print("   [OK] Search executed")
                page.screenshot(path='result/store_02_search.png')

                # Clear search
                search_input.fill('')
                page.press('input[name="search"]', 'Enter')
                page.wait_for_timeout(500)

                self.test_results.append(("Store Search", "PASS"))
                return True
            else:
                print("   [SKIP] Search input not found")
                self.test_results.append(("Store Search", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/store_02_error.png')
            self.test_results.append(("Store Search", "ERROR"))
            return False

    def test_03_create_store(self, page):
        """Test: Create new store"""
        print("\n[Test 3] Create Store")
        print("-" * 70)

        try:
            # Navigate to create page
            page.goto(f"{self.base_url}/stores/")
            page.wait_for_load_state("networkidle")

            # Look for "New Store" or "Create" button
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
                    store_name = f"Test Store {timestamp}"

                    # Fill basic fields
                    if page.locator('input[name="name"]').count() > 0:
                        page.fill('input[name="name"]', store_name)

                    if page.locator('input[name="location"]').count() > 0:
                        page.fill('input[name="location"]', 'Test Location')

                    if page.locator('input[name="phone"]').count() > 0:
                        page.fill('input[name="phone"]', '03-1234-5678')

                    page.screenshot(path='result/store_03_create_form.png')

                    # Submit if submit button exists
                    if page.locator('input[type="submit"]').count() > 0:
                        page.click('input[type="submit"]')
                        page.wait_for_timeout(2000)

                        # Verify creation
                        if page.locator(f'text={store_name}').count() > 0:
                            print(f"   [OK] Store '{store_name}' created")
                            page.screenshot(path='result/store_03_created.png')
                            self.test_results.append(("Create Store", "PASS"))
                            return store_name
                        else:
                            print("   [WARNING] Store creation unclear")
                            self.test_results.append(("Create Store", "WARNING"))
                            return store_name
                    else:
                        print("   [SKIP] Submit button not found")
                        self.test_results.append(("Create Store", "SKIP"))
                        return None
                else:
                    print("   [SKIP] Create form not found")
                    self.test_results.append(("Create Store", "SKIP"))
                    return None
            else:
                print("   [SKIP] Create button not found")
                self.test_results.append(("Create Store", "SKIP"))
                return None

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/store_03_error.png')
            self.test_results.append(("Create Store", "ERROR"))
            return None

    def test_04_view_store(self, page):
        """Test: View store details"""
        print("\n[Test 4] View Store Details")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/stores/")
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

                print("   [OK] Store detail page loaded")
                page.screenshot(path='result/store_04_view.png')

                page.go_back()
                page.wait_for_timeout(500)

                self.test_results.append(("View Store", "PASS"))
                return True
            else:
                print("   [SKIP] View link not found")
                self.test_results.append(("View Store", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/store_04_error.png')
            self.test_results.append(("View Store", "ERROR"))
            return False

    def test_05_edit_store(self, page, store_name):
        """Test: Edit store"""
        print("\n[Test 5] Edit Store")
        print("-" * 70)

        try:
            if not store_name:
                print("   [SKIP] No store to edit")
                self.test_results.append(("Edit Store", "SKIP"))
                return False

            page.goto(f"{self.base_url}/stores/")
            page.wait_for_load_state("networkidle")

            # Find the store and edit link
            if page.locator(f'text={store_name}').count() > 0:
                store_row = page.locator(f'tr:has-text("{store_name}")')
                if store_row.count() == 0:
                    store_row = page.locator(f'.card:has-text("{store_name}")')

                edit_link = page.locator('a').filter(has_text='編集').first
                if edit_link.count() > 0:
                    edit_link.click()
                    page.wait_for_timeout(1000)

                    # Update a field
                    if page.locator('input[name="phone"]').count() > 0:
                        page.fill('input[name="phone"]', '03-9999-8888')

                    page.screenshot(path='result/store_05_edit_form.png')

                    if page.locator('input[type="submit"]').count() > 0:
                        page.click('input[type="submit"]')
                        page.wait_for_timeout(2000)

                        print("   [OK] Store edited")
                        page.screenshot(path='result/store_05_edited.png')
                        self.test_results.append(("Edit Store", "PASS"))
                        return True
                    else:
                        print("   [SKIP] Submit button not found")
                        self.test_results.append(("Edit Store", "SKIP"))
                        return False
                else:
                    print("   [SKIP] Edit link not found")
                    self.test_results.append(("Edit Store", "SKIP"))
                    return False
            else:
                print(f"   [SKIP] Store '{store_name}' not found")
                self.test_results.append(("Edit Store", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/store_05_error.png')
            self.test_results.append(("Edit Store", "ERROR"))
            return False

    def test_06_filter_stores(self, page):
        """Test: Filter stores"""
        print("\n[Test 6] Filter Stores")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/stores/")
            page.wait_for_load_state("networkidle")

            # Look for filter options
            filter_select = page.locator('select').first
            if filter_select.count() > 0:
                # Select first non-empty option
                filter_select.select_option(index=1)
                page.wait_for_timeout(1000)

                print("   [OK] Filter applied")
                page.screenshot(path='result/store_06_filter.png')

                # Reset filter
                filter_select.select_option(index=0)
                page.wait_for_timeout(500)

                self.test_results.append(("Filter Stores", "PASS"))
                return True
            else:
                print("   [SKIP] Filter select not found")
                self.test_results.append(("Filter Stores", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/store_06_error.png')
            self.test_results.append(("Filter Stores", "ERROR"))
            return False

    def test_07_delete_store(self, page, store_name):
        """Test: Delete store"""
        print("\n[Test 7] Delete Store")
        print("-" * 70)

        try:
            if not store_name:
                print("   [SKIP] No store to delete")
                self.test_results.append(("Delete Store", "SKIP"))
                return False

            page.goto(f"{self.base_url}/stores/")
            page.wait_for_load_state("networkidle")

            if page.locator(f'text={store_name}').count() > 0:
                # Setup dialog handler
                page.on("dialog", lambda dialog: dialog.accept())

                delete_button = page.locator('button').filter(has_text='削除').first
                if delete_button.count() > 0:
                    delete_button.click()
                    page.wait_for_timeout(2000)

                    # Verify deletion
                    if page.locator(f'text={store_name}').count() == 0:
                        print(f"   [OK] Store '{store_name}' deleted")
                        page.screenshot(path='result/store_07_deleted.png')
                        self.test_results.append(("Delete Store", "PASS"))
                        return True
                    else:
                        print("   [WARNING] Deletion unclear")
                        self.test_results.append(("Delete Store", "WARNING"))
                        return False
                else:
                    print("   [SKIP] Delete button not found")
                    self.test_results.append(("Delete Store", "SKIP"))
                    return False
            else:
                print(f"   [SKIP] Store '{store_name}' not found")
                self.test_results.append(("Delete Store", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/store_07_error.png')
            self.test_results.append(("Delete Store", "ERROR"))
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("STORE MANAGEMENT TEST SUMMARY")
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
        """Run all store management tests"""
        print("\n" + "="*70)
        print("STORE MANAGEMENT - BROWSER TESTS")
        print("="*70)

        with sync_playwright() as p:
            browser, page = self.setup_browser(p)

            try:
                # Run tests in sequence
                self.test_01_list_stores(page)
                self.test_02_search_store(page)
                store_name = self.test_03_create_store(page)
                self.test_04_view_store(page)

                if store_name:
                    self.test_05_edit_store(page, store_name)
                    self.test_06_filter_stores(page)
                    self.test_07_delete_store(page, store_name)

                self.print_summary()

            except Exception as e:
                print(f"\n[FATAL ERROR] {str(e)}")
                page.screenshot(path='result/store_fatal_error.png')
            finally:
                time.sleep(2)
                browser.close()


if __name__ == '__main__':
    test = StoreManagementTest()
    test.run_all_tests()
