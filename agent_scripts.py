import sys
import os
import subprocess
# Removed direct genai import
from shared.ai_utils import AIModel # Import centralized AIModel

# Removed direct genai configuration

def run_agent(agent_name, filepath):
    """Runs a specified agent script."""
    try:
        agent_script = f"{agent_name.lower().replace(' ', '_').replace('/', '_')}_agent.py"
        result = subprocess.run(['python', agent_script, filepath], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running {agent_name} agent: {e.stderr}"

def generate_gemini_suggestions(code, report, model_name='gemini-pro'):
    """Generates Gemini API suggestions using the centralized AIModel."""
    # Instantiate AIModel with gemini provider
    # TODO: Consider making the model name configurable or passed in
    ai_model = AIModel(model_name=model_name, provider="gemini")
    
    prompt = f"Analyze the following code and provide suggestions based on the report:\\n\\nCode:\\n```\\n{code}\\n```\\n\\nReport:\\n{report}\\n\\nSuggestions:"
    
    # Use the centralized generate_text method
    suggestions = ai_model.generate_text(prompt, max_length=1000) # Increased max_length for potentially longer suggestions
    return suggestions
