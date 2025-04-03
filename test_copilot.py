try:
    import importlib.util
    
    # Check if copilot router exists
    router_spec = importlib.util.find_spec('features.copilot_router.services.router_service')
    if router_spec is not None:
        print("✅ Copilot router service module found")
    else:
        print("❌ Copilot router service module not found")
    
    # Check if plan files exist
    import os
    if os.path.exists('features/copilot/PLAN.md'):
        print("✅ Copilot plan file exists")
        with open('features/copilot/PLAN.md', 'r') as f:
            plan_content = f.read()
            print(f"Plan file length: {len(plan_content)} characters")
    else:
        print("❌ Copilot plan file doesn't exist")
        
except Exception as e:
    print(f"❌ Error testing copilot integration: {e}")
