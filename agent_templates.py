def create_agent_script(agent_name):
    """Creates a basic agent script template."""
    agent_name_lower = agent_name.lower().replace(' ', '_').replace('/', '_')
    script = f"""
import sys
import os
# import google.generativeai as genai # Removed, using centralized AIModel via agent_scripts
from agent_scripts import generate_gemini_suggestions

# genai.configure(api_key=os.environ.get("GOOGLE_API_KEY")) # Removed, using centralized AIModel via agent_scripts

def analyze(filepath):
    \"\"\"Analyzes the code for {agent_name} concerns.\"\"\"
    try:
        with open(filepath, 'r') as file:
            code = file.read()

        report = f"{agent_name} Analysis Report:\\n----------------------------\\n"
        # Add your analysis logic here
        report += "Add your analysis logic here.\\n"

        # Generate Gemini API suggestions
        suggestions = generate_gemini_suggestions(code, report)
        report += f"\\nGemini API Suggestions:\\n----------------------------\\n{{suggestions}}"

        return report

    except FileNotFoundError:
        return f"Error: File not found at {{filepath}}"
    except Exception as e:
        return f"An error occurred: {{e}}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python {agent_name_lower}_agent.py <filepath>")
    else:
        filepath = sys.argv[1]
        report = analyze(filepath)
        print(report)
"""
    return script
