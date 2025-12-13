import os
import sys

from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool

# Try to import PyTorch and model
try:
    import torch
    import torch.nn.functional as F
    import numpy as np
    
    # Add wafer_detection to path for model class
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    wafer_dir = os.path.join(project_root, "wafer_detection")
    if wafer_dir not in sys.path:
        sys.path.insert(0, wafer_dir)
    from model import CNN
    
    HAS_TORCH = True
except ImportError as e:
    HAS_TORCH = False
    print(f"[ML Agent Init] ⚠️ PyTorch not available: {e}")

CLASS_NAMES = [
    "Center", "Donut", "Edge-Loc", "Edge-Ring", "Loc",
    "Near-full", "Random", "Scratch", "none"
]

# Model path is now in root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "k_cross_CNN.pt")


def run_ml_inference(context):
    """
    ML Inference tool: Runs the trained CNN model on the preprocessed tensor.
    Uses tensor from context (prepared by ingestion agent).
    """
    print("\n" + "─"*50)
    print("🤖 [ML Agent] Starting Machine Learning Inference")
    print("─"*50)
    
    if not HAS_TORCH:
        print("   ⚠️ PyTorch not available - using simulated inference")
        return _simulate_inference(context)
    
    print(f"   📦 Loading model from: {MODEL_PATH}")
    
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"   💻 Using device: {device}")
        
        # Load model
        model = CNN().to(device)
        if os.path.exists(MODEL_PATH):
            state = torch.load(MODEL_PATH, map_location=device, weights_only=False)
            model.load_state_dict(state)
            model.eval()
            print("   ✅ Model loaded successfully")
        else:
            print(f"   ❌ Model file not found at {MODEL_PATH}")
            return _simulate_inference(context)
        
        # Get tensor from context (prepared by ingestion agent)
        tensor = None
        
        if hasattr(context, 'processed_tensor') and context.processed_tensor is not None:
            tensor = context.processed_tensor
            if not isinstance(tensor, torch.Tensor):
                tensor = torch.tensor(tensor)
            tensor = tensor.to(device)
            print(f"   ✅ Using tensor from context")
            print(f"   📐 Tensor shape: {tensor.shape}")
        else:
            # Fallback: try to load from file if image_path is .npy
            image_path = context.image_path if hasattr(context, 'image_path') else ""
            if image_path.endswith('.npy'):
                print(f"   📂 Loading from file: {image_path}")
                from preprocess_real import preprocess_real_wafer
                tensor = preprocess_real_wafer(image_path).to(device)
            else:
                print("   ⚠️ No tensor in context - using synthetic for demo")
                tensor = torch.randn(1, 3, 56, 56).to(device)
        
        # Ensure correct dtype
        tensor = tensor.float()
        
        # Run inference
        print("   🧠 Running neural network inference...")
        with torch.no_grad():
            logits = model(tensor)
            probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()
        
        # Process results
        pred_idx = int(np.argmax(probs))
        top_class = CLASS_NAMES[pred_idx]
        top_prob = float(probs[pred_idx])
        
        print("\n   📊 Probability Distribution:")
        print("   " + "─"*40)
        for i, (cls, p) in enumerate(zip(CLASS_NAMES, probs)):
            bar = "█" * int(p * 20)
            marker = " ← PREDICTED" if i == pred_idx else ""
            print(f"   {cls:12s}: {p:.4f} {bar}{marker}")
        print("   " + "─"*40)
        
        print(f"\n   🎯 Top Prediction: {top_class} ({top_prob*100:.1f}% confidence)")
        
        # Update context
        context.probability_distribution = {k: float(v) for k, v in zip(CLASS_NAMES, probs)}
        context.predicted_class = top_class
        context.confidence = top_prob
        context.has_defect = (top_class != "none")
        
        if context.has_defect:
            print(f"   ⚠️ DEFECT DETECTED: {top_class}")
        else:
            print("   ✅ No defect detected - wafer appears clean")
        
        return context
        
    except Exception as e:
        print(f"   ❌ Inference error: {e}")
        import traceback
        traceback.print_exc()
        return _simulate_inference(context)


def _simulate_inference(context):
    """Fallback simulation when PyTorch is not available."""
    import random
    
    print("   🎲 Running SIMULATED inference (demo mode)")
    
    probs = [random.random() for _ in CLASS_NAMES]
    total = sum(probs)
    probs = [p/total for p in probs]
    
    pred_idx = probs.index(max(probs))
    top_class = CLASS_NAMES[pred_idx]
    top_prob = probs[pred_idx]
    
    print("\n   📊 Simulated Probability Distribution:")
    for cls, p in zip(CLASS_NAMES, probs):
        bar = "█" * int(p * 20)
        print(f"   {cls:12s}: {p:.4f} {bar}")
    
    print(f"\n   🎯 Simulated Prediction: {top_class} ({top_prob*100:.1f}%)")
    
    context.probability_distribution = {k: v for k, v in zip(CLASS_NAMES, probs)}
    context.predicted_class = top_class
    context.confidence = top_prob
    context.has_defect = (top_class != "none")
    
    return context


ml_agent = Agent(
    name="ml_agent",
    model="gemini-2.5-pro",
    description="Runs the trained CNN model to detect wafer defects.",
    instruction="""
    You are the ML Agent.
    Your role is to:
    1. Load the trained k_cross_CNN model from root directory
    2. Use the preprocessed tensor from context (prepared by ingestion agent)
    3. Run inference to get probability distribution
    4. Identify the most likely defect class
    5. Store results in the shared context
    
    Always explain your predictions and confidence levels.
    """,
    tools=[FunctionTool(run_ml_inference)],
    output_key="ml_output"
)
