import os
import re

def update_frontend():
    """Update the frontend HTML file with enhanced features"""
    frontend_path = 'frontend/build/index.html'
    additions_path = 'frontend_additions.html'
    
    if not os.path.exists(frontend_path):
        print(f"Error: {frontend_path} not found")
        return False
    
    if not os.path.exists(additions_path):
        print(f"Error: {additions_path} not found")
        return False
    
    # Read files
    with open(frontend_path, 'r') as f:
        frontend_content = f.read()
    
    with open(additions_path, 'r') as f:
        additions_content = f.read()
    
    # Check if additions are already integrated
    if "Advanced Analysis" in frontend_content and "Custom Tables" in frontend_content:
        print("Frontend additions already integrated")
        return True
    
    # Find the closing body tag
    body_end_match = re.search(r'</body>', frontend_content)
    if not body_end_match:
        print("Could not find </body> tag in frontend HTML")
        return False
    
    body_end_pos = body_end_match.start()
    
    # Insert the additions before the closing body tag
    updated_content = frontend_content[:body_end_pos] + "\n\n" + additions_content + "\n\n" + frontend_content[body_end_pos:]
    
    # Write back to file
    with open(frontend_path, 'w') as f:
        f.write(updated_content)
    
    print(f"Successfully updated {frontend_path} with enhanced frontend features")
    return True

if __name__ == "__main__":
    update_frontend()
