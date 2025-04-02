#!/bin/bash
# Script to validate the vertical slice architecture migration

echo "===== Validating Vertical Slice Architecture ====="

# Function to check if a feature is properly structured
check_feature() {
    local feature=$1
    local feature_dir="/workspaces/back/project_organized/features/$feature"
    
    echo "Checking feature: $feature"
    
    # Check required files
    if [ ! -f "$feature_dir/__init__.py" ]; then
        echo "❌ Missing __init__.py"
    else
        echo "✅ __init__.py exists"
    fi
    
    if [ ! -f "$feature_dir/api.py" ]; then
        echo "❌ Missing api.py"
    else
        echo "✅ api.py exists"
    fi
    
    if [ ! -f "$feature_dir/service.py" ]; then
        echo "❌ Missing service.py"
    else
        echo "✅ service.py exists"
    fi
    
    # Check if tests directory exists
    if [ ! -d "$feature_dir/tests" ]; then
        echo "❌ Missing tests directory"
    else
        echo "✅ tests directory exists"
        
        # Check if there are any test files
        test_files=$(find "$feature_dir/tests" -name "test_*.py" | wc -l)
        if [ "$test_files" -eq 0 ]; then
            echo "❌ No test files found"
        else
            echo "✅ Has $test_files test files"
        fi
    fi
    
    echo ""
}

# Check main features
for feature in pdf_processing document_upload financial_analysis document_qa document_export; do
    check_feature $feature
done

# Check if app.py is using the feature registry
if grep -q "registry.register_all_with_app" "/workspaces/back/project_organized/app.py"; then
    echo "✅ app.py is using the feature registry"
else
    echo "❌ app.py is not using the feature registry"
fi

echo -e "\n✅ Validation complete!"
echo "Fix any issues highlighted above to complete the migration."
