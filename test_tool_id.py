"""
Quick test to verify tool_id and chamber_id are being saved correctly
"""
import requests

# Test with tool_id and chamber_id
files = {'file': open('good.npy', 'rb')}
data = {
    'tool_id': 'TOOL-1',
    'chamber_id': 'CHAMBER-A'
}

print("Testing with tool_id and chamber_id...")
response = requests.post('http://localhost:8000/api/analyze', files=files, data=data)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Wafer ID: {result.get('waferId')}")
    print(f"✅ Prediction: {result.get('predictedClass')}")
    print(f"✅ Verdict: {result.get('verdict')}")
    
    # Check if tool_id was saved (you can verify in database)
    print("\n📊 Check the database - wafer should have:")
    print(f"   - tool_id: TOOL-1")
    print(f"   - chamber_id: CHAMBER-A")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
