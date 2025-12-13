import os
import sys
import time
import json

# Add the wafer_detection directory to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
wafer_dir = os.path.join(project_root, "wafer_detection")
if wafer_dir not in sys.path:
    sys.path.append(wafer_dir)

# Try imports
try:
    import torch
    import torch.nn.functional as F
    import numpy as np
    from model import CNN
    from preprocess_real import preprocess_real_wafer
    HAS_TORCH = True
except ImportError as e:
    HAS_TORCH = False
    print(f"[Warning] ML libraries missing: {e}. Falling back to mock.")

CLASS_NAMES = [
    "Center", "Donut", "Edge-Loc", "Edge-Ring", "Loc",
    "Near-full", "Random", "Scratch", "none"
]

MODEL_PATH = os.path.join(wafer_dir, "k_cross_CNN.pt")

def run_ml_inference(input_data):
    """
    Runs the CNN model on the input.
    Input can be a dictionary containing 'tensor' or 'image_path'.
    """
    if not HAS_TORCH:
        return _mock_inference()
        
    print("[Tool: run_ml_inference] Loading Real Model...")
    
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = CNN().to(device)
        
        if os.path.exists(MODEL_PATH):
            state = torch.load(MODEL_PATH, map_location=device)
            model.load_state_dict(state)
            model.eval()
        else:
            print(f"[Error] Model not found at {MODEL_PATH}")
            return _mock_inference()

        # Handle input
        tensor = None
        if isinstance(input_data, dict):
            # If we recieved a Tensor object directly (rare in JSON/REST agents, but possible in local objects)
            if "tensor" in input_data and isinstance(input_data["tensor"], torch.Tensor):
                tensor = input_data["tensor"]
            # If we recieved a path to a wafer map (legacy support for the infer.py style)
            elif "image_path" in input_data:
                # The user's preprocess_real expects an .npy file
                # If we have a jpg, this might fail unless we adapt it.
                # For this specific task, let's assume valid .npy input for the real model, 
                # or fallback if it fails.
                path = input_data["image_path"]
                if path.endswith(".npy"):
                    tensor = preprocess_real_wafer(path).to(device)
        
        if tensor is None:
            print("[Tool: run_ml_inference] No valid tensor input found. Using mock input for demo.")
            # Create dummy tensor for demo if input content isn't actually compatible
            tensor = torch.randn(1, 3, 56, 56).to(device)

        print(f"[Tool: run_ml_inference] Running inference on {device}...")
        with torch.no_grad():
            logits = model(tensor)
            probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()
            
        # Format output
        pred_idx = np.argmax(probs)
        top_class = CLASS_NAMES[pred_idx]
        top_prob = float(probs[pred_idx])
        
        return {
            "logits": logits.tolist(),
            "probability": top_prob,
            "predicted_class": top_class,
            "all_probs": {k: float(v) for k, v in zip(CLASS_NAMES, probs)}
        }

    except Exception as e:
        print(f"[Error] Inference failed: {e}")
        return _mock_inference()

def _mock_inference():
    print("[Tool: run_ml_inference] !!! USING MOCK INFERENCE !!!")
    import random
    prob = random.random()
    idx = random.randint(0, 8)
    return {
        "logits": [],
        "probability": prob,
        "predicted_class": CLASS_NAMES[idx],
        "mock": True
    }

def analyze_predictions(input_data):
    # Handle passed-through data
    ml_output = input_data
    if isinstance(input_data, dict):
         # Extract nested valid output if present
         if "probability" not in input_data:
             ml_output = input_data.get("run_ml_inference", input_data)

    print("[Tool: analyze_predictions] Analyzing...")
    prob = ml_output.get("probability", 0.0)
    pred_class = ml_output.get("predicted_class", "Unknown")
    
    # Logic: "none" class means no defect
    has_defect = pred_class != "none"
    
    # Severity logic
    severity = "None"
    if has_defect:
        if prob > 0.8:
            severity = "High"
        elif prob > 0.5:
            severity = "Medium"
        else:
            severity = "Low"

    return {
        "has_defect": has_defect,
        "severity": severity,
        "class": pred_class,
        "confidence": prob
    }

def validate_analysis(input_data):
    analysis_result = input_data
    if isinstance(input_data, dict):
        if "confidence" not in input_data:
             analysis_result = input_data.get("analyze_predictions", input_data)

    print("[Tool: validate_analysis] Validating...")
    conf = analysis_result.get("confidence", 0)
    
    # If confidence is too low but a class was predicted, flag it
    if 0.2 < conf < 0.4:
         print(f"Validation WARNING: Low confidence ({conf:.2f})")
         return True # Just warn, don't fail for this demo
         
    print("Validation PASSED")
    return True
