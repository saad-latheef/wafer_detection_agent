from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class WaferContext:
    """
    Shared context object passed between all agents in the pipeline.
    This holds the complete state of a wafer inspection run.
    """
    # Input
    image_path: str = ""
    
    # Ingestion outputs
    processed_tensor: Any = None
    metadata: Dict = field(default_factory=dict)
    
    # Detection/ML outputs  
    probability_distribution: Dict[str, float] = field(default_factory=dict)
    predicted_class: str = ""
    confidence: float = 0.0
    
    # Analysis outputs
    analysis_result: Dict = field(default_factory=dict)
    major_issues: list = field(default_factory=list)
    
    # Validation state
    is_valid: bool = False
    validation_attempts: int = 0
    max_attempts: int = 3
    
    # Explanation output
    explanation: str = ""
    
    # Final decision
    has_defect: bool = False
    severity: str = "None"
    
    def to_dict(self) -> Dict:
        """Convert context to dictionary for logging."""
        return {
            "image_path": self.image_path,
            "predicted_class": self.predicted_class,
            "confidence": self.confidence,
            "is_valid": self.is_valid,
            "has_defect": self.has_defect,
            "severity": self.severity,
            "explanation": self.explanation[:100] + "..." if len(self.explanation) > 100 else self.explanation
        }
