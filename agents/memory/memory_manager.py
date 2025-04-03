import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

class MemoryManager:
    """Manager for persistent agent memory storage."""
    
    def __init__(self, storage_dir: str = "memory"):
        """Initialize the memory manager.
        
        Args:
            storage_dir: Directory to store memory files
        """
        self.storage_dir = storage_dir
        self.logger = logging.getLogger("memory_manager")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
    
    def get_agent_memory_path(self, agent_name: str) -> str:
        """Get the path to an agent's memory file.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Path to memory file
        """
        return os.path.join(self.storage_dir, f"{agent_name}.json")
    
    def save_global_memory(self, key: str, value: Any) -> bool:
        """Save a value in global memory.
        
        Args:
            key: Memory key
            value: Value to save
            
        Returns:
            True if successful, False otherwise
        """
        global_memory_path = os.path.join(self.storage_dir, "global.json")
        
        try:
            # Load existing memory
            memory = {}
            if os.path.exists(global_memory_path):
                with open(global_memory_path, 'r') as f:
                    memory = json.load(f)
            
            # Update memory
            memory[key] = value
            memory["_last_updated"] = datetime.now().isoformat()
            
            # Save memory
            with open(global_memory_path, 'w') as f:
                json.dump(memory, f)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving global memory: {str(e)}")
            return False
    
    def get_global_memory(self, key: str, default: Any = None) -> Any:
        """Get a value from global memory.
        
        Args:
            key: Memory key
            default: Default value if key not found
            
        Returns:
            Value if found, default otherwise
        """
        global_memory_path = os.path.join(self.storage_dir, "global.json")
        
        try:
            # Check if memory file exists
            if not os.path.exists(global_memory_path):
                return default
                
            # Load memory
            with open(global_memory_path, 'r') as f:
                memory = json.load(f)
                
            # Return value if found
            return memory.get(key, default)
            
        except Exception as e:
            self.logger.error(f"Error getting global memory: {str(e)}")
            return default
    
    def list_all_memories(self) -> Dict[str, Any]:
        """List all stored memories.
        
        Returns:
            Dictionary with agent names as keys and their memories as values
        """
        memories = {}
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json"):
                    agent_name = os.path.splitext(filename)[0]
                    memory_path = os.path.join(self.storage_dir, filename)
                    
                    with open(memory_path, 'r') as f:
                        memory = json.load(f)
                        memories[agent_name] = memory
                        
            return memories
            
        except Exception as e:
            self.logger.error(f"Error listing memories: {str(e)}")
            return {}
