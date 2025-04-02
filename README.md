# Financial Document Processor

A system for processing financial documents with AI-powered document Q&A capabilities.

## API Keys and Environment Variables

This project requires an OpenRouter API key for AI functionality.

### For Development

1. Run the setup script:
   ```bash
   ./setup_env.sh
   ```
   This will create a `.env` file from the template and prompt for your API key.

2. If you already have a key, you can manually create a `.env` file:
   ```bash
   cp .env.example .env
   # Then edit .env and add your API key
   ```

### Before Pushing to GitHub

Always run the preparation script before pushing to GitHub:
```bash
./prepare_for_github.sh
```

This will:
- Make sure `.env` is in `.gitignore`
- Create a safe `.env.example` file without actual API keys
- Backup your current `.env` file with API keys to `.env.local`
- Check for accidentally exposed API keys in the code

## Running Tests

Test the Q&A functionality with:
```bash
./run_with_real_pdf.sh
```

For comprehensive testing:
```bash
./run_comprehensive_test.sh
```

## Benchmark Different Models

Compare performance of different models:
```bash
./benchmark_models.sh
```
