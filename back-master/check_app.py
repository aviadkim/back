import os
import requests
import socket
import subprocess

def check_port(port):
    """Check if a port is in use"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', port))
        s.close()
        return False
    except:
        return True

def get_running_process(keyword):
    """Get process containing the keyword"""
    try:
        output = subprocess.check_output(['ps', 'aux']).decode('utf-8')
        for line in output.split('\n'):
            if keyword in line and 'grep' not in line:
                return line
        return None
    except:
        return None

# Check common ports
ports_to_check = [5000, 5001, 8080]
print("Checking ports...")
for port in ports_to_check:
    if check_port(port):
        print(f"Port {port} is in use")
        # Try to get health check
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            print(f"Health check response ({port}): {response.status_code}")
            print(response.text[:100] + "..." if len(response.text) > 100 else response.text)
        except:
            print(f"No response from health check on port {port}")
    else:
        print(f"Port {port} is not in use")

# Look for running Flask processes
print("\nLooking for running Flask processes...")
process = get_running_process('python')
if process:
    print(f"Found Python process: {process}")
else:
    print("No Python process found")
