import sys
import os
import subprocess
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def run_agent(agent_name, filepath):
    """Runs a specified agent script."""
    try:
        agent_script = f"{agent_name.lower().replace(' ', '_').replace('/', '_')}_agent.py"
        result = subprocess.run(['python', agent_script, filepath], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running {agent_name} agent: {e.stderr}"

def generate_gemini_suggestions(code, report):
    """Generates Gemini API suggestions."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Analyze the following code and provide suggestions:\\n\\n{code}\\n\\nReport:\\n{report}"
    response = model.generate_content(prompt)
    return response.text
