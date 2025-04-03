# Architecture Migration Plan

## Current Issues
- Duplicated functionality across directories
- Inconsistent organization (mix of feature-based, function-based, domain-based)
- Empty or unused directories
- Large `node_modules` directory in repository

## Target Architecture
We'll move toward a Vertical Slice Architecture:
```
back/
├── app.py                # Main Flask application entry point
├── shared/               # Common utilities and cross-cutting concerns 
├── features/             # All business features as vertical slices
│   ├── document_upload/  # Each feature has its own API, service, models, tests
│   ├── pdf_processing/   
│   ├── financial_analysis/
│   └── etc/
├── config/               # Configuration files
└── tests/                # Integration and system tests
```

## Migration Strategy (No File Deletion)

### Phase 1: Initial Setup
1. Create the basic structure in `project_organized/` (already started)
2. Create symlinks from old locations to new locations for critical files
3. Gradually refactor components into the new structure

### Phase 2: Component Migration
For each component:
1. Move code to new location (copy, don't delete)
2. Update imports in the new location
3. Create adapter in old location that imports from new location
4. Update tests to use new location

### Phase 3: Clean-Up (Future)
Once all functionality is migrated and tested:
1. Update `.gitignore` to exclude generated directories
2. Remove adapter code
3. Eventually archive old structure

## Immediate Actions

1. **Update `.gitignore`** to exclude generated files and directories
2. **Create adapter pattern** to allow gradual migration
3. **Start with shared utilities** by consolidating into `shared/` directory
4. **Identify core features** and organize them in `features/` directory

## Long-Term Actions

1. **Complete migration** of all components to new structure
2. **Improve test organization** for better coverage and maintainability
3. **Add API documentation** using OpenAPI/Swagger
4. **Implement dependency injection** pattern for better modularity
```

## Example Migration for a Component

**Original File**: `/workspaces/back/routes/document.py`
**New Location**: `/workspaces/back/features/document_upload/api.py`

1. Copy content to new location with improvements
2. Create adapter in original location:
```python
# /workspaces/back/routes/document.py
# This file is now an adapter to the new architecture
# Please use features/document_upload/api.py instead
from features.document_upload.api import *
```
```
