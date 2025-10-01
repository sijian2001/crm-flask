"""
Integrated Test Runner
Runs all browser tests for the CRM system
"""
import sys
import time
from datetime import datetime
import subprocess


class TestRunner:
    """Runs all browser tests and generates a summary report"""

    def __init__(self):
        self.test_files = [
            ('test_authentication.py', 'Authentication'),
            ('test_employee_management.py', 'Employee Management'),
            ('test_store_management.py', 'Store Management'),
            ('test_customer_management.py', 'Customer Management'),
            ('test_product_management.py', 'Product Management'),
        ]
        self.results = []
        self.start_time = None
        self.end_time = None

    def print_header(self):
        """Print test suite header"""
        print("\n" + "="*80)
        print(" " * 20 + "CRM SYSTEM - COMPREHENSIVE BROWSER TESTS")
        print("="*80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Test Suites: {len(self.test_files)}")
        print("="*80)

    def run_test_file(self, test_file, test_name):
        """Run a single test file"""
        print(f"\n{'='*80}")
        print(f"Running: {test_name}")
        print(f"File: {test_file}")
        print(f"{'='*80}")

        try:
            start = time.time()
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            duration = time.time() - start

            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            # Determine status
            if result.returncode == 0:
                status = "PASS"
            else:
                status = "FAIL"

            self.results.append({
                'name': test_name,
                'file': test_file,
                'status': status,
                'duration': duration,
                'returncode': result.returncode
            })

            return status

        except subprocess.TimeoutExpired:
            print(f"\n[ERROR] Test timed out after 5 minutes")
            self.results.append({
                'name': test_name,
                'file': test_file,
                'status': 'TIMEOUT',
                'duration': 300,
                'returncode': -1
            })
            return "TIMEOUT"

        except Exception as e:
            print(f"\n[ERROR] Failed to run test: {str(e)}")
            self.results.append({
                'name': test_name,
                'file': test_file,
                'status': 'ERROR',
                'duration': 0,
                'returncode': -1
            })
            return "ERROR"

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print(" " * 25 + "COMPREHENSIVE TEST SUMMARY")
        print("="*80)

        # Individual test results
        for result in self.results:
            status_icon = {
                "PASS": "[OK]",
                "FAIL": "[FAIL]",
                "TIMEOUT": "[TIMEOUT]",
                "ERROR": "[ERROR]"
            }[result['status']]

            duration_str = f"{result['duration']:.1f}s"
            print(f"{status_icon} {result['name']:30} ({duration_str})")

        print("-" * 80)

        # Statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == "PASS")
        failed = sum(1 for r in self.results if r['status'] == "FAIL")
        timeout = sum(1 for r in self.results if r['status'] == "TIMEOUT")
        errors = sum(1 for r in self.results if r['status'] == "ERROR")

        total_duration = self.end_time - self.start_time

        print(f"Total Test Suites: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Timeout: {timeout}")
        print(f"Errors: {errors}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        print(f"Total Duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Overall status
        if passed == total:
            print("\n[SUCCESS] All test suites passed!")
            return 0
        else:
            print(f"\n[WARNING] {failed + timeout + errors} test suite(s) did not pass")
            return 1

    def generate_report(self):
        """Generate markdown test report"""
        report_file = 'result/test_report.md'

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# CRM System - Browser Test Report\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # Summary table
                f.write("## Summary\n\n")
                f.write("| Metric | Value |\n")
                f.write("|--------|-------|\n")

                total = len(self.results)
                passed = sum(1 for r in self.results if r['status'] == "PASS")
                failed = sum(1 for r in self.results if r['status'] == "FAIL")

                f.write(f"| Total Test Suites | {total} |\n")
                f.write(f"| Passed | {passed} |\n")
                f.write(f"| Failed | {failed} |\n")
                f.write(f"| Success Rate | {(passed/total*100):.1f}% |\n")
                f.write(f"| Total Duration | {(self.end_time - self.start_time):.1f}s |\n\n")

                # Test results
                f.write("## Test Results\n\n")
                f.write("| Test Suite | Status | Duration |\n")
                f.write("|------------|--------|----------|\n")

                for result in self.results:
                    status_emoji = {
                        "PASS": "✅",
                        "FAIL": "❌",
                        "TIMEOUT": "⏱️",
                        "ERROR": "⚠️"
                    }[result['status']]

                    f.write(f"| {result['name']} | {status_emoji} {result['status']} | {result['duration']:.1f}s |\n")

                f.write("\n## Test Details\n\n")
                for result in self.results:
                    f.write(f"### {result['name']}\n")
                    f.write(f"- **File:** `{result['file']}`\n")
                    f.write(f"- **Status:** {result['status']}\n")
                    f.write(f"- **Duration:** {result['duration']:.1f}s\n")
                    f.write(f"- **Return Code:** {result['returncode']}\n\n")

            print(f"\n[OK] Test report generated: {report_file}")

        except Exception as e:
            print(f"\n[WARNING] Failed to generate report: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        self.print_header()
        self.start_time = time.time()

        for test_file, test_name in self.test_files:
            self.run_test_file(test_file, test_name)
            print("\n" + "-"*80)
            time.sleep(2)  # Brief pause between tests

        self.end_time = time.time()
        exit_code = self.print_summary()
        self.generate_report()

        return exit_code


def main():
    """Main entry point"""
    runner = TestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
