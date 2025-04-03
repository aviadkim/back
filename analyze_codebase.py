import os
import re
import json

def find_python_files(root_dir):
    """Find all Python files in the directory"""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip virtual environments and node_modules
        if 'venv' in root or 'node_modules' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def analyze_imports(file_path):
    """Analyze imports in a Python file"""
    imports = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Find import statements
        import_patterns = [
            r'^\s*import\s+([\w\.]+)',
            r'^\s*from\s+([\w\.]+)\s+import'
        ]
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)
    return imports

def analyze_functions(file_path):
    """Analyze functions in a Python file"""
    functions = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Find function definitions
        matches = re.findall(r'^\s*def\s+(\w+)\s*\(', content, re.MULTILINE)
        functions.extend(matches)
    return functions

def analyze_classes(file_path):
    """Analyze classes in a Python file"""
    classes = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Find class definitions
        matches = re.findall(r'^\s*class\s+(\w+)', content, re.MULTILINE)
        classes.extend(matches)
    return classes

def get_file_category(file_path, file_name):
    """Categorize files by functionality"""
    categories = {
        'app': ['app.py'],
        'routes': ['document_routes.py', 'langchain_routes.py'],
        'models': ['document_models.py'],
        'services': ['document_service.py'],
        'utils': ['pdf_processor.py'],
        'extraction': ['financial_data_extractor.py', 'ocr_text_extractor.py'],
        'analysis': ['enhanced_financial_extractor.py', 'portfolio_analysis.py'],
        'qa': ['simple_qa.py'],
        'tests': ['test_', '_test'],
        'agent': ['agent_framework', 'coordinator.py', 'memory_agent.py']
    }
    
    for category, patterns in categories.items():
        for pattern in patterns:
            if pattern in file_path:
                return category
    
    return 'other'

def main():
    root_dir = '.'
    files = find_python_files(root_dir)
    
    codebase_analysis = {
        'file_count': len(files),
        'categories': {},
        'files': []
    }
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        category = get_file_category(file_path, file_name)
        
        # Count by category
        if category not in codebase_analysis['categories']:
            codebase_analysis['categories'][category] = 0
        codebase_analysis['categories'][category] += 1
        
        # Analyze file
        imports = analyze_imports(file_path)
        functions = analyze_functions(file_path)
        classes = analyze_classes(file_path)
        
        file_info = {
            'path': file_path,
            'name': file_name,
            'category': category,
            'imports_count': len(imports),
            'functions_count': len(functions),
            'classes_count': len(classes),
            'size': os.path.getsize(file_path)
        }
        
        codebase_analysis['files'].append(file_info)
    
    # Sort files by category for easier reading
    codebase_analysis['files'].sort(key=lambda x: (x['category'], x['name']))
    
    # Save analysis to file
    with open('codebase_analysis.json', 'w') as f:
        json.dump(codebase_analysis, f, indent=2)
    
    # Print summary
    print(f"Total Python files: {codebase_analysis['file_count']}")
    print("\nFiles by category:")
    for category, count in sorted(codebase_analysis['categories'].items()):
        print(f"  {category}: {count}")
    
    print("\nTop 10 largest files:")
    largest_files = sorted(codebase_analysis['files'], key=lambda x: x['size'], reverse=True)[:10]
    for file in largest_files:
        print(f"  {file['path']} - {file['size'] / 1024:.1f} KB")

if __name__ == "__main__":
    main()
