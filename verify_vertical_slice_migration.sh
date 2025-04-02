#!/bin/bash

echo "===== Vertical Slice Architecture Final Verification ====="

# 1. Check that all core feature directories exist and have required files
echo "Checking feature directory structure..."
FEATURE_DIRS=("document_upload" "pdf_processing" "financial_analysis" "document_qa" "document_export")
REQUIRED_FILES=("__init__.py" "api.py" "service.py")

missing_files=0
for feature in "${FEATURE_DIRS[@]}"; do
    feature_dir="/workspaces/back/project_organized/features/$feature"
    
    if [ ! -d "$feature_dir" ]; then
        echo "❌ Missing feature directory: $feature"
        missing_files=$((missing_files + 1))
        continue
    fi
    
    echo "✓ Found feature directory: $feature"
    
    for required in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$feature_dir/$required" ]; then
            echo "  ❌ Missing required file: $feature/$required"
            missing_files=$((missing_files + 1))
        else
            echo "  ✓ Found required file: $feature/$required"
        fi
    done
    
    # Check for tests directory
    if [ ! -d "$feature_dir/tests" ]; then
        echo "  ⚠️ Warning: No tests directory for feature: $feature"
    elif [ ! -f "$feature_dir/tests/__init__.py" ]; then
        echo "  ⚠️ Warning: Missing __init__.py in tests directory: $feature/tests"
    fi
    
    echo ""
done

# 2. Check that shared services are set up correctly
echo "Checking shared services..."
SHARED_DIRS=("ai" "database" "file_storage" "models" "utils" "pdf")

for shared in "${SHARED_DIRS[@]}"; do
    if [ ! -d "/workspaces/back/project_organized/shared/$shared" ]; then
        echo "❌ Missing shared service directory: $shared"
        missing_files=$((missing_files + 1))
    elif [ ! -f "/workspaces/back/project_organized/shared/$shared/__init__.py" ]; then
        echo "❌ Missing __init__.py in shared service: $shared"
        missing_files=$((missing_files + 1))
    else
        echo "✓ Found shared service: $shared"
    fi
done

echo ""

# 3. Check that the app entry point exists and has feature registration
echo "Checking main application entry point..."
APP_FILE="/workspaces/back/project_organized/app.py"

if [ ! -f "$APP_FILE" ]; then
    echo "❌ Missing main application entry point: app.py"
    missing_files=$((missing_files + 1))
else
    echo "✓ Found main application entry point: app.py"
    
    # Check if app.py contains feature registration
    if grep -q "register_routes" "$APP_FILE"; then
        echo "✓ app.py includes feature registration"
    else
        echo "⚠️ Warning: app.py might be missing feature registration"
    fi
fi

echo ""

# 4. Check for adapter files to ensure backward compatibility
echo "Checking adapter files for backward compatibility..."
ADAPTER_SOURCE_FILES=("enhanced_pdf_processor.py" "financial_data_extractor.py" "enhanced_financial_extractor.py" 
                     "excel_exporter.py" "simple_qa.py" "financial_document_qa.py")

missing_adapters=0
for adapter in "${ADAPTER_SOURCE_FILES[@]}"; do
    source_file="/workspaces/back/$adapter"
    if [ ! -f "$source_file" ]; then
        echo "⚠️ Warning: Source file for adapter not found: $adapter"
        continue
    fi
    
    # Check if it contains adapter code
    if grep -q "This redirects to the new vertical slice architecture" "$source_file"; then
        echo "✓ Found adapter: $adapter"
    else
        echo "❌ Missing adapter code in file: $adapter"
        missing_adapters=$((missing_adapters + 1))
    fi
done

echo ""

# 5. Check for the start script
echo "Checking for start script..."
if [ ! -f "/workspaces/back/project_organized/start_full_app.sh" ]; then
    echo "❌ Missing start script: start_full_app.sh"
    missing_files=$((missing_files + 1))
else
    echo "✓ Found start script: start_full_app.sh"
    
    # Check if it's executable
    if [ ! -x "/workspaces/back/project_organized/start_full_app.sh" ]; then
        echo "⚠️ Warning: start_full_app.sh is not executable"
    fi
fi

echo ""

# 6. Check dependency container
echo "Checking for dependency container..."
if [ ! -f "/workspaces/back/project_organized/dependency_container.py" ]; then
    echo "❌ Missing dependency container: dependency_container.py"
    missing_files=$((missing_files + 1))
else
    echo "✓ Found dependency container: dependency_container.py"
fi

echo ""

# 7. Check migration status
echo "Checking migration status document..."
if [ ! -f "/workspaces/back/project_organized/MIGRATION_STATUS.md" ]; then
    echo "⚠️ Warning: Missing migration status document: MIGRATION_STATUS.md"
else
    echo "✓ Found migration status document: MIGRATION_STATUS.md"
fi

echo ""

# 8. Summary
echo "===== Migration Verification Summary ====="
if [ $missing_files -eq 0 ] && [ $missing_adapters -eq 0 ]; then
    echo "✅ All essential vertical slice architecture components are present!"
    
    # Create a final migration completion marker
    touch "/workspaces/back/project_organized/.migration_complete"
    echo "Migration completion marker created: .migration_complete"
    echo ""
    echo "You can now run the application with the vertical slice architecture:"
    echo "  cd /workspaces/back/project_organized && ./start_full_app.sh"
else
    echo "⚠️ Found $missing_files missing essential files and $missing_adapters missing adapters."
    echo ""
    echo "To complete the migration:"
    echo "  1. Run: ./complete_migration.sh"
    echo "  2. Run: ./create_adapters.sh"
    echo "  3. Run this verification again"
fi

echo ""
echo "===== Verification Complete ====="
