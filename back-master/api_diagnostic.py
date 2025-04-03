#!/usr/bin/env python3
"""
Diagnostic tool for API endpoints.
This script attempts to call all API endpoints and reports their status.
"""
import requests
import json
import sys
import os
import time
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("APIDiagnostic")

class APIDiagnostic:
    """Diagnostic tool for checking API endpoints"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.document_id = None
        self.results = []
        
        # Check if tabulate is available
        try:
            import tabulate
            self.has_tabulate = True
        except ImportError:
            self.has_tabulate = False
            logger.warning("tabulate package not installed. Using simple format for results.")
    
    def run_diagnostics(self):
        """Run diagnostics on all API endpoints"""
        logger.info("===== Starting API Diagnostics =====")
        
        # Basic endpoints
        self.check_endpoint('GET', '/health', "Health Check")
        self.check_endpoint('GET', '/', "Root Endpoint")
        
        # Document endpoints
        self.check_endpoint('GET', '/api/documents', "List Documents")
        
        # First get document ID if available
        try:
            response = self.session.get(f"{self.base_url}/api/documents")
            if response.status_code == 200:
                documents = response.json().get('documents', [])
                if documents:
                    self.document_id = documents[0].get('document_id')
                    logger.info(f"Found document ID: {self.document_id}")
        except:
            pass
            
        # Document specific endpoints
        if self.document_id:
            self.check_endpoint('GET', f'/api/documents/{self.document_id}', "Document Details")
            self.check_endpoint('GET', f'/api/documents/{self.document_id}/financial', "Financial Data")
            self.check_endpoint('GET', f'/api/documents/{self.document_id}/advanced_analysis', "Advanced Analysis")
            
            # Custom table endpoint
            table_spec = {
                "columns": ["isin", "name", "currency", "price"],
                "sort_by": "name",
                "sort_order": "asc"
            }
            self.check_endpoint('POST', f'/api/documents/{self.document_id}/custom_table', "Custom Table", 
                                data=table_spec)
                                
            # Q&A endpoint
            question_data = {
                "document_id": self.document_id,
                "question": "What is the total portfolio value?"
            }
            self.check_endpoint('POST', '/api/qa/ask', "Q&A System", data=question_data)
        else:
            logger.warning("No document ID found for testing document-specific endpoints")
            
        # Check PDF processing endpoint
        self.check_endpoint('GET', '/api/pdf/status', "PDF Processing Status")
        
        # Print results
        self.print_results()
        
        # Return overall status
        success_count = sum(1 for result in self.results if result['status'] == 'OK')
        total_count = len(self.results)
        
        logger.info(f"Overall success rate: {success_count}/{total_count} endpoints working")
        return success_count == total_count
    
    def check_endpoint(self, method, path, name, data=None):
        """Check a specific endpoint"""
        url = f"{self.base_url}{path}"
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = self.session.get(url, timeout=5)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=5)
            else:
                logger.error(f"Unsupported method: {method}")
                return
                
            duration = round((time.time() - start_time) * 1000)
            
            if response.status_code in (200, 201):
                status = "OK"
                try:
                    response_data = response.json()
                    response_preview = json.dumps(response_data)[:100] + "..." if len(json.dumps(response_data)) > 100 else json.dumps(response_data)
                except:
                    response_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
            else:
                status = "FAIL"
                response_preview = response.text[:100] if response.text else f"Status code: {response.status_code}"
                
            self.results.append({
                'name': name,
                'method': method,
                'url': path,
                'status_code': response.status_code,
                'status': status,
                'duration': duration,
                'response': response_preview
            })
            
        except requests.exceptions.ConnectionError:
            self.results.append({
                'name': name,
                'method': method,
                'url': path,
                'status_code': 'N/A',
                'status': 'FAIL',
                'duration': 0,
                'response': 'Connection error'
            })
        except Exception as e:
            self.results.append({
                'name': name,
                'method': method,
                'url': path,
                'status_code': 'N/A',
                'status': 'FAIL',
                'duration': 0,
                'response': str(e)
            })
    
    def print_results(self):
        """Print the results in a table format"""
        logger.info("\n===== API Diagnostics Results =====")
        
        if self.has_tabulate:
            from tabulate import tabulate
            headers = ["Name", "Method", "Endpoint", "Status", "Code", "Response Time", "Response Preview"]
            table_data = []
            
            for result in self.results:
                status_color = "\033[92m" if result['status'] == 'OK' else "\033[91m"  # Green for OK, Red for FAIL
                reset_color = "\033[0m"
                
                table_data.append([
                    result['name'],
                    result['method'],
                    result['url'],
                    f"{status_color}{result['status']}{reset_color}",
                    result['status_code'],
                    f"{result['duration']} ms",
                    result['response']
                ])
                
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            # Simple format if tabulate is not available
            for result in self.results:
                status_marker = "✅" if result['status'] == 'OK' else "❌"
                status_text = f"{status_marker} {result['status']}"
                print(f"{result['name']} ({result['method']} {result['url']}): {status_text} ({result['status_code']}) - {result['duration']} ms")

def main():
    parser = argparse.ArgumentParser(description="API Diagnostics Tool")
    parser.add_argument("--url", default="http://localhost:5001", help="Base URL for the API")
    args = parser.parse_args()
    
    # Check if the server is running
    try:
        requests.get(f"{args.url}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to server at {args.url}")
        logger.error("Make sure the server is running.")
        return 1
        
    # Run diagnostics
    diagnostic = APIDiagnostic(args.url)
    success = diagnostic.run_diagnostics()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
