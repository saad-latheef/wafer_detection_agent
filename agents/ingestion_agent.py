import os
import sys
import numpy as np
from PIL import Image

from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool


def ingest_image(context):
    """
    Ingestion tool: Prepares the image for further processing.
    Converts JPG/PNG images to wafer map format for the ML model.
    Stores the processed tensor directly in context for efficiency.
    """
    print("\n" + "─"*50)
    print("📥 [Ingestion Agent] Starting image ingestion process")
    print("─"*50)
    
    image_path = context.image_path if hasattr(context, 'image_path') else ""
    
    print(f"   📁 Input image path: {image_path}")
    
    # Validate file exists
    if not image_path or not os.path.exists(image_path):
        print(f"   ❌ ERROR: Image file not found at {image_path}")
        return context
    
    print("   🔍 Validating image format...")
    
    # Determine file type and process accordingly
    if image_path.endswith('.npy'):
        # Already in numpy format - load directly
        print("   ✅ Detected NumPy array format (.npy)")
        wafer_map = np.load(image_path)
        print(f"   📐 Wafer map shape: {wafer_map.shape}")
        
    elif image_path.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        # Convert image to wafer map format
        print("   🖼️ Detected image format - converting to wafer map...")
        wafer_map = _convert_image_to_wafer_map(image_path)
        print(f"   📐 Generated wafer map shape: {wafer_map.shape}")
        
    else:
        print(f"   ❌ Unsupported format: {image_path}")
        return context
    
    # Convert wafer map to model-ready tensor
    print("   🔄 Converting wafer map to model tensor...")
    tensor = _wafer_map_to_tensor(wafer_map)
    print(f"   📐 Tensor shape: {tensor.shape}")
    
    # Store in context (more efficient than file I/O)
    context.processed_tensor = tensor
    context.metadata = {
        "original_path": image_path,
        "format": image_path.split('.')[-1],
        "wafer_map_shape": wafer_map.shape,
        "tensor_shape": tensor.shape,
        "ready_for_model": True
    }
    
    print(f"   📋 Metadata: {context.metadata}")
    print("   ✅ Ingestion complete - tensor stored in context")
    
    return context


def _convert_image_to_wafer_map(image_path):
    """
    Converts a JPG/PNG image to wafer map format.
    Wafer map values: 0=non-wafer, 1=normal, 2=defect
    
    Conversion logic:
    - Grayscale the image
    - Dark areas (< threshold1) = defect (2)
    - Light areas (> threshold2) = non-wafer (0)
    - Middle = normal wafer (1)
    """
    print("   🔧 Image conversion process:")
    
    # Load image
    img = Image.open(image_path)
    print(f"      Original size: {img.size}, mode: {img.mode}")
    
    # Convert to grayscale
    gray = img.convert('L')
    
    # Resize to standard wafer size (56x56 as expected by model after preprocessing)
    # But wafer map can be any size, preprocessing will resize
    gray = gray.resize((56, 56))
    print(f"      Resized to: {gray.size}")
    
    # Convert to numpy array
    gray_array = np.array(gray)
    
    # Create wafer map based on intensity thresholds
    wafer_map = np.ones_like(gray_array, dtype=np.uint8)  # Default: normal (1)
    
    # Dark pixels = defect (value 2)
    defect_threshold = 100
    wafer_map[gray_array < defect_threshold] = 2
    
    # Very bright pixels = non-wafer area (value 0)  
    non_wafer_threshold = 240
    wafer_map[gray_array > non_wafer_threshold] = 0
    
    # Count regions
    defect_count = np.sum(wafer_map == 2)
    normal_count = np.sum(wafer_map == 1)
    non_wafer_count = np.sum(wafer_map == 0)
    
    print(f"      Wafer map created:")
    print(f"         - Defect pixels (2): {defect_count}")
    print(f"         - Normal pixels (1): {normal_count}")
    print(f"         - Non-wafer pixels (0): {non_wafer_count}")
    
    return wafer_map


def _wafer_map_to_tensor(wafer_map):
    """
    Converts wafer map (values 0,1,2) to RGB tensor for the CNN model.
    Same logic as preprocess_real_wafer but works with in-memory data.
    """
    import torch
    
    h, w = wafer_map.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    
    # One-hot style encoding to RGB
    rgb[wafer_map == 0, 0] = 255  # non-wafer → Red channel
    rgb[wafer_map == 1, 1] = 255  # normal → Green channel
    rgb[wafer_map == 2, 2] = 255  # defect → Blue channel
    
    # Resize to model input size (56x56)
    img = Image.fromarray(rgb).resize((56, 56))
    img_array = np.array(img).astype(np.float32) / 255.0
    
    # Convert to tensor: (H, W, C) -> (C, H, W) -> (1, C, H, W)
    tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
    
    return tensor


ingestion_agent = Agent(
    name="ingestion_agent",
    model="gemini-2.5-pro",
    description="Handles image ingestion and converts images to wafer map format.",
    instruction="""
    You are the Ingestion Agent.
    Your role is to:
    1. Accept the input image path (JPG, PNG, or NPY)
    2. Convert images to wafer map format (0=non-wafer, 1=normal, 2=defect)
    3. Transform wafer map to model-ready tensor
    4. Store the processed tensor in context for the ML agent
    
    Always explain your decision-making process clearly.
    """,
    tools=[FunctionTool(ingest_image)],
    output_key="ingestion_output"
)
