"""Test that tool_id defaults to model name when not provided"""
import requests
import time

print("Test 1: With custom tool_id")
r1 = requests.post(
    'http://localhost:8000/api/analyze', 
    files={'file': open('Datasets/NPY files/02_good.npy', 'rb')}, 
    data={'tool_id': 'CUSTOM-TOOL', 'chamber_id': 'CH-1'}
)

print("Test 2: Without tool_id (should default to model name)")
r2 = requests.post(
    'http://localhost:8000/api/analyze', 
    files={'file': open('Datasets/NPY files/02_good.npy', 'rb')}, 
    data={}
)

time.sleep(1)

r3 = requests.get('http://localhost:8000/api/history?limit=2')
records = r3.json()['records']

print(f"\n✓ Latest (no input): tool_id = {records[0]['toolId']}")
print(f"  Expected: CNN (or model name)")
print(f"\n✓ Previous (with input): tool_id = {records[1]['toolId']}")  
print(f"  Expected: CUSTOM-TOOL")

if records[0]['toolId'] in ['CNN', 'ViT', 'ResNet']:
    print("\n✅ SUCCESS! Tool ID defaults to model name when not provided")
else:
    print(f"\n⚠️ Unexpected tool_id: {records[0]['toolId']}")
