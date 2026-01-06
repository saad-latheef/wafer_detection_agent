"""Compare .npy predictions before/after to identify regression"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.context import WaferContext
from agents.ingestion_agent import ingest_image  
from agents.ml_agent import run_ml_inference

# Test multiple .npy files
test_files = [
    "Datasets/NPY files/01_edge_loc.npy",
    "Datasets/NPY files/02_good.npy",
]

print("="*70)
print("TESTING MULTIPLE .NPY FILES")
print("="*70)

for npy_file in test_files:
    if not os.path.exists(npy_file):
        print(f"\n⚠️ Skipping {os.path.basename(npy_file)} - not found")
        continue
        
    print(f"\n{'='*70}")
    print(f"Testing: {os.path.basename(npy_file)}")
    print(f"{'='*70}")
    
    context = WaferContext(image_path=npy_file, max_attempts=3)
    ingest_image(context)
    run_ml_inference(context)
    
    print(f"\n📊 RESULTS:")
    print(f"   Predicted: {context.predicted_class}")
    print(f"   Confidence: {context.confidence:.4f} ({context.confidence*100:.2f}%)")
    print(f"   Model: {context.model_name}")
    
    if hasattr(context, 'probability_distribution'):
        probs = context.probability_distribution
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"\n   Top 3 Predictions:")
        for i, (cls, prob) in enumerate(sorted_probs, 1):
            print(f"      {i}. {cls}: {prob:.4f} ({prob*100:.2f}%)")
    
    # Check if "Scratch" is being incorrectly predicted
    if context.predicted_class == "Scratch":
        print(f"\n   ⚠️ WARNING: Predicted as Scratch")
        print(f"   Expected: {os.path.basename(npy_file).split('_')[1].replace('.npy', '')}")

print(f"\n{'='*70}")
print("TEST COMPLETE")
print("="*70)
