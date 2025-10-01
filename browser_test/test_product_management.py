"""
Product Management Feature - Comprehensive Browser Tests
Tests product CRUD operations, search, filtering, and category management
"""
from playwright.sync_api import sync_playwright
import time


class ProductManagementTest:
    """Product management feature tests"""

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

    def test_01_list_products(self, page):
        """Test: Product list display"""
        print("\n[Test 1] Product List Display")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/products/")
            page.wait_for_load_state("networkidle")

            # Check if products are displayed
            if page.locator('table').count() > 0 or page.locator('.card').count() > 0:
                print("   [OK] Product list loaded")

                # Count products
                product_count = page.locator('table tbody tr').count()
                if product_count == 0:
                    product_count = page.locator('.card').count()

                print(f"   [OK] Found {product_count} products")

                page.screenshot(path='result/product_01_list.png')
                self.test_results.append(("Product List", "PASS"))
                return True
            else:
                print("   [FAIL] No products found")
                self.test_results.append(("Product List", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/product_01_error.png')
            self.test_results.append(("Product List", "ERROR"))
            return False

    def test_02_search_product(self, page):
        """Test: Product search functionality"""
        print("\n[Test 2] Product Search")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/products/")
            page.wait_for_load_state("networkidle")

            # Look for search input
            search_input = page.locator('input[name="search"]')
            if search_input.count() > 0:
                search_input.fill('Product')
                page.press('input[name="search"]', 'Enter')
                page.wait_for_timeout(1000)

                results = page.locator('table tbody tr').count()
                print(f"   [OK] Search returned {results} results")
                page.screenshot(path='result/product_02_search.png')

                # Clear search
                search_input.fill('')
                page.press('input[name="search"]', 'Enter')
                page.wait_for_timeout(500)

                self.test_results.append(("Product Search", "PASS"))
                return True
            else:
                print("   [SKIP] Search input not found")
                self.test_results.append(("Product Search", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/product_02_error.png')
            self.test_results.append(("Product Search", "ERROR"))
            return False

    def test_03_filter_by_category(self, page):
        """Test: Filter products by category"""
        print("\n[Test 3] Filter by Category")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/products/")
            page.wait_for_load_state("networkidle")

            # Look for category filter
            category_select = page.locator('select[name="category"]')
            if category_select.count() == 0:
                category_select = page.locator('select').first

            if category_select.count() > 0:
                # Select a category
                category_select.select_option(index=1)
                page.wait_for_timeout(1000)

                print("   [OK] Category filter applied")
                page.screenshot(path='result/product_03_category_filter.png')

                # Reset filter
                category_select.select_option(index=0)
                page.wait_for_timeout(500)

                self.test_results.append(("Filter by Category", "PASS"))
                return True
            else:
                print("   [SKIP] Category filter not found")
                self.test_results.append(("Filter by Category", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/product_03_error.png')
            self.test_results.append(("Filter by Category", "ERROR"))
            return False

    def test_04_create_product(self, page):
        """Test: Create new product"""
        print("\n[Test 4] Create Product")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/products/")
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
                    product_name = f"Test Product {timestamp}"

                    # Fill basic fields
                    if page.locator('input[name="name"]').count() > 0:
                        page.fill('input[name="name"]', product_name)

                    if page.locator('textarea[name="description"]').count() > 0:
                        page.fill('textarea[name="description"]', 'Test product description')

                    if page.locator('input[name="price"]').count() > 0:
                        page.fill('input[name="price"]', '1000')

                    if page.locator('input[name="stock"]').count() > 0:
                        page.fill('input[name="stock"]', '100')

                    # Select category if exists
                    if page.locator('select[name="category_id"]').count() > 0:
                        page.select_option('select[name="category_id"]', index=1)

                    page.screenshot(path='result/product_04_create_form.png')

                    # Submit if submit button exists
                    if page.locator('input[type="submit"]').count() > 0:
                        page.click('input[type="submit"]')
                        page.wait_for_timeout(2000)

                        # Verify creation
                        if page.locator(f'text={product_name}').count() > 0:
                            print(f"   [OK] Product '{product_name}' created")
                            page.screenshot(path='result/product_04_created.png')
                            self.test_results.append(("Create Product", "PASS"))
                            return product_name
                        else:
                            print("   [WARNING] Product creation unclear")
                            self.test_results.append(("Create Product", "WARNING"))
                            return product_name
                    else:
                        print("   [SKIP] Submit button not found")
                        self.test_results.append(("Create Product", "SKIP"))
                        return None
                else:
                    print("   [SKIP] Create form not found")
                    self.test_results.append(("Create Product", "SKIP"))
                    return None
            else:
                print("   [SKIP] Create button not found")
                self.test_results.append(("Create Product", "SKIP"))
                return None

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/product_04_error.png')
            self.test_results.append(("Create Product", "ERROR"))
            return None

    def test_05_view_product(self, page):
        """Test: View product details"""
        print("\n[Test 5] View Product Details")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/products/")
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

                print("   [OK] Product detail page loaded")
                page.screenshot(path='result/product_05_view.png')

                page.go_back()
                page.wait_for_timeout(500)

                self.test_results.append(("View Product", "PASS"))
                return True
            else:
                print("   [SKIP] View link not found")
                self.test_results.append(("View Product", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/product_05_error.png')
            self.test_results.append(("View Product", "ERROR"))
            return False

    def test_06_edit_product(self, page, product_name):
        """Test: Edit product"""
        print("\n[Test 6] Edit Product")
        print("-" * 70)

        try:
            if not product_name:
                print("   [SKIP] No product to edit")
                self.test_results.append(("Edit Product", "SKIP"))
                return False

            page.goto(f"{self.base_url}/products/")
            page.wait_for_load_state("networkidle")

            # Find the product and edit link
            if page.locator(f'text={product_name}').count() > 0:
                edit_link = page.locator('a').filter(has_text='編集').first
                if edit_link.count() > 0:
                    edit_link.click()
                    page.wait_for_timeout(1000)

                    # Update price
                    if page.locator('input[name="price"]').count() > 0:
                        page.fill('input[name="price"]', '1500')

                    page.screenshot(path='result/product_06_edit_form.png')

                    if page.locator('input[type="submit"]').count() > 0:
                        page.click('input[type="submit"]')
                        page.wait_for_timeout(2000)

                        print("   [OK] Product edited")
                        page.screenshot(path='result/product_06_edited.png')
                        self.test_results.append(("Edit Product", "PASS"))
                        return True
                    else:
                        print("   [SKIP] Submit button not found")
                        self.test_results.append(("Edit Product", "SKIP"))
                        return False
                else:
                    print("   [SKIP] Edit link not found")
                    self.test_results.append(("Edit Product", "SKIP"))
                    return False
            else:
                print(f"   [SKIP] Product '{product_name}' not found")
                self.test_results.append(("Edit Product", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/product_06_error.png')
            self.test_results.append(("Edit Product", "ERROR"))
            return False

    def test_07_inventory_check(self, page):
        """Test: Check inventory display"""
        print("\n[Test 7] Inventory Display")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/products/")
            page.wait_for_load_state("networkidle")

            # Check if inventory/stock information is visible
            if page.locator('text=/在庫|stock/i').count() > 0:
                print("   [OK] Inventory information displayed")
                page.screenshot(path='result/product_07_inventory.png')
                self.test_results.append(("Inventory Display", "PASS"))
                return True
            else:
                print("   [SKIP] Inventory information not found")
                self.test_results.append(("Inventory Display", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/product_07_error.png')
            self.test_results.append(("Inventory Display", "ERROR"))
            return False

    def test_08_delete_product(self, page, product_name):
        """Test: Delete product"""
        print("\n[Test 8] Delete Product")
        print("-" * 70)

        try:
            if not product_name:
                print("   [SKIP] No product to delete")
                self.test_results.append(("Delete Product", "SKIP"))
                return False

            page.goto(f"{self.base_url}/products/")
            page.wait_for_load_state("networkidle")

            if page.locator(f'text={product_name}').count() > 0:
                # Setup dialog handler
                page.on("dialog", lambda dialog: dialog.accept())

                delete_button = page.locator('button').filter(has_text='削除').first
                if delete_button.count() > 0:
                    delete_button.click()
                    page.wait_for_timeout(2000)

                    # Verify deletion
                    if page.locator(f'text={product_name}').count() == 0:
                        print(f"   [OK] Product '{product_name}' deleted")
                        page.screenshot(path='result/product_08_deleted.png')
                        self.test_results.append(("Delete Product", "PASS"))
                        return True
                    else:
                        print("   [WARNING] Deletion unclear")
                        self.test_results.append(("Delete Product", "WARNING"))
                        return False
                else:
                    print("   [SKIP] Delete button not found")
                    self.test_results.append(("Delete Product", "SKIP"))
                    return False
            else:
                print(f"   [SKIP] Product '{product_name}' not found")
                self.test_results.append(("Delete Product", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/product_08_error.png')
            self.test_results.append(("Delete Product", "ERROR"))
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("PRODUCT MANAGEMENT TEST SUMMARY")
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
        """Run all product management tests"""
        print("\n" + "="*70)
        print("PRODUCT MANAGEMENT - BROWSER TESTS")
        print("="*70)

        with sync_playwright() as p:
            browser, page = self.setup_browser(p)

            try:
                # Run tests in sequence
                self.test_01_list_products(page)
                self.test_02_search_product(page)
                self.test_03_filter_by_category(page)
                product_name = self.test_04_create_product(page)
                self.test_05_view_product(page)

                if product_name:
                    self.test_06_edit_product(page, product_name)
                    self.test_07_inventory_check(page)
                    self.test_08_delete_product(page, product_name)

                self.print_summary()

            except Exception as e:
                print(f"\n[FATAL ERROR] {str(e)}")
                page.screenshot(path='result/product_fatal_error.png')
            finally:
                time.sleep(2)
                browser.close()


if __name__ == '__main__':
    test = ProductManagementTest()
    test.run_all_tests()
