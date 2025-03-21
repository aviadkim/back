#!/usr/bin/env python3
"""
AI-Assisted Development Workflow
-------------------------------
This script combines project analysis, code generation, and testing
in an integrated workflow designed for AI-assisted development.

Usage:
1. Run this script in your GitHub Codespace: python dev_workflow.py
2. Follow the interactive prompts to analyze, build, or test
3. Share the generated reports with Claude for assistance

Requirements: Python 3.6+
"""

import os
import sys
import json
import time
import fnmatch
import subprocess
import re
import unittest
import traceback
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any, Optional, Union

# Constants
MAX_FILE_SIZE = 1024 * 1024  # 1MB
IGNORE_PATTERNS = [
    '.git/*', '__pycache__/*', 'node_modules/*', '.venv/*', 'venv/*',
    'dist/*', 'build/*', '.next/*', '.cache/*', 'coverage/*',
    '*.pyc', '*.pyo', '*.so', '*.class', '*.dll', '*.exe', '*.o', '*.a',
    '*.jar', '*.war', '*.ear', '*.zip', '*.tar.gz', '*.rar',
    '.DS_Store', 'Thumbs.db'
]

# File groupings by type
FILE_TYPES = {
    'frontend': ['.html', '.css', '.scss', '.sass', '.less', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte'],
    'backend': ['.py', '.rb', '.php', '.java', '.go', '.rs', '.cs', '.scala', '.kt', '.js', '.ts'],
    'data': ['.json', '.xml', '.yaml', '.yml', '.csv', '.tsv', '.sql', '.db', '.sqlite'],
    'config': ['.toml', '.ini', '.cfg', '.conf', '.properties', '.env', '.npmrc', '.babelrc', '.eslintrc'],
    'docs': ['.md', '.rst', '.txt', '.pdf', '.doc', '.docx'],
    'tests': ['test_', '_test', 'spec', '_spec'],
    'assets': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.tiff', '.svg', '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv'],
}

def should_ignore(path: str) -> bool:
    """Check if a file should be ignored based on patterns."""
    # Immediately ignore node_modules directory
    if 'node_modules' in path.split(os.sep):
        return True

    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def get_file_type(path: str) -> str:
    """Determine the type of file based on extension and name."""
    file_name = os.path.basename(path)
    file_ext = os.path.splitext(path)[1].lower()

    # Check if it's a test file based on name
    for test_pattern in FILE_TYPES['tests']:
        if test_pattern in file_name.lower():
            return 'tests'

    # Check based on extension
    for file_type, extensions in FILE_TYPES.items():
        if file_type == 'tests':
            continue
        if file_ext in extensions:
            return file_type

    return 'other'

def get_git_info() -> Dict[str, Any]:
    """Get basic information from git repository."""
    git_info = {}

    try:
        # Check if git is available and current directory is a git repo
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Get current branch
        branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git_info['current_branch'] = branch.stdout.decode('utf-8').strip()

        # Get number of commits
        commit_count = subprocess.run(['git', 'rev-list', '--count', 'HEAD'],
                                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git_info['commit_count'] = commit_count.stdout.decode('utf-8').strip()

        # Get recent commit history
        recent_commits = subprocess.run(['git', 'log', '--pretty=format:%h|%an|%s', '-n', '5'],
                                        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        commits = []
        for line in recent_commits.stdout.decode('utf-8').strip().split('\n'):
            if line:
                parts = line.split('|', 2)
                if len(parts) == 3:
                    hash_id, author, message = parts
                    commits.append({
                        'hash': hash_id,
                        'author': author,
                        'message': message
                    })
        git_info['recent_commits'] = commits

        # Get contributors
        contributors = subprocess.run(['git', 'shortlog', '-sne', 'HEAD'],
                                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git_info['contributors'] = []
        for line in contributors.stdout.decode('utf-8').strip().split('\n'):
            if line:
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    count, name = parts
                    git_info['contributors'].append({
                        'count': count.strip(),
                        'name': name.strip()
                    })

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        git_info['error'] = f"Failed to get git info: {str(e)}"

    return git_info

def detect_technologies(files: Dict[str, Any]) -> Dict[str, List[str]]:
    """Detect technologies used in the project based on file content and names."""
    technologies = {
        'languages': set(),
        'frameworks': set(),
        'databases': set(),
        'build_tools': set(),
        'package_managers': set(),
        'testing': set(),
    }

    # Technology indicators in files or their content
    tech_indicators = {
        'languages': {
            'JavaScript': ['.js', '.jsx', '.mjs'],
            'TypeScript': ['.ts', '.tsx'],
            'Python': ['.py', 'requirements.txt', 'setup.py', 'Pipfile'],
            'Java': ['.java', 'pom.xml', 'build.gradle'],
            'Go': ['.go', 'go.mod', 'go.sum'],
            'Ruby': ['.rb', 'Gemfile'],
            'PHP': ['.php', 'composer.json'],
            'C#': ['.cs', '.csproj', '.sln'],
            'Rust': ['.rs', 'Cargo.toml'],
            'Swift': ['.swift'],
            'Kotlin': ['.kt', '.kts'],
            'C++': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
            'C': ['.c', '.h'],
        },
        'frameworks': {
            'React': ['react', '.jsx', '.tsx'],
            'Vue.js': ['vue', '.vue'],
            'Angular': ['angular', '.component.ts'],
            'Svelte': ['.svelte'],
            'Express': ['express'],
            'Django': ['django', 'wsgi.py', 'asgi.py'],
            'Flask': ['flask'],
            'FastAPI': ['fastapi'],
            'Spring': ['spring', 'application.properties', 'application.yml'],
            'Laravel': ['laravel', 'artisan'],
            'Rails': ['rails', 'config/routes.rb', 'app/controllers'],
            'ASP.NET': ['.cshtml', '.aspx', 'Web.config'],
            'Flutter': ['pubspec.yaml', '.dart'],
        },
        'databases': {
            'MongoDB': ['mongodb', 'mongoose'],
            'PostgreSQL': ['postgresql', 'postgres', 'pg'],
            'MySQL': ['mysql'],
            'SQLite': ['sqlite'],
            'Redis': ['redis'],
            'Cassandra': ['cassandra'],
            'Firebase': ['firebase'],
            'DynamoDB': ['dynamodb', 'aws-sdk'],
            'Oracle': ['oracle', 'oracledb'],
            'SQL Server': ['sqlserver', 'mssql'],
        },
        'build_tools': {
            'Webpack': ['webpack'],
            'Babel': ['.babelrc', 'babel.config.js'],
            'Maven': ['pom.xml'],
            'Gradle': ['build.gradle', 'gradle.properties'],
            'Gulp': ['gulpfile.js'],
            'Grunt': ['Gruntfile.js'],
            'NPM Scripts': ['scripts', 'package.json'],
            'Make': ['Makefile'],
            'CMake': ['CMakeLists.txt'],
            'Vite': ['vite.config'],
        },
        'package_managers': {
            'NPM': ['package.json', 'package-lock.json'],
            'Yarn': ['yarn.lock'],
            'Pip': ['requirements.txt', 'setup.py'],
            'Pipenv': ['Pipfile', 'Pipfile.lock'],
            'Poetry': ['pyproject.toml'],
            'Maven': ['pom.xml'],
            'Gradle': ['build.gradle'],
            'Composer': ['composer.json', 'composer.lock'],
            'Cargo': ['Cargo.toml', 'Cargo.lock'],
            'Go Modules': ['go.mod', 'go.sum'],
            'Bundler': ['Gemfile', 'Gemfile.lock'],
            'NuGet': ['packages.config', '.csproj'],
        },
        'testing': {
            'Jest': ['jest', 'test.js', 'spec.js', 'test.jsx', 'spec.jsx', 'test.ts', 'spec.ts'],
            'Mocha': ['mocha', 'test.js', 'spec.js'],
            'PyTest': ['pytest', 'test_', '_test.py', 'conftest.py'],
            'UnitTest': ['unittest', 'test_', '_test.py'],
            'JUnit': ['junit', 'Test.java'],
            'TestNG': ['testng', 'Test.java'],
            'RSpec': ['rspec', '_spec.rb'],
            'PHPUnit': ['phpunit', 'Test.php'],
            'Go Test': ['_test.go'],
            'Cypress': ['cypress'],
            'Selenium': ['selenium'],
            'Jasmine': ['jasmine', 'spec.js', 'spec.ts'],
        }
    }

    # Look for files that indicate certain technologies
    for file_path, file_info in files.items():
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()

        # Check for technology indicators in file path
        for tech_type, tech_dict in tech_indicators.items():
            for tech, indicators in tech_dict.items():
                for indicator in indicators:
                    if (indicator.startswith('.') and indicator == file_ext) or \
                       (not indicator.startswith('.') and indicator in file_path.lower()):
                        technologies[tech_type].add(tech)

        # Check for technology indicators in file content
        if 'content_sample' in file_info:
            content_sample = file_info['content_sample'].lower()
            for tech_type, tech_dict in tech_indicators.items():
                for tech, indicators in tech_dict.items():
                    for indicator in indicators:
                        if not indicator.startswith('.') and indicator in content_sample:
                            technologies[tech_type].add(tech)

    # Convert sets to sorted lists
    for tech_type in technologies:
        technologies[tech_type] = sorted(list(technologies[tech_type]))

    return technologies

def get_file_complexity(file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
    """Analyze file complexity based on various metrics."""
    try:
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                return {
                    'error': f"Could not read file: {str(e)}",
                    'lines': 0,
                    'complexity': 'unknown'
                }

        lines = content.count('\n') + 1

        # More sophisticated complexity heuristic based on file size, language, and content
        file_ext = os.path.splitext(file_path)[1].lower()

        # Adjust thresholds based on file type
        if file_ext in ['.md', '.txt', '.rst']:
            # Documentation files can be longer
            complexity = 'low' if lines < 300 else ('medium' if lines < 600 else 'high')
        elif file_ext in ['.json', '.xml', '.yaml', '.yml']:
            # Data files can be long but not necessarily complex
            complexity = 'low' if lines < 200 else ('medium' if lines < 500 else 'high')
        elif file_ext in ['.css', '.scss', '.less']:
            # Style files can be long but organized
            complexity = 'low' if lines < 150 else ('medium' if lines < 400 else 'high')
        else:
            # Code files
            complexity = 'low' if lines < 100 else ('medium' if lines < 300 else 'high')

            # Additional code complexity indicators
            if content:
                # Check for nested logic (if/for/while)
                indentation_levels = set()
                for line in content.split('\n'):
                    if line.strip() and not line.strip().startswith(('#', '//', '/*', '*')):
                        indentation = len(line) - len(line.lstrip())
                        indentation_levels.add(indentation)

                # If we have many indentation levels, complexity increases
                if len(indentation_levels) > 5:
                    complexity = 'high' if complexity != 'high' else 'very high'

                # Count complex structures
                if file_ext in ['.py', '.js', '.jsx', '.ts', '.tsx']:
                    structures = 0
                    structures += content.count(' if ') + content.count('if(')
                    structures += content.count(' for ') + content.count('for(')
                    structures += content.count(' while ') + content.count('while(')
                    structures += content.count(' switch ') + content.count('switch(')
                    structures += content.count(' class ')
                    structures += content.count(' function ')
                    structures += content.count(' def ') if file_ext == '.py' else 0

                    if structures > 30:
                        complexity = 'high'

        result = {
            'lines': lines,
            'complexity': complexity,
        }

        return result
    except Exception as e:
        return {
            'error': f"Error analyzing complexity: {str(e)}",
            'lines': 0,
            'complexity': 'unknown'
        }

def analyze_directory(root_dir: str) -> Dict[str, Any]:
    """Analyze a directory and return information about its structure and files."""
    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        return {"error": f"Directory {root_dir} does not exist or is not a directory"}

    start_time = time.time()

    # Initialize results
    results = {
        "project_summary": {
            "root_dir": os.path.abspath(root_dir),
            "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_count": 0,
            "directory_count": 0,
            "file_types": defaultdict(int),
            "file_extensions": defaultdict(int),
            "largest_files": [],
            "recently_modified_files": []
        },
        "files": {},
        "technology_stack": {},
        "git_info": get_git_info(),
        "package_files": {},
        "detected_dependencies": {},
        "metrics": {},
        "potential_issues": [],
        "project_structure": {}
    }

    # Collect directory structure
    directory_structure = defaultdict(list)

    # Collect all files
    all_files = []

    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            rel_dirpath = os.path.relpath(dirpath, root_dir)

            if should_ignore(rel_dirpath):
                dirnames[:] = []  # Don't go into ignored directories
                continue

            results["project_summary"]["directory_count"] += 1

            # Add to directory structure
            if rel_dirpath != '.':
                parent_dir = os.path.dirname(rel_dirpath)
                if parent_dir == '':
                    parent_dir = '.'
                directory_structure[parent_dir].append(os.path.basename(rel_dirpath))

            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_file_path = os.path.relpath(file_path, root_dir)

                if should_ignore(rel_file_path):
                    continue

                try:
                    file_stat = os.stat(file_path)
                    file_type = get_file_type(rel_file_path)
                    file_ext = os.path.splitext(rel_file_path)[1].lower()

                    # Add to directory structure
                    if rel_dirpath != '.':
                        directory_structure[rel_dirpath].append(filename)
                    else:
                        directory_structure['.'].append(filename)

                    file_info = {
                        "path": rel_file_path,
                        "size": file_stat.st_size,
                        "last_modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime)),
                        "type": file_type
                    }

                    # Record file summary data
                    results["project_summary"]["file_count"] += 1
                    results["project_summary"]["file_types"][file_type] += 1
                    results["project_summary"]["file_extensions"][file_ext] += 1

                    # Track large files
                    if file_stat.st_size > 100 * 1024:  # Larger than 100KB
                        results["project_summary"]["largest_files"].append({
                            "path": rel_file_path,
                            "size": file_stat.st_size
                        })

                    # Track recently modified files
                    if time.time() - file_stat.st_mtime < 7 * 24 * 60 * 60:  # Modified in the last week
                        results["project_summary"]["recently_modified_files"].append({
                            "path": rel_file_path,
                            "last_modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime))
                        })

                    # Read content of text files for analysis
                    if file_stat.st_size < MAX_FILE_SIZE and file_ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.md', '.json', '.yml', '.yaml', '.txt', '.sh', '.java', '.go', '.rb', '.php']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                file_info["content_sample"] = content[:2000]  # Store only first 2000 chars
                                file_info["full_content"] = content  # Store full content for code suggestions

                                # Analyze complexity
                                complexity_info = get_file_complexity(file_path, content)
                                file_info.update(complexity_info)

                                # Flag potential issues
                                if complexity_info.get('complexity') == 'high' or complexity_info.get('complexity') == 'very high':
                                    results["potential_issues"].append({
                                        "type": "high_complexity",
                                        "file": rel_file_path,
                                        "description": f"File has high complexity ({complexity_info.get('lines', 0)} lines)"
                                    })

                                # Store package information
                                if os.path.basename(file_path) in ['package.json', 'requirements.txt', 'pyproject.toml', 'Pipfile', 'pom.xml', 'build.gradle', 'Gemfile', 'composer.json', 'Cargo.toml', 'go.mod']:
                                    results["package_files"][rel_file_path] = {
                                        "content": content,
                                        "file_type": file_type
                                    }
                        except Exception as e:
                            file_info["error"] = f"Could not read content: {str(e)}"

                    results["files"][rel_file_path] = file_info
                    all_files.append((rel_file_path, file_info))
                except Exception as e:
                    print(f"Error processing {rel_file_path}: {str(e)}")
    except Exception as e:
        print(f"Error during directory traversal: {str(e)}")
        traceback.print_exc()

    # Add directory structure to results
    results["project_structure"] = dict(directory_structure)

    # Sort largest files and recent files
    results["project_summary"]["largest_files"] = sorted(
        results["project_summary"]["largest_files"],
        key=lambda x: x["size"],
        reverse=True
    )[:10]  # Top 10 largest

    results["project_summary"]["recently_modified_files"] = sorted(
        results["project_summary"]["recently_modified_files"],
        key=lambda x: x["last_modified"],
        reverse=True
    )[:10]  # Top 10 most recent

    # Detect technologies
    results["technology_stack"] = detect_technologies(results["files"])

    # Extract dependencies from package files
    for file_path, file_info in results["package_files"].items():
        file_name = os.path.basename(file_path)
        content = file_info.get("content", "")

        if file_name == 'package.json':
            try:
                data = json.loads(content)
                dependencies = {}
                if "dependencies" in data:
                    dependencies.update(data["dependencies"])
                if "devDependencies" in data:
                    dependencies.update(data["devDependencies"])

                results["detected_dependencies"]["npm"] = {
                    "count": len(dependencies),
                    "items": dependencies
                }
            except json.JSONDecodeError:
                pass

        elif file_name == 'requirements.txt':
            try:
                packages = {}
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            name, version = line.split('==', 1)
                            packages[name.strip()] = version.strip()
                        else:
                            packages[line] = "unspecified"

                results["detected_dependencies"]["python"] = {
                    "count": len(packages),
                    "items": packages
                }
            except Exception:
                pass

    # Calculate metrics
    results["metrics"] = {
        "file_count_by_type": dict(results["project_summary"]["file_types"]),
        "file_count_by_extension": dict(results["project_summary"]["file_extensions"]),
        "analysis_duration_seconds": round(time.time() - start_time, 2)
    }

    return results

def suggest_next_steps(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate specific code suggestions for the next development steps."""
    if not analysis or not analysis.get("technology_stack"):
        return {
            "new_files": [],
            "updates": [],
            "next_features": []
        }

    tech_stack = analysis.get("technology_stack", {})
    languages = tech_stack.get("languages", [])
    frameworks = tech_stack.get("frameworks", [])

    suggestions = {
        "new_files": [],
        "updates": [],
        "next_features": []
    }

    # Identify recently modified files for context
    recent_files = analysis.get("project_summary", {}).get("recently_modified_files", [])
    recent_file_paths = [file["path"] for file in recent_files]

    # Suggest new files based on project type
    if "Python" in languages:
        # Check if it's a web application
        is_web_app = any(fw in frameworks for fw in ["Flask", "Django", "FastAPI"])

        if is_web_app:
            # If no API routes found, suggest creating them
            has_routes = any("routes" in path.lower() or "views" in path.lower() for path in analysis["files"].keys())
            if not has_routes:
                suggestions["new_files"].append({
                    "file_path": "api/routes.py" if "FastAPI" in frameworks else "app/routes.py",
                    "description": "Create API routes file to define endpoints",
                    "template": '''
# api/routes.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint to verify API is running."""
    return {"message": "API is running"}

@router.get("/items")
async def list_items():
    """Return a list of items."""
    # TODO: Implement database connection
    return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    """Get a specific item by ID."""
    # TODO: Implement database lookup
    if item_id > 100:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, "name": f"Item {item_id}"}
'''
                })

            # If database is used but no models, suggest models
            has_db = any(db in tech_stack.get("databases", []) for db in ["PostgreSQL", "MySQL", "SQLite"])
            has_models = any("model" in path.lower() for path in analysis["files"].keys())

            if has_db and not has_models:
                suggestions["new_files"].append({
                    "file_path": "models/base.py",
                    "description": "Create database models",
                    "template": '''
# models/base.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
'''
                })

            # Suggest test files
            has_tests = any(file_info["type"] == "tests" for file_info in analysis["files"].values())
            if not has_tests:
                suggestions["new_files"].append({
                    "file_path": "tests/test_app.py",
                    "description": "Create test file for basic functionality",
                    "template": '''
# tests/test_app.py
import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestApp(unittest.TestCase):
    def setUp(self):
        # Setup code that runs before each test
        pass

    def tearDown(self):
        # Cleanup code that runs after each test
        pass

    def test_basic_functionality(self):
        # Test basic app functionality
        self.assertTrue(True)  # Placeholder assertion

    def test_important_feature(self):
        # Test a specific feature
        expected = "expected result"
        actual = "expected result"  # Replace with actual function call
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
'''
                })

    # For JavaScript/TypeScript projects
    if any(lang in languages for lang in ["JavaScript", "TypeScript"]):
        is_react = "React" in frameworks

        if is_react:
            # If no components directory, suggest creating one
            has_components = any("components" in path.lower() for path in analysis["files"].keys())
            if not has_components:
                suggestions["new_files"].append({
                    "file_path": "src/components/Button.jsx" if "JavaScript" in languages else "src/components/Button.tsx",
                    "description": "Create reusable button component",
                    "template": '''
import React, { useState, useEffect } from 'react';

interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  text,
  onClick,
  variant = 'primary',
  size = 'medium',
  disabled = false
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-blue-500 hover:bg-blue-600 text-white';
      case 'secondary':
        return 'bg-gray-200 hover:bg-gray-300 text-gray-800';
      case 'danger':
        return 'bg-red-500 hover:bg-red-600 text-white';
      default:
        return 'bg-blue-500 hover:bg-blue-600 text-white';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return 'px-2 py-1 text-sm';
      case 'medium':
        return 'px-4 py-2';
      case 'large':
        return 'px-6 py-3 text-lg';
      default:
        return 'px-4 py-2';
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${getVariantClasses()}
        ${getSizeClasses()}
        rounded font-medium focus:outline-none focus:ring-2 focus:ring-opacity-50
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      {text}
    </button>
  );
};

export default Button;
'''
                })

            # Suggest test files for React
            has_tests = any("test" in path.lower() for path in analysis["files"].keys())
            if not has_tests:
                suggestions["new_files"].append({
                    "file_path": "src/components/__tests__/Button.test.jsx" if "JavaScript" in languages else "src/components/__tests__/Button.test.tsx",
                    "description": "Create test file for Button component",
                    "template": '''
import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import Button from '../Button';

describe('Button component', () => {
  test('renders with the correct text', () => {
    render(<Button text="Click me" onClick={() => {}} />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button text="Click me" onClick={handleClick} />);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies the correct variant classes', () => {
    const { rerender } = render(<Button text="Primary" onClick={() => {}} variant="primary" />);
    expect(screen.getByText('Primary').className).toContain('bg-blue-500');

    rerender(<Button text="Secondary" onClick={() => {}} variant="secondary" />);
    expect(screen.getByText('Secondary').className).toContain('bg-gray-200');

    rerender(<Button text="Danger" onClick={() => {}} variant="danger" />);
    expect(screen.getByText('Danger').className).toContain('bg-red-500');
  });

  test('applies the correct size classes', () => {
    const { rerender } = render(<Button text="Small" onClick={() => {}} size="small" />);
    expect(screen.getByText('Small').className).toContain('px-2 py-1');

    rerender(<Button text="Medium" onClick={() => {}} size="medium" />);
    expect(screen.getByText('Medium').className).toContain('px-4 py-2');

    rerender(<Button text="Large" onClick={() => {}} size="large" />);
    expect(screen.getByText('Large').className).toContain('px-6 py-3');
  });

  test('applies disabled styles when disabled', () => {
    render(<Button text="Disabled" onClick={() => {}} disabled />);
    const button = screen.getByText('Disabled');
    expect(button).toBeDisabled();
    expect(button.className).toContain('opacity-50');
  });
});
'''
                })

    # Suggest updates to existing files based on recent activity
    for file_path in recent_file_paths:
        file_info = analysis["files"].get(file_path, {})
        file_content = file_info.get("full_content", "")
        file_ext = os.path.splitext(file_path)[1].lower()

        # For Python files
        if file_ext == '.py':
            # Check if the file is missing docstrings
            has_docstrings = '"""' in file_content or "'''" in file_content
            if not has_docstrings:
                suggestions["updates"].append({
                    "file_path": file_path,
                    "description": "Add docstrings to improve code documentation",
                    "changes": [
                        {
                            "type": "add_docstring",
                            "target": "file",
                            "content": '"""\nModule description: What this file does\n\nAuthor: Your Name\nDate: ' + datetime.now().strftime("%Y-%m-%d") + '\n"""'
                        }
                    ]
                })

            # Check if there are functions without type hints
            if 'def ' in file_content and 'typing' not in file_content:
                suggestions["updates"].append({
                    "file_path": file_path,
                    "description": "Add type hints to functions",
                    "changes": [
                        {
                            "type": "add_import",
                            "content": "from typing import List, Dict, Optional, Tuple, Any"
                        }
                    ]
                })

        # For JavaScript/TypeScript files
        elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            # Check if there are functions without comments
            has_comments = '/**' in file_content or '/*' in file_content
            if not has_comments and 'function' in file_content:
                suggestions["updates"].append({
                    "file_path": file_path,
                    "description": "Add JSDoc comments to improve code documentation",
                    "changes": [
                        {
                            "type": "add_docs",
                            "target": "functions",
                            "template": "/**\n * Function description\n * @param {type} paramName - Parameter description\n * @returns {type} Return value description\n */"
                        }
                    ]
                })

    # Suggest next features based on current project state
    if "Python" in languages:
        if "FastAPI" in frameworks:
            suggestions["next_features"].append({
                "title": "Implement authentication with JWT",
                "description": "Add secure JWT authentication to protect API endpoints",
                "steps": [
                    "1. Install dependencies: `pip install python-jose passlib`",
                    "2. Create auth.py with JWT token generation and verification",
                    "3. Add user login/register endpoints",
                    "4. Create dependency for protected routes"
                ]
            })

        if "Flask" in frameworks:
            suggestions["next_features"].append({
                "title": "Add database integration with SQLAlchemy",
                "description": "Implement ORM for database operations",
                "steps": [
                    "1. Install dependencies: `pip install flask-sqlalchemy`",
                    "2. Configure database connection in app.py",
                    "3. Create models with SQLAlchemy classes",
                    "4. Implement CRUD operations"
                ]
            })

    if "React" in frameworks:
        suggestions["next_features"].append({
            "title": "Implement state management",
            "description": "Add Redux or React Context for better state management",
            "steps": [
                "1. Install dependencies: `npm install @reduxjs/toolkit react-redux`",
                "2. Create store configuration",
                "3. Define slices for application state",
                "4. Connect components to the store"
            ]
        })

    return suggestions

def create_next_files(output_dir: str, next_steps: Dict[str, Any], tech_stack: Dict[str, List[str]]) -> None:
    """Create the suggested new files based on next steps."""
    if not next_steps or not next_steps.get("new_files"):
        print("No new files to create.")
        return

    for file_suggestion in next_steps.get("new_files", []):
        try:
            file_path = file_suggestion["file_path"]
            full_path = os.path.abspath(os.path.join(output_dir, file_path))

            # Verify path is within project directory
            if not full_path.startswith(os.path.abspath(output_dir)):
                print(f"Warning: Skipping file outside project directory: {file_path}")
                continue

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Use template content if provided, otherwise generate one
            content = file_suggestion.get("template", "").strip()
            if not content:
                content = generate_code_template(file_path, tech_stack)

            with open(full_path, 'w') as f:
                f.write(content)

            print(f"Created new file: {file_path}")
        except Exception as e:
            print(f"Error creating file {file_path}: {str(e)}")
            traceback.print_exc()

def generate_code_template(file_path: str, technology_stack: Dict[str, List[str]]) -> str:
    """Generate code template for a new file based on its path and project tech stack."""
    try:
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()

        # Python templates
        if file_ext == '.py':
            module_name = file_name.replace('.py', '')

            # API routes
            if 'routes' in file_name.lower() or 'views' in file_name.lower():
                if 'FastAPI' in technology_stack.get('frameworks', []):
                    return f'''"""
API Routes for {module_name}

This module defines the API endpoints for the application.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint to check API health."""
    return {{"status": "healthy"}}

@router.get("/items")
async def get_items():
    """Retrieve all items."""
    # TODO: Implement database access
    return [{{"id": 1, "name": "Item 1"}}, {{"id": 2, "name": "Item 2"}}]

@router.post("/items")
async def create_item(item: dict):
    """Create a new item."""
    # TODO: Implement item creation
    return {{"id": 3, **item}}
'''
                elif 'Flask' in technology_stack.get('frameworks', []):
                    return f'''"""
API Routes for {module_name}

This module defines the API endpoints for the application.
"""

from flask import Blueprint, request, jsonify

{module_name}_bp = Blueprint('{module_name}', __name__)

@{module_name}_bp.route('/')
def index():
    """Root endpoint to check API health."""
    return jsonify({{"status": "healthy"}})

@{module_name}_bp.route('/items', methods=['GET'])
def get_items():
    """Retrieve all items."""
    # TODO: Implement database access
    items = [{{"id": 1, "name": "Item 1"}}, {{"id": 2, "name": "Item 2"}}]
    return jsonify(items)

@{module_name}_bp.route('/items', methods=['POST'])
def create_item():
    """Create a new item."""
    data = request.get_json()
    # TODO: Implement item creation
    return jsonify({{"id": 3, **data}})
'''

            # Test files
            if file_name.startswith('test_') or file_name.endswith('_test'):
                return f'''"""
Tests for the {module_name.replace('test_', '').replace('_test', '')} module.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
# from module_to_test import function_to_test

class Test{module_name.replace('test_', '').replace('_test', '').capitalize()}(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass

    def tearDown(self):
        """Tear down test fixtures."""
        pass

    def test_some_functionality(self):
        """Test that some functionality works as expected."""
        expected = True
        # actual = function_to_test()
        actual = True  # Replace with actual test
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
'''

            # Default Python file
            return f'''"""
{module_name.replace('_', ' ').title()}

Description of what this module does.
"""

from typing import List, Dict, Optional, Any

def main():
    """Main function for the module."""
    print("Hello from {module_name}!")

if __name__ == "__main__":
    main()
'''

        # JavaScript/TypeScript templates
        elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            is_typescript = file_ext in ['.ts', '.tsx']
            is_react = file_ext in ['.jsx', '.tsx'] or 'React' in technology_stack.get('frameworks', [])

            if is_react and 'component' in file_path.lower():
                component_name = file_name.replace(file_ext, '')

                if is_typescript:
                    template = f'''import React, {{ useState, useEffect }} from 'react';

interface {component_name}Props {{
  title?: string;
}}

const {component_name}: React.FC<{component_name}Props> = ({{ title = "Default Title" }}) => {{
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {{
    // Fetch data or perform side effects
    console.log("Component mounted");

    return () => {{
      // Cleanup
      console.log("Component will unmount");
    }};
  }}, []);
  
  return (
    <div className="container">
      <h1>{{title}}</h1>
      <div className="content">
        {{/* Component content goes here */}}
        <p>This is the {component_name} component</p>
      </div>
    </div>
  );
}};

export default {component_name};
'''
                    return template
                else:
                    template = f'''import React, {{ useState, useEffect }} from 'react';

const {component_name} = ({{ title = "Default Title" }}) => {{
  const [data, setData] = useState([]);
  
  useEffect(() => {{
    // Fetch data or perform side effects
    console.log("Component mounted");
    
    return () => {{
      // Cleanup
      console.log("Component will unmount");
    }};
  }}, []);
  
  return (
    <div className="container">
      <h1>{{title}}</h1>
      <div className="content">
        {{/* Component content goes here */}}
        <p>This is the {component_name} component</p>
      </div>
    </div>
  );
}};

export default {component_name};
'''
                    return template

            # Test files
            if 'test' in file_path.lower() or 'spec' in file_path.lower():
                component_name = file_name.replace('.test', '').replace('.spec', '').replace(file_ext, '')

                return f'''import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import {component_name} from '../{component_name}';

describe('{component_name} component', () => {{
  test('renders correctly', () => {{
    render(<{component_name} />);
    // Add your test assertions here
  }});

  test('displays the correct title', () => {{
    render(<{component_name} title="Test Title" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  }});
}});
'''

        # Default template for other file types
        return f"// {file_name}\n// Created automatically by Project Analyzer\n"
    except Exception as e:
        print(f"Error generating code template: {str(e)}")
        return f"// {file_name}\n// Could not generate template: {str(e)}\n"

def discover_python_tests(root_dir: str) -> Dict[str, str]:
    """Discover Python test files in the project."""
    test_files = {}

    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if 'node_modules' in dirpath or '__pycache__' in dirpath:
                continue

            for filename in filenames:
                if (filename.startswith('test_') or filename.endswith('_test.py')) and filename.endswith('.py'):
                    file_path = os.path.join(dirpath, filename)
                    rel_file_path = os.path.relpath(file_path, root_dir)

                    # Get module name
                    module_path = rel_file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                    test_files[rel_file_path] = module_path
    except Exception as e:
        print(f"Error discovering Python tests: {str(e)}")

    return test_files

def discover_js_tests(root_dir: str) -> List[str]:
    """Discover JavaScript/TypeScript test files in the project."""
    test_files = []

    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if 'node_modules' in dirpath:
                continue

            for filename in filenames:
                if (filename.endswith('.test.js') or filename.endswith('.test.jsx') or
                    filename.endswith('.test.ts') or filename.endswith('.test.tsx') or
                    filename.endswith('.spec.js') or filename.endswith('.spec.jsx') or
                    filename.endswith('.spec.ts') or filename.endswith('.spec.tsx')):
                    file_path = os.path.join(dirpath, filename)
                    rel_file_path = os.path.relpath(file_path, root_dir)
                    test_files.append(rel_file_path)
    except Exception as e:
        print(f"Error discovering JavaScript tests: {str(e)}")

    return test_files

def run_python_tests(test_files: Dict[str, str], root_dir: str) -> Dict[str, Any]:
    """Run Python tests and return results."""
    results = {
        "total": len(test_files),
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "test_results": {}
    }

    # Save current directory to restore it later
    original_dir = os.getcwd()

    try:
        os.chdir(root_dir)

        for file_path, module_path in test_files.items():
            print(f"Running tests in {file_path}...")

            try:
                # Create a test suite
                test_suite = unittest.defaultTestLoader.loadTestsFromName(module_path)
                test_runner = unittest.TextTestRunner(verbosity=2)

                # Run the tests
                test_result = test_runner.run(test_suite)

                # Record results
                results["test_results"][file_path] = {
                    "run": test_result.testsRun,
                    "passed": test_result.testsRun - len(test_result.failures) - len(test_result.errors),
                    "failed": len(test_result.failures),
                    "errors": len(test_result.errors),
                    "failures": [str(failure[0]) for failure in test_result.failures],
                    "error_messages": [str(error[0]) for error in test_result.errors]
                }

                results["passed"] += results["test_results"][file_path]["passed"]
                results["failed"] += results["test_results"][file_path]["failed"]
                results["errors"] += results["test_results"][file_path]["errors"]

            except Exception as e:
                results["test_results"][file_path] = {
                    "run": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "failures": [],
                    "error_messages": [str(e)]
                }
                results["errors"] += 1
                print(f"Error running tests in {file_path}: {str(e)}")
    except Exception as e:
        print(f"Error running Python tests: {str(e)}")
    finally:
        # Restore original directory
        os.chdir(original_dir)

    return results

def run_js_tests(test_files: List[str], root_dir: str) -> Dict[str, Any]:
    """Run JavaScript/TypeScript tests using Jest if available."""
    results = {
        "total": len(test_files),
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "test_results": {}
    }

    # Check if Jest is installed
    try:
        # Try to locate Jest in the project
        jest_path = os.path.join(root_dir, 'node_modules', '.bin', 'jest')
        if not os.path.exists(jest_path):
            jest_path = 'jest'  # Try global Jest

        # Run Jest
        for file_path in test_files:
            print(f"Running tests in {file_path}...")

            try:
                # Run Jest on the specific file
                process = subprocess.run(
                    [jest_path, file_path, '--json'],
                    cwd=root_dir,
                    capture_output=True,
                    text=True,
                    check=False
                )

                if process.returncode == 0:
                    # Tests passed
                    try:
                        jest_output = json.loads(process.stdout)
                        results["test_results"][file_path] = {
                            "run": jest_output.get("numTotalTests", 0),
                            "passed": jest_output.get("numPassedTests", 0),
                            "failed": jest_output.get("numFailedTests", 0),
                            "errors": 0,
                            "failures": [],
                            "error_messages": []
                        }
                        results["passed"] += results["test_results"][file_path]["passed"]
                        results["failed"] += results["test_results"][file_path]["failed"]
                    except json.JSONDecodeError:
                        # Couldn't parse Jest output
                        results["test_results"][file_path] = {
                            "run": 1,
                            "passed": 1,
                            "failed": 0,
                            "errors": 0,
                            "failures": [],
                            "error_messages": []
                        }
                        results["passed"] += 1
                else:
                    # Tests failed
                    try:
                        jest_output = json.loads(process.stdout)
                        results["test_results"][file_path] = {
                            "run": jest_output.get("numTotalTests", 0),
                            "passed": jest_output.get("numPassedTests", 0),
                            "failed": jest_output.get("numFailedTests", 0),
                            "errors": 0,
                            "failures": [],
                            "error_messages": [process.stderr]
                        }
                        results["passed"] += results["test_results"][file_path]["passed"]
                        results["failed"] += results["test_results"][file_path]["failed"]
                    except json.JSONDecodeError:
                        # Couldn't parse Jest output
                        results["test_results"][file_path] = {
                            "run": 1,
                            "passed": 0,
                            "failed": 1,
                            "errors": 0,
                            "failures": ["Test failed"],
                            "error_messages": [process.stderr]
                        }
                        results["failed"] += 1

            except Exception as e:
                results["test_results"][file_path] = {
                    "run": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "failures": [],
                    "error_messages": [str(e)]
                }
                results["errors"] += 1

    except Exception as e:
        # Jest not found or other error
        print(f"Error running JavaScript tests: {str(e)}")
        for file_path in test_files:
            results["test_results"][file_path] = {
                "run": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "failures": [],
                "error_messages": [f"Jest not available: {str(e)}"]
            }
            results["errors"] += 1

    return results

def run_all_tests(root_dir: str) -> Dict[str, Any]:
    """Run all tests in the project and return results."""
    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        print(f"Error: Directory not found: {root_dir}")
        return {"error": f"Directory {root_dir} does not exist or is not a directory"}

    results = {
        "summary": {
            "total_files": 0,
            "passed_files": 0,
            "failed_files": 0,
            "error_files": 0,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "error_tests": 0
        },
        "python_tests": None,
        "js_tests": None,
    }

    try:
        # Discover and run Python tests
        python_test_files = discover_python_tests(root_dir)
        if python_test_files:
            python_results = run_python_tests(python_test_files, root_dir)
            results["python_tests"] = python_results

            # Update summary
            results["summary"]["total_files"] += python_results["total"]
            results["summary"]["total_tests"] += sum(result.get("run", 0) for result in python_results["test_results"].values())
            results["summary"]["passed_tests"] += python_results["passed"]
            results["summary"]["failed_tests"] += python_results["failed"]
            results["summary"]["error_tests"] += python_results["errors"]

            # Count passed/failed files
            for file_result in python_results["test_results"].values():
                if file_result.get("errors", 0) > 0:
                    results["summary"]["error_files"] += 1
                elif file_result.get("failed", 0) > 0:
                    results["summary"]["failed_files"] += 1
                else:
                    results["summary"]["passed_files"] += 1

        # Discover and run JavaScript tests
        js_test_files = discover_js_tests(root_dir)
        if js_test_files:
            js_results = run_js_tests(js_test_files, root_dir)
            results["js_tests"] = js_results

            # Update summary
            results["summary"]["total_files"] += js_results["total"]
            results["summary"]["total_tests"] += sum(result.get("run", 0) for result in js_results["test_results"].values())
            results["summary"]["passed_tests"] += js_results["passed"]
            results["summary"]["failed_tests"] += js_results["failed"]
            results["summary"]["error_tests"] += js_results["errors"]

            # Count passed/failed files
            for file_result in js_results["test_results"].values():
                if file_result.get("errors", 0) > 0:
                    results["summary"]["error_files"] += 1
                elif file_result.get("failed", 0) > 0:
                    results["summary"]["failed_files"] += 1
                else:
                    results["summary"]["passed_files"] += 1
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        traceback.print_exc()
        results["error"] = str(e)

    return results

def generate_test_report(test_results: Dict[str, Any], root_dir: str) -> str:
    """Generate a formatted report of test results."""
    if not test_results:
        return "# Test Report\nNo test results available."

    report = []
    report.append("# Test Report")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Handle error case
    if "error" in test_results:
        report.append(f"## Error\n{test_results['error']}")
        return "\n".join(report)

    # Summary
    summary = test_results.get("summary", {})
    report.append("## Test Summary")
    report.append(f"- **Total Test Files**: {summary.get('total_files', 0)}")
    report.append(f"- **Passed Files**: {summary.get('passed_files', 0)}")
    report.append(f"- **Failed Files**: {summary.get('failed_files', 0)}")
    report.append(f"- **Error Files**: {summary.get('error_files', 0)}")
    report.append(f"- **Total Tests**: {summary.get('total_tests', 0)}")
    report.append(f"- **Passed Tests**: {summary.get('passed_tests', 0)}")
    report.append(f"- **Failed Tests**: {summary.get('failed_tests', 0)}")
    report.append(f"- **Error Tests**: {summary.get('error_tests', 0)}")

    # Python test results
    python_tests = test_results.get("python_tests", {})
    if python_tests:
        report.append("\n## Python Test Results")
        report.append(f"- **Total Files**: {python_tests.get('total', 0)}")
        report.append(f"- **Passed Tests**: {python_tests.get('passed', 0)}")
        report.append(f"- **Failed Tests**: {python_tests.get('failed', 0)}")
        report.append(f"- **Error Tests**: {python_tests.get('errors', 0)}")

        # Detailed results for each file
        for file_path, file_results in python_tests.get("test_results", {}).items():
            report.append(f"\n### {file_path}")
            report.append(f"- **Tests Run**: {file_results.get('run', 0)}")
            report.append(f"- **Passed**: {file_results.get('passed', 0)}")
            report.append(f"- **Failed**: {file_results.get('failed', 0)}")
            report.append(f"- **Errors**: {file_results.get('errors', 0)}")

            # Failures
            if file_results.get("failures"):
                report.append("\n#### Failures")
                for failure in file_results.get("failures", []):
                    report.append(f"- {failure}")

            # Errors
            if file_results.get("error_messages"):
                report.append("\n#### Errors")
                for error in file_results.get("error_messages", []):
                    report.append(f"- {error}")

    # JavaScript test results
    js_tests = test_results.get("js_tests", {})
    if js_tests:
        report.append("\n## JavaScript Test Results")
        report.append(f"- **Total Files**: {js_tests.get('total', 0)}")
        report.append(f"- **Passed Tests**: {js_tests.get('passed', 0)}")
        report.append(f"- **Failed Tests**: {js_tests.get('failed', 0)}")
        report.append(f"- **Error Tests**: {js_tests.get('errors', 0)}")

        # Detailed results for each file
        for file_path, file_results in js_tests.get("test_results", {}).items():
            report.append(f"\n### {file_path}")
            report.append(f"- **Tests Run**: {file_results.get('run', 0)}")
            report.append(f"- **Passed**: {file_results.get('passed', 0)}")
            report.append(f"- **Failed**: {file_results.get('failed', 0)}")
            report.append(f"- **Errors**: {file_results.get('errors', 0)}")

            # Failures
            if file_results.get("failures"):
                report.append("\n#### Failures")
                for failure in file_results.get("failures", []):
                    report.append(f"- {failure}")

            # Errors
            if file_results.get("error_messages"):
                report.append("\n#### Errors")
                for error in file_results.get("error_messages", []):
                    report.append(f"- {error}")

    return "\n".join(report)

def get_latest_version(output_dir: str) -> str:
    """Get the latest version number from existing analysis reports."""
    try:
        # Check for existing version pattern files
        version_pattern = r'project_report_v(\d+\.\d+)\.md'
        version_files = []

        if not os.path.exists(output_dir):
            return "1.0"

        for file in os.listdir(output_dir):
            match = re.match(version_pattern, file)
            if match:
                version_files.append((file, match.group(1)))

        if not version_files:
            return "1.0"

        # Sort by version number
        version_files.sort(key=lambda x: [int(n) for n in x[1].split('.')])
        latest_version = version_files[-1][1]

        # Increment minor version
        major, minor = latest_version.split('.')
        new_minor = int(minor) + 1

        return f"{major}.{new_minor}"
    except Exception as e:
        print(f"Error getting latest version: {str(e)}")
        # If any error occurs, start with version 1.0
        return "1.0"

def generate_ai_assistant_guide(analysis: Dict[str, Any], recommendations: List[Dict[str, Any]], next_steps: Dict[str, Any], test_results: Optional[Dict[str, Any]] = None) -> str:
    """Generate a comprehensive guide for AI assistants to understand the project."""
    if not analysis or not analysis.get("project_summary"):
        return "# AI Assistant Project Guide\nInsufficient data to generate guide."

    guide = []
    guide.append("# AI Assistant Project Guide")
    guide.append("This document provides comprehensive information about the project to help AI assistants (like Claude) provide better assistance.\n")

    # Project overview and context
    project_summary = analysis.get("project_summary", {})
    tech_stack = analysis.get("technology_stack", {})

    guide.append("## Project Context")
    guide.append(f"- **Project Type**: {', '.join(tech_stack.get('languages', ['Unknown']))}-based application")
    if tech_stack.get('frameworks'):
        guide.append(f"- **Frameworks**: {', '.join(tech_stack.get('frameworks', []))}")
    guide.append(f"- **Project Size**: {project_summary.get('file_count', 0)} files in {project_summary.get('directory_count', 0)} directories")

    # Project structure
    guide.append("\n## Project Structure")
    guide.append("Key directories and their purposes:\n")

    project_structure = analysis.get("project_structure", {})
    handled_dirs = set()

    # First list important directories
    important_dirs = ["src", "app", "api", "models", "views", "controllers", "utils", "tests", "docs"]
    for dir_name in important_dirs:
        for path in project_structure:
            if dir_name in path and path not in handled_dirs:
                guide.append(f"- **{path}/** - Contains {len(project_structure[path])} files/directories")
                handled_dirs.add(path)

    # Then add any remaining root-level directories
    for path in project_structure:
        if path not in handled_dirs and path != '.' and '/' not in path:
            guide.append(f"- **{path}/** - Contains {len(project_structure[path])} files/directories")
            handled_dirs.add(path)

    # Key files
    guide.append("\n## Key Files")

    # Identify important files based on common patterns
    important_files = []
    for file_path in analysis.get("files", {}):
        file_name = os.path.basename(file_path)
        if any(name in file_name.lower() for name in ["main", "app", "index", "config", "settings", "requirements", "package.json"]):
            important_files.append(file_path)

    for file_path in sorted(important_files):
        file_info = analysis.get("files", {}).get(file_path, {})
        guide.append(f"- **{file_path}** - {file_info.get('lines', 0)} lines")

    # Development priorities
    guide.append("\n## Development Priorities")

    # List high and medium priority recommendations
    high_medium_recs = [rec for rec in recommendations if rec["priority"] in ["high", "medium"]]
    if high_medium_recs:
        guide.append("Based on analysis, these areas need attention:\n")
        for rec in high_medium_recs:
            guide.append(f"- {rec['description']} - {rec['reason']}")

    # Next development steps
    guide.append("\n## Next Development Steps")

    if next_steps.get("new_files"):
        guide.append("\n### New Files to Create")
        for file in next_steps["new_files"]:
            guide.append(f"- {file['file_path']} - {file['description']}")

    if next_steps.get("next_features"):
        guide.append("\n### Features to Implement")
        for feature in next_steps["next_features"]:
            guide.append(f"- {feature['title']} - {feature['description']}")

    # Test results
    if test_results and "error" not in test_results:
        guide.append("\n## Test Results")
        summary = test_results.get("summary", {})
        guide.append(f"- **Total Tests**: {summary.get('total_tests', 0)}")
        guide.append(f"- **Passed**: {summary.get('passed_tests', 0)}")
        guide.append(f"- **Failed**: {summary.get('failed_tests', 0)}")
        guide.append(f"- **Errors**: {summary.get('error_tests', 0)}")

        if summary.get('failed_tests', 0) > 0 or summary.get('error_tests', 0) > 0:
            guide.append("\nAttention needed: Some tests are failing. Check the test report for details.")

    # How to assist guide
    guide.append("\n## How to Assist with this Project")
    guide.append("As an AI assistant, you can help with the following:\n")
    guide.append("1. **Code Implementation** - Write or improve code based on the recommendations")
    guide.append("2. **Refactoring Help** - Provide solutions for complex files")
    guide.append("3. **Architecture Advice** - Suggest improvements to project structure")
    guide.append("4. **Feature Planning** - Help break down feature implementations into manageable steps")
    guide.append("5. **Bug Fixing** - Help identify and fix issues in the codebase")
    guide.append("6. **Documentation** - Assist in writing documentation for code and APIs")
    guide.append("7. **Test Creation** - Help write unit and integration tests")

    # Common request templates
    guide.append("\n### Common Request Templates")
    guide.append("When working with the developer, these request formats will be most helpful:\n")
    guide.append("```")
    guide.append('1. "Please implement [feature name] described in the report"')
    guide.append('2. "Help me refactor [file path] to reduce complexity"')
    guide.append('3. "Suggest a proper directory structure for this project"')
    guide.append('4. "Write documentation for [component/feature]"')
    guide.append('5. "Review this code: [paste code]"')
    guide.append('6. "Write tests for [feature/component]"')
    guide.append('7. "Fix the failing test in [test file]"')
    guide.append("```")

    return "\n".join(guide)

def generate_report(analysis: Dict[str, Any], recommendations: List[Dict[str, Any]], complex_file_analysis: Dict[str, List[Dict[str, Any]]], next_steps: Dict[str, Any], version: str) -> str:
    """Generate a formatted report from the analysis and recommendations."""
    if not analysis or not analysis.get("project_summary"):
        raise ValueError("Invalid or empty analysis data")

    report = []
    report.append(f"# Project Analysis Report v{version}")
    report.append(f"Generated on: {analysis.get('project_summary', {}).get('analysis_time', 'Unknown')}\n")

    # Project overview
    report.append("## Project Overview")
    project_summary = analysis.get("project_summary", {})
    report.append(f"- **Project Directory**: {project_summary.get('root_dir', 'Unknown')}")
    report.append(f"- **Total Files**: {project_summary.get('file_count', 0)}")
    report.append(f"- **Total Directories**: {project_summary.get('directory_count', 0)}")

    # File types
    report.append("\n### File Distribution")
    file_types = project_summary.get("file_types", {})
    for file_type, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
        report.append(f"- **{file_type.capitalize()}**: {count} files")

    # Technology stack
    report.append("\n## Technology Stack")
    tech_stack = analysis.get("technology_stack", {})

    for tech_type, techs in tech_stack.items():
        if techs:
            report.append(f"\n### {tech_type.replace('_', ' ').title()}")
            for tech in techs:
                report.append(f"- {tech}")

    # Git info
    git_info = analysis.get("git_info", {})
    if git_info and "error" not in git_info:
        report.append("\n## Git Information")
        report.append(f"- **Current Branch**: {git_info.get('current_branch', 'Unknown')}")
        report.append(f"- **Total Commits**: {git_info.get('commit_count', 'Unknown')}")

        if git_info.get("recent_commits"):
            report.append("\n### Recent Commits")
            for commit in git_info.get("recent_commits", [])[:3]:
                report.append(f"- `{commit.get('hash', '')}` {commit.get('message', '')}")

    # Dependencies
    deps = analysis.get("detected_dependencies", {})
    if deps:
        report.append("\n## Dependencies")
        for dep_type, dep_info in deps.items():
            report.append(f"\n### {dep_type.capitalize()} Dependencies")
            report.append(f"- **Total**: {dep_info.get('count', 0)} packages")

            # List some key dependencies
            items = dep_info.get("items", {})
            if len(items) > 0:
                report.append("\n**Key packages:**")
                for name, version in list(items.items())[:5]:
                    report.append(f"- {name}: {version}")
                if len(items) > 5:
                    report.append(f"- ... and {len(items) - 5} more")

    # Complex Files with Specific Recommendations
    if complex_file_analysis:
        report.append("\n## Complex Files Analysis")
        for file_path, recommendations in complex_file_analysis.items():
            report.append(f"\n### {file_path}")
            for rec in recommendations:
                report.append(f"- **{rec['action']}**: {rec['description']}")

    # Recommendations
    if recommendations:
        report.append("\n## Recommendations")

        # Group by priority
        priorities = {"high": [], "medium": [], "low": []}
        for rec in recommendations:
            # Ensure recommendation has a priority
            priority = rec.get("priority", "medium")
            if priority not in priorities:
                priority = "medium"
            priorities[priority].append(rec)

        # Print high priority recommendations first
        for priority in ["high", "medium", "low"]:
            if priorities[priority]:
                report.append(f"\n### {priority.capitalize()} Priority")
                for rec in priorities[priority]:
                    report.append(f"- **{rec['description']}**")
                    report.append(f"  - *Why*: {rec.get('reason', 'Recommended based on project analysis')}")

    # Next Steps
    report.append("\n## Suggested Next Steps")

    # New files
    if next_steps.get("new_files"):
        report.append("\n### Suggested New Files")
        for file_suggestion in next_steps["new_files"]:
            report.append(f"- **{file_suggestion['file_path']}**")
            report.append(f"  - {file_suggestion['description']}")

    # Updates to existing files
    if next_steps.get("updates"):
        report.append("\n### Suggested Updates to Existing Files")
        for update_suggestion in next_steps["updates"]:
            report.append(f"- **{update_suggestion['file_path']}**")
            report.append(f"  - {update_suggestion['description']}")

    # Feature suggestions
    if next_steps.get("next_features"):
        report.append("\n### Feature Implementation Ideas")
        for feature in next_steps["next_features"]:
            report.append(f"- **{feature['title']}**")
            report.append(f"  - {feature['description']}")
            report.append("  - Implementation steps:")
            for step in feature["steps"]:
                report.append(f"    - {step}")

    # Recent activity
    if project_summary.get("recently_modified_files"):
        report.append("\n## Recent Activity")
        report.append("Files modified recently:")
        for file in project_summary.get("recently_modified_files", [])[:5]:
            report.append(f"- {file['path']} ({file['last_modified']})")

    # AI Assistance Guide
    report.append("\n## AI Assistance Guide")
    report.append("When sharing this report with an AI assistant like Claude:")
    report.append("1. **Ask specific questions** about the project structure or recommendations")
    report.append("2. **Request code implementation** for specific features")
    report.append("3. **Ask for refactoring help** for complex files")
    report.append("4. **Request explanations** of technical concepts in the project")
    report.append("5. **Get detailed implementation plans** for suggested features")
    report.append("\nExample prompts:")
    report.append('- "Can you help me implement the JWT authentication feature suggested in the report?"')
    report.append('- "Please refactor the complex file X.py according to the recommendations"')
    report.append('- "Write the code for the suggested new file api/routes.py"')

    return "\n".join(report)

def analyze_complex_files(analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Analyze complex files in more detail and provide specific refactoring recommendations."""
    if not analysis or not analysis.get("potential_issues"):
        return {}

    complex_file_recommendations = defaultdict(list)

    for issue in analysis.get("potential_issues", []):
        if issue["type"] == "high_complexity":
            file_path = issue["file"]
            file_ext = os.path.splitext(file_path)[1].lower()

            # Skip node_modules and test files
            if 'node_modules' in file_path or 'test' in file_path:
                continue

            file_info = analysis.get("files", {}).get(file_path, {})

            if file_ext == '.py':
                complex_file_recommendations[file_path].append({
                    "action": "Extract functions",
                    "description": "Break down large functions into smaller, more focused ones"
                })
                complex_file_recommendations[file_path].append({
                    "action": "Create classes",
                    "description": "Group related functionality into classes"
                })
                complex_file_recommendations[file_path].append({
                    "action": "Split file",
                    "description": "Move related functions into separate modules"
                })
            elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                complex_file_recommendations[file_path].append({
                    "action": "Component decomposition",
                    "description": "Break down large components into smaller ones"
                })
                complex_file_recommendations[file_path].append({
                    "action": "Extract hooks",
                    "description": "Move complex logic into custom hooks"
                })
                complex_file_recommendations[file_path].append({
                    "action": "Create utility functions",
                    "description": "Extract repeated logic into utility functions"
                })
            elif file_ext in ['.json']:
                complex_file_recommendations[file_path].append({
                    "action": "Split large configuration",
                    "description": "Divide configuration into logical parts in separate files"
                })
            else:
                complex_file_recommendations[file_path].append({
                    "action": "General refactoring",
                    "description": "Break down the file into multiple smaller modules"
                })

    return dict(complex_file_recommendations)

def get_recommendations(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate recommendations based on the analysis."""
    if not analysis:
        return []

    recommendations = []

    # Check for potential issues - EXCLUDE NODE_MODULES
    if analysis.get("potential_issues"):
        for issue in analysis.get("potential_issues", []):
            if issue["type"] == "high_complexity" and 'node_modules' not in issue['file']:
                recommendations.append({
                    "type": "refactoring",
                    "priority": "medium",
                    "description": f"Consider refactoring {issue['file']} into smaller modules",
                    "reason": "File has high complexity which could lead to maintenance challenges"
                })
    
    # Check for outdated dependencies (simplified approach)
    if "detected_dependencies" in analysis:
        for dep_type, dep_info in analysis["detected_dependencies"].items():
            if dep_info.get("count", 0) > 20:
                recommendations.append({
                    "type": "dependency_management",
                    "priority": "medium",
                    "description": f"Consider auditing and pruning your {dep_type} dependencies",
                    "reason": f"You have {dep_info.get('count')} dependencies which may include unused or outdated packages"
                })
    
    # Check for testing
    file_types = analysis.get("project_summary", {}).get("file_types", {})
    if file_types.get("tests", 0) < file_types.get("backend", 0) * 0.3:
        recommendations.append({
            "type": "testing",
            "priority": "high",
            "description": "Increase test coverage for backend code",
            "reason": "The ratio of test files to backend files is low"
        })
    
    # Check for documentation
    if file_types.get("docs", 0) < 3 and analysis.get("project_summary", {}).get("file_count", 0) > 20:
        recommendations.append({
            "type": "documentation",
            "priority": "medium",
            "description": "Add more documentation files (README.md, API docs, etc.)",
            "reason": "Limited documentation found for a project of this size"
        })
    
    # Check for configuration management
    tech_stack = analysis.get("technology_stack", {})
    languages = tech_stack.get("languages", [])
    if len(languages) > 2 and file_types.get("config", 0) < 3:
        recommendations.append({
            "type": "configuration",
            "priority": "low",
            "description": "Consider using more configuration files to manage environment settings",
            "reason": "Multi-language projects benefit from clear configuration management"
        })
    
    # Validate all recommendations have required keys
    validated_recommendations = []
    for rec in recommendations:
        if "priority" not in rec:
            # Default to medium priority if missing
            rec["priority"] = "medium"
        if "description" not in rec:
            continue  # Skip recommendations without a description
        if "reason" not in rec:
            rec["reason"] = "Recommended based on project analysis"
        
        validated_recommendations.append(rec)
    
    return sorted(validated_recommendations, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])

def main():
    """Main entry point for the interactive development workflow."""
    print("\n=======================================")
    print("  AI-Assisted Development Workflow")
    print("=======================================\n")
    
    # Get the project directory
    project_dir = os.getcwd()
    print(f"Working directory: {project_dir}\n")
    
    # Create output directory
    output_dir = os.path.join(project_dir, "project_analysis")
    os.makedirs(output_dir, exist_ok=True)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Analyze project")
        print("2. Run tests")
        print("3. Generate new files")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            print("\nAnalyzing project structure...")
            # Get version
            version = get_latest_version(output_dir)
            print(f"Creating report version {version}")
            
            # Run analysis
            analysis = analyze_directory(project_dir)
            if "error" in analysis:
                print(f"Error: {analysis['error']}")
                continue
                
            # Generate recommendations
            complex_file_analysis = analyze_complex_files(analysis)
            recommendations = get_recommendations(analysis)
            next_steps = suggest_next_steps(analysis)
            
            # Generate reports
            report = generate_report(analysis, recommendations, complex_file_analysis, next_steps, version)
            ai_guide = generate_ai_assistant_guide(analysis, recommendations, next_steps)
            
            # Save reports
            analysis_path = os.path.join(output_dir, f"project_analysis_v{version}.json")
            with open(analysis_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            report_path = os.path.join(output_dir, f"project_report_v{version}.md")
            with open(report_path, 'w') as f:
                f.write(report)
            
            guide_path = os.path.join(output_dir, f"ai_assistant_guide_v{version}.md")
            with open(guide_path, 'w') as f:
                f.write(ai_guide)
                
            print(f"\nAnalysis complete!")
            print(f"Report saved to: {report_path}")
            print(f"AI Assistant guide saved to: {guide_path}")
            
        elif choice == '2':
            print("\nRunning tests...")
            test_results = run_all_tests(project_dir)
            
            if "error" in test_results:
                print(f"Error running tests: {test_results['error']}")
            else:
                summary = test_results.get("summary", {})
                print(f"\nTest Summary:")
                print(f"- Total Tests: {summary.get('total_tests', 0)}")
                print(f"- Passed: {summary.get('passed_tests', 0)}")
                print(f"- Failed: {summary.get('failed_tests', 0)}")
                print(f"- Errors: {summary.get('error_tests', 0)}")
                
                # Save test report
                test_report = generate_test_report(test_results, project_dir)
                report_path = os.path.join(output_dir, f"test_report_{time.strftime('%Y%m%d_%H%M%S')}.md")
                with open(report_path, 'w') as f:
                    f.write(test_report)
                    
                print(f"\nDetailed test report saved to: {report_path}")
                
        elif choice == '3':
            print("\nGenerating new files based on recommendations...")
            
            # First need to analyze the project
            analysis = analyze_directory(project_dir)
            if "error" in analysis:
                print(f"Error: {analysis['error']}")
                continue
                
            # Get next steps
            next_steps = suggest_next_steps(analysis)
            
            if not next_steps.get("new_files"):
                print("No new file recommendations available.")
            else:
                print("\nAvailable file templates:")
                for i, file_suggestion in enumerate(next_steps["new_files"], 1):
                    print(f"{i}. {file_suggestion['file_path']} - {file_suggestion['description']}")
                
                file_choice = input("\nEnter number of file to create (or 'all' for all files): ")
                
                if file_choice.lower() == 'all':
                    create_next_files(project_dir, next_steps, analysis.get("technology_stack", {}))
                    print("All recommended files have been created.")
                else:
                    try:
                        idx = int(file_choice) - 1
                        if 0 <= idx < len(next_steps["new_files"]):
                            file_suggestion = next_steps["new_files"][idx]
                            file_path = file_suggestion["file_path"]
                            full_path = os.path.join(project_dir, file_path)
                            
                            # Create directory if it doesn't exist
                            os.makedirs(os.path.dirname(full_path), exist_ok=True)
                            
                            # Use template content if provided, otherwise generate one
                            content = file_suggestion.get("template", "").strip()
                            if not content:
                                content = generate_code_template(file_path, analysis.get("technology_stack", {}))
                            
                            with open(full_path, 'w') as f:
                                f.write(content)
                            
                            print(f"Created new file: {file_path}")
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Please enter a number or 'all'.")
            
        elif choice == '4':
            print("\nExiting. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        traceback.print_exc()
