import os
import sys
import logging
from typing import Dict, Any
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.memory.memory_manager import MemoryManager
from agents.financial.financial_agent import FinancialAgent
from pdf_processor.extraction.text_extractor import PDFTextExtractor
from pdf_processor.tables.table_extractor import TableExtractor
from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer

def init_logging():
    """Initialize logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("financial_analyzer")

def init_agents():
    """Initialize agents."""
    logger = logging.getLogger("init")
    
    # Create memory manager
    memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")
    os.makedirs(memory_dir, exist_ok=True)
    memory_manager = MemoryManager(memory_dir)
    
    # Create financial agent
    financial_agent = FinancialAgent(
        memory_path=memory_manager.get_agent_memory_path("financial")
    )
    
    logger.info("Agents initialized successfully")
    
    return {
        "memory_manager": memory_manager,
        "financial_agent": financial_agent
    }

def init_app():
    """Initialize the application."""
    logger = init_logging()
    
    logger.info("Initializing application...")
    
    # Initialize agents
    agents = init_agents()
    
    logger.info("Application initialized successfully")
    
    return agents

def analyze_directory(root_dir, should_ignore_func):
    """Shared directory analysis function"""
    results = {
        "project_summary": {
            "directory_count": 0,
            "file_count": 0
        }
    }
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        rel_dirpath = os.path.relpath(dirpath, root_dir)

        if should_ignore_func(rel_dirpath):
            dirnames[:] = []  # Don't go into ignored directories
            continue

        results["project_summary"]["directory_count"] += 1
    
    return results

def generate_priority_section(priorities, report):
    """Shared priority report generation"""
    for priority in ["high", "medium", "low"]:
        if priorities[priority]:
            report.append(f"\n### {priority.capitalize()} Priority")
            for rec in priorities[priority]:
                report.append(f"- **{rec['description']}**")
    return report

def add_recent_activity(project_summary, report):
    """Shared recent activity report generation"""
    if project_summary.get("recently_modified_files"):
        report.append("\n## Recent Activity")
        report.append("Files modified recently:")
        for file in project_summary.get("recently_modified_files", [])[:5]:
            report.append(f"- {file['path']} ({file['last_modified']})")
    return report

def generate_component_template(component_name, is_typescript=False, is_react=False):
    """Shared component template generation"""
    if not is_react:
        return ""
        
    if is_typescript:
        return f'''import React, {{ useState, useEffect }} from 'react';
interface {component_name}Props {{
    title?: string;
}}
const {component_name}: React.FC<{component_name}Props> = ({{ title = "Default Title" }}) => {{
    const [data, setData] = useState<any[]>([]);
    useEffect(() => {{
        console.log("Component mounted");
        return () => console.log("Component will unmount");
    }}, []);
    return (
        <div className="container">
            <h1>{{title}}</h1>
            <div className="content">
                <p>This is the {component_name} component</p>
            </div>
        </div>
    );
}};
export default {component_name};'''
    else:
        return f'''import React, {{ useState, useEffect }} from 'react';
const {component_name} = ({{ title = "Default Title" }}) => {{
    const [data, setData] = useState([]);
    useEffect(() => {{
        console.log("Component mounted");
        return () => console.log("Component will unmount");
    }}, []);
    return (
        <div className="container">
            <h1>{{title}}</h1>
            <div className="content">
                <p>This is the {component_name} component</p>
            </div>
        </div>
    );
}};
export default {component_name};'''
    
if __name__ == "__main__":
    init_app()
