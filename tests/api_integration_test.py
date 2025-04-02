#!/usr/bin/env python3
"""
API Integration Test for Financial Document Processing System
========================================================

This script tests the complete API flow including:
- Document upload
- Processing status checks
- Retrieval of processed data
- Table extraction
- Financial analysis
- User interaction with chatbot

Usage:
    python3 api_integration_test.py [--verbose] [--file PATH_TO_PDF]

Requirements:
    - Flask server running
    - Test PDF document in test_documents/ or specified via --file
    - API keys configured in .env
"""

import os
import sys
import json
import time
import logging
import argparse
import requests
import traceback
from pathlib import Path
from dotenv import load_dotenv
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tests/api_integration_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ApiIntegrationTest")

# Load environment variables
load_dotenv()

# Constants
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000") # Allow overriding via env var
TEST_DOCS_PATH = Path("test_documents")
RESULTS_PATH = Path("test_results")

# Ensure results directory exists
RESULTS_PATH.mkdir(exist_ok=True)

class ApiIntegrationTester:
    """API Integration test orchestrator."""

    def __init__(self, args):
        self.verbose = args.verbose
        self.test_file = args.file
        self.session = requests.Session()
        self.document_id = None
        self.results = {
            "timestamp": time.time(),
            "test_file": None,
            "upload": None,
            "processing": None,
            "document_info": None,
            "tables": None,
            "financial_entities": None,
            "chat_responses": None
        }

    def run_integration_test(self):
        """Run the complete API integration test flow."""
        logger.info("Starting API integration test")

        try:
            # Step 0: Check API health
            if not self.check_api_health():
                logger.error("API is not healthy, cannot continue test")
                return False

            # Step 1: Upload document
            if not self.upload_document():
                logger.error("Failed to upload document, cannot continue test")
                return False

            # Step 2: Check processing status
            if not self.check_processing_status():
                 logger.warning("Document processing did not complete successfully, continuing with available data...")
                 # Allow test to continue to check retrieval endpoints even if processing failed

            # Step 3: Get document information
            self.get_document_info()

            # Step 4: Extract tables
            self.extract_tables()

            # Step 5: Get financial entities
            self.get_financial_entities()

            # Step 6: Test chatbot interactions
            self.test_chatbot()

            # Save results
            self.save_results()

            logger.info("API integration test completed")
            # Check overall success based on critical steps
            overall_success = (
                self.results.get("upload", {}).get("success", False) and
                self.results.get("processing", {}).get("success", False) # Consider processing success critical
            )
            logger.info(f"Overall test status: {'SUCCESS' if overall_success else 'FAILED'}")
            return overall_success

        except Exception as e:
            logger.error(f"API integration test failed: {str(e)}")
            traceback.print_exc()
            self.save_results() # Save partial results on error
            return False

    def check_api_health(self):
        """Check if the API server is running and healthy."""
        logger.info("Step 0: Checking API health...")
        health_url = f"{API_BASE_URL}/api/health"
        try:
            response = self.session.get(health_url, timeout=5)
            if response.status_code == 200:
                logger.info("API is healthy")
                return True
            else:
                logger.error(f"API health check failed with status code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not connect to API at {API_BASE_URL}: {e}")
            return False

    def upload_document(self):
        """Upload a test document to the API."""
        logger.info("Step 1: Uploading document...")

        # Find a test file if not specified
        file_path = self.test_file
        if not file_path:
            test_files = list(TEST_DOCS_PATH.glob("*.pdf"))
            if not test_files:
                logger.error(f"No test PDF files found in {TEST_DOCS_PATH}")
                self.results["upload"] = {"success": False, "error": "No test PDF files found"}
                return False
            file_path = test_files[0] # Use the first found file

        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"Test file not found: {file_path}")
            self.results["upload"] = {"success": False, "error": f"Test file not found: {file_path}"}
            return False

        self.results["test_file"] = str(file_path)
        logger.info(f"Uploading file: {file_path}")

        try:
            with open(file_path, "rb") as f:
                response = self.session.post(
                    f"{API_BASE_URL}/api/upload",
                    files={"file": (file_path.name, f)},
                    data={"language": "auto"} # Assuming language detection is handled
                )

            if response.status_code != 200:
                logger.error(f"Upload failed with status code {response.status_code}. Response: {response.text}")
                self.results["upload"] = {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                return False

            # Parse response
            result = response.json()
            self.document_id = result.get("document_id")

            if not self.document_id:
                logger.error(f"No document_id returned from upload. Response: {result}")
                self.results["upload"] = {
                    "success": False,
                    "error": "No document_id returned",
                    "response": result
                }
                return False

            logger.info(f"Document uploaded successfully. ID: {self.document_id}")
            self.results["upload"] = {
                "success": True,
                "document_id": self.document_id,
                "response": result
            }
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Error uploading document (RequestException): {str(e)}")
            self.results["upload"] = {"success": False, "error": f"RequestException: {str(e)}"}
            return False
        except json.JSONDecodeError as e:
             logger.error(f"Error decoding upload response JSON: {str(e)}. Response text: {response.text}")
             self.results["upload"] = {"success": False, "error": f"JSONDecodeError: {str(e)}", "response_text": response.text}
             return False
        except Exception as e:
            logger.error(f"Unexpected error uploading document: {str(e)}")
            self.results["upload"] = {"success": False, "error": f"Unexpected error: {str(e)}"}
            return False

    def check_processing_status(self):
        """Check document processing status until complete."""
        if not self.document_id:
            logger.error("No document_id available for status check")
            return False

        logger.info("Step 2: Checking processing status...")
        status_url = f"{API_BASE_URL}/api/documents/{self.document_id}/status"

        max_retries = 60 # Increased retries for potentially long processing
        retry_interval = 5 # Increased interval
        status_results = []
        final_status = "unknown"

        for i in range(max_retries):
            try:
                response = self.session.get(status_url)
                if response.status_code != 200:
                    logger.error(f"Status check failed with code {response.status_code}. Response: {response.text}")
                    # Don't retry immediately on server error, wait
                    time.sleep(retry_interval)
                    continue

                result = response.json()
                status = result.get("status")
                final_status = status # Keep track of the last known status
                status_results.append({
                    "timestamp": time.time(),
                    "status": status,
                    "details": result
                })

                logger.info(f"Processing status: {status} (Attempt {i+1}/{max_retries})")

                if status == "completed":
                    logger.info("Document processing completed successfully.")
                    self.results["processing"] = {
                        "success": True,
                        "final_status": status,
                        "attempts": i + 1,
                        "status_history": status_results
                    }
                    return True
                elif status == "failed":
                    logger.error(f"Document processing failed. Details: {result.get('error', 'No details provided')}")
                    self.results["processing"] = {
                        "success": False,
                        "final_status": status,
                        "error": result.get('error', 'Processing failed'),
                        "attempts": i + 1,
                        "status_history": status_results
                    }
                    return False # Stop checking if failed

                time.sleep(retry_interval)

            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking status (RequestException): {str(e)}")
                time.sleep(retry_interval * 2) # Wait longer if connection error
            except json.JSONDecodeError as e:
                 logger.error(f"Error decoding status response JSON: {str(e)}. Response text: {response.text}")
                 time.sleep(retry_interval)
            except Exception as e:
                logger.error(f"Unexpected error checking status: {str(e)}")
                time.sleep(retry_interval)

        logger.warning(f"Processing did not complete within the timeout ({max_retries * retry_interval}s). Last status: {final_status}")
        self.results["processing"] = {
            "success": False,
            "final_status": final_status,
            "error": "Processing timeout",
            "attempts": max_retries,
            "status_history": status_results
        }
        return False

    def get_document_info(self):
        """Get processed document information."""
        if not self.document_id:
            logger.error("No document_id available for info retrieval")
            return

        logger.info("Step 3: Getting document information...")
        info_url = f"{API_BASE_URL}/api/documents/{self.document_id}"

        try:
            response = self.session.get(info_url)
            if response.status_code != 200:
                logger.error(f"Failed to get document info: {response.status_code}. Response: {response.text}")
                self.results["document_info"] = {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                return

            result = response.json()
            page_count = len(result.get('pages', [])) if isinstance(result.get('pages'), list) else 0
            logger.info(f"Document info retrieved successfully ({page_count} pages)")

            self.results["document_info"] = {
                "success": True,
                "page_count": page_count,
                "document": result # Store the full document info
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting document info (RequestException): {str(e)}")
            self.results["document_info"] = {"success": False, "error": f"RequestException: {str(e)}"}
        except json.JSONDecodeError as e:
             logger.error(f"Error decoding document info JSON: {str(e)}. Response text: {response.text}")
             self.results["document_info"] = {"success": False, "error": f"JSONDecodeError: {str(e)}", "response_text": response.text}
        except Exception as e:
            logger.error(f"Unexpected error getting document info: {str(e)}")
            self.results["document_info"] = {"success": False, "error": f"Unexpected error: {str(e)}"}

    def extract_tables(self):
        """Extract tables from the document."""
        if not self.document_id:
            logger.error("No document_id available for table extraction")
            return

        logger.info("Step 4: Extracting tables...")
        tables_url = f"{API_BASE_URL}/api/documents/{self.document_id}/tables"

        try:
            response = self.session.get(tables_url)
            if response.status_code != 200:
                logger.error(f"Failed to extract tables: {response.status_code}. Response: {response.text}")
                self.results["tables"] = {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                return

            result = response.json()
            # Assuming result format is {"tables": {page_num: [table1, table2]}}
            tables_data = result.get("tables", {})
            table_count = sum(len(tables) for page, tables in tables_data.items())
            logger.info(f"Tables extracted successfully ({table_count} tables)")

            self.results["tables"] = {
                "success": True,
                "table_count": table_count,
                "tables": tables_data # Store the extracted tables
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error extracting tables (RequestException): {str(e)}")
            self.results["tables"] = {"success": False, "error": f"RequestException: {str(e)}"}
        except json.JSONDecodeError as e:
             logger.error(f"Error decoding tables JSON: {str(e)}. Response text: {response.text}")
             self.results["tables"] = {"success": False, "error": f"JSONDecodeError: {str(e)}", "response_text": response.text}
        except Exception as e:
            logger.error(f"Unexpected error extracting tables: {str(e)}")
            self.results["tables"] = {"success": False, "error": f"Unexpected error: {str(e)}"}

    def get_financial_entities(self):
        """Get financial entities from the document."""
        if not self.document_id:
            logger.error("No document_id available for entity extraction")
            return

        logger.info("Step 5: Getting financial entities...")
        entities_url = f"{API_BASE_URL}/api/documents/{self.document_id}/entities"

        try:
            response = self.session.get(entities_url)
            if response.status_code != 200:
                logger.error(f"Failed to get financial entities: {response.status_code}. Response: {response.text}")
                self.results["financial_entities"] = {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                return

            result = response.json()
            # Assuming result format is {"entities": [entity1, entity2]}
            entities_data = result.get("entities", [])
            entity_count = len(entities_data)
            logger.info(f"Financial entities extracted successfully ({entity_count} entities)")

            self.results["financial_entities"] = {
                "success": True,
                "entity_count": entity_count,
                "entities": entities_data # Store the extracted entities
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting financial entities (RequestException): {str(e)}")
            self.results["financial_entities"] = {"success": False, "error": f"RequestException: {str(e)}"}
        except json.JSONDecodeError as e:
             logger.error(f"Error decoding entities JSON: {str(e)}. Response text: {response.text}")
             self.results["financial_entities"] = {"success": False, "error": f"JSONDecodeError: {str(e)}", "response_text": response.text}
        except Exception as e:
            logger.error(f"Unexpected error getting financial entities: {str(e)}")
            self.results["financial_entities"] = {"success": False, "error": f"Unexpected error: {str(e)}"}

    def test_chatbot(self):
        """Test chatbot interactions with the document."""
        if not self.document_id:
            logger.error("No document_id available for chatbot test")
            return

        logger.info("Step 6: Testing chatbot interactions...")
        chat_url = f"{API_BASE_URL}/api/documents/{self.document_id}/chat"

        # Define test questions
        test_questions = [
            "What is the total number of tables in this document?",
            "Can you list all ISIN numbers found in the document?",
            "What are the main financial metrics in this document?",
            "Summarize the document content.",
            "What is the date of this document?"
        ]

        chat_results = []
        all_successful = True

        for question in test_questions:
            logger.info(f"  Sending question: '{question}'")
            try:
                response = self.session.post(
                    chat_url,
                    json={"question": question},
                    timeout=60 # Longer timeout for potentially complex queries
                )

                if response.status_code != 200:
                    logger.error(f"Chatbot query failed: {response.status_code}. Response: {response.text}")
                    chat_results.append({
                        "question": question,
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    all_successful = False
                    continue

                result = response.json()
                logger.info(f"  Chatbot response received for: '{question}'")
                if self.verbose:
                    logger.info(f"    Response: {result.get('response')[:100]}...") # Log snippet

                chat_results.append({
                    "question": question,
                    "success": True,
                    "response": result.get("response"),
                    "response_time": result.get("response_time")
                })

            except requests.exceptions.RequestException as e:
                logger.error(f"Error in chatbot interaction (RequestException): {str(e)}")
                chat_results.append({"question": question, "success": False, "error": f"RequestException: {str(e)}"})
                all_successful = False
            except json.JSONDecodeError as e:
                 logger.error(f"Error decoding chatbot response JSON: {str(e)}. Response text: {response.text}")
                 chat_results.append({"question": question, "success": False, "error": f"JSONDecodeError: {str(e)}", "response_text": response.text})
                 all_successful = False
            except Exception as e:
                logger.error(f"Unexpected error in chatbot interaction: {str(e)}")
                chat_results.append({"question": question, "success": False, "error": f"Unexpected error: {str(e)}"})
                all_successful = False

        self.results["chat_responses"] = {
            "success": all_successful,
            "responses": chat_results
        }

    def save_results(self):
        """Save test results to a JSON file."""
        result_id = str(uuid.uuid4())[:8]
        result_file = RESULTS_PATH / f"api_integration_test_{result_id}.json"

        try:
            with open(result_file, "w") as f:
                json.dump(self.results, f, indent=2, default=str) # Use default=str for non-serializable types like Path
            logger.info(f"Test results saved to {result_file}")
        except Exception as e:
            logger.error(f"Error saving test results: {str(e)}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run API integration tests for financial document processing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--file", type=str, help="Path to specific test PDF file")

    args = parser.parse_args()

    # Create and run tester
    tester = ApiIntegrationTester(args)
    success = tester.run_integration_test()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()