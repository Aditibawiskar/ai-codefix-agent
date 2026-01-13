import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

print("--- 1. Loading Env ---")
load_dotenv()
token = os.getenv("HF_TOKEN")
model = os.getenv("HF_MODEL")
print(f"Model: {model}")

print("\n--- 2. Testing Chat Completion ---")
client = InferenceClient(token=token)

try:
    response = client.chat_completion(
        messages=[{"role": "user", "content": "def hello_world():"}],
        model=model,
        max_tokens=50,
    )
    print("✅ SUCCESS!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ ERROR: {e}")
