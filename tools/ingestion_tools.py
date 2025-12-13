import os

def ingest_image(input_data):
    # Extract path if input is a dict (from Agent context)
    image_path = input_data
    if isinstance(input_data, dict):
        image_path = input_data.get("image_path")
        
    print(f"[Tool: ingest_image] Processing {image_path}...")
    if not image_path or not isinstance(image_path, str) or not os.path.exists(image_path):
        print(f"Error: Invalid path {image_path}")
        return {"error": "Image not found"}
    
    # Simulate processing
    return {
        "tensor": "mock_tensor_data",
        "metadata": {"width": 1024, "height": 1024, "format": "JPG"}
    }
