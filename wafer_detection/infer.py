import torch
import torch.nn.functional as F
import numpy as np

from model import CNN
from preprocess_real import preprocess_real_wafer

# --------------------
# CONFIG
# --------------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "k_cross_CNN.pt"
INPUT_PATH = "real_input/wafer.npy"

CLASS_NAMES = [
    "Center",
    "Donut",
    "Edge-Loc",
    "Edge-Ring",
    "Loc",
    "Near-full",
    "Random",
    "Scratch",
    "none"
]

# --------------------
# LOAD MODEL
# --------------------
model = CNN().to(DEVICE)
state = torch.load(MODEL_PATH, map_location=DEVICE)
model.load_state_dict(state)
model.eval()

# --------------------
# LOAD & PREPROCESS REAL INPUT
# --------------------
tensor = preprocess_real_wafer(INPUT_PATH).to(DEVICE)

# Safety check
assert tensor.dtype == torch.float32, "Input tensor must be float32"
assert tensor.shape == (1, 3, 56, 56), f"Unexpected input shape: {tensor.shape}"

# --------------------
# INFERENCE
# --------------------
with torch.no_grad():
    logits = model(tensor)
    probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()

# --------------------
# OUTPUT
# --------------------
print("\n🔍 Defect Probability Distribution:\n")

for cls, p in zip(CLASS_NAMES, probs):
    print(f"{cls:12s}: {p:.4f}")

pred_idx = np.argmax(probs)

print("\n✅ Dominant Defect:", CLASS_NAMES[pred_idx])
print("🎯 Confidence:", probs[pred_idx])
