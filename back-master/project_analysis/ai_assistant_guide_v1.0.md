# AI Assistant Project Guide
This document provides comprehensive information about the project to help AI assistants (like Claude) provide better assistance.

## Project Context
- **Project Type**: C, C++, JavaScript, Python-based application
- **Frameworks**: Angular, Express, FastAPI, React, Spring, Vue.js
- **Project Size**: 522 files in 67 directories

## Project Structure
Key directories and their purposes:

- **frontend/src/** - Contains 6 files/directories
- **frontend/src/services/** - Contains 2 files/directories
- **frontend/src/services/financial/** - Contains 1 files/directories
- **frontend/src/components/** - Contains 5 files/directories
- **frontend/src/hooks/** - Contains 1 files/directories
- **api/** - Contains 7 files/directories
- **api/routes/** - Contains 1 files/directories
- **models/** - Contains 4 files/directories
- **utils/** - Contains 3 files/directories
- **project_analysis/** - Contains 2 files/directories
- **agents/** - Contains 3 files/directories
- **frontend/** - Contains 6 files/directories
- **scripts/** - Contains 11 files/directories
- **pdf_processor/** - Contains 5 files/directories
- **test_documents/** - Contains 2 files/directories

## Key Files
- **api/main.py** - 213 lines
- **app.log** - 0 lines
- **frontend/package.json** - 47 lines
- **frontend/public/index.html** - 24 lines
- **frontend/src/App.js** - 611 lines
- **frontend/src/index.js** - 16 lines
- **frontend/src/rtlConfig.js** - 17 lines
- **requirements.txt** - 21 lines
- **run_app.py** - 69 lines
- **test_documents/poppler-23.11.0/poppler-23.11.0/Library/include/poppler/poppler-config.h** - 0 lines
- **utils/init_app.py** - 64 lines

## Development Priorities
Based on analysis, these areas need attention:

- Increase test coverage for backend code - The ratio of test files to backend files is low
- Consider refactoring dev_workflow.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring project_analyzer.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring project_builder.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring api/routes.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring project_analysis/project_report.md into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring agents/memory/memory_manager.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring agents/financial/financial_agent.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring frontend/package-lock.json into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring frontend/src/App.js into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring frontend/src/services/api.js into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring frontend/src/components/PdfViewer.js into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring frontend/src/components/DocumentTable.js into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring frontend/src/components/SmartPdfBot.js into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring frontend/src/components/SmartTemplateBuilder.js into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring scripts/pdf_mupdf_reader.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring scripts/test_document.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring scripts/setup.js into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring scripts/process_document.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring scripts/benchmark.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring pdf_processor/analysis/financial_analyzer.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring pdf_processor/tables/table_extractor.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring pdf_processor/extraction/text_extractor.py into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring models/ocr_results_page_10.json into smaller modules - File has high complexity which could lead to maintenance challenges
- Consider refactoring models/ocr_results_page_9.json into smaller modules - File has high complexity which could lead to maintenance challenges

## Next Development Steps

### Features to Implement
- Implement authentication with JWT - Add secure JWT authentication to protect API endpoints
- Implement state management - Add Redux or React Context for better state management

## How to Assist with this Project
As an AI assistant, you can help with the following:

1. **Code Implementation** - Write or improve code based on the recommendations
2. **Refactoring Help** - Provide solutions for complex files
3. **Architecture Advice** - Suggest improvements to project structure
4. **Feature Planning** - Help break down feature implementations into manageable steps
5. **Bug Fixing** - Help identify and fix issues in the codebase
6. **Documentation** - Assist in writing documentation for code and APIs
7. **Test Creation** - Help write unit and integration tests

### Common Request Templates
When working with the developer, these request formats will be most helpful:

```
1. "Please implement [feature name] described in the report"
2. "Help me refactor [file path] to reduce complexity"
3. "Suggest a proper directory structure for this project"
4. "Write documentation for [component/feature]"
5. "Review this code: [paste code]"
6. "Write tests for [feature/component]"
7. "Fix the failing test in [test file]"
```