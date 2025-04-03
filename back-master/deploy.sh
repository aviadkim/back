#!/bin/bash
# ===========================================================================
# Financial Document Processor - Unified Deployment Script
# ===========================================================================
# This script handles deployment for different environments (dev, staging, prod)
# Usage: ./deploy.sh [environment] [options]
#
# Examples:
#   ./deploy.sh dev          # Deploy to development environment
#   ./deploy.sh staging      # Deploy to staging environment
#   ./deploy.sh prod         # Deploy to production environment
#   ./deploy.sh dev --skip-tests  # Skip tests during deployment
#   ./deploy.sh prod --force # Force deployment even if tests fail
# ===========================================================================

set -e  # Exit on error

# Default values
ENVIRONMENT="dev"
SKIP_TESTS=false
FORCE_DEPLOY=false
AWS_PROFILE="default"
DOCKER_BUILD=true
MONGODB_SETUP=true

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    dev|staging|prod)
      ENVIRONMENT="$1"
      shift
      ;;
    --skip-tests)
      SKIP_TESTS=true
      shift
      ;;
    --force)
      FORCE_DEPLOY=true
      shift
      ;;
    --aws-profile=*)
      AWS_PROFILE="${1#*=}"
      shift
      ;;
    --no-docker)
      DOCKER_BUILD=false
      shift
      ;;
    --no-mongodb)
      MONGODB_SETUP=false
      shift
      ;;
    --help)
      echo "Usage: ./deploy.sh [environment] [options]"
      echo "Environments: dev, staging, prod"
      echo "Options:"
      echo "  --skip-tests        Skip running tests"
      echo "  --force             Force deployment even if tests fail"
      echo "  --aws-profile=NAME  Use specific AWS profile"
      echo "  --no-docker         Skip Docker build"
      echo "  --no-mongodb        Skip MongoDB setup"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Configuration based on environment
case $ENVIRONMENT in
  dev)
    ENV_FILE=".env.development"
    AWS_S3_BUCKET="financial-docs-dev"
    AWS_REGION="us-east-1"
    MONGODB_URI="mongodb://localhost:27017/financial_documents_dev"
    SERVICE_NAME="financial-docs-dev"
    ;;
  staging)
    ENV_FILE=".env.staging"
    AWS_S3_BUCKET="financial-docs-staging"
    AWS_REGION="us-east-1"
    MONGODB_URI="mongodb://mongodb:27017/financial_documents_staging"
    SERVICE_NAME="financial-docs-staging"
    ;;
  prod)
    ENV_FILE=".env.production"
    AWS_S3_BUCKET="financial-docs-prod"
    AWS_REGION="us-east-1"
    MONGODB_URI="mongodb://mongodb:27017/financial_documents_prod"
    SERVICE_NAME="financial-docs-prod"
    ;;
  *)
    echo -e "${RED}Invalid environment: $ENVIRONMENT${NC}"
    echo "Valid environments: dev, staging, prod"
    exit 1
    ;;
esac

# Display header
echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}Financial Document Processor - Deployment Script${NC}"
echo -e "${BLUE}=========================================================${NC}"
echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
echo -e "AWS Profile: ${GREEN}$AWS_PROFILE${NC}"
echo -e "Docker Build: ${GREEN}$DOCKER_BUILD${NC}"
echo -e "MongoDB Setup: ${GREEN}$MONGODB_SETUP${NC}"
echo -e "${BLUE}=========================================================${NC}"
echo ""

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Warning: $ENV_FILE not found. Using .env file.${NC}"
    ENV_FILE=".env"

    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}Warning: .env not found. Creating from .env.example${NC}"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            ENV_FILE=".env"
        else
            echo -e "${RED}Error: No environment file found!${NC}"
            exit 1
        fi
    fi
fi

echo -e "Using environment file: ${GREEN}$ENV_FILE${NC}"
echo ""

# Step 1: Install dependencies
echo -e "${BLUE}Step 1: Installing dependencies...${NC}"
pip install -r requirements.txt
npm install --prefix frontend
echo -e "${GREEN}Dependencies installed successfully!${NC}"
echo ""

# Step 2: Run tests (unless skipped)
if [ "$SKIP_TESTS" = false ]; then
    echo -e "${BLUE}Step 2: Running tests...${NC}"

    # Run Python backend tests
    echo "Running backend tests..."
    python -m pytest tests/ -v
    BACKEND_TEST_RESULT=$?

    # Run frontend tests
    echo "Running frontend tests..."
    cd frontend && npm test -- --watchAll=false
    FRONTEND_TEST_RESULT=$?
    cd ..

    # Check test results
    if [ $BACKEND_TEST_RESULT -ne 0 ] || [ $FRONTEND_TEST_RESULT -ne 0 ]; then
        echo -e "${RED}Tests failed!${NC}"
        if [ "$FORCE_DEPLOY" = false ]; then
            echo -e "${RED}Deployment aborted. Use --force to deploy anyway.${NC}"
            exit 1
        else
            echo -e "${YELLOW}Proceeding with deployment despite test failures (--force).${NC}"
        fi
    else
        echo -e "${GREEN}All tests passed!${NC}"
    fi
else
    echo -e "${YELLOW}Step 2: Tests skipped (--skip-tests).${NC}"
fi
echo ""

# Step 3: Build frontend
echo -e "${BLUE}Step 3: Building frontend...${NC}"
cd frontend && npm run build && cd ..
echo -e "${GREEN}Frontend built successfully!${NC}"
echo ""

# Step 4: Deploy based on environment
echo -e "${BLUE}Step 4: Deploying application...${NC}"

case $ENVIRONMENT in
  dev)
    echo "Starting development server..."
    # Copy the appropriate .env file
    cp $ENV_FILE .env

    # Start MongoDB container using docker-compose
    echo "Starting MongoDB container..."
    docker-compose -f docker-compose.yml up -d mongodb
    echo "Waiting a few seconds for MongoDB to initialize..."
    sleep 5 # Give MongoDB a moment to start

    # Start the Flask app
    echo "Starting backend server..."
    python app.py &
    BACKEND_PID=$!

    echo "Starting frontend development server..."
    cd frontend && npm start &
    FRONTEND_PID=$!

    echo -e "${GREEN}Development servers started:${NC}"
    echo "  - Backend: http://localhost:5000"
    echo "  - Frontend: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop servers"

    # Wait for both processes
    wait $BACKEND_PID $FRONTEND_PID
    ;;

  staging|prod)
    echo "Deploying to $ENVIRONMENT environment..."

    # Deploy using docker-compose
    echo "Starting docker-compose deployment..."
    cp $ENV_FILE .env

    if [ "$ENVIRONMENT" = "staging" ]; then
        docker-compose -f docker-compose.yml up -d
    else
        docker-compose -f docker-compose.production.yml up -d
    fi

    echo -e "${GREEN}Deployment completed successfully!${NC}"
    ;;
esac

echo ""
echo -e "${BLUE}=========================================================${NC}"
echo -e "${GREEN}Deployment to $ENVIRONMENT environment completed!${NC}"
echo -e "${BLUE}=========================================================${NC}"