#!/usr/bin/env python3
"""
Project Manager Assistant v1.9
----------------------------
This script serves as your central dashboard for managing the project,
integrating all the tools we've created and providing a unified interface.

Updates in v1.9:
- Added robust test framework detection and execution
- Improved error handling and feedback
- Added support for multiple test frameworks (pytest, unittest, jest, mocha)
- Better handling of missing dependencies

Usage:
1. Run in your GitHub Codespace
2. Select the action you want to perform
3. Get comprehensive insights and manage your project efficiently
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
import webbrowser

class ProjectManager:
    def __init__(self):
        self.project_dir = os.getcwd()
        
        # Check for required dependencies
        self.available_test_frameworks = self._check_test_frameworks()
        
        self.tools = {
            "1": {
                "name": "Project Analysis",
                "description": "Analyze project structure and provide recommendations",
                "script": "project_analyzer.py"
            },
            "2": {
                "name": "App Diagnostics",
                "description": "Diagnose application issues and connectivity problems",
                "script": "app_diagnostics.py"
            },
            "3": {
                "name": "Performance Monitor",
                "description": "Monitor application performance in real-time",
                "script": "performance_monitor.py"
            },
            "4": {
                "name": "Link & API Validator",
                "description": "Check for broken links and API issues",
                "script": "link_validator.py"
            },
            "5": {
                "name": "Test Data Generator",
                "description": "Generate test data for your application",
                "script": "data_generator.py"
            },
            "6": {
                "name": "Create New Feature",
                "description": "Generate scaffolding for a new feature",
                "function": self.create_new_feature
            },
            "7": {
                "name": "Project Dashboard",
                "description": "Open project dashboard in browser",
                "function": self.open_dashboard
            },
            "8": {
                "name": "Run Tests",
                "description": "Run all tests for the project",
                "function": self.run_tests
            }
        }
        
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
    
    def _check_test_frameworks(self):
        """Check which testing frameworks are available"""
        frameworks = {
            'pytest': False,
            'unittest': False,
            'jest': False,
            'mocha': False
        }
        
        # Check Python test frameworks
        try:
            import pytest
            frameworks['pytest'] = True
        except ImportError:
            pass
            
        try:
            import unittest
            frameworks['unittest'] = True
        except ImportError:
            pass
            
        # Check JS test frameworks
        if os.path.exists("package.json"):
            if os.path.exists(os.path.join("node_modules", "jest")):
                frameworks['jest'] = True
            if os.path.exists(os.path.join("node_modules", "mocha")):
                frameworks['mocha'] = True
        
        return frameworks

    def display_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 60)
        print("  Project Manager Assistant")
        print("=" * 60)
        print("\nAvailable tools:\n")
        
        for key, tool in self.tools.items():
            print(f"{key}. {tool['name']}")
            print(f"   {tool['description']}")
            print()
        
        print("0. Exit")
        print("=" * 60)
    
    def run(self):
        """Run the project manager"""
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (0-8): ")
            
            if choice == "0":
                print("\nExiting Project Manager. Goodbye!")
                break
            
            if choice in self.tools:
                tool = self.tools[choice]
                print(f"\nRunning {tool['name']}...")
                
                if "script" in tool:
                    self.run_script(tool["script"])
                elif "function" in tool:
                    tool["function"]()
            else:
                print("\nInvalid choice. Please try again.")
    
    def run_script(self, script_name):
        """Run a script from the tools directory"""
        script_path = os.path.join(self.project_dir, script_name)
        
        if os.path.exists(script_path):
            try:
                subprocess.run([sys.executable, script_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running {script_name}: {e}")
        else:
            print(f"Script not found: {script_path}")
            print("Please make sure all tool scripts are in your project directory.")
    
    def run_tests(self):
        """Run all tests for the project"""
        print("\nScanning for tests...")
        
        # First check if any test framework is available
        if not any(self.available_test_frameworks.values()):
            print("\n⚠️  No testing frameworks detected. Please install required dependencies:")
            print("\nFor Python tests, run one of:")
            print("    pip install pytest")
            print("    pip install pytest-cov  # for coverage reports")
            print("\nFor JavaScript tests, run one of:")
            print("    npm install --save-dev jest")
            print("    npm install --save-dev mocha")
            return False
        
        # First check if test directories exist
        test_dirs = []
        test_files = []
        
        for root, dirs, files in os.walk(self.project_dir):
            # Skip virtual environments and cache directories
            if any(skip in root for skip in ["node_modules", ".git", "__pycache__", "venv", "env", ".venv", ".pytest_cache"]):
                continue
                
            # Look for test files and directories
            if any(name in dirs for name in ["tests", "test", "__tests__"]):
                test_dirs.append(root)
            
            # Look for individual test files
            for file in files:
                if file.startswith("test_") or file.endswith("_test.py") or file.endswith(".test.js"):
                    test_files.append(os.path.join(root, file))
        
        if not test_dirs and not test_files:
            print("⚠️  No test files or directories found.")
            return False
        
        print(f"\nFound {len(test_dirs)} test directories and {len(test_files)} test files.")
        
        # Track test execution status
        success = True
        tests_run = False
        
        # Try Python tests first
        if self.available_test_frameworks['pytest']:
            try:
                import pytest
                print("\nRunning pytest...")
                pytest_args = ["-v", "--color=yes"]
                pytest_result = pytest.main(pytest_args)
                tests_run = True
                if pytest_result != 0:
                    success = False
                    print("❌ Some pytest tests failed")
                else:
                    print("✅ All pytest tests passed")
            except ImportError:
                pass
        
        if not tests_run and self.available_test_frameworks['unittest']:
            try:
                import unittest
                print("\nRunning unittest...")
                # Find and run all tests using unittest
                suite = unittest.TestLoader().discover(self.project_dir, pattern="test_*.py")
                result = unittest.TextTestRunner(verbosity=2).run(suite)
                tests_run = True
                if not result.wasSuccessful():
                    success = False
                    print("❌ Some unittest tests failed")
                else:
                    print("✅ All unittest tests passed")
            except ImportError:
                pass
        
        # Try JavaScript tests
        if os.path.exists("package.json"):
            if self.available_test_frameworks['jest']:
                print("\nRunning Jest tests...")
                try:
                    result = subprocess.run(
                        ["npx", "jest", "--color"],
                        capture_output=True,
                        text=True,
                        cwd=self.project_dir
                    )
                    tests_run = True
                    print(result.stdout)
                    if result.returncode != 0:
                        success = False
                        print("❌ Jest tests failed")
                    else:
                        print("✅ Jest tests passed")
                except subprocess.CalledProcessError as e:
                    print(f"Error running Jest: {e}")
                    success = False
                except FileNotFoundError:
                    print("⚠️  npx not found. Please install Node.js and npm")
            
            elif self.available_test_frameworks['mocha']:
                print("Running Mocha tests...")
                try:
                    result = subprocess.run(
                        ["npx", "mocha", "--color"],
                        capture_output=True,
                        text=True,
                        cwd=self.project_dir
                    )
                    tests_run = True
                    print(result.stdout)
                    if result.returncode != 0:
                        success = False
                        print("❌ Mocha tests failed")
                    else:
                        print("✅ Mocha tests passed")
                except subprocess.CalledProcessError as e:
                    print(f"Error running Mocha: {e}")
                    success = False
                except FileNotFoundError:
                    print("⚠️  npx not found. Please install Node.js and npm")
        
        if not tests_run:
            print("\n⚠️  No testing frameworks detected. Please install one of the following:")
            print("- pytest or unittest (for Python tests)")
            print("- jest (for JavaScript tests)")
            print("- mocha (for JavaScript tests)")
            return False
        
        print("\nTest Summary:")
        print("-------------")
        if success:
            print("✅ All tests completed successfully!")
        else:
            print("❌ Some tests failed. Please check the output above for details.")
        
        return success

    def create_new_feature(self):
        """Generate scaffolding for a new feature"""
        print("\nCreate New Feature")
        print("-----------------")
        
        feature_name = input("Enter feature name (e.g., user-authentication): ")
        if not feature_name:
            print("Feature name cannot be empty.")
            return
        
        feature_type = input("Enter feature type (frontend/backend/full): ")
        if feature_type not in ["frontend", "backend", "full"]:
            print("Invalid feature type. Using 'full' as default.")
            feature_type = "full"
        
        # Create feature directory
        feature_dir = os.path.join(self.project_dir, "src", "features", feature_name)
        os.makedirs(feature_dir, exist_ok=True)
        
        if feature_type in ["frontend", "full"]:
            # Create frontend files
            os.makedirs(os.path.join(feature_dir, "components"), exist_ok=True)
            
            # Create component file
            component_name = "".join(word.capitalize() for word in feature_name.split("-"))
            
            with open(os.path.join(feature_dir, "components", f"{component_name}.jsx"), "w") as f:
                f.write(f"""import React, {{ useState, useEffect }} from 'react';
