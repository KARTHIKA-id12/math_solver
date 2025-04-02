import google.generativeai as genai

# Load your API key from config.py
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

# List available models
models = genai.list_models()
for model in models:
    print(model.name)
