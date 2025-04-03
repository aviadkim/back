import logging
from typing import Dict, List, Any, Optional, Union
import json
import os
import time

class BaseAgent:
    """Base class for all specialized agents."""
    
    def __init__(self, name: str, memory_path: Optional[str] = None):
        """Initialize the agent.
        
        Args:
            name: Name of the agent
            memory_path: Optional path to persist agent memory
        """
        self.name = name
        self.memory = {}
        self.memory_path = memory_path
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Load memory if path is provided and file exists
        if memory_path and os.path.exists(memory_path):
            self._load_memory()
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return a result.
        
        Args:
            task: Task dictionary with instructions
            
        Returns:
            Dictionary containing results
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def store_result(self, key: str, value: Any) -> None:
        """Store a result in agent memory.
        
        Args:
            key: Key to store the value under
            value: Value to store
        """
        self.memory[key] = value
        if self.memory_path:
            self._save_memory()
    
    def get_result(self, key: str, default: Any = None) -> Any:
        """Get a result from agent memory.
        
        Args:
            key: Key to retrieve
            default: Default value if key not found
            
        Returns:
            Value if found, default otherwise
        """
        return self.memory.get(key, default)
    
    def has_memory(self, key: str) -> bool:
        """Check if a key exists in memory.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return key in self.memory
    
    def list_memories(self) -> List[str]:
        """List all keys in memory.
        
        Returns:
            List of memory keys
        """
        return list(self.memory.keys())
    
    def clear_memory(self) -> None:
        """Clear all stored memory."""
        self.memory = {}
        if self.memory_path and os.path.exists(self.memory_path):
            os.remove(self.memory_path)
    
    def _save_memory(self) -> None:
        """Save memory to persistent storage."""
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f)
        except Exception as e:
            self.logger.error(f"Failed to save memory: {str(e)}")
    
    def _load_memory(self) -> None:
        """Load memory from persistent storage."""
        try:
            with open(self.memory_path, 'r') as f:
                self.memory = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load memory: {str(e)}")