import './styles.css';

const {component_name} = () => {{
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {{
    const fetchData = async () => {{
      try {{
        // TODO: Replace with actual API call
        const response = await fetch('/api/{feature_name}');
        
        if (!response.ok) {{
          throw new Error(`HTTP error! Status: ${{response.status}}`);
        }}
        
        const result = await response.json();
        setData(result);
        setError(null);
      }} catch (err) {{
        setError(err.message);
        setData(null);
      }} finally {{
        setLoading(false);
      }}
    }};

    fetchData();
  }}, []);

  return (
    <div className="{feature_name}-container">
      <h2>{component_name}</h2>
      
      {{loading && <div className="loading">Loading...</div>}}
      {{error && <div className="error">Error: {{error}}</div>}}
      
      {{data && (
        <div className="data-container">
          /* TODO: Render your data here */
          <pre>{{JSON.stringify(data, null, 2)}}</pre>
        </div>
      )}}
    </div>
  );
}};

export default {component_name};
""")
            
            # Create styles file
            with open(os.path.join(feature_dir, "components", "styles.css"), "w") as f:
                f.write(f"""/* Styles for {feature_name} */
.{feature_name}-container {{
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  margin: 20px 0;
}}

.loading {{
  color: #888;
  font-style: italic;
}}

.error {{
  color: #d32f2f;
  background-color: #ffebee;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}}

.data-container {{
  margin-top: 20px;
}}
""")
            
            # Create index file
            with open(os.path.join(feature_dir, "index.js"), "w") as f:
                f.write(f"""export {{ default as {component_name} }} from './components/{component_name}';
""")
        
        if feature_type in ["backend", "full"]:
            # Create backend files
            os.makedirs(os.path.join(feature_dir, "api"), exist_ok=True)
            
            # Create API route file
            with open(os.path.join(feature_dir, "api", "routes.js"), "w") as f:
                f.write(f"""const express = require('express');
const router = express.Router();
const controller = require('./controller');

// GET all items
router.get('/', controller.getAll);

// GET single item by ID
router.get('/:id', controller.getById);

// POST new item
router.post('/', controller.create);

// PUT update item
router.put('/:id', controller.update);

// DELETE item
router.delete('/:id', controller.delete);

module.exports = router;
""")
            
            # Create controller file
            with open(os.path.join(feature_dir, "api", "controller.js"), "w") as f:
                f.write(f"""const service = require('./service');

exports.getAll = async (req, res) => {{
  try {{
    const items = await service.getAll();
    res.json(items);
  }} catch (err) {{
    res.status(500).json({{ error: err.message }});
  }}
}};

exports.getById = async (req, res) => {{
  try {{
    const item = await service.getById(req.params.id);
    if (!item) {{
      return res.status(404).json({{ error: 'Item not found' }});
    }}
    res.json(item);
  }} catch (err) {{
    res.status(500).json({{ error: err.message }});
  }}
}};

exports.create = async (req, res) => {{
  try {{
    const newItem = await service.create(req.body);
    res.status(201).json(newItem);
  }} catch (err) {{
    res.status(400).json({{ error: err.message }});
  }}
}};

exports.update = async (req, res) => {{
  try {{
    const updatedItem = await service.update(req.params.id, req.body);
    if (!updatedItem) {{
      return res.status(404).json({{ error: 'Item not found' }});
    }}
    res.json(updatedItem);
  }} catch (err) {{
    res.status(400).json({{ error: err.message }});
  }}
}};

exports.delete = async (req, res) => {{
  try {{
    const deleted = await service.delete(req.params.id);
    if (!deleted) {{
      return res.status(404).json({{ error: 'Item not found' }});
    }}
    res.status(204).send();
  }} catch (err) {{
    res.status(500).json({{ error: err.message }});
  }}
}};
""")
            
            # Create service file
            with open(os.path.join(feature_dir, "api", "service.js"), "w") as f:
                f.write(f"""// TODO: Replace with actual database model
const items = [];
let nextId = 1;

exports.getAll = async () => {{
  return [...items];
}};

exports.getById = async (id) => {{
  return items.find(item => item.id === parseInt(id));
}};

exports.create = async (data) => {{
  const newItem = {{
    id: nextId++,
    ...data,
    createdAt: new Date().toISOString()
  }};
  
  items.push(newItem);
  return newItem;
}};

exports.update = async (id, data) => {{
  const index = items.findIndex(item => item.id === parseInt(id));
  
  if (index === -1) {{
    return null;
  }}
  
  const updatedItem = {{
    ...items[index],
    ...data,
    updatedAt: new Date().toISOString()
  }};
  
  items[index] = updatedItem;
  return updatedItem;
}};

exports.delete = async (id) => {{
  const index = items.findIndex(item => item.id === parseInt(id));
  
  if (index === -1) {{
    return false;
  }}
  
  items.splice(index, 1);
  return true;
}};
""")
        
        # Create tests directory
        os.makedirs(os.path.join(feature_dir, "tests"), exist_ok=True)
        
        if feature_type in ["frontend", "full"]:
            # Create frontend test file
            with open(os.path.join(feature_dir, "tests", f"{component_name}.test.js"), "w") as f:
                f.write(f"""import React from 'react';
import {{ render, screen, waitFor }} from '@testing-library/react';
import '@testing-library/jest-dom';
import {{ {component_name} }} from '../index';

// Mock fetch API
global.fetch = jest.fn();

describe('{component_name} Component', () => {{
  beforeEach(() => {{
    fetch.mockClear();
  }});

  it('renders loading state initially', () => {{
    // Mock the fetch implementation
    fetch.mockImplementationOnce(() => {{
      return new Promise(resolve => {{
        // This promise never resolves to simulate loading
      }});
    }});

    render(<{component_name} />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  }});

  it('renders data when fetch succeeds', async () => {{
    // Mock data
    const mockData = {{ example: 'data' }};
    
    // Mock the fetch implementation
    fetch.mockImplementationOnce(() => {{
      return Promise.resolve({{
        ok: true,
        json: () => Promise.resolve(mockData)
      }});
    }});

    render(<{component_name} />);
    
    // Wait for loading to finish
    await waitFor(() => {{
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    }});
    
    // Expect data to be rendered
    expect(screen.getByText(JSON.stringify(mockData, null, 2))).toBeInTheDocument();
  }});

  it('renders error when fetch fails', async () => {{
    // Mock the fetch implementation
    fetch.mockImplementationOnce(() => {{
      return Promise.resolve({{
        ok: false,
        status: 500
      }});
    }});

    render(<{component_name} />);
    
    // Wait for loading to finish and error to show
    await waitFor(() => {{
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    }});
  }});
}});
""")
        
        if feature_type in ["backend", "full"]:
            # Create backend test file
            with open(os.path.join(feature_dir, "tests", "api.test.js"), "w") as f:
                f.write(f"""const request = require('supertest');
const express = require('express');
const router = require('../api/routes');

// Create test app
const app = express();
app.use(express.json());
app.use('/api/{feature_name}', router);

describe('{feature_name} API', () => {{
  it('GET / should return all items', async () => {{
    const res = await request(app).get('/api/{feature_name}');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBeTruthy();
  }});

  it('POST / should create a new item', async () => {{
    const newItem = {{
      name: 'Test Item',
      description: 'This is a test item'
    }};
    
    const res = await request(app)
      .post('/api/{feature_name}')
      .send(newItem);
    
    expect(res.statusCode).toEqual(201);
    expect(res.body).toHaveProperty('id');
    expect(res.body.name).toEqual(newItem.name);
  }});

  it('GET /:id should return a single item', async () => {{
    // First create an item
    const newItem = {{ name: 'Get Test' }};
    const createRes = await request(app)
      .post('/api/{feature_name}')
      .send(newItem);
    
    const id = createRes.body.id;
    
    // Then get the item
    const getRes = await request(app).get(`/api/{feature_name}/${{id}}`);
    
    expect(getRes.statusCode).toEqual(200);
    expect(getRes.body.id).toEqual(id);
  }});

  it('PUT /:id should update an item', async () => {{
    // First create an item
    const newItem = {{ name: 'Update Test' }};
    const createRes = await request(app)
      .post('/api/{feature_name}')
      .send(newItem);
    
    const id = createRes.body.id;
    const updateData = {{ name: 'Updated Name' }};
    
    // Then update the item
    const updateRes = await request(app)
      .put(`/api/{feature_name}/${{id}}`)
      .send(updateData);
    
    expect(updateRes.statusCode).toEqual(200);
    expect(updateRes.body.name).toEqual(updateData.name);
  }});

  it('DELETE /:id should delete an item', async () => {{
    // First create an item
    const newItem = {{ name: 'Delete Test' }};
    const createRes = await request(app)
      .post('/api/{feature_name}')
      .send(newItem);
    
    const id = createRes.body.id;
    
    // Then delete the item
    const deleteRes = await request(app).delete(`/api/{feature_name}/${{id}}`);
    expect(deleteRes.statusCode).toEqual(204);
    
    // Try to get the deleted item
    const getRes = await request(app).get(`/api/{feature_name}/${{id}}`);
    expect(getRes.statusCode).toEqual(404);
  }});
}});
""")
        
        # Create README file
        with open(os.path.join(feature_dir, "README.md"), "w") as f:
            f.write(f"""# {feature_name.replace('-', ' ').title()} Feature

## Overview
{feature_name.replace('-', ' ').title()} feature implementation.

## Structure
```
{feature_name}/
├── api/                # Backend API files
│   ├── routes.js       # API endpoints
│   ├── controller.js   # Request handlers
│   └── service.js      # Business logic
├── components/         # Frontend components
│   ├── {component_name}.jsx  # Main component
│   └── styles.css      # Component styles
├── tests/              # Test files
│   ├── {component_name}.test.js  # Frontend tests
│   └── api.test.js     # API tests
└── index.js            # Feature exports
```

## Usage
```jsx
import {{ {component_name} }} from './features/{feature_name}';

// Then use in your app
<{component_name} />
```

## API Endpoints
- `GET /api/{feature_name}` - Get all items
- `GET /api/{feature_name}/:id` - Get item by ID
- `POST /api/{feature_name}` - Create new item
- `PUT /api/{feature_name}/:id` - Update item
- `DELETE /api/{feature_name}/:id` - Delete item
""")
        
        print(f"\nFeature '{feature_name}' scaffolding created successfully!")
        print(f"Location: {feature_dir}")
    
    def open_dashboard(self):
        """Open the project dashboard in a browser"""
        dashboard_path = os.path.join(self.project_dir, "reports", "dashboard.html")
        
        # Generate the dashboard
        self.generate_dashboard()
        
        # Open in browser
        print(f"Opening dashboard: {dashboard_path}")
        try:
            webbrowser.open(f"file://{dashboard_path}")
        except Exception as e:
            print(f"Error opening dashboard: {e}")
    
    def generate_dashboard(self):
        """Generate the project dashboard"""
        dashboard_dir = os.path.join(self.project_dir, "reports")
        os.makedirs(dashboard_dir, exist_ok=True)
        
        # Collect data from various reports
        data = {
            "project_info": self.get_project_info(),
            "analysis": self.get_analysis_data(),
            "diagnostics": self.get_diagnostics_data(),
            "performance": self.get_performance_data(),
            "validation": self.get_validation_data(),
        }
        
        # Save dashboard data
        with open(os.path.join(dashboard_dir, "dashboard_data.json"), "w") as f:
            json.dump(data, f, indent=2)
        
        # Generate HTML dashboard
        with open(os.path.join(dashboard_dir, "dashboard.html"), "w") as f:
            f.write(self.generate_dashboard_html(data))
        
        print(f"Dashboard generated at: {os.path.join(dashboard_dir, 'dashboard.html')}")
    
    def get_project_info(self):
        """Get basic project information"""
        info = {
            "name": os.path.basename(self.project_dir),
            "path": self.project_dir,
            "generated_at": datetime.now().isoformat(),
        }
        
        # Try to get package.json info
        package_json_path = os.path.join(self.project_dir, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, "r") as f:
                    package_data = json.load(f)
                    info["version"] = package_data.get("version", "unknown")
                    info["description"] = package_data.get("description", "")
                    info["dependencies"] = len(package_data.get("dependencies", {}))
                    info["devDependencies"] = len(package_data.get("devDependencies", {}))
            except Exception:
                pass
        
        return info
    
    def get_analysis_data(self):
        """Get data from the project analysis report"""
        analysis_path = os.path.join(self.project_dir, "project_analysis", "project_analysis.json")
        if os.path.exists(analysis_path):
            try:
                with open(analysis_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def get_diagnostics_data(self):
        """Get data from the app diagnostics report"""
        diagnostics_path = os.path.join(self.project_dir, "app_diagnostics_report.json")
        if os.path.exists(diagnostics_path):
            try:
                with open(diagnostics_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def get_performance_data(self):
        """Get data from the performance monitoring report"""
        performance_path = os.path.join(self.project_dir, "monitoring", "performance_metrics.json")
        if os.path.exists(performance_path):
            try:
                with open(performance_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def get_validation_data(self):
        """Get data from the link validation report"""
        validation_path = os.path.join(self.project_dir, "validation", "validation_data.json")
        if os.path.exists(validation_path):
            try:
                with open(validation_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def generate_dashboard_html(self, data):
        """Generate the HTML for the dashboard"""
        # This is a simplified version - a real implementation would be more elaborate
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        h1, h2, h3 {
            margin-top: 0;
        }
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            overflow: hidden;
        }
        .card-header {
            background-color: #3498db;
            color: white;
            padding: 15px;
        }
        .card-body {
            padding: 15px;
        }
        .metric {
            display: inline-block;
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 10px;
            margin: 5px;
            min-width: 120px;
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            margin: 5px 0;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
        }
        .status-good {
            color: #2ecc71;
        }
        .status-warning {
            color: #f39c12;
        }
        .status-error {
            color: #e74c3c;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <header>
        <h1>Project Dashboard</h1>
        <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </header>
    <div class="container">
"""
        
        # Project Info Section
        project_info = data.get("project_info", {})
        html += """
        <div class="card">
            <div class="card-header">
                <h2>Project Information</h2>
            </div>
            <div class="card-body">
"""
        if project_info:
            html += f"""
                <div class="metric">
                    <div class="metric-label">Project</div>
                    <div class="metric-value">{project_info.get('name', 'Unknown')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Version</div>
                    <div class="metric-value">{project_info.get('version', 'N/A')}</div>
                </div>
"""
            if "dependencies" in project_info:
                html += f"""
                <div class="metric">
                    <div class="metric-label">Dependencies</div>
                    <div class="metric-value">{project_info.get('dependencies', 0)}</div>
                </div>
"""
        html += """
            </div>
        </div>
"""
        
        # Analysis Section
        analysis = data.get("analysis", {})
        if analysis:
            html += """
        <div class="card">
            <div class="card-header">
                <h2>Project Analysis</h2>
            </div>
            <div class="card-body">
"""
            project_summary = analysis.get("project_summary", {})
            if project_summary:
                html += f"""
                <div class="metric">
                    <div class="metric-label">Files</div>
                    <div class="metric-value">{project_summary.get('file_count', 0)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Directories</div>
                    <div class="metric-value">{project_summary.get('directory_count', 0)}</div>
                </div>
"""
            
            # File types breakdown
            file_types = project_summary.get("file_types", {})
            if file_types:
                html += """
                <h3>File Types</h3>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Count</th>
                    </tr>
"""
                for file_type, count in file_types.items():
                    html += f"""
                    <tr>
                        <td>{file_type}</td>
                        <td>{count}</td>
                    </tr>
"""
                html += """
                </table>
"""
            
            html += """
            </div>
        </div>
"""
        
        # Diagnostics Section
        diagnostics = data.get("diagnostics", {})
        if diagnostics:
            html += """
        <div class="card">
            <div class="card-header">
                <h2>Application Diagnostics</h2>
            </div>
            <div class="card-body">
"""
            issues_found = diagnostics.get("issues_found", 0)
            status_class = "status-good" if issues_found == 0 else "status-error"
            
            html += f"""
                <div class="metric">
                    <div class="metric-label">Issues Found</div>
                    <div class="metric-value {status_class}">{issues_found}</div>
                </div>
"""
            
            # Issues by category
            issues_by_category = diagnostics.get("issues_by_category", {})
            if issues_by_category:
                html += """
                <h3>Issues by Category</h3>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                    </tr>
"""
                for category, issues in issues_by_category.items():
                    html += f"""
                    <tr>
                        <td>{category}</td>
                        <td>{len(issues)}</td>
                    </tr>
"""
                html += """
                </table>
"""
            
            html += """
            </div>
        </div>
"""
        
        # Performance Section
        performance = data.get("performance", {})
        if performance:
            html += """
        <div class="card">
            <div class="card-header">
                <h2>Performance Metrics</h2>
            </div>
            <div class="card-body">
                <img src="../monitoring/performance_charts.png" alt="Performance Charts" style="max-width: 100%;">
            </div>
        </div>
"""
        
        # Validation Section
        validation = data.get("validation", {})
        if validation:
            html += """
        <div class="card">
            <div class="card-header">
                <h2>Link & API Validation</h2>
            </div>
            <div class="card-body">
"""
            broken_links = validation.get("broken_links", [])
            api_issues = validation.get("api_issues", [])
            
            html += f"""
                <div class="metric">
                    <div class="metric-label">Broken Links</div>
                    <div class="metric-value {('status-error' if broken_links else 'status-good')}">{len(broken_links)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">API Issues</div>
                    <div class="metric-value {('status-error' if api_issues else 'status-good')}">{len(api_issues)}</div>
                </div>
"""
            
            if broken_links:
                html += """
                <h3>Broken Links</h3>
                <table>
                    <tr>
                        <th>URL</th>
                        <th>Status</th>
                        <th>Reason</th>
                    </tr>
"""
                for link in broken_links[:10]:  # Show only top 10
                    html += f"""
                    <tr>
                        <td>{link.get('url', 'Unknown')}</td>
                        <td>{link.get('status', 'Unknown')}</td>
                        <td>{link.get('reason', 'Unknown')}</td>
                    </tr>
"""
                html += """
                </table>
"""
            
            html += """
            </div>
        </div>
"""
        
        # Close HTML
        html += """
    </div>
    <footer style="text-align: center; padding: 20px; background: #2c3e50; color: white;">
        <p>Project Manager Assistant</p>
    </footer>
</body>
</html>
"""
        return html

if __name__ == "__main__":
    try:
        manager = ProjectManager()
        manager.run()
    except KeyboardInterrupt:
        print("\nProject Manager cancelled by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()