import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Load the key
load_dotenv()
key = os.getenv("GEMINI_KEY")
genai.configure(api_key=key)

print(f"Checking models for key ending in ...{key[-5:]}")
print("-" * 30)

try:
    found_any = False
    # 2. Ask Google for the list
    for m in genai.list_models():
        # 3. Only show models that support text chat
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ AVAILABLE: {m.name}")
            found_any = True
            
    if not found_any:
        print("❌ No text-generation models found for this API key.")
        print("This usually means your Google Cloud project doesn't have the Generative AI API enabled.")
        
except Exception as e:
    print(f"❌ Connection Error: {e}")
