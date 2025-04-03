# Vertical Slice Architecture Implementation

This is a reorganization of the existing codebase following vertical slice architecture principles.

## Structure

- `features/`: Contains business features as vertical slices
  - `pdf_processing/`: PDF text extraction
  - `financial_analysis/`: Financial data extraction
  - `document_upload/`: Document management
  - `document_qa/`: Question answering
  - `portfolio_analysis/`: Portfolio analysis
- `shared/`: Shared code used across features
- `config/`: Configuration files
- `tests/`: System-wide tests

## Migration Path

1. Copy files to new structure without deleting originals
2. Create adapters in old locations pointing to new code
3. Update app.py to use the new structure
4. Run tests to verify functionality
