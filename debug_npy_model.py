"""Direct test of .npy inference to see raw model outputs"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch
import torch.nn.functional as F
from agents.ml_agent import CLASS_NAMES

# Load the k_cross_CNN model
model_path = "k_cross_CNN.pt"
checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
state_dict = checkpoint.get('model_state_dict', checkpoint)

# Load model architecture
from agents.ml_agent import _load_torch_model
model = _load_torch_model(torch.device('cpu'))

print("="*70)
print("DIRECT .NPY MODEL TEST")
print("="*70)

# Load and process .npy file
npy_file = "Datasets/NPY files/02_good.npy"
wafer_map = np.load(npy_file)

print(f"\n1. Input File: {npy_file}")
print(f"   Wafer map shape: {wafer_map.shape}")
print(f"   Value counts: 0={np.sum(wafer_map==0)}, 1={np.sum(wafer_map==1)}, 2={np.sum(wafer_map==2)}")

# Convert using the ingestion agent's method
from agents.ingestion_agent import _wafer_map_to_tensor
tensor = _wafer_map_to_tensor(wafer_map)

print(f"\n2. Tensor Info:")
print(f"   Shape: {tensor.shape}")
print(f"   Dtype: {tensor.dtype}")
print(f"   Min/Max: {tensor.min():.4f} / {tensor.max():.4f}")

# Run inference
with torch.no_grad():
    logits = model(tensor.float())
    probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()

print(f"\n3. Model Output:")
print(f"   Logits shape: {logits.shape}")
print(f"   Probs shape: {probs.shape}")

# Show all predictions
print(f"\n4. All Class Probabilities:")
for idx, (cls, prob) in enumerate(zip(CLASS_NAMES, probs)):
    marker = "👉" if idx == np.argmax(probs) else "  "
    print(f"   {marker} {idx}: {cls:12s} = {prob:.6f} ({prob*100:.2f}%)")

pred_idx = np.argmax(probs)
print(f"\n5. Final Prediction:")
print(f"   Index: {pred_idx}")
print(f"   Class: {CLASS_NAMES[pred_idx]}")
print(f"   Confidence: {probs[pred_idx]:.6f} ({probs[pred_idx]*100:.2f}%)")
print(f"\n   Expected: Normal (or good)")
print(f"   Got: {CLASS_NAMES[pred_idx]}")
print(f"   CORRECT: {CLASS_NAMES[pred_idx] in ['Normal', 'none', 'good']}")

print("="*70)
