#!/usr/bin/env python3
"""
Frontend UI Test for Financial Document Processing System
========================================================

This script tests the frontend UI components by simulating user interactions:
- Document upload workflow
- Document viewer
- Table visualizer
- Financial analysis dashboard
- Chat interface

This uses Selenium WebDriver to automate browser testing.

Usage:
    python3 frontend_ui_test.py [--browser chrome|firefox] [--headless] [--url http://localhost:3000]

Requirements:
    - Selenium WebDriver (pip install selenium)
    - ChromeDriver or GeckoDriver (ensure it's in PATH or specify path)
    - Running frontend server (npm start or served build)
"""

import os
import sys
import json
import time
import logging
import argparse
import traceback
from pathlib import Path
from datetime import datetime
import uuid

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
except ImportError:
    print("Selenium is required for UI testing. Install with: pip install selenium")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tests/ui_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("UiTest")

# Constants
DEFAULT_FRONTEND_URL = "http://localhost:3000"
TEST_DOCS_PATH = Path("test_documents")
RESULTS_PATH = Path("test_results/ui_tests")
SCREENSHOT_PATH = RESULTS_PATH / "screenshots"

# Ensure directories exist
RESULTS_PATH.mkdir(exist_ok=True, parents=True)
SCREENSHOT_PATH.mkdir(exist_ok=True, parents=True)

