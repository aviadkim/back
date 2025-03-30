# Financial Document Analysis System - v5.0

## Overview

This system provides advanced analysis of financial documents using a Vertical Slice Architecture. It can process various document types (PDF, Excel, CSV), extract tables, and allow natural language interaction with document content.

## Key Features

- **Document Scanning**: Upload and process financial documents
- **Chat Interface**: Interact with documents using natural language
- **Table Extraction**: View, manipulate, and export table data
- **Vertical Slice Architecture**: Complete feature isolation for easier development

## Architecture

This project implements a **Vertical Slice Architecture**, which organizes code around business features rather than technical layers. Each feature contains all the necessary components (API, services, UI) for a complete functionality slice.

### Project Structure

```
/
├── features/                   # Feature slices
│   ├── pdf_scanning/          # PDF scanning feature
│   │   ├── index.js           # Feature routes
│   │   └── service.js         # Business logic
│   ├── document_chat/         # Document chat feature
│   │   ├── index.js           # Feature routes
│   │   └── service.js         # Business logic
│   └── table_extraction/      # Table extraction feature
│       ├── index.js           # Feature routes
│       └── service.js         # Business logic
│
├── agent_framework/           # AI agent system
│   ├── coordinator.py        # Agent orchestration
│   └── __init__.py           # Framework initialization
│
├── frontend/                  # Frontend React app
│   ├── build/                # Production build
│   └── src/                  # Source code
│       ├── components/       # React components
│       ├── App.jsx           # Main app component
│       ├── index.js          # Entry point
│       └── tailwind.css      # Styles
│
├── uploads/                   # Document storage
├── logs/                      # Application logs
├── tests/                     # Test suite
│   └── test_app.py           # Application tests
│
├── vertical_slice_app.py      # Main application
├── start.sh                   # Start script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── docker-compose.yml         # Docker configuration
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+ (for frontend development)
- Docker (recommended for MongoDB)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aviadkim/back.git
   cd back
   ```

2. Run the start script:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

This will:
- Create necessary directories
- Set up a Python virtual environment
- Install dependencies
- Create a default .env file
- Start MongoDB if Docker is available
- Launch the application

### Manual Setup

If you prefer to set up manually:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create .env file with your settings:
   ```
   FLASK_ENV=development
   PORT=5001
   HUGGINGFACE_API_KEY=your_key_here
   MONGO_URI=mongodb://localhost:27017/financial_documents
   SECRET_KEY=your_secret_key
   JWT_SECRET=your_jwt_secret
   DEFAULT_LANGUAGE=he
   DEFAULT_MODEL=gemini
   ```

4. Start MongoDB:
   ```bash
   docker-compose up -d mongodb
   ```

5. Run the application:
   ```bash
   python vertical_slice_app.py
   ```

## Development Guide

### Adding a New Feature

To add a new feature following the Vertical Slice Architecture:

1. Create a new directory in `features/`:
   ```bash
   mkdir -p features/new_feature_name
   ```

2. Create the core files:
   - `index.js` - API routes
   - `service.js` - Business logic

3. Register the feature in `vertical_slice_app.py`:
   ```python
   # Import the new feature
   from features.new_feature_name import new_feature_bp
   
   # Register the blueprint
   app.register_blueprint(new_feature_bp)
   ```

4. Create corresponding UI components in `frontend/src/components/`

### Testing

Run the test suite with:
```bash
python -m pytest tests/
```

Add new tests for your features in the `tests/` directory.

## API Documentation

### Document Upload

- **POST /api/upload**
  - Upload a document for analysis
  - Form parameters:
    - `file`: The document file
    - `language`: Document language (default: 'he')

### Document Retrieval

- **GET /api/documents**
  - Get list of all documents
  
- **GET /api/documents/:document_id**
  - Get details for a specific document

### Document Chat

- **POST /api/chat/sessions**
  - Create a new chat session
  - JSON body:
    - `userId`: User identifier
    - `documents`: Array of document IDs

- **GET /api/chat/sessions/:sessionId/history**
  - Get chat history for a session
  
- **POST /api/chat/sessions/:sessionId/messages**
  - Send a message in a chat session
  - JSON body:
    - `message`: The message text

- **GET /api/chat/documents/:documentId/suggestions**
  - Get suggested questions for a document

### Table Extraction

- **GET /api/tables/document/:documentId**
  - Get tables from a document
  
- **POST /api/tables/generate**
  - Generate a specialized table view
  
- **POST /api/tables/export**
  - Export table data in various formats
  
- **GET /api/tables/:tableId**
  - Get a specific table by ID

## Migrating from Previous Versions

Version 5.0 introduces a complete Vertical Slice Architecture. If you're upgrading from a previous version:

1. The old layered architecture files remain in place for backward compatibility
2. New features should follow the vertical slice pattern in the `features/` directory
3. Gradually migrate existing functionality to the new architecture

### Migration Steps

1. Identify a feature to migrate
2. Create a new feature slice in `features/`
3. Move the relevant code from routes, services, and models
4. Update the UI components
5. Test thoroughly before replacing the old implementation

## Technology Stack

- **Backend**:
  - Flask (Python)
  - MongoDB
  - HuggingFace/Mistral/OpenAI APIs

- **Frontend**:
  - React
  - Tailwind CSS

- **Infrastructure**:
  - Docker
  - Python virtual environment

## Maintenance and Troubleshooting

### Common Issues

- **MongoDB Connection Error**:
  - Check if MongoDB is running: `docker ps`
  - Verify connection string in .env: `MONGO_URI`
  
- **API Key Issues**:
  - Ensure all required API keys are set in .env
  - For development, dummy keys can be used in some cases

- **File Upload Problems**:
  - Check permissions on `uploads/` directory
  - Verify file size limits in the code

### Logs

Application logs are stored in the `logs/` directory. Check these for detailed error information.

## Future Development

The application follows a phased development approach:

1. **Phase 1** (Current): Core infrastructure with Vertical Slice Architecture
2. **Phase 2**: Enhanced AI capabilities and user management
3. **Phase 3**: Advanced analytics and reporting
4. **Phase 4**: Enterprise features (multi-tenant, advanced security)

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Create a new feature branch from master
2. Follow the Vertical Slice Architecture pattern
3. Add tests for your changes
4. Update documentation as needed
5. Submit a pull request

## License

This project is proprietary and confidential.

## Contact

For questions or support, contact: aviad@kimfo-fs.com
