"""
Authentication Feature - Comprehensive Browser Tests
Tests login, logout, registration, and session management
"""
from playwright.sync_api import sync_playwright
import time


class AuthenticationTest:
    """Authentication feature tests"""

    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = []

    def setup_browser(self, p):
        """Setup browser without login"""
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        return browser, page

    def test_01_login_page_access(self, page):
        """Test: Access login page"""
        print("\n[Test 1] Login Page Access")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/auth/login")
            page.wait_for_load_state("networkidle")

            # Check page title
            title = page.title()
            print(f"   Page title: {title}")

            # Check form exists
            if page.locator('form').count() > 0:
                print("   [OK] Login form found")

                # Check form fields
                username_field = page.locator('input[name="username"]')
                password_field = page.locator('input[name="password"]')
                submit_button = page.locator('input[type="submit"]')

                if username_field.count() > 0 and password_field.count() > 0 and submit_button.count() > 0:
                    print("   [OK] All required fields present")
                    page.screenshot(path='result/auth_01_login_page.png')
                    self.test_results.append(("Login Page Access", "PASS"))
                    return True
                else:
                    print("   [FAIL] Missing required fields")
                    self.test_results.append(("Login Page Access", "FAIL"))
                    return False
            else:
                print("   [FAIL] Login form not found")
                self.test_results.append(("Login Page Access", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/auth_01_error.png')
            self.test_results.append(("Login Page Access", "ERROR"))
            return False

    def test_02_login_validation(self, page):
        """Test: Login form validation"""
        print("\n[Test 2] Login Validation")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/auth/login")
            page.wait_for_load_state("networkidle")

            # Test empty submission
            print("   Testing empty form submission...")
            page.click('input[type="submit"]')
            page.wait_for_timeout(1000)

            # Should stay on login page
            if 'login' in page.url:
                print("   [OK] Empty form rejected")
            else:
                print("   [FAIL] Empty form accepted")

            # Test wrong credentials
            print("   Testing wrong credentials...")
            page.fill('input[name="username"]', 'wronguser')
            page.fill('input[name="password"]', 'wrongpass')
            page.click('input[type="submit"]')
            page.wait_for_timeout(1000)

            # Should show error and stay on login page
            if 'login' in page.url:
                print("   [OK] Wrong credentials rejected")
                page.screenshot(path='result/auth_02_validation.png')
                self.test_results.append(("Login Validation", "PASS"))
                return True
            else:
                print("   [FAIL] Wrong credentials accepted")
                self.test_results.append(("Login Validation", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/auth_02_error.png')
            self.test_results.append(("Login Validation", "ERROR"))
            return False

    def test_03_successful_login(self, page):
        """Test: Successful login"""
        print("\n[Test 3] Successful Login")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/auth/login")
            page.wait_for_load_state("networkidle")

            # Fill correct credentials
            page.fill('input[name="username"]', 'admin')
            page.fill('input[name="password"]', 'admin123')

            page.screenshot(path='result/auth_03_before_login.png')

            page.click('input[type="submit"]')
            page.wait_for_timeout(2000)

            # Should redirect to dashboard/home
            if 'login' not in page.url:
                print(f"   [OK] Login successful, redirected to: {page.url}")

                # Check for logout link
                if page.locator('a').filter(has_text='ログアウト').count() > 0:
                    print("   [OK] Logout link visible")

                page.screenshot(path='result/auth_03_after_login.png')
                self.test_results.append(("Successful Login", "PASS"))
                return True
            else:
                print("   [FAIL] Login failed")
                page.screenshot(path='result/auth_03_fail.png')
                self.test_results.append(("Successful Login", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/auth_03_error.png')
            self.test_results.append(("Successful Login", "ERROR"))
            return False

    def test_04_protected_route_access(self, page):
        """Test: Access protected routes while logged in"""
        print("\n[Test 4] Protected Route Access")
        print("-" * 70)

        try:
            # Try to access employees page (should work when logged in)
            page.goto(f"{self.base_url}/employees/")
            page.wait_for_load_state("networkidle")

            if 'employees' in page.url and 'login' not in page.url:
                print("   [OK] Protected route accessible when logged in")
                page.screenshot(path='result/auth_04_protected_access.png')
                self.test_results.append(("Protected Route Access", "PASS"))
                return True
            else:
                print("   [FAIL] Protected route not accessible")
                self.test_results.append(("Protected Route Access", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/auth_04_error.png')
            self.test_results.append(("Protected Route Access", "ERROR"))
            return False

    def test_05_logout(self, page):
        """Test: Logout functionality"""
        print("\n[Test 5] Logout")
        print("-" * 70)

        try:
            # Click logout link
            logout_link = page.locator('a').filter(has_text='ログアウト')
            if logout_link.count() > 0:
                logout_link.click()
                page.wait_for_timeout(2000)

                # Should redirect to login or home page
                if 'login' in page.url or page.url == f"{self.base_url}/":
                    print("   [OK] Logout successful")
                    page.screenshot(path='result/auth_05_after_logout.png')
                    self.test_results.append(("Logout", "PASS"))
                    return True
                else:
                    print("   [FAIL] Logout did not redirect properly")
                    self.test_results.append(("Logout", "FAIL"))
                    return False
            else:
                print("   [SKIP] Logout link not found")
                self.test_results.append(("Logout", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/auth_05_error.png')
            self.test_results.append(("Logout", "ERROR"))
            return False

    def test_06_logged_out_protection(self, page):
        """Test: Protected routes redirect when logged out"""
        print("\n[Test 6] Protection After Logout")
        print("-" * 70)

        try:
            # Try to access protected route after logout
            page.goto(f"{self.base_url}/employees/")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            # Should redirect to login
            if 'login' in page.url:
                print("   [OK] Protected route redirects to login when logged out")
                page.screenshot(path='result/auth_06_redirect.png')
                self.test_results.append(("Logged Out Protection", "PASS"))
                return True
            else:
                print("   [FAIL] Protected route accessible when logged out")
                self.test_results.append(("Logged Out Protection", "FAIL"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/auth_06_error.png')
            self.test_results.append(("Logged Out Protection", "ERROR"))
            return False

    def test_07_registration_page(self, page):
        """Test: Registration page access"""
        print("\n[Test 7] Registration Page")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/auth/register")
            page.wait_for_load_state("networkidle")

            # Check if registration form exists
            if page.locator('form').count() > 0:
                print("   [OK] Registration page loaded")

                # Check for required fields
                username_field = page.locator('input[name="username"]')
                email_field = page.locator('input[name="email"]')
                password_field = page.locator('input[name="password"]')

                if username_field.count() > 0 and email_field.count() > 0 and password_field.count() > 0:
                    print("   [OK] Registration form has required fields")
                    page.screenshot(path='result/auth_07_register.png')
                    self.test_results.append(("Registration Page", "PASS"))
                    return True
                else:
                    print("   [FAIL] Missing required registration fields")
                    self.test_results.append(("Registration Page", "FAIL"))
                    return False
            else:
                print("   [SKIP] Registration form not found")
                self.test_results.append(("Registration Page", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/auth_07_error.png')
            self.test_results.append(("Registration Page", "ERROR"))
            return False

    def test_08_remember_me(self, page):
        """Test: Remember me functionality"""
        print("\n[Test 8] Remember Me Feature")
        print("-" * 70)

        try:
            page.goto(f"{self.base_url}/auth/login")
            page.wait_for_load_state("networkidle")

            # Check if remember_me checkbox exists
            remember_me = page.locator('input[name="remember_me"]')
            if remember_me.count() > 0:
                print("   [OK] Remember me checkbox found")

                # Test login with remember me
                page.fill('input[name="username"]', 'admin')
                page.fill('input[name="password"]', 'admin123')
                page.check('input[name="remember_me"]')

                page.screenshot(path='result/auth_08_remember_me.png')
                page.click('input[type="submit"]')
                page.wait_for_timeout(2000)

                if 'login' not in page.url:
                    print("   [OK] Login with remember me successful")
                    self.test_results.append(("Remember Me", "PASS"))
                    return True
                else:
                    print("   [FAIL] Login with remember me failed")
                    self.test_results.append(("Remember Me", "FAIL"))
                    return False
            else:
                print("   [SKIP] Remember me checkbox not found")
                self.test_results.append(("Remember Me", "SKIP"))
                return False

        except Exception as e:
            print(f"   [ERROR] {str(e)}")
            page.screenshot(path='result/auth_08_error.png')
            self.test_results.append(("Remember Me", "ERROR"))
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("AUTHENTICATION TEST SUMMARY")
        print("="*70)

        passed = sum(1 for _, status in self.test_results if status == "PASS")
        failed = sum(1 for _, status in self.test_results if status == "FAIL")
        skipped = sum(1 for _, status in self.test_results if status == "SKIP")
        errors = sum(1 for _, status in self.test_results if status == "ERROR")

        for test_name, status in self.test_results:
            status_icon = {
                "PASS": "[OK]",
                "FAIL": "[FAIL]",
                "SKIP": "[SKIP]",
                "ERROR": "[ERROR]"
            }[status]
            print(f"{status_icon} {test_name}")

        print("-" * 70)
        print(f"Total: {len(self.test_results)} tests")
        print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped} | Errors: {errors}")
        print("="*70)

    def run_all_tests(self):
        """Run all authentication tests"""
        print("\n" + "="*70)
        print("AUTHENTICATION - BROWSER TESTS")
        print("="*70)

        with sync_playwright() as p:
            browser, page = self.setup_browser(p)

            try:
                # Run tests in sequence
                self.test_01_login_page_access(page)
                self.test_02_login_validation(page)
                self.test_03_successful_login(page)
                self.test_04_protected_route_access(page)
                self.test_05_logout(page)
                self.test_06_logged_out_protection(page)
                self.test_07_registration_page(page)
                self.test_08_remember_me(page)

                self.print_summary()

            except Exception as e:
                print(f"\n[FATAL ERROR] {str(e)}")
                page.screenshot(path='result/auth_fatal_error.png')
            finally:
                time.sleep(2)
                browser.close()


if __name__ == '__main__':
    test = AuthenticationTest()
    test.run_all_tests()
