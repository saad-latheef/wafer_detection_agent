"""Test .npy file prediction"""
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.context import WaferContext
from agents.ingestion_agent import ingest_image
from agents.ml_agent import run_ml_inference

# Test with a .npy file
npy_file = "Datasets/NPY files/01_edge_loc.npy"  # Edge loc test file

if not os.path.exists(npy_file):
    print(f"❌ Test file not found: {npy_file}")
    print("Please specify a valid .npy test file")
    exit(1)

print("="*60)
print(f"Testing .npy prediction: {npy_file}")
print("="*60)

context = WaferContext(image_path=npy_file, max_attempts=3)

print("\n1. Running ingestion...")
ingest_image(context)

print("\n2. Running ML inference...")
run_ml_inference(context)

print("\n3. Results:")
print(f"   Model: {getattr(context, 'model_name', 'NOT SET')}")
print(f"   Predicted: {getattr(context, 'predicted_class', 'NOT SET')}")
print(f"   Confidence: {getattr(context, 'confidence', 0):.4f}")

if hasattr(context, 'individual_results'):
    print(f"\n4. Individual Model Results:")
    for idx, result in enumerate(context.individual_results):
        print(f"   Model {idx+1}: {result.get('model')}")
        print(f"      Prediction: {result.get('prediction')}")
        print(f"      Confidence: {result.get('confidence', 0):.4f}")

if hasattr(context, 'probability_distribution'):
    print(f"\n5. Top 3 Probabilities:")
    probs = context.probability_distribution
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
    for cls, prob in sorted_probs:
        print(f"   {cls}: {prob:.4f}")

print("="*60)
