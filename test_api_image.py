"""Enhanced test script with validation"""
import requests
import os

# Find a test image
image_path = "Datasets/Photos/Edge_Loc_25000.png"

if not os.path.exists(image_path):
    print(f"Image not found: {image_path}")
    exit(1)

print(f"Testing image upload: {image_path}")
print("="*60)

# Upload to API
url = "http://localhost:8000/api/analyze"

with open(image_path, 'rb') as f:
    files = {'file': (os.path.basename(image_path), f, 'image/png')}
    
    try:
        response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ SUCCESS - Response Structure:")
            print(f"  Model Used: {data.get('modelUsed', 'N/A')}")
            print(f"  Predicted Class: {data.get('finalVerdict', 'N/A')}")
            
            confidence = data.get('confidence', 0)
            print(f"  Confidence (raw): {confidence}")
            print(f"  Confidence (%): {confidence * 100:.2f}%")
            
            # Validate confidence is in correct range
            if 0 <= confidence <= 1:
                print(f"  ✅ Confidence in valid range [0, 1]")
            else:
                print(f"  ❌ ERROR: Confidence out of range! Got {confidence}")
            
            print(f"\n  Agent Results ({len(data.get('agentResults', []))}):")
            for idx, result in enumerate(data.get('agentResults', [])):
                print(f"    {idx+1}. {result.get('name', 'N/A')}: {result.get('model', 'N/A')}")
                print(f"       Pattern: {result.get('topPattern', 'N/A')}")
                print(f"       Confidence: {result.get('confidence', 0):.4f} ({result.get('confidence', 0)*100:.2f}%)")
            
            # Check if ML model card exists
            model_cards = [r for r in data.get('agentResults', []) if 'best_model' in r.get('model', '').lower() or 'model:' in r.get('name', '').lower()]
            if model_cards:
                print(f"\n  ✅ ML Model card found!")
                for card in model_cards:
                    print(f"     Name: {card.get('name')}")
                    print(f"     Model: {card.get('model')}")
            else:
                print(f"\n  ⚠️ WARNING: ML Model card NOT in agent results")
                print(f"     Expected: Model card for 'best_model.pt (ResNet18)'")
                print(f"     Found: Only {[r.get('name') for r in data.get('agentResults', [])]}")
            
            # Check probability distribution
            prob_dist = data.get('fullProbabilityDistribution', {})
            if prob_dist:
                print(f"\n  Probability Distribution:")
                sorted_probs = sorted(prob_dist.items(), key=lambda x: x[1], reverse=True)[:3]
                for pattern, prob in sorted_probs:
                    print(f"    {pattern}: {prob:.4f} ({prob*100:.2f}%)")
        else:
            print(f"\n❌ ERROR Response:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("="*60)
