"""Test copilot with simple request"""
import requests
import json

query = "What is the current yield rate?"

print(f"Testing: {query}")
print("="*60)

response = requests.post(
    'http://localhost:8000/api/copilot/query',
    json={"query": query}
)

if response.status_code == 200:
    data = response.json()
    print("✅ Response received!\n")
    print(data.get('response', 'No response'))
    print("\n" + "="*60)
    print("Suggestions:")
    for s in data.get('suggestions', []):
        print(f"  - {s}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
