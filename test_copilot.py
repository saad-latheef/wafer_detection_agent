"""Test the new Gemini-powered AI Copilot"""
import requests
import json

print("="*60)
print("TESTING GEMINI AI COPILOT")
print("="*60)

# Test query
test_queries = [
    "What's the current yield rate?",
    "Which tool has the most defects?",
    "Show me recent defect trends"
]

for query in test_queries:
    print(f"\n📝 Query: {query}")
    print("-"*60)
    
    try:
        response = requests.post(
            'http://localhost:8000/api/copilot/query',
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Response received:")
            print(f"\n{data.get('response', 'No response')}\n")
            
            if 'suggestions' in data:
                print("💡 Suggested follow-ups:")
                for i, suggestion in enumerate(data['suggestions'], 1):
                    print(f"   {i}. {suggestion}")
            
            if 'powered_by' in data:
                print(f"\n🤖 Powered by: {data['powered_by']}")
                
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("="*60)
