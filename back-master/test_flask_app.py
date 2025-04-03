try:
    from app import app
    print("✅ Flask application imported successfully")
    
    # Check available routes
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{rule} [{methods}]")
        
except Exception as e:
    print(f"❌ Failed to import Flask application: {e}")
