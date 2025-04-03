import os
import logging
from agent_framework.coordinator import AgentCoordinator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def test_llm_setup():
    """Test if the LLM setup works properly"""
    # Print environment variables
    print(f"HUGGINGFACE_API_KEY present: {'Yes' if os.environ.get('HUGGINGFACE_API_KEY') else 'No'}")
    print(f"LLM_PROVIDER: {os.environ.get('LLM_PROVIDER', 'Not set')}")
    
    # Initialize agent coordinator
    coordinator = AgentCoordinator()
    
    # Check which provider was selected
    print(f"Selected LLM provider: {coordinator.llm_provider}")
    print(f"LLM initialized: {'Yes' if coordinator.llm else 'No'}")
    
    # Return success based on LLM availability
    return coordinator.llm is not None

if __name__ == "__main__":
    success = test_llm_setup()
    print(f"LLM setup test {'passed' if success else 'failed'}")
    exit(0 if success else 1)
