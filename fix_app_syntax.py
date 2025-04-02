def fix_app_imports():
    """Fix the syntax error in app.py imports"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Fix the merged import
    if 'import shutilfrom' in content:
        fixed_content = content.replace('import shutilfrom', 'import shutil\nfrom')
        
        with open('app.py', 'w') as f:
            f.write(fixed_content)
        
        print("Syntax error in imports fixed!")
        return True
    else:
        print("Expected syntax error not found. Check file manually.")
        return False

if __name__ == "__main__":
    fix_app_imports()
