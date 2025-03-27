"""
Agent Framework for Financial Document Analysis

This package contains the AI agent framework for analyzing and
interacting with financial documents through chat and data extraction.

Components:
- Memory Agent: Manages document storage and retrieval
- Coordinator: Coordinates AI operations and API calls 
"""

from .memory_agent import MemoryAgent
from .coordinator import AgentCoordinator

__all__ = ["MemoryAgent", "AgentCoordinator"]
