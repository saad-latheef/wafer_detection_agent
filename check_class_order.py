"""Check class names in checkpoint"""
import sys
sys.path.insert(0, '../pytorch_image_classifier')

import torch

checkpoint_path = '../pytorch_image_classifier/models/best_model.pt'
checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)

config = checkpoint.get('config', {})
print("="*60)
print("CHECKPOINT CLASS NAMES")
print("="*60)
print("Class names:", config.get('class_names', 'NOT FOUND'))
print("Number of classes:", config.get('num_classes', 'NOT FOUND'))
print("\nClass order (index -> name):")
for idx, name in enumerate(config.get('class_names', [])):
    print(f"  {idx}: {name}")

print("\n" + "="*60)
print("ML_AGENT CLASS_NAMES (current)")
print("="*60)

# Import from ml_agent
from agents.ml_agent import CLASS_NAMES as agent_classes

print("Class names:", agent_classes)
print("\nClass order (index -> name):")
for idx, name in enumerate(agent_classes):
    print(f"  {idx}: {name}")

print("\n" + "="*60)
print("COMPARISON")
print("="*60)

checkpoint_classes = config.get('class_names', [])
if checkpoint_classes == agent_classes:
    print("✅ CLASS NAMES MATCH!")
else:
    print("❌ CLASS NAMES MISMATCH!")
    print("\nDifferences:")
    for idx in range(max(len(checkpoint_classes), len(agent_classes))):
        c_name = checkpoint_classes[idx] if idx < len(checkpoint_classes) else "MISSING"
        a_name = agent_classes[idx] if idx < len(agent_classes) else "MISSING"
        match = "✓" if c_name == a_name else "✗"
        print(f"  {idx}: {c_name:15} vs {a_name:15} {match}")
