import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No GOOGLE_API_KEY found")
    exit(1)

genai.configure(api_key=api_key)

print("Attempting to list models...")
try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
