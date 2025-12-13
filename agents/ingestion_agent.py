import os
import sys
import numpy as np
import cv2
from PIL import Image

from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool

# WM-811K standard wafer map dimensions
DEFAULT_DIE_ROWS = 26
DEFAULT_DIE_COLS = 33


def ingest_image(context):
    """
    Ingestion tool: Converts JPG/PNG images to die-level wafer maps.
    Uses die-grid extraction + per-die anomaly detection (WM-811K compatible).
    """
    print("\n" + "─"*50)
    print("📥 [Ingestion Agent] Starting image ingestion process")
    print("─"*50)
    
    image_path = context.image_path if hasattr(context, 'image_path') else ""
    
    print(f"   📁 Input image path: {image_path}")
    
    if not image_path or not os.path.exists(image_path):
        print(f"   ❌ ERROR: Image file not found at {image_path}")
        return context
    
    print("   🔍 Validating image format...")
    
    if image_path.endswith('.npy'):
        # Already in wafer map format
        print("   ✅ Detected NumPy wafer map format (.npy)")
        wafer_map = np.load(image_path)
        print(f"   📐 Wafer map shape: {wafer_map.shape}")
        
    elif image_path.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        # Convert image to die-level wafer map
        print("   🖼️ Converting image to die-level wafer map (WM-811K style)...")
        wafer_map = _convert_image_to_die_level_map(image_path)
        print(f"   📐 Generated wafer map shape: {wafer_map.shape}")
        
    else:
        print(f"   ❌ Unsupported format: {image_path}")
        return context
    
    # Convert to model tensor
    print("   🔄 Converting wafer map to model tensor...")
    tensor = _wafer_map_to_tensor(wafer_map)
    print(f"   📐 Tensor shape: {tensor.shape}")
    
    context.processed_tensor = tensor
    context.metadata = {
        "original_path": image_path,
        "format": image_path.split('.')[-1],
        "wafer_map_shape": wafer_map.shape,
        "tensor_shape": tuple(tensor.shape),
        "ready_for_model": True
    }
    
    print("   ✅ Ingestion complete - die-level wafer map ready")
    return context


def _detect_wafer_circle(gray):
    """
    Detects wafer boundary using Hough Circle Transform.
    Returns (center_x, center_y, radius) or estimates from image size.
    """
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Try Hough Circle detection
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=gray.shape[0] // 2,
        param1=50,
        param2=30,
        minRadius=gray.shape[0] // 4,
        maxRadius=gray.shape[0] // 2
    )
    
    if circles is not None:
        # Take the largest/best circle
        circle = circles[0][0]
        return int(circle[0]), int(circle[1]), int(circle[2])
    
    # Fallback: use image center
    h, w = gray.shape
    return w // 2, h // 2, min(h, w) // 2 - 5


def _convert_image_to_die_level_map(image_path, die_rows=DEFAULT_DIE_ROWS, die_cols=DEFAULT_DIE_COLS):
    """
    Converts JPG/PNG to die-level wafer map (WM-811K compatible).
    
    Pipeline:
    1. Detect wafer circle
    2. Create die grid (26x33 like WM-811K)
    3. For each die: compute anomaly score
    4. Mark dies as normal(1) or defect(2), non-wafer(0)
    """
    print("   🔧 Die-level conversion pipeline:")
    
    # Load image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        pil_img = Image.open(image_path).convert('L')
        img = np.array(pil_img)
    
    h, w = img.shape
    print(f"      Image size: {w}x{h}")
    
    # Step 1: Detect wafer circle
    print("      🔵 Step 1: Detecting wafer boundary...")
    cx, cy, radius = _detect_wafer_circle(img)
    print(f"         Wafer center: ({cx}, {cy}), radius: {radius}")
    
    # Step 2: Create die grid
    print(f"      🔵 Step 2: Creating {die_rows}x{die_cols} die grid...")
    wafer_map = np.zeros((die_rows, die_cols), dtype=np.uint8)
    
    # Calculate die dimensions
    die_h = (2 * radius) / die_rows
    die_w = (2 * radius) / die_cols
    
    # Get wafer statistics for normalization
    # Create wafer mask
    wafer_mask = np.zeros_like(img)
    cv2.circle(wafer_mask, (cx, cy), radius, 255, -1)
    wafer_pixels = img[wafer_mask == 255]
    wafer_mean = wafer_pixels.mean()
    wafer_std = wafer_pixels.std() + 1e-6
    
    print(f"         Wafer mean intensity: {wafer_mean:.1f}, std: {wafer_std:.1f}")
    
    # Step 3: Per-die anomaly detection
    print("      🔵 Step 3: Per-die anomaly detection...")
    defect_count = 0
    normal_count = 0
    non_wafer_count = 0
    
    for i in range(die_rows):
        for j in range(die_cols):
            # Die center in image coordinates
            die_cx = int(cx - radius + (j + 0.5) * die_w)
            die_cy = int(cy - radius + (i + 0.5) * die_h)
            
            # Check if die is inside wafer circle
            dist_from_center = np.sqrt((die_cx - cx)**2 + (die_cy - cy)**2)
            
            if dist_from_center > radius * 0.95:
                # Outside wafer
                wafer_map[i, j] = 0
                non_wafer_count += 1
            else:
                # Extract die region
                y1 = max(0, int(cy - radius + i * die_h))
                y2 = min(h, int(cy - radius + (i + 1) * die_h))
                x1 = max(0, int(cx - radius + j * die_w))
                x2 = min(w, int(cx - radius + (j + 1) * die_w))
                
                if y2 > y1 and x2 > x1:
                    die_region = img[y1:y2, x1:x2]
                    die_mean = die_region.mean()
                    
                    # Z-score relative to wafer
                    z_score = (die_mean - wafer_mean) / wafer_std
                    
                    # Defect detection: significant deviation from mean
                    if abs(z_score) > 1.0:  # More than 1 std from mean
                        wafer_map[i, j] = 2  # Defect
                        defect_count += 1
                    else:
                        wafer_map[i, j] = 1  # Normal
                        normal_count += 1
                else:
                    wafer_map[i, j] = 0
                    non_wafer_count += 1
    
    print(f"      📊 Die-level statistics:")
    print(f"         - Non-wafer dies (0): {non_wafer_count}")
    print(f"         - Normal dies (1):    {normal_count}")
    print(f"         - Defect dies (2):    {defect_count}")
    
    return wafer_map


def _wafer_map_to_tensor(wafer_map):
    """
    Converts die-level wafer map to RGB tensor for CNN.
    """
    import torch
    
    h, w = wafer_map.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    
    rgb[wafer_map == 0, 0] = 255  # non-wafer → Red
    rgb[wafer_map == 1, 1] = 255  # normal → Green
    rgb[wafer_map == 2, 2] = 255  # defect → Blue
    
    # Resize to 56x56 (model input size)
    img = Image.fromarray(rgb).resize((56, 56))
    img_array = np.array(img).astype(np.float32) / 255.0
    
    tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
    return tensor


ingestion_agent = Agent(
    name="ingestion_agent",
    model="gemini-2.5-pro",
    description="Converts images to die-level wafer maps (WM-811K compatible).",
    instruction="""
    You are the Ingestion Agent.
    Your role is to:
    1. Detect wafer boundary using circle detection
    2. Create die-level grid (26x33 like WM-811K)
    3. Score each die for anomalies relative to wafer mean
    4. Build die-level wafer map ready for the CNN model
    """,
    tools=[FunctionTool(ingest_image)],
    output_key="ingestion_output"
)
