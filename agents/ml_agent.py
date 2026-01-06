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

# Try to import TensorFlow
try:
    import tensorflow as tf
    from tensorflow import keras
    HAS_TF = True
    print(f"[ML Agent Init] ✅ TensorFlow available: {tf.__version__}")
except ImportError as e:
    HAS_TF = False
    print(f"[ML Agent Init] ⚠️ TensorFlow not available: {e}")


# CLASS NAMES - CRITICAL: Different models trained with different class orders!
# NPY model (k_cross_CNN.pt) trained with original class names (hyphens and "none")
NPY_CLASS_NAMES = [
    "Center", "Donut", "Edge-Loc", "Edge-Ring", "Loc",
    "Near-full", "Random", "Scratch", "none"
]

# Image model (best_model.pt) trained with underscores and "Normal"
IMAGE_CLASS_NAMES = [
    "Center", "Donut", "Edge_Loc", "Edge_Ring", "Loc",
    "Near_Full", "Normal", "Random", "Scratch"
]

# Keep this for backward compatibility (uses image model order)
CLASS_NAMES = IMAGE_CLASS_NAMES


# Model paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH_TORCH = os.path.join(PROJECT_ROOT, "k_cross_CNN.pt")
MODEL_PATH_VIT = os.path.join(PROJECT_ROOT, "ViT_Wafer_Defect.h5")
MODEL_PATH_EXT = os.path.join(PROJECT_ROOT, "my_model.weights.h5")
MODEL_PATH_BEST = os.path.join(PROJECT_ROOT, "best_model.pt")  # New ResNet18 model for images

# Global model cache
_MODELS = {
    "torch": None,
    "vit": None,
    "ext": None,
    "best": None  # Cache for best_model.pt
}

def _load_torch_model(device):
    if _MODELS["torch"] is not None:
        return _MODELS["torch"]
    
    if not HAS_TORCH:
        return None
        
    try:
        model = CNN().to(device)
        if os.path.exists(MODEL_PATH_TORCH):
            state = torch.load(MODEL_PATH_TORCH, map_location=device, weights_only=False)
            model.load_state_dict(state)
            model.eval()
            print(f"   ✅ [Torch] Model loaded from {os.path.basename(MODEL_PATH_TORCH)}")
            _MODELS["torch"] = model
            return model
        else:
            print(f"   ❌ [Torch] Model file not found: {MODEL_PATH_TORCH}")
            return None
    except Exception as e:
        print(f"   ❌ [Torch] Load failed: {e}")
        return None

def _load_tf_model(path, key, is_weights_only=False):
    if _MODELS[key] is not None:
        return _MODELS[key]
        
    if not HAS_TF:
        return None
        
    if not os.path.exists(path):
        print(f"   ❌ [TF] Model file not found: {path}")
        return None
        
    try:
        if is_weights_only:
             # If it's weights only, we generally need the architecture.
             # Assuming standard loading matches user expectation for now.
             # If this fails, we might need a model definition.
             print(f"   ⚠️ [TF] Loading weights-only .h5 is risky without architecture. Attempting load_model...")
             model = keras.models.load_model(path)
        else:
            model = keras.models.load_model(path)
            
        print(f"   ✅ [TF] Model loaded from {os.path.basename(path)}")
        _MODELS[key] = model
        return model
    except Exception as e:
        print(f"   ❌ [TF] Load failed for {os.path.basename(path)}: {e}")
        return None

