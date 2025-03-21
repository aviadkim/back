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

if __name__ == "__main__":
    init_app()
