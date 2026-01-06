"""Direct test to verify NPY_CLASS_NAMES is being used"""
from agents.ml_agent import NPY_CLASS_NAMES, IMAGE_CLASS_NAMES

print("="*60)
print("VERIFYING CLASS NAMES ARE CORRECT")
print("="*60)

print("\nNPY_CLASS_NAMES (for k_cross_CNN.pt):")
for i, name in enumerate(NPY_CLASS_NAMES):
    print(f"  {i}: {name}")

print("\nIMAGE_CLASS_NAMES (for best_model.pt):")  
for i, name in enumerate(IMAGE_CLASS_NAMES):
    print(f"  {i}: {name}")

print("\nKEY DIFFERENCE:")
print(f"  NPY index 8: {NPY_CLASS_NAMES[8]}")
print(f"  IMAGE index 8: {IMAGE_CLASS_NAMES[8]}")
print()
print("✅ Fix is in place if NPY index 8 = 'none'")
print("="*60)
