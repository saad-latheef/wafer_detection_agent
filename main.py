import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.context import WaferContext
from agents.coordinator_agent import coordinator_sequential


def main():
    print("╔" + "═"*68 + "╗")
    print("║" + " "*20 + "WAFER DETECTION SYSTEM" + " "*26 + "║")
    print("║" + " "*15 + "Google ADK Agent Architecture" + " "*23 + "║")
    print("╚" + "═"*68 + "╝")
    print()
    
    # Use test.jpg as input - the ingestion agent will convert it to wafer map format
    test_image = os.path.join(project_root, "test.jpg")
    
    if not os.path.exists(test_image):
        # Fallback to wafer.npy if test.jpg doesn't exist
        test_image = os.path.join(project_root, "wafer.npy")
        print(f"⚠️ test.jpg not found, using fallback: {test_image}")
    else:
        print(f"📁 Using input image: {test_image}")
    
    print()
    
    # Create shared context
    context = WaferContext(
        image_path=test_image,
        max_attempts=3
    )
    
    print("═"*70)
    print("🚀 STARTING WAFER INSPECTION PIPELINE")
    print("═"*70)
    
    # Run the coordinator agent with the context
    result = coordinator_sequential.run(context)
    
    print()
    print("═"*70)
    print("📊 FINAL INSPECTION SUMMARY")
    print("═"*70)
    
    print(f"""
    Image Analyzed:    {context.image_path}
    Defect Detected:   {context.has_defect}
    Predicted Class:   {context.predicted_class}
    Confidence:        {context.confidence*100:.1f}%
    Severity:          {context.severity}
    Validation Status: {'PASSED' if context.is_valid else 'FAILED'}
    Attempts Used:     {context.validation_attempts}
    """)
    
    print("═"*70)
    print("✅ INSPECTION COMPLETE")
    print("═"*70)


if __name__ == "__main__":
    main()
