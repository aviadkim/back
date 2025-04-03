#!/usr/bin/env python3
"""
Project Analyzer for GitHub Codespace
-------------------------------------
This script analyzes your GitHub project structure and provides recommendations
that you can share with Claude or other AI assistants to guide improvements.

Usage:
1. Run this script in your GitHub Codespace
2. Share the output with your AI assistant
3. Use the AI suggestions with Cursor to implement changes

Requirements: Python 3.6+
"""

import os
import sys
import json
import time
import fnmatch
import subprocess
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any, Optional

# Maximum file size to analyze (in bytes)
MAX_FILE_SIZE = 1024 * 1024  # 1MB

# Patterns for files to ignore
IGNORE_PATTERNS = [
    '.git/*', '__pycache__/*', 'node_modules/*', '.venv/*', 'venv/*',
    '*.pyc', '*.pyo', '*.so', '*.class', '*.dll', '*.exe', '*.o', '*.a',
    '*.jar', '*.war', '*.ear', '*.zip', '*.tar.gz', '*.rar',
    '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.ico', '*.tiff',
    '*.mp3', '*.mp4', '*.wav', '*.avi', '*.mov', '*.mkv',
    '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx',
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
}

def should_ignore(path: str) -> bool:
    """Check if a file should be ignored based on patterns."""
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
            'PyTest': ['pytest', 'test_', '_test.py'],
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
        # This is a simple approach - more sophisticated parsing could be done
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
    
    # Simple complexity heuristic based on file size
    if lines < 100:
        complexity = 'low'
    elif lines < 300:
        complexity = 'medium'
    else:
        complexity = 'high'
    
    # Additional language-specific complexity metrics could be added here
    file_ext = os.path.splitext(file_path)[1].lower()
    
    result = {
        'lines': lines,
        'complexity': complexity,
    }
    
    return result

def analyze_directory(root_dir: str) -> Dict[str, Any]:
    """Analyze a directory and return information about its structure and files."""
    start_time = time.time()
    
    if not os.path.exists(root_dir):
        return {"error": f"Directory {root_dir} does not exist"}
    
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
        "potential_issues": []
    }
    
    # Collect all files
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        rel_dirpath = os.path.relpath(dirpath, root_dir)
        
        if should_ignore(rel_dirpath):
            dirnames[:] = []  # Don't go into ignored directories
            continue
            
        results["project_summary"]["directory_count"] += 1
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            rel_file_path = os.path.relpath(file_path, root_dir)
            
            if should_ignore(rel_file_path):
                continue
                
            try:
                file_stat = os.stat(file_path)
                file_type = get_file_type(rel_file_path)
                file_ext = os.path.splitext(rel_file_path)[1].lower()
                
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
                            
                            # Analyze complexity
                            complexity_info = get_file_complexity(file_path, content)
                            file_info.update(complexity_info)
                            
                            # Flag potential issues
                            if complexity_info.get('complexity') == 'high':
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

def get_recommendations(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate recommendations based on the analysis."""
    recommendations = []
    
    # Check for potential issues
    if analysis.get("potential_issues"):
        for issue in analysis["potential_issues"]:
            if issue["type"] == "high_complexity":
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
    
    # Add build system recommendation if needed
    if "JavaScript" in tech_stack.get("languages", []) and "Webpack" not in tech_stack.get("build_tools", []) and "Vite" not in tech_stack.get("build_tools", []):
        recommendations.append({
            "type": "build_tools",
            "priority": "medium",
            "description": "Consider adding a modern build tool like Webpack or Vite",
            "reason": "JavaScript project without a modern build system may have suboptimal performance"
        })
    
    # Check project structure
    files = analysis.get("files", {})
    has_src_dir = any(path.startswith("src/") for path in files.keys())
    if not has_src_dir and len(files) > 10:
        recommendations.append({
            "type": "project_structure",
            "priority": "low",
            "description": "Consider organizing code into a src/ directory and separating from configuration files",
            "reason": "Improved organization helps maintainability as projects grow"
        })
    
    return sorted(recommendations, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])

def generate_report(analysis: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
    """Generate a formatted report from the analysis and recommendations."""
    report = []
    report.append("# Project Analysis Report")
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
    for file_type, count in file_types.items():
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
    
    # Recommendations
    if recommendations:
        report.append("\n## Recommendations")
        
        # Group by priority
        priorities = {"high": [], "medium": [], "low": []}
        for rec in recommendations:
            priorities[rec["priority"]].append(rec)
        
        # Print high priority recommendations first
        for priority in ["high", "medium", "low"]:
            if priorities[priority]:
                report.append(f"\n### {priority.capitalize()} Priority")
                for rec in priorities[priority]:
                    report.append(f"- **{rec['description']}**")
                    report.append(f"  - *Why*: {rec['reason']}")
    
    # Recent activity
    if project_summary.get("recently_modified_files"):
        report.append("\n## Recent Activity")
        report.append("Files modified recently:")
        for file in project_summary.get("recently_modified_files", [])[:5]:
            report.append(f"- {file['path']} ({file['last_modified']})")
    
    return "\n".join(report)

def main():
    print("\nProject Analyzer for GitHub Codespace")
    print("--------------------------------------")
    
    # Get the project directory
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        project_dir = os.getcwd()
        print(f"Analyzing current directory: {project_dir}")
    
    print("Analysis in progress... This may take a few moments.")
    
    # Run the analysis
    analysis = analyze_directory(project_dir)
    
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    # Generate recommendations
    recommendations = get_recommendations(analysis)
    
    # Generate the report
    report = generate_report(analysis, recommendations)
    
    # Output the report
    print("\nAnalysis completed!")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_dir, "project_analysis")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save full analysis as JSON
    analysis_path = os.path.join(output_dir, "project_analysis.json")
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Save report as markdown
    report_path = os.path.join(output_dir, "project_report.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nFull analysis saved to: {analysis_path}")
    print(f"Summary report saved to: {report_path}")
    print("\nPlease share the report with your AI assistant for specific recommendations.")
    
    # Print the report to console as well
    print("\n" + "=" * 80)
    print(report)
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAnalysis cancelled by user.")
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")