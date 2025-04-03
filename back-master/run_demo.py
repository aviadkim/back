"""
Simple runner for the agent demonstration script
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Run the demonstration script"""
    logger.info("Setting up environment...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if Hugging Face API key is set
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        logger.error("HUGGINGFACE_API_KEY environment variable is not set")
        logger.error("Please set this in your .env file or environment")
        return False
    
    logger.info(f"Found HUGGINGFACE_API_KEY: {api_key[:4]}...{api_key[-4:]}")
    
    # Make sure HUGGINGFACE_HUB_TOKEN is also set
    os.environ["HUGGINGFACE_HUB_TOKEN"] = api_key
    logger.info("Set HUGGINGFACE_HUB_TOKEN from HUGGINGFACE_API_KEY")
    
    # Run the demonstration script
    logger.info("Running agent demonstration...")
    try:
        from demonstrate_agents import demonstrate_agent_capabilities
        
        # Call the demonstration function
        result = demonstrate_agent_capabilities()
        
        if result:
            logger.info("Demonstration completed successfully")
        else:
            logger.error("Demonstration failed")
        
        return result
    except Exception as e:
        logger.error(f"Error running demonstration: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    main()
