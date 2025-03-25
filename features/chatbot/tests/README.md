# Chatbot Feature Tests

This directory contains tests for the chatbot feature of the financial document analysis system. These tests verify the functionality of the chatbot components and their integration with the agent framework.

## Test Files

- `test_huggingface_connection.py` - Tests the connection to the Hugging Face API
- `test_chatbot_capabilities.py` - Tests the core capabilities of the chatbot
- `test_chatbot_api.py` - Tests the HTTP API endpoints
- `run_all_tests.py` - Script to run all tests in sequence

## Running the Tests

### Prerequisites

Make sure you have set up your environment:

1. Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set the Hugging Face API key in your environment:
   - For local testing, add it to your `.env` file:
     ```
     HUGGINGFACE_API_KEY=your_api_key_here
     ```
   - For GitHub Codespaces, add it to your GitHub secrets
   - For Render, add it to your environment variables

### Running Individual Tests

You can run each test file separately:

```bash
# Test Hugging Face API connection
python -m features.chatbot.tests.test_huggingface_connection

# Test chatbot capabilities
python -m features.chatbot.tests.test_chatbot_capabilities

# Test chatbot API endpoints
python -m pytest features/chatbot/tests/test_chatbot_api.py -v
```

### Running All Tests

To run all tests in sequence:

```bash
python -m features.chatbot.tests.run_all_tests
```

This will execute all test files and provide a summary of the results.

## Test Descriptions

### Hugging Face API Connection Test

This test verifies that:
1. The Hugging Face API key is properly configured
2. The system can connect to the Hugging Face API
3. Embeddings can be generated successfully

### Chatbot Capabilities Test

This test demonstrates the core capabilities of the chatbot:
1. Session creation and management
2. Memory agent functionality
3. Document reference tracking
4. Message history management
5. Query processing with the agent framework
6. Suggested questions generation

### Chatbot API Tests

These tests verify the HTTP API endpoints:
1. Session creation endpoint
2. Query processing endpoint
3. Session history retrieval endpoint
4. Session clearing endpoint

## Troubleshooting

If you encounter issues with the tests:

1. **API Key Issues**:
   - Verify that your Hugging Face API key is correctly set
   - Check that the key has the necessary permissions
   - Try generating a new API key if needed

2. **Import Errors**:
   - Make sure all dependencies are installed:
     ```bash
     pip install langchain-huggingface
     ```

3. **Connection Issues**:
   - Check your internet connection
   - Verify that firewalls aren't blocking the API requests

4. **Model Access Issues**:
   - Ensure your Hugging Face account has access to the required models
   - Some models might require acceptance of terms of use or have usage limitations

For more detailed error information, check the log files in the `logs/` directory.
