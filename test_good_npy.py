"""Test good.npy file to verify fix"""
import requests
import os

npy_file = "Datasets/NPY files/02_good.npy"

if not os.path.exists(npy_file):
    print(f"File not found: {npy_file}")
    exit(1)

print("="*60)
print("TESTING NPY FIX WITH GOOD WAFER FILE")
print("="*60)
print(f"File: {npy_file}")
print()

with open(npy_file, 'rb') as f:
    files = {'file': (os.path.basename(npy_file), f, 'application/octet-stream')}
    
    try:
        response = requests.post('http://localhost:8000/api/analyze', files=files)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get prediction from first agent result
            agent_results = data.get('agentResults', [])
            if agent_results:
                prediction = agent_results[0].get('topPattern', 'N/A')
                confidence = agent_results[0].get('confidence', 0)
                model = data.get('modelUsed', 'N/A')
                
                print(f"Model: {model}")
                print(f"Predicted: {prediction}")
                print(f"Confidence: {confidence:.4f} ({confidence*100:.2f}%)")
                print()
                
                # Check if fix worked
                if prediction == "none":
                    print("✅ SUCCESS! Correctly predicts 'none' (good wafer)")
                elif prediction in ["Normal", "good"]:
                    print("✅ CLOSE! Predicts as normal/good (acceptable)")
                else:
                    print(f"❌ STILL BROKEN! Predicts as '{prediction}' instead of 'none'")
                    print()
                    print("Expected: 'none' (indicating no defect)")
                    
            else:
                print("❌ No agent results in response")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

print("="*60)
