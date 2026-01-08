"""
Diagnostic script to check what's happening with ML models and individual_results
"""
import os
import sys
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.context import WaferContext
from agents.ingestion_agent import ingest_image
from agents.ml_agent import run_ml_inference

# Test with a simple NPY file
test_file = "Datasets/NPY files/02_good.npy"

if not os.path.exists(test_file):
    print(f"Test file not found: {test_file}")
    sys.exit(1)

print("=" * 60)
print("Diagnostic: ML Agent Individual Results")
print("=" * 60)

context = WaferContext(image_path=test_file, max_attempts=3)

# Run ingestion
print("\n1. Running ingestion...")
ingest_image(context)
print(f"   ✓ Tensor shape: {context.processed_tensor.shape if hasattr(context, 'processed_tensor') else 'None'}")

# Run ML inference
print("\n2. Running ML inference...")
run_ml_inference(context)

# Check results
print("\n3. Checking results...")
print(f"   hasattr(context, 'individual_results'): {hasattr(context, 'individual_results')}")
print(f"   hasattr(context, 'model_name'): {hasattr(context, 'model_name')}")

if hasattr(context, 'individual_results'):
    print(f"  individual_results type: {type(context.individual_results)}")
    print(f"   individual_results length: {len(context.individual_results)}")
    print(f"   individual_results bool: {bool(context.individual_results)}")
    
    if context.individual_results:
        print(f"\n   Individual Results:")
        for idx, result in enumerate(context.individual_results):
            print(f"     [{idx}] Model: {result.get('model', 'Unknown')}")
            print(f"         Prediction: {result.get('prediction', 'None')}")
            print(f"         Confidence: {result.get('confidence', 0.0):.2%}")
    else:
        print("   ⚠️ individual_results is EMPTY!")
else:
    print("   ❌ individual_results NOT SET!")

if hasattr(context, 'model_name'):
    print(f"\n   Model name: {context.model_name}")

if hasattr(context, 'predicted_class'):
    print(f"   Predicted class: {context.predicted_class}")
    print(f"   Confidence: {context.confidence:.2%}")

print("\n" + "=" * 60)
