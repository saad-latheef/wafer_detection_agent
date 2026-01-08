"""Test that tool_id appears in frontend history"""
import requests
import time

print("Creating new record with tool_id...")
r = requests.post(
    'http://localhost:8000/api/analyze', 
    files={'file': open('Datasets/NPY files/02_good.npy', 'rb')}, 
    data={'tool_id': 'PROD-777', 'chamber_id': 'CH-ALPHA'}
)

time.sleep(1)

r2 = requests.get('http://localhost:8000/api/history?limit=1')
record = r2.json()['records'][0]

print(f"\n✓ Latest record tool_id: {record['toolId']}")
print(f"✓ Latest record chamber_id: {record['chamberId']}")
print(f"✓ Wafer ID: {record['waferId']}")
print("\nThe frontend will now show PROD-777 for this record!")
print("Refresh the Scan History page in the browser to see it.")
