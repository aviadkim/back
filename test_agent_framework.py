try:
    from agent_framework.coordinator import Coordinator
    print("✅ Agent framework coordinator imported successfully")
    
    # Try to initialize a coordinator
    coordinator = Coordinator()
    print("✅ Coordinator initialized successfully")
    
    # Check if memory agent is available
    try:
        from agent_framework.memory_agent import MemoryAgent
        print("✅ Memory agent imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import memory agent: {e}")
        
except ImportError as e:
    print(f"❌ Failed to import agent framework: {e}")
