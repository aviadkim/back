import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')
if not api_key:
    print("Error: OPENROUTER_API_KEY not found in .env file")
    exit(1)

# Use the primary model defined in .env for testing, or a default
model_to_test = os.getenv('OPENROUTER_PRIMARY_MODEL', 'mistralai/mistral-small-3.1-24b-instruct:free')
site_url = os.getenv('SITE_URL', 'http://localhost:5000') # Get site URL from env or default
site_name = os.getenv('SITE_NAME', 'Financial Document Processor') # Get site name from env or default


print(f"Testing OpenRouter API Key with model: {model_to_test}")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": site_url, # Use SITE_URL from env
    "X-Title": site_name # Use SITE_NAME from env
}
data = {
    "model": model_to_test,
    "messages": [
        {"role": "user", "content": "What is 1+1?"}
    ]
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status code: {response.status_code}")
    # Attempt to pretty-print JSON, otherwise print raw text
    try:
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Response is not valid JSON:")
        print(response.text)
except Exception as e:
    print(f"Error during API request: {str(e)}")