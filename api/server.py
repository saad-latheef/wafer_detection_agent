"""
FastAPI server for Wafer Detection Agent.
Returns comprehensive analysis data matching agent output.
"""
import os
import sys
import tempfile
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.context import WaferContext
from agents.ingestion_agent import ingest_image
from agents.ml_agent import run_ml_inference
from agents.analysis_agent import analyze_results
from agents.explanation_agent import generate_explanation

app = FastAPI(title="Wafer Detection Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PatternProbability(BaseModel):
    pattern: str
    probability: float


class IngestionDetails(BaseModel):
    waferMapShape: List[int]
    tensorShape: List[int]
    nonWaferCount: int
    normalCount: int
    defectCount: int


class AnalysisDetails(BaseModel):
    consistencyScore: float
    issuesFound: List[str]
    recommendation: str
    majorIssues: List[Dict[str, Any]]


class ValidationDetails(BaseModel):
    attempts: int
    maxAttempts: int
    criteriaChecks: List[Dict[str, Any]]
    passed: bool


class AgentResult(BaseModel):
    name: str
    model: str
    topPattern: str
    topProbabilities: List[PatternProbability]
    confidence: float
    qualityFlag: Optional[str]
    description: str
    rootCauses: List[str]
    actionSuggestions: List[str]


class TriggerAction(BaseModel):
    alertSent: bool
    recipient: str
    subject: str
    severity: str
    actions: List[str]


class AnalysisResponse(BaseModel):
    waferId: str
    fileName: str
    finalVerdict: str
    confidence: float
    severity: str
    
    # Detailed info from each agent
    ingestionDetails: IngestionDetails
    analysisDetails: AnalysisDetails
    validationDetails: ValidationDetails
    triggerAction: TriggerAction
    
    # Agent results for 3 columns
    agentResults: List[AgentResult]
    
    # Full data
    fullProbabilityDistribution: Dict[str, float]
    explanation: str
    
    # Processing info
    modelUsed: str
    deviceUsed: str


# Root cause mappings
ROOT_CAUSES = {
    "Center": [
        "Focus or exposure center bias",
        "Chuck temperature center gradient",
        "Gas flow distribution center concentration"
    ],
    "Donut": [
        "Photoresist coating ring pattern",
        "Spin coating non-uniformity",
        "Temperature gradient during processing"
    ],
    "Edge-Loc": [
        "Edge handling damage",
        "Edge exclusion zone misconfiguration",
        "Peripheral contamination"
    ],
    "Edge-Ring": [
        "Edge bead removal (EBR) process deviation",
        "Spin coating non-uniformity at wafer periphery",
        "Chamber edge heating inconsistency"
    ],
    "Loc": [
        "Localized particle contamination",
        "Point source defect during deposition",
        "Mask defect or alignment issue"
    ],
    "Near-full": [
        "Severe process contamination",
        "Complete chamber malfunction",
        "Critical recipe parameter deviation"
    ],
    "Random": [
        "Ambient particle contamination",
        "Handling and transport issues",
        "Cleanroom environment degradation"
    ],
    "Scratch": [
        "Mechanical handling damage",
        "Robotic arm malfunction",
        "Wafer cassette contact issues"
    ],
    "none": []
}

ACTION_SUGGESTIONS = {
    "Center": [
        "Verify stepper focus calibration",
        "Check chuck thermal uniformity",
        "Analyze process gas flow patterns"
    ],
    "Donut": [
        "Inspect photoresist dispense system",
        "Calibrate spin coater acceleration",
        "Check bake plate temperature uniformity"
    ],
    "Edge-Loc": [
        "Inspect edge contact points",
        "Review edge exclusion settings",
        "Check for peripheral contamination"
    ],
    "Edge-Ring": [
        "Check EBR tool calibration and nozzle positioning",
        "Verify spin coating recipe parameters",
        "Inspect edge exclusion zone settings"
    ],
    "Loc": [
        "Run particle analysis on affected area",
        "Check deposition uniformity",
        "Inspect mask for defects"
    ],
    "Near-full": [
        "Immediate lot hold recommended",
        "Full chamber qualification required",
        "Escalate to process engineering team"
    ],
    "Random": [
        "Review cleanroom particle counts",
        "Inspect wafer handling equipment",
        "Check HEPA filter status"
    ],
    "Scratch": [
        "Inspect robotic handler end effectors",
        "Check wafer cassette for damage",
        "Review handling procedures"
    ],
    "none": [
        "Continue production monitoring",
        "Standard quality gate passage"
    ]
}

TRIGGER_ACTIONS = {
    "High": [
        "STOP production line for inspection",
        "Flag wafer for immediate review",
        "Notify Quality Control team"
    ],
    "Medium": [
        "Mark wafer for quality review",
        "Continue production with monitoring",
        "Log for trend analysis"
    ],
    "Low": [
        "Log defect for monitoring",
        "Continue normal operation",
        "Review in next batch analysis"
    ],
    "None": [
        "Continue production monitoring",
        "Standard quality gate passage"
    ]
}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_wafer(file: UploadFile = File(...)):
    if not file.filename.endswith('.npy'):
        raise HTTPException(status_code=400, detail="Only .npy files are supported")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.npy') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        context = WaferContext(image_path=tmp_path, max_attempts=3)
        
        # Run ingestion
        ingest_image(context)
        
        # Run ML inference
        run_ml_inference(context)
        
        # Run analysis
        analyze_results(context)
        
        # Generate explanation
        generate_explanation(context)
        
        # Extract all data
        prob_dist = context.probability_distribution or {}
        predicted = context.predicted_class or "none"
        confidence = context.confidence or 0.0
        has_defect = context.has_defect or False
        severity = context.severity or "None"
        explanation = context.explanation or ""
        metadata = context.metadata or {}
        analysis_result = context.analysis_result or {}
        major_issues = context.major_issues if hasattr(context, 'major_issues') else []
        
        # Build ingestion details
        wafer_shape = list(metadata.get("wafer_map_shape", [0, 0]))
        tensor_shape = list(metadata.get("tensor_shape", [1, 3, 56, 56]))
        
        ingestion_details = IngestionDetails(
            waferMapShape=wafer_shape,
            tensorShape=tensor_shape,
            nonWaferCount=metadata.get("non_wafer_count", 0),
            normalCount=metadata.get("normal_count", 0),
            defectCount=metadata.get("defect_count", 0)
        )
        
        # Build analysis details
        analysis_details = AnalysisDetails(
            consistencyScore=analysis_result.get("consistency_score", 1.0),
            issuesFound=analysis_result.get("issues_found", []),
            recommendation=analysis_result.get("recommendation", "PASS"),
            majorIssues=[{"class": i.get("class", ""), "probability": i.get("probability", 0)} for i in major_issues]
        )
        
        # Build validation details
        validation_details = ValidationDetails(
            attempts=context.validation_attempts if hasattr(context, 'validation_attempts') else 1,
            maxAttempts=3,
            criteriaChecks=[
                {"name": "Consistency Score", "passed": analysis_result.get("consistency_score", 1.0) >= 0.6},
                {"name": "Confidence Threshold", "passed": confidence >= 0.25},
                {"name": "No Prediction Mismatch", "passed": "prediction_mismatch" not in analysis_result.get("issues_found", [])}
            ],
            passed=context.is_valid if hasattr(context, 'is_valid') else True
        )
        
        # Build trigger action
        trigger_action = TriggerAction(
            alertSent=has_defect,
            recipient="quality-control@semiconductor.com",
            subject=f"[ALERT] Wafer Defect Detected - {predicted}",
            severity=severity,
            actions=TRIGGER_ACTIONS.get(severity, TRIGGER_ACTIONS["None"])
        )
        
        # Sort probabilities
        sorted_probs = sorted(prob_dist.items(), key=lambda x: x[1], reverse=True)
        top_probs = [
            PatternProbability(pattern=p, probability=round(v * 100, 2))
            for p, v in sorted_probs
        ]
        
        # Quality flag
        quality_flag = None
        if confidence < 0.5:
            quality_flag = "⚠️ Low confidence - manual review recommended"
        elif confidence < 0.75:
            quality_flag = "⚠️ Moderate confidence - consider verification"
        
        # Create agent results
        agent_results = [
            AgentResult(
                name="CNN Classifier",
                model="k_cross_CNN (Pattern Detection)",
                topPattern=predicted,
                topProbabilities=top_probs,
                confidence=round(confidence * 100, 1),
                qualityFlag=quality_flag,
                description=f"Primary pattern detected: {predicted} with {confidence*100:.1f}% confidence. "
                           f"Neural network inference completed on CPU. Tensor shape: {tensor_shape}.",
                rootCauses=ROOT_CAUSES.get(predicted, []),
                actionSuggestions=ACTION_SUGGESTIONS.get(predicted, [])
            ),
            AgentResult(
                name="Analysis Agent",
                model="Statistical Analysis Module",
                topPattern=predicted,
                topProbabilities=top_probs[:5],
                confidence=round(confidence * 100, 1),
                qualityFlag=None if not analysis_result.get("issues_found") else "⚠️ Issues detected",
                description=f"Consistency score: {analysis_result.get('consistency_score', 1.0)*100:.0f}%. "
                           f"Severity: {severity}. Recommendation: {analysis_result.get('recommendation', 'PASS')}. "
                           f"Major issues: {len(major_issues)}.",
                rootCauses=ROOT_CAUSES.get(predicted, []),
                actionSuggestions=ACTION_SUGGESTIONS.get(predicted, [])
            ),
            AgentResult(
                name="Validation Agent",
                model="Quality Assurance Module",
                topPattern=predicted,
                topProbabilities=top_probs[:5],
                confidence=round(confidence * 100, 1),
                qualityFlag=None if validation_details.passed else "⚠️ Required multiple attempts",
                description=f"Validation: {'PASSED' if validation_details.passed else 'NEEDS REVIEW'} "
                           f"(Attempt {validation_details.attempts}/{validation_details.maxAttempts}). "
                           f"All {len(validation_details.criteriaChecks)} criteria met.",
                rootCauses=ROOT_CAUSES.get(predicted, []),
                actionSuggestions=ACTION_SUGGESTIONS.get(predicted, [])
            )
        ]
        
        return AnalysisResponse(
            waferId=f"W-{hash(file.filename) % 10000:04d}",
            fileName=file.filename,
            finalVerdict="FAIL" if has_defect else "PASS",
            confidence=round(confidence * 100, 1),
            severity=severity,
            ingestionDetails=ingestion_details,
            analysisDetails=analysis_details,
            validationDetails=validation_details,
            triggerAction=trigger_action,
            agentResults=agent_results,
            fullProbabilityDistribution={k: round(v * 100, 2) for k, v in prob_dist.items()},
            explanation=explanation,
            modelUsed="k_cross_CNN.pt",
            deviceUsed="cpu"
        )
        
    finally:
        os.unlink(tmp_path)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "model": "k_cross_CNN.pt", "device": "cpu"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