def _load_best_model(device):
    """Load the best_model.pt (ResNet18 for images)."""
    if _MODELS["best"] is not None:
        return _MODELS["best"]
    
    if not HAS_TORCH:
        return None
    
    if not os.path.exists(MODEL_PATH_BEST):
        print(f"   ❌ [Best Model] File not found: {MODEL_PATH_BEST}")
        return None
    
    try:
        import torchvision.models as models
        
        # Load checkpoint
        checkpoint = torch.load(MODEL_PATH_BEST, map_location=device, weights_only=False)
        
        # Get model configuration from checkpoint
        model_config = checkpoint.get('config', {})
        num_classes = model_config.get('num_classes', 9)
        
        # Create ResNet18 architecture
        model = models.resnet18(pretrained=False)
        num_features = model.fc.in_features
        model.fc = torch.nn.Linear(num_features, num_classes)
        
        # Load weights - handle 'model.' prefix if present
        state_dict = checkpoint['model_state_dict']
        
        # Check if keys have 'model.' prefix and remove it
        if any(key.startswith('model.') for key in state_dict.keys()):
            state_dict = {key.replace('model.', ''): value for key, value in state_dict.items()}
        
        model.load_state_dict(state_dict)
        model = model.to(device)
        model.eval()
        
        print(f"   ✅ [Best Model] ResNet18 loaded from {os.path.basename(MODEL_PATH_BEST)}")
        print(f"       Trained accuracy: {checkpoint.get('best_acc', 'N/A')}%")
        
        _MODELS["best"] = model
        return model
        
    except Exception as e:
        print(f"   ❌ [Best Model] Load failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_ml_inference(context):
    """
    ML Inference tool: Runs the appropriate model(s) based on input type.
    """
    print("\n" + "─"*50)
    print("🤖 [ML Agent] Starting Machine Learning Inference")
    print("─"*50)
    
    # Determine input type
    image_path = context.image_path if hasattr(context, 'image_path') else ""
    is_image_input = image_path.lower().endswith(('.png', '.jpg', '.jpeg'))
    
    # Get tensor/data
    tensor = None
    if hasattr(context, 'processed_tensor') and context.processed_tensor is not None:
        tensor = context.processed_tensor
    
    if tensor is None:
        print("   ⚠️ No input tensor found in context.")
        return _simulate_inference(context)

    # Initialize results list
    context.individual_results = []

    # --- IMAGE INPUT FLOW (ResNet18 best_model.pt) ---
    if is_image_input:
        print("   🖼️ Detected IMAGE input - using ResNet18 model")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_best = _load_best_model(device)
        
        if model_best and HAS_TORCH:
            try:
                # Tensor is already preprocessed by ingestion agent
                t_in = tensor.to(device).float()
                
                with torch.no_grad():
                    logits = model_best(t_in)
                    probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()
                
                pred_idx = np.argmax(probs)
                top_class = CLASS_NAMES[pred_idx]
                top_prob = float(probs[pred_idx])
                
                print(f"   🧠 ResNet18 Prediction: {top_class} ({top_prob*100:.1f}%)")
                
                # Add to individual results
                context.individual_results = [{
                    "model": "best_model.pt (ResNet18)",
                    "probs": probs.tolist(),
                    "prediction": top_class,
                    "confidence": top_prob
                }]
                
                context.model_name = "best_model.pt (ResNet18)"
                _update_context(context, probs, top_class, top_prob)
                return context
                
            except Exception as e:
                print(f"   ❌ ResNet18 inference failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback if best_model fails
        print("   ⚠️ ResNet18 model unavailable. Falling back to simulation.")
        context.model_name = "Simulation (ResNet18 Missing)"
        return _simulate_inference(context)

    # --- NPY INPUT FLOW (Ensemble: Torch + MyModel) ---
    else:
        print("   💾 Detected WAFER MAP (.npy) input - running Ensemble")
        results = []
        
        # 1. Run Torch Model
        if HAS_TORCH:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model_torch = _load_torch_model(device)
            if model_torch:
                try:
                    t_in = tensor.to(device).float()
                    with torch.no_grad():
                        logits = model_torch(t_in)
                        probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()
                        
                    # Add to individual results - USE NPY_CLASS_NAMES for k_cross_CNN!
                    pred_idx = np.argmax(probs)
                    results.append(("k_cross_CNN.pt", probs))
                    context.individual_results.append({
                        "model": "k_cross_CNN.pt",
                        "probs": probs.tolist(), 
                        "prediction": NPY_CLASS_NAMES[pred_idx],
                        "confidence": float(probs[pred_idx])
                    })
                except Exception as e:
                    print(f"   ❌ Torch inference failed: {e}")

        # 2. Run Extension Model (TF)
        model_ext = _load_tf_model(MODEL_PATH_EXT, "ext")
        if model_ext:
            try:
                # Convert processed_tensor (Torch) to Numpy for TF
                np_in = tensor.cpu().numpy()
                if np_in.shape[1] < np_in.shape[2]: # NCHW -> NHWC
                     np_in = np.moveaxis(np_in, 1, -1)
                
                probs_ext = model_ext.predict(np_in, verbose=0)[0]
                
                # Add to individual results - USE NPY_CLASS_NAMES for my_model too!
                pred_idx = np.argmax(probs_ext)
                results.append(("my_model.weights.h5", probs_ext))
                context.individual_results.append({
                    "model": "my_model.weights.h5",
                    "probs": probs_ext.tolist(),
                    "prediction": NPY_CLASS_NAMES[pred_idx],
                    "confidence": float(probs_ext[pred_idx])
                })
            except Exception as e:
                 print(f"   ❌ MyModel inference failed: {e}")
        
        # 3. Ensemble Decision (Best Confidence)
        if not results:
            print("   ⚠️ No models ran successfully. Simulating.")
            context.model_name = "Simulation (Models Failed)"
            return _simulate_inference(context)
            
        print("\n   🤝 Ensemble Results:")
        best_conf = -1
        best_pred = None
        best_probs = None
        best_source = ""
        
        for name, p in results:
            pred_idx = np.argmax(p)
            conf = p[pred_idx]
            # CRITICAL: Use NPY_CLASS_NAMES for .npy models!
            cls = NPY_CLASS_NAMES[pred_idx]  
            print(f"      - {name}: {cls} ({conf*100:.1f}%)")
            
            if conf > best_conf:
                best_conf = conf
                best_pred = cls
                best_probs = p
                best_source = name
        
        print(f"\n   🏆 Best Prediction: {best_pred} from {best_source}")
        context.model_name = f"Ensemble (Best: {best_source})"
        print(f"   ✅ Set context.individual_results: {len(context.individual_results)} entries")
        _update_context(context, best_probs, best_pred, best_conf)
        return context

def _run_tf_inference(context, model, tensor, model_name):
    try:
        # Convert Torch tensor to Numpy (NHWC)
        np_in = tensor.cpu().numpy()
        if np_in.shape[1] < np_in.shape[2]: # NCHW -> NHWC
            np_in = np.moveaxis(np_in, 1, -1)
            
        probs = model.predict(np_in, verbose=0)[0]
        
        pred_idx = np.argmax(probs)
        top_class = CLASS_NAMES[pred_idx]
        top_prob = float(probs[pred_idx])
        
        print(f"   🧠 {model_name} Prediction: {top_class} ({top_prob*100:.1f}%)")
        
        # Add to individual results
        context.individual_results = [{
            "model": model_name,
            "probs": probs.tolist(),
            "prediction": top_class,
            "confidence": top_prob
        }]
        
        _update_context(context, probs, top_class, top_prob)
        return context
        
    except Exception as e:
        print(f"   ❌ {model_name} inference error: {e}")
        return _simulate_inference(context)

def _update_context(context, probs, top_class, top_prob):
    context.probability_distribution = {k: float(v) for k, v in zip(CLASS_NAMES, probs)}
    context.predicted_class = top_class
    context.confidence = top_prob
    context.has_defect = (top_class != "none")
    
    if context.has_defect:
        print(f"   ⚠️ DEFECT DETECTED: {top_class}")
    else:
        print("   ✅ No defect detected")


def _simulate_inference(context):
    """Fallback simulation when models fail."""
    import random
    
    print("   🎲 Running SIMULATED inference (fallback)")
    
    probs = [random.random() for _ in CLASS_NAMES]
    total = sum(probs)
    probs = [p/total for p in probs]
    
    pred_idx = probs.index(max(probs))
    top_class = CLASS_NAMES[pred_idx]
    top_prob = probs[pred_idx]
    
    # Add fake individual result
    context.individual_results = [{
        "model": "Simulation",
        "probs": np.array(probs),
        "prediction": top_class,
        "confidence": top_prob
    }]
    
    _update_context(context, probs, top_class, top_prob)
    return context


ml_agent = Agent(
    name="ml_agent",
    model="gemini-2.5-pro",
    description="Runs multi-model defect detection (PyTorch CNN, Keras ViT, Custom Keras).",
    instruction="""
    You are the ML Agent.
    Your role is to:
    1. Analyze the input type (Image vs Wafer Map).
    2. Route to the appropriate model:
       - Images -> ViT_Wafer_Defect.h5
       - Wafer Maps -> Ensemble of k_cross_CNN.pt and my_model.weights.h5
    3. Return the best prediction with confidence.
    
    Always explain which models were used.
    """,
    tools=[FunctionTool(run_ml_inference)],
    output_key="ml_output"
)

