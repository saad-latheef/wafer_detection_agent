"""Quick test to verify best_model.pt loads correctly"""
import torch
import torchvision.models as models

# Load checkpoint
checkpoint = torch.load("best_model.pt", map_location='cpu', weights_only=False)

print("Checkpoint Info:")
print(f"  Epoch: {checkpoint.get('epoch', 'N/A')}")
print(f"  Best Accuracy: {checkpoint.get('best_acc', 'N/A')}%")

# Get config
config = checkpoint.get('config', {})
print(f"\nModel Config:")
print(f"  Num Classes: {config.get('num_classes', 'N/A')}")
print(f"  Model Type: {config.get('model_type', 'N/A')}")
print(f"  Class Names: {config.get('class_names', 'N/A')}")

# Try to load model
print("\nTrying to load model...")
try:
    num_classes = config.get('num_classes', 9)
    model = models.resnet18(pretrained=False)
    num_features = model.fc.in_features
    model.fc = torch.nn.Linear(num_features, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    print("✅ Model loaded successfully!")
    
    # Test forward pass
    dummy_input = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        output = model(dummy_input)
        probs = torch.softmax(output, dim=1)
    
    print(f"Output shape: {output.shape}")
    print(f"Probabilities sum: {probs.sum():.4f}")
    print("✅ Model inference works!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
