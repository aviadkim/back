#!/bin/bash
# Enhanced script for batch migration of components

# Create base directories if they don't exist
mkdir -p project_organized/features/agents
mkdir -p project_organized/features/auth
mkdir -p project_organized/features/document_export
mkdir -p project_organized/shared/utils
mkdir -p project_organized/shared/models
mkdir -p project_organized/shared/database

# Function to migrate a component
migrate_component() {
    local SOURCE=$1
    local TARGET_DIR=$2
    local TARGET_FILE=${3:-$(basename $SOURCE)}
    
    # Skip if source doesn't exist
    if [ ! -f "$SOURCE" ]; then
        echo "⚠️  Source file not found: $SOURCE"
        return
    fi
    
    # Create target directory
    mkdir -p "$(dirname "$TARGET_DIR/$TARGET_FILE")"
    
    # Copy the file
    cp "$SOURCE" "$TARGET_DIR/$TARGET_FILE"
    echo "✅ Migrated $SOURCE to $TARGET_DIR/$TARGET_FILE"
}

# Migrate PDF processing components
echo "===== Migrating PDF processing components ====="
migrate_component "ocr_text_extractor.py" "project_organized/features/pdf_processing" "ocr.py"
migrate_component "simple_pdf_extractor.py" "project_organized/features/pdf_processing" "simple_extractor.py"

# Migrate Financial Analysis components
echo "===== Migrating Financial Analysis components ====="
migrate_component "financial_data_extractor.py" "project_organized/features/financial_analysis/extractors" 
migrate_component "enhanced_financial_extractor.py" "project_organized/features/financial_analysis/extractors"
migrate_component "advanced_financial_extractor.py" "project_organized/features/financial_analysis/extractors"
migrate_component "financial_document_processor.py" "project_organized/features/financial_analysis"

# Migrate Document QA components
echo "===== Migrating Document QA components ====="
migrate_component "simple_qa.py" "project_organized/features/document_qa"
migrate_component "financial_document_qa.py" "project_organized/features/document_qa"

# Migrate Excel export functionality
echo "===== Migrating Document Export components ====="
migrate_component "excel_exporter.py" "project_organized/features/document_export"

# Migrate utility files
echo "===== Migrating Utility components ====="
migrate_component "utils/pdf_processor.py" "project_organized/shared/pdf"
migrate_component "utils/aws_helpers.py" "project_organized/shared/utils"
migrate_component "utils/logger.py" "project_organized/shared/utils"

# Migrate models
echo "===== Migrating Models ====="
migrate_component "models/document_models.py" "project_organized/shared/models"
migrate_component "models/table_model.py" "project_organized/shared/models"

# Create __init__.py files
find project_organized -type d | while read dir; do
    if [ ! -f "$dir/__init__.py" ]; then
        echo "\"\"\"$(basename "$dir") module\"\"\"" > "$dir/__init__.py"
        echo "Created $dir/__init__.py"
    fi
done

echo "===== Migration Complete ====="
echo "Run test_new_architecture.sh to verify the migration"
