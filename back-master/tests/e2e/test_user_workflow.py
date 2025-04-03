import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="module")
def browser():
    """Create a headless browser for testing"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(10)
    yield browser
    browser.quit()

@pytest.mark.skip(reason="Frontend tests require Selenium to be set up")
def test_document_upload_workflow(browser):
    """Test the complete document upload workflow"""
    # Navigate to the frontend
    browser.get("http://localhost:5001")
    
    # Wait for page to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "uploadForm"))
    )
    
    # Upload a document
    file_input = browser.find_element(By.ID, "fileInput")
    file_input.send_keys("/path/to/sample.pdf")
    
    # Select language
    language_select = browser.find_element(By.ID, "languageSelect")
    language_select.send_keys("Hebrew + English")
    
    # Submit form
    upload_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Upload')]")
    upload_button.click()
    
    # Wait for upload to complete
    WebDriverWait(browser, 30).until(
        EC.visibility_of_element_located((By.ID, "uploadResult"))
    )
    
    # Verify upload success
    result_text = browser.find_element(By.ID, "uploadResultJson").text
    assert "document_id" in result_text
    
    # Refresh document list
    refresh_button = browser.find_element(By.ID, "refreshDocuments")
    refresh_button.click()
    
    # Wait for document list to update
    time.sleep(2)
    
    # Verify document appears in list
    document_list = browser.find_element(By.ID, "documentsList").text
    assert "Messos" in document_list or "sample.pdf" in document_list
