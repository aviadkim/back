# Vertical Slice Architecture Guide for Financial Document Analysis System

This guide explains how to work with the Vertical Slice Architecture pattern implemented in this project and demonstrates how to use it in a Codespace environment.

## What is Vertical Slice Architecture?

Vertical Slice Architecture organizes code around business features rather than technical layers. Each "slice" contains all the components (API endpoints, services, data models) needed to implement a specific feature.

![Vertical vs Traditional Architecture](https://i.imgur.com/JxQIRPH.png)

## Project Structure

Our project is organized according to the Vertical Slice Architecture pattern:

```
/back/
├── features/                      # Vertical feature slices
│   ├── pdf_scanning/              # PDF scanning feature slice
│   │   ├── __init__.py            # Exports the feature's blueprint
│   │   ├── api.py                 # API endpoints
│   │   ├── services.py            # Business logic
│   │   └── tests/                 # Feature-specific tests
│   ├── chatbot/                   # Chatbot feature slice
│       ├── __init__.py            # Exports the feature's blueprint
│       ├── api.py                 # API endpoints
│       ├── services.py            # Business logic
│       ├── models.py              # Data models
│       └── tests/                 # Feature-specific tests
├── agent_framework/               # Shared framework for all features
│   ├── coordinator.py             # Coordinates between agents
│   ├── memory_agent.py            # Manages conversation memory
│   ├── nlp_agent.py               # Processes natural language
│   ├── table_generator.py         # Generates tables from financial data
│   └── embeddings_provider.py     # Manages embedding generation
├── shared/                        # Other shared components
│   ├── database.py                # Database utilities
│   └── utils.py                   # General utilities
├── app.py                         # Main application entry point
└── test_*.py                      # Test scripts for specific components
```

## Working with the Architecture in Codespace

Here's how to work with this architecture in a GitHub Codespace environment:

### 1. Setting Up Your Environment

```bash
# Clone the repository (if not already in Codespace)
git clone https://github.com/aviadkim/back.git
cd back

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (particularly the Hugging Face API key)
echo "HUGGINGFACE_API_KEY=your_api_key_here" > .env
```

### 2. Testing Your API Key

```bash
# Run the enhanced API key test
python test_api_key_fixed.py
```

### 3. Running Component Tests

```bash
# Test the table generator capability
python test_table_generator.py

# Test the chatbot API endpoints
python -m pytest features/chatbot/tests/test_chatbot_api.py -v

# Test the Hugging Face connection
python -m features.chatbot/tests/test_huggingface_connection.py
```

### 4. Running the Full Agent Demonstration

```bash
# Run the comprehensive agent capabilities demonstration
python demonstrate_agents.py
```

## Developing New Features

To develop a new feature following the Vertical Slice Architecture pattern:

1. **Create a new feature directory**:
   ```bash
   mkdir -p features/new_feature_name
   mkdir -p features/new_feature_name/tests
   ```

2. **Create the basic files**:
   ```bash
   touch features/new_feature_name/__init__.py
   touch features/new_feature_name/api.py
   touch features/new_feature_name/services.py
   touch features/new_feature_name/tests/__init__.py
   ```

3. **Implement the feature components**:
   - `__init__.py`: Export the feature's blueprint
   - `api.py`: Define API endpoints
   - `services.py`: Implement business logic
   - Add tests in the `tests/` directory

4. **Register the blueprint in app.py**:
   ```python
   from features.new_feature_name import new_feature_blueprint
   app.register_blueprint(new_feature_blueprint)
   ```

## Best Practices for Vertical Slice Architecture

1. **Feature Independence**: Each feature should be as independent as possible, with minimal dependencies on other features.

2. **Shared Code**: Use the `agent_framework/` or `shared/` directories for code that needs to be reused across features.

3. **Testing by Feature**: Test each feature as a complete unit, from API to database.

4. **Feature Evolution**: When a feature grows too large, consider breaking it down into multiple related features.

5. **Consistent Structure**: Maintain a consistent structure across all feature slices for easier navigation and maintenance.

## Understanding the Agent Framework

The agent framework provides core functionality used by multiple features:

- **Coordinator**: Manages interactions between different agents and session management.
- **Memory Agent**: Handles conversation history and document references.
- **NLP Agent**: Processes and structures natural language queries.
- **Table Generator**: Creates custom tables from financial data.
- **Embeddings Provider**: Provides semantic embeddings for text understanding.

When developing with the agent framework, treat it as a service that your feature consumes rather than extending it directly.

## Example: Using the Table Generator in a New Feature

Here's a simple example of how to use the table generator in a new feature:

```python
# features/portfolio_analysis/services.py
from agent_framework.table_generator import CustomTableGenerator

class PortfolioAnalysisService:
    def __init__(self):
        self.table_generator = CustomTableGenerator()
    
    def generate_portfolio_summary(self, portfolio_data):
        table_spec = {
            "columns": ["asset_class", "market_value", "allocation_percentage"],
            "group_by": "asset_class"
        }
        
        return self.table_generator.generate_custom_table(portfolio_data, table_spec)
```

This example demonstrates how a new feature can leverage the shared capabilities while maintaining its own business logic.
