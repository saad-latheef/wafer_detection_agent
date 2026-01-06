"""Test multiple images from different classes to verify model predictions"""
import requests
import os
from pathlib import Path

# Test one image from each class
test_cases = [
    "Datasets/Photos/Center_12000.png",
    "Datasets/Photos/Donut_24000.png",
    "Datasets/Photos/Edge_Loc_25000.png",
    "Datasets/Photos/Edge_Ring_26000.png",
    "Datasets/Photos/normal_00000.png",
]

url = "http://localhost:8000/api/analyze"

print("="*80)
print("TESTING MODEL ACCURACY ON MULTIPLE IMAGES")
print("="*80)

results = []

for image_path in test_cases:
    if not os.path.exists(image_path):
        print(f"⚠️ SKIP: {image_path} not found")
        continue
    
    # Extract expected class from filename
    filename = os.path.basename(image_path)
    expected_class = filename.split('_')[0]  # "Center", "Donut", etc.
    
    print(f"\n📁 Testing: {filename}")
    print(f"   Expected: {expected_class}")
    
    with open(image_path, 'rb') as f:
        files = {'file': (filename, f, 'image/png')}
        
        try:
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                predicted = data.get('agentResults', [{}])[0].get('topPattern', 'N/A')
                confidence = data.get('agentResults', [{}])[0].get('confidence', 0)
                
                # Check top 3 predictions
                prob_dist = data.get('fullProbabilityDistribution', {})
                top3 = sorted(prob_dist.items(), key=lambda x: x[1], reverse=True)[:3]
                
                match = "✅" if predicted == expected_class else "❌"
                
                print(f"   Predicted: {predicted} ({confidence*100:.2f}%) {match}")
                print(f"   Top 3:")
                for cls, prob in top3:
                    marker = "→" if cls == expected_class else " "
                    print(f"     {marker} {cls}: {prob*100:.2f}%")
                
                results.append({
                    'file': filename,
                    'expected': expected_class,
                    'predicted': predicted,
                    'correct': predicted == expected_class,
                    'confidence': confidence
                })
            else:
                print(f"   ❌ ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if results:
    correct = sum(1 for r in results if r['correct'])
    total = len(results)
    accuracy = correct / total * 100
    
    print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"\nResults:")
    for r in results:
        status = "✅" if r['correct'] else "❌"
        print(f"  {status} {r['file']}: Expected={r['expected']}, Got={r['predicted']} ({r['confidence']*100:.1f}%)")
    
    if accuracy < 80:
        print(f"\n⚠️ WARNING: Model accuracy is {accuracy:.1f}% - should be ~99%!")
        print("   Possible issues:")
        print("   1. Image preprocessing mismatch with training")
        print("   2. Class name mapping incorrect")
        print("   3. Model checkpoint issue")
else:
    print("No results - check if images exist")

print("="*80)
