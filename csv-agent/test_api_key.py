import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

# Load environment variables
load_dotenv()

api_key = os.getenv("CEREBRAS_API_KEY")
print(f"API Key found: {api_key[:20]}..." if api_key else "API Key NOT found")

# Test connection
try:
    client = Cerebras(api_key=api_key)
    
    # Simple test request
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Say 'hello' in one word"}],
        model="llama3.1-8b",
        max_tokens=10
    )
    
    print("✅ API Key is VALID!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ API Key test FAILED: {e}")
