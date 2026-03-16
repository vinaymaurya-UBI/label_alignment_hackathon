import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")

print(f"Testing with API Key: {api_key[:10]}...")
print(f"Model Name: {model_name}")

genai.configure(api_key=api_key)

try:
    print("\nAttempting to list models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Available Model: {m.name}")
    
    print(f"\nAttempting to generate content with {model_name}...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"\nERROR: {e}")
