import os
import re

def update_app_py():
    """Update app.py to include enhanced endpoints"""
    if not os.path.exists('app.py'):
        print("Error: app.py not found")
        return False
    
    # Read the current content
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check if enhanced endpoints are already imported
    if 'from enhanced_api_endpoints import register_enhanced_endpoints' in content:
        print("Enhanced endpoints already imported in app.py")
        return True
    
    # Find a good insertion point for the import
    import_section_match = re.search(r'(import.*?\n\n)', content, re.DOTALL)
    if not import_section_match:
        print("Could not find import section in app.py")
        return False
    
    import_section_end = import_section_match.end()
    
    # Add the import
    new_import = "\n# Import enhanced endpoints\nfrom enhanced_api_endpoints import register_enhanced_endpoints\n"
    updated_content = content[:import_section_end] + new_import + content[import_section_end:]
    
    # Find where to register the endpoints
    app_creation_match = re.search(r'app\s*=\s*Flask\(.*?\)', updated_content)
    if not app_creation_match:
        print("Could not find Flask app creation in app.py")
        return False
    
    app_creation_end = app_creation_match.end()
    
    # Add the registration
    register_code = "\n\n# Register enhanced endpoints\napp = register_enhanced_endpoints(app)\n"
    updated_content = updated_content[:app_creation_end] + register_code + updated_content[app_creation_end:]
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(updated_content)
    
    print("Successfully updated app.py with enhanced endpoints")
    return True

if __name__ == "__main__":
    update_app_py()
