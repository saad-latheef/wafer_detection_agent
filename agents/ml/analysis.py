class AnalysisModule:
    """
    Role: Post-processing
    Responsibilities:
    - Thresholding
    - Severity scoring
    - Region-based aggregation
    - Uncertainty estimation
    """
    def __init__(self, threshold=0.7):
        self.threshold = threshold

    def analyze(self, raw_output):
        print("[AnalysisModule] Analyzing raw model output...")
        
        prob = raw_output.get("defect_probability", 0.0)
        
        # Determine if defect is present based on threshold
        is_defect = prob > self.threshold
        
        # Calculate severity (mock logic)
        severity = "High" if prob > 0.9 else ("Medium" if prob > 0.75 else "Low")
        if not is_defect:
            severity = "None"
            
        analysis_result = {
            "has_defect": is_defect,
            "confidence": prob,
            "severity": severity,
            "details": "scratch_detected_upper_quadrant" if is_defect else "clean_surface"
        }
        
        print(f"[AnalysisModule] Analysis complete. Result: {analysis_result}")
        return analysis_result
