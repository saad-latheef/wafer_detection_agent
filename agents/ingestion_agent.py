import os
import numpy as np
from PIL import Image

from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool


def ingest_image(context):
    """
    Ingestion tool: Loads wafer.npy files and prepares tensor for ML model.
    """
    print("\n" + "─"*50)
    print("📥 [Ingestion Agent] Starting ingestion process")
    print("─"*50)
    
    image_path = context.image_path if hasattr(context, 'image_path') else ""
    
    print(f"   📁 Input path: {image_path}")
    
    if not image_path or not os.path.exists(image_path):
        print(f"   ❌ ERROR: File not found at {image_path}")
        return context
    
    is_image = image_path.lower().endswith(('.png', '.jpg', '.jpeg'))
    
    if is_image:
        print("   🖼️ Processing standard image file...")
        try:
            # Load and resize image
            img = Image.open(image_path).convert('RGB')
            img = img.resize((224, 224))  # ResNet18 expects 224x224
            img_array = np.array(img).astype(np.float32) / 255.0
            
            # Apply ImageNet normalization (CRITICAL - must match training!)
            # Training used: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            img_array = (img_array - mean) / std
            
            # Convert to tensor: (H, W, C) -> (C, H, W) -> (1, C, H, W)
            import torch
            tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0).float()
            
            # Mock wafer map statistics since we don't have a discrete map
            non_wafer = 0
            normal = 0
            defect = 0
            wafer_map_shape = (224, 224)
            
            print(f"   📐 Resized to: 224x224")
            print(f"   ✅ Applied ImageNet normalization")
        except Exception as e:
            print(f"   ❌ ERROR: Image processing failed: {e}")
            return context
            
    elif image_path.endswith('.npy'):
        # Load wafer map
        print("   📂 Loading wafer map (.npy)...")
        wafer_map = np.load(image_path)
        print(f"   📐 Wafer map shape: {wafer_map.shape}")
        
        # Count regions
        non_wafer = int(np.sum(wafer_map == 0))
        normal = int(np.sum(wafer_map == 1))
        defect = int(np.sum(wafer_map == 2))
        print(f"   📊 Statistics:")
        print(f"      - Non-wafer (0): {non_wafer}")
        print(f"      - Normal (1):    {normal}")
        print(f"      - Defect (2):    {defect}")
        
        # Convert to tensor
        print("   🔄 Converting to model tensor...")
        tensor = _wafer_map_to_tensor(wafer_map)
        wafer_map_shape = wafer_map.shape
        
    else:
        print(f"   ❌ ERROR: Unsupported file type: {image_path}")
        return context

    print(f"   📐 Tensor shape: {tensor.shape}")
    
    # Store in context
    context.processed_tensor = tensor
    context.metadata = {
        "original_path": image_path,
        "wafer_map_shape": wafer_map_shape,
        "tensor_shape": tuple(tensor.shape),
        "defect_count": int(defect),
        "normal_count": int(normal),
        "non_wafer_count": int(non_wafer)
    }
    
    print("   ✅ Ingestion complete - tensor ready for ML agent")
    return context


def _wafer_map_to_tensor(wafer_map):
    """
    Converts wafer map (0,1,2) to RGB tensor for CNN.
    Uses same encoding as preprocess_real_wafer.
    """
    import torch
    
    h, w = wafer_map.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    
    # One-hot encoding to RGB channels
    rgb[wafer_map == 0, 0] = 255  # non-wafer → Red
    rgb[wafer_map == 1, 1] = 255  # normal → Green
    rgb[wafer_map == 2, 2] = 255  # defect → Blue
    
    # Resize to 56x56 (model input size)
    img = Image.fromarray(rgb).resize((56, 56))
    img_array = np.array(img).astype(np.float32) / 255.0
    
    # Convert to tensor: (H, W, C) -> (C, H, W) -> (1, C, H, W)
    tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
    
    return tensor


ingestion_agent = Agent(
    name="ingestion_agent",
    model="gemini-2.5-pro",
    description="Loads wafer.npy files and prepares them for ML detection.",
    instruction="""
    You are the Ingestion Agent.
    Your role is to:
    1. Accept wafer.npy file path
    2. Load and validate the wafer map array
    3. Convert to RGB tensor for the CNN model
    4. Store processed tensor in context
    """,
    tools=[FunctionTool(ingest_image)],
    output_key="ingestion_output"
)
