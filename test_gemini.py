import google.generativeai as genai
import sys

genai.configure(api_key="AIzaSyD1oho3hSOE6x_Ql_1oAb7mMllHe-NSgc4")

model = genai.GenerativeModel('models/text-bison-001') # Changed model
try:
    response = model.generate_content("Hello, world!")
    print(response.text)
    print(sys.executable)
except Exception as e:
    print(f"Error: {e}")
