# Migration Guide: Transitioning to Vertical Slice Architecture (v5.0)

This guide provides detailed instructions for transitioning from the previous layered architecture to the new Vertical Slice Architecture introduced in version 5.0.

## Understanding Vertical Slice Architecture

Vertical Slice Architecture organizes code around business features rather than technical layers. Each "slice" contains all the technical elements (API, services, UI) needed to implement a complete business feature.

### Key Benefits

- **Feature isolation**: Changes to one feature don't affect others
- **Easier onboarding**: Developers can understand a complete feature without learning the entire codebase
- **Independent deployment**: Features can be deployed separately
- **Clearer business alignment**: Code structure reflects business capabilities

## Current Architecture vs. Vertical Slice Architecture

### Previous Structure (Layered)
```
/back
├── routes/                  # All HTTP routes
│   ├── document_routes.py
│   ├── langchain_routes.py
│
├── models/                  # Database models
│   ├── document_models.py
│
├── services/                # Business logic
│   └── document_service.py
│
├── utils/                   # Shared utilities
│   └── pdf_processor.py
│
├── app.py                   # Main Flask app
```

### New Structure (Vertical Slice)
```
/back
├── features/                # Feature slices
│   ├── pdf_scanning/        # PDF scanning feature
│   │   ├── index.js         # Routes specific to this feature
│   │   └── service.js       # Business logic specific to this feature
│   ├── document_chat/       # Document chat feature
│   │   ├── index.js         # Routes specific to this feature
│   │   └── service.js       # Business logic specific to this feature
│
├── agent_framework/         # Shared framework
│
├── vertical_slice_app.py    # New main app entry point
```

## Step-by-Step Migration Process

### Phase 1: Setup Parallel Architecture

1. **Create the vertical slice structure**:
   ```bash
   mkdir -p features/pdf_scanning features/document_chat features/table_extraction
   ```

2. **Set up the new main app**:
   Create `vertical_slice_app.py` to load feature modules

3. **Set up tests**:
   ```bash
   mkdir -p tests
   ```

### Phase 2: Migrate Features

For each feature in your application:

1. **Identify the feature scope**:
   - What routes are involved?
   - What services does it use?
   - What models does it access?
   - What UI components are needed?

2. **Create the feature directory**:
   ```bash
   mkdir -p features/feature_name
   ```

3. **Implement the API endpoint module**:
   Create `features/feature_name/index.js` with the routes for this feature

4. **Implement the service module**:
   Create `features/feature_name/service.js` with the business logic

5. **Move related UI components**:
   Organize related UI components in the frontend structure

### Example: Migrating Document Upload Feature

#### 1. Identify Components

From the old structure:
- `/routes/document_routes.py` - Contains upload route
- `/services/document_service.py` - Contains document processing logic
- `/utils/pdf_processor.py` - Contains PDF handling utilities
- Frontend upload component

#### 2. Create Feature Structure

```bash
mkdir -p features/document_upload
touch features/document_upload/index.js
touch features/document_upload/service.js
```

#### 3. Migrate Route Logic

**Old (`/routes/document_routes.py`):**
```python
@app.route('/api/upload', methods=['POST'])
def upload_document():
    file = request.files['file']
    # Process file
    result = document_service.process_document(file)
    return jsonify(result)
```

**New (`features/document_upload/index.js`):**
```javascript
const express = require('express');
const router = express.Router();
const uploadService = require('./service');

router.post('/api/upload', async (req, res) => {
  try {
    const file = req.files.file;
    const result = await uploadService.processDocument(file);
    return res.json(result);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
});

module.exports = router;
```

#### 4. Migrate Service Logic

**Old (`/services/document_service.py`):**
```python
def process_document(file):
    # Process document
    return { 'status': 'success' }
```

**New (`features/document_upload/service.js`):**
```javascript
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

async function processDocument(file) {
  // Save file
  const filename = `${uuidv4()}-${file.name}`;
  const filepath = path.join('uploads', filename);
  await file.mv(filepath);
  
  // Process document
  // ...
  
  return { status: 'success', file: filename };
}

module.exports = {
  processDocument
};
```

#### 5. Register the Feature

In `vertical_slice_app.py`:
```python
# Import features
from features.document_upload import document_upload_bp

# Register feature blueprints
app.register_blueprint(document_upload_bp)
```

### Phase 3: Shared Components

Some components may be shared across features. Handle these carefully:

1. **Identify truly shared components**:
   - Authentication
   - Database connection
   - Common utilities

2. **Create minimal shared directories**:
   ```bash
   mkdir -p shared/utils shared/auth
   ```

3. **Keep shared code minimal**:
   - Only include what is absolutely necessary
   - Consider duplicating code rather than creating complex dependencies
   - Use dependency injection where possible

### Phase 4: Testing the Migration

For each migrated feature:

1. **Write tests**:
   ```bash
   touch tests/test_feature_name.py
   ```

2. **Test in isolation**:
   Ensure the feature works independently

3. **Test integration**:
   Ensure the feature works with the rest of the application

### Phase 5: UI Integration

1. **Create feature-specific components**:
   Organize frontend components around features

2. **Use component composition**:
   Build larger views by composing feature components

3. **Manage shared state carefully**:
   Use context providers or state management libraries

## Advanced Migration Topics

### Handling Database Access

In a pure Vertical Slice Architecture, each feature might have its own data access code. However, for practical reasons, you may want to:

1. **Share database models**:
   Keep models in a shared location but access them from feature-specific code

2. **Use a repository pattern**:
   Implement repositories that features can use for data access

### Managing Dependencies

As you migrate, manage dependencies carefully:

1. **Explicit imports**:
   Import only what's needed from other features or shared code

2. **Avoid circular dependencies**:
   Ensure features don't depend on each other in circular ways

3. **Use dependency injection**:
   Pass dependencies explicitly rather than importing them directly

## Conclusion

Migrating to Vertical Slice Architecture is an incremental process. You don't need to migrate everything at once. Start with one feature, learn from the experience, and gradually migrate others.

The hybrid approach (maintaining both architectures during migration) allows for a smooth transition without disrupting ongoing development.

## Testing the Migration

After migrating a feature, run:

```bash
python -m pytest tests/test_feature_name.py
```

This helps ensure that the migrated feature works correctly.

## Getting Help

If you encounter issues during migration, refer to:

- The official documentation
- The test suite
- Code examples in the `features/` directory
