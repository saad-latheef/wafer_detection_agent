class ValidationModule:
    """
    Role: Self-check + Feedback
    Responsibilities:
    - Confidence validation
    - Cross-check against heuristics
    - Trigger re-run / fallback model if needed
    """
    def __init__(self):
        pass

    def validate(self, analysis_result):
        """
        Validates the analysis result.
        Returns:
            bool: True if valid, False if re-run is needed.
        """
        print("[ValidationModule] Validating results...")
        
        confidence = analysis_result.get("confidence", 0)
        
        # Heuristic: If confidence is very low (e.g. 0.4-0.6 range often implies uncertainty in binary class),
        # we might flag it as invalid or needing re-check.
        # For this demo, let's say 0.3 to 0.5 is the 'ambiguous zone'.
        if 0.3 < confidence < 0.5:
            print("[ValidationModule] ⚠️ Result is ambiguous (Confidence in 0.3-0.5 range). Validation FAILED.")
            return False
        
        print(f"[ValidationModule] Result valid. Confidence: {confidence:.2f}")
        return True
