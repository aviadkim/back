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

### Quick Installation (Recommended)

If you just want to test the application quickly, use our simplified installation script:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/aviadkim/back.git
cd back

# Make the script executable
chmod +x install_basic_deps.sh

# Run the simplified installation script
./install_basic_deps.sh

# Run the application
python vertical_slice_app.py
```

This installs only the core dependencies needed to run the application.

### Full Installation

For a complete development environment:

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

## AWS Deployment

The project includes automatic deployment to AWS Elastic Beanstalk:

1. Push changes to the master branch on GitHub
2. The GitHub Actions workflow will automatically deploy to AWS
3. Check the deployment status in the Actions tab of your GitHub repository

If you need to manually deploy:

```bash
# Install the EB CLI
pip install awsebcli

# Initialize EB (if not already done)
eb init -p docker financial-docs-analyzer

# Deploy
eb deploy
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

## Troubleshooting

### Common Issues

- **"No module named 'flask'"**: Run `pip install flask` or use the `install_basic_deps.sh` script
- **MongoDB Connection Error**: Check if MongoDB is running with `docker ps`
- **Permission Denied for .sh Files**: Run `chmod +x script_name.sh` to make scripts executable
- **Environment Variable Issues**: Make sure your .env file exists and has the correct values

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
