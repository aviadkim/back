#!/usr/bin/env python3
"""
Comprehensive test runner for the vertical slice architecture
"""
import os
import sys
import subprocess
import argparse

def run_feature_tests(feature=None):
    """Run tests for a specific feature or all features"""
    if feature:
        cmd = f"pytest features/{feature}/tests/ -v"
    else:
        cmd = "pytest features/*/tests/ -v"
        
    print(f"\n===== Running Feature Tests: {feature or 'All'} =====")
    subprocess.run(cmd, shell=True)

def run_integration_tests():
    """Run integration tests"""
    print("\n===== Running Integration Tests =====")
    subprocess.run("pytest tests/integration/ -v", shell=True)

def run_api_tests():
    """Run API tests against running server"""
    print("\n===== Running API Tests =====")
    
    # First check if server is running
    try:
        import requests
        response = requests.get('http://localhost:5001/health')
        if response.status_code == 200:
            print("Server is running, proceeding with API tests")
        else:
            print(f"Server returned status {response.status_code}, tests may fail")
    except:
        print("WARNING: Server does not appear to be running on port 5001")
        print("Start server before running API tests with: python app.py")
    
    # Run API tests
    subprocess.run("pytest tests/api/ -v", shell=True)

def main():
    parser = argparse.ArgumentParser(description="Run tests for vertical slice architecture")
    parser.add_argument("--feature", help="Specific feature to test (e.g., pdf_processing)")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    
    args = parser.parse_args()
    
    if args.all:
        run_feature_tests()
        run_integration_tests()
        run_api_tests()
    elif args.feature:
        run_feature_tests(args.feature)
    elif args.integration:
        run_integration_tests()
    elif args.api:
        run_api_tests()
    else:
        # Default to running feature tests
        run_feature_tests()

if __name__ == "__main__":
    main()
