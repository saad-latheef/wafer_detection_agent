"""Test if agents can be imported and run"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing agent imports...")
print("="*60)

try:
    from shared.context import WaferContext
    print("✅ WaferContext imported")
except Exception as e:
    print(f"❌ WaferContext import failed: {e}")
    exit(1)

try:
    from agents.ingestion_agent import ingest_image
    print("✅ ingest_image imported")
except Exception as e:
    print(f"❌ ingest_image import failed: {e}")
    exit(1)

try:
    from agents.ml_agent import run_ml_inference
    print("✅ run_ml_inference imported")
except Exception as e:
    print(f"❌ run_ml_inference import failed: {e}")
    exit(1)

# Test with a real image
image_path = "Datasets/Photos/Edge_Loc_25000.png"

if not os.path.exists(image_path):
    print(f"❌ Test image not found: {image_path}")
    exit(1)

print(f"\nTesting with image: {image_path}")
print("="*60)

context = WaferContext(image_path=image_path, max_attempts=3)

print("\n1. Running ingestion...")
ingest_image(context)

if hasattr(context, 'processed_tensor'):
    print(f"✅ Tensor created: {context.processed_tensor.shape}")
else:
    print("❌ No tensor created!")

print("\n2. Running ML inference...")
run_ml_inference(context)

if hasattr(context, 'model_name'):
    print(f"✅ Model name: {context.model_name}")
else:
    print("❌ No model_name set!")

if hasattr(context, 'predicted_class'):
    print(f"✅ Predicted: {context.predicted_class}")
else:
    print("❌ No prediction!")

print("="*60)
