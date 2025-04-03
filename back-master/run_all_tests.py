import os
import sys
import subprocess
import argparse
import time

def run_tests(test_type='all', verbose=False):
    """Run tests of specified type"""
    print(f"\n{'='*50}")
    print(f"Running {test_type} tests")
    print(f"{'='*50}")
    
    v_flag = '-v' if verbose else ''
    
    if test_type == 'unit' or test_type == 'all':
        print("\nRunning unit tests...")
        subprocess.run(f"python -m pytest tests/unit {v_flag}", shell=True)
    
    if test_type == 'integration' or test_type == 'all':
        print("\nRunning integration tests...")
        subprocess.run(f"python -m pytest tests/integration {v_flag}", shell=True)
    
    if test_type == 'e2e' or test_type == 'all':
        print("\nRunning end-to-end tests...")
        subprocess.run(f"python -m pytest tests/e2e {v_flag}", shell=True)
    
    if test_type == 'api':
        print("\nRunning API tests...")
        subprocess.run("python tests/api_tests.py", shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run tests for Financial Document Analysis System')
    parser.add_argument('--type', choices=['all', 'unit', 'integration', 'e2e', 'api'], 
                        default='all', help='Type of tests to run')
    parser.add_argument('--verbose', action='store_true', help='Show verbose output')
    
    args = parser.parse_args()
    run_tests(args.type, args.verbose)
