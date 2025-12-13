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
    
    if not image_path.endswith('.npy'):
        print(f"   ❌ ERROR: Expected .npy file, got: {image_path}")
        return context
    
    # Load wafer map
    print("   📂 Loading wafer map (.npy)...")
    wafer_map = np.load(image_path)
    print(f"   📐 Wafer map shape: {wafer_map.shape}")
    print(f"   📊 Values: {np.unique(wafer_map)}")
    
    # Count regions
    non_wafer = np.sum(wafer_map == 0)
    normal = np.sum(wafer_map == 1)
    defect = np.sum(wafer_map == 2)
    print(f"   📊 Statistics:")
    print(f"      - Non-wafer (0): {non_wafer}")
    print(f"      - Normal (1):    {normal}")
    print(f"      - Defect (2):    {defect}")
    
    # Convert to tensor
    print("   🔄 Converting to model tensor...")
    tensor = _wafer_map_to_tensor(wafer_map)
    print(f"   📐 Tensor shape: {tensor.shape}")
    
    # Store in context
    context.processed_tensor = tensor
    context.metadata = {
        "original_path": image_path,
        "wafer_map_shape": wafer_map.shape,
        "tensor_shape": tuple(tensor.shape),
        "defect_count": int(defect),
        "normal_count": int(normal)
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
