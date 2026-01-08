"""
Test script to verify tool_id and chamber_id are being saved correctly after the fix.
"""
import requests
import os

# Find a test file
test_file = "Datasets/NPY files/02_good.npy"
if not os.path.exists(test_file):
    print(f"❌ Test file '{test_file}' not found")
    print("Please place a test .npy file in the current directory or update the script with the correct path")
    exit(1)

# Test with tool_id and chamber_id
files = {'file': open(test_file, 'rb')}
data = {
    'tool_id': 'TOOL-TEST-123',
    'chamber_id': 'CHAMBER-A-456'
}

print("=" * 60)
print("Testing tool_id and chamber_id fix...")
print("=" * 60)
print(f"File: {test_file}")
print(f"Tool ID: {data['tool_id']}")
print(f"Chamber ID: {data['chamber_id']}")
print()

try:
    response = requests.post('http://localhost:8000/api/analyze', files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API call successful!")
        print()
        print(f"Wafer ID: {result.get('waferId')}")
        print(f"Prediction: {result.get('predictedClass', 'N/A')}")
        print(f"Verdict: {result.get('finalVerdict')}")
        print(f"Confidence: {result.get('confidence', 0) * 100:.1f}%")
        print()
        print("=" * 60)
        print("Checking database record...")
        print("=" * 60)
        
        # Now query the history to verify tool_id was saved
        history_response = requests.get('http://localhost:8000/api/history', params={'limit': 1})
        
        if history_response.status_code == 200:
            history = history_response.json()
            if history.get('records') and len(history['records']) > 0:
                latest = history['records'][0]
                saved_tool_id = latest.get('toolId', 'N/A')
                saved_chamber_id = latest.get('chamberId', 'N/A')
                
                print(f"Saved Tool ID: {saved_tool_id}")
                print(f"Saved Chamber ID: {saved_chamber_id}")
                print()
                
                # Verify the fix worked
                if saved_tool_id == data['tool_id']:
                    print("✅ SUCCESS! Tool ID was saved correctly!")
                else:
                    print(f"❌ FAILED! Expected '{data['tool_id']}' but got '{saved_tool_id}'")
                    
                if saved_chamber_id == data['chamber_id']:
                    print("✅ SUCCESS! Chamber ID was saved correctly!")
                else:
                    print(f"❌ FAILED! Expected '{data['chamber_id']}' but got '{saved_chamber_id}'")
            else:
                print("⚠️ No records found in history")
        else:
            print(f"⚠️ Could not fetch history: {history_response.status_code}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to backend server")
    print("Make sure the server is running on http://localhost:8000")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 60)
