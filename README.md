# Financial Document Analysis System

A comprehensive system for analyzing financial documents built with Flask and React using Vertical Slice Architecture.

## Features

* PDF document scanning and text extraction with OCR
* AI-powered document analysis with HuggingFace models
* Chatbot interface for querying document content
* Table extraction and generation from documents
* Secure document storage and management

## Architecture

This project is built using **Vertical Slice Architecture**, which organizes code around business features rather than technical layers. Each feature is a complete vertical "slice" that includes all technical layers required for that feature.

### Key Components

* **Feature-based Organization**: Code is organized by business features (pdf_scanning, chatbot, etc.)
* **AI Agent Framework**: Intelligent agents for document processing and analysis
* **MongoDB Storage**: Document metadata and analysis results
* **React Frontend**: User interface organized by features
* **AWS Deployment**: Cloud deployment using AWS Lightsail

## Getting Started

### Prerequisites

* Python 3.9+
* Node.js 14+
* MongoDB
* Docker (for containerization)
* AWS CLI (for deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/aviadkim/back.git
cd back
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create required directories:
```bash
mkdir -p uploads data/embeddings data/templates logs
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start MongoDB:
```bash
docker-compose up -d mongodb
```

6. Run the application:
```bash
python app.py
```

### Running Tests

```bash
pytest
```

## Deployment to AWS

This project includes scripts and configurations for deploying to AWS Lightsail Containers. For detailed deployment instructions, see [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md).

### Quick Deployment Steps

1. Set up AWS secrets:
```bash
./setup-aws-secrets.sh
```

2. Set up storage for documents:
```bash
./setup-storage-bucket.sh
```

3. Deploy to AWS Lightsail:
```bash
./deploy-to-lightsail.sh
```

### AWS Management Console Access

After deployment, you can access and manage your application through the AWS Management Console:

1. Visit [https://lightsail.aws.amazon.com/ls/webapp/home/containers](https://lightsail.aws.amazon.com/ls/webapp/home/containers)
2. Sign in with your AWS credentials
3. Select your container service (financial-docs)
4. View deployment status, logs, and metrics

Your application will be accessible at the public endpoint URL shown in the AWS Lightsail Console once deployment is complete.

## Project Structure

```
/workspaces/back/
├── features/                      # All business features organized by capability
│   ├── pdf_scanning/              # PDF scanning feature
│   │   ├── api.py                 # API endpoints
│   │   ├── models.py              # Feature-specific models
│   │   ├── services.py            # Business logic
│   │   └── tests/                 # Feature-specific tests
│   ├── chatbot/                   # Chatbot feature
│   └── ...
├── agent_framework/               # AI agent components
│   ├── coordinator.py             # Orchestrates different agents
│   ├── memory_agent.py            # Manages document memory
│   └── ...
├── utils/                         # Shared utilities
│   ├── aws_helpers.py             # AWS integration utilities
│   ├── storage_client.py          # Document storage client
│   └── ...
├── frontend/                      # React frontend
│   ├── src/                       # Source code
│   │   ├── features/              # Feature-organized components
│   │   └── ...
│   └── ...
├── app.py                         # Main Flask application
├── deploy-to-lightsail.sh         # AWS deployment script
├── setup-aws-secrets.sh           # AWS secrets setup script
├── setup-storage-bucket.sh        # AWS storage setup script
├── docker-compose.yml             # Docker configuration
├── Dockerfile                     # Docker container definition
└── lightsail-compose.yml          # AWS Lightsail configuration
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```
# General settings
FLASK_ENV=development
PORT=5000

# API Keys
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
# Optional - only if you're using these services
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database
MONGO_URI=mongodb://localhost:27017/financial_documents

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Language
DEFAULT_LANGUAGE=he

# Storage (AWS)
USE_CLOUD_STORAGE=False  # Set to True to use AWS Lightsail Object Storage
BUCKET_NAME=your-bucket-name
```

## Contributing

1. Create a feature branch for your changes
2. Follow the Vertical Slice Architecture pattern
3. Add tests for your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
