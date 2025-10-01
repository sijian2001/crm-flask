# Browser Tests for CRM System

This directory contains comprehensive browser tests for all features of the CRM system using Playwright.

## Test Structure

```
browser_test/
├── result/                          # Test screenshots and reports
├── test_authentication.py           # Authentication tests (login, logout, registration)
├── test_employee_management.py      # Employee CRUD, search, statistics
├── test_store_management.py         # Store CRUD, search, filtering
├── test_customer_management.py      # Customer CRUD, search, filtering
├── test_product_management.py       # Product CRUD, category, inventory
├── run_all_tests.py                 # Integrated test runner
└── README.md                        # This file
```

## Test Coverage

### 1. Authentication Tests (`test_authentication.py`)
- ✅ Login page access
- ✅ Form validation
- ✅ Successful login
- ✅ Protected route access
- ✅ Logout functionality
- ✅ Session protection
- ✅ Registration page
- ✅ Remember me feature

**Run:** `python test_authentication.py`

### 2. Employee Management Tests (`test_employee_management.py`)
- ✅ Employee list display
- ✅ Search functionality
- ✅ Create employee
- ✅ View employee details
- ✅ Edit employee
- ✅ Statistics page
- ✅ Delete employee

**Run:** `python test_employee_management.py`

### 3. Store Management Tests (`test_store_management.py`)
- ✅ Store list display
- ✅ Search stores
- ✅ Create store
- ✅ View store details
- ✅ Edit store
- ✅ Filter stores
- ✅ Delete store

**Run:** `python test_store_management.py`

### 4. Customer Management Tests (`test_customer_management.py`)
- ✅ Customer list display
- ✅ Search customers
- ✅ Create customer
- ✅ View customer details
- ✅ Edit customer
- ✅ Filter customers
- ✅ Delete customer

**Run:** `python test_customer_management.py`

### 5. Product Management Tests (`test_product_management.py`)
- ✅ Product list display
- ✅ Search products
- ✅ Filter by category
- ✅ Create product
- ✅ View product details
- ✅ Edit product
- ✅ Inventory check
- ✅ Delete product

**Run:** `python test_product_management.py`

## Prerequisites

1. Install Playwright:
```bash
pip install playwright
playwright install chromium
```

2. Start the Flask development server:
```bash
python app.py
```

The server should be running on `http://127.0.0.1:8000`

## Running Tests

### Run All Tests
Execute all test suites in sequence:
```bash
python run_all_tests.py
```

This will:
- Run all 5 test suites
- Generate screenshots for each test
- Create a comprehensive test report in `result/test_report.md`
- Display summary statistics

### Run Individual Test Suite
Run a specific feature test:
```bash
# Authentication tests
python test_authentication.py

# Employee management tests
python test_employee_management.py

# Store management tests
python test_store_management.py

# Customer management tests
python test_customer_management.py

# Product management tests
python test_product_management.py
```

### Run Legacy Tests
Legacy comprehensive tests:
```bash
# Detailed system tests
python test_browser_detailed.py

# Employee feature tests
python test_browser_employee.py
```

## Test Results

### Screenshots
All screenshots are saved in the `result/` directory with descriptive names:
- `auth_XX_*.png` - Authentication test screenshots
- `emp_XX_*.png` - Employee management screenshots
- `store_XX_*.png` - Store management screenshots
- `customer_XX_*.png` - Customer management screenshots
- `product_XX_*.png` - Product management screenshots

### Test Reports
After running `run_all_tests.py`, check:
- Console output for detailed test execution
- `result/test_report.md` for comprehensive markdown report

## Test Configuration

### Browser Settings
- **Browser:** Chromium (headless=False for visual feedback)
- **Viewport:** 1920x1080
- **Slow Motion:** 300ms (for better visibility)
- **Timeout:** 30 seconds per action

### Test Credentials
- **Username:** admin
- **Password:** admin123

## Troubleshooting

### Server Not Running
```
Error: net::ERR_CONNECTION_REFUSED
```
**Solution:** Start the Flask server with `python app.py`

### Timeout Errors
```
TimeoutError: Timeout 30000ms exceeded
```
**Solution:**
- Check if the server is responding
- Verify the route exists
- Increase timeout if necessary

### Element Not Found
```
waiting for locator("...") to be visible
```
**Solution:**
- Check if the feature is implemented
- Verify the HTML structure matches the selector
- Update selectors in the test file

## Test Development

### Adding New Tests
1. Create a new test file following the naming convention
2. Import Playwright: `from playwright.sync_api import sync_playwright`
3. Create a test class with setup_browser method
4. Implement test methods (test_01, test_02, etc.)
5. Add to `run_all_tests.py` if needed

### Test Structure Template
```python
class FeatureTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = []

    def setup_browser(self, p):
        # Browser setup and login
        pass

    def test_01_feature(self, page):
        # Test implementation
        pass

    def print_summary(self):
        # Summary output
        pass

    def run_all_tests(self):
        # Test runner
        pass
```

## Best Practices

1. **Always check server status** before running tests
2. **Run tests individually first** to debug issues
3. **Check screenshots** when tests fail
4. **Update selectors** if HTML structure changes
5. **Add waits** for dynamic content
6. **Handle dialogs** (confirmations, alerts)
7. **Clean up test data** created during tests

## CI/CD Integration

To run tests in headless mode for CI/CD:

```python
# In setup_browser method, change:
browser = p.chromium.launch(headless=True, slow_mo=0)
```

## Support

For issues or questions:
1. Check the screenshots in `result/` directory
2. Review console output for error messages
3. Verify server logs for backend errors
4. Check the test report in `result/test_report.md`
