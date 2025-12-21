
import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

from backend.pdf_generator import generate_wafer_report_pdf

def test_pdf_gen():
    lot_data = {
        "total_wafers": 10,
        "defective_wafers": 2,
        "yield_rate": 80.0,
        "defect_distribution": {"Scratch": 1, "Donut": 1}
    }
    
    wafer_analyses = [
        {
            "waferId": "W1",
            "fileName": "wafer1.npy",
            "finalVerdict": "PASS",
            "confidence": 98.5,
            "severity": "None"
        },
        {
            "waferId": "W2",
            "fileName": "wafer2.npy",
            "finalVerdict": "FAIL",
            "confidence": 99.1,
            "severity": "High"
        }
    ]
    
    try:
        print("Generating PDF...")
        buffer = generate_wafer_report_pdf(lot_data, wafer_analyses)
        size = buffer.getbuffer().nbytes
        print(f"PDF generated successfully. Size: {size} bytes")
        
        with open("test_report.pdf", "wb") as f:
            f.write(buffer.getvalue())
        print("Saved to test_report.pdf")
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_gen()
