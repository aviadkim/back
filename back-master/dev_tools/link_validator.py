#!/usr/bin/env python3
"""
Link & API Validator
------------------
This script validates all links in your web application and checks
that API endpoints return valid responses according to expected schemas.

Usage:
1. Run in your GitHub Codespace
2. Provide the URL of your deployed app or local development server
3. Get a report of broken links and API validation issues
"""

import os
import sys
import re
import json
import time
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import concurrent.futures
from jsonschema import validate, exceptions as schema_exceptions
from datetime import datetime

class LinkApiValidator:
    def __init__(self, base_url, concurrency=5):
        self.base_url = base_url
        self.concurrency = concurrency
        self.visited_links = set()
        self.broken_links = []
        self.api_issues = []
        self.api_schemas = {}
        self.load_api_schemas()
    
    def load_api_schemas(self):
        """Load API schemas from schema directory if it exists"""
        schema_dir = os.path.join(os.getcwd(), "schemas")
        if os.path.exists(schema_dir):
            for filename in os.listdir(schema_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(schema_dir, filename), 'r') as f:
                            schema = json.load(f)
                            endpoint = filename.replace(".json", "")
                            self.api_schemas[endpoint] = schema
                            print(f"Loaded schema for {endpoint}")
                    except Exception as e:
                        print(f"Error loading schema {filename}: {str(e)}")
    
    def validate(self):
        """Validate links and API endpoints"""
        print(f"Starting validation of {self.base_url}")
        start_time = time.time()
        
        # Start with the base URL
        self.validate_url(self.base_url)
        
        # Process discovered links with concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            while True:
                # Get unvisited links
                links_to_visit = [link for link in self.discovered_links if link not in self.visited_links]
                if not links_to_visit:
                    break
                
                # Visit links concurrently
                futures = [executor.submit(self.validate_url, link) for link in links_to_visit[:self.concurrency]]
                concurrent.futures.wait(futures)
        
        # Generate report
        self.generate_report()
        print(f"Validation completed in {time.time() - start_time:.2f} seconds")
    
    def validate_url(self, url):
        """Validate a single URL"""
        if url in self.visited_links:
            return
        
        self.visited_links.add(url)
        print(f"Validating: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            # Check if it's an API endpoint (based on URL pattern and response)
            if "/api/" in url or response.headers.get("Content-Type", "").startswith("application/json"):
                self.validate_api_endpoint(url, response)
            else:
                # It's a web page, check for broken links
                if response.status_code >= 400:
                    self.broken_links.append({
                        "url": url,
                        "status": response.status_code,
                        "reason": response.reason
                    })
                else:
                    # Parse the page for more links
                    self.extract_links(url, response.text)
        except requests.exceptions.RequestException as e:
            self.broken_links.append({
                "url": url,
                "status": None,
                "reason": str(e)
            })
    
    def validate_api_endpoint(self, url, response):
        """Validate API response against schema if available"""
        # Extract endpoint name from URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        endpoint = path.strip("/").replace("/", "_")
        
        try:
            if response.status_code >= 400:
                self.api_issues.append({
                    "endpoint": url,
                    "status": response.status_code,
                    "reason": response.reason,
                    "type": "status_error"
                })
                return
            
            # Try to parse response as JSON
            try:
                data = response.json()
            except ValueError:
                self.api_issues.append({
                    "endpoint": url,
                    "status": response.status_code,
                    "reason": "Response is not valid JSON",
                    "type": "json_error"
                })
                return
            
            # Validate against schema if available
            if endpoint in self.api_schemas:
                try:
                    validate(instance=data, schema=self.api_schemas[endpoint])
                except schema_exceptions.ValidationError as e:
                    self.api_issues.append({
                        "endpoint": url,
                        "status": response.status_code,
                        "reason": f"Schema validation failed: {e.message}",
                        "type": "schema_error"
                    })
        except Exception as e:
            self.api_issues.append({
                "endpoint": url,
                "status": None,
                "reason": f"Error validating API: {str(e)}",
                "type": "validation_error"
            })
    
    def extract_links(self, base_url, html_content):
        """Extract links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip anchor links, javascript, and mailto
            if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            # Convert relative URL to absolute
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            
            # Only include links from the same domain
            if urlparse(href).netloc == urlparse(self.base_url).netloc:
                self.discovered_links.add(href)
    
    def generate_report(self):
        """Generate validation report"""
        os.makedirs("validation", exist_ok=True)
        
        # Save raw data as JSON
        with open("validation/validation_data.json", "w") as f:
            json.dump({
                "broken_links": self.broken_links,
                "api_issues": self.api_issues,
                "visited_links": list(self.visited_links)
            }, f, indent=2)
        
        # Generate markdown report
        with open("validation/validation_report.md", "w") as f:
            f.write("# Link and API Validation Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Base URL: {self.base_url}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Links Checked**: {len(self.visited_links)}\n")
            f.write(f"- **Broken Links**: {len(self.broken_links)}\n")
            f.write(f"- **API Issues**: {len(self.api_issues)}\n\n")
            
            if self.broken_links:
                f.write("## Broken Links\n\n")
                for link in self.broken_links:
                    f.write(f"### {link['url']}\n")
                    f.write(f"- **Status**: {link['status']}\n")
                    f.write(f"- **Reason**: {link['reason']}\n\n")
            
            if self.api_issues:
                f.write("## API Issues\n\n")
                for issue in self.api_issues:
                    f.write(f"### {issue['endpoint']}\n")
                    f.write(f"- **Status**: {issue['status']}\n")
                    f.write(f"- **Type**: {issue['type']}\n")
                    f.write(f"- **Reason**: {issue['reason']}\n\n")
        
        print(f"Report saved to: validation/validation_report.md")

if __name__ == "__main__":
    print("Link & API Validator")
    print("------------------")
    
    # Parse arguments
    base_url = "http://localhost:3000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    validator = LinkApiValidator(base_url)
    validator.validate()