#!/bin/bash

echo "===== AI Model Benchmarking for Document Q&A ====="

# Create a test directory if it doesn't exist
mkdir -p /workspaces/back/benchmark_results

# Function to test a specific model
test_model() {
    local model_name=$1
    local api_key_var=$2
    local test_output="/workspaces/back/benchmark_results/${model_name}_results.txt"
    
    echo "Testing model: $model_name"
    echo "Results will be saved to $test_output"
    
    # Update .env file to use the specified model
    sed -i "s/DEFAULT_MODEL=.*/DEFAULT_MODEL=$model_name/" /workspaces/back/.env
    
    # Restart the application with the new model
    cd /workspaces/back
    pkill -f "python app.py" || true
    sleep 2
    
    # Start the application
    cd /workspaces/back/project_organized
    python app.py &
    APP_PID=$!
    
    # Wait for the application to start
    echo "Waiting for application to start..."
    sleep 5
    
    # Run the test with timing
    echo "Running document Q&A test..."
    {
        echo "===== $model_name Model Test Results ====="
        echo "Date: $(date)"
        echo ""
        
        time python /workspaces/back/test_document_qa_with_pdf.py
    } 2>&1 | tee "$test_output"
    
    # Stop the application
    kill $APP_PID
    sleep 2
}

# Function to enable API key for a model
enable_key() {
    local model=$1
    local key_var=$2
    local key_value=$3
    
    case $model in
        fallback)
            # No key needed for fallback mode
            ;;
        openrouter)
            # Enable OpenRouter key
            sed -i "s/^OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
            ;;
        gemini)
            # Enable Gemini key
            sed -i "s/^GEMINI_API_KEY=.*/GEMINI_API_KEY=$key_value/" /workspaces/back/.env
            ;;
        huggingface)
            # Enable Hugging Face key
            sed -i "s/^HUGGINGFACE_API_KEY=.*/HUGGINGFACE_API_KEY=$key_value/" /workspaces/back/.env
            ;;
    esac
}

# First, run test with fallback mode (no API keys needed)
test_model "fallback" ""

# Test with OpenRouter
# This is already working from our previous tests
test_model "openrouter" "OPENROUTER_API_KEY"

# Summarize results
echo -e "\n===== Benchmark Summary ====="
echo "Results saved to the benchmark_results directory"
echo "You can compare the performance of different models by examining the results files."
echo ""
echo "To test with additional models like Gemini or Hugging Face,"
echo "add valid API keys to your .env file and modify this script."