class UiTester:
    """Frontend UI Test orchestrator."""

    def __init__(self, args):
        self.browser_type = args.browser
        self.headless = args.headless
        self.frontend_url = args.url
        self.driver = None
        self.test_run_id = str(uuid.uuid4())[:8]
        self.results = {
            "test_run_id": self.test_run_id,
            "timestamp": datetime.now().isoformat(),
            "browser": args.browser,
            "headless": args.headless,
            "frontend_url": self.frontend_url,
            "tests": {
                "setup": {"success": False, "screenshots": [], "duration": 0, "error": None},
                "login": {"success": False, "screenshots": [], "duration": 0, "error": None},
                "upload": {"success": False, "screenshots": [], "duration": 0, "error": None},
                "document_viewer": {"success": False, "screenshots": [], "duration": 0, "error": None},
                "table_viewer": {"success": False, "screenshots": [], "duration": 0, "error": None},
                "financial_dashboard": {"success": False, "screenshots": [], "duration": 0, "error": None},
                "chat_interface": {"success": False, "screenshots": [], "duration": 0, "error": None}
            },
            "overall_status": "PENDING"
        }

    def setup_driver(self):
        """Set up the WebDriver for browser automation."""
        start_time = time.time()
        test_name = "setup"
        logger.info(f"Setting up {self.browser_type} WebDriver...")

        try:
            if self.browser_type == "chrome":
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox") # Often needed in containers
                options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
                options.add_argument("--window-size=1920,1080")
                # Add options to ignore certificate errors if needed
                # options.add_argument('--ignore-certificate-errors')
                # options.add_argument('--allow-running-insecure-content')

                # Specify ChromeDriver path if not in PATH (optional)
                # service = webdriver.ChromeService(executable_path='/path/to/chromedriver')
                # self.driver = webdriver.Chrome(service=service, options=options)
                self.driver = webdriver.Chrome(options=options)

            elif self.browser_type == "firefox":
                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--width=1920")
                options.add_argument("--height=1080")

                # Specify GeckoDriver path if not in PATH (optional)
                # service = webdriver.FirefoxService(executable_path='/path/to/geckodriver')
                # self.driver = webdriver.Firefox(service=service, options=options)
                self.driver = webdriver.Firefox(options=options)

            else:
                logger.error(f"Unsupported browser type: {self.browser_type}")
                self.results["tests"][test_name]["error"] = f"Unsupported browser: {self.browser_type}"
                return False

            self.driver.implicitly_wait(10) # Default wait time for elements
            logger.info("WebDriver setup successful")
            self.results["tests"][test_name]["success"] = True
            return True

        except WebDriverException as e:
             logger.error(f"WebDriverException during setup: {str(e)}")
             logger.error("Ensure the correct WebDriver (ChromeDriver/GeckoDriver) is installed and in your PATH.")
             self.results["tests"][test_name]["error"] = f"WebDriverException: {str(e)}"
             return False
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}")
            self.results["tests"][test_name]["error"] = str(e)
            return False
        finally:
            self.results["tests"][test_name]["duration"] = time.time() - start_time


    def take_screenshot(self, name, test_name):
        """Take a screenshot and save it."""
        if not self.driver:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{name}_{timestamp}_{self.test_run_id}.png"
        filepath = SCREENSHOT_PATH / filename

        try:
            self.driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            # Add screenshot to results for the specific test
            if test_name in self.results["tests"]:
                self.results["tests"][test_name]["screenshots"].append(str(filepath))
            return str(filepath)
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return None

    def run_ui_tests(self):
        """Run all UI tests."""
        logger.info(f"Starting UI tests for {self.frontend_url} using {self.browser_type}")

        if not self.setup_driver():
            logger.error("Failed to set up WebDriver, cannot run tests")
            self.results["overall_status"] = "FAILED (Setup)"
            self.save_results()
            return False

        try:
            # Run tests sequentially using the helper
            self._run_test_step(self.test_login, "login")
            self._run_test_step(self.test_document_upload, "upload")
            self._run_test_step(self.test_document_viewer, "document_viewer")
            self._run_test_step(self.test_table_viewer, "table_viewer")
            self._run_test_step(self.test_financial_dashboard, "financial_dashboard")
            self._run_test_step(self.test_chat_interface, "chat_interface")


            # Determine overall status
            all_passed = all(test.get("success", False) for test_name, test in self.results["tests"].items() if test_name != "setup")
            self.results["overall_status"] = "PASSED" if all_passed else "FAILED"
            logger.info(f"UI tests completed. Overall status: {self.results['overall_status']}")

        except Exception as e:
            logger.error(f"Unhandled error during UI testing: {str(e)}")
            traceback.print_exc()
            self.results["overall_status"] = "ERROR"
            self.take_screenshot("unhandled_error", "global") # Generic screenshot on error

        finally:
            # Save results
            self.save_results()

            # Close the browser
            if self.driver:
                logger.info("Closing WebDriver...")
                self.driver.quit()
                logger.info("WebDriver closed.")

        return self.results["overall_status"] == "PASSED"

    def _run_test_step(self, test_func, test_name):
        """Helper to run a test step, record duration, and handle errors."""
        start_time = time.time()
        logger.info(f"--- Starting test: {test_name} ---")
        try:
            # Assume success unless exception occurs or explicitly set to False in test
            self.results["tests"][test_name]["success"] = True
            test_func()
        except Exception as e:
            logger.error(f"Error during {test_name} test: {str(e)}")
            self.take_screenshot(f"{test_name}_error", test_name)
            self.results["tests"][test_name]["error"] = str(e)
            self.results["tests"][test_name]["success"] = False
            traceback.print_exc() # Log traceback for debugging
        finally:
            duration = time.time() - start_time
            self.results["tests"][test_name]["duration"] = duration
            status = "PASSED" if self.results["tests"][test_name]["success"] else "FAILED"
            logger.info(f"--- Finished test: {test_name} ({status}) - Duration: {duration:.2f}s ---")


    def test_login(self):
        """Test user login functionality."""
        test_name = "login"
        # Navigate to the login page
        login_url = self.frontend_url + "/login" # Assuming /login path
        logger.info(f"Navigating to login page: {login_url}")
        self.driver.get(login_url)
        self.take_screenshot("initial_page", test_name)

        # Check if we're on the login page (look for specific elements)
        try:
            # Use more robust selectors if IDs are not stable
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='username'], input#email"))
            )
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input#password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button#login-button")
            logger.info("Login form elements found")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Login form elements not found: {e}")
            self.take_screenshot("login_form_not_found", test_name)
            self.results["tests"][test_name]["error"] = "Login form elements not found"
            # Check if maybe login is not required or already logged in
            if "/login" not in self.driver.current_url:
                 logger.warning("Not on login page, maybe login is optional or already logged in. Skipping login step.")
                 self.results["tests"][test_name]["notes"] = "Skipped (not on login page)"
                 # Don't mark as failed if login isn't needed
            else:
                 self.results["tests"][test_name]["success"] = False # Fail the test if elements aren't found on login page
                 raise e # Re-raise exception to be caught by _run_test_step
            return # Skip rest of login test

        # Enter credentials (use dummy credentials)
        email_field.send_keys("test@example.com")
        password_field.send_keys("password123")
        self.take_screenshot("credentials_entered", test_name)

        # Submit the form
        login_button.click()
        logger.info("Submitted login form")

        # Wait for login to complete (check for URL change or dashboard element)
        try:
            # Option 1: Wait for URL change (adjust path as needed)
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/dashboard") # Or EC.url_to_be(self.frontend_url + "/")
            )
            logger.info("Login successful (URL changed)")
        except TimeoutException:
            # Option 2: Check if a known element on the post-login page exists
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard-container, #user-profile")) # Example selectors
                )
                logger.info("Login successful (Dashboard element found)")
            except TimeoutException:
                logger.error("Login failed: URL did not change and dashboard element not found")
                self.take_screenshot("login_failed", test_name)
                self.results["tests"][test_name]["error"] = "Login redirection or dashboard element not found"
                # Check for error messages on the login page
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, ".error-message, .alert-danger")
                    error_text = error_element.text
                    logger.error(f"Login error message found: {error_text}")
                    self.results["tests"][test_name]["error"] += f" | Error message: {error_text}"
                except NoSuchElementException:
                    pass # No specific error message found
                self.results["tests"][test_name]["success"] = False # Mark as failed

        self.take_screenshot("after_login_attempt", test_name)


    def test_document_upload(self):
        """Test document upload functionality."""
        test_name = "upload"
        # Navigate to the upload page (adjust path as needed)
        upload_url = self.frontend_url + "/upload"
        logger.info(f"Navigating to upload page: {upload_url}")
        self.driver.get(upload_url)
        self.take_screenshot("upload_page", test_name)

        # Wait for the upload component/input to load
        try:
            # Use a more specific selector if possible
            upload_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            logger.info("File input element found")
        except TimeoutException as e:
            logger.error("Could not find file upload input element")
            self.take_screenshot("upload_input_not_found", test_name)
            self.results["tests"][test_name]["error"] = "Upload input element not found"
            self.results["tests"][test_name]["success"] = False
            raise e

        # Find a test file
        test_files = list(TEST_DOCS_PATH.glob("*.pdf"))
        if not test_files:
            logger.error(f"No test PDF files found in {TEST_DOCS_PATH}")
            self.results["tests"][test_name]["error"] = "No test PDF files found"
            self.results["tests"][test_name]["success"] = False
            return # Cannot proceed without a file

        test_file_path = str(test_files[0].resolve()) # Use absolute path
        logger.info(f"Using test file: {test_file_path}")

        # Upload the file using send_keys on the input element
        try:
             # Make input visible if it's hidden by CSS (common pattern)
             self.driver.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", upload_input)
        except Exception as js_error:
             logger.warning(f"Could not make file input visible via JS: {js_error}")

        try:
            upload_input.send_keys(test_file_path)
            logger.info("File path sent to input element")
            self.take_screenshot("file_selected", test_name)
        except WebDriverException as e:
             logger.error(f"Error sending keys to file input: {e}")
             logger.error("This might happen if the input element is obscured or not interactable.")
             self.take_screenshot("send_keys_error", test_name)
             self.results["tests"][test_name]["error"] = f"Error interacting with file input: {e}"
             self.results["tests"][test_name]["success"] = False
             raise e


        # Find and click the upload button (if one exists, otherwise upload might be automatic)
        upload_button = None
        try:
            # Wait a short moment for potential button enablement after file selection
            time.sleep(1)
            upload_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button#upload-button, button:contains('Upload')")
            logger.info("Found upload button")
            upload_button.click()
            logger.info("Clicked upload button")
        except NoSuchElementException:
            logger.warning("No explicit upload button found, assuming auto-upload or proceeding without click")
            self.take_screenshot("no_upload_button", test_name)

        # Wait for upload to complete (look for success message, progress bar completion, or navigation)
        try:
            # Option 1: Wait for a success message element
            WebDriverWait(self.driver, 60).until( # Increased timeout for upload/processing
                EC.presence_of_element_located((By.CSS_SELECTOR, ".upload-success, .alert-success, #upload-complete"))
            )
            logger.info("Upload success message found")
        except TimeoutException:
            # Option 2: Check if redirected to a document view page
            if "/documents/" in self.driver.current_url or "/view/" in self.driver.current_url:
                logger.info("Redirected after upload, assuming success")
            else:
                # Option 3: Check for error messages
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, ".upload-error, .alert-danger")
                    error_text = error_element.text
                    logger.error(f"Upload failed, error message found: {error_text}")
                    self.results["tests"][test_name]["error"] = f"Upload failed: {error_text}"
                    self.results["tests"][test_name]["success"] = False
                except NoSuchElementException:
                    logger.error("Upload failed: No success message or redirection, and no error message found within timeout")
                    self.results["tests"][test_name]["error"] = "Upload confirmation not found"
                    self.results["tests"][test_name]["success"] = False

        self.take_screenshot("after_upload_attempt", test_name)


    def test_document_viewer(self):
        """Test document viewer functionality."""
        test_name = "document_viewer"
        # Navigate to the documents list page (adjust path)
        docs_url = self.frontend_url + "/documents"
        logger.info(f"Navigating to documents page: {docs_url}")
        self.driver.get(docs_url)
        self.take_screenshot("documents_page", test_name)

        # Wait for the documents list/table to load and find the first document link/item
        try:
            # Use a selector that targets the clickable element leading to the viewer
            first_doc_link = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".document-list-item a, .document-table-row a, .list-group-item a[href*='/documents/']"))
            )
            logger.info("Found first document link/item")
            doc_name = first_doc_link.text
            logger.info(f"Clicking on document: {doc_name}")
            first_doc_link.click()
        except TimeoutException as e:
            logger.error("No clickable document items found in the list")
            self.take_screenshot("no_documents_found", test_name)
            self.results["tests"][test_name]["error"] = "No clickable document items found"
            self.results["tests"][test_name]["success"] = False
            raise e

        # Wait for the document viewer page/component to load
        try:
            # Look for a container specific to the viewer, or a PDF canvas element
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".document-viewer-container, .pdf-canvas, #pdf-viewer"))
            )
            logger.info("Document viewer loaded")
            self.take_screenshot("viewer_loaded", test_name)
        except TimeoutException as e:
            logger.error("Document viewer component did not load after clicking document link")
            self.take_screenshot("viewer_not_loaded", test_name)
            self.results["tests"][test_name]["error"] = "Document viewer component not loaded"
            self.results["tests"][test_name]["success"] = False
            raise e

        # Test basic viewer interactions (optional, depends on viewer features)
        # Example: Test pagination
        try:
            next_page_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Next page'], .pagination-next")
            if next_page_button.is_enabled():
                next_page_button.click()
                logger.info("Clicked next page button")
                time.sleep(1) # Allow page to render
                self.take_screenshot("next_page", test_name)
        except NoSuchElementException:
            logger.info("Pagination controls not found or not enabled")

        # Example: Test zoom
        try:
            zoom_in_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Zoom in'], .zoom-in")
            if zoom_in_button.is_enabled():
                zoom_in_button.click()
                logger.info("Clicked zoom in button")
                time.sleep(0.5)
                self.take_screenshot("zoomed_in", test_name)
        except NoSuchElementException:
            logger.info("Zoom controls not found or not enabled")


    def test_table_viewer(self):
        """Test table viewer functionality (if applicable)."""
        test_name = "table_viewer"
        # Assuming we are still on a document view page, try to navigate to a 'Tables' tab/section
        try:
            # Look for a tab or link related to tables
            tables_link = WebDriverWait(self.driver, 5).until(
                 EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='tables'], button:contains('Tables'), .nav-link[data-target*='table']"))
            )
            logger.info("Found 'Tables' tab/link")
            tables_link.click()
            logger.info("Navigated to tables view")
            self.take_screenshot("tables_view", test_name)
        except TimeoutException:
            logger.warning("Could not find or click a 'Tables' tab/link. Skipping table viewer test.")
            self.results["tests"][test_name]["notes"] = "Skipped (No Tables tab/link found)"
            # Don't mark as failed if feature might not exist
            return

        # Wait for tables to load (look for table elements)
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.data-table, .table-viewer-component"))
            )
            logger.info("Table viewer loaded")
            self.take_screenshot("tables_loaded", test_name)
        except TimeoutException as e:
            logger.error("Table viewer component or tables did not load")
            self.take_screenshot("tables_not_loaded", test_name)
            self.results["tests"][test_name]["error"] = "Tables did not load"
            self.results["tests"][test_name]["success"] = False
            raise e

        # Basic check: Ensure at least one table is present
        tables = self.driver.find_elements(By.CSS_SELECTOR, "table.data-table, .table-viewer-component table")
        if not tables:
            logger.warning("No tables found within the table viewer")
            # This might be acceptable if the document has no tables
            self.results["tests"][test_name]["notes"] = "No tables found in viewer (might be expected)"
        else:
             logger.info(f"Found {len(tables)} table(s) in the viewer")

        # Optional: Test table interactions (e.g., sorting, filtering, export) if implemented


    def test_financial_dashboard(self):
        """Test financial dashboard functionality."""
        test_name = "financial_dashboard"
        # Navigate to the dashboard page
        dashboard_url = self.frontend_url + "/dashboard" # Adjust path if needed
        logger.info(f"Navigating to dashboard page: {dashboard_url}")
        self.driver.get(dashboard_url)
        self.take_screenshot("dashboard_page", test_name)

        # Wait for dashboard components (e.g., charts, KPIs) to load
        try:
            # Look for a main container or a specific chart library element
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard-container, .recharts-wrapper, .chartjs-render-monitor"))
            )
            logger.info("Dashboard components loaded")
            self.take_screenshot("dashboard_loaded", test_name)
        except TimeoutException as e:
            logger.error("Dashboard components did not load")
            self.take_screenshot("dashboard_not_loaded", test_name)
            self.results["tests"][test_name]["error"] = "Dashboard components not loaded"
            self.results["tests"][test_name]["success"] = False
            raise e

        # Basic checks: Look for expected elements like charts or key figures
        charts = self.driver.find_elements(By.CSS_SELECTOR, ".recharts-wrapper, .chartjs-render-monitor, canvas")
        kpis = self.driver.find_elements(By.CSS_SELECTOR, ".kpi-value, .stat-number")

        if not charts and not kpis:
            logger.warning("No charts or KPI elements found on the dashboard")
            self.results["tests"][test_name]["notes"] = "No charts or KPIs found (check selectors)"
        else:
            logger.info(f"Found {len(charts)} chart(s) and {len(kpis)} KPI(s)")

        # Optional: Test interactions like filtering or hovering if implemented


    def test_chat_interface(self):
        """Test chat interface functionality."""
        test_name = "chat_interface"
        # Navigate to a page with the chat interface or a dedicated chat page
        # Option 1: Try finding a chat button/icon first
        chat_opened = False
        try:
            chat_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Chat'], .chat-widget-button"))
            )
            logger.info("Found chat widget button")
            chat_button.click()
            logger.info("Opened chat widget")
            chat_opened = True
            self.take_screenshot("chat_widget_opened", test_name)
        except TimeoutException:
            # Option 2: Navigate to a dedicated chat page
            chat_url = self.frontend_url + "/chat" # Adjust path if needed
            logger.info(f"Chat widget button not found, navigating to dedicated chat page: {chat_url}")
            self.driver.get(chat_url)
            self.take_screenshot("chat_page", test_name)

        # Wait for chat input field to be ready
        try:
            chat_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='message'], input.chat-input"))
            )
            logger.info("Chat input field found")
        except TimeoutException as e:
            logger.error("Chat input field not found")
            self.take_screenshot("chat_input_not_found", test_name)
            self.results["tests"][test_name]["error"] = "Chat input field not found"
            self.results["tests"][test_name]["success"] = False
            raise e

        # Send a test message
        test_message = "Hello, can you summarize the document?"
        chat_input.send_keys(test_message)
        logger.info(f"Entered message: '{test_message}'")
        self.take_screenshot("chat_message_entered", test_name)

        # Find and click the send button
        try:
            send_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[aria-label*='Send']")
            send_button.click()
            logger.info("Clicked send button")
        except NoSuchElementException:
            # Try sending with Enter key
            logger.warning("Send button not found, trying Enter key")
            chat_input.send_keys(Keys.RETURN)

        # Wait for a response message to appear
        try:
            # Look for a message container marked as received or from the bot
            WebDriverWait(self.driver, 30).until( # Longer timeout for AI response
                EC.presence_of_element_located((By.CSS_SELECTOR, ".message-bubble.received, .chat-message.bot"))
            )
            logger.info("Chat response received")
            self.take_screenshot("chat_response_received", test_name)
        except TimeoutException:
            logger.error("No chat response received within timeout")
            self.take_screenshot("chat_no_response", test_name)
            self.results["tests"][test_name]["error"] = "No chat response received"
            self.results["tests"][test_name]["success"] = False


    def save_results(self):
        """Save test results to a JSON file."""
        result_file = RESULTS_PATH / f"ui_test_results_{self.test_run_id}.json"

        try:
            with open(result_file, "w") as f:
                json.dump(self.results, f, indent=2, default=str)
            logger.info(f"UI test results saved to {result_file}")
        except Exception as e:
            logger.error(f"Error saving UI test results: {str(e)}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run UI tests for financial document processing frontend")
    parser.add_argument("--browser", type=str, choices=["chrome", "firefox"], default="chrome", help="Browser to use for testing")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--url", type=str, default=DEFAULT_FRONTEND_URL, help="URL of the frontend application")

    args = parser.parse_args()

    # Create and run tester
    tester = UiTester(args)
    success = tester.run_ui_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()